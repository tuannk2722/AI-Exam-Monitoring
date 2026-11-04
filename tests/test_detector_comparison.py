import copy
import importlib.util
import unittest

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.inference.detector_comparison import validate_census


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class CensusGateTests(unittest.TestCase):
    def setUp(self):
        self.cohort = {"frames": [{"frame_index": 0}]}
        self.census = {
            "status": "accepted",
            "reviewer": "repository-owner",
            "decision_ref": {"path": "receipt"},
            "frames": [
                {
                    "frame_index": 0,
                    "complete_visible_person_census": True,
                    "people": [{"person_id": "p001", "anchors": ["a", "b"]}],
                    "missing_people": [],
                    "false_boxes": [],
                }
            ],
        }

    def test_accepts_complete_census(self):
        validate_census(self.census, self.cohort)

    def test_draft_or_missing_decision_rejected(self):
        for field, value in [("status", "draft"), ("decision_ref", None), ("reviewer", None)]:
            c = copy.deepcopy(self.census)
            c[field] = value
            with self.assertRaises(DataContractError):
                validate_census(c, self.cohort)

    def test_unknown_completeness_and_missing_people_rejected(self):
        for field, value in [
            ("complete_visible_person_census", False),
            ("missing_people", None),
            ("false_boxes", None),
        ]:
            c = copy.deepcopy(self.census)
            c["frames"][0][field] = value
            with self.assertRaises(DataContractError):
                validate_census(c, self.cohort)

    def test_duplicate_assignment_and_wrong_cohort_rejected(self):
        c = copy.deepcopy(self.census)
        c["frames"][0]["people"].append({"person_id": "p002", "anchors": ["a"]})
        with self.assertRaises(DataContractError):
            validate_census(c, self.cohort)
        with self.assertRaises(DataContractError):
            validate_census(self.census, {"frames": [{"frame_index": 1}]})
