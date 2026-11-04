import importlib.util
import unittest

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.inference.matching_review import rank_people


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class MatchingReviewTests(unittest.TestCase):
    def test_ranking_retains_ambiguity(self):
        people = [
            {"person_id": "p002", "location_boxes": [[0, 0, 10, 10]]},
            {"person_id": "p001", "location_boxes": [[0, 0, 10, 10]]},
        ]
        ranked = rank_people([0, 0, 10, 10], people)
        self.assertEqual([r["person_id"] for r in ranked], ["p001", "p002"])
        self.assertTrue(all("accepted_person_id" not in r for r in ranked))

    def test_group_multiple_boxes_and_no_overlap(self):
        people = [{"person_id": "p001", "location_boxes": [[0, 0, 1, 1], [4, 4, 6, 6]]}]
        self.assertEqual(rank_people([4, 4, 6, 6], people)[0]["iou_hint"], 1.0)
        self.assertEqual(rank_people([10, 10, 11, 11], people), [])
