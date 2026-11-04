from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import torch
    import yaml

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.classifier import BundleClassifier
    from ai_exam_monitoring.inference.person import PersonDetection, crop_boxes
    from ai_exam_monitoring.inference.runtime import process_frames, run_video
    from ai_exam_monitoring.inference.runtime_config import (
        RuntimeConfig,
        load_runtime_config,
        media_deadline,
        verify_media,
    )
    from ai_exam_monitoring.inference.video import (
        RecordedVideo,
        VideoFrame,
        qa_indices,
        sample_indices,
        validate_time,
    )
    from ai_exam_monitoring.training.artifacts import digest_json
    from ai_exam_monitoring.training.data import image_tensor


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class RuntimeTests(unittest.TestCase):
    def test_classifier_restores_threads_changed_by_detector(self):
        classifier = BundleClassifier.__new__(BundleClassifier)
        classifier.threads = 4
        previous = torch.get_num_threads()
        try:
            torch.set_num_threads(2)
            # Stop before preprocessing/model execution: verify the shared-state guard.
            with patch.object(classifier, "preview", side_effect=RuntimeError("stop")):
                with self.assertRaisesRegex(RuntimeError, "stop"):
                    classifier.predict(Image.new("RGB", (8, 8)))
            self.assertEqual(torch.get_num_threads(), 4)
        finally:
            torch.set_num_threads(previous)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.margins = {"left": .2, "right": .2, "top": .1, "bottom": .2}
        self.config = RuntimeConfig({"crop": self.margins}, self.root)

    def test_geometry_rounding_clipping_and_context_contains_anchor(self):
        p, c = crop_boxes(PersonDetection((10.2, 20.8, 30.1, 60.2), .8),
                          (100, 100), self.margins)
        self.assertEqual(p, (10, 20, 31, 61))
        self.assertEqual(c, (5, 15, 36, 70))
        p, c = crop_boxes(PersonDetection((-2.1, -1.1, 101., 102.), .8),
                          (100, 100), self.margins)
        self.assertEqual(p, (0, 0, 100, 100))
        self.assertEqual(c, p)

    def test_invalid_detector_geometry_and_confidence(self):
        for box in [(3, 0, 2, 5), (100, 0, 120, 5), (0, 0, float("nan"), 5)]:
            with self.subTest(box=box), self.assertRaises(DataContractError):
                crop_boxes(PersonDetection(box, .8), (50, 50), self.margins)
        with self.assertRaises(DataContractError):
            crop_boxes(PersonDetection((0, 0, 3, 5), float("nan")), (50, 50), self.margins)

    def test_bad_timestamps_and_qa_sampling_in_time(self):
        for value, previous in [(float("nan"), None), (-1, None), (0, 0), (1, 2)]:
            with self.subTest(value=value), self.assertRaises(DataContractError):
                validate_time(value, previous)
        self.assertEqual(qa_indices([0., 1., 2., 50., 100.], 3), {0, 3, 4})
        self.assertEqual(qa_indices([0.], 20), {0})

    def test_two_hz_preserves_source_indices_and_timestamps(self):
        self.assertEqual(sample_indices([0., 33., 499., 500., 533., 1000.], 2), [0, 3, 5])
        self.assertEqual(sample_indices([0., 33., 499., 500., 999., 1000.], 1), [0, 5])
        self.assertEqual(sample_indices([0., 1600., 1700., 2000.], 2), [0, 1, 3])
        d, c = self.adapters()
        frames = [self.frames()[0], VideoFrame(15, 500., self.frames()[1].image)]
        process_frames(frames, d, c, self.config, self.root, {}, {0, 15},
                       expected_times=[0., 500.], expected_indices=[0, 15])
        rows = [json.loads(s) for s in (self.root / "predictions.jsonl").read_text().splitlines()]
        self.assertEqual(rows[2]["frame_index"], 15)
        self.assertEqual(rows[2]["video_time_ms"], 500.)
        self.assertTrue((self.root / "f00000015-source.png").exists())

    def adapters(self, scores=None):
        class FixtureDetector:
            def predict(inner, image):
                return ([] if image.getpixel((0, 0)) == (0, 0, 0)
                        else [PersonDetection((1., 1., 10., 12.), .9)])

        class FixtureClassifier:
            thresholds = [.5, .3914746344089508]

            def predict(inner, image):
                return scores if scores is not None else [.5, .39]

            def preview(inner, image):
                return image.resize((336, 336))

        return FixtureDetector(), FixtureClassifier()

    def frames(self):
        return [VideoFrame(0, 0., Image.new("RGB", (20, 20))),
                VideoFrame(1, 40., Image.new("RGB", (20, 20), "white"))]

    def test_empty_frame_target_order_thresholds_and_gallery(self):
        d, c = self.adapters()
        result = process_frames(self.frames(), d, c, self.config, self.root, {}, {0, 1})
        rows = [json.loads(s) for s in (self.root / "predictions.jsonl").read_text().splitlines()]
        self.assertEqual(rows[0]["target_order"], ["phone_use", "looking_around"])
        self.assertEqual(rows[1]["observations"], [])
        self.assertEqual(rows[2]["video_time_ms"], 40.)
        self.assertEqual(rows[2]["observations"][0]["above_threshold"], [True, False])
        self.assertEqual(result["frames"], 2)
        self.assertEqual(result["observations"], 1)
        self.assertTrue((self.root / "f00000001-a000-input.png").is_file())
        self.assertIn("Không detection", (self.root / "index.html").read_text(encoding="utf-8"))

    def test_failure_leaves_no_completed_outcome(self):
        d, c = self.adapters([.5, float("nan")])
        with self.assertRaises(DataContractError):
            process_frames(self.frames(), d, c, self.config, self.root, {}, {0, 1})
        rows = [json.loads(s) for s in (self.root / "predictions.jsonl").read_text().splitlines()]
        self.assertEqual(rows[-1]["status"], "failed")
        self.assertEqual(rows[-1]["failed_frame_index"], 1)
        self.assertNotIn('"completed"', (self.root / "predictions.jsonl").read_text())
        self.assertIn("FAILED", (self.root / "index.html").read_text(encoding="utf-8"))

    def test_sampled_failure_reports_source_frame_not_processed_count(self):
        d, c = self.adapters([.5, float("nan")])
        frames = [self.frames()[0], VideoFrame(30, 1000., self.frames()[1].image)]
        with self.assertRaises(DataContractError):
            process_frames(frames, d, c, self.config, self.root, {}, set(),
                           expected_times=[0., 1000.], expected_indices=[0, 30])
        rows = [json.loads(s) for s in (self.root / "predictions.jsonl").read_text().splitlines()]
        self.assertEqual(rows[-1]["completed_frames"], 1)
        self.assertEqual(rows[-1]["failed_frame_index"], 30)
        self.assertIn("frame 30", (self.root / "index.html").read_text(encoding="utf-8"))

    def test_iterator_failure_does_not_blame_previous_or_invent_source_frame(self):
        def broken_frames(after_first):
            if after_first:
                yield self.frames()[0]
            raise DataContractError("Synthetic decoder failure")

        for after_first in (False, True):
            output = self.root / str(after_first)
            output.mkdir()
            d, c = self.adapters()
            with self.assertRaises(DataContractError):
                process_frames(broken_frames(after_first), d, c, self.config, output, {}, set(),
                               expected_times=[0., 1000.], expected_indices=[0, 30])
            rows = [json.loads(s) for s in (output / "predictions.jsonl").read_text().splitlines()]
            self.assertEqual(rows[-1]["completed_frames"], int(after_first))
            self.assertIsNone(rows[-1]["failed_frame_index"])
            self.assertFalse((output / "failed-frame.png").exists())

    def test_incomplete_stream_does_not_mark_last_completed_frame_failed(self):
        d, c = self.adapters()
        with self.assertRaises(DataContractError):
            process_frames(self.frames()[:1], d, c, self.config, self.root, {}, set(),
                           expected_times=[0., 1000.], expected_indices=[0, 30])
        rows = [json.loads(s) for s in (self.root / "predictions.jsonl").read_text().splitlines()]
        self.assertEqual(rows[-1]["completed_frames"], 1)
        self.assertIsNone(rows[-1]["failed_frame_index"])
        self.assertFalse((self.root / "failed-frame.png").exists())

    def test_missing_frames_and_timestamp_changes_rejected(self):
        for frames, expected in [([self.frames()[1]], None), (self.frames(), [0., 41.])]:
            output = self.root / str(len(list(self.root.iterdir())))
            output.mkdir()
            d, c = self.adapters()
            with self.assertRaises(DataContractError):
                process_frames(frames, d, c, self.config, output, {}, set(),
                               expected_times=expected)

    def test_existing_output_rejected_before_input_or_model_access(self):
        with patch("ai_exam_monitoring.inference.runtime.load_runtime_config") as load:
            with self.assertRaises(DataContractError):
                run_video(Path("missing"), self.root, Path("missing.mp4"),
                          Path("missing"), self.root)
        load.assert_not_called()

    def test_session_failure_and_success_have_authoritative_final_outcome(self):
        from contextlib import ExitStack
        from types import SimpleNamespace

        source = self.root / "clip.mp4"
        source.write_bytes(b"synthetic fixture")
        approval = self.root / "rights.json"
        approval.write_text("{}")
        config = RuntimeConfig({"runtime_id": "fixture", "gallery_frames": 20,
                                "pins": {}, "crop": self.margins}, self.root)
        d, c = self.adapters()
        deadline = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        for fail in (False, True):
            output = self.root / "outputs" / str(fail)
            with ExitStack() as stack:
                prefix = "ai_exam_monitoring.inference.runtime."
                stack.enter_context(patch(prefix + "load_runtime_config", return_value=config))
                stack.enter_context(patch(prefix + "verify_media",
                                          return_value={"source_sha256": sha256_file(source),
                                                        "media_delete_by": deadline}))
                stack.enter_context(patch(prefix + "RecordedVideo", return_value=SimpleNamespace(
                    fps=25., frames=lambda: iter(self.frames()))))
                stack.enter_context(patch(prefix + "BundleClassifier", return_value=c))
                stack.enter_context(patch(prefix + "PersonDetector", return_value=d))
                stack.enter_context(patch(prefix + "environment", return_value={}))
                if fail:
                    stack.enter_context(patch(prefix + "PersonDetector", side_effect=RuntimeError))
                    with self.assertRaises(RuntimeError):
                        run_video(Path("unused"), self.root, source, approval, output)
                else:
                    run_video(Path("unused"), self.root, source, approval, output)
            session = json.loads((output / "session.json").read_text())
            rows = [json.loads(s) for s in
                    (output / "predictions.jsonl").read_text().splitlines()]
            self.assertEqual(session["status"], "failed" if fail else "completed")
            self.assertEqual(rows[-1]["status"], session["status"])
            self.assertEqual(session["media_delete_by"], deadline)
            self.assertTrue((output / "checksums.json").is_file())

    def test_preprocessing_matches_training_pixel_and_tensor_path(self):
        from types import SimpleNamespace

        from torchvision.transforms import functional as TF

        classifier = BundleClassifier.__new__(BundleClassifier)
        classifier.config = SimpleNamespace(image_size=336, fill=[124, 116, 104],
                                            mean=[.485, .456, .406], std=[.229, .224, .225])
        image = Image.new("RGB", (17, 31), (240, 17, 99))
        path = self.root / "synthetic.png"
        image.save(path)
        actual = TF.normalize(TF.to_tensor(classifier.preview(image)),
                              classifier.config.mean, classifier.config.std)
        self.assertTrue(torch.equal(actual, image_tensor(path, classifier.config)))
        self.assertEqual(classifier.preview(image).getpixel((0, 0)), (124, 116, 104))

    def test_media_receipt_hash_holdout_and_rights(self):
        source = self.root / "fixture.mp4"
        source.write_bytes(b"synthetic-test-only")
        config = RuntimeConfig({"runtime_id": "fixture"}, self.root)
        raw = {"schema_version": "runtime-media-approval-v1", "status": "approved",
               "runtime_id": "fixture", "use_scope": "local_prototype_qa",
               "source_sha256": sha256_file(source), "test_or_holdout": False,
               "rights_confirmed": True, "third_party_processing": False,
               "access": "repository_owner", "retention_days": 7,
               "decision_ref": "synthetic-test-fixture"}
        path = self.root / "receipt.json"
        path.write_text(json.dumps(raw))
        self.assertEqual(verify_media(source, path, config)["source_sha256"], raw["source_sha256"])
        for key, value in [("test_or_holdout", True), ("rights_confirmed", False),
                           ("source_sha256", "0" * 64), ("third_party_processing", True)]:
            path.write_text(json.dumps({**raw, key: value}))
            with self.subTest(key=key), self.assertRaises(ConfigurationError):
                verify_media(source, path, config)

    def test_absolute_deadline_invalid_expired_and_extension_rejected(self):
        now = datetime.now(UTC)
        for value in (None, "bad", now.replace(tzinfo=None).isoformat(),
                      (now - timedelta(seconds=1)).isoformat(),
                      (now + timedelta(days=8)).isoformat()):
            with self.subTest(value=value), self.assertRaises(ConfigurationError):
                media_deadline({"media_delete_by": value})
        with self.assertRaises(ConfigurationError):
            media_deadline({})
        deadline = (now + timedelta(days=1)).isoformat()
        self.assertEqual(media_deadline({"media_delete_by": deadline}).isoformat(), deadline)

    def test_v2_receipt_cannot_extend_pinned_parent_session(self):
        source = self.root / "clip.mp4"
        source.write_bytes(b"fixture")
        deadline = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        parent = self.root / "parent.json"
        parent.write_text(json.dumps({"source_sha256": sha256_file(source),
                                      "media_delete_by": deadline}))
        receipt = {"schema_version": "runtime-media-approval-v2", "status": "approved",
                   "runtime_id": "fixture", "use_scope": "local_prototype_qa",
                   "source_sha256": sha256_file(source), "test_or_holdout": False,
                   "rights_confirmed": True, "third_party_processing": False,
                   "access": "repository_owner", "retention_days": 7,
                   "decision_ref": "fixture", "media_delete_by": deadline,
                   "parent_session": {"path": parent.name, "sha256": sha256_file(parent)}}
        path = self.root / "rights.json"
        config = RuntimeConfig({"runtime_id": "fixture"}, self.root)
        path.write_text(json.dumps(receipt))
        verify_media(source, path, config)
        receipt["media_delete_by"] = (datetime.now(UTC) + timedelta(days=2)).isoformat()
        path.write_text(json.dumps(receipt))
        with self.assertRaises(ConfigurationError):
            verify_media(source, path, config)

    def test_expiry_during_frame_processing_stops_before_inference(self):
        d, c = self.adapters()
        with self.assertRaises(ConfigurationError):
            process_frames(self.frames(), d, c, self.config, self.root,
                           {"media_delete_by": "2000-01-01T00:00:00+00:00"}, set())
        rows = [json.loads(s) for s in (self.root / "predictions.jsonl").read_text().splitlines()]
        self.assertEqual(rows[-1]["status"], "failed")
        self.assertEqual(rows[-1]["completed_frames"], 0)
        self.assertFalse((self.root / "failed-frame.png").exists())

    def test_config_approval_and_pin_mutation_rejected(self):
        pins = {}
        for name in ("checkpoint", "resolved_config", "calibration", "bundle", "run",
                     "detector_weights", "detector_receipt"):
            path = self.root / name
            path.write_bytes(b"synthetic")
            pins[name] = {"path": name, "sha256": sha256_file(path)}
        raw = {"schema_version": "recorded-runtime-config-v1", "runtime_id": "fixture",
               "approval_ref": "approval.json", "pins": pins,
               "detector": {"imgsz": 640, "conf": .25, "iou": .7, "max_det": 100,
                            "device": "cpu", "half": False},
               "crop": {"version": "context-v1", **self.margins},
               "classifier": {"device": "cpu", "batch_size": 1, "threads": 4,
                              "precision": "float32",
                              "target_order": ["phone_use", "looking_around"]},
               "gallery_frames": 20}
        path = self.root / "config.yaml"
        path.write_text(yaml.safe_dump(raw))
        (self.root / "approval.json").write_text(json.dumps({"status": "approved",
                "runtime_id": "fixture", "config_sha256": digest_json(raw)}))
        load_runtime_config(path, self.root)
        for hz in (1, 2):
            v2 = {**raw, "schema_version": "recorded-runtime-config-v2", "sampling_hz": hz}
            path.write_text(yaml.safe_dump(v2))
            (self.root / "approval.json").write_text(json.dumps({"status": "approved",
                    "runtime_id": "fixture", "config_sha256": digest_json(v2)}))
            load_runtime_config(path, self.root)
        for bad_hz in (3, True):
            v2 = {**raw, "schema_version": "recorded-runtime-config-v2", "sampling_hz": bad_hz}
            path.write_text(yaml.safe_dump(v2))
            (self.root / "approval.json").write_text(json.dumps({"status": "approved",
                    "runtime_id": "fixture", "config_sha256": digest_json(v2)}))
            with self.subTest(bad_hz=bad_hz), self.assertRaises(ConfigurationError):
                load_runtime_config(path, self.root)
        selection_path = self.root / "selection.json"
        d2 = {**raw["detector"], "iou": .3}
        selection = {"status": "accepted", "winner": "D2", "detector": d2,
                     "detector_weights": pins["detector_weights"], "decision_ref": "fixture"}
        selection_path.write_text(json.dumps(selection))
        v3 = {**raw, "schema_version": "recorded-runtime-config-v3", "sampling_hz": 1,
              "detector": d2, "pins": {**pins, "detector_selection": {
                  "path": selection_path.name, "sha256": sha256_file(selection_path)}}}
        path.write_text(yaml.safe_dump(v3))
        (self.root / "approval.json").write_text(json.dumps({"status": "approved",
                "runtime_id": "fixture", "config_sha256": digest_json(v3)}))
        self.assertEqual(load_runtime_config(path, self.root).raw["detector"]["iou"], .3)
        selection_path.write_text(json.dumps({**selection, "winner": "D1"}))
        v3["pins"]["detector_selection"]["sha256"] = sha256_file(selection_path)
        path.write_text(yaml.safe_dump(v3))
        (self.root / "approval.json").write_text(json.dumps({"status": "approved",
                "runtime_id": "fixture", "config_sha256": digest_json(v3)}))
        with self.assertRaises(ConfigurationError):
            load_runtime_config(path, self.root)
        changed_v1 = {**raw, "detector": d2}
        path.write_text(yaml.safe_dump(changed_v1))
        (self.root / "approval.json").write_text(json.dumps({"status": "approved",
                "runtime_id": "fixture", "config_sha256": digest_json(changed_v1)}))
        with self.assertRaises(ConfigurationError):
            load_runtime_config(path, self.root)
        path.write_text(yaml.safe_dump(raw))
        (self.root / "approval.json").write_text(json.dumps({"status": "approved",
                "runtime_id": "fixture", "config_sha256": digest_json(raw)}))
        (self.root / "checkpoint").write_bytes(b"changed")
        with self.assertRaises(ConfigurationError):
            load_runtime_config(path, self.root)
        raw["gallery_frames"] = 19
        path.write_text(yaml.safe_dump(raw))
        with self.assertRaises(ConfigurationError):
            load_runtime_config(path, self.root)

    @unittest.skipUnless(importlib.util.find_spec("cv2"), "Install runtime dependencies")
    def test_real_decoder_rgb_timestamps_and_truncation(self):
        import cv2
        import numpy as np

        path = self.root / "synthetic.mp4"
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 25., (32, 32))
        self.assertTrue(writer.isOpened())
        try:
            for _ in range(3):
                frame = np.zeros((32, 32, 3), dtype=np.uint8)
                frame[:, :, 2] = 255
                writer.write(frame)
        finally:
            writer.release()
        video = RecordedVideo(path)
        frames = list(video.frames())
        self.assertEqual([f.index for f in frames], [0, 1, 2])
        self.assertAlmostEqual(frames[1].time_ms, 40.)
        self.assertGreater(frames[0].image.getpixel((0, 0))[0], 240)
        video.count += 1
        with self.assertRaises(DataContractError):
            list(video.frames())


if __name__ == "__main__":
    unittest.main()
