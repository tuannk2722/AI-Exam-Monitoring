from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision", "psutil"))
if ML_AVAILABLE:
    import yaml
    from test_runtime_execution import FixtureClassifier, FixtureDetector

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.execution import ExecutionSettings
    from ai_exam_monitoring.inference.frame_processor import FrameProcessor
    from ai_exam_monitoring.inference.profile_runtime import load_profile, profile_runtime
    from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
    from ai_exam_monitoring.inference.video import VideoFrame
    from ai_exam_monitoring.training.artifacts import digest_json


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "synthetic.mp4"
        self.source.write_bytes(b"synthetic-fixture-no-real-video")
        self.receipt = self.root / "rights.json"
        self.rights = dict(
            schema_version="runtime-media-approval-v2", status="approved", runtime_id="fixture",
            use_scope="local_prototype_qa", source_sha256=sha256_file(self.source),
            test_or_holdout=False, rights_confirmed=True, third_party_processing=False,
            access="repository_owner", retention_days=7, decision_ref="synthetic-fixture",
            media_delete_by=(datetime.now(UTC) + timedelta(days=1)).isoformat())
        self.receipt.write_text(json.dumps(self.rights))
        self.detector_receipt = self.root / "detector.json"
        self.detector_receipt.write_text(json.dumps({"packages": {}}))
        self.parent = self.root / "runtime.yaml"
        self.parent.write_text("synthetic-parent")
        self.runtime = RuntimeConfig(dict(
            schema_version="recorded-runtime-config-v4", runtime_id="fixture", sampling_hz=1,
            crop=dict(left=0, right=0, top=0, bottom=0),
            pins={"detector_receipt": {"path": "detector.json",
                                       "sha256": sha256_file(self.detector_receipt)}}), self.root)
        self.raw = dict(schema_version="runtime-execution-profile-v1", profile_id="fixture-profile",
                        runtime={"path": "runtime.yaml", "sha256": sha256_file(self.parent)},
                        device="cpu", batch_size=4, packages={}, warmup_samples=1,
                        measured_samples=2, timing_window=2, approval_ref="approval.json")
        self.config = self.root / "profile.yaml"
        self.output = self.root / "outputs/profile"
        self.approve()

    def approve(self):
        self.config.write_text(yaml.safe_dump(self.raw))
        (self.root / "approval.json").write_text(json.dumps(dict(
            status="approved", profile_id=self.raw["profile_id"],
            config_sha256=digest_json(self.raw), scope="local_runtime_compute_profile",
            decision_ref="synthetic-fixture")))

    def run_profile(self, count=3, processor=None, mutate=None):
        self.closed = False
        def frames():
            try:
                for i in range(count):
                    yield VideoFrame(i, i * 1000., Image.new("RGB", (14, 2)))
                    if mutate is not None:
                        mutate()
            finally:
                self.closed = True
        processor = processor or FrameProcessor(FixtureDetector(), FixtureClassifier(),
                                                 self.runtime.raw["crop"], batch_size=4)
        with patch("ai_exam_monitoring.inference.profile_runtime.load_runtime_config",
                   return_value=self.runtime), \
                patch("ai_exam_monitoring.inference.profile_runtime.verify_execution_packages"), \
                patch("ai_exam_monitoring.inference.profile_runtime.RecordedVideo",
                      return_value=SimpleNamespace(frames=frames)), \
                patch("ai_exam_monitoring.inference.profile_runtime.create_execution_processor",
                      return_value=processor), \
                patch("ai_exam_monitoring.inference.profile_runtime.probe", return_value={}), \
                patch("ai_exam_monitoring.inference.profile_runtime.code_identity",
                      return_value={}):
            return profile_runtime(self.config, self.root, self.source, self.receipt, self.output)

    def test_warmup_excluded_measurements_bounded_outputs_have_no_images_or_scores(self):
        result = self.run_profile()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["completed_samples"], 2)
        self.assertEqual(result["observations"], 28)
        self.assertEqual(result["warmup_completed"], 1)
        self.assertEqual(result["timing"]["stages"]["frame"]["completed"], 2)
        self.assertEqual(result["timing"]["stages"]["classify"]["completed"], 8)
        self.assertEqual(result["timing"]["stages"]["classify"]["window_count"], 2)
        self.assertIsNone(result["cuda_peak_allocated_bytes"])
        self.assertTrue(self.closed)
        rows = [json.loads(x) for x in (self.output / "samples.jsonl").read_text().splitlines()]
        self.assertEqual([r["frame_index"] for r in rows], [1, 2])
        self.assertEqual(set(rows[0]), {"frame_index", "source_time_ms", "observations"})
        for name, digest in json.loads((self.output / "checksums.json").read_text()).items():
            self.assertEqual(sha256_file(self.output / name), digest)

    def test_short_source_and_model_error_keep_failed_record_and_release_decoder(self):
        with self.assertRaises(DataContractError):
            self.run_profile(count=1)
        self.assertTrue(self.closed)
        self.assertEqual(json.loads((self.output / "profile.json").read_text())["status"], "failed")
        self.output = self.root / "outputs/second"
        processor = FrameProcessor(FixtureDetector(), FixtureClassifier(), self.runtime.raw["crop"])
        with patch.object(processor, "process", side_effect=RuntimeError("OOM")):
            with self.assertRaisesRegex(RuntimeError, "OOM"):
                self.run_profile(processor=processor)
        self.assertTrue(self.closed)
        self.assertEqual(json.loads((self.output / "profile.json").read_text())["error_type"],
                         "RuntimeError")

    def test_changed_source_is_failed_and_parent_and_receipt_are_immutable(self):
        original = [p.read_bytes() for p in (self.parent, self.receipt)]
        with self.assertRaises(DataContractError):
            self.run_profile(mutate=lambda: self.source.write_bytes(b"changed"))
        self.assertEqual(original, [p.read_bytes() for p in (self.parent, self.receipt)])
        self.assertTrue(self.closed)

    def test_lost_cuda_during_final_memory_read_does_not_hide_original_failure(self):
        import torch

        self.raw["device"] = "cuda:0"
        self.approve()
        processor = FrameProcessor(FixtureDetector(), FixtureClassifier(), self.runtime.raw["crop"])
        with patch.object(processor, "process", side_effect=RuntimeError("original OOM")), \
                patch.object(ExecutionSettings, "synchronize"), \
                patch.object(ExecutionSettings, "resolve", side_effect=[
                    torch.device("cuda:0"), DataContractError("device lost")]), \
                patch("torch.cuda.reset_peak_memory_stats"):
            with self.assertRaisesRegex(RuntimeError, "original OOM"):
                self.run_profile(processor=processor)
        result = json.loads((self.output / "profile.json").read_text())
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["cuda_memory_unavailable"])

    def test_expired_receipt_rejected_before_output_or_models(self):
        self.rights["media_delete_by"] = "2000-01-01T00:00:00+00:00"
        self.receipt.write_text(json.dumps(self.rights))
        with self.assertRaises(ConfigurationError):
            self.run_profile()
        self.assertFalse(self.output.exists())

    def test_profile_approval_mutation_and_parent_pin_are_checked(self):
        with patch("ai_exam_monitoring.inference.profile_runtime.load_runtime_config",
                   return_value=self.runtime):
            raw, runtime, settings = load_profile(self.config, self.root)
            self.assertEqual(settings, ExecutionSettings("cpu", 4))
            self.assertEqual(raw, self.raw)
            self.assertIs(runtime, self.runtime)
            self.raw["batch_size"] = 8
            self.config.write_text(yaml.safe_dump(self.raw))
            with self.assertRaises(ConfigurationError):
                load_profile(self.config, self.root)
            self.approve()
            self.parent.write_text("changed")
            with self.assertRaises(ConfigurationError):
                load_profile(self.config, self.root)

    def test_e009_profile_keeps_exact_parent_and_rejects_other_runtime_versions(self):
        for schema in ("recorded-runtime-config-v5", "recorded-runtime-config-v3"):
            runtime = RuntimeConfig({**self.runtime.raw, "schema_version": schema}, self.root)
            with self.subTest(schema=schema), patch(
                "ai_exam_monitoring.inference.profile_runtime.load_runtime_config",
                return_value=runtime,
            ):
                if schema.endswith("v5"):
                    _, selected, settings = load_profile(self.config, self.root)
                    self.assertIs(selected, runtime)
                    self.assertEqual(settings, ExecutionSettings("cpu", 4))
                else:
                    with self.assertRaises(ConfigurationError):
                        load_profile(self.config, self.root)

    def test_path_guard_and_existing_output_not_overwritten(self):
        self.output = self.root / "outside"
        with self.assertRaises(DataContractError):
            self.run_profile()
        self.output = self.root / "outputs/existing"
        self.output.mkdir(parents=True)
        protected = self.output / "keep.txt"
        protected.write_text("keep")
        with self.assertRaises(FileExistsError):
            self.run_profile()
        self.assertEqual(protected.read_text(), "keep")
