from __future__ import annotations

import importlib.util
import json
import tempfile
import threading
import time
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.frame_processor import FrameProcessor
    from ai_exam_monitoring.inference.online_video import OnlineVideoRunner, create_online_video
    from ai_exam_monitoring.inference.person import PersonDetection
    from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
    from ai_exam_monitoring.inference.video import FrameSampler, VideoFrame, sample_indices


class FixtureDetector:
    def predict(self, image):
        return [PersonDetection((1.2, 2.2, 8.5, 9.5), .8)]


class FixtureClassifier:
    thresholds = [.5, .4]

    def predict(self, image):
        return [.5, .39]

    def preview(self, image):
        raise AssertionError("Online processing must not produce QA previews")


def processor():
    return FrameProcessor(FixtureDetector(), FixtureClassifier(),
                          {"left": .2, "right": .2, "top": .1, "bottom": .2})


class FixtureSource:
    def __init__(self, times, after_first=None):
        self.times = times
        self.count = len(times)
        self.opens = self.closed = self.decoded = 0
        self.after_first = after_first

    def frames(self):
        self.opens += 1
        try:
            for i, stamp in enumerate(self.times):
                self.decoded += 1
                yield VideoFrame(i, stamp, Image.new("RGB", (20, 20), (i, 0, 0)))
                if i == 0 and self.after_first is not None:
                    if not self.after_first.wait(3):
                        raise RuntimeError("Test synchronization timeout")
        finally:
            self.closed += 1


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class OnlineVideoTests(unittest.TestCase):
    def wait_for(self, predicate):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if predicate():
                return
            threading.Event().wait(.002)
        self.fail("Timed out awaiting playback condition")

    def runner(self, source, factory=processor, **kwargs):
        runner = OnlineVideoRunner("fixture", source, factory, sampling_hz=1000,
                                   guard=kwargs.get("guard", lambda: None),
                                   verify_source=kwargs.get("verify_source", lambda: None))
        def cleanup():
            runner.stop()
            self.assertTrue(runner.join(4), "Worker leaked")
        self.addCleanup(cleanup)
        return runner

    def test_frame_geometry_scores_and_no_qa_io(self):
        image = Image.new("RGB", (20, 20), "white")
        frame = VideoFrame(30, 1000., image)
        p = processor()
        detected = p.detect(frame)
        row = p.classify(detected)
        self.assertIs(detected.frame.image, image)
        self.assertEqual(row, {
            "record_type": "frame", "frame_index": 30, "video_time_ms": 1000.,
            "width": 20, "height": 20, "observations": [{
                "anchor_id": "f00000030-a000", "person_box": (1, 2, 9, 10),
                "context_box": (0, 1, 11, 12), "detector_confidence": .8,
                "scores": [.5, .39], "above_threshold": [True, False],
            }],
        })
        self.assertEqual(p.process(frame), row)

    def test_incremental_sampling_preserves_pts_and_gaps(self):
        times = [33., 44., 1034., 2600., 2700., 3033.]
        sampler = FrameSampler(1)
        selected = [i for i, stamp in enumerate(times) if sampler.include(stamp)]
        self.assertEqual(selected, [0, 2, 3, 5])
        self.assertEqual(sample_indices(times, 1), selected)
        with self.assertRaises(DataContractError):
            sampler.include(3033.)

    def test_single_decode_pass_final_sample_and_exact_overlay(self):
        source = FixtureSource([0., 1., 2.])
        runner = self.runner(source)
        runner.start()
        runner.start()
        self.assertTrue(runner.join(3))
        state = runner.snapshot()
        self.assertEqual(state.status, "completed")
        self.assertEqual((source.opens, source.closed, source.decoded), (1, 1, 3))
        result = runner.take_result()
        self.assertIsNotNone(result)
        self.assertEqual(result.stamp.sequence, 2)
        self.assertEqual(result.observations["frame_index"], result.stamp.sequence)
        self.assertEqual(result.image.getpixel((0, 0)), (2, 0, 0))
        self.assertIsNot(result.annotated(), result.image)
        self.assertIsNone(runner.take_result())
        self.assertEqual(state.buffer.accepted, state.buffer.taken + state.buffer.dropped)

    def test_slow_ai_drops_pending_without_blocking_decode(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        source = FixtureSource([float(i) for i in range(15)], entered)
        p = processor()
        original = p.process
        def slow(frame):
            if frame.index == 0:
                entered.set()
                if not release.wait(3):
                    raise RuntimeError("Test barrier timeout")
            return original(frame)
        p.process = slow
        runner = self.runner(source, lambda: p)
        runner.start()
        self.wait_for(lambda: runner.snapshot().source_frame_index == 14)
        state = runner.snapshot()
        self.assertGreater(state.buffer.dropped, 0)
        self.assertTrue(state.buffer.pending)
        self.assertEqual(source.decoded, 15)
        release.set()
        self.assertTrue(runner.join(3))
        self.assertEqual(runner.take_result().stamp.sequence, 14)
        self.assertEqual(runner.snapshot().processed, 2)

    def test_seek_invalidates_inflight_result_and_restarts_exact_index(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        source = FixtureSource([0., 100., 200., 300.], entered)
        p = processor()
        original = p.process
        def slow(frame):
            if frame.index == 0:
                entered.set()
                if not release.wait(3):
                    raise RuntimeError("Test barrier timeout")
            return original(frame)
        p.process = slow
        runner = self.runner(source, lambda: p)
        runner.start()
        self.assertTrue(entered.wait(3))
        runner.seek(2)
        self.assertIsNone(runner.take_result())
        self.wait_for(lambda: runner.snapshot().source_frame_index == 2)
        release.set()
        self.assertTrue(runner.join(3))
        result = runner.take_result()
        self.assertEqual(result.stamp.epoch, 1)
        self.assertEqual(result.stamp.sequence, 3)
        self.assertEqual(result.stamp.source_time_ms, 300.)
        self.assertEqual(runner.snapshot().stale_results, 1)
        self.assertEqual((source.opens, source.closed), (2, 2))

    def test_pause_holds_clock_and_seek_stays_paused(self):
        source = FixtureSource([0., 150., 300.])
        runner = self.runner(source)
        runner.start()
        self.wait_for(lambda: runner.snapshot().source_frame_index == 0)
        runner.pause()
        runner.pause()
        before = runner.snapshot().buffer.accepted
        threading.Event().wait(.18)
        self.assertEqual(runner.snapshot().buffer.accepted, before)
        runner.seek(1)
        threading.Event().wait(.03)
        self.assertEqual(runner.snapshot().status, "paused")
        self.assertIsNone(runner.snapshot().source_frame_index)
        self.assertIsNone(runner.take_result())
        runner.resume()
        runner.resume()
        self.wait_for(lambda: runner.snapshot().source_frame_index == 1)
        self.assertEqual(runner.snapshot().source_time_ms, 150.)
        self.assertTrue(runner.join(3))

    def test_resume_preserves_remaining_media_delay(self):
        runner = self.runner(FixtureSource([0., 200.]))
        runner.start()
        self.wait_for(lambda: runner.snapshot().source_frame_index == 0)
        runner.pause()
        threading.Event().wait(.25)
        runner.resume()
        threading.Event().wait(.04)
        self.assertEqual(runner.snapshot().source_frame_index, 0)
        self.assertTrue(runner.join(3))

    def test_stop_during_model_startup_never_opens_decoder(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        def factory():
            entered.set()
            if not release.wait(3):
                raise RuntimeError("Test barrier timeout")
            return processor()
        source = FixtureSource([0.])
        runner = self.runner(source, factory)
        runner.start()
        self.assertTrue(entered.wait(3))
        runner.stop()
        release.set()
        self.assertTrue(runner.join(3))
        self.assertEqual(runner.snapshot().status, "stopped")
        self.assertEqual(source.opens, 0)

    def test_stop_interrupts_long_media_wait_and_releases_decoder(self):
        source = FixtureSource([0., 100000.])
        runner = self.runner(source)
        runner.start()
        self.wait_for(lambda: runner.snapshot().source_frame_index == 0)
        self.wait_for(lambda: runner.snapshot().processed == 1)
        self.assertEqual(runner.snapshot().status, "running")
        self.assertEqual(runner.take_result().stamp.sequence, 0)
        runner.stop()
        runner.stop()
        self.assertTrue(runner.join(1))
        self.assertEqual(runner.snapshot().status, "stopped")
        self.assertIsNone(runner.take_result())
        self.assertEqual(source.closed, 1)

    def test_stop_during_inference_never_publishes_late_result(self):
        entered, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        p = processor()
        def slow(frame):
            entered.set()
            if not release.wait(3):
                raise RuntimeError("Test barrier timeout")
            return {}
        p.process = slow
        source = FixtureSource([0.])
        runner = self.runner(source, lambda: p)
        runner.start()
        self.assertTrue(entered.wait(3))
        runner.stop()
        self.assertFalse(runner.join(.01))
        self.assertEqual(runner.snapshot().status, "stopping")
        release.set()
        self.assertTrue(runner.join(3))
        self.assertEqual(runner.snapshot().status, "stopped")
        self.assertIsNone(runner.take_result())

    def test_decode_inference_and_source_integrity_failures_clear_results(self):
        cases = ["decode", "inference", "integrity", "startup"]
        for case in cases:
            with self.subTest(case=case):
                source = FixtureSource([0., 1.])
                p = processor()
                def fail(*args):
                    raise DataContractError("private path must not appear in state")
                if case == "decode":
                    source.count = 3
                if case == "inference":
                    p.process = fail
                calls = []
                def verify(calls=calls, case=case):
                    calls.append(1)
                    if case == "integrity" and len(calls) == 2:
                        fail()
                runner = self.runner(source, fail if case == "startup" else lambda p=p: p,
                                     verify_source=verify)
                runner.start()
                self.assertTrue(runner.join(3))
                state = runner.snapshot()
                self.assertEqual(state.status, "failed")
                self.assertEqual(state.error_type, "DataContractError")
                self.assertIsNone(runner.take_result())
                self.assertEqual(source.opens, source.closed)

    def test_deadline_checked_while_paused_and_on_result_read(self):
        expired = threading.Event()
        def guard():
            if expired.is_set():
                raise DataContractError("expired")
        source = FixtureSource([0., 100000.])
        runner = self.runner(source, guard=guard)
        runner.start()
        self.wait_for(lambda: runner.snapshot().source_frame_index == 0)
        runner.pause()
        expired.set()
        self.assertTrue(runner.join(2))
        self.assertEqual(runner.snapshot().status, "failed")
        with self.assertRaises(DataContractError):
            runner.take_result()
        self.assertEqual(source.closed, 1)

    def test_invalid_commands_and_idle_stop_do_not_open_source(self):
        source = FixtureSource([0.])
        runner = self.runner(source)
        for action in (runner.pause, runner.resume, lambda: runner.seek(0)):
            with self.assertRaises(DataContractError):
                action()
        runner.stop()
        runner.start()
        self.assertEqual(runner.snapshot().status, "stopped")
        self.assertEqual(source.opens, 0)

    def test_factory_checks_rights_before_video_or_model_access(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "fixture.mp4"
            source.write_bytes(b"synthetic")
            with (patch("ai_exam_monitoring.inference.online_video.load_runtime_config"),
                  patch("ai_exam_monitoring.inference.online_video.verify_media",
                        side_effect=DataContractError("unauthorized")),
                  patch("ai_exam_monitoring.inference.online_video.RecordedVideo") as video):
                with self.assertRaises(DataContractError):
                    create_online_video(root / "config", root, source, root / "receipt",
                                        session_id="fixture")
                video.assert_not_called()

    def test_production_factory_with_real_synthetic_mp4_and_rights_guards(self):
        try:
            import cv2
            import numpy as np
            import torch  # noqa: F401
        except ImportError:
            self.skipTest("Install OpenCV and classifier dependencies")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "synthetic.mp4"
            writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"mp4v"), 20., (32, 32))
            if not writer.isOpened():
                self.skipTest("MP4 encoder unavailable")
            try:
                for i in range(5):
                    writer.write(np.full((32, 32, 3), i * 20, dtype=np.uint8))
            finally:
                writer.release()
            config = RuntimeConfig({"runtime_id": "fixture", "sampling_hz": 20,
                                    "crop": processor().crop_policy}, root)
            receipt = root / "rights.json"
            receipt.write_text(json.dumps({
                "schema_version": "runtime-media-approval-v1", "status": "approved",
                "runtime_id": "fixture", "use_scope": "local_prototype_qa",
                "source_sha256": sha256_file(source), "test_or_holdout": False,
                "rights_confirmed": True, "third_party_processing": False,
                "access": "repository_owner", "retention_days": 7,
                "decision_ref": "synthetic-test-only",
                "media_delete_by": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
            }), encoding="utf-8")
            with (patch("ai_exam_monitoring.inference.online_video.load_runtime_config",
                        return_value=config) as load,
                  patch("ai_exam_monitoring.inference.classifier.BundleClassifier",
                        return_value=FixtureClassifier()) as classifier,
                  patch("ai_exam_monitoring.inference.person.PersonDetector",
                        return_value=FixtureDetector())):
                runner = create_online_video(root / "config", root, source, receipt,
                                             session_id="synthetic")
                classifier.assert_not_called()
                try:
                    runner.start()
                    self.assertTrue(runner.join(3))
                    self.assertEqual(runner.snapshot().status, "completed")
                    self.assertEqual(load.call_count, 2)
                    result = runner.take_result()
                    self.assertEqual(result.stamp.sequence, 4)
                    self.assertAlmostEqual(result.stamp.source_time_ms, 200.)
                    self.assertGreaterEqual(result.finished_ns, result.stamp.captured_ns)
                    self.assertEqual(result.image.size, (32, 32))
                finally:
                    runner.stop()
                    self.assertTrue(runner.join(3))
                # Windows cannot remove an MP4 still held by VideoCapture.
                source.unlink()

    def test_offline_processor_parity_and_qa_regression(self):
        try:
            from ai_exam_monitoring.inference.runtime import process_frames
            from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
        except ImportError:
            self.skipTest("Install classifier dependencies")
        p = processor()
        frame = VideoFrame(0, 0., Image.new("RGB", (20, 20)))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = RuntimeConfig({"crop": p.crop_policy}, root)
            process_frames([frame], p.detector, p.classifier, config, root, {}, set())
            row = json.loads((root / "predictions.jsonl").read_text().splitlines()[1])
            self.assertEqual(row, json.loads(json.dumps(p.process(frame))))


if __name__ == "__main__":
    unittest.main()
