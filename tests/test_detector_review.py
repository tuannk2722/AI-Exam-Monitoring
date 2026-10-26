from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.detector_review import (
        assert_baseline_parity,
        draft_review,
        preflight,
        run_ablation,
        serialize_boxes,
        validate_review,
        validate_run_review,
    )
    from ai_exam_monitoring.inference.person import PersonDetection
    from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
    from ai_exam_monitoring.training.artifacts import digest_json


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class DetectorReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.margins = {"left": .2, "right": .2, "top": .1, "bottom": .2}
        self.detection = PersonDetection((1.2, 2.4, 9.1, 11.7), .75)
        image_path = self.root / "source.png"
        Image.new("RGB", (20, 20), "white").save(image_path)
        boxes = serialize_boxes([self.detection], (20, 20), self.margins)
        self.cohort = {"media_delete_by": "2099-01-01T00:00:00+00:00", "frames": [
            {"frame_index": 30, "video_time_ms": 1000.,
             "source_png": {"path": "source.png", "sha256": sha256_file(image_path)},
             "baseline_observations": [{**boxes[0], "anchor_id": "a000"}]}]}
        self.review = {"schema_version": "detector-person-review-v1", "status": "accepted",
                       "cohort_sha256": "c" * 64, "reviewer": "repository-owner",
                       "decision_ref": "synthetic-owner-fixture", "frames": [
                           {"frame_index": 30, "complete_visible_person_census": True,
                            "people": [{"person_id": "p01", "location_description": "left"},
                                       {"person_id": "p02", "location_description": "rear"}],
                            "baseline_assignment": {"a000": "p01"}, "unresolved_cases": []}]}
        self.raw = {"run_id": "synthetic", "pins": {"cohort": {"sha256": "c" * 64}},
                    "arms": [{"id": "D0", "conf": .25, "iou": .7},
                             {"id": "D1", "conf": .25, "iou": .5},
                             {"id": "D2", "conf": .25, "iou": .3}]}
        self.baseline = RuntimeConfig({"crop": self.margins,
                                      "classifier": {"threads": 1}, "detector": {
            "conf": .25, "iou": .7, "imgsz": 640, "max_det": 100,
            "device": "cpu", "half": False}}, self.root)
        self.review_path = self.root / "review.json"
        self.review_path.write_text(json.dumps(self.review))

    def test_float_and_integer_geometry_and_strict_parity(self):
        boxes = serialize_boxes([self.detection], (20, 20), self.margins)
        self.assertEqual(boxes[0]["xyxy_float"], [1.2, 2.4, 9.1, 11.7])
        self.assertEqual(boxes[0]["person_box"], [1, 2, 10, 12])
        assert_baseline_parity(boxes, self.cohort["frames"][0]["baseline_observations"])
        for key, value in [("detector_confidence", .750001), ("person_box", [1, 2, 9, 12])]:
            changed = copy.deepcopy(boxes)
            changed[0][key] = value
            with self.subTest(key=key), self.assertRaises(DataContractError):
                assert_baseline_parity(changed, boxes)
        with self.assertRaises(DataContractError):
            serialize_boxes([PersonDetection((1., 2., float("nan"), 5.), .8)],
                            (20, 20), self.margins)

    def test_review_allows_missed_people_and_rejects_unknown_or_incomplete(self):
        validate_review(self.review, self.cohort, "c" * 64)
        for key, value in [("complete_visible_person_census", False),
                           ("baseline_assignment", {"a000": "unknown"}),
                           ("baseline_assignment", {}), ("unresolved_cases", ["occluded"]),
                           ("frame_index", 31)]:
            review = copy.deepcopy(self.review)
            review["frames"][0][key] = value
            with self.subTest(key=key), self.assertRaises(DataContractError):
                validate_review(review, self.cohort, "c" * 64)
        for key, value in [("status", "draft"), ("cohort_sha256", "d" * 64),
                           ("decision_ref", None)]:
            with self.subTest(key=key), self.assertRaises(DataContractError):
                validate_review({**self.review, key: value}, self.cohort, "c" * 64)

    def test_existing_output_fails_before_preflight(self):
        with patch("ai_exam_monitoring.inference.detector_review.preflight") as preflight:
            with self.assertRaises(DataContractError):
                run_ablation(Path("missing"), self.root, self.review_path, self.root)
        preflight.assert_not_called()

    def test_diagnostic_review_stays_draft_and_requires_exact_pin(self):
        review = {**self.review, "status": "draft", "reviewer": None, "decision_ref": None}
        raw = {**self.raw, "schema_version": "detector-ablation-config-v2",
               "review_policy": "diagnostic_unknown_no_selection",
               "pins": {**self.raw["pins"], "draft_review": {"sha256": "d" * 64}}}
        validate_run_review(raw, review, self.cohort, "d" * 64)
        with self.assertRaises(DataContractError):
            validate_run_review(raw, review, self.cohort, "e" * 64)
        with self.assertRaises(DataContractError):
            validate_run_review(raw, self.review, self.cohort, "d" * 64)
        with self.assertRaises(DataContractError):
            validate_run_review(self.raw, review, self.cohort, "d" * 64)

    def test_diagnostic_preflight_requires_explicit_scope(self):
        raw = {**self.raw, "schema_version": "detector-ablation-config-v2",
               "classifier_inference": False, "role_policy": "unknown_diagnostic_only",
               "review_policy": "diagnostic_unknown_no_selection", "approval_ref": "approval"}
        approval = {"status": "approved", "run_id": raw["run_id"],
                    "config_sha256": digest_json(raw), "scope": ["implementation"],
                    "cohort_labels_accepted": False, "quality_acceptance": False}
        prefix = "ai_exam_monitoring.inference.detector_review."
        with patch(prefix + "load_yaml", return_value=raw), \
                patch(prefix + "read_object", return_value=approval):
            with self.assertRaisesRegex(DataContractError, "exception approval"):
                preflight(Path("fixture"), self.root)

    def test_diagnostic_run_preserves_unknown_and_never_selects_winner(self):
        self.review_path.write_text(json.dumps({**self.review, "status": "draft"}))
        raw = {**self.raw, "schema_version": "detector-ablation-config-v2",
               "review_policy": "diagnostic_unknown_no_selection",
               "pins": {**self.raw["pins"],
                        "draft_review": {"sha256": sha256_file(self.review_path)}}}
        prefix = "ai_exam_monitoring.inference.detector_review."
        output = self.root / "outputs" / "diagnostic"
        with patch(prefix + "preflight", return_value=(raw, self.baseline, self.cohort, {})), \
                patch(prefix + "PersonDetector") as factory, \
                patch(prefix + "environment", return_value={}), \
                patch(prefix + "code_identity", return_value={}):
            factory.return_value.predict.return_value = [self.detection]
            run_ablation(Path("fixture"), self.root, self.review_path, output)
        run = json.loads((output / "run.json").read_text())
        self.assertEqual(run["quality_acceptance"], "not_evaluated_diagnostic")
        self.assertIsNone(run["winner"])
        review = json.loads((output / "person-review.json").read_text())
        self.assertEqual(review["status"], "draft")
        matching = json.loads((output / "matching-draft.json").read_text())
        self.assertTrue(all(v == "unknown" for row in matching["frames"]
                            for v in row["assignment"].values()))

    def test_draft_groups_are_not_accepted_and_do_not_mutate_cohort(self):
        cohort = copy.deepcopy(self.cohort)
        first = cohort["frames"][0]["baseline_observations"][0]
        cohort["frames"][0]["baseline_observations"].append({**first, "anchor_id": "a001"})
        cohort["pair_candidates"] = [{"case_id": "C01", "frame_index": 30,
                                      "anchor_ids": ["a000", "a001"],
                                      "draft_relation": "same_person_candidate"}]
        original = copy.deepcopy(cohort)
        draft = draft_review(cohort, "c" * 64)
        self.assertEqual(cohort, original)
        self.assertEqual(len(draft["frames"][0]["people"]), 1)
        self.assertIn("C01", draft["frames"][0]["unresolved_cases"])
        with self.assertRaises(DataContractError):
            validate_review(draft, cohort, "c" * 64)

    def test_draft_review_blocks_detector_construction(self):
        self.review_path.write_text(json.dumps({**self.review, "status": "draft"}))
        prefix = "ai_exam_monitoring.inference.detector_review."
        with patch(prefix + "preflight", return_value=(self.raw, self.baseline, self.cohort, {})), \
                patch(prefix + "PersonDetector") as detector:
            with self.assertRaises(DataContractError):
                run_ablation(Path("fixture"), self.root, self.review_path,
                             self.root / "outputs" / "draft")
        detector.assert_not_called()

    def test_each_arm_runs_detector_and_parity_failure_stops_candidates(self):
        prefix = "ai_exam_monitoring.inference.detector_review."
        for fail in (False, True):
            calls = []
            detection = self.detection

            class FixtureDetector:
                variables = {}

                def predict(inner, image, calls=calls, fail=fail, detection=detection):
                    calls.append(inner.variables.copy())
                    return [] if fail else [detection]

            output = self.root / "outputs" / str(fail)
            with patch(prefix + "preflight",
                       return_value=(self.raw, self.baseline, self.cohort, {})), \
                    patch(prefix + "PersonDetector", return_value=FixtureDetector()), \
                    patch(prefix + "environment", return_value={}), \
                    patch(prefix + "code_identity", return_value={}):
                if fail:
                    with self.assertRaises(DataContractError):
                        run_ablation(Path("fixture"), self.root, self.review_path, output)
                else:
                    run_ablation(Path("fixture"), self.root, self.review_path, output)
            run = json.loads((output / "run.json").read_text())
            self.assertEqual(run["status"], "failed" if fail else "completed")
            self.assertEqual([v["iou"] for v in calls], [.7] if fail else [.7, .5, .3])
            self.assertEqual(run["completed_forwards"], 1 if fail else 3)
            self.assertEqual(run["media_delete_by"], self.cohort["media_delete_by"])
            self.assertEqual(run["quality_acceptance"], "pending_review")
            checksums = json.loads((output / "checksums.json").read_text())
            for name, sha in checksums.items():
                self.assertEqual(sha256_file(output / name), sha)


if __name__ == "__main__":
    unittest.main()
