"""Unit tests for tools.inspector (backend and server)."""

from __future__ import annotations

import unittest

from PIL import Image

from tools.inspector.backend import (
    analyze_crop,
    base64_to_image,
    image_to_base64,
    letterbox_image,
    scan_checkpoints,
)


class TestModelInspector(unittest.TestCase):
    def test_scan_checkpoints_finds_best_models(self) -> None:
        ckpts = scan_checkpoints()
        self.assertGreater(len(ckpts), 0)
        self.assertTrue(any(c["is_best"] for c in ckpts))
        self.assertTrue(any("E004-V9-LP" in c["label"] for c in ckpts))

    def test_letterbox_image_exact_dimensions(self) -> None:
        img = Image.new("RGB", (100, 300), (255, 0, 0))
        canvas, tensor = letterbox_image(img, target_size=224)

        self.assertEqual(canvas.size, (224, 224))
        self.assertEqual(tensor.shape, (1, 3, 224, 224))
        corner_pixel = canvas.getpixel((0, 0))
        self.assertEqual(corner_pixel, (124, 116, 104))

    def test_base64_roundtrip(self) -> None:
        img = Image.new("RGB", (64, 64), (10, 20, 30))
        b64 = image_to_base64(img)
        recovered = base64_to_image(b64)
        self.assertEqual(recovered.size, (64, 64))

    def test_analyze_crop_returns_valid_structure(self) -> None:
        ckpts = scan_checkpoints()
        best_lp = next(c for c in ckpts if "E004-V9-LP" in c["label"] and c["is_best"])

        img = Image.new("RGB", (150, 200), (120, 130, 140))
        res = analyze_crop(img, best_lp["path"], threshold=0.5)

        self.assertIn("phone_use", res)
        self.assertIn("looking_around", res)
        self.assertGreaterEqual(res["phone_use"]["score"], 0.0)
        self.assertLessEqual(res["phone_use"]["score"], 1.0)
        self.assertIsInstance(res["phone_use"]["decision"], bool)
        self.assertEqual(res["metadata"]["experiment"], "E004-V9-LP")


if __name__ == "__main__":
    unittest.main()

