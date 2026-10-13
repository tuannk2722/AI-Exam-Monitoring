import hashlib
import importlib.util
import io
import tempfile
import unittest
import warnings
import zipfile
from dataclasses import replace
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import PixelBox
from ai_exam_monitoring.data.source_review import (
    PinnedYoloZip,
    descriptor_distance,
    diverse_inspection,
    fingerprint,
    member_key,
    preview_input,
    write_pending_crop,
)


class SourceReviewTests(unittest.TestCase):
    def make_zip(self, root, label="0 0.5 0.5 0.4 0.4\n", duplicate=None):
        image = Image.new("RGB", (40, 20), (50, 100, 150))
        payload = io.BytesIO()
        image.save(payload, format="PNG")
        path = root / "source.zip"
        with zipfile.ZipFile(path, "w") as stream:
            stream.writestr("train/images/image.png", payload.getvalue())
            stream.writestr("train/labels/image.txt", label)
            if duplicate:
                stream.writestr(duplicate, b"ambiguous")
        return path, payload.getvalue()

    def test_pin_pairing_empty_and_reject_partial_bad_annotations(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, raw = self.make_zip(root, label="")
            with self.assertRaises(DataContractError):
                PinnedYoloZip(path, "0" * 64, {0: "hint"})
            reader = PinnedYoloZip(path, sha256_file(path), {0: "hint"})
            try:
                source = reader.read(
                    member_key("train/images/image.png"), hashlib.sha256(raw).hexdigest()
                )
                self.assertEqual(source.annotations, ())
                self.assertEqual(fingerprint(source)["canonical_targets"], [None, None])
                with self.assertRaises(DataContractError):
                    reader.read(source.member_sha256, "0" * 64)
            finally:
                reader.close()
            path, _ = self.make_zip(root, label="0 0.5 0.5 0.4 0.4\n0 0.5 0.5 0 0.4")
            reader = PinnedYoloZip(path, sha256_file(path), {0: "hint"})
            try:
                with self.assertRaises(DataContractError):
                    reader.read(member_key("train/images/image.png"))
            finally:
                reader.close()

    def test_duplicate_and_traversal_members_fail(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for extra in ("train/images/image.png", "../escape.png"):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    path, _ = self.make_zip(root, duplicate=extra)
                with self.assertRaises(DataContractError):
                    PinnedYoloZip(path, sha256_file(path), {0: "hint"})

    def test_pending_crop_not_supervision_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path, _ = self.make_zip(root)
            reader = PinnedYoloZip(path, sha256_file(path), {0: "device_hint"})
            try:
                source = reader.read(member_key("train/images/image.png"))
                row = write_pending_crop(
                    source,
                    PixelBox(10, 5, 25, 15),
                    PixelBox(5, 0, 35, 20),
                    "DRAFT-01",
                    root / "review",
                    states=("P", "N"),
                    reason="Visual draft only",
                    input_size=224,
                    fill=(124, 116, 104),
                )
                self.assertFalse(row["owner_approved"])
                self.assertEqual(row["canonical_mask"], [0, 0])
                self.assertEqual(row["usage"], "review_only")
                self.assertIsNone(row["split"])
                self.assertEqual(
                    row["source_sha256"], sha256_file(root / "review/DRAFT-01/source.bin")
                )
                with self.assertRaises(DataContractError):
                    write_pending_crop(
                        source,
                        PixelBox(10, 5, 25, 15),
                        PixelBox(5, 0, 35, 20),
                        "DRAFT-01",
                        root / "review",
                        states=("P", "N"),
                        reason="same",
                        input_size=224,
                        fill=(124, 116, 104),
                    )
                with self.assertRaises(DataContractError):
                    write_pending_crop(
                        source,
                        PixelBox(10, 5, 25, 15),
                        PixelBox(5, 0, 41, 20),
                        "DRAFT-02",
                        root / "review",
                        states=("P", "N"),
                        reason="outside",
                        input_size=224,
                        fill=(124, 116, 104),
                    )
            finally:
                reader.close()

    def test_diverse_inspection_deterministic_not_independence(self):
        rows = [
            {"source_sha256": str(i), "scene_descriptor": [i] * 288, "independence_proven": False}
            for i in [0, 100, 200]
        ]
        selected = diverse_inspection(rows, [rows[0]], 2)
        self.assertEqual([r["source_sha256"] for r in selected], ["200", "100"])
        self.assertEqual(selected, diverse_inspection(list(reversed(rows)), [rows[0]], 2))
        self.assertFalse(any(r["independence_proven"] for r in selected))
        with self.assertRaises(DataContractError):
            descriptor_distance([0], [0])

    def test_preview_geometry_and_padding(self):
        image = Image.new("RGB", (100, 50), (200, 10, 20))
        output = preview_input(image, 224, (124, 116, 104))
        self.assertEqual(output.size, (224, 224))
        self.assertEqual(output.getpixel((0, 0)), (124, 116, 104))
        self.assertEqual(output.getpixel((112, 112)), (200, 10, 20))

    @unittest.skipUnless(
        all(importlib.util.find_spec(n) for n in ("torch", "torchvision")),
        "Install classifier dependencies for preprocessing parity",
    )
    def test_review_pixels_match_training_consumer(self):
        from test_training import config

        from ai_exam_monitoring.training.data import letterbox

        current = replace(config(), image_size=224)
        for mode in ("RGB", "RGBA", "L"):
            for size in ((175, 308), (1001, 111), (1, 300)):
                with self.subTest(mode=mode, size=size):
                    source = Image.new(mode, size, 7)
                    source.putpixel((0, 0), source.convert("RGB").getpixel((0, 0))[0])
                    preview = preview_input(source, current.image_size, tuple(current.fill))
                    self.assertEqual(preview.tobytes(), letterbox(source, current).tobytes())


if __name__ == "__main__":
    unittest.main()
