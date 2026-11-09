"""Synthetic upload/transport/lifecycle tests; production never injects fixture models."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import threading
import time
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image, ImageDraw

AVAILABLE = all(importlib.util.find_spec(p) for p in ("fastapi", "httpx", "torch", "torchvision"))
if AVAILABLE:
    import yaml
    from fastapi.testclient import TestClient

    from ai_exam_monitoring.common.errors import ConfigurationError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.frame_processor import FrameProcessor
    from ai_exam_monitoring.inference.online_video import OnlineVideoRunner
    from ai_exam_monitoring.inference.person import PersonDetection
    from ai_exam_monitoring.inference.runtime_config import RuntimeConfig, media_deadline
    from ai_exam_monitoring.inference.video import VideoFrame
    from ai_exam_monitoring.web.app import create_app
    from ai_exam_monitoring.web.monitor import Monitor


class SyntheticDetector:
    def predict(self, image):
        return [PersonDetection((80., 55., 280., 315.), .9)]


class SyntheticClassifier:
    thresholds = [.5, .4]

    def predict(self, image):
        return [.8, .2]

    def preview(self, image):
        raise AssertionError("No offline QA in monitor tests")


def monitor_fixture(root: Path):
    """Shared with opt-in browser test. Only temporary synthetic inputs."""
    config_dir = root / "configs/web/LIVE-VIDEO-WEB-20261028"
    config_dir.mkdir(parents=True, exist_ok=True)
    (root / "configs/web/review.yaml").write_text("output_root: outputs/web-review\n")
    config_path = config_dir / "monitor.yaml"
    config_path.write_text(yaml.safe_dump({
        "schema_version": "online-video-web-config-v1", "runtime": "runtime.yaml",
        "output_root": "outputs/monitor", "max_upload_bytes": 1048576,
        "max_receipt_bytes": 65536, "jpeg_quality": 85, "transport_interval_ms": 10,
    }))
    runtime = RuntimeConfig({"runtime_id": "synthetic", "sampling_hz": 1000,
                             "crop": {"left": .2, "right": .2, "top": .1, "bottom": .2}}, root)
    payload = b"synthetic transport fixture, no real media"
    receipt = {"schema_version": "runtime-media-approval-v1", "status": "approved",
               "runtime_id": "synthetic", "use_scope": "local_prototype_qa",
               "source_sha256": hashlib.sha256(payload).hexdigest(), "test_or_holdout": False,
               "rights_confirmed": True, "third_party_processing": False,
               "access": "repository_owner", "retention_days": 7,
               "decision_ref": "synthetic-test-only",
               "media_delete_by": (datetime.now(UTC) + timedelta(days=1)).isoformat()}
    return runtime, payload, receipt, config_path


def synthetic_runner(runtime, count=5, interval=30., classifier=None):
    def factory(config, root, source, receipt, *, session_id):
        rights = json.loads(receipt.read_text(encoding="utf-8"))
        class Source:
            def __init__(self):
                self.count = count
            def frames(self):
                for index in range(count):
                    image = Image.new("RGB", (640, 360), (20 + (index % 8) * 25, 60, 90))
                    draw = ImageDraw.Draw(image)
                    draw.rectangle((60, 220, 580, 340), fill="#496477")
                    draw.rectangle((110, 80, 240, 230), fill="#809bad")
                    draw.text((320, 30), f"SYNTHETIC TEST - frame {index}", fill="white")
                    yield VideoFrame(index, index * interval, image)
        return OnlineVideoRunner(
            session_id, Source(),
            lambda: FrameProcessor(SyntheticDetector(), classifier or SyntheticClassifier(),
                                   runtime.raw["crop"]),
            sampling_hz=1000, guard=lambda: media_deadline(rights), verify_source=lambda: None,
        )
    return factory


def monitor_models_fixture(root: Path):
    runtime, payload, receipt, config_path = monitor_fixture(root)
    config = yaml.safe_load(config_path.read_text())
    config.pop("runtime")
    config.update(schema_version="online-video-web-config-v2", default_model="B0",
                  models={key: {"label": key, "runtime": f"{key}.yaml"}
                          for key in ("B0", "B448")})
    config_path.write_text(yaml.safe_dump(config))
    runtimes = {}
    for key, size in (("B0", 336), ("B448", 448)):
        pins = {}
        for name, value in {
            "resolved_config": dict(transform="rgb_letterbox_bilinear_v1", image_size=size,
                                    mean=[.485, .456, .406], std=[.229, .224, .225],
                                    fill=[124, 116, 104]),
            "calibration": dict(thresholds=[.207, .451] if key == "B0" else [.358, .5]),
            "checkpoint": {},
        }.items():
            path = root / f"{key}-{name}.json"
            path.write_text(json.dumps(value))
            pins[name] = {"path": path.name, "sha256": sha256_file(path)}
        raw = copy.deepcopy(runtime.raw)
        raw.update(schema_version="recorded-runtime-config-v5", pins=pins,
                   classifier=dict(model_id=key, experiment_id=f"fixture-{key}",
                                   target_order=["phone_use", "looking_around"]))
        runtimes[key] = RuntimeConfig(raw, root)
    return runtimes, payload, receipt, config_path


@unittest.skipUnless(AVAILABLE, "Install web and classifier dependencies")
class WebMonitorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runtime, self.payload, self.receipt, self.config_path = monitor_fixture(self.root)
        for name, kwargs in (
            ("load_runtime_config", {"return_value": self.runtime}),
            ("RecordedVideo", {"return_value": SimpleNamespace(count=5, fps=1000 / 30)}),
            ("create_online_video", {"side_effect": synthetic_runner(self.runtime)}),
        ):
            patcher = patch(f"ai_exam_monitoring.web.monitor.{name}", **kwargs)
            mock = patcher.start()
            self.addCleanup(patcher.stop)
            if name == "create_online_video":
                self.factory = mock
        self.app = create_app(self.root)
        self.monitor = self.app.state.monitor
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def create(self, receipt=None, size=None):
        response = self.client.post("/api/monitor/uploads", json={
            "receipt": receipt if receipt is not None else self.receipt,
            "size": len(self.payload) if size is None else size,
        })
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["session"]["id"]

    def ready(self):
        identity = self.create()
        response = self.client.put(f"/api/monitor/uploads/{identity}", content=self.payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["session"]["status"], "ready")
        return identity

    def wait_for(self, predicate):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            if predicate():
                return
            threading.Event().wait(.005)
        self.fail("Timed out waiting for synthetic session")

    def command(self, identity, action, **extra):
        state = self.monitor.state()["session"]
        body = {"action": action, "command_id": state["command_id"] + 1,
                "epoch": state["epoch"], **extra}
        return self.client.post(f"/api/monitor/sessions/{identity}/command", json=body), body

    def test_upload_start_completion_snapshot_reconnect_and_jpeg(self):
        identity = self.ready()
        self.factory.assert_not_called()
        response = self.client.post(f"/api/monitor/sessions/{identity}/start")
        self.assertEqual(response.status_code, 200)
        self.wait_for(lambda: self.monitor.state()["session"]["status"] == "completed")
        self.monitor.worker.join(2)
        state = self.monitor.state()
        self.assertEqual(state["observations"]["frame_index"], 4)
        self.assertEqual(state["observations"]["observations"][0]["above_threshold"], [True, False])
        self.assertGreaterEqual(state["result_age_ms"], 0)
        stream = self.client.get(f"/api/monitor/sessions/{identity}/preview?epoch=0")
        self.assertEqual(stream.status_code, 200)
        self.assertIn(b"Content-Type: image/jpeg", stream.content)
        self.assertIn(b"\xff\xd8", stream.content)
        for cursor in (None, "obsolete:900"):
            response = self.client.get(f"/api/monitor/sessions/{identity}/events",
                                       headers={"Last-Event-ID": cursor} if cursor else {})
            self.assertIn("event: snapshot", response.text)
            self.assertIn('"status": "completed"', response.text)
        self.factory.assert_called_once()
        self.assertNotIn("source.part", [p.name for p in self.monitor.path(identity).iterdir()])
        self.assertFalse((self.monitor.path(identity) / "predictions.jsonl").exists())

    def test_eof_between_result_take_and_state_snapshot_drains_final_result(self):
        from ai_exam_monitoring.inference.online_video import OnlineResult
        from ai_exam_monitoring.inference.streaming import FrameStamp

        identity = self.ready()
        results = iter([
            OnlineResult(FrameStamp(identity, 0, index, index * 30., index + 1, 32, 32),
                         Image.new("RGB", (32, 32)),
                         {"frame_index": index, "observations": []}, index + 2)
            for index in (3, 4)
        ])
        def state(status):
            return SimpleNamespace(status=status, epoch=0, source_frame_index=4,
                                   source_time_ms=120., processed=5, stale_results=0,
                                   error_type=None, buffer=SimpleNamespace(dropped=0))
        snapshots = iter([state("running"), state("completed"),
                          state("completed"), state("completed")])
        self.monitor.runner = SimpleNamespace(snapshot=lambda: next(snapshots),
                                              take_result=lambda: next(results),
                                              join=lambda: True, stop=lambda: None)
        self.monitor._pump()
        self.assertEqual(self.monitor.record["status"], "completed")
        self.assertEqual(self.monitor.latest["frame_index"], 4)
        self.assertEqual(self.monitor.preview.snapshot().stamp.sequence, 4)

    def test_wrong_hash_incomplete_and_oversize_upload_leave_no_payload(self):
        for payload in (b"x" * len(self.payload), self.payload + b"extra", self.payload[:-1]):
            with self.subTest(payload=payload):
                identity = self.create()
                response = self.client.put(f"/api/monitor/uploads/{identity}", content=payload)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.monitor.state()["session"]["status"], "failed")
                self.assertFalse((self.monitor.path(identity) / "source.part").exists())
                self.assertFalse((self.monitor.path(identity) / "source.mp4").exists())
        self.factory.assert_not_called()

    def test_double_upload_and_expiry_mid_body_do_not_leave_open_payload(self):
        identity = self.create()
        handle = self.monitor.begin_upload(identity)
        try:
            self.monitor.write_chunk(identity, handle, self.payload[:4])
            response = self.client.put(f"/api/monitor/uploads/{identity}", content=self.payload)
            self.assertEqual(response.status_code, 409)
            self.monitor.record["media_delete_by"] = "2000-01-01T00:00:00+00:00"
            with self.assertRaises(ConfigurationError):
                self.monitor.write_chunk(identity, handle, self.payload[4:])
        finally:
            handle.close()
            self.monitor.abort_upload(identity, "SyntheticExpired")
        self.assertFalse((self.monitor.path(identity) / "source.part").exists())
        self.assertFalse(self.monitor.writing)

    def test_codec_error_cleans_renamed_payload(self):
        identity = self.create()
        with patch("ai_exam_monitoring.web.monitor.RecordedVideo", side_effect=ValueError("codec")):
            response = self.client.put(f"/api/monitor/uploads/{identity}", content=self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertFalse((self.monitor.path(identity) / "source.mp4").exists())
        self.assertEqual(self.monitor.state()["session"]["status"], "failed")

    def test_rights_limits_and_foreign_origin_rejected_before_payload(self):
        for key, value in (("rights_confirmed", False), ("test_or_holdout", True),
                           ("media_delete_by", "2000-01-01T00:00:00+00:00")):
            receipt = {**self.receipt, key: value}
            response = self.client.post("/api/monitor/uploads",
                                        json={"receipt": receipt, "size": 3})
            self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/monitor/uploads",
                                    json={"receipt": self.receipt, "size": 2**30})
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/monitor/uploads", content=b"x" * 70000)
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/monitor/uploads", json={}, headers={"Origin": "https://other.invalid"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(list(self.monitor.directory.iterdir()), [])

    def test_one_session_and_offline_online_exclusion(self):
        identity = self.create()
        self.assertEqual(self.client.post("/api/monitor/uploads", json={
            "receipt": self.receipt, "size": len(self.payload)}).status_code, 409)
        response = self.client.post("/api/jobs", json={"source": "unused", "receipt": "unused"})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.client.delete(f"/api/monitor/sessions/{identity}").status_code, 204)
        self.app.state.jobs.active["fixture"] = {"status": "running"}
        self.assertEqual(self.client.post("/api/monitor/uploads", json={
            "receipt": self.receipt, "size": len(self.payload)}).status_code, 409)

    def test_pause_seek_idempotency_stop_and_delete(self):
        self.factory.side_effect = synthetic_runner(self.runtime, count=10, interval=500.)
        identity = self.ready()
        self.client.post(f"/api/monitor/sessions/{identity}/start")
        self.wait_for(lambda: self.monitor.state()["session"]["status"] == "running")
        response, _ = self.command(identity, "pause")
        self.assertEqual(response.json()["session"]["status"], "paused")
        response, body = self.command(identity, "seek", frame_index=2)
        self.assertEqual(response.json()["session"]["epoch"], 1)
        again = self.client.post(f"/api/monitor/sessions/{identity}/command", json=body)
        self.assertEqual(again.json()["session"]["epoch"], 1)
        wrong = {**body, "frame_index": 3}
        response = self.client.post(f"/api/monitor/sessions/{identity}/command", json=wrong)
        self.assertEqual(response.status_code, 409)
        response = self.client.get(f"/api/monitor/sessions/{identity}/preview?epoch=0")
        self.assertEqual(response.status_code, 409)
        self.assertIsNone(self.monitor.preview.snapshot().jpeg)
        self.assertIsNone(self.monitor.state()["observations"])
        response, _ = self.command(identity, "stop")
        self.assertEqual(response.status_code, 200)
        self.monitor.worker.join(3)
        self.assertEqual(self.monitor.state()["session"]["status"], "stopped")
        self.assertTrue(self.monitor.preview.snapshot().closed)
        self.assertEqual(self.client.delete(f"/api/monitor/sessions/{identity}").status_code, 204)
        self.assertFalse(self.monitor.path(identity).exists())

    def test_expiry_disables_media_and_cleans_finished_upload(self):
        identity = self.ready()
        self.monitor.record["media_delete_by"] = "2000-01-01T00:00:00+00:00"
        state = self.client.get("/api/monitor/state").json()
        self.assertEqual(state["session"]["error_type"], "MediaExpired")
        self.assertIsNone(state["observations"])
        self.assertFalse((self.monitor.path(identity) / "source.mp4").exists())

    def test_restart_marks_interrupted_and_removes_only_owned_partial(self):
        identity = self.create()
        directory = self.monitor.path(identity)
        (directory / "source.part").write_bytes(b"partial fixture")
        foreign = self.monitor.directory / "keep-unrelated.txt"
        foreign.write_text("preserve")
        restarted = Monitor(self.root, self.config_path)
        restarted.close()
        record = json.loads((directory / "session.json").read_text())
        self.assertEqual(record["status"], "failed")
        self.assertEqual(record["error_type"], "ServerInterrupted")
        self.assertFalse((directory / "source.part").exists())
        self.assertEqual(foreign.read_text(), "preserve")

    def test_mutated_metadata_cannot_start_and_new_home_keeps_review(self):
        identity = self.ready()
        (self.monitor.path(identity) / "receipt.json").write_text("{}")
        response = self.client.post(f"/api/monitor/sessions/{identity}/start")
        self.assertEqual(response.status_code, 400)
        self.factory.assert_not_called()
        self.assertIn("monitor.js", self.client.get("/").text)
        self.assertIn("app.js", self.client.get("/review").text)
        self.assertEqual(self.client.get("/api/sessions").status_code, 200)

    def test_unknown_payload_not_deleted(self):
        identity = self.ready()
        (self.monitor.path(identity) / "outside-scope.txt").write_text("preserve")
        response = self.client.delete(f"/api/monitor/sessions/{identity}")
        self.assertEqual(response.status_code, 400)
        self.assertTrue((self.monitor.path(identity) / "source.mp4").exists())

    def test_payload_root_cannot_escape_outputs(self):
        config = yaml.safe_load(self.config_path.read_text())
        config = copy.deepcopy(config)
        config["output_root"] = "../outside"
        self.config_path.write_text(yaml.safe_dump(config))
        with self.assertRaises(ValueError):
            Monitor(self.root, self.config_path)

    def test_model_choice_default_provenance_cross_session_and_restart(self):
        runtimes, _, _, config_path = monitor_models_fixture(self.root)
        with patch("ai_exam_monitoring.web.monitor.load_runtime_config",
                   side_effect=lambda path, root: runtimes[path.stem]):
            with TestClient(create_app(self.root)) as client:
                monitor = client.app.state.monitor
                self.assertEqual(client.get("/api/monitor/state").json()["default_model"], "B0")
                for choice in ("../B0.yaml", 4):
                    response = client.post("/api/monitor/uploads", json={
                        "receipt": self.receipt, "size": len(self.payload), "model_id": choice})
                    self.assertEqual(response.status_code, 400)
                for choice in (None, "B448"):
                    body = {"receipt": self.receipt, "size": len(self.payload)}
                    if choice:
                        body["model_id"] = choice
                    response = client.post("/api/monitor/uploads", json=body)
                    self.assertEqual(response.status_code, 201, response.text)
                    record = response.json()["session"]
                    selected = choice or "B0"
                    self.assertEqual(record["schema_version"], "online-video-web-session-v2")
                    self.assertEqual(record["model_id"], selected)
                    self.assertEqual(record["classifier"]["preprocessing"]["image_size"],
                                     336 if selected == "B0" else 448)
                    self.assertEqual(record["classifier"]["thresholds"],
                                     [.207, .451] if selected == "B0" else [.358, .5])
                    identity = record["id"]
                    # A second choice cannot replace a ready/uploading session.
                    self.assertEqual(client.post("/api/monitor/uploads", json={
                        **body, "model_id": "B0"}).status_code, 409)
                    self.assertEqual(client.put(f"/api/monitor/uploads/{identity}",
                                                content=self.payload).status_code, 200)
                    if choice is None:
                        restarted = Monitor(self.root, config_path)
                        restarted.close()
                        saved = json.loads((monitor.path(identity) / "session.json").read_text())
                        self.assertEqual(saved["error_type"], "ServerInterrupted")
                        self.assertEqual(saved["model_id"], "B0")
                    else:
                        self.assertEqual(client.post(
                            f"/api/monitor/sessions/{identity}/start").status_code, 200)
                        self.wait_for(lambda: monitor.state()["session"]["status"] == "completed")
                        monitor.worker.join(2)
                        self.assertEqual(self.factory.call_args.args[0], self.root / "B448.yaml")
                        self.assertEqual(monitor.state()["session"]["model_id"], "B448")
                    self.assertEqual(client.delete(
                        f"/api/monitor/sessions/{identity}").status_code, 204)
