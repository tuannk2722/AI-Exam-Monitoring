import copy
import importlib.util
import unittest

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.inference.pose_diagnostic import relation, support


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class PoseDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.rules = dict(
            keypoint_confidence_min=0.5,
            head_indices=[0, 1, 2, 3, 4],
            shoulder_indices=[5, 6],
            minimum_head_points=3,
            minimum_shoulder_points=2,
        )
        self.pose = {"keypoints": [[5.0, 5.0, 0.9] for _ in range(17)]}
        self.box = [0.0, 0.0, 10.0, 10.0]

    def test_unique_and_ambiguous_support(self):
        self.assertEqual(support(self.box, [self.pose], self.rules), [0])
        self.assertEqual(support(self.box, [self.pose, self.pose], self.rules), [0, 1])
        self.assertEqual(relation([0, 1], [0]), "unknown")
        self.assertEqual(relation([], []), "unknown")
        self.assertEqual(relation([0], [0]), "same_proposed")
        self.assertEqual(relation([0], [1]), "different_proposed")

    def test_head_and_shoulder_requirements(self):
        p = copy.deepcopy(self.pose)
        for i in (0, 1, 2):
            p["keypoints"][i][2] = 0.49
        self.assertEqual(support(self.box, [p], self.rules), [])
        p = copy.deepcopy(self.pose)
        p["keypoints"][6][2] = 0.49
        self.assertEqual(support(self.box, [p], self.rules), [])

    def test_all_visible_head_points_must_be_inside(self):
        p = copy.deepcopy(self.pose)
        p["keypoints"][4][0] = 10.01
        self.assertEqual(support(self.box, [p], self.rules), [])
        p["keypoints"][4][2] = 0.49
        self.assertEqual(support(self.box, [p], self.rules), [0])

    def test_invalid_missing_points_abstain(self):
        p = copy.deepcopy(self.pose)
        p["keypoints"][0][0] = float("nan")
        self.assertEqual(support(self.box, [p], self.rules), [])
        self.assertEqual(support(self.box, [{"keypoints": []}], self.rules), [])
