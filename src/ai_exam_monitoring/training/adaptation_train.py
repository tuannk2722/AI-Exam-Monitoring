"""Matched full-image training with global masked objective and epoch-boundary resume."""

from __future__ import annotations

import copy
import json
import math
import random
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .adaptation_config import (
    AdaptationConfig,
    E005AdaptationConfig,
    ResearchAdaptationConfig,
    load_adaptation_config,
    verify_adaptation_approval,
)
from .adaptation_data import ImageCohort, prepare_cohorts
from .adaptation_metrics import (
    build_fp_fn_gallery,
    calibrate_optimal_thresholds,
    enrich_v11_support_and_gates,
    evaluate_scores_per_target_thresholds,
    group_bootstrap,
    minibatch_loss,
    report_scores,
    slice_reports,
)
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
from .metrics import evaluate_scores, masked_loss
from .train import peak_rss, restore_rng, rng_state, write_curve


def infer(model: AdaptationModel, cohort: ImageCohort, config: AdaptationConfig) -> torch.Tensor:
    model.eval()
    logits = []
    is_v3 = isinstance(config, E005AdaptationConfig)
    with torch.no_grad():
        for start in range(0, len(cohort.ids), config.batch_size):
            indices = list(range(start, min(start + config.batch_size, len(cohort.ids))))
            batch_in = (
                cohort.model_batch(indices, config, train_mode=False)
                if is_v3
                else cohort.batch(indices, config)
            )
            logits.append(model(batch_in).cpu())
    result = torch.cat(logits)
    if not torch.isfinite(result).all():
        raise DataContractError("Nonfinite cohort logits")
    return result


def early_diagnostic(
    model: AdaptationModel, cohorts: list[ImageCohort], config: AdaptationConfig
) -> dict[str, Any]:
    """Measure without changing RNG, any module mode, weights, optimizer or sampler."""
    saved_rng = rng_state()
    modes = [(module, module.training) for module in model.modules()]
    try:
        result = {}
        for cohort in cohorts:
            logits = infer(model, cohort, config)
            metrics = evaluate_scores(
                logits.sigmoid(), cohort.values, cohort.mask, config.threshold
            )
            result[cohort.name] = {
                "macro_masked_bce": float(masked_loss(logits, cohort.values, cohort.mask)),
                "macro_ap": metrics["macro_ap"],
            }
        return result
    finally:
        restore_rng(saved_rng)
        for module, mode in modes:
            module.training = mode


