import hashlib
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import test_pilot_package
from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_package import _preflight, build_pilot_package
from ai_exam_monitoring.data.pilot_schema import (
    DERIVED_SCHEMA_VERSION,
    CropDerivation,
    record_from_dict,
    record_to_dict,
)


class DerivedCropTests(unittest.TestCase):
    def test_import_integrity_and_native_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row, source_root, crop = test_pilot_package.PilotPackageTests().make_record(
                root, "D001", 1)
            original = record_to_dict(row)
            self.assertNotIn("derivation", original["crop"])
            self.assertEqual(original, record_to_dict(record_from_dict(original)))
            with Image.open(crop) as image:
                native_sha = hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()
                image.resize((6, 6)).save(crop, format="JPEG")
            digest = sha256_file(crop)
            review = replace(row.crop.review, crop_sha256=digest)
            target = replace(row.phone_use, review=review)
            native = replace(row, crop=replace(row.crop, crop_sha256=digest, review=review),
                             phone_use=target)
            with self.assertRaisesRegex(DataContractError, "pixels"):
                _preflight([native], {"rf": source_root}, {row.sample_id: crop})
            derivation = CropDerivation(row.source.image_sha256, native_sha, 6, 6,
                                        "JPEG", "fixture-import", review)
            derived = replace(native, schema_version=DERIVED_SCHEMA_VERSION,
                              crop=replace(native.crop, derivation=derivation))
            self.assertEqual(derived, record_from_dict(record_to_dict(derived)))
            _preflight([derived], {"rf": source_root}, {row.sample_id: crop})
            derived = replace(derived, crop=replace(derived.crop, crop_relpath="crops/D001.jpg"))
            for name in ("package-a", "package-b"):
                build_pilot_package(
                    [derived], root / name, {"rf": source_root}, {row.sample_id: crop}, [],
                    {"status": "prepared_pending_gates", "dataset_version": row.dataset_version,
                     "git_commit": "fixture"}, [row.sample_id])
                self.assertEqual((root / name / "crops/D001.jpg").read_bytes(), crop.read_bytes())
            self.assertEqual((root / "package-a/checksums.sha256").read_bytes(),
                             (root / "package-b/checksums.sha256").read_bytes())
            from ai_exam_monitoring.training.data import crop_path
            self.assertEqual(crop_path(root / "package-a", derived),
                             root / "package-a/crops/D001.jpg")
            bad_dimensions = replace(derived, crop=replace(derived.crop,
                                     derivation=replace(derivation, output_width=8)))
            with self.assertRaisesRegex(DataContractError, "dimensions"):
                crop_path(root / "package-a", bad_dimensions)
            with self.assertRaisesRegex(DataContractError, "requires exact"):
                _preflight([derived], {"rf": source_root}, {})
            for change in ({"native_roi_rgb_sha256": "0" * 64}, {"output_width": 8},
                           {"output_format": "PNG"}):
                bad = replace(derived, crop=replace(derived.crop,
                              derivation=replace(derivation, **change)))
                with self.assertRaisesRegex(DataContractError, "provenance"):
                    _preflight([bad], {"rf": source_root}, {row.sample_id: crop})
            with self.assertRaises(DataContractError):
                replace(derived, schema_version="pilot-b-manifest-v1")
            with self.assertRaises(DataContractError):
                replace(derived, crop=replace(derived.crop,
                        derivation=replace(derivation, source_sha256="0" * 64)))
            payload = record_to_dict(derived)
            payload["crop"]["derivation"]["unknown_field"] = True
            with self.assertRaises(DataContractError):
                record_from_dict(payload)
            crop.write_bytes(b"tampered")
            with self.assertRaisesRegex(DataContractError, "checksum"):
                _preflight([derived], {"rf": source_root}, {row.sample_id: crop})


if __name__ == "__main__":
    unittest.main()
