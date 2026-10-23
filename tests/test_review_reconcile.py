import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import test_pilot_package
from PIL import Image

from ai_exam_monitoring.data.review_reconcile import (
    apply_review_only_policy,
    merge_review,
    rgb_digest,
)


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        r, _, _ = test_pilot_package.PilotPackageTests().make_record(
            Path(self.temp.name), "example", 1)
        self.record = r
        rows = [{"id": r.sample_id, "sha256": r.crop.crop_sha256}]
        cohort = hashlib.sha256(json.dumps(
            [(x["id"], x["sha256"]) for x in rows], separators=(",", ":")
        ).encode()).hexdigest()
        self.inventory = {"records": rows, "cohort": cohort}
        self.review = {"schema": "crop-review-draft-v1", "cohort": cohort,
                       "decisions": {}, "inventory": rows}

    def test_absent_record_and_blank_fields_inherit_but_explicit_unknown_overrides(self):
        baseline = merge_review([self.record], self.inventory, self.review)[0]
        self.assertEqual(baseline["old_pnu"], baseline["effective_pnu"])
        self.review["decisions"]["example"] = {
            "sha256": self.record.crop.crop_sha256, "phone": "U", "looking": "",
            "action": "", "done": False}
        row = merge_review([self.record], self.inventory, self.review)[0]
        self.assertEqual(row["effective_pnu"], ["U", baseline["old_pnu"][1]])
        self.assertEqual(row["label_origin"], ["owner_delta", "v12_inherited"])
        self.assertEqual(row["effective_action"], "keep")

    def test_reject_foreign_cohort_id_sha_and_inventory(self):
        for mutation in ("cohort", "unknown_id", "sha", "inventory", "label"):
            value = copy.deepcopy(self.review)
            if mutation == "cohort":
                value["cohort"] = "bad"
            elif mutation == "inventory":
                value["inventory"] = []
            else:
                value["decisions"]["other" if mutation == "unknown_id" else "example"] = {
                    "sha256": "bad" if mutation == "sha" else self.record.crop.crop_sha256,
                    "phone": "invalid" if mutation == "label" else "P"}
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                merge_review([self.record], self.inventory, value)

    def test_remove_and_notes_are_not_lost_when_done_is_false(self):
        self.review["decisions"]["example"] = {
            "sha256": self.record.crop.crop_sha256, "action": "remove", "done": False,
            "note": "Review geometry"}
        row = merge_review([self.record], self.inventory, self.review)[0]
        self.assertEqual(row["effective_action"], "remove")
        self.assertTrue(row["needs_geometry_review"])

    def test_rgb_hash_includes_shape(self):
        self.assertNotEqual(rgb_digest(Image.new("RGB", (2, 4))),
                            rgb_digest(Image.new("RGB", (4, 2))))

    def test_review_only_requires_substantive_input_not_ui_metadata(self):
        base = {"old_usage": "review_only", "effective_action": "keep",
                "needs_geometry_review": False}
        for decision, expected in [({}, "remove"), ({"phone": "", "done": False}, "remove"),
                                   ({"angle": "front", "tags": "tag"}, "remove"),
                                   ({"phone": "N"}, "keep"), ({"action": "keep"}, "keep"),
                                   ({"note": "recrop"}, "keep")]:
            with self.subTest(decision=decision):
                row = {**base, "owner_delta": decision}
                self.assertEqual(apply_review_only_policy([row])[0]["effective_action"], expected)
                self.assertEqual(row["effective_action"], "keep")
        self.assertEqual(apply_review_only_policy([
            {**base, "old_usage": "train", "owner_delta": {}}
        ])[0]["effective_action"], "keep")


if __name__ == "__main__":
    unittest.main()
