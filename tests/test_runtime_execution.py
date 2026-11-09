from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.inference.frame_processor import FrameProcessor
from ai_exam_monitoring.inference.person import PersonDetection
from ai_exam_monitoring.inference.profiling import StageProfiler
from ai_exam_monitoring.inference.video import VideoFrame

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import torch

    from ai_exam_monitoring.inference.classifier import BundleClassifier
    from ai_exam_monitoring.inference.execution import ExecutionSettings, verify_execution_packages
    from ai_exam_monitoring.inference.execution_processor import create_execution_processor


class FixtureDetector:
    def predict(self, image):
        return [PersonDetection((i, 0, i + 1, 2), .8) for i in range(image.width)]


class FixtureClassifier:
    thresholds = [.5, .4]

    def __init__(self):
        self.chunks = []

    def preview(self, image):
        return image

    def predict(self, image):
        return [image.getpixel((0, 0))[0] / 255, .45]

    def predict_batch(self, images):
        self.chunks.append(len(images))
        return [self.predict(image) for image in images]


class FrameBatchTests(unittest.TestCase):
    def test_frame_and_live_primitives_import_without_ml_dependencies(self):
        code = textwrap.dedent("""
            import importlib.abc
            import sys

            class BlockML(importlib.abc.MetaPathFinder):
                def find_spec(self, fullname, path=None, target=None):
                    if fullname.split('.')[0] in {'torch', 'torchvision', 'ultralytics', 'cv2'}:
                        raise ModuleNotFoundError(f'Optional dependency imported: {fullname}')

            sys.meta_path.insert(0, BlockML())
            import ai_exam_monitoring.inference.frame_processor
            import ai_exam_monitoring.inference.live_events
            import ai_exam_monitoring.inference.live_timing
        """)
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                                check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def processor(self, batch, classifier=None, profiler=None):
        return FrameProcessor(FixtureDetector(), classifier or FixtureClassifier(),
                              dict(left=0, right=0, top=0, bottom=0),
                              batch_size=batch, profiler=profiler)

    def frame(self, count=14):
        image = Image.new("RGB", (count, 2))
        for x in range(count):
            image.putpixel((x, 0), (x * 17, 0, 0))
        return VideoFrame(9, 1234., image)

    def test_chunk_tail_order_scores_geometry_and_sink_match_scalar(self):
        frame = self.frame()
        expected = self.processor(1).process(frame)
        for batch in (2, 4, 8, 14):
            with self.subTest(batch=batch):
                classifier = FixtureClassifier()
                seen = []
                actual = self.processor(batch, classifier).process(
                    frame, lambda obs, crop, seen=seen: seen.append((obs["anchor_id"], crop.size)))
                self.assertEqual(actual, expected)
                self.assertEqual(len(seen), 14)
                self.assertEqual(sum(classifier.chunks), 14)
                self.assertLessEqual(max(classifier.chunks), batch)

    def test_empty_detections_do_not_call_classifier(self):
        classifier = FixtureClassifier()
        processor = self.processor(4, classifier)
        with patch.object(processor.detector, "predict", return_value=[]):
            self.assertEqual(processor.process(self.frame())["observations"], [])
        self.assertEqual(classifier.chunks, [])

    def test_bad_batch_output_and_oom_propagate_without_scalar_retry(self):
        for bad in ([], [[float("nan"), .5]] * 4, [[.5]] * 4, [[2., .5]] * 4):
            classifier = FixtureClassifier()
            with patch.object(classifier, "predict_batch", return_value=bad), \
                    patch.object(classifier, "predict") as scalar:
                with self.assertRaises(DataContractError):
                    self.processor(4, classifier).process(self.frame())
                scalar.assert_not_called()
        classifier = FixtureClassifier()
        with patch.object(classifier, "predict_batch", side_effect=RuntimeError("OOM")), \
                patch.object(classifier, "predict") as scalar:
            with self.assertRaisesRegex(RuntimeError, "OOM"):
                self.processor(4, classifier).process(self.frame())
            scalar.assert_not_called()

    def test_invalid_batch_and_missing_capability_fail_at_construction(self):
        for batch in (True, 0, -1, 101, 1.5):
            with self.assertRaises(DataContractError):
                self.processor(batch)
        with self.assertRaises(DataContractError):
            self.processor(2, SimpleNamespace(thresholds=[.5, .4]))

    def test_profiling_does_not_change_observations(self):
        profiler = StageProfiler(3, synchronize=lambda: None)
        self.assertEqual(self.processor(4).process(self.frame()),
                         self.processor(4, profiler=profiler).process(self.frame()))
        rows = profiler.snapshot()["stages"]
        self.assertEqual(rows["classify"]["completed"], 4)
        self.assertEqual(rows["classify"]["window_count"], 3)
        self.assertEqual(rows["frame"]["completed"], 1)


