"""Synthetic cohort/unknown/selection guards for cached-score diagnostics."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.training.diagnostics import consensus, local, outcome, shortlist


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


if __name__ == "__main__":
    unittest.main()
