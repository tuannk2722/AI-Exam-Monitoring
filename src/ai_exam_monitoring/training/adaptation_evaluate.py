"""Standalone full-bundle evaluation and payload-keyed final access."""

from __future__ import annotations

import json
import platform
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from . import holdout_access
from .adaptation_config import (
    AdaptationConfig,
    DatasetSpec,
    RepresentationConfig,
    config_from_dict,
    local_path,
    verify_adaptation_approval,
)
from .adaptation_data import ImageCohort, prepare_cohorts
from .adaptation_model import AdaptationModel, tensor_digest
from .adaptation_train import cohort_report, runtime_signature
from .artifacts import checksum_artifacts, code_identity, digest_json, environment, now, write_json
from .data import crop_path, image_tensor, labels, verify_dataset
from .device import configure_device, execution_environment
from .train import peak_rss


def load_bundle(run_dir: Path, workspace: Path) -> tuple[AdaptationModel, dict[str, Any]]:
    config = config_from_dict(
        json.loads((run_dir / "resolved-config.json").read_text(encoding="utf-8"))
    )
    verify_adaptation_approval(config, workspace)
    record = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    bundle = json.loads((run_dir / "bundle.json").read_text(encoding="utf-8"))
    torch.set_num_threads(config.threads)
    device = configure_device(config)
    if (
        record["status"] != "FINISHED"
        or bundle["schema_version"] != "full-model-bundle-v1"
        or record["code_sha256"] != code_identity()["sha256"]
        or bundle["code_sha256"] != record["code_sha256"]
        or bundle["config_sha256"] != digest_json(config.to_dict())
        or bundle["config_sha256"] != record["config_sha256"]
        or bundle["runtime_sha256"] != runtime_signature(execution_environment(config))
        or bundle["target_order"] != config.target_order
        or bundle["threshold"] != config.threshold
    ):
        raise DataContractError("Bundle/run/config/code/runtime mismatch")
    checks = json.loads((run_dir / "checksums.json").read_text(encoding="utf-8"))
    for name in (
        "best.pt",
        "bundle.json",
        "resolved-config.json",
        "code-provenance.json",
        "run.json",
    ):
        if sha256_file(run_dir / name) != checks.get(name):
            raise DataContractError("Bundle artifact checksum changed")
    if sha256_file(run_dir / "best.pt") != bundle["checkpoint_sha256"]:
        raise DataContractError("Checkpoint changed")
    payload = torch.load(run_dir / "best.pt", map_location="cpu", weights_only=True)
    if (
        payload["schema_version"] != bundle["schema_version"]
        or payload["identity"] != bundle["identity"]
        or payload["config"] != config.to_dict()
        or tensor_digest(payload["model"]) != payload["model_tensor_sha256"]
    ):
        raise DataContractError("Full model tensor/config identity changed")
    model = AdaptationModel(config, full_state=payload["model"], workspace=workspace).to(device)
    model.eval()
    return model, payload


def benchmark(
    model: AdaptationModel,
    paths: list[Path],
    config: AdaptationConfig,
    *,
    warmup: int = 10,
    measured: int = 500,
) -> dict[str, Any]:
    if not paths or warmup != 10 or measured != 500 or config.threads != 4:
        raise DataContractError(
            "Benchmark requires frozen crops, B1/4threads, warmup10/measured500"
        )
    torch.set_num_threads(4)
    pins = [(str(p), sha256_file(p)) for p in paths]  # hashes explicitly outside timed region
    model.eval()
    times = []
    with torch.no_grad():
        for i in range(warmup + measured):
            start = time.perf_counter()
            logits = model(image_tensor(paths[i % len(paths)], config).unsqueeze(0))
            elapsed = time.perf_counter() - start
            if not torch.isfinite(logits).all():
                raise DataContractError("Nonfinite benchmark output")
            if i >= warmup:
                times.append(elapsed * 1000)
    return {
        "batch_size": 1,
        "threads": 4,
        "warmup": warmup,
        "measured": measured,
        "timing_scope": "decode_letterbox_normalize_forward",
        "hashes_outside_timing": True,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "environment": environment(),
        "crop_order_pins": pins,
        "p95_ms": float(np.percentile(times, 95)),
        "median_ms": float(np.median(times)),
        "peak_rss_bytes": peak_rss(),
        "rss_semantics": "Windows process peak_wset; otherwise current RSS, not claimed peak",
        "samples_ms": times,
    }