class ProfilingTests(unittest.TestCase):
    def test_sync_brackets_work_and_rolling_percentiles_are_labelled(self):
        events = []
        ticks = iter([0, 1_000_000, 10_000_000, 13_000_000, 20_000_000, 25_000_000])
        profiler = StageProfiler(2, synchronize=lambda: events.append("sync"),
                                 clock=lambda: next(ticks))
        for _ in range(3):
            with profiler.measure("classify"):
                events.append("work")
        self.assertEqual(events, ["sync", "work", "sync"] * 3)
        row = profiler.snapshot()["stages"]["classify"]
        self.assertEqual(row, dict(completed=3, failed=0, mean_ms=3., max_ms=5.,
                                  window_count=2, window_p50_ms=3., window_p95_ms=5.))

    def test_failure_is_not_successful_latency_and_unbounded_stage_keys_rejected(self):
        profiler = StageProfiler(2, synchronize=lambda: None)
        with self.assertRaisesRegex(RuntimeError, "failure"), profiler.measure("detect"):
            raise RuntimeError("failure")
        row = profiler.snapshot()["stages"]["detect"]
        self.assertEqual(row["failed"], 1)
        self.assertEqual(row["completed"], 0)
        self.assertIsNone(row["mean_ms"])
        with self.assertRaises(DataContractError), profiler.measure("random-frame-id"):
            pass
        with self.assertRaises(DataContractError):
            StageProfiler(0, synchronize=lambda: None)


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class ExecutionTests(unittest.TestCase):
    def classifier(self, batch):
        class TinyModel(torch.nn.Module):
            def forward(self, value):
                return value.mean(dim=(2, 3))[:, :2]

        classifier = BundleClassifier.__new__(BundleClassifier)
        classifier.target_order = ["phone_use", "looking_around"]
        classifier.execution = ExecutionSettings("cpu", batch)
        classifier.device = classifier.execution.resolve()
        classifier.threads = torch.get_num_threads()
        classifier.model = TinyModel().eval()
        classifier.config = SimpleNamespace(image_size=14, fill=[124, 116, 104],
                                            mean=[.485, .456, .406], std=[.229, .224, .225])
        return classifier

    def test_real_tensor_batch_matches_scalar_and_preserves_model(self):
        classifier = self.classifier(4)
        images = [Image.new("RGB", size, color) for size, color in (
            ((17, 31), (240, 17, 99)), ((31, 7), (0, 60, 30)), ((14, 14), (125, 55, 222)))]
        expected = [classifier.predict(image) for image in images]
        actual = classifier.predict_batch(images)
        torch.testing.assert_close(torch.tensor(actual), torch.tensor(expected), rtol=0, atol=1e-7)
        self.assertFalse(classifier.model.training)
        self.assertEqual(classifier.predict_batch([]), [])
        with self.assertRaises(DataContractError):
            classifier.predict_batch(images * 2)

    def test_real_tensor_shape_nan_and_no_grad(self):
        classifier = self.classifier(4)
        image = Image.new("RGB", (14, 14))
        for result in (torch.zeros(2, 2), torch.full((1, 2), float("nan"))):
            with patch.object(classifier.model, "forward", return_value=result):
                with self.assertRaises(DataContractError):
                    classifier.predict_batch([image])
        def forward(value):
            self.assertFalse(torch.is_grad_enabled())
            self.assertEqual(value.dtype, torch.float32)
            return value.mean(dim=(2, 3))[:, :2]
        with patch.object(classifier.model, "forward", side_effect=forward):
            classifier.predict_batch([image])

    def test_cuda_missing_or_bad_index_fails_before_checkpoint_access(self):
        for device, count in (("cuda:0", 0), ("cuda:2", 1)):
            with patch("torch.cuda.is_available", return_value=count > 0), \
                    patch("torch.cuda.device_count", return_value=count):
                with self.assertRaises(DataContractError):
                    BundleClassifier(None, execution=ExecutionSettings(device, 4))
        for device in ("auto", "cuda", "mps", "cuda:-1", "cuda:01"):
            with self.assertRaises(DataContractError):
                ExecutionSettings(device, 1)

    def test_cuda_fp32_flags_restore_on_failure_and_sync_uses_explicit_device(self):
        settings = ExecutionSettings("cuda:1", 4)
        before = (torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32,
                  torch.backends.cudnn.benchmark)
        with patch.object(ExecutionSettings, "resolve", return_value=torch.device("cuda:1")), \
                patch("torch.cuda.synchronize") as synchronize:
            with self.assertRaisesRegex(RuntimeError, "OOM"), settings.precision():
                self.assertFalse(torch.backends.cuda.matmul.allow_tf32)
                self.assertFalse(torch.backends.cudnn.allow_tf32)
                self.assertFalse(torch.backends.cudnn.benchmark)
                raise RuntimeError("OOM")
            settings.synchronize()
            synchronize.assert_called_once_with(torch.device("cuda:1"))
        self.assertEqual(before, (torch.backends.cuda.matmul.allow_tf32,
                                 torch.backends.cudnn.allow_tf32, torch.backends.cudnn.benchmark))

    def test_exact_package_manifest_allows_only_torch_build_variant(self):
        parent = {"torch": "2.8.0+cpu", "torchvision": "0.23.0+cpu", "ultralytics": "8.3.221"}
        expected = {**parent, "torch": "2.8.0+cu128", "torchvision": "0.23.0+cu128"}
        settings = ExecutionSettings("cuda:0", 4)
        with patch("ai_exam_monitoring.inference.execution.version", side_effect=expected.get), \
                patch.object(ExecutionSettings, "resolve", return_value=torch.device("cuda:0")):
            verify_execution_packages(parent, expected, settings)
            for bad in ({**expected, "torch": "2.9.0+cu128"},
                        {**expected, "ultralytics": "9.0"}, {"torch": "2.8.0+cu128"}, parent):
                with self.assertRaises(DataContractError):
                    verify_execution_packages(parent, bad, settings)
        self.assertEqual(parent["torch"], "2.8.0+cpu")

    def test_factory_rejects_environment_before_model_allocation(self):
        with tempfile.TemporaryDirectory() as folder:
            receipt = Path(folder) / "receipt.json"
            receipt.write_text(json.dumps({"packages": {"torch": "2.8.0+cpu"}}))
            runtime = SimpleNamespace(raw={"schema_version": "recorded-runtime-config-v4"},
                                      pin=lambda _: receipt)
            with patch("ai_exam_monitoring.inference.execution_processor.BundleClassifier") as load:
                with self.assertRaises(DataContractError):
                    create_execution_processor(runtime, ExecutionSettings("cpu", 4), {})
                load.assert_not_called()

    def test_e009_factory_uses_same_execution_and_package_guards(self):
        settings = ExecutionSettings("cpu", 4)
        with tempfile.TemporaryDirectory() as folder:
            receipt = Path(folder) / "receipt.json"
            receipt.write_text(json.dumps({"packages": {"torch": "2.8.0+cpu"}}))
            runtime = SimpleNamespace(
                raw={"schema_version": "recorded-runtime-config-v5",
                     "crop": dict(left=0, right=0, top=0, bottom=0)}, pin=lambda _: receipt)
            with patch("ai_exam_monitoring.inference.execution_processor.verify_execution_packages"
                       ) as verify, patch(
                "ai_exam_monitoring.inference.execution_processor.BundleClassifier",
                return_value=FixtureClassifier(),
            ) as classifier, patch(
                "ai_exam_monitoring.inference.execution_processor.PersonDetector",
                return_value=FixtureDetector(),
            ) as detector:
                processor = create_execution_processor(runtime, settings, {"exact": "manifest"})
                verify.assert_called_once_with({"torch": "2.8.0+cpu"},
                                               {"exact": "manifest"}, settings)
                classifier.assert_called_once_with(runtime, execution=settings)
                detector.assert_called_once_with(runtime, execution=settings,
                                                 packages={"exact": "manifest"})
                self.assertEqual(processor.batch_size, 4)
