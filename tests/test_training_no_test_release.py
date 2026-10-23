import importlib.util
import unittest
from dataclasses import replace

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from test_pilot_schema import usable_record

    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.training.data import _verify_no_test_release


@unittest.skipUnless(ML_AVAILABLE, "Requires classifier CPU dependencies")
class NoTestReleaseTests(unittest.TestCase):
    def setUp(self):
        self.rows = [usable_record("train"), usable_record("val", split="val")]
        self.release = {
            "owner_decision_ref": "owner.json",
            "test_freeze_ref": "owner.json#no-test-development",
            "test_freeze": {
                "status": "not_applicable_zero_test",
                "independent_holdout": "future_separate_protocol",
            },
        }

    def test_explicit_development_protocol_accepts_train_val(self):
        _verify_no_test_release(self.release, self.rows)

    def test_test_record_or_missing_validation_cannot_bypass_freeze(self):
        for rows in (self.rows + [usable_record("test", split="test")], self.rows[:1]):
            with self.subTest(rows=len(rows)), self.assertRaises(DataContractError):
                _verify_no_test_release(self.release, rows)

    def test_unknown_protocol_and_missing_approval_fail(self):
        for change in ({"test_freeze_ref": "unrelated.json"},
                       {"owner_decision_ref": None},
                       {"test_freeze": {"status": "not_applicable_zero_test"}}):
            with self.subTest(change=change), self.assertRaises(DataContractError):
                _verify_no_test_release(dict(self.release, **change), self.rows)

    def test_train_row_cannot_claim_old_test_freeze(self):
        rows = [replace(self.rows[0], test_freeze_ref="old-freeze"), self.rows[1]]
        with self.assertRaises(DataContractError):
            _verify_no_test_release(self.release, rows)
