import importlib.util
import unittest

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.inference.census_review import reviewed_groups


def rel(a, b, kind="same_person", status="owner_confirmed"):
    return dict(anchors=[a, b], relation=kind, status=status)


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class CensusTests(unittest.TestCase):
    def test_only_confirmed_same_is_grouped(self):
        self.assertEqual(
            reviewed_groups(["a", "b", "c", "d"], [rel("a", "b"), rel("c", "d", status="draft")]),
            [["a", "b"], ["c"], ["d"]],
        )

    def test_different_and_unknown_stay_separate(self):
        self.assertEqual(
            reviewed_groups(["a", "b"], [rel("a", "b", "different_person")]), [["a"], ["b"]]
        )
        self.assertEqual(reviewed_groups(["a", "b"], []), [["a"], ["b"]])

    def test_conflicts_and_transitive_merges_rejected(self):
        for rows in (
            [rel("a", "b"), rel("b", "c")],
            [rel("a", "b"), rel("a", "b", "different_person")],
            [rel("a", "missing")],
        ):
            with self.assertRaises(DataContractError):
                reviewed_groups(["a", "b", "c"], rows)

    def test_other_frame_is_ignored(self):
        self.assertEqual(reviewed_groups(["a"], [rel("x", "y")]), [["a"]])
