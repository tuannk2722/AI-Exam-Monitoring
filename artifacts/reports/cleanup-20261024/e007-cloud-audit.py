"""One-off verification of imported E007 artifacts; no model inference or training."""
import json
import math
import statistics
from pathlib import Path

import numpy as np
import torch

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import code_identity, digest_json, write_json
from ai_exam_monitoring.training.adaptation_train import runtime_signature
from ai_exam_monitoring.training.adaptation_model import tensor_digest
from ai_exam_monitoring.training.calibration import calibrate_exact, evaluate_pair

root = Path.cwd()
base = root / "outputs/E007-V13-Colab-20261024/runs"
report = root / "artifacts/reports/e007-v13-colab-20261024"
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
campaign = read(base / "campaign.json")
smoke = read(report / "gpu-smoke.json")
assert campaign["status"] == "FINISHED" and len(campaign["research_runs"]) == 9
assert campaign["code_sha256"] == code_identity()["sha256"] == smoke["code_sha256"]
assert sha256_file(root / campaign["design"]["path"]) == campaign["design"]["sha256"]
assert campaign["elapsed_seconds"] < campaign["deadline"] - campaign["started_at"]
manifest = {r["sample_id"]: r for r in map(json.loads, (
    root / "data/processed/pilot-b/pilot-b-20261023-v13/manifest.jsonl"
).read_text(encoding="utf-8").splitlines())}
runtime = read(base / "runtime.json")
assert runtime_signature(runtime) == smoke["runtime_sha256"]
summaries, predictions, file_count = [], {}, 0
for item in campaign["smoke_runs"] + campaign["research_runs"]:
    folder = base / item["id"]
    for kind in ("run", "config", "metrics"):
        assert sha256_file(root / item[kind]["path"]) == item[kind]["sha256"]
    for directory in (folder, base / (item["id"] + "-reload")):
        checks = read(directory / "checksums.json")
        for name, digest in checks.items():
            assert sha256_file(directory / name) == digest, (item["id"], name)
            file_count += 1
    run = read(folder / "run.json")
    config = read(folder / "resolved-config.json")
    metrics = read(folder / "metrics.json")
    assert run["status"] == "FINISHED"
    assert runtime_signature(run["environment"]) == smoke["runtime_sha256"]
    assert run["config_sha256"] == digest_json(config)
    history = read(folder / "history.json")
    best = min(history, key=lambda x: (-x["val_macro_ap"], x["val_loss"], x["epoch"]))
    assert best["epoch"] == run["best_epoch"]
    for name in ("train", "selection"):
        rows = read(folder / f"predictions-{name}.json")
        assert len(rows) == (1119 if name == "train" else 185)
        assert len({r["sample_id"] for r in rows}) == len(rows)
        for row in rows:
            original = manifest[row["sample_id"]]
            assert original["usage"] == row["split"]
            assert original["target_values"] == row["targets"]
            assert original["target_mask"] == row["mask"]
            assert original["group"]["leakage_group_id"] == row["group_id"]
        if name == "selection":
            assert rows == read(base / (item["id"] + "-reload") / "predictions-selection.json")
    reload_metrics = read(base / (item["id"] + "-reload") / "metrics.json")
    assert reload_metrics["selection"] == metrics["selection"]
    rows = read(folder / "predictions-selection.json")
    scores = torch.tensor([r["scores"] for r in rows])
    values = torch.tensor([[0 if v is None else v for v in r["targets"]] for r in rows],
                          dtype=torch.float32)
    masks = torch.tensor([r["mask"] for r in rows], dtype=torch.bool)
    thresholds = calibrate_exact(scores, values, masks)
    actual = evaluate_pair(scores, values, masks, thresholds, [r["group_id"] for r in rows])
    assert actual == metrics["selection"]["calibrated_evaluation"]
    assert metrics["train"]["calibrated_thresholds"] == metrics["selection"]["calibrated_thresholds"]
    if item not in campaign["research_runs"]:
        continue
    predictions[(item["arm"], item["seed"])] = rows
    envelope = {}
    for c, target in enumerate(config["target_order"]):
        s = scores[masks[:, c], c].double()
        y = values[masks[:, c], c].bool()
        candidates = sorted({0., .5, math.nextafter(1., 2.), *s.tolist()})
        operating = []
        for threshold in candidates:
            pred = s >= threshold
            tp, fp = int((pred & y).sum()), int((pred & ~y).sum())
            precision = tp / (tp + fp) if tp + fp else None
            recall, fpr = tp / int(y.sum()), fp / int((~y).sum())
            operating.append((precision, recall, fpr))
        envelope[target] = {
            "feasible_80_80_20": any(p is not None and p >= .8 and r >= .8 and f <= .2
                                     for p, r, f in operating),
            "max_precision_at_recall_ge80": max(p for p, r, f in operating if r >= .8),
            "max_recall_at_precision_ge80": max(
                (r for p, r, f in operating if p is not None and p >= .8), default=None),
        }
    summaries.append({
        "id": item["id"], "arm": item["arm"], "seed": item["seed"],
        "best_epoch": run["best_epoch"], "completed_epochs": run["completed_epochs"],
        "elapsed_seconds": run["elapsed_seconds"], "macro_ap": metrics["selection"]["macro_ap"],
        "raw_bce": metrics["selection"]["macro_masked_bce"],
        "train_macro_ap": metrics["train"]["macro_ap"],
        "thresholds": metrics["selection"]["calibrated_thresholds"],
        "calibrated": actual, "default_targets": metrics["selection"]["targets"],
        "threshold_envelope": envelope,
    })
    print(item["id"], "checksums/labels/reload/calibration PASS", flush=True)

