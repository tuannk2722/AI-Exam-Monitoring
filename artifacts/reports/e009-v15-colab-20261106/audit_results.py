"""Read-only E009 metadata audit; recompute saved-score results, never infer/train."""

from __future__ import annotations

import hashlib
import json
import math
import stat
import statistics
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath

import torch
import yaml

from ai_exam_monitoring.data.pilot_schema import read_records, record_to_dict
from ai_exam_monitoring.training.adaptation_config import config_from_dict
from ai_exam_monitoring.training.adaptation_train import runtime_signature
from ai_exam_monitoring.training.artifacts import code_identity, digest_json
from ai_exam_monitoring.training.calibration import calibrate_exact, evaluate_pair
from ai_exam_monitoring.training.metrics import evaluate_scores
from ai_exam_monitoring.training.research_analysis import (
    paired_group_bootstrap,
    recipe_key,
    representative_seed,
    resolve_arm,
    summarize_seeds,
)

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
INPUT = ROOT / "outputs/E009-V15-Colab-20261106"
ZIP = INPUT / "E009-V15-results-metadata-1793994801.zip"
TARGETS = ["phone_use", "looking_around"]
DISCREPANCIES = []


def sha(value):
    return hashlib.sha256(value).hexdigest()


def compare(actual, expected, context=""):
    if isinstance(actual, dict):
        for key, value in actual.items():
            compare(value, expected[key], context + "/" + str(key))
    elif isinstance(actual, (list, tuple)):
        assert len(actual) == len(expected), context
        for index, (a, b) in enumerate(zip(actual, expected, strict=True)):
            compare(a, b, context + "/" + str(index))
    elif isinstance(actual, float):
        assert math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10), (
            context,
            actual,
            expected,
        )
    else:
        assert actual == expected, (context, actual, expected)


def compare_reported_metrics(actual, expected, context=""):
    """Record discrepancies; never rewrite original metrics or loosen equality."""
    if isinstance(actual, dict):
        for key, value in actual.items():
            compare_reported_metrics(value, expected[key], context + "/" + str(key))
    elif isinstance(actual, (tuple, list)):
        assert len(actual) == len(expected), context
        for i, (a, b) in enumerate(zip(actual, expected, strict=True)):
            compare_reported_metrics(a, b, context + "/" + str(i))
    else:
        try:
            compare(actual, expected, context)
        except AssertionError:
            DISCREPANCIES.append(
                {"path": context, "recomputed_from_exported_scores": actual, "reported": expected}
            )


