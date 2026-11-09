"""Known-target-only objectives and explicit-support classifier metrics."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Any

import torch
from torch.nn import functional as F

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import MULTILABEL_TARGET_ORDER, TARGET_ORDER


def validate_arrays(scores: torch.Tensor, values: torch.Tensor, mask: torch.Tensor,
                    *, target_order: Sequence[str] = TARGET_ORDER) -> None:
    if tuple(target_order) not in (TARGET_ORDER, MULTILABEL_TARGET_ORDER):
        raise DataContractError("Unsupported target contract/order")
    if (scores.ndim != 2 or scores.shape[1] != len(target_order) or scores.shape != values.shape
            or mask.shape != values.shape or mask.dtype != torch.bool or len(scores) == 0):
        raise DataContractError("Expected nonempty [N,K] scores/values and boolean mask")
    if not torch.isfinite(scores).all() or not torch.isfinite(values[mask]).all():
        raise DataContractError("Nonfinite scores or known labels")
    if not ((values[mask] == 0) | (values[mask] == 1)).all():
        raise DataContractError("Known targets must be binary")


def masked_loss(logits: torch.Tensor, values: torch.Tensor, mask: torch.Tensor,
                *, target_order: Sequence[str] = TARGET_ORDER) -> torch.Tensor:
    validate_arrays(logits, values, mask, target_order=target_order)
    losses = []
    for c in range(len(target_order)):
        known = mask[:, c]
        if not known.any():
            raise DataContractError("Full-batch objective needs known support for each target")
        losses.append(F.binary_cross_entropy_with_logits(logits[known, c], values[known, c]))
    return torch.stack(losses).mean()


def average_precision(values: torch.Tensor, scores: torch.Tensor) -> float:
    """Non-interpolated AP, grouping equal scores before precision/recall updates."""
    order = torch.argsort(scores, descending=True, stable=True)
    y, s = values[order].double(), scores[order]
    ends = torch.cat((s[:-1] != s[1:], torch.tensor([True])))
    indices = torch.arange(1, len(y) + 1, dtype=torch.float64)[ends]
    positives = y.cumsum(0)[ends]
    recall = positives / y.sum()
    delta = torch.diff(recall, prepend=torch.zeros(1, dtype=torch.float64))
    return float((delta * positives / indices).sum())


@dataclass(frozen=True)
class TargetMetrics:
    positive: int
    negative: int
    unknown: int
    tp: int
    fp: int
    fn: int
    tn: int
    ap: float | None
    precision: float | None
    recall: float | None
    f1: float | None
    reason: str | None


def evaluate_scores(scores: torch.Tensor, values: torch.Tensor, mask: torch.Tensor,
                    threshold: float, *, target_order: Sequence[str] = TARGET_ORDER
                    ) -> dict[str, Any]:
    scores, values, mask = scores.detach().cpu(), values.cpu(), mask.cpu()
    validate_arrays(scores, values, mask, target_order=target_order)
    if not 0 < threshold < 1 or not ((scores >= 0) & (scores <= 1)).all():
        raise DataContractError("Scores and threshold must be probabilities")
    result = {}
    aps = []
    for c, target in enumerate(target_order):
        known = mask[:, c]
        y, s = values[known, c].bool(), scores[known, c]
        predicted = s >= threshold
        p, n = int(y.sum()), int((~y).sum())
        tp, fp = int((predicted & y).sum()), int((predicted & ~y).sum())
        fn, tn = p - tp, n - fp
        valid = p > 0 and n > 0
        ap = average_precision(y.float(), s) if valid else None
        precision = tp / (tp + fp) if valid and tp + fp else None
        recall = tp / p if valid else None
        f1 = 2 * tp / (2 * tp + fp + fn) if valid else None
        reason = ("missing_positive_or_negative" if not valid else
                  "precision_undefined_no_positive_predictions" if precision is None else None)
        result[target] = asdict(TargetMetrics(p, n, int((~known).sum()), tp, fp, fn, tn,
                                             ap, precision, recall, f1, reason))
        if ap is not None:
            aps.append(ap)
    both = mask.all(1)
    co_positive = int((values[both].bool().all(1)).sum())
    return {"targets": result,
            "macro_ap": sum(aps) / len(target_order) if len(aps) == len(target_order) else None,
            "threshold": threshold, "records": len(scores),
            "cooccurrence": ({"fully_known": int(both.sum()), "positive": co_positive,
                              "metric": None, "reason": "insufficient_pilot_support"}
                             if tuple(target_order) == TARGET_ORDER else
                             {"metric": None, "reason": "not_defined_for_five_target_contract"})}