for arm in ("R0", "D1"):
    a = torch.load(base / f"E007-V13-SMOKE-{arm}-FULL/last.pt", map_location="cpu", weights_only=True)
    b = torch.load(base / f"E007-V13-SMOKE-{arm}-RESUME/last.pt", map_location="cpu", weights_only=True)
    assert a["history"] == b["history"]
    assert tensor_digest(a["model"]) == tensor_digest(b["model"])
    assert tensor_digest(a["best_model"]) == tensor_digest(b["best_model"])
    del a, b

statistics_by_arm = {}
for arm in ("R0", "D1"):
    rows = [r for r in summaries if r["arm"] == arm]
    statistics_by_arm[arm] = {"mean_macro_ap": statistics.mean(r["macro_ap"] for r in rows),
                              "sample_sd_macro_ap": statistics.stdev(r["macro_ap"] for r in rows),
                              "mean_raw_bce": statistics.mean(r["raw_bce"] for r in rows)}
    for target in ("phone_use", "looking_around"):
        statistics_by_arm[arm][target] = {
            "mean_ap": statistics.mean(r["calibrated"]["targets"][target]["ap"] for r in rows),
            "passed_seeds": sum(r["calibrated"]["targets"][target]["v11_quality_gate_pass"]
                                for r in rows),
        }

seeds = (20261023, 20261024, 20261025)
stable_errors = {}
for c, target in enumerate(("phone_use", "looking_around")):
    stable_errors[target] = {}
    for label, truth in (("false_positives", 0), ("false_negatives", 1)):
        sets = [{r["sample_id"] for r in predictions[("D1", seed)]
                 if r["mask"][c] and r["targets"][c] == truth
                 and r["calibrated_decisions"][c] != bool(truth)} for seed in seeds]
        stable_errors[target][label] = sorted(set.intersection(*sets))

def ap(score, target):
    if not target.any() or target.all():
        return float("nan")
    order = np.argsort(-score, kind="stable")
    ss, yy = score[order], target[order]
    end = np.r_[np.flatnonzero(np.diff(ss)), len(ss)-1]
    tp = np.cumsum(yy)[end]
    return float(np.sum(np.diff(np.r_[0, tp]) / yy.sum() * tp / (end+1)))

reference = predictions[("R0", seeds[0])]
ids = [r["sample_id"] for r in reference]
groups = np.array([r["group_id"] for r in reference])
unique = sorted(set(groups))
indices = [np.flatnonzero(groups == group) for group in unique]
values = np.array([[0 if v is None else v for v in r["targets"]] for r in reference])
mask = np.array([r["mask"] for r in reference], dtype=bool)
score_arrays = {}
for key, rows in predictions.items():
    assert [r["sample_id"] for r in rows] == ids
    score_arrays[key] = np.array([r["scores"] for r in rows])
rng = np.random.default_rng(20261024)
deltas = []
for _ in range(2000):
    idx = np.concatenate([indices[i] for i in rng.integers(0, len(unique), len(unique))])
    differences = []
    for seed in seeds:
        for c in range(2):
            known = idx[mask[idx, c]]
            differences.append(ap(score_arrays[("D1", seed)][known, c], values[known, c])
                               - ap(score_arrays[("R0", seed)][known, c], values[known, c]))
    if np.isfinite(differences).all():
        deltas.append(float(np.mean(differences)))

result = {
    "status": "VERIFIED", "scope": "cached artifacts only; no training/inference/test access",
    "campaign_sha256": sha256_file(base / "campaign.json"),
    "source_sha256": campaign["code_sha256"], "checked_artifact_hashes": file_count,
    "smoke_tensor_resume_parity": "PASS", "research_reload_parity": "9/9 PASS",
    "runtime": {k:runtime[k] for k in ("device", "accelerator", "packages", "python")},
    "campaign_seconds": campaign["elapsed_seconds"], "smoke_seconds": smoke["elapsed_seconds"],
    "screening_champion": campaign["screening_champion"], "runs": summaries,
    "three_seed_statistics": statistics_by_arm, "stable_d1_errors_across_three_seeds": stable_errors,
    "paired_group_bootstrap": {
        "description": "D1 minus R0 macro AP, paired group resampling; mean over same 3 fixed seeds",
        "development_only": True, "groups": len(unique), "replicates": len(deltas),
        "percentile_95_ci": np.quantile(deltas, [.025, .975]).tolist(),
        "point_delta": statistics_by_arm["D1"]["mean_macro_ap"]-statistics_by_arm["R0"]["mean_macro_ap"],
    },
    "decision": "continue_research_only; no run passes both targets; no promotion",
}
write_json(report / "cloud-results-audit.json", result)
write_json(report / "campaign-result.json", campaign)
print(json.dumps({"statistics": statistics_by_arm, "bootstrap":result["paired_group_bootstrap"],
                  "stable_errors":stable_errors},indent=2))
