"""Matched full-image training with global masked objective and epoch-boundary resume."""

from __future__ import annotations

import copy
import json
import random
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .adaptation_config import AdaptationConfig, load_adaptation_config, verify_adaptation_approval
from .adaptation_data import ImageCohort, prepare_cohorts
from .adaptation_metrics import group_bootstrap, minibatch_loss, report_scores, slice_reports
from .adaptation_model import AdaptationModel, tensor_digest
from .artifacts import (
    RunRecord,
    checksum_artifacts,
    code_identity,
    digest_json,
    environment,
    now,
    save_checkpoint,
    write_json,
)
from .metrics import masked_loss
from .train import peak_rss, restore_rng, rng_state, write_curve


def infer(model: AdaptationModel, cohort: ImageCohort, config: AdaptationConfig) -> torch.Tensor:
    model.eval()
    logits = []
    with torch.no_grad():
        for start in range(0, len(cohort.ids), config.batch_size):
            indices = list(range(start, min(start + config.batch_size, len(cohort.ids))))
            logits.append(model(cohort.batch(indices, config)).cpu())
    result = torch.cat(logits)
    if not torch.isfinite(result).all():
        raise DataContractError("Nonfinite cohort logits")
    return result


def train_images(
    model: AdaptationModel,
    train: ImageCohort,
    selection: ImageCohort,
    config: AdaptationConfig,
    output: Path,
    identity: str,
    *,
    resume: bool = False,
    interrupt_after: int | None = None,
    remaining_seconds: float | None = None,
) -> dict[str, Any]:
    if (
        train.role != "train"
        or selection.role != "selection"
        or not train.mask.any(1).all()
        or not train.mask.any(0).all()
        or not selection.mask.any(0).all()
    ):
        raise DataContractError("Train/selection support invalid")
    groups, names = model.parameter_groups(config)
    optimizer = torch.optim.AdamW(groups)
    generator = torch.Generator().manual_seed(config.seed)
    state: dict[str, Any] = {
        "schema_version": "full-model-epoch-v1",
        "identity": identity,
        "config": config.to_dict(),
        "epoch": 0,
        "global_step": 0,
        "best_epoch": 0,
        "best_loss": float("inf"),
        "best_model": None,
        "early_reference": float("inf"),
        "stale": 0,
        "history": [],
        "parameter_groups": names,
        "sampler_permutation": [],
        "sampler_cursor": 0,
        "resume_semantics": "restart_uncommitted_epoch_from_last_atomic_epoch_boundary",
    }
    if resume:
        state = torch.load(output / "last.pt", map_location="cpu", weights_only=True)
        if (
            state["schema_version"] != "full-model-epoch-v1"
            or state["identity"] != identity
            or state["config"] != config.to_dict()
            or state["parameter_groups"] != names
            or state["sampler_cursor"] not in {0, len(train.ids)}
        ):
            raise DataContractError("Resume identity/config/parameter/sampler state changed")
        model.load_state_dict(state["model"], strict=True)
        optimizer.load_state_dict(state["optimizer"])
        generator.set_state(state["sampler_rng"])
        restore_rng(state["rng"])
    else:
        write_json(
            output / "initialization.json",
            {
                "head_tensor_sha256": tensor_digest(model.network.fc.state_dict()),
                "pretrained_sha256": config.weights.sha256,
                "initial_head_file_sha256": config.head_initialization.sha256,
                "parameter_groups": names,
                "seed": config.seed,
            },
        )

    def checkpoint() -> None:
        state.update(
            model=model.state_dict(),
            optimizer=optimizer.state_dict(),
            rng=rng_state(),
            sampler_rng=generator.get_state(),
        )
        save_checkpoint(output / "last.pt", state)

    if not resume:
        checkpoint()
    deadline = time.perf_counter() + (
        config.wall_time_seconds if remaining_seconds is None else remaining_seconds
    )
    known = train.mask.sum(0)
    for epoch in range(state["epoch"] + 1, config.max_epochs + 1):
        if state["stale"] >= config.patience:
            break
        order = torch.randperm(len(train.ids), generator=generator).tolist()
        model.train()
        for start in range(0, len(order), config.batch_size):
            if time.perf_counter() >= deadline:
                raise TimeoutError("Approved wall-time budget exhausted; config unchanged")
            indices = order[start : start + config.batch_size]
            optimizer.zero_grad(set_to_none=True)
            logits = model(train.batch(indices, config))
            loss = minibatch_loss(
                logits, train.values[indices], train.mask[indices], len(train.ids), known
            )
            if not torch.isfinite(loss):
                raise DataContractError("Nonfinite mini-batch loss")
            torch.autograd.backward(loss)
            if any(
                p.grad is None or not torch.isfinite(p.grad).all()
                for p in model.parameters()
                if p.requires_grad
            ):
                raise DataContractError("Missing/nonfinite trainable gradient")
            optimizer.step()
            if any(not torch.isfinite(p).all() for p in model.parameters()):
                raise DataContractError("Nonfinite model weights")
            state["global_step"] += 1
        train_loss = float(masked_loss(infer(model, train, config), train.values, train.mask))
        val_loss = float(
            masked_loss(infer(model, selection, config), selection.values, selection.mask)
        )
        if time.perf_counter() >= deadline:
            raise TimeoutError("Approved wall-time budget exhausted before epoch commit")
        if val_loss < state["best_loss"]:
            state.update(
                best_loss=val_loss, best_epoch=epoch, best_model=copy.deepcopy(model.state_dict())
            )
        if val_loss < state["early_reference"] - config.min_delta:
            state.update(early_reference=val_loss, stale=0)
        else:
            state["stale"] += 1
        state["epoch"] = epoch
        state["sampler_permutation"], state["sampler_cursor"] = order, len(order)
        state["history"].append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "permutation_sha256": digest_json([train.ids[i] for i in order]),
            }
        )
        checkpoint()
        write_json(output / "history.json", state["history"])
        if interrupt_after == epoch:
            raise KeyboardInterrupt("Requested epoch-boundary recovery drill")
    if state["best_model"] is None:
        raise DataContractError("No completed optimizer epoch")
    save_checkpoint(
        output / "best.pt",
        {
            "schema_version": "full-model-bundle-v1",
            "identity": identity,
            "config": config.to_dict(),
            "model": state["best_model"],
            "epoch": state["best_epoch"],
            "val_loss": state["best_loss"],
            "model_tensor_sha256": tensor_digest(state["best_model"]),
            "train_prevalence": (train.values * train.mask).sum(0) / train.mask.sum(0),
        },
    )
    model.load_state_dict(state["best_model"], strict=True)
    return state


