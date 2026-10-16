"""External crop audit integrity and unknown-label boundaries."""

import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.crop_bundle_audit import (
    candidate_issues,
    image_fingerprint,
    read_pinned_zip,
    safe_member,
)


class CropBundleAuditTests(unittest.TestCase):
    def test_paths(self) -> None:
        for name in ("../x", "/x", "C:/x", "a\\b", "a/../b", "a//b", "a./b"):
            with self.assertRaises(DataContractError):
                safe_member(name)
        safe_member("crops/p/frame.jpg")

    def test_zip_pin_and_crc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.zip"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("a.txt", b"hello")
            self.assertEqual(read_pinned_zip(path, sha256_file(path)), {"a.txt": b"hello"})
            with self.assertRaises(DataContractError):
                read_pinned_zip(path, "0" * 64)

    def test_case_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a.zip"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("A.jpg", b"a")
                z.writestr("a.jpg", b"b")
            with self.assertRaises(DataContractError):
                read_pinned_zip(path, sha256_file(path))

    def test_rgb_fingerprint_is_independent_of_encoding(self) -> None:
        image = Image.new("RGB", (9, 8), "red")
        a, b = io.BytesIO(), io.BytesIO()
        image.save(a, "PNG", compress_level=0)
        image.save(b, "PNG", compress_level=9)
        fa, fb = image_fingerprint(a.getvalue()), image_fingerprint(b.getvalue())
        self.assertNotEqual(fa["sha256"], fb["sha256"])
        self.assertEqual(fa["rgb_sha256"], fb["rgb_sha256"])
        with self.assertRaises(OSError):
            image_fingerprint(b"not an image")

    def test_unknown_and_geometry(self) -> None:
        row = dict(
            crop_file="crops/a.jpg",
            source_frame="derived/a.jpg",
            phone="U",
            looking="P",
            source_width=100,
            source_height=100,
            crop_width=224,
            crop_height=224,
            frame_num=1,
            bbox_xyxy=[0, 0, 50, 50],
            anchor_center_xy=[25, 25],
            split=None,
            training_ready=False,
            label_status="provisional",
            review_only=True,
            parent_id="p",
            source_group="p",
        )
        self.assertEqual(candidate_issues(row), [])
        self.assertEqual(row["phone"], "U")
        self.assertIn("box_outside_source", candidate_issues({**row, "bbox_xyxy": [0, 0, 101, 50]}))
        self.assertIn("invalid_phone", candidate_issues({**row, "phone": "normal"}))
        self.assertIn("unexpected_assignment", candidate_issues({**row, "split": "train"}))


if __name__ == "__main__":
    unittest.main()
