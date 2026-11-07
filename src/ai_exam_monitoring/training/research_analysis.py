"""Paired seed ranking and fixed-threshold, whole-group development analysis."""

from __future__ import annotations

import math
import statistics
from typing import Any

import numpy as np

from ai_exam_monitoring.common.errors import DataContractError


def resolve_arm(arms: dict[str, Any], name: str, seen: tuple[str, ...] = ()) -> dict[str, Any]:
    if name in seen or name not in arms:
        raise DataContractError("Unknown/cyclic campaign arm")
    value = dict(arms[name])
    parent = value.pop("same_as", None)
    return {**(resolve_arm(arms, parent, (*seen, name)) if parent else {}), **value}


def recipe_key(arm: str, metrics: list[dict[str, Any]], arms: dict[str, Any]) -> tuple[Any, ...]:
    if not metrics:
        raise DataContractError("Recipe has no complete seeds")
    both = total = 0
    gaps, aps, losses = [], [], []
    for result in metrics:
        rows = list(result["calibrated_evaluation"]["targets"].values())
        if len(rows) != 2:
            raise DataContractError("Recipe needs two target reports")
        passed = sum(row.get("v11_quality_gate_pass") is True for row in rows)
        both += int(passed == 2)
        total += passed
        gaps.append(sum(max(0., .8-(r["precision"] or 0.))
                        + max(0., .8-(r["recall"] or 0.))
                        + max(0., (r["fpr"] if r["fpr"] is not None else 1.)-.2) for r in rows))
        if result["macro_ap"] is None:
            raise DataContractError("Cannot rank unavailable macro AP")
        aps.append(float(result["macro_ap"]))
        losses.append(float(result["macro_masked_bce"]))
    config = resolve_arm(arms, arm)
    size = 86 if config["encoder"] == "dinov2_vitb14" else 21
    return (-both, -total, statistics.mean(gaps), -statistics.mean(aps),
            statistics.mean(losses), size, config["image_size"], arm)


def summarize_seeds(results: dict[int, dict[str, Any]]) -> dict[str, Any]:
    rows = list(results.values())
    fields = {"macro_ap": [float(r["macro_ap"]) for r in rows],
              "raw_masked_bce": [float(r["macro_masked_bce"]) for r in rows]}
    for target in ("phone_use", "looking_around"):
        for metric in ("ap", "precision", "recall", "f1", "fpr"):
            values = [r["calibrated_evaluation"]["targets"][target][metric] for r in rows]
            fields[target+"."+metric] = [float(v) for v in values if v is not None]
    return {name: {"mean": statistics.mean(values) if values else None,
                   "sample_sd": statistics.stdev(values) if len(values) > 1 else None,
                   "defined_seeds": len(values)} for name, values in fields.items()}