def cohort_report(
    model: AdaptationModel,
    cohort: ImageCohort,
    config: AdaptationConfig,
    prevalence: torch.Tensor,
    protocol: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    logits = infer(model, cohort, config)
    metrics = report_scores(logits, cohort.values, cohort.mask, config.threshold, prevalence)
    metrics["group_bootstrap"] = group_bootstrap(
        logits.sigmoid(), cohort.values, cohort.mask, cohort.groups, config.threshold
    )
    metrics["slices"] = slice_reports(
        logits,
        cohort.values,
        cohort.mask,
        cohort.ids,
        cohort.groups,
        protocol.get("slice_enrollment", {}).get(cohort.name, {}),
        config.threshold,
        prevalence,
    )
    rows = []
    for i, record in enumerate(cohort.records):
        score = logits[i].sigmoid().tolist()
        rows.append(
            {
                "sample_id": record.sample_id,
                "source_id": record.source.source_id,
                "group_id": cohort.groups[i],
                "split": record.usage,
                "scores": score,
                "targets": list(record.target_values),
                "mask": list(record.target_mask),
                "target_order": config.target_order,
                "decisions": [s >= config.threshold for s in score],
            }
        )
    return metrics, rows


def runtime_signature(env: dict[str, Any]) -> str:
    return digest_json(
        {key: env[key] for key in ("python", "platform", "packages", "threads", "device")}
    )


def run_adaptation(
    config_path: Path,
    output: Path,
    workspace: Path,
    *,
    resume: bool = False,
    interrupt_after: int | None = None,
) -> RunRecord:
    config = load_adaptation_config(config_path)
    workspace, output = workspace.resolve(), output.resolve()
    verify_adaptation_approval(config, workspace)
    if not output.is_relative_to(workspace / "outputs"):
        raise DataContractError("Adaptation output must be under workspace outputs")
    if not resume:
        output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(config.threads)
    torch.use_deterministic_algorithms(True)
    random.seed(config.seed)
    np.random.seed(config.seed)
    torch.manual_seed(config.seed)
    code, env = code_identity(), environment()
    identity = digest_json(
        {"config": config.to_dict(), "code": code["sha256"], "runtime": runtime_signature(env)}
    )
    if resume:
        record = RunRecord(**json.loads((output / "run.json").read_text(encoding="utf-8")))
        if (
            record.status not in {"FAILED", "OOM", "INTERRUPTED"}
            or record.config_sha256 != digest_json(config.to_dict())
            or record.code_sha256 != code["sha256"]
            or runtime_signature(record.environment) != runtime_signature(env)
        ):
            raise DataContractError("Resume run/config/code/environment mismatch")
        checks = json.loads((output / "checksums.json").read_text(encoding="utf-8"))
        for name in (
            "last.pt",
            "initialization.json",
            "resolved-config.json",
            "code-provenance.json",
        ):
            if sha256_file(output / name) != checks.get(name):
                raise DataContractError("Resume checkpoint/artifacts changed")
        record.resumed_at.append(now())
        record.status, record.error = "RUNNING", None
    else:
        train_spec = next(c.data for c in config.cohorts if c.role == "train")
        record = RunRecord(
            config.experiment_id,
            config.owner,
            config.hypothesis,
            digest_json(config.to_dict()),
            code["sha256"],
            env,
            train_spec.dataset_version,
            train_spec.split_version,
            train_spec.encoding_version,
            train_spec.payload_sha256,
            config.weights.sha256,
        )
        write_json(output / "resolved-config.json", config.to_dict())
        write_json(output / "code-provenance.json", code)
        write_json(output / "environment.json", env)
    record.write(output)
    started = time.perf_counter()
    try:
        config.weights_license.verify(workspace)
        cohorts, protocol = prepare_cohorts(config, workspace)
        train = next(c for c in cohorts if c.role == "train")
        selection = next(c for c in cohorts if c.role == "selection")
        model = AdaptationModel(
            config,
            weights=config.weights.verify(workspace),
            initial_head=config.head_initialization.verify(workspace),
        )
        result = train_images(
            model,
            train,
            selection,
            config,
            output,
            identity,
            resume=resume,
            interrupt_after=interrupt_after,
            remaining_seconds=config.wall_time_seconds
            - record.elapsed_seconds
            - (time.perf_counter() - started),
        )
        prevalence = (train.values * train.mask).sum(0) / train.mask.sum(0)
        metrics = {}
        for cohort in cohorts:
            if record.elapsed_seconds + time.perf_counter() - started >= config.wall_time_seconds:
                raise TimeoutError("Approved wall-time budget exhausted during reporting")
            metrics[cohort.name], predictions = cohort_report(
                model, cohort, config, prevalence, protocol
            )
            write_json(output / f"predictions-{cohort.name}.json", predictions)
        if record.elapsed_seconds + time.perf_counter() - started >= config.wall_time_seconds:
            raise TimeoutError("Approved wall-time budget exhausted during reporting")
        write_json(output / "metrics.json", metrics)
        write_curve(output, result["history"])
        write_json(
            output / "bundle.json",
            {
                "schema_version": "full-model-bundle-v1",
                "checkpoint_sha256": sha256_file(output / "best.pt"),
                "config_sha256": digest_json(config.to_dict()),
                "code_sha256": code["sha256"],
                "runtime_sha256": runtime_signature(env),
                "identity": identity,
                "license_pin": config.to_dict()["weights_license"],
                "pretrained_required_for_reload": False,
                "target_order": config.target_order,
                "threshold": config.threshold,
            },
        )
        record.best_epoch, record.completed_epochs = result["best_epoch"], result["epoch"]
        record.status, record.decision = "FINISHED", "continue_research_only"
        record.observation = (
            "Matched image experiment finished; no final test or promotion inferred."
        )
    except BaseException as error:
        record.status = (
            "INTERRUPTED" if isinstance(error, (KeyboardInterrupt, TimeoutError)) else "FAILED"
        )
        if isinstance(error, MemoryError) or "out of memory" in str(error).lower():
            record.status = "OOM"
        record.error = f"{type(error).__name__}: {error}"
        record.observation = "No automatic config/batch change; resume restarts uncommitted epoch."
        if (output / "last.pt").is_file():
            checkpoint = torch.load(output / "last.pt", map_location="cpu", weights_only=True)
            record.completed_epochs, record.best_epoch = (
                checkpoint["epoch"],
                checkpoint["best_epoch"],
            )
        raise
    finally:
        record.ended_at = now()
        record.elapsed_seconds += time.perf_counter() - started
        record.peak_rss_bytes = peak_rss()
        record.write(output)
        checksum_artifacts(output)
    return record
