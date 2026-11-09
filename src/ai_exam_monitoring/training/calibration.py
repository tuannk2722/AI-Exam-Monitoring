"""Exact score-boundary calibration for V4, with explicit null precision."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import TARGET_ORDER

from .adaptation_metrics import enrich_v11_support_and_gates
from .metrics import evaluate_scores, validate_arrays


def evaluate_pair(
    scores: torch.Tensor, values: torch.Tensor, mask: torch.Tensor,
    thresholds: Sequence[float], groups: Sequence[str] | None = None,
    *, target_order: Sequence[str] = TARGET_ORDER,
) -> dict[str, Any]:
    scores, values, mask = scores.detach().cpu().double(), values.cpu(), mask.cpu()
    validate_arrays(scores, values, mask, target_order=target_order)
    if (len(thresholds) != len(target_order)
            or any(not math.isfinite(t) or not 0 <= t <= math.nextafter(1., 2.)
                                   for t in thresholds)):
        raise DataContractError("Invalid exact probability decision boundary")
    result = evaluate_scores(scores, values, mask, .5, target_order=target_order)
    result.pop("threshold")
    result["thresholds"] = dict(zip(target_order, thresholds, strict=True))
    for c, name in enumerate(target_order):
        row = result["targets"][name]
        known = mask[:, c]
        pred, y = scores[known, c] >= thresholds[c], values[known, c].bool()
        tp, fp = int((pred & y).sum()), int((pred & ~y).sum())
        p, n = row["positive"], row["negative"]
        valid = p > 0 and n > 0
        row.update(tp=tp, fp=fp, fn=p-tp, tn=n-fp,
                   precision=tp/(tp+fp) if valid and tp+fp else None,
                   recall=tp/p if valid else None,
                   f1=2*tp/(p+tp+fp) if valid else None,
                   fpr=fp/n if n else None,
                   reason=("missing_positive_or_negative" if not valid else
                           "precision_undefined_no_positive_predictions" if not tp+fp else None))
    if groups is not None:
        if len(groups) != len(scores):
            raise DataContractError("Group length mismatch")
        if tuple(target_order) == TARGET_ORDER:
            enrich_v11_support_and_gates(result, values, mask, groups)
    return result


def calibrate_exact(
    scores: torch.Tensor, values: torch.Tensor, mask: torch.Tensor,
    *, target_order: Sequence[str] = TARGET_ORDER,
    objectives: Mapping[str, Mapping[str, float]] | None = None,
) -> tuple[float, ...]:
    scores, values, mask = scores.detach().cpu().double(), values.cpu(), mask.cpu()
    validate_arrays(scores, values, mask, target_order=target_order)
    if not ((scores >= 0) & (scores <= 1)).all():
        raise DataContractError("Scores outside [0,1]")
    chosen = []
    if objectives is None and tuple(target_order) != TARGET_ORDER:
        raise DataContractError("Five-target calibration requires explicit protocol objectives")
    if objectives is not None:
        validate_objectives(objectives, target_order)
    for c, name in enumerate(target_order):
        goals = (objectives[name] if objectives is not None else
                 {"precision_min": .8, "recall_min": .8, "fpr_max": .2})
        precision_min, recall_min, fpr_max = (
            goals["precision_min"], goals["recall_min"], goals["fpr_max"])
        s, y = scores[mask[:, c], c], values[mask[:, c], c].bool()
        p, n = int(y.sum()), int((~y).sum())
        if not p or not n:
            if tuple(target_order) != TARGET_ORDER:
                raise DataContractError("Calibration requires P/N support for every target")
            chosen.append(.5)
            continue
        candidates = sorted({0., .5, math.nextafter(1., 2.), *s.tolist()})
        feasible, fallback = [], []
        for threshold in candidates:
            pred = s >= threshold
            tp, fp = int((pred & y).sum()), int((pred & ~y).sum())
            precision = tp/(tp+fp) if tp+fp else None
            recall, fpr = tp/p, fp/n
            f1 = 2*tp/(p+tp+fp)
            gap = (max(0., precision_min-(precision or 0.))
                   + max(0., recall_min-recall)+max(0., fpr-fpr_max))
            tail = (-abs(threshold-.5), -threshold)
            if (precision is not None and precision >= precision_min
                    and recall >= recall_min and fpr <= fpr_max):
                feasible.append(((f1, min(precision-precision_min, recall-recall_min,
                                         fpr_max-fpr), *tail), threshold))
            fallback.append(((-gap, f1, *tail), threshold))
        chosen.append(max(feasible or fallback)[1])
    return tuple(chosen)


def validate_objectives(objectives: Mapping[str, Mapping[str, float]] | None,
                        target_order: Sequence[str]) -> None:
    """Required variables, not default quality/release gates."""
    if not isinstance(objectives, Mapping) or set(objectives) != set(target_order):
        raise DataContractError("Calibration objectives must cover exact target names")
    for goals in objectives.values():
        if (not isinstance(goals, Mapping)
                or set(goals) != {"precision_min", "recall_min", "fpr_max"}
                or any(type(v) not in (float, int) or not math.isfinite(v) or not 0 <= v <= 1
                       for v in goals.values())):
            raise DataContractError("Invalid calibration objectives")
