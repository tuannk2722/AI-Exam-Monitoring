"""Versioned mini-batch loss, support-aware diagnostics and whole-group intervals."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import TARGET_ORDER

from .metrics import evaluate_scores, masked_loss, validate_arrays


def minibatch_loss(
    logits: torch.Tensor,
    values: torch.Tensor,
    mask: torch.Tensor,
    population: int,
    known_counts: torch.Tensor,
    *,
    pos_weight: tuple[float, float] = (1.0, 1.0),
    label_smoothing: float = 0.0,
) -> torch.Tensor:
    validate_arrays(logits, values, mask)
    if (
        type(population) is not int
        or population < len(logits)
        or known_counts.shape != (2,)
        or not torch.isfinite(known_counts).all()
        or not ((known_counts > 0) & (known_counts <= population)).all()
        or not (known_counts == known_counts.round()).all()
        or not mask.any(1).all()
        or (mask.sum(0) > known_counts).any()
    ):
        raise DataContractError("Invalid population support or all-unknown supervision record")
    loss = logits.sum() * 0
    for target in range(2):
        known = mask[:, target]
        if known.any():
            y = values[known, target]
            if label_smoothing > 0.0:
                y = y * (1.0 - label_smoothing) + 0.5 * label_smoothing
            pw_val = float(pos_weight[target])
            if pw_val != 1.0:
                pw = torch.tensor(pw_val, dtype=logits.dtype, device=logits.device)
                term = F.binary_cross_entropy_with_logits(
                    logits[known, target], y, pos_weight=pw, reduction="sum"
                )
            else:
                term = F.binary_cross_entropy_with_logits(
                    logits[known, target], y, reduction="sum"
                )
            loss = loss + term / known_counts[target]
    return loss * population / (2 * len(logits))


def enrich_v11_support_and_gates(
    report: dict[str, Any],
    values: torch.Tensor,
    mask: torch.Tensor,
    groups: Sequence[str],
) -> dict[str, Any]:
    both_gates_pass = True
    for c, target_name in enumerate(TARGET_ORDER):
        row = report["targets"][target_name]
        row["fpr"] = row["fp"] / row["negative"] if row["negative"] else None
        pos_groups = {
            groups[i]
            for i in range(len(groups))
            if bool(mask[i, c]) and float(values[i, c]) == 1.0
        }
        neg_groups = {
            groups[i]
            for i in range(len(groups))
            if bool(mask[i, c]) and float(values[i, c]) == 0.0
        }
        known_groups = pos_groups | neg_groups
        row["positive_groups"] = len(pos_groups)
        row["negative_groups"] = len(neg_groups)
        row["evidenced_groups"] = len(known_groups)
        support_ok = (
            row["positive"] >= 30
            and row["negative"] >= 30
            and len(pos_groups) >= 5
            and len(neg_groups) >= 5
        )
        row["v11_support_gate_status"] = "AVAILABLE" if support_ok else "INCONCLUSIVE"
        prec = row.get("precision")
        rec = row.get("recall")
        fpr = row.get("fpr")
        quality_ok = bool(
            support_ok
            and prec is not None
            and prec >= 0.80
            and rec is not None
            and rec >= 0.80
            and fpr is not None
            and fpr <= 0.20
        )
        row["v11_quality_gate_pass"] = quality_ok if support_ok else None
        if not quality_ok:
            both_gates_pass = False
    report["v11_all_targets_pass_gates"] = both_gates_pass
    return report


def evaluate_scores_per_target_thresholds(
    scores: torch.Tensor,
    values: torch.Tensor,
    mask: torch.Tensor,
    thresholds: tuple[float, float],
    groups: Sequence[str] | None = None,
) -> dict[str, Any]:
    scores, values, mask = scores.detach().cpu(), values.cpu(), mask.cpu()
    validate_arrays(scores, values, mask)
    if len(thresholds) != 2 or any(not (0.0 < float(t) < 1.0) for t in thresholds):
        raise DataContractError("Per-target thresholds must be in (0, 1)")
    p0 = evaluate_scores(scores, values, mask, float(thresholds[0]))
    p1 = evaluate_scores(scores, values, mask, float(thresholds[1]))
    combined: dict[str, Any] = {
        "targets": {
            TARGET_ORDER[0]: p0["targets"][TARGET_ORDER[0]],
            TARGET_ORDER[1]: p1["targets"][TARGET_ORDER[1]],
        },
        "macro_ap": p0["macro_ap"],
        "thresholds": {
            TARGET_ORDER[0]: float(thresholds[0]),
            TARGET_ORDER[1]: float(thresholds[1]),
        },
        "records": len(scores),
        "cooccurrence": p0["cooccurrence"],
    }
    for target_name in TARGET_ORDER:
        row = combined["targets"][target_name]
        row["fpr"] = row["fp"] / row["negative"] if row["negative"] else None
    if groups is not None:
        enrich_v11_support_and_gates(combined, values, mask, groups)
    return combined


def calibrate_optimal_thresholds(
    scores: torch.Tensor,
    values: torch.Tensor,
    mask: torch.Tensor,
    groups: Sequence[str] | None = None,
) -> dict[str, Any]:
    scores, values, mask = scores.detach().cpu(), values.cpu(), mask.cpu()
    validate_arrays(scores, values, mask)
    chosen: list[float] = []
    grid = [round(0.05 + 0.01 * k, 4) for k in range(90)]
    for c in range(2):
        known = mask[:, c]
        y = values[known, c].bool()
        s = scores[known, c]
        unique_s = sorted({float(v) for v in s.tolist() if 0.05 <= float(v) <= 0.95})
        candidates = sorted(set(grid + unique_s))
        p_cnt = int(y.sum())
        n_cnt = int((~y).sum())
        if p_cnt == 0 or n_cnt == 0:
            chosen.append(0.5)
            continue
        best_pass_t: float | None = None
        best_pass_key: tuple[float, float, float] = (-1.0, -1.0, -1.0)
        best_fallback_t = 0.5
        best_fallback_key: tuple[float, float, float] = (-float("inf"), -1.0, -1.0)
        for t in candidates:
            pred = s >= t
            tp = int((pred & y).sum())
            fp = int((pred & ~y).sum())
            fn = p_cnt - tp
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / p_cnt
            fpr = fp / n_cnt
            f1 = (2.0 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
            if prec >= 0.80 and rec >= 0.80 and fpr <= 0.20:
                margin = min(prec - 0.80, rec - 0.80, 0.20 - fpr)
                pass_key = (round(f1, 6), round(margin, 6), -abs(t - 0.5))
                if pass_key > best_pass_key:
                    best_pass_key = pass_key
                    best_pass_t = float(t)
            shortfall = (
                max(0.0, 0.80 - prec)
                + max(0.0, 0.80 - rec)
                + max(0.0, fpr - 0.20)
            )
            fallback_key = (-round(shortfall, 6), round(f1, 6), -abs(t - 0.5))
            if fallback_key > best_fallback_key:
                best_fallback_key = fallback_key
                best_fallback_t = float(t)
        chosen.append(best_pass_t if best_pass_t is not None else best_fallback_t)
    pair = (chosen[0], chosen[1])
    return {
        "thresholds": {TARGET_ORDER[0]: pair[0], TARGET_ORDER[1]: pair[1]},
        "threshold_list": [pair[0], pair[1]],
        "evaluation": evaluate_scores_per_target_thresholds(
            scores, values, mask, pair, groups=groups
        ),
    }


def build_fp_fn_gallery(
    records: Sequence[Any],
    groups: Sequence[str],
    scores: torch.Tensor,
    thresholds: tuple[float, float],
    *,
    slice_membership: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    scores_cpu = scores.detach().cpu()
    new270_set = set(slice_membership.get("new270_val_74", ())) if slice_membership else set()
    unexp_set = set(slice_membership.get("unexposed_val_88", ())) if slice_membership else set()
    gallery: dict[str, list[dict[str, Any]]] = {}
    for c, target_name in enumerate(TARGET_ORDER):
        t = float(thresholds[c])
        errors: list[dict[str, Any]] = []
        for i, record in enumerate(records):
            if not record.target_mask[c]:
                continue
            truth = int(record.target_values[c])
            prob = float(scores_cpu[i, c])
            pred = 1 if prob >= t else 0
            if pred == truth:
                continue
            err_type = "FP" if pred == 1 and truth == 0 else "FN"
            area_ratio = None
            if record.crop is not None:
                pb = record.crop.person_box
                cb = record.crop.context_box
                p_area = (pb.xmax - pb.xmin) * (pb.ymax - pb.ymin)
                c_area = max(1, (cb.xmax - cb.xmin) * (cb.ymax - cb.ymin))
                area_ratio = round(p_area / c_area, 4)
            errors.append(
                {
                    "sample_id": record.sample_id,
                    "source_id": record.source.source_id,
                    "group_id": groups[i],
                    "error_type": err_type,
                    "truth": truth,
                    "predicted": pred,
                    "score": round(prob, 6),
                    "threshold": round(t, 4),
                    "margin": round(abs(prob - t), 6),
                    "person_context_area_ratio": area_ratio,
                    "in_new270": record.sample_id in new270_set,
                    "in_unexposed_val_88": record.sample_id in unexp_set,
                }
            )
        errors.sort(key=lambda item: (-float(item["margin"]), str(item["sample_id"])))
        gallery[target_name] = errors
    return gallery


def report_scores(
    logits: torch.Tensor,
    values: torch.Tensor,
    mask: torch.Tensor,
    threshold: float,
    prevalence: torch.Tensor,
) -> dict[str, Any]:
    result = evaluate_scores(logits.sigmoid(), values, mask, threshold)
    result["macro_masked_bce"] = (
        float(masked_loss(logits, values, mask)) if mask.any(0).all() else None
    )
    for target_name in TARGET_ORDER:
        row = result["targets"][target_name]
        row["fpr"] = row["fp"] / row["negative"] if row["negative"] else None
    if (
        prevalence.shape != (2,)
        or not torch.isfinite(prevalence).all()
        or not ((prevalence >= 0) & (prevalence <= 1)).all()
    ):
        raise DataContractError("Invalid train-only prevalence")
    constant = evaluate_scores(prevalence.expand_as(logits), values, mask, threshold)
    losses = []
    for target in range(2):
        known = mask[:, target]
        if known.any():
            # Exact Bernoulli cross entropy: incompatible p=0/1 yields unavailable,
            # not a clipped baseline with artificially finite loss.
            y = values[known, target]
            p = prevalence[target].double()
            terms = torch.where(y.bool(), -p.log(), -torch.log1p(-p))
            losses.append(float(terms.mean()))
    constant["macro_masked_bce"] = (
        sum(losses) / 2 if len(losses) == 2 and all(np.isfinite(v) for v in losses) else None
    )
    result["constant_train_prevalence"] = constant
    return result


def group_bootstrap(
    scores: torch.Tensor,
    values: torch.Tensor,
    mask: torch.Tensor,
    groups: Sequence[str],
    threshold: float,
    *,
    samples: int = 5000,
    seed: int = 42,
) -> dict[str, Any]:
    validate_arrays(scores, values, mask)
    if (
        len(groups) != len(scores)
        or any(not isinstance(g, str) or not g for g in groups)
        or type(samples) is not int
        or samples <= 0
        or not 0 < threshold < 1
        or not ((scores >= 0) & (scores <= 1)).all()
    ):
        raise DataContractError("Invalid bootstrap groups/scores/protocol")
    unique = sorted(set(groups))
    # Aggregate confusion per whole group; repeated group draws repeat its entire mass.
    statistics = np.zeros((len(unique), 2, 4), dtype=np.int64)
    for i, group in enumerate(unique):
        indices = [j for j, g in enumerate(groups) if g == group]
        for target in range(2):
            selected = mask[indices, target]
            y = values[indices, target][selected].bool()
            predicted = scores[indices, target][selected] >= threshold
            statistics[i, target] = [
                int((predicted & y).sum()),
                int((predicted & ~y).sum()),
                int((~predicted & y).sum()),
                int((~predicted & ~y).sum()),
            ]
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(unique), size=(samples, len(unique)))
    totals = statistics[draws].sum(1)
    output: dict[str, Any] = {
        "groups": len(unique),
        "samples": samples,
        "seed": seed,
        "method": "whole_group_percentile_95",
        "targets": {},
    }
    for target, name in enumerate(TARGET_ORDER):
        tp, fp, fn, tn = totals[:, target].T
        metrics = {}
        for metric, numerator, denominator in (
            ("precision", tp, tp + fp),
            ("recall", tp, tp + fn),
            ("fpr", fp, fp + tn),
        ):
            valid = denominator > 0
            valid_fraction = float(valid.mean())
            eligible = len(unique) >= 2 and valid_fraction >= 0.95
            interval = (
                np.percentile(numerator[valid] / denominator[valid], [2.5, 97.5]).tolist()
                if eligible
                else None
            )
            metrics[metric] = {
                "interval": interval,
                "valid_resamples": int(valid.sum()),
                "valid_fraction": valid_fraction,
                "status": "AVAILABLE" if eligible else "INCONCLUSIVE",
            }
        output["targets"][name] = metrics
    return output


def slice_reports(
    logits: torch.Tensor,
    values: torch.Tensor,
    mask: torch.Tensor,
    ids: Sequence[str],
    groups: Sequence[str],
    enrollment: dict[str, list[str]],
    threshold: float,
    prevalence: torch.Tensor,
) -> dict[str, Any]:
    result = {}
    for name, members in enrollment.items():
        if not members or len(set(members)) != len(members) or not set(members) <= set(ids):
            raise DataContractError("Invalid frozen slice membership")
        indices = [i for i, ident in enumerate(ids) if ident in set(members)]
        report = report_scores(
            logits[indices], values[indices], mask[indices], threshold, prevalence
        )
        for target, target_name in enumerate(TARGET_ORDER):
            row = report["targets"][target_name]
            known_groups = {groups[i] for i in indices if mask[i, target]}
            pos_groups = {
                groups[i] for i in indices if mask[i, target] and float(values[i, target]) == 1.0
            }
            neg_groups = {
                groups[i] for i in indices if mask[i, target] and float(values[i, target]) == 0.0
            }
            row["evidenced_groups"] = len(known_groups)
            row["positive_groups"] = len(pos_groups)
            row["negative_groups"] = len(neg_groups)
            row["support_status"] = (
                "AVAILABLE"
                if row["positive"] >= 20 and row["negative"] >= 20 and len(known_groups) >= 3
                else "INCONCLUSIVE"
            )
            row["v11_support_gate_status"] = (
                "AVAILABLE"
                if (
                    row["positive"] >= 30
                    and row["negative"] >= 30
                    and len(pos_groups) >= 5
                    and len(neg_groups) >= 5
                )
                else "INCONCLUSIVE"
            )
        result[name] = report
    return result

