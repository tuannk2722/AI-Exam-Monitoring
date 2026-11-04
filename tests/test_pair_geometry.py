import importlib.util
import unittest

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.inference.pair_geometry import overlap


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class PairGeometryTests(unittest.TestCase):
    def test_containment_is_not_iou_and_float_precision_is_preserved(self):
        result = overlap([0., 0., 10., 10.], [1.5, 1.5, 3.5, 3.5])
        self.assertEqual(result["intersection_over_smaller"], 1.)
        self.assertAlmostEqual(result["iou"], .04)
        self.assertEqual(result, overlap([1.5, 1.5, 3.5, 3.5], [0., 0., 10., 10.]))

    def test_disjoint_touching_identical(self):
        a = [0., 0., 2., 2.]
        self.assertEqual(overlap(a, [2., 0., 4., 2.])["iou"], 0.)
        self.assertEqual(overlap(a, [5., 5., 6., 6.])["intersection_over_smaller"], 0.)
        self.assertEqual(overlap(a, a)["iou"], 1.)

    def test_invalid_geometry_rejected(self):
        for box in ([0., 0., 0., 1.], [0., 0., float("nan"), 2.], [0., 1., 2.]):
            with self.assertRaises(DataContractError):
                overlap(box, [0., 0., 2., 2.])