def representative_seed(results: dict[int, dict[str, Any]]) -> int | None:
    passing = [(float(r["macro_ap"]), seed) for seed, r in results.items()
               if all(t.get("v11_quality_gate_pass") is True
                      for t in r["calibrated_evaluation"]["targets"].values())]
    if not passing:
        return None
    passing.sort()
    return passing[(len(passing)-1)//2][1]


def paired_group_bootstrap(
    control: dict[int, list[dict[str, Any]]], candidate: dict[int, list[dict[str, Any]]],
    *, replicates: int = 2000, seed: int = 20261106,
) -> dict[str, Any]:
    if not control or set(control) != set(candidate) or replicates <= 0:
        raise DataContractError("Unpaired seed sets or empty bootstrap")
    seeds = sorted(control)
    reference = sorted(control[seeds[0]], key=lambda r: r["sample_id"])
    identities = [(r["sample_id"], r["group_id"], r["targets"], r["mask"]) for r in reference]
    groups = sorted({r["group_id"] for r in reference})
    if not groups or len({r["sample_id"] for r in reference}) != len(reference):
        raise DataContractError("Invalid bootstrap membership")
    for row in reference:
        if (len(row["targets"]) != 2 or len(row["mask"]) != 2
                or any(m not in (0, 1) or (m and v not in (0, 1)) or (not m and v is not None)
                       for v, m in zip(row["targets"], row["mask"], strict=True))):
            raise DataContractError("Bootstrap unknown/known encoding mismatch")
    y = np.array([[v or 0 for v in r["targets"]] for r in reference], dtype=bool)
    mask = np.array([r["mask"] for r in reference], dtype=bool)
    arrays = []
    for collection in (control, candidate):
        scores, thresholds = [], []
        for s in seeds:
            rows = sorted(collection[s], key=lambda r: r["sample_id"])
            if [(r["sample_id"], r["group_id"], r["targets"], r["mask"])
                    for r in rows] != identities:
                raise DataContractError("Bootstrap cohort/labels/masks/groups differ")
            pair = rows[0]["calibrated_thresholds"]
            if any(r["calibrated_thresholds"] != pair for r in rows):
                raise DataContractError("Threshold changed within bootstrap cohort")
            scores.append(np.array([r["scores"] for r in rows], dtype=float))
            thresholds.append(np.array(pair, dtype=float))
        a, t = np.stack(scores), np.stack(thresholds)
        if not np.isfinite(a).all() or not ((a >= 0) & (a <= 1)).all() or not np.isfinite(t).all():
            raise DataContractError("Nonfinite/out-of-range bootstrap scores")
        arrays.append((a, t))
    indices = [np.array([i for i, r in enumerate(reference) if r["group_id"] == g]) for g in groups]

    def measures(scores: np.ndarray, thresholds: np.ndarray, selected: np.ndarray) -> list[float]:
        per_seed = []
        for s in range(len(seeds)):
            ap, other = [], []
            for c in range(2):
                idx = selected[mask[selected, c]]
                labels, prob = y[idx, c], scores[s, idx, c]
                positive, negative = int(labels.sum()), int((~labels).sum())
                if not positive or not negative:
                    return [math.nan] * 7
                order = np.argsort(-prob, kind="stable")
                sorted_y, sorted_p = labels[order], prob[order]
                ends = np.r_[sorted_p[:-1] != sorted_p[1:], True]
                count = np.arange(1, len(idx)+1)[ends]
                true = sorted_y.cumsum()[ends]
                recall = true / positive
                ap.append(float((np.diff(np.r_[0., recall]) * true/count).sum()))
                pred = prob >= thresholds[s, c]
                tp, fp = int((pred & labels).sum()), int((pred & ~labels).sum())
                other.extend([tp/(tp+fp) if tp+fp else math.nan, tp/positive, fp/negative])
            per_seed.append([sum(ap)/2, *other])
        return [float(v) for v in np.mean(per_seed, axis=0)]

    rng = np.random.default_rng(seed)
    deltas = []
    for _ in range(replicates):
        selected = np.concatenate([indices[i] for i in rng.integers(0, len(groups), len(groups))])
        values = [np.array(measures(a, t, selected)) for a, t in arrays]
        deltas.append(values[1]-values[0])
    matrix = np.stack(deltas)
    result = {}
    names = ["macro_ap", "phone_precision", "phone_recall", "phone_fpr",
             "looking_precision", "looking_recall", "looking_fpr"]
    for i, name in enumerate(names):
        values = matrix[:, i][np.isfinite(matrix[:, i])]
        result[name] = {"valid_replicates": len(values),
                        "percentile_95": np.percentile(values, [2.5, 97.5]).tolist()
                        if len(values) else None}
    return {"method": "paired_whole_group_fixed_threshold_percentile_95",
            "groups": len(groups), "seeds": seeds, "replicates": replicates, "seed": seed,
            "threshold_refit": False, "independent_acceptance": False,
            "delta_candidate_minus_C0": result}
