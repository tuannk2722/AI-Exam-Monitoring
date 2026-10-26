from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import numpy as np

AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "ultralytics", "lap"))
if AVAILABLE:
    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.tracking import (
        assignments,
        load_inputs,
        run_arm,
        technical_summary,
        tracker_factory,
        validate_frames,
    )
    from ai_exam_monitoring.inference.tracking_review import draft_cases


def frame(index=0, items=None):
    if items is None:
        items = [(10, .9)]
    return {"frame_index": index * 30, "video_time_ms": index * 1000,
            "width": 400, "height": 200,
            "observations": [{"anchor_id": f"f{index}-a{i}",
                              "person_box": [x, 10, x + 30, 90],
                              "detector_confidence": score}
                             for i, (x, score) in enumerate(items)]}


@unittest.skipUnless(AVAILABLE, "Install pinned tracking dependencies")
class TrackingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.settings = {"ultralytics_version": "8.3.221", "proposed_lap_version": "0.5.12",
                         "track_buffer": 60, "match_thresh": .8, "fuse_score": True,
                         "frame_rate": 1, "expected_max_time_lost_updates": 2}
        self.arm = {"arm_id": "B1", "type": "bytetrack", "track_high_thresh": .5,
                    "track_low_thresh": .25, "new_track_thresh": .5}
        self.auth = {"media_delete_by": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                     "source_sha256": "synthetic"}

    def tracker(self):
        return tracker_factory(self.settings, self.arm, self.root)

    def test_filtered_indices_and_permutation(self):
        tracker = self.tracker()
        first, _ = assignments(frame(items=[(10, .9), (100, .9), (200, .9)]), tracker, 0)
        ids = [r["track_id"] for r in first]
        second, _ = assignments(frame(1, [(200, .3), (10, .8), (100, .4)]), tracker, 0)
        self.assertEqual([r["track_id"] for r in second], [ids[2], ids[0], ids[1]])
        self.assertEqual([r["anchor_id"] for r in second], ["f1-a0", "f1-a1", "f1-a2"])

    def test_late_appearance_is_not_fabricated(self):
        tracker = self.tracker()
        self.assertEqual(assignments(frame(items=[]), tracker, 0)[0], [])
        rows, _ = assignments(frame(1), tracker, 0)
        self.assertIsNone(rows[0]["track_id"])
        rows, _ = assignments(frame(2), tracker, 0)
        self.assertIsNotNone(rows[0]["track_id"])

    def test_gap_recovery_and_expiry(self):
        tracker = self.tracker()
        first = assignments(frame(), tracker, 0)[0][0]["track_id"]
        assignments(frame(1, []), tracker, 0)
        recovered = assignments(frame(2), tracker, 0)[0][0]["track_id"]
        self.assertEqual(first, recovered)
        for i in range(3, 8):
            assignments(frame(i, []), tracker, 0)
        assignments(frame(8), tracker, 0)
        new = assignments(frame(9), tracker, 0)[0][0]["track_id"]
        self.assertIsNotNone(new)
        self.assertNotEqual(first, new)

    def test_session_reset(self):
        first = assignments(frame(), self.tracker(), 0)[0][0]["track_id"]
        second = assignments(frame(), self.tracker(), 0)[0][0]["track_id"]
        self.assertEqual(first, second)

    def test_no_tracking_gives_unique_anchor_ids(self):
        first, number = assignments(frame(), None, 0)
        second, _ = assignments(frame(1), None, number)
        self.assertNotEqual(first[0]["track_id"], second[0]["track_id"])

    def test_invalid_result_mapping_rejected(self):
        class Invalid:
            def update(self, detections):
                return np.array([[0, 0, 20, 20, 1, .9, 0, 9]])
        with self.assertRaises(DataContractError):
            assignments(frame(), Invalid(), 0)

    def test_input_validation(self):
        validate_frames([frame(), frame(1, [])], 1)
        invalid = [frame(), frame(1)]
        invalid[1]["video_time_ms"] = 2000
        with self.assertRaises(DataContractError):
            validate_frames(invalid, 1)
        invalid = frame()
        invalid["observations"][0]["person_box"][0] = -1
        with self.assertRaises(DataContractError):
            validate_frames([invalid], 1)

    def test_dependency_check_precedes_import(self):
        with patch("ai_exam_monitoring.inference.tracking.version", return_value="wrong"), \
                patch("ai_exam_monitoring.inference.tracking.import_module") as imp:
            with self.assertRaises(DataContractError):
                self.tracker()
            imp.assert_not_called()

    def test_technical_counts_are_not_quality(self):
        rows = [{"assignments": [{"track_id": 1}, {"track_id": None}]},
                {"assignments": []}, {"assignments": [{"track_id": 1}]}]
        result = technical_summary(rows, [1, 2, 3])
        self.assertEqual(result["assigned"], 2)
        self.assertEqual(result["tracks"][0]["gap_count"], 1)
        self.assertIsNone(result["quality_metrics"])

    def test_failed_outcome_and_expired_deadline(self):
        config = {"tracker": self.settings}
        auth = {**self.auth,
                "media_delete_by": (datetime.now(UTC) - timedelta(seconds=1)).isoformat()}
        out = self.root / "failed"
        with self.assertRaises(ConfigurationError):
            run_arm({"arm_id": "N0", "type": "no_tracking"}, config, [frame()],
                    auth, {"session.json": {"sha256": "x"}}, self.root, out, {}, {})
        self.assertEqual(json.loads((out / "session.json").read_text())["status"], "failed")
        self.assertTrue((out / "checksums.json").exists())

    def test_parent_mutation_fails_after_processing(self):
        out = self.root / "mutation"
        pin = {"session.json": {"path": "parent.json", "sha256": "0" * 64}}
        (self.root / "parent.json").write_text("changed")
        with self.assertRaises(ConfigurationError):
            run_arm({"arm_id": "N0", "type": "no_tracking"}, {}, [frame()], self.auth,
                    pin, self.root, out, {}, {})
        self.assertEqual(json.loads((out / "session.json").read_text())["status"], "failed")

    def fixture(self):
        def save(name, obj):
            path = self.root / name
            path.write_text(json.dumps(obj), encoding="utf-8")
            return {"path": name, "sha256": sha256_file(path)}
        parent = {**self.auth, "status": "approved", "rights_confirmed": True,
                  "test_or_holdout": False, "third_party_processing": False,
                  "access": "repository_owner"}
        media = save("media.json", parent)
        session = {**self.auth, "status": "completed", "runtime_id": "test",
                   "media_approval_sha256": media["sha256"], "frames": 1,
                   "observations": 1, "sampled_frame_indices": [0]}
        predictions = self.root / "predictions.jsonl"
        rows = [{"schema_version": "recorded-observations-v1", "record_type": "metadata",
                 "source_sha256": "synthetic"}, {**frame(), "record_type": "frame"},
                {"record_type": "outcome", "status": "completed"}]
        predictions.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        pins = {"session.json": save("session.json", session),
                "predictions.jsonl": {"path": "predictions.jsonl",
                                      "sha256": sha256_file(predictions)}}
        config = {"proposal_id": "test", "parent_runtime_id": "test", "sampling_hz": 1,
                  "expected_samples": 1, "expected_observations": 1,
                  "arms": [{"arm_id": a} for a in ("N0", "B0", "B1")], "media": self.auth}
        auth = {**self.auth, "schema_version": "tracking-authorization-v1", "status": "approved",
                "proposal_id": "test", "access": "repository_owner", "upload": False,
                "events": False, "risk": False, "web": False,
                "allowed_actions": ["implementation", "synthetic_checks", "replay_N0_B0_B1",
                                    "local_review_gallery"],
                "design": save("design.json", {}), "proposal": save("config.yaml", config),
                "preflight": save("preflight.json", {"input_pins": pins}), "parent_media": media}
        save("authorization.json", auth)
        return self.root / "authorization.json", auth

    def test_input_guard_and_pinned_mutation(self):
        path, _ = self.fixture()
        self.assertEqual(len(load_inputs(path, self.root)[2]), 1)
        (self.root / "predictions.jsonl").write_text("{}")
        with self.assertRaises(ConfigurationError):
            load_inputs(path, self.root)

    def test_approval_and_retention_cannot_be_extended(self):
        path, auth = self.fixture()
        auth["media_delete_by"] = (datetime.now(UTC) + timedelta(days=2)).isoformat()
        path.write_text(json.dumps(auth))
        with self.assertRaises(DataContractError):
            load_inputs(path, self.root)
        auth["status"] = "draft"
        path.write_text(json.dumps(auth))
        with self.assertRaises(DataContractError):
            load_inputs(path, self.root)

    def test_review_groups_are_drafts_and_include_unassigned(self):
        cases = draft_cases({"B0": [
            {"assignments": [{"anchor_id": "a", "track_id": 1}]},
            {"assignments": [{"anchor_id": "b", "track_id": None}]},
            {"assignments": [{"anchor_id": "c", "track_id": 1}]}]})
        group = next(c for c in cases if c["kind"] == "draft_track_group")
        self.assertEqual(group["gaps"], [[0, 2]])
        self.assertEqual(group["identity_truth"], "unreviewed")
        self.assertTrue(any(c["kind"] == "unassigned" for c in cases))


if __name__ == "__main__":
    unittest.main()
