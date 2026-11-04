import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np
import test_pilot_package
from PIL import Image

from ai_exam_monitoring.data.review_workspace import (
    accepted_records,
    visual_features,
    visual_groups,
)


class ReviewWorkspaceTests(unittest.TestCase):
    def test_approved_review_only_included_excluded_omitted(self):
        with tempfile.TemporaryDirectory() as td:
            r, _, _ = test_pilot_package.PilotPackageTests().make_record(Path(td), "approved", 1)
            excluded = replace(r, sample_id="excluded", disposition="excluded",
                               usage="excluded", exclusion_reason="superseded")
            self.assertEqual([x.sample_id for x in accepted_records([excluded, r])], ["approved"])
            with self.assertRaises(ValueError):
                accepted_records([r, r])

    def test_grouping_covers_every_index_once_and_is_deterministic(self):
        rng = np.random.default_rng(1)
        x = rng.normal(size=(60, 15)).astype(np.float32)
        groups = visual_groups(x, 7)
        self.assertEqual(sorted(i for g in groups for i in g), list(range(60)))
        self.assertEqual(groups, visual_groups(x, 7))

    def test_identical_images_not_lost_to_empty_clusters(self):
        x = np.zeros((20, 10), dtype=np.float32)
        self.assertEqual(visual_groups(x, 8), [list(range(20))])

    def test_features_use_pixels_and_geometry_only(self):
        a = visual_features(Image.new("RGB", (100, 200), (90, 120, 150)))
        b = visual_features(Image.new("RGB", (200, 400), (90, 120, 150)))
        np.testing.assert_array_equal(a, b)
        self.assertFalse(np.array_equal(a, visual_features(
            Image.new("RGB", (200, 100), (90, 120, 150)))))


if __name__ == "__main__":
    unittest.main()
