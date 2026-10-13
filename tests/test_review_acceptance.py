from __future__ import annotations

import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import (
    ContextReview,
    CropRef,
    GroupReview,
    PilotRecord,
    PixelBox,
    RightsReview,
    SourceRef,
    TargetReview,
    read_records,
    write_records,
)
from ai_exam_monitoring.data.review_acceptance import accept_reviews


class ReviewAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("source.bin", "crop.png", "input.png"):
            (self.root / name).write_bytes(name.encode())
        source_sha = sha256_file(self.root / "source.bin")
        crop_sha = sha256_file(self.root / "crop.png")
        self.record = PilotRecord(
            "S01", "review-v1", "selection-v1", "crop-v1",
            SourceRef("source", "a" * 64, "source.bin", source_sha, 100, 100),
            TargetReview("unknown", "Pending"), TargetReview("unknown", "Pending"),
            ContextReview("unknown", "Not approved"), RightsReview(None, None),
            crop=CropRef("anchor-01", PixelBox(10, 10, 50, 50),
                         PixelBox(0, 0, 90, 90), "crop.png", crop_sha),
            group=GroupReview(), ineligibility_reasons=("group_and_split_pending",),
        )
        self.receipt = {
            "schema_version": "crop-review-acceptance-v1",
            "scope": "labels_and_geometry_only", "target_order": ["phone_use", "looking_around"],
            "ledger_sha256": "b" * 64, "reviewer": "repository-owner",
            "reviewed_at": "2026-10-12",
            "decisions": [{
                "sample_id": "S01", "states": ["P", "U"], "reason": "Reviewed exact crop",
                "geometry_accepted": True, "source_sha256": source_sha,
                "crop_sha256": crop_sha, "input_relpath": "input.png",
                "input_sha256": sha256_file(self.root / "input.png"),
            }],
        }

    def apply(self, receipt=None, record=None):
        return accept_reviews(
            [record or self.record], receipt or self.receipt, ledger_sha256="b" * 64,
            evidence_ref="owner-review.json", workspace=self.root,
        )

    def test_roundtrip_masks_and_no_group_split_context_or_rights_inference(self):
        result = self.apply()[0]
        self.assertEqual(result.target_values, (1, None))
        self.assertEqual(result.target_mask, (1, 0))
        self.assertEqual(result.usage, "review_only")
        self.assertEqual(result.disposition, "approved")
        self.assertIsNone(result.split)
        self.assertIsNone(result.release_review)
        self.assertEqual(result.group, self.record.group)
        self.assertEqual(result.rights, self.record.rights)
        self.assertEqual(result.work_context_review, self.record.work_context_review)
        write_records(self.root / "ledger.jsonl", [result])
        self.assertEqual(read_records(self.root / "ledger.jsonl"), [result])
        self.assertEqual(self.record.target_mask, (0, 0))
        with self.assertRaises(DataContractError):
            replace(result, usage="train", split="train")

    def test_two_negatives_do_not_approve_work_context_and_uu_stays_unsupervised(self):
        for states in (["N", "N"], ["U", "U"]):
            self.receipt["decisions"][0]["states"] = states
            result = self.apply()[0]
            self.assertEqual(result.normal_review, "unknown")
            if states == ["U", "U"]:
                self.assertEqual(result.target_mask, (0, 0))

    def test_reject_wrong_version_order_scope_membership_and_extra_fields(self):
        for key, value in (
            ("schema_version", "future"), ("target_order", ["looking_around", "phone_use"]),
            ("scope", "train"), ("ledger_sha256", "c" * 64), ("extra", True),
            ("decisions", []),
        ):
            receipt = copy.deepcopy(self.receipt)
            receipt[key] = value
            with self.subTest(key=key), self.assertRaises(DataContractError):
                self.apply(receipt)
        for ident in ("OTHER", None):
            receipt = copy.deepcopy(self.receipt)
            receipt["decisions"][0]["sample_id"] = ident
            with self.assertRaises(DataContractError):
                self.apply(receipt)
        self.receipt["decisions"] *= 2
        with self.assertRaises(DataContractError):
            self.apply()

    def test_reject_stale_sha_invalid_states_unapproved_geometry_and_media_escape(self):
        for key, value in (
            ("crop_sha256", "d" * 64), ("source_sha256", "d" * 64),
            ("input_sha256", "d" * 64), ("states", ["N"]), ("states", [False, "P"]),
            ("geometry_accepted", False), ("geometry_accepted", 1), ("reason", " "),
            ("input_relpath", "../outside.png"), ("extra", "train"),
        ):
            receipt = copy.deepcopy(self.receipt)
            receipt["decisions"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(DataContractError):
                self.apply(receipt)
        (self.root / "crop.png").write_bytes(b"recrop")
        with self.assertRaises(DataContractError):
            self.apply()

    def test_accepted_record_cannot_be_reimported(self):
        with self.assertRaises(DataContractError):
            self.apply(record=self.apply()[0])

    def test_cli_pins_and_no_overwrite_or_partial_output(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "review_cli", Path(__file__).parents[1] / "scripts/import_crop_review.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ledger = self.root / "pending.jsonl"
        write_records(ledger, [self.record])
        self.receipt["ledger_sha256"] = sha256_file(ledger)
        decisions = self.root / "decisions.json"
        decisions.write_text(json.dumps(self.receipt), encoding="utf8")
        output = self.root / "data/interim/result"
        # Receipt hashes the module in the declared workspace, too.
        module_path = self.root / "src/ai_exam_monitoring/data/review_acceptance.py"
        module_path.parent.mkdir(parents=True)
        module_path.write_bytes(b"synthetic-module-identity")
        args = (ledger, sha256_file(ledger), decisions, sha256_file(decisions), output, self.root)
        module.build(*args)
        self.assertEqual(read_records(output / "ledger.jsonl")[0].target_values, (1, None))
        with self.assertRaises(DataContractError):
            module.build(*args)
        missing = self.root / "data/interim/rejected"
        with self.assertRaises(DataContractError):
            module.build(ledger, "0" * 64, decisions, sha256_file(decisions), missing, self.root)
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
