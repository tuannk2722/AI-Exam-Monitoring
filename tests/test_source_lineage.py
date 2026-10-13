import unittest

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.source_lineage import lineage_components


class SourceLineageTests(unittest.TestCase):
    def inventory(self, member, sha, lineage, source="A"):
        return dict(source_id=source, member_sha256=member, source_sha256=sha,
                    archive_sha256=source, lineage_hint_sha256=lineage)

    def assessment(self, row, scene="scene", role="holdout"):
        return {**row, "draft_scene_boundary": scene, "draft_role": role,
                "review_id": row["member_sha256"], "confirmed_parent_scene_overlap": False}

    def test_transitive_links_conflicts_and_no_independence_inference(self):
        rows = [self.inventory("1", "x", "l"), self.inventory("2", "y", "l"),
                self.inventory("3", "y", "m", "B"), self.inventory("4", "z", "n", "B")]
        reviews = [self.assessment(rows[0]), self.assessment(rows[2], "other", "development"),
                   self.assessment(rows[3], "other", "development")]
        parent = [dict(source_sha256="z", usages=["train"], sample_ids=["OLD"])]
        result = lineage_components(rows, reviews, parent)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["member_keys"]), 4)
        self.assertTrue(result[0]["reserve_role_conflict"])
        self.assertFalse(result[0]["independence_proven"])
        self.assertEqual(result[0]["exact_non_test_parent_samples"], ["OLD"])
        self.assertEqual(result, lineage_components(list(reversed(rows)), reviews, parent))

    def test_same_filename_hint_across_archives_is_not_an_edge(self):
        rows = [self.inventory("1", "x", "l"), self.inventory("2", "y", "l", "B")]
        reviews = [self.assessment(rows[0], "one"), self.assessment(rows[1], "two")]
        self.assertEqual(len(lineage_components(rows, reviews, [])), 2)

    def test_reject_bad_assessment_pins_duplicates_and_test_fingerprints(self):
        row = self.inventory("1", "x", "l")
        review = self.assessment(row)
        for inventory, reviews, parent in (
            ([row, row], [review], []), ([row], [review, review], []),
            ([row], [{**review, "source_sha256": "changed"}], []),
            ([row], [review], [dict(source_sha256="t", usages=["test"], sample_ids=["T"])]),
        ):
            with self.assertRaises(DataContractError):
                lineage_components(inventory, reviews, parent)


if __name__ == "__main__":
    unittest.main()