def _compute_epoch_lrs(
    config: E005AdaptationConfig, epoch: int
) -> tuple[float, float]:
    if config.trainable_scope == "head_only":
        if config.lr_scheduler == "cosine" and config.max_epochs > 1:
            progress = (epoch - 1) / max(1, config.max_epochs - 1)
            factor = config.min_lr_ratio + 0.5 * (1.0 - config.min_lr_ratio) * (
                1.0 + math.cos(math.pi * progress)
            )
            return (config.head_learning_rate * factor, 0.0)
        return (config.head_learning_rate, 0.0)
    if epoch <= config.warmup_epochs:
        return (config.head_learning_rate, 0.0)
    if config.lr_scheduler == "cosine":
        ft_epochs = max(1, config.max_epochs - config.warmup_epochs)
        t_cur = epoch - config.warmup_epochs - 1
        t_max = max(1, ft_epochs - 1)
        factor = (
            config.min_lr_ratio
            + 0.5 * (1.0 - config.min_lr_ratio) * (1.0 + math.cos(math.pi * t_cur / t_max))
            if ft_epochs > 1
            else 1.0
        )
        return (config.head_learning_rate * factor, config.layer4_learning_rate * factor)
    return (config.head_learning_rate, config.layer4_learning_rate)


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
    use_ap_selection = (
        isinstance(config, E005AdaptationConfig) and config.selection_metric == "val_macro_ap"
    )
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
        "early_reference": -float("inf") if use_ap_selection else float("inf"),
        "stale": 0,
        "history": [],
        "parameter_groups": names,
        "sampler_permutation": [],
        "sampler_cursor": 0,
        "resume_semantics": "restart_uncommitted_epoch_from_last_atomic_epoch_boundary",
    }
    if isinstance(config, E005AdaptationConfig):
        state["best_val_macro_ap"] = -float("inf")
        state["selection_metric"] = config.selection_metric
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
        provenance = (
            {"head_provenance": config.to_dict()["head_provenance"]}
            if isinstance(config, ResearchAdaptationConfig) else {}
        )
        write_json(
            output / "initialization.json",
            {
                "head_tensor_sha256": tensor_digest(model.network.fc.state_dict()),
                "pretrained_sha256": config.weights.sha256,
                "initial_head_file_sha256": config.head_initialization.sha256,
                "parameter_groups": names,
                "seed": config.seed,
                **provenance,
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
    research = isinstance(config, ResearchAdaptationConfig)
    if research:
        diagnostic_path = output / "early-diagnostics.json"
        diagnostics = (
            json.loads(diagnostic_path.read_text(encoding="utf-8"))
            if resume and diagnostic_path.exists() else []
        )
        attempt = max((row["attempt"] for row in diagnostics), default=0) + 1

        def diagnose(epoch: int, step: int) -> None:
            if time.perf_counter() >= deadline:
                raise TimeoutError("Approved budget exhausted before diagnostic")
            diagnostics.append({
                "attempt": attempt, "epoch": epoch, "step": step,
                "global_step": state["global_step"],
                "committed_epoch_before_measurement": state["epoch"],
                "diagnostic_only": True,
                "cohorts": early_diagnostic(model, [train, selection], config),
            })
            write_json(diagnostic_path, diagnostics)
            if time.perf_counter() >= deadline:
                raise TimeoutError("Approved budget exhausted during diagnostic")

        if state["epoch"] == 0:
            diagnose(0, 0)
    known = train.mask.sum(0)
    for epoch in range(state["epoch"] + 1, config.max_epochs + 1):
        if state["stale"] >= config.patience:
            break
        stage_name = "legacy"
        head_lr = config.head_learning_rate
        layer4_lr = config.layer4_learning_rate
        if isinstance(config, E005AdaptationConfig):
            stage_name = model.configure_trainable_stage(config, epoch=epoch)
            head_lr, layer4_lr = _compute_epoch_lrs(config, epoch)
            for pg in optimizer.param_groups:
                pg["lr"] = head_lr if pg.get("name") == "head" else layer4_lr
        order = torch.randperm(len(train.ids), generator=generator).tolist()
        model.train()
        for start in range(0, len(order), config.batch_size):
            if time.perf_counter() >= deadline:
                raise TimeoutError("Approved wall-time budget exhausted; config unchanged")
            indices = order[start : start + config.batch_size]
            optimizer.zero_grad(set_to_none=True)
            if isinstance(config, E005AdaptationConfig):
                batch_in = train.model_batch(indices, config, epoch=epoch, train_mode=True)
                logits = model(batch_in)
                loss = minibatch_loss(
                    logits,
                    train.values[indices],
                    train.mask[indices],
                    len(train.ids),
                    known,
                    pos_weight=config.pos_weight,
                    label_smoothing=config.label_smoothing,
                )
            else:
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
            if (isinstance(config, ResearchAdaptationConfig) and epoch == 1
                    and start // config.batch_size + 1 in config.diagnostic_steps):
                diagnose(epoch, start // config.batch_size + 1)
        train_logits = infer(model, train, config)
        val_logits = infer(model, selection, config)
        train_loss = float(masked_loss(train_logits, train.values, train.mask))
        val_loss = float(masked_loss(val_logits, selection.values, selection.mask))
        if time.perf_counter() >= deadline:
            raise TimeoutError("Approved wall-time budget exhausted before epoch commit")
        history_entry: dict[str, Any] = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "permutation_sha256": digest_json([train.ids[i] for i in order]),
        }
        if isinstance(config, E005AdaptationConfig):
            train_eval = evaluate_scores(
                train_logits.sigmoid(), train.values, train.mask, config.threshold
            )
            val_eval = evaluate_scores(
                val_logits.sigmoid(), selection.values, selection.mask, config.threshold
            )
            train_ap = float(train_eval["macro_ap"] or 0.0)
            val_ap = float(val_eval["macro_ap"] or 0.0)
            history_entry.update(
                stage=stage_name,
                head_lr=head_lr,
                layer4_lr=layer4_lr,
                train_macro_ap=train_ap,
                val_macro_ap=val_ap,
            )
            if use_ap_selection:
                prev_best_ap = float(state.get("best_val_macro_ap", -float("inf")))
                if val_ap > prev_best_ap or (
                    val_ap == prev_best_ap and val_loss < state["best_loss"]
                ):
                    state.update(
                        best_val_macro_ap=val_ap,
                        best_loss=val_loss,
                        best_epoch=epoch,
                        best_model=copy.deepcopy(model.state_dict()),
                    )
                if val_ap > state["early_reference"] + config.min_delta:
                    state.update(early_reference=val_ap, stale=0)
                else:
                    state["stale"] += 1
            else:
                if val_loss < state["best_loss"]:
                    state.update(
                        best_val_macro_ap=val_ap,
                        best_loss=val_loss,
                        best_epoch=epoch,
                        best_model=copy.deepcopy(model.state_dict()),
                    )
                if val_loss < state["early_reference"] - config.min_delta:
                    state.update(early_reference=val_loss, stale=0)
                else:
                    state["stale"] += 1
        else:
            if val_loss < state["best_loss"]:
                state.update(
                    best_loss=val_loss,
                    best_epoch=epoch,
                    best_model=copy.deepcopy(model.state_dict()),
                )
            if val_loss < state["early_reference"] - config.min_delta:
                state.update(early_reference=val_loss, stale=0)
            else:
                state["stale"] += 1
        state["epoch"] = epoch
        state["sampler_permutation"], state["sampler_cursor"] = order, len(order)
        state["history"].append(history_entry)
        checkpoint()
        write_json(output / "history.json", state["history"])
        if interrupt_after == epoch:
            raise KeyboardInterrupt("Requested epoch-boundary recovery drill")
    if state["best_model"] is None:
        raise DataContractError("No completed optimizer epoch")
    bundle_payload: dict[str, Any] = {
        "schema_version": "full-model-bundle-v1",
        "identity": identity,
        "config": config.to_dict(),
        "model": state["best_model"],
        "epoch": state["best_epoch"],
        "val_loss": state["best_loss"],
        "model_tensor_sha256": tensor_digest(state["best_model"]),
        "train_prevalence": (train.values * train.mask).sum(0) / train.mask.sum(0),
    }
    if isinstance(config, E005AdaptationConfig):
        bundle_payload["best_val_macro_ap"] = state.get("best_val_macro_ap")
        bundle_payload["selection_metric"] = config.selection_metric
    save_checkpoint(output / "best.pt", bundle_payload)
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
    enrolled_slices = protocol.get("slice_enrollment", {}).get(cohort.name, {})
    metrics["slices"] = slice_reports(
        logits,
        cohort.values,
        cohort.mask,
        cohort.ids,
        cohort.groups,
        enrolled_slices,
        config.threshold,
        prevalence,
    )
    calibrated_pair: tuple[float, float] | None = None
    if isinstance(config, E005AdaptationConfig):
        enrich_v11_support_and_gates(metrics, cohort.values, cohort.mask, cohort.groups)
        for s_name, members in enrolled_slices.items():
            s_idx = [i for i, ident in enumerate(cohort.ids) if ident in set(members)]
            s_grp = [cohort.groups[i] for i in s_idx]
            enrich_v11_support_and_gates(
                metrics["slices"][s_name], cohort.values[s_idx], cohort.mask[s_idx], s_grp
            )
        by_source: dict[str, Any] = {}
        for source_id in sorted({r.source.source_id for r in cohort.records}):
            src_indices = [
                i for i, r in enumerate(cohort.records) if r.source.source_id == source_id
            ]
            src_groups = [cohort.groups[i] for i in src_indices]
            src_rep = report_scores(
                logits[src_indices],
                cohort.values[src_indices],
                cohort.mask[src_indices],
                config.threshold,
                prevalence,
            )
            enrich_v11_support_and_gates(
                src_rep, cohort.values[src_indices], cohort.mask[src_indices], src_groups
            )
            by_source[source_id] = src_rep
        metrics["by_source"] = by_source
        metrics["fp_fn_gallery_default_threshold"] = build_fp_fn_gallery(
            cohort.records,
            cohort.groups,
            logits.sigmoid(),
            (config.threshold, config.threshold),
            slice_membership=enrolled_slices,
        )
        if config.calibrate_thresholds_on_val:
            cal = calibrate_optimal_thresholds(
                logits.sigmoid(), cohort.values, cohort.mask, groups=cohort.groups
            )
            t_list = cal["threshold_list"]
            calibrated_pair = (float(t_list[0]), float(t_list[1]))
            metrics["calibrated_thresholds"] = cal["thresholds"]
            metrics["calibrated_evaluation"] = cal["evaluation"]
            cal_slices: dict[str, Any] = {}
            for s_name, members in enrolled_slices.items():
                s_idx = [i for i, ident in enumerate(cohort.ids) if ident in set(members)]
                s_grp = [cohort.groups[i] for i in s_idx]
                cal_slices[s_name] = evaluate_scores_per_target_thresholds(
                    logits[s_idx].sigmoid(),
                    cohort.values[s_idx],
                    cohort.mask[s_idx],
                    calibrated_pair,
                    groups=s_grp,
                )
            metrics["calibrated_slices"] = cal_slices
            metrics["fp_fn_gallery_calibrated_threshold"] = build_fp_fn_gallery(
                cohort.records,
                cohort.groups,
                logits.sigmoid(),
                calibrated_pair,
                slice_membership=enrolled_slices,
            )
    rows = []
    for i, record in enumerate(cohort.records):
        score = logits[i].sigmoid().tolist()
        row_dict: dict[str, Any] = {
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
        if calibrated_pair is not None:
            row_dict["calibrated_thresholds"] = [calibrated_pair[0], calibrated_pair[1]]
            row_dict["calibrated_decisions"] = [
                score[0] >= calibrated_pair[0],
                score[1] >= calibrated_pair[1],
            ]
        rows.append(row_dict)
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