def main():
    torch.set_num_threads(4)
    with zipfile.ZipFile(ZIP) as archive:
        entries = archive.infolist()
        assert len(entries) == len({i.filename for i in entries})
        assert sum(i.file_size for i in entries) < 100_000_000
        for item in entries:
            path = PurePosixPath(item.filename)
            assert not path.is_absolute() and ".." not in path.parts
            assert "\\" not in item.filename and ":" not in item.filename
            assert not stat.S_ISLNK(item.external_attr >> 16) and not item.is_dir()
            assert path.suffix in {".json", ".yaml", ".yml", ".log", ".txt", ".svg"}
        assert archive.testzip() is None
        data = {i.filename: archive.read(i) for i in entries}

    def read(name):
        return json.loads(data[name])

    campaign = read("runs/campaign.json")
    manifest = read("mirror-manifest.json")
    inventory = {n: {"sha256": sha(b), "bytes": len(b)} for n, b in data.items()}
    absent = []
    verified = 0
    for name, row in manifest["files"].items():
        if name in data:
            assert inventory[name] == row, name
            verified += 1
        else:
            assert PurePosixPath(name).suffix == ".pt", name
            absent.append({"path": name, **row})
    assert set(data) == (
        {n for n in manifest["files"] if n in data}
        | {"mirror-manifest.json"}
        | {n for n in data if n.startswith("bootstrap/")}
    )
    print(
        "ZIP CRC and manifest PASS:",
        len(data),
        "members,",
        verified,
        "published metadata",
        flush=True,
    )

    design_path = ROOT / campaign["design"]["path"]
    assert sha(design_path.read_bytes()) == campaign["design"]["sha256"]
    design = json.loads(design_path.read_text(encoding="utf-8"))
    proposal = yaml.safe_load((ROOT / design["proposal"]["path"]).read_text(encoding="utf-8"))
    original_code = code_identity()
    assert campaign["code_sha256"] == original_code["sha256"]
    auth_name = "bootstrap/e009-recovery-authorization-20261107.json"
    recovery = read(auth_name)
    local_auth_path = (
        ROOT / "configs/experiments/E009-V15-20261106/recovery-authorization-20261107.json"
    )
    assert recovery == json.loads(local_auth_path.read_text(encoding="utf-8"))
    assert data[auth_name] == local_auth_path.read_text(encoding="utf-8").encode("utf-8")
    assert campaign["recovery_extension"] == {
        "sha256": sha((ROOT / "src/e009_recovery.py").read_bytes()),
        "authorization_sha256": sha(data[auth_name]),
    }
    notes = [
        {
            "kind": "authorization_transport_LF",
            "semantic_content_unchanged": True,
            "approved_config_sha256": sha(local_auth_path.read_bytes()),
            "runtime_payload_sha256": sha(data[auth_name]),
            "explanation": (
                "Notebook transports the approved JSON as UTF-8 LF; local config uses CRLF."
            ),
        }
    ]
    # Numerical demonstration only: no model, checkpoint or dataset inference.
    logit = torch.tensor(-1.092032790184021, dtype=torch.float32)
    vector_probability = float(logit.expand(344, 2).contiguous().sigmoid()[0, 0])
    row_probability = float(logit.expand(2).contiguous().sigmoid()[0])
    sigmoid_evidence = {
        "method": "synthetic_float32_vector_vs_row_sigmoid_no_model_inference",
        "logit": float(logit),
        "vector_probability": vector_probability,
        "row_probability": row_probability,
        "difference": vector_probability - row_probability,
        "producer": "training/adaptation_train.py::cohort_report",
        "explanation": (
            "Metrics use logits.sigmoid(); prediction export recomputes logits[i].sigmoid()."
        ),
        "original_logits_available": False,
        "case": "BL S20261106 / V6-CA-006 / phone_use at stored threshold",
    }
    smoke = read("receipts/full/gpu-smoke.json")
    assert campaign["status"] == "FINISHED" and smoke["status"] == "PASS"
    assert campaign["profile"] == smoke["profile"] == "full"
    assert campaign["final_test_inference_authorized"] is False
    assert smoke["completed_smoke_reused"] and not smoke["smoke_training_repeated"]
    assert smoke["runs"] == campaign["smoke_runs"]
    assert smoke["checks"] == dict(resume="PASS", reload="PASS", stage_transition="PASS")
    assert smoke["code_sha256"] == campaign["code_sha256"]
    assert smoke["design_sha256"] == campaign["design"]["sha256"]
    runtime = read("runs/runtime.json")
    assert runtime_signature(runtime) == smoke["runtime_sha256"] == campaign["runtime_sha256"]
    assert runtime["accelerator"]["gpu"] == "NVIDIA A100-SXM4-80GB"
    assert runtime["accelerator"]["precision"] == "float32"
    assert not runtime["accelerator"]["matmul_tf32"] and not runtime["accelerator"]["cudnn_tf32"]
    journal = json.loads((INPUT / "E009-launch-1793994801.json").read_text(encoding="utf-8"))
    assert journal["bundle_sha256"] == recovery["bundle_sha256"]
    assert journal["started_at"] == campaign["started_at"] == recovery["started_at"]
    assert journal["freeze_sha256"] == sha(data["bootstrap/environment-first.txt"])
    assert journal["setup_elapsed_seconds"] <= 40 * 60 and journal["environment_ready"]
    budget = campaign["effective_budget"]
    assert budget["total_minutes"] == 720 and budget["research_pool_minutes"] == 500
    assert budget["run_including_reload_minutes"] == 45
    assert budget["per_research_run_including_reload_and_sync_minutes"] == 45
    assert budget["training_deadline_minutes_from_first_launch"] == 610
    assert budget["max_research_runs"] == 25

    missing_pins = {}
    checked_pins = set()

    def verify_pin(value):
        if isinstance(value, dict) and set(value) == {"path", "sha256"}:
            path, expected = value["path"], value["sha256"]
            if path in checked_pins:
                return
            if "/materialized/" in path:
                content = data["configs/" + path.split("/materialized/", 1)[1]]
            elif path.endswith("/recovery-authorization.json"):
                content = data[auth_name]
            elif path.startswith(design["run_dir"] + "/"):
                member = "runs/" + path.split(design["run_dir"] + "/", 1)[1]
                if member not in data:
                    assert manifest["files"][member]["sha256"] == expected
                    missing_pins[path] = expected
                    return
                content = data[member]
            elif path == design["smoke_receipt"].replace("{profile}", "full"):
                content = data["receipts/full/gpu-smoke.json"]
            else:
                target = ROOT / path
                if not target.is_file():
                    assert PurePosixPath(path).suffix in {".pt", ".pth"}, path
                    missing_pins[path] = expected
                    return
                content = target.read_bytes()
            assert sha(content) == expected, path
            checked_pins.add(path)
        elif isinstance(value, dict):
            for child in value.values():
                verify_pin(child)
        elif isinstance(value, list):
            for child in value:
                verify_pin(child)

    verify_pin(design)
    verify_pin(smoke)
    verify_pin(recovery["proposal"])
    records = read_records(ROOT / "data/processed/pilot-b/pilot-b-20261106-v15/manifest.jsonl")
    original = {r.sample_id: r for r in records}
    cohorts = {
        role: sorted([r for r in records if r.usage == role], key=lambda r: r.sample_id)
        for role in ("train", "val")
    }
    assert len(cohorts["train"]) == 1377 and len(cohorts["val"]) == 344
    groups = {role: {r.group.leakage_group_id for r in rows} for role, rows in cohorts.items()}
    assert not (groups["train"] & groups["val"])
    print("Source/data/runtime/recovery pins PASS; checking 31 runs", flush=True)
    summaries, errors, metadata_checks = [], {}, 0
    all_metrics, val_predictions, recomputed_metrics = {}, {}, {}
    last_end, maximum_run = 0.0, 0.0
    for phase in ("smoke", "research"):
        prefix = "configs/full/" + phase + "/"
        plan = read(prefix + "plan.json")
        protocol, approval, readiness = [
            read(prefix + n + ".json") for n in ("protocol", "approval", "readiness")
        ]
        verify_pin(approval)
        verify_pin(readiness)
        assert readiness["protocol_sha256"] == sha(data[prefix + "protocol.json"])
        assert protocol["final_test_inference_authorized"] is False
        assert not protocol["independence_claim"]
        for role, cohort in (("train", "train"), ("val", "selection")):
            assert protocol["cohorts"][cohort]["records_sha256"] == digest_json(
                [record_to_dict(r) for r in cohorts[role]]
            )
        assert plan["code_sha256"] == campaign["code_sha256"]
        assert approval["code_sha256"] == campaign["code_sha256"]
        if phase == "research":
            assert plan["budget"] == budget
            assert plan["recovery_authorization"]["sha256"] == sha(data[auth_name])
        active = campaign[phase + "_runs"]
        for ident in active:
            base = "runs/" + ident + "/"
            item = campaign["runs"][ident]["item"]
            assert item in plan["items"]
            run, config, metrics, calibration, history = [
                read(base + n + ".json")
                for n in ("run", "resolved-config", "metrics", "calibration", "history")
            ]
            assert run["status"] == "FINISHED" and run["error"] is None
            assert run["code_sha256"] == campaign["code_sha256"]
            assert (
                run["payload_sha256"]
                == smoke["payload_sha256"]
                == config["cohorts"][0]["data"]["payload_sha256"]
            )
            assert (
                config["cohorts"][0]["data"]["dataset_version"]
                == run["dataset_version"]
                == "pilot-b-20261106-v15"
            )
            assert run["config_sha256"] == digest_json(config) == approval["configs"][ident]
            loaded = config_from_dict(yaml.safe_load(data[prefix + ident + ".yaml"]))
            compare(loaded.to_dict(), config, ident + "/config")
            assert loaded.match_signature() == approval["config_signatures"][ident]
            assert runtime_signature(run["environment"]) == campaign["runtime_sha256"]
            assert read(base + "code-provenance.json") == original_code
            assert (
                run["environment"]["pip_freeze"] == data["bootstrap/environment-first.txt"].decode()
            )
            verify_pin(config)
            arm = resolve_arm(proposal["arms"], item["arm"])
            common = proposal["common"]
            expected = {
                "encoder_variant": arm["encoder"],
                "image_size": arm["image_size"],
                "train_last_blocks": arm["train_last_blocks"],
                "train_final_norm": True,
                "layer4_learning_rate": arm["backbone_learning_rate"],
                "head_learning_rate": common["head_learning_rate"],
                "batch_size": 16,
                "workers": 0,
                "threads": 4,
                "precision": "float32",
                "device": "cuda",
                "optimizer": "AdamW",
                "weight_decay": 0.01,
                "patience": 6,
                "min_delta": 0.0001,
                "warmup_epochs": 3,
                "lr_scheduler": "cosine",
                "min_lr_ratio": 0.1,
                "head_hidden_dim": 128,
                "head_dropout": 0.3,
                "pos_weight": common["loss"]["pos_weight"],
                "label_smoothing": 0.05,
                "selection_metric": "val_macro_ap",
                "calibrate_thresholds_on_val": True,
                "pooling": "global_mean",
                "augmentation": common["augmentation"],
                "max_epochs": 5 if phase == "smoke" else 24,
                "wall_time_seconds": 4200 if phase == "smoke" else 2700,
            }
            compare(expected, config, ident + "/recipe")
            checksums = read(base + "checksums.json")
            for relative, expected_hash in checksums.items():
                member = base + relative
                if member in data:
                    assert sha(data[member]) == expected_hash, member
                    metadata_checks += 1
                else:
                    assert relative in {"best.pt", "last.pt"}
                    assert manifest["files"][member]["sha256"] == expected_hash
            assert len(history) == run["completed_epochs"] <= config["max_epochs"]
            assert [h["epoch"] for h in history] == list(range(1, len(history) + 1))
            selected = min(history, key=lambda h: (-h["val_macro_ap"], h["val_loss"], h["epoch"]))
            assert selected["epoch"] == run["best_epoch"]
            assert all(h["stage"] == "warmup_head_only" for h in history[:3])
            assert all(h["stage"] != "warmup_head_only" for h in history[3:])
            compare(selected["val_macro_ap"], metrics["selection"]["macro_ap"], ident + "/best_AP")
            compare(
                selected["val_loss"], metrics["selection"]["macro_masked_bce"], ident + "/best_BCE"
            )
            reload_base = "runs/" + ident + "-reload/"
            reload = read(reload_base + "evaluation.json")
            assert reload["status"] == "FINISHED" and reload["split"] == "val"
            assert (
                reload["checkpoint_sha256"]
                == checksums["best.pt"]
                == calibration["checkpoint_sha256"]
            )
            assert reload["config_sha256"] == run["config_sha256"]
            assert reload["code_sha256"] == run["code_sha256"]
            assert reload["protocol_sha256"] == sha(data[prefix + "protocol.json"])
            assert read(reload_base + "metrics.json") == {"selection": metrics["selection"]}
            assert (
                data[reload_base + "predictions-selection.json"]
                == data[base + "predictions-selection.json"]
            )
            for relative, expected_hash in read(reload_base + "checksums.json").items():
                assert sha(data[reload_base + relative]) == expected_hash
                metadata_checks += 1
            for cohort, role in (("train", "train"), ("selection", "val")):
                preds = read(base + "predictions-" + cohort + ".json")
                ids = [r["sample_id"] for r in preds]
                assert ids == [r.sample_id for r in cohorts[role]]
                assert len(ids) == len(set(ids))
                for row in preds:
                    record = original[row["sample_id"]]
                    assert row["group_id"] == record.group.leakage_group_id
                    assert row["split"] == role and row["target_order"] == TARGETS
                    assert row["targets"] == list(record.target_values)
                    assert row["mask"] == list(record.target_mask)
                    assert row["calibrated_thresholds"] == calibration["thresholds"]
                    assert all(math.isfinite(v) and 0 <= v <= 1 for v in row["scores"])
                    assert row["decisions"] == [v >= 0.5 for v in row["scores"]]
                    assert row["calibrated_decisions"] == [
                        v >= t
                        for v, t in zip(row["scores"], calibration["thresholds"], strict=True)
                    ]
                scores = torch.tensor([r["scores"] for r in preds], dtype=torch.float64)
                values = torch.tensor([[v or 0 for v in r["targets"]] for r in preds])
                mask = torch.tensor([r["mask"] for r in preds], dtype=torch.bool)
                raw_recomputed = evaluate_scores(scores, values, mask, 0.5)
                calibrated_recomputed = evaluate_pair(
                    scores,
                    values,
                    mask,
                    tuple(calibration["thresholds"]),
                    [r["group_id"] for r in preds],
                )
                compare_reported_metrics(raw_recomputed, metrics[cohort], ident + "/" + cohort)
                compare_reported_metrics(
                    calibrated_recomputed,
                    metrics[cohort]["calibrated_evaluation"],
                    ident + "/" + cohort + "/calibrated",
                )
                if cohort == "selection":
                    assert digest_json(ids) == calibration["selection_ids_sha256"]
                    compare_reported_metrics(
                        list(calibrate_exact(scores, values, mask)),
                        calibration["thresholds"],
                        ident + "/calibration_replay_thresholds_not_installed",
                    )
                    recomputed_metrics[ident] = {
                        **metrics[cohort],
                        **raw_recomputed,
                        "calibrated_evaluation": calibrated_recomputed,
                    }
                    val_predictions[ident] = preds
                    for name, members in protocol["slice_enrollment"]["selection"].items():
                        indices = [
                            i for i, row in enumerate(preds) if row["sample_id"] in set(members)
                        ]
                        compare_reported_metrics(
                            evaluate_pair(
                                scores[indices],
                                values[indices],
                                mask[indices],
                                tuple(calibration["thresholds"]),
                                [preds[i]["group_id"] for i in indices],
                            ),
                            metrics[cohort]["calibrated_slices"][name],
                            ident + "/slice/" + name,
                        )
            entry = campaign["runs"][ident]
            ended = datetime.fromisoformat(run["ended_at"]).timestamp()
            assert entry["status"] == "FINISHED" and entry["reload"] == "PASS"
            assert entry["first_started_at"] <= ended
            if phase == "research":
                assert entry["elapsed_including_reload_sync_seconds"] <= 45 * 60
                assert ended <= min(
                    campaign["started_at"] + 610 * 60, campaign["research_started_at"] + 500 * 60
                )
                last_end = max(last_end, ended)
                maximum_run = max(maximum_run, entry["elapsed_including_reload_sync_seconds"])
                summaries.append(
                    {
                        "id": ident,
                        "arm": item["arm"],
                        "seed": item["seed"],
                        "best_epoch": run["best_epoch"],
                        "epochs": run["completed_epochs"],
                        "elapsed_seconds": run["elapsed_seconds"],
                        "including_reload_sync_seconds": entry[
                            "elapsed_including_reload_sync_seconds"
                        ],
                        "thresholds": calibration["thresholds"],
                        "macro_ap": metrics["selection"]["macro_ap"],
                        "fixed": metrics["selection"]["targets"],
                        "calibrated": metrics["selection"]["calibrated_evaluation"]["targets"],
                    }
                )
                errors[ident] = {
                    target: {
                        kind: [
                            r["sample_id"]
                            for r in val_predictions[ident]
                            if r["mask"][i]
                            and r["targets"][i] == truth
                            and r["calibrated_decisions"][i] == decision
                        ]
                        for kind, truth, decision in (("fp", 0, True), ("fn", 1, False))
                    }
                    for i, target in enumerate(TARGETS)
                }
            all_metrics[ident] = metrics["selection"]
        print(
            phase,
            "metadata/reload verified:",
            len(active),
            "metric discrepancy fields:",
            len(DISCREPANCIES),
            flush=True,
        )

    for arm in budget["smoke_arms"]:
        full, resumed = [f"runs/E009-V15-SMOKE-{arm}-{mode}/" for mode in ("FULL", "RESUME")]
        for name in (
            "history.json",
            "metrics.json",
            "predictions-train.json",
            "predictions-selection.json",
        ):
            assert data[full + name] == data[resumed + name]
        a = read(full + "run.json")
        entry = campaign["runs"][f"E009-V15-SMOKE-{arm}-FULL"]
        projection = (
            a["elapsed_seconds"] * 24 / 5 * 1.25
            + entry["reload_seconds"]
            + entry["final_sync_seconds"]
        )
        compare(projection, smoke["projection_seconds"][arm], "smoke/projection")
        assert projection <= 2700
    expected = [(a, s) for s in budget["screening_seeds"] for a in budget["screening_arms"]]
    expected += [(a, s) for s in budget["confirmation_seeds"] for a in ["C0", "B0", "B448"]]
    assert [(r["arm"], r["seed"]) for r in summaries] == expected
    screening_rank = sorted(
        budget["screening_arms"],
        key=lambda a: recipe_key(
            a,
            [all_metrics[f"E009-V15-{a}-S{s}"] for s in budget["screening_seeds"]],
            proposal["arms"],
        ),
    )
    assert screening_rank == campaign["screening_rank"]
    finalists = list(dict.fromkeys([*screening_rank[:2], "C0"]))
    assert finalists == campaign["confirmation_arms"]
    summary = read("runs/research-summary.json")
    final_results = {}
    for arm in finalists:
        results = {
            s: all_metrics[f"E009-V15-{arm}-S{s}"]
            for s in [*budget["screening_seeds"], *budget["confirmation_seeds"]]
        }
        assert {str(s): r for s, r in results.items()} == summary["recipes"][arm]["per_seed"]
        compare(
            summarize_seeds(results), summary["recipes"][arm]["mean_sample_sd"], arm + "/summary"
        )
        compare(
            recipe_key(arm, list(results.values()), proposal["arms"]),
            summary["recipes"][arm]["ranking_key"],
            arm + "/rank",
        )
        assert representative_seed(results) == summary["recipes"][arm]["representative_seed"]
        final_results[arm] = {
            "means": summarize_seeds(results),
            "representative_seed": representative_seed(results),
            "both_targets_pass": sum(
                all(
                    t["v11_quality_gate_pass"] is True
                    for t in r["calibrated_evaluation"]["targets"].values()
                )
                for r in results.values()
            ),
            "fixed_both_targets_pass": sum(
                all(t["v11_quality_gate_pass"] is True for t in r["targets"].values())
                for r in results.values()
            ),
        }
    ranking = sorted(
        finalists,
        key=lambda a: recipe_key(
            a,
            [
                all_metrics[f"E009-V15-{a}-S{s}"]
                for s in [*budget["screening_seeds"], *budget["confirmation_seeds"]]
            ],
            proposal["arms"],
        ),
    )
    assert ranking == summary["final_recipe_rank"] and ranking[0] == summary["winner"]
    assert summary["four_of_five_both_targets"] == (
        final_results[ranking[0]]["both_targets_pass"] >= 4
    )
    verify_pin(summary["checkpoint_handoff"])
    recomputed_finalists = {}
    for arm in finalists:
        results = {
            s: recomputed_metrics[f"E009-V15-{arm}-S{s}"]
            for s in [*budget["screening_seeds"], *budget["confirmation_seeds"]]
        }
        recomputed_finalists[arm] = {
            "means": summarize_seeds(results),
            "representative_seed": representative_seed(results),
            "both_targets_pass": sum(
                all(
                    t["v11_quality_gate_pass"] is True
                    for t in r["calibrated_evaluation"]["targets"].values()
                )
                for r in results.values()
            ),
            "per_seed": {
                s: {"macro_ap": r["macro_ap"], "calibrated": r["calibrated_evaluation"]["targets"]}
                for s, r in results.items()
            },
        }
    recomputed_screening_rank = sorted(
        budget["screening_arms"],
        key=lambda a: recipe_key(
            a,
            [recomputed_metrics[f"E009-V15-{a}-S{s}"] for s in budget["screening_seeds"]],
            proposal["arms"],
        ),
    )
    recomputed_final_rank = sorted(
        finalists,
        key=lambda a: recipe_key(
            a,
            [
                recomputed_metrics[f"E009-V15-{a}-S{s}"]
                for s in [*budget["screening_seeds"], *budget["confirmation_seeds"]]
            ],
            proposal["arms"],
        ),
    )
    bootstrap = read("runs/paired-bootstrap.json")
    for arm in finalists:
        if arm == "C0":
            continue
        control = {
            s: val_predictions[f"E009-V15-C0-S{s}"]
            for s in [*budget["screening_seeds"], *budget["confirmation_seeds"]]
        }
        candidate = {s: val_predictions[f"E009-V15-{arm}-S{s}"] for s in control}
        compare(
            paired_group_bootstrap(control, candidate, replicates=2000, seed=20261106),
            bootstrap[arm],
            arm + "/paired-bootstrap",
        )
        print(arm, "2000 paired group bootstrap replicates PASS", flush=True)
    shared_errors = {}
    for arm in finalists:
        runs = [r["id"] for r in summaries if r["arm"] == arm]
        shared_errors[arm] = {
            t: {
                k: sorted(set.intersection(*(set(errors[r][t][k]) for r in runs)))
                for k in ("fp", "fn")
            }
            for t in TARGETS
        }
    requests = []
    for arm in ranking:
        seed = final_results[arm]["representative_seed"]
        ident = f"E009-V15-{arm}-S{seed}"
        requests.append(
            {
                "arm": arm,
                "run_id": ident,
                "seed": seed,
                "role": "primary" if arm == ranking[0] else "comparison",
                "files": {
                    n: manifest["files"]["runs/" + ident + "/" + n] for n in ("best.pt", "last.pt")
                },
            }
        )
    origin_summary = {}
    for arm in finalists:
        origin_summary[arm] = {}
        for origin in ("old_train_moved_to_val", "old_val_kept", "new_native_S03"):
            slices = [
                r["calibrated_slices"]["cohort_origin:" + origin]
                for r in summary["recipes"][arm]["per_seed"].values()
            ]
            origin_summary[arm][origin] = {"records": slices[0]["records"], "targets": {}}
            for target in TARGETS:
                rows = [r["targets"][target] for r in slices]
                means = {
                    metric: statistics.mean([r[metric] for r in rows if r[metric] is not None])
                    if any(r[metric] is not None for r in rows)
                    else None
                    for metric in ("precision", "recall", "fpr", "ap")
                }
                origin_summary[arm][origin]["targets"][target] = {
                    "positive": rows[0]["positive"],
                    "negative": rows[0]["negative"],
                    "support": rows[0]["v11_support_gate_status"],
                    "means": means,
                    "pass_seeds": sum(r["v11_quality_gate_pass"] is True for r in rows),
                    "per_seed_recall": [r["recall"] for r in rows],
                }
    receipt = {
        "status": "METADATA_AUDIT_WITH_FINDINGS" if DISCREPANCIES else "PASS_METADATA_AUDIT",
        "integrity_and_protocol_checks": "PASS",
        "local_checkpoint_bytes_verified": False,
        "local_model_inference_performed": False,
        "test_opened": False,
        "model_promoted": False,
        "source_zip": {
            "path": ZIP.relative_to(ROOT).as_posix(),
            "bytes": ZIP.stat().st_size,
            "sha256": sha(ZIP.read_bytes()),
        },
        "journal": {
            "path": (INPUT / "E009-launch-1793994801.json").relative_to(ROOT).as_posix(),
            "source": "read_only_private_Drive_preview",
            "data": journal,
        },
        "counts": {
            "zip_members": len(data),
            "manifest_members_verified": verified,
            "artifact_checksums_verified": metadata_checks,
            "external_pin_files_verified": len(checked_pins),
            "smoke_runs": 6,
            "research_runs": 25,
            "train": 1377,
            "val": 344,
            "test": 0,
        },
        "code_sha256": campaign["code_sha256"],
        "design": campaign["design"],
        "runtime": runtime,
        "recovery": campaign["recovery_extension"],
        "effective_budget": budget,
        "clock": {
            "original_started_at": campaign["started_at"],
            "research_started_at": campaign["research_started_at"],
            "last_training_ended_at": last_end,
            "elapsed_to_last_training_minutes": (last_end - campaign["started_at"]) / 60,
            "research_to_last_training_minutes": (last_end - campaign["research_started_at"]) / 60,
            "maximum_run_including_reload_sync_minutes": maximum_run / 60,
            "campaign_final_sync_end_exact": "not_recorded_in_campaign_JSON",
        },
        "screening_rank": screening_rank,
        "final_rank": ranking,
        "finalists": final_results,
        "recomputed_at_stored_thresholds": {
            "screening_rank": recomputed_screening_rank,
            "final_rank": recomputed_final_rank,
            "finalists": recomputed_finalists,
        },
        "metric_discrepancies": DISCREPANCIES,
        "score_export_numerical_reproduction": sigmoid_evidence,
        "runs": summaries,
        "paired_group_bootstrap": bootstrap,
        "shared_errors_five_seeds": shared_errors,
        "cohort_origin_summary_five_seeds": origin_summary,
        "checkpoint_requests": requests,
        "omitted_checkpoint_files": absent,
        "unavailable_binary_pins": missing_pins,
        "traceability_notes": notes,
        "limits": [
            (
                "Metadata verifies recorded CUDA reload claims, "
                "not locally downloaded checkpoint bytes."
            ),
            (
                "Thresholds and recipe/checkpoint selection used the same development val; "
                "no independent test."
            ),
            "Legacy source/group/generated-data limitations of accepted V15 remain.",
            (
                "Per-run marginal bootstrap intervals are not all replayed; "
                "approved paired final bootstrap is replayed."
            ),
        ],
        "inventory": inventory,
    }
    (REPORT / "results-audit-20261107.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        receipt["status"],
        json.dumps(
            {
                "counts": receipt["counts"],
                "rank": ranking,
                "recomputed_rank": recomputed_final_rank,
                "discrepancy_fields": len(DISCREPANCIES),
                "elapsed_minutes": receipt["clock"]["elapsed_to_last_training_minutes"],
                "checkpoint_requests": [r["run_id"] for r in requests],
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
