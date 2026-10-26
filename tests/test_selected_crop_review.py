from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.selected_crop_review import (
        exact_cached_match,
        run_review,
        verify_image,
    )


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class SelectedCropTests(unittest.TestCase):
    def test_changed_geometry_confidence_or_ambiguous_anchor_cannot_reuse(self):
        box = {"person_box": [1, 2, 4, 5], "context_box": [0, 0, 6, 7],
               "detector_confidence": .75}
        cached = {**box, "scores": [.2, .8]}
        self.assertIs(exact_cached_match(box, [cached]), cached)
        for key, value in [("person_box", [1, 2, 4, 6]), ("context_box", [0, 0, 6, 8]),
                           ("detector_confidence", .75001)]:
            self.assertIsNone(exact_cached_match({**box, key: value}, [cached]))
        with self.assertRaises(DataContractError):
            exact_cached_match(box, [cached, cached])

    def test_cached_pixels_and_hash_both_required(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "crop.png"
            image = Image.new("RGB", (8, 10), "red")
            image.save(path)
            sha = sha256_file(path)
            verify_image(path, image, sha)
            with self.assertRaises(DataContractError):
                verify_image(path, Image.new("RGB", (8, 10), "blue"), sha)
            with self.assertRaises(DataContractError):
                verify_image(path, image, "0" * 64)
            with self.assertRaises(DataContractError):
                verify_image(path, image.resize((10, 8)), sha)

    def test_no_overwrite_before_config_or_model_load(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with self.assertRaises(DataContractError):
                run_review(path / "missing", path, path)


if __name__ == "__main__":
    unittest.main()
