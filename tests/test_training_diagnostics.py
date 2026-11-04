"""Synthetic cohort/unknown/selection guards for cached-score diagnostics."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image
from test_pilot_schema import evidence, usable_record

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import TARGET_ORDER, write_records
from ai_exam_monitoring.training.diagnostics import (
    build,
    consensus,
    local,
    make_gallery,
    operating_envelope,
    outcome,
    shortlist,
    write_json,
)


class DiagnosticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.row = {
            "sample_id": "a", "split": "val", "source_id": "source",
            "group_id": "group", "targets": [1, None], "mask": [1, 0],
            "scores": [0.5, 0.99],
        }
        self.predictions = {r: {"a": copy.deepcopy(self.row)} for r in ("one", "two", "three")}
        self.cuts = {r: [0.5, 0.5] for r in self.predictions}

    def test_equal_threshold_is_positive_unknown_is_not_false_positive(self) -> None:
        rows = consensus(self.predictions, self.cuts, list(self.predictions))
        self.assertEqual(rows[0]["stable_outcome"], "TP")
        self.assertEqual(rows[1]["stable_outcome"], "U")
        self.assertEqual(rows[1]["error_count"], 0)

    def test_threshold_is_run_specific_not_a_pooled_threshold(self) -> None:
        self.cuts["two"] = [0.6, 0.5]
        rows = consensus(self.predictions, self.cuts, list(self.predictions))
        self.assertEqual(rows[0]["stable_outcome"], "mixed")
        self.assertEqual(rows[0]["error_count"], 1)
        self.assertEqual(rows[0]["outcomes"]["two"], "FN")

    def test_rejects_cohort_drift(self) -> None:
        self.predictions["two"]["b"] = self.predictions["two"].pop("a")
        with self.assertRaises(DataContractError):
            consensus(self.predictions, self.cuts, list(self.predictions))

    def test_rejects_label_group_or_split_drift(self) -> None:
        for key, value in (("targets", [0, None]), ("mask", [1, 1]),
                           ("group_id", "other"), ("split", "test")):
            with self.subTest(key=key):
                p = copy.deepcopy(self.predictions)
                p["two"]["a"][key] = value
                with self.assertRaises(DataContractError):
                    consensus(p, self.cuts, list(p))

    def test_rejects_duplicate_runs(self) -> None:
        with self.assertRaises(DataContractError):
            consensus(self.predictions, self.cuts, ["one", "one"])

    def test_rejects_even_matched_test_cohort(self) -> None:
        for p in self.predictions.values():
            p["a"]["split"] = "test"
        with self.assertRaises(DataContractError):
            consensus(self.predictions, self.cuts, list(self.predictions))

    def test_shortlist_diversifies_groups_and_does_not_drop_unknown(self) -> None:
        rows = []
        for sid, source, group, category, margin in (
            ("a", "s1", "g1", "FP", 0.9), ("b", "s1", "g1", "FP", 0.8),
            ("c", "s2", "g2", "FP", 0.1), ("u", "s3", "g3", "U", 0.4),
        ):
            rows.append({"sample_id": sid, "source_id": source, "group_id": group,
                         "target": "phone_use", "stable_outcome": category,
                         "mean_margin": margin})
        selected = shortlist(rows, 2)
        self.assertEqual({r["sample_id"] for r in selected}, {"a", "c", "u"})
        self.assertEqual(selected, shortlist(list(reversed(rows)), 2))

    def test_unevaluated_unknown_stays_unknown_at_both_extremes(self) -> None:
        for score in (0.0, 1.0):
            self.row["scores"][1] = score
            self.assertEqual(outcome(self.row, 1, 0.5), "U")

    def test_path_cannot_escape_workspace(self) -> None:
        with self.assertRaises(DataContractError):
            local(Path.cwd(), "../outside")

    def test_envelope_keeps_ties_together_and_unknown_out_of_support(self) -> None:
        rows = [{**self.row, "targets": [y, None], "scores": [s, .5]}
                for y, s in ((1, .04), (1, .03), (0, .03), (0, .01))]
        rows.append({**self.row, "targets": [None, None], "mask": [0, 0],
                     "scores": [1., 1.]})
        result = operating_envelope(rows, 0)
        self.assertFalse(result["feasible_80_80_20"])
        self.assertEqual(result["max_precision_at_recall_ge80"], 2 / 3)
        self.assertEqual(result["max_recall_at_precision_ge80"], .5)
        self.assertEqual((result["positive"], result["negative"]), (2, 2))
        self.assertIsNone(operating_envelope(rows, 1)["feasible_80_80_20"])


class DiagnosticsBuildTests(unittest.TestCase):
    def fixture(self, root, *, drift=False, schema="representation-adaptation-v4"):
        package = root / "data/package"
        run = root / "outputs/campaign/runs/run-one"
        package.mkdir(parents=True)
        run.mkdir(parents=True)
        records = [usable_record(s, split=s, image_sha=hashlib.sha256(s.encode()).hexdigest())
                   for s in ("train", "val")]
        records = [replace(r, crop=replace(r.crop, crop_sha256=r.source.image_sha256,
                                          review=evidence(r.source.image_sha256)),
                           phone_use=replace(r.phone_use, review=evidence(r.source.image_sha256)),
                           group=replace(r.group, leakage_group_id=r.sample_id)) for r in records]
        write_records(package / "manifest.jsonl", records)
        (package / "checksums.sha256").write_text(
            sha256_file(package / "manifest.jsonl") + "  manifest.jsonl\n")
        for name in ("diagnostics.py", "adaptation_data.py", "adaptation_config.py", "data.py"):
            path = root / "src/ai_exam_monitoring/training" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic source fixture")
        payload = sha256_file(package / "checksums.sha256")
        cuts = [0., math.nextafter(1., 2.)]
        metrics, cohorts = {}, []
        for record, suffix in zip(records, ("train", "selection"), strict=True):
            ts = [.5, .5] if drift and suffix == "train" else cuts
            row = {"sample_id": record.sample_id, "split": record.usage,
                   "source_id": record.source.source_id,
                   "group_id": record.group.leakage_group_id,
                   "targets": list(record.target_values), "mask": list(record.target_mask),
                   "scores": [0., 1.], "decisions": [False, True],
                   "target_order": list(TARGET_ORDER), "calibrated_thresholds": ts,
                   "calibrated_decisions": [0. >= ts[0], 1. >= ts[1]]}
            write_json(run / f"predictions-{suffix}.json", [row])
            entries = {}
            for mode, thresholds in (("fixed", [.5, .5]), ("calibrated", ts)):
                entries[mode] = {"targets": {
                    name: {key.lower(): int(outcome(row, i, thresholds[i]) == key)
                           for key in ("TP", "FP", "FN", "TN")}
                    for i, name in enumerate(TARGET_ORDER)}}
            metrics[suffix] = {**entries["fixed"], "calibrated_thresholds": dict(
                zip(TARGET_ORDER, ts, strict=True)), "calibrated_evaluation": entries["calibrated"]}
            cohorts.append({"role": suffix, "sample_ids": [record.sample_id],
                            "data": {"dataset": "data/package", "payload_sha256": payload}})
        write_json(run / "metrics.json", metrics)
        write_json(run / "run.json", {"status": "FINISHED"})
        write_json(run / "resolved-config.json", {"experiment_id": "run-one",
                   "schema_version": schema, "threshold": .5, "cohorts": cohorts})
        write_json(run / "checksums.json", {p.name: sha256_file(p) for p in run.iterdir()})
        config = {"package": "data/package", "payload_sha256": payload,
                  "run_root": "outputs/campaign/runs", "runs": ["run-one"],
                  "run_checksum_pins": {"run-one": sha256_file(run / "checksums.json")},
                  "recipes": {"D1": ["run-one"]}, "reference_recipe": "D1",
                  "errors_per_bucket": 2, "review_sample_ids": ["val"],
                  "report_output": "artifacts/reports/audit", "media_output": "data/interim/audit"}
        write_json(root / "config.json", config)
        return root / "config.json"

    def test_nested_runs_v4_endpoints_and_confusion_are_audited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            config = self.fixture(root)
            with patch("ai_exam_monitoring.training.diagnostics.make_gallery"):
                summary = build(root, config)
            self.assertEqual(summary["D1_calibrated"]["val"]["phone_use"], {"TP": 1})
            self.assertEqual(summary["D1_fixed"]["val"]["phone_use"], {"FN": 1})
            self.assertTrue((root / "artifacts/reports/audit/operating-envelopes.json").is_file())
            with self.assertRaises(DataContractError):
                build(root, config)

    def test_v4_train_calibration_drift_and_legacy_endpoints_are_rejected(self):
        for kwargs in ({"drift": True}, {"schema": "matched-adaptation-v3"}):
            with self.subTest(kwargs=kwargs), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                config = self.fixture(root, **kwargs)
                with self.assertRaises(DataContractError):
                    build(root, config)
                self.assertFalse((root / "artifacts/reports/audit").exists())

    @unittest.skipUnless(importlib.util.find_spec("torch"), "Install classifier dependencies")
    def test_gallery_preserves_entire_336_input_and_marks_actual_size(self):
        from ai_exam_monitoring.training.adaptation_config import E005AdaptationConfig
        from ai_exam_monitoring.training.data import letterbox

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            package, media = root / "package", root / "media"
            package.mkdir()
            media.mkdir()
            rec = usable_record("val", split="val")
            source = Image.new("RGB", (100, 80), "red")
            source.save(root / "source.png")
            crop = source.crop((10, 0, 80, 80))
            path = package / rec.crop.crop_relpath
            path.parent.mkdir(parents=True)
            crop.save(path)
            rec = replace(rec, source=replace(rec.source, image_relpath="source.png"))
            write_json(root / "roots.json", {rec.source.source_id: "."})
            rc = Mock(spec=E005AdaptationConfig, image_size=336, fill=(124, 116, 104),
                      cohorts=[Mock(role="train", sample_ids=[])])
            cfg = {"reference_recipe": "D1", "recipes": {"D1": ["run"]},
                   "source_roots": "roots.json", "source_roots_sha256": "fixture"}
            with patch("ai_exam_monitoring.training.adaptation_config.config_from_dict",
                       return_value=rc):
                make_gallery(root, package, media, [{"sample_id": "val"}], {"val": rec},
                             {"run": {}}, cfg, lambda *args: None)
            with Image.open(media / "card-001.png") as card:
                self.assertEqual(card.height, 401)
                self.assertEqual(card.crop((712, 55, 1048, 391)).tobytes(),
                                 letterbox(crop, rc).tobytes())
            page = (media / "index.html").read_text(encoding="utf8")
            self.assertIn("336 px", page)
            self.assertNotIn("224", page)


if __name__ == "__main__":
    unittest.main()
