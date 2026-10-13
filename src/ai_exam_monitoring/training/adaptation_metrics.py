"""Versioned mini-batch loss, support-aware diagnostics and whole-group intervals."""

from __future__ import annotations

from collections.abc import Sequence
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
            loss = (
                loss
                + F.binary_cross_entropy_with_logits(
                    logits[known, target], values[known, target], reduction="sum"
                )
                / known_counts[target]
            )
    return loss * population / (2 * len(logits))


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
            row["evidenced_groups"] = len(known_groups)
            row["support_status"] = (
                "AVAILABLE"
                if row["positive"] >= 20 and row["negative"] >= 20 and len(known_groups) >= 3
                else "INCONCLUSIVE"
            )
        result[name] = report
    return result
