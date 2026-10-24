"""Exact score-boundary calibration for V4, with explicit null precision."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import TARGET_ORDER

from .adaptation_metrics import enrich_v11_support_and_gates
from .metrics import evaluate_scores, validate_arrays


def evaluate_pair(
    scores: torch.Tensor, values: torch.Tensor, mask: torch.Tensor,
    thresholds: tuple[float, float], groups: Sequence[str] | None = None,
) -> dict[str, Any]:
    scores, values, mask = scores.detach().cpu().double(), values.cpu(), mask.cpu()
    validate_arrays(scores, values, mask)
    if (len(thresholds) != 2 or any(not math.isfinite(t) or not 0 <= t <= math.nextafter(1., 2.)
                                   for t in thresholds)):
        raise DataContractError("Invalid exact probability decision boundary")
    result = evaluate_scores(scores, values, mask, .5)
    result.pop("threshold")
    result["thresholds"] = dict(zip(TARGET_ORDER, thresholds, strict=True))
    for c, name in enumerate(TARGET_ORDER):
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
        enrich_v11_support_and_gates(result, values, mask, groups)
    return result


def calibrate_exact(
    scores: torch.Tensor, values: torch.Tensor, mask: torch.Tensor,
) -> tuple[float, float]:
    scores, values, mask = scores.detach().cpu().double(), values.cpu(), mask.cpu()
    validate_arrays(scores, values, mask)
    if not ((scores >= 0) & (scores <= 1)).all():
        raise DataContractError("Scores outside [0,1]")
    chosen = []
    for c in range(2):
        s, y = scores[mask[:, c], c], values[mask[:, c], c].bool()
        p, n = int(y.sum()), int((~y).sum())
        if not p or not n:
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
            gap = max(0., .8-(precision or 0.))+max(0., .8-recall)+max(0., fpr-.2)
            tail = (-abs(threshold-.5), -threshold)
            if precision is not None and precision >= .8 and recall >= .8 and fpr <= .2:
                feasible.append(((f1, min(precision-.8, recall-.8, .2-fpr), *tail), threshold))
            fallback.append(((-gap, f1, *tail), threshold))
        chosen.append(max(feasible or fallback)[1])
    return (chosen[0], chosen[1])
