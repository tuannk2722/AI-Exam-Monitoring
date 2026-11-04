from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

AVAILABLE = importlib.util.find_spec("torch") is not None
if AVAILABLE:
    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.inference.person import PersonDetection
    from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
    from ai_exam_monitoring.inference.tracking_cadence import (
        cache_frames,
        endpoint_check,
        grid_stride,
        project_parent,
        run,
    )
    from ai_exam_monitoring.inference.video import VideoFrame


@unittest.skipUnless(AVAILABLE, "Install classifier dependencies")
class CadenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.auth = {"media_delete_by": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                     "source_sha256": "synthetic"}
        self.cfg = {"source_fps": 10, "cache_hz": 10, "source_frames": 10,
                    "expected_cache_samples": 10, "expected_parent_samples": 1,
                    "expected_new_forwards": 9, "review_windows_seconds": []}
        self.runtime = RuntimeConfig({"crop": {"left": .2, "right": .2,
                                              "top": .1, "bottom": .2}}, self.root)
        self.frames = [VideoFrame(i, i * 100., Image.new("RGB", (100, 100))) for i in range(10)]
        self.parents = [{"frame_index": 0, "video_time_ms": 0., "width": 100, "height": 100,
                         "observations": [{"anchor_id": "f00000000-a000",
                                           "person_box": [10, 10, 30, 60],
                                           "detector_confidence": .9, "scores": [.2, .6],
                                           "above_threshold": [False, True]}]}]

    def detector(self):
        return SimpleNamespace(predict=lambda im: [PersonDetection((10, 10, 30, 60), .9)])

    def test_cache_reuses_parent_and_never_fabricates_scores(self):
        original = copy.deepcopy(self.parents)
        rows, summary = cache_frames(self.frames, self.detector(), self.runtime, self.cfg,
                                     self.auth, self.parents, self.root)
        self.assertEqual(rows[0]["observations"], original[0]["observations"])
        self.assertEqual(self.parents, original)
        self.assertNotIn("scores", rows[1]["observations"][0])
        self.assertEqual(summary["new_detector_forwards"], 9)
        self.assertEqual(summary["new_classifier_forwards"], 0)
        self.assertEqual(rows[-1]["frame_index"], 9)

    def test_grid_is_source_time_not_sequential_tracker_id(self):
        self.assertEqual(grid_stride(30, 5), 6)
        self.assertEqual(grid_stride(30, 10), 3)
        with self.assertRaises(DataContractError):
            grid_stride(30, 7)

    def test_missing_decode_frame_rejected(self):
        with self.assertRaises(DataContractError):
            cache_frames(self.frames[1:], self.detector(), self.runtime, self.cfg,
                         self.auth, self.parents, self.root)

    def test_budget_cannot_silently_expand(self):
        self.cfg["expected_new_forwards"] = 2
        with self.assertRaises(DataContractError):
            cache_frames(self.frames, self.detector(), self.runtime, self.cfg,
                         self.auth, self.parents, self.root)
        rows = (self.root / "detections.jsonl").read_text().splitlines()
        self.assertEqual(len(rows), 3)

    def test_expired_media_prevents_detector_use(self):
        self.auth["media_delete_by"] = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
        with self.assertRaises(ConfigurationError):
            cache_frames(self.frames, self.detector(), self.runtime, self.cfg,
                         self.auth, self.parents, self.root)

    def test_projection_requires_exact_geometry_and_anchor(self):
        rows = [{"frame_index": 0, "video_time_ms": 0., "assignments": [
            {"anchor_id": "f00000000-a000", "person_box": [10, 10, 30, 60], "track_id": 7}]}]
        self.assertEqual(project_parent(rows, self.parents), rows)
        rows[0]["assignments"][0]["person_box"][0] = 11
        with self.assertRaises(DataContractError):
            project_parent(rows, self.parents)

    def test_null_endpoint_is_not_a_pass(self):
        rows = [{"frame_index": 240, "assignments": [{"anchor_id": "a", "track_id": None}]},
                {"frame_index": 270, "assignments": [{"anchor_id": "b", "track_id": 3}]}]
        case = {"frame_indices": [240, 270], "anchors": ["a", "b"]}
        result = endpoint_check(rows, case)
        self.assertFalse(result["distinct_assigned_ids"])
        self.assertTrue(result["visual_trace_required"])

    def test_detector_failure_records_failed_outcome(self):
        self.cfg["experiment_id"] = "synthetic"
        auth_path = self.root / "auth.json"
        auth_path.write_text("{}")
        source = self.root / "source.mp4"
        source.write_bytes(b"synthetic")
        video = SimpleNamespace(fps=10, count=10, frames=lambda: iter(self.frames))
        broken = SimpleNamespace(predict=lambda im: (_ for _ in ()).throw(RuntimeError("fixture")))
        prefix = "ai_exam_monitoring.inference.tracking_cadence."
        with patch(prefix + "load_experiment", return_value=(
                self.auth, self.cfg, self.runtime, self.parents, {})), \
                patch(prefix + "RecordedVideo", return_value=video), \
                patch(prefix + "PersonDetector", return_value=broken), \
                patch(prefix + "version", return_value="synthetic"), \
                patch(prefix + "environment", return_value={}), \
                patch(prefix + "code_identity", return_value={}):
            output = self.root / "outputs/failure"
            with self.assertRaises(RuntimeError):
                run(auth_path, self.root, source, output)
        self.assertEqual(json.loads((output / "session.json").read_text())["status"], "failed")
        self.assertEqual(json.loads((output / "detections/session.json").read_text())["status"],
                         "failed")


if __name__ == "__main__":
    unittest.main()
