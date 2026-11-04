"""Local API and persistence integration using synthetic evidence, never real decisions."""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import shutil
import tempfile
import time
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

AVAILABLE = all(importlib.util.find_spec(p) for p in ("fastapi", "httpx", "torch"))
if AVAILABLE:
    from fastapi.testclient import TestClient

    from ai_exam_monitoring.common.config import load_yaml
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.events import aggregate
    from ai_exam_monitoring.training.artifacts import checksum_artifacts, write_json
    from ai_exam_monitoring.web.app import create_app
    from ai_exam_monitoring.web.catalog import Catalog


def fixture(root: Path) -> str:
    """A tiny, clearly synthetic event session for API/browser checks."""
    runtime = root / "outputs/runtime"
    tracker = root / "outputs/tracking"
    events = root / "outputs/events"
    for path in (runtime, tracker, events, root / "configs/web"):
        path.mkdir(parents=True)
    deadline = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    write_json(root / "model.json", {"image_size": 336, "fill": [124, 116, 104]})

    def pin(path):
        return {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}

    rule = load_yaml(Path("configs/events/EVENTS-PROTOTYPE-20261027/approved-rule.yaml"))
    write_json(root / "rule.json", rule)
    write_json(
        runtime / "session.json",
        {
            "schema_version": "recorded-session-v1",
            "status": "completed",
            "media_delete_by": deadline,
            "frames": 3,
        },
    )
    write_json(runtime / "runtime-config.json", {})
    namespace = sha256_file(runtime / "session.json")
    metadata = {
        "record_type": "metadata",
        "target_order": ["phone_use", "looking_around"],
        "thresholds": [0.5, 0.4],
        "fps": 30,
        "source_frame_count": 90,
        "crop_policy": {"version": "context-v1"},
        "media_delete_by": deadline,
        "pins": {"resolved_config": pin(root / "model.json")},
    }
    frames, assignments = [], []
    for i in range(3):
        anchor = f"f{i * 30:08d}-a000"
        obs = {
            "anchor_id": anchor,
            "person_box": [200, 160, 600, 650],
            "context_box": [120, 100, 680, 700],
            "scores": [0.8, 0.2],
            "above_threshold": [True, False],
            "detector_confidence": 0.9,
        }
        frames.append(
            {
                "record_type": "frame",
                "frame_index": i * 30,
                "video_time_ms": i * 1000,
                "width": 1280,
                "height": 720,
                "observations": [obs],
            }
        )
        assignments.append(
            {
                "frame_index": i * 30,
                "video_time_ms": i * 1000,
                "arm_id": "C10",
                "parent_session_sha256": namespace,
                "assignments": [
                    {"anchor_id": anchor, "person_box": obs["person_box"], "track_id": 1}
                ],
            }
        )
        Image.new("RGB", (1280, 720), (60 + i * 30, 100, 140)).save(
            runtime / f"f{i * 30:08d}-source.png"
        )
    (runtime / "predictions.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in [metadata, *frames]), encoding="utf-8"
    )
    (tracker / "assignments.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in assignments), encoding="utf-8"
    )
    write_json(tracker / "session.json", {"status": "completed"})
    parent_pins = {
        name: pin(runtime / name)
        for name in ("session.json", "runtime-config.json", "predictions.jsonl")
    }
    candidates, accounting = aggregate(frames, assignments, metadata, rule, namespace, "synthetic")
    (events / "events.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in candidates), encoding="utf-8"
    )
    write_json(
        events / "session.json",
        {
            "schema_version": "temporal-event-session-v1",
            "status": "completed",
            "event_run_id": "SYNTHETIC-UI-TEST",
            "event_count": 1,
            "media_delete_by": deadline,
            "counts_by_behavior": {"phone_use": 1, "looking_around": 0},
        },
    )
    write_json(events / "accounting.json", accounting)
    write_json(
        events / "provenance.json",
        {
            "source_sha256": "0" * 64,
            "parent_pins": parent_pins,
            "pins": {
                "rule": pin(root / "rule.json"),
                "tracker_session": pin(tracker / "session.json"),
                "assignments": pin(tracker / "assignments.jsonl"),
            },
        },
    )
    checksum_artifacts(runtime)
    checksum_artifacts(events)
    (root / "configs/web/review.yaml").write_text(
        "output_root: outputs/web-review\n", encoding="utf-8"
    )
    return "outputs/events"