def evaluate_adaptation(
    run_dir: Path,
    output: Path,
    workspace: Path,
    split: str,
    protocol_path: Path | None = None,
    *,
    run_benchmark: bool = False,
) -> dict[str, Any]:
    workspace, output = workspace.resolve(), output.resolve()
    if output.exists() or not output.is_relative_to(workspace / "outputs"):
        raise DataContractError("Require new evaluation output under outputs")
    config = config_from_dict(
        json.loads((run_dir / "resolved-config.json").read_text(encoding="utf-8"))
    )
    verify_adaptation_approval(config, workspace)
    if isinstance(config, RepresentationConfig) and (split == "test" or run_benchmark):
        raise DataContractError("V4 research has no final test or legacy CPU benchmark scope")
    token, payload_key = None, None
    protocol: dict[str, Any]
    if split == "test":
        if protocol_path is None or run_benchmark:
            raise DataContractError(
                "Final test requires separate owner protocol; benchmark uses development only"
            )
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        expected = {
            "schema_version": "final-adaptation-protocol-v1",
            "status": "approved",
            "owner": config.owner,
            "experiment_id": config.experiment_id,
            "config_sha256": digest_json(config.to_dict()),
            "code_sha256": code_identity()["sha256"],
            "checkpoint_sha256": json.loads((run_dir / "bundle.json").read_text(encoding="utf-8"))[
                "checkpoint_sha256"
            ],
            "threshold": config.threshold,
            "target_order": config.target_order,
            "candidate_count": 1,
        }
        if (
            any(protocol.get(k) != v for k, v in expected.items())
            or not protocol.get("decision_ref")
            or config.model != "resnet18_layer4"
            or config.run_kind != "promotion"
        ):
            raise DataContractError("Final protocol does not authorize this single candidate")
        data = DatasetSpec(**protocol["data"])
        payload_key = data.payload_sha256
        # No crop reading/model deserialization before exclusive payload reservation.
        token = holdout_access.reserve(
            workspace,
            payload_key,
            {
                **expected,
                "protocol_sha256": sha256_file(protocol_path),
                "output": output.relative_to(workspace).as_posix(),
            },
        )
    elif split == "val":
        protocol = config.protocol.read_json(workspace)
    else:
        raise DataContractError("Evaluator supports val or separately approved test")
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    try:
        torch.use_deterministic_algorithms(True)
        model, bundle = load_bundle(run_dir, workspace)
        startup_seconds = time.perf_counter() - started
        if split == "val":
            cohorts, protocol = prepare_cohorts(config, workspace)
            selected = [c for c in cohorts if c.role != "train"]
        else:
            data = DatasetSpec(**protocol["data"])
            root = local_path(workspace, data.dataset)
            records = verify_dataset(root, data)
            if any(r.usage != "test" for r in records):
                raise DataContractError("Final holdout must be a separate test-only package")
            by_id = {r.sample_id: r for r in records}
            ids = protocol["sample_ids"]
            if len(ids) != len(by_id) or set(ids) != set(by_id):
                raise DataContractError("Final protocol membership changed")
            rows = [by_id[s] for s in ids]
            from ai_exam_monitoring.data.pilot_schema import record_to_dict

            if digest_json([record_to_dict(r) for r in rows]) != protocol["records_sha256"]:
                raise DataContractError("Holdout record identities changed")
            families = protocol["family_assignments"]
            groups = []
            for row in rows:
                family = families[row.sample_id]
                if (
                    family.get("owner_accepted") is not True
                    or family.get("independence_verified") is not True
                    or not family.get("evidence_refs")
                    or not family.get("family_id")
                ):
                    raise DataContractError("Final group independence missing")
                groups.append(family["family_id"])
            values, mask = labels(rows)
            training_protocol = config.protocol.read_json(workspace)
            reserved = training_protocol["reserved_holdout"]
            if (
                reserved.get("payload_sha256") != payload_key
                or set(groups) != set(reserved["family_ids"])
                or {r.source.image_sha256 for r in rows} != set(reserved["source_sha256"])
            ):
                raise DataContractError("Final holdout differs from pre-training reservation")
            development, _ = prepare_cohorts(config, workspace)
            for cohort in development:
                if (
                    set(cohort.ids) & set(ids)
                    or set(cohort.groups) & set(groups)
                    or {r.source.image_sha256 for r in cohort.records}
                    & {r.source.image_sha256 for r in rows}
                    or {r.crop.crop_sha256 for r in cohort.records if r.crop}
                    & {r.crop.crop_sha256 for r in rows if r.crop}
                ):
                    raise DataContractError("Final holdout overlaps training/development")
            contexts = {families[r.sample_id].get("context_id") for r in rows}
            if None in contexts or "" in contexts or len(contexts) < 2 or len(set(groups)) < 10:
                raise DataContractError("G3 actual holdout groups/contexts insufficient")
            for target in range(2):
                for value in (0, 1):
                    indices = [
                        i
                        for i in range(len(rows))
                        if mask[i, target] and values[i, target] == value
                    ]
                    if len(indices) < 100 or len({groups[i] for i in indices}) < 5:
                        raise DataContractError("G3 actual holdout P/N support insufficient")
            selected = [
                ImageCohort(
                    "holdout",
                    "holdout",
                    rows,
                    [crop_path(root, r) for r in rows],
                    values,
                    mask,
                    groups,
                )
            ]
        metrics = {}
        thresholds = None
        if isinstance(config, RepresentationConfig):
            checks = json.loads((run_dir / "checksums.json").read_text(encoding="utf-8"))
            calibration_path = run_dir / "calibration.json"
            if sha256_file(calibration_path) != checks.get("calibration.json"):
                raise DataContractError("Calibration artifact changed")
            calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
            selection = next(c for c in selected if c.role == "selection")
            if (calibration.get("checkpoint_sha256") != sha256_file(run_dir / "best.pt")
                    or calibration.get("selection_ids_sha256") != digest_json(selection.ids)
                    or calibration.get("fit_cohort") != selection.name):
                raise DataContractError("Calibration checkpoint/cohort mismatch")
            thresholds = (float(calibration["thresholds"][0]), float(calibration["thresholds"][1]))
        for cohort in selected:
            metrics[cohort.name], predictions = cohort_report(
                model,
                cohort,
                config,
                bundle["train_prevalence"],
                protocol,
                thresholds=thresholds,
            )
            write_json(output / f"predictions-{cohort.name}.json", predictions)
        if run_benchmark:
            cohort = next(c for c in selected if c.role == "selection")
            metrics["benchmark"] = {
                **benchmark(model, cohort.paths, config),
                "startup_seconds": startup_seconds,
            }
        write_json(output / "metrics.json", metrics)
        write_json(
            output / "evaluation.json",
            {
                "status": "FINISHED",
                "split": split,
                "evaluated_at": now(),
                "best_epoch": bundle["epoch"],
                "checkpoint_sha256": sha256_file(run_dir / "best.pt"),
                "protocol_sha256": sha256_file(protocol_path)
                if protocol_path
                else config.protocol.sha256,
                "config_sha256": digest_json(config.to_dict()),
                "code_sha256": code_identity()["sha256"],
                "promotion": "owner_decision_required",
            },
        )
        checksum_artifacts(output)
        if token is not None and payload_key is not None:
            holdout_access.finish(
                workspace,
                payload_key,
                token,
                success=True,
                evidence={"evaluation_sha256": sha256_file(output / "evaluation.json")},
            )
        return metrics
    except BaseException as error:
        write_json(
            output / "evaluation.json",
            {"status": "FAILED", "error": f"{type(error).__name__}: {error}"},
        )
        if token is not None and payload_key is not None:
            holdout_access.finish(
                workspace,
                payload_key,
                token,
                success=False,
                evidence={"error": f"{type(error).__name__}: {error}"},
            )
        raise
