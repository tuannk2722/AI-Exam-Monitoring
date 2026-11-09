"""Synthetic model metadata through runtime, playback and monitor rendering."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import tempfile
import time
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image
from test_web_monitor import AVAILABLE as WEB_AVAILABLE

from ai_exam_monitoring.data.pilot_schema import (
    MULTILABEL_ENCODING_VERSION,
    MULTILABEL_SEMANTICS_VERSION,
    MULTILABEL_TARGET_ORDER,
)

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import test_e009_runtime
    import test_online_video
    import torch

    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.classifier import BundleClassifier
    from ai_exam_monitoring.inference.execution import ExecutionSettings
    from ai_exam_monitoring.inference.frame_processor import FrameProcessor
    from ai_exam_monitoring.inference.online_video import OnlineResult
    from ai_exam_monitoring.inference.runtime import process_frames
    from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
    from ai_exam_monitoring.inference.streaming import FrameStamp
    from ai_exam_monitoring.inference.video import VideoFrame
    from ai_exam_monitoring.training.adaptation_config import FilePin
    from ai_exam_monitoring.training.adaptation_model import create_e005_initial_head


class FiveClassifier:
    target_order = MULTILABEL_TARGET_ORDER
    thresholds = [.5] * 5

    def predict(self, image):
        return [.8, .9, .9, .7, .1]

    def preview(self, image):
        return image


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class MultilabelRuntimeTests(unittest.TestCase):
    def test_processor_metadata_and_overlay_keep_all_independent_scores(self):
        classifier = FiveClassifier()
        detector = test_online_video.FixtureDetector()
        policy = {"left": .2, "right": .2, "top": .1, "bottom": .2}
        processor = FrameProcessor(detector, classifier, policy)
        frame = VideoFrame(0, 0., Image.new("RGB", (20, 20), "white"))
        row = processor.process(frame)
        self.assertEqual(row["observations"][0]["above_threshold"], [True] * 4 + [False])
        result = OnlineResult(FrameStamp("test", 0, 0, 0., 1, 20, 20), frame.image, row,
                              time.perf_counter_ns(), processor.target_order)
        self.assertEqual(result.annotated().size, frame.image.size)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            config = RuntimeConfig({"crop": policy}, root)
            process_frames([frame], detector, classifier, config, root, {}, {0})
            metadata = json.loads((root / "predictions.jsonl").read_text().splitlines()[0])
            self.assertEqual(metadata["target_order"], list(MULTILABEL_TARGET_ORDER))
            self.assertEqual(metadata["semantics_version"], MULTILABEL_SEMANTICS_VERSION)
            self.assertIn("standing_up", (root / "index.html").read_text(encoding="utf-8"))
        bad = FiveClassifier()
        bad.thresholds = [.5, .5]
        with self.assertRaises(DataContractError):
            FrameProcessor(detector, bad, policy)

    def test_five_output_bundle_prediction_batch_and_metadata_guards(self):
        helper = test_e009_runtime.E009RuntimeTests()
        helper.setUp()
        self.addCleanup(helper.doCleanups)
        root, config = helper.root, helper.config
        head = root / "five-head.pt"
        create_e005_initial_head(head, config.seed, in_dim=1536,
                                 hidden_dim=config.head_hidden_dim,
                                 dropout=config.head_dropout, target_order=MULTILABEL_TARGET_ORDER)
        data = replace(config.cohorts[0].data, encoding_version=MULTILABEL_ENCODING_VERSION)
        config = replace(config, cohorts=tuple(replace(c, data=data) for c in config.cohorts),
                          target_order=list(MULTILABEL_TARGET_ORDER), pos_weight=(1.,) * 5,
                          head_initialization=FilePin(head.name, sha256_file(head)))
        runtime = helper.runtime(config)
        raw = copy.deepcopy(runtime.raw)
        raw["classifier"].update(target_order=list(MULTILABEL_TARGET_ORDER),
                                 semantics_version=MULTILABEL_SEMANTICS_VERSION)
        for name in ("bundle", "calibration"):
            path = runtime.pin(name)
            value = json.loads(path.read_text())
            value.update(target_order=list(MULTILABEL_TARGET_ORDER),
                         semantics_version=MULTILABEL_SEMANTICS_VERSION)
            if name == "calibration":
                value["thresholds"] = [.1, .2, .3, .4, .5]
            path.write_text(json.dumps(value), encoding="utf-8")
            raw["pins"][name]["sha256"] = sha256_file(path)
        runtime = RuntimeConfig(raw, root)
        classifier = BundleClassifier(runtime, execution=ExecutionSettings("cpu", 2))
        image = Image.new("RGB", (31, 70), "white")
        scores = classifier.predict(image)
        batch = classifier.predict_batch([image, image])
        self.assertEqual(len(scores), 5)
        self.assertTrue(torch.allclose(torch.tensor(scores), torch.tensor(batch[0]), atol=1e-6))
        self.assertEqual(classifier.target_order, list(MULTILABEL_TARGET_ORDER))
        for field, value in (("target_order", ["phone_use", "looking_around"]),
                             ("semantics_version", "wrong")):
            altered = copy.deepcopy(raw)
            altered["classifier"][field] = value
            with self.assertRaises(DataContractError):
                BundleClassifier(RuntimeConfig(altered, root))


@unittest.skipUnless(WEB_AVAILABLE, "Install web and classifier dependencies")
class MultilabelMonitorTests(unittest.TestCase):
    def test_named_model_upload_and_snapshot_preserve_five_target_metadata(self):
        import yaml
        from fastapi.testclient import TestClient
        from test_web_monitor import monitor_models_fixture, synthetic_runner

        from ai_exam_monitoring.web.app import create_app

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runtimes, payload, receipt, path = monitor_models_fixture(root)
            raw = copy.deepcopy(runtimes["B0"].raw)
            raw["classifier"].update(model_id="FIVE", target_order=list(MULTILABEL_TARGET_ORDER),
                                     semantics_version=MULTILABEL_SEMANTICS_VERSION)
            runtime = RuntimeConfig(raw, root)
            calibration_path = runtime.pin("calibration")
            calibration_path.write_text(json.dumps({"thresholds": [.5] * 5}))
            raw["pins"]["calibration"]["sha256"] = sha256_file(calibration_path)
            config = yaml.safe_load(path.read_text())
            config.update(default_model="FIVE", models={
                "FIVE": {"label": "Synthetic five", "runtime": "FIVE.yaml"}})
            path.write_text(yaml.safe_dump(config))
            with (patch("ai_exam_monitoring.web.monitor.load_runtime_config", return_value=runtime),
                  patch("ai_exam_monitoring.web.monitor.RecordedVideo",
                        return_value=SimpleNamespace(count=5, fps=30.)),
                  patch("ai_exam_monitoring.web.monitor.create_online_video",
                        side_effect=synthetic_runner(runtime, classifier=FiveClassifier()))):
                app = create_app(root)
                with TestClient(app) as client:
                    response = client.post("/api/monitor/uploads", json={
                        "receipt": receipt, "size": len(payload)})
                    self.assertEqual(response.status_code, 201, response.text)
                    session = response.json()["session"]
                    identity = session["id"]
                    self.assertEqual(session["model_id"], "FIVE")
                    self.assertEqual(session["classifier"]["target_order"],
                                     list(MULTILABEL_TARGET_ORDER))
                    self.assertEqual(session["classifier"]["semantics_version"],
                                     MULTILABEL_SEMANTICS_VERSION)
                    self.assertEqual(client.put(f"/api/monitor/uploads/{identity}",
                                                content=payload).status_code, 200)
                    self.assertEqual(client.post(f"/api/monitor/sessions/{identity}/start")
                                     .status_code, 200)
                    deadline = time.monotonic() + 5
                    while app.state.monitor.state()["session"]["status"] != "completed":
                        self.assertLess(time.monotonic(), deadline)
                        time.sleep(.01)
                    state = client.get("/api/monitor/state").json()
                    observation = state["observations"]["observations"][0]
                    self.assertEqual(len(observation["scores"]), 5)
                    self.assertEqual(observation["above_threshold"], [True] * 4 + [False])


@unittest.skipUnless(os.environ.get("RUN_WEB_BROWSER_TESTS") == "1",
                     "Opt-in Playwright/Chrome")
class MultilabelMonitorBrowserTests(unittest.TestCase):
    def test_monitor_renders_labels_from_model_metadata(self):
        from playwright.sync_api import expect, sync_playwright

        assets = Path(__file__).parents[1] / "src/ai_exam_monitoring/web/assets"
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page()
            html = (assets / "monitor.html").read_text(encoding="utf-8").replace(
                '<script src="/assets/monitor.js" defer></script>', "")
            page.route("http://fixture.local/**", lambda route: route.fulfill(
                status=200, content_type="text/css" if route.request.url.endswith(".css")
                else "text/html", body=(assets / Path(route.request.url).name).read_text(
                    encoding="utf-8") if route.request.url.endswith(".css") else html))
            page.goto("http://fixture.local/")
            # Load the production script; all network state is synthetic in this fixture.
            page.route("**/api/monitor/**", lambda route: route.fulfill(
                status=200, content_type="application/json", body='{"session":null}'))
            page.add_script_tag(content=(assets / "monitor.js").read_text(encoding="utf-8"))
            page.wait_for_timeout(100)
            state = {"session": {"id": "synthetic", "status": "completed", "epoch": 0,
                                  "media_delete_by": "2099-01-01T00:00:00Z",
                                  "classifier": {"target_order": list(MULTILABEL_TARGET_ORDER)}},
                     "observations": {"frame_index": 1, "observations": [
                         {"above_threshold": [False, False, True, True, True]}]}}
            page.evaluate("value => render(value)", state)
            expect(page.locator("#observations")).to_contain_text("Gục/ngủ biểu kiến")
            expect(page.locator("#observations")).to_contain_text("Giơ tay")
            expect(page.locator("#observations")).to_contain_text("Đang đứng")
            state["session"]["classifier"]["target_order"] = ["phone_use", "looking_around"]
            state["observations"]["frame_index"] = 2
            state["observations"]["observations"][0]["above_threshold"] = [True, False]
            page.evaluate("value => render(value)", state)
            expect(page.locator("#observations")).to_contain_text("Dùng điện thoại")
            expect(page.locator("#observations")).not_to_contain_text("Giơ tay")
            state["observations"]["frame_index"] = 3
            state["observations"]["observations"][0]["above_threshold"] = [True] * 5
            page.evaluate("value => render(value)", state)
            expect(page.locator("#observations")).to_contain_text("không khớp metadata nhãn")
            browser.close()