@unittest.skipUnless(AVAILABLE, "Install web and classifier dependencies")
class WebReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.identity = fixture(self.root)
        self.app = create_app(self.root)
        self.client = TestClient(self.app)
        self.query = {"identity": self.identity}

    def tearDown(self):
        self.app.state.jobs.executor.shutdown(wait=True)
        self.client.close()
        self.temp.cleanup()

    def test_read_join_and_preprocess(self):
        response = self.client.get("/api/session", params=self.query)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["events"]), 1)
        self.assertEqual(data["frames"][0]["observations"][0]["track_id"], 1)
        self.assertIsNone(data["acceptance"])
        image = self.client.get(
            "/api/image",
            params={**self.query, "frame": 0, "anchor": "f00000000-a000", "kind": "input"},
        )
        self.assertEqual(image.status_code, 200)
        with Image.open(io.BytesIO(image.content)) as prepared:
            self.assertEqual(prepared.size, (336, 336))
            self.assertEqual(prepared.getpixel((0, 0)), (124, 116, 104))
        self.assertEqual(image.headers["cache-control"], "no-store")

    def test_decisions_roundtrip_conflict_import_and_immutable_events(self):
        path = self.root / self.identity / "events.jsonl"
        original = path.read_bytes()
        data = self.client.get("/api/session", params=self.query).json()
        event_id = data["events"][0]["event"]["event_id"]
        review = self.client.get("/api/review", params=self.query).json()
        for status in ("confirmed", "dismissed", "uncertain", "candidate"):
            review["decisions"][event_id] = {
                "status": status,
                "note": "Synthetic test",
                "reasons": ["Che khuất"],
                "flagged": True,
            }
            saved = self.client.put("/api/review", params=self.query, json=review)
            self.assertEqual(saved.status_code, 200)
            self.assertEqual(
                self.client.put("/api/review", params=self.query, json=review).status_code, 409
            )
            review = saved.json()
        self.assertEqual(self.client.get("/api/review", params=self.query).json(), review)
        wrong = copy.deepcopy(review)
        wrong["events_sha256"] = "f" * 64
        self.assertEqual(
            self.client.put("/api/review", params=self.query, json=wrong).status_code, 400
        )
        wrong = copy.deepcopy(review)
        wrong["decisions"]["foreign"] = {"status": "confirmed"}
        self.assertEqual(
            self.client.put("/api/review", params=self.query, json=wrong).status_code, 400
        )
        self.assertEqual(path.read_bytes(), original)

    def test_missing_media_retention_and_wrong_pins(self):
        data = self.app.state.catalog.load(self.identity)
        (self.root / "outputs/runtime/f00000030-source.png").unlink()
        self.assertEqual(
            self.client.get("/api/image", params={**self.query, "frame": 30}).status_code, 400
        )
        data["session"]["media_delete_by"] = "2000-01-01T00:00:00+00:00"
        self.assertEqual(
            self.client.get("/api/image", params={**self.query, "frame": 0}).status_code, 410
        )
        self.assertEqual(self.client.get("/api/session", params=self.query).status_code, 200)
        (self.root / "outputs/events/events.jsonl").write_text("{}\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            Catalog(self.root).load(self.identity)

    def test_path_and_preflight_errors(self):
        self.assertEqual(
            self.client.get("/api/session", params={"identity": "../outside"}).status_code, 400
        )
        result = self.client.post(
            "/api/preflight", json={"source": "missing.mp4", "receipt": "missing.json"}
        )
        self.assertEqual(result.status_code, 400)
        self.assertIn("detail", result.json())

    def test_new_job_runtime_tracking_events_chain_and_failure(self):
        from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
        from ai_exam_monitoring.inference.video import VideoFrame

        jobs = self.app.state.jobs
        jobs.config.update(runtime="runtime.yaml", tracker="tracker.yaml", event_rule="rule.json")
        write_json(self.root / "runtime.yaml", {})
        write_json(
            self.root / "tracker.yaml", {"tracker_policy": {"track_buffer": 60}, "arm_policy": {}}
        )
        source = self.root / "synthetic.mp4"
        source.write_bytes(b"synthetic test source, not a production video")
        deadline = (datetime.now(UTC) + timedelta(days=1)).isoformat()
        frames = [VideoFrame(i, i * 1000 / 30, Image.new("RGB", (1280, 720))) for i in range(90)]
        video = SimpleNamespace(fps=30.0, frames=lambda: iter(frames))

        def runtime_fixture(config, workspace, media, receipt, output):
            shutil.copytree(self.root / "outputs/runtime", output)
            prediction_path = output / "predictions.jsonl"
            values = [json.loads(line) for line in prediction_path.read_text().splitlines()]
            values[0]["pins"]["checkpoint"] = {"sha256": "synthetic"}
            prediction_path.write_text(
                "".join(json.dumps(v) + "\n" for v in values), encoding="utf-8"
            )
            return {"status": "completed"}

        def assigned(frame, tracker, next_id):
            return (
                [
                    {"anchor_id": o["anchor_id"], "person_box": o["person_box"], "track_id": 1}
                    for o in frame["observations"]
                ],
                next_id,
            )

        with (
            patch.object(
                jobs,
                "preflight",
                return_value={
                    "source_sha256": sha256_file(source),
                    "media_delete_by": deadline,
                    "frames": 90,
                    "fps": 30,
                },
            ),
            patch("ai_exam_monitoring.inference.runtime.run_video", side_effect=runtime_fixture),
            patch(
                "ai_exam_monitoring.inference.runtime_config.load_runtime_config",
                return_value=RuntimeConfig({"crop": {}}, self.root),
            ),
            patch(
                "ai_exam_monitoring.inference.person.PersonDetector",
                return_value=SimpleNamespace(predict=lambda _: []),
            ),
            patch("ai_exam_monitoring.inference.video.RecordedVideo", return_value=video),
            patch("ai_exam_monitoring.inference.tracking.tracker_factory", return_value=object()),
            patch("ai_exam_monitoring.inference.tracking.assignments", side_effect=assigned),
        ):
            result = jobs.start(str(source), str(self.root / "receipt.json"))
            deadline_wait = time.monotonic() + 20
            while jobs.active[result["id"]]["status"] in {"queued", "running"}:
                self.assertLess(time.monotonic(), deadline_wait)
                time.sleep(0.05)
            state = jobs.active[result["id"]]
            self.assertEqual(state["status"], "completed", state)
            data = Catalog(self.root).load(state["review_id"])
            self.assertEqual(len(data["events"]), 1)
            self.assertEqual(len(data["assignments"]), 30)
            self.assertEqual(len(data["frames"]), 3)
            self.assertEqual(data["session"]["media_delete_by"], deadline)
            self.assertIsNone(data["acceptance"])
            with patch(
                "ai_exam_monitoring.inference.runtime.run_video",
                side_effect=RuntimeError("synthetic failure"),
            ):
                failed = jobs.start(str(source), str(self.root / "receipt.json"))
                while jobs.active[failed["id"]]["status"] in {"queued", "running"}:
                    self.assertLess(time.monotonic(), deadline_wait)
                    time.sleep(0.05)
                self.assertEqual(jobs.active[failed["id"]]["status"], "failed")
