"""Local jobs reuse the approved runtime, C10 association and event aggregation."""

from __future__ import annotations

import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    environment,
    now,
    write_json,
)

from .catalog import Catalog, read_json, rows


class Jobs:
    def __init__(self, catalog: Catalog, config: dict[str, Any]):
        self.catalog, self.config = catalog, config
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.lock = threading.Lock()
        self.active: dict[str, dict[str, Any]] = {}
        root = catalog.path(config["output_root"])
        if root.exists():
            for path in root.glob("job-*/session.json"):
                record = read_json(path)
                if record.get("status") in {"queued", "running"}:
                    record.update(
                        status="failed",
                        error_type="ServerInterrupted",
                        error="Server đã dừng trước khi phiên hoàn tất",
                        ended_at=now(),
                    )
                    write_json(path, record)

    def preflight(self, source: str, receipt: str) -> dict[str, Any]:
        from ai_exam_monitoring.inference.runtime_config import (
            load_runtime_config,
            media_deadline,
            verify_media,
        )
        from ai_exam_monitoring.inference.video import RecordedVideo

        path = Path(source).resolve()
        if path.suffix.lower() != ".mp4" or not path.is_file():
            raise ValueError("Chọn file MP4 local tồn tại")
        runtime = load_runtime_config(self.catalog.path(self.config["runtime"]), self.catalog.root)
        rights = verify_media(path, Path(receipt).resolve(), runtime)
        media_deadline(rights)
        video = RecordedVideo(path)
        if not video.fps.is_integer() or int(video.fps) % 10:
            raise ValueError("C10 hiện cần FPS nguyên chia hết cho 10; không tự đổi cadence")
        return {
            "source_sha256": rights["source_sha256"],
            "media_delete_by": rights["media_delete_by"],
            "frames": video.count,
            "fps": video.fps,
            "duration_seconds": video.count / video.fps,
            "bytes": path.stat().st_size,
            "runtime_id": runtime.raw["runtime_id"],
        }

    def start(self, source: str, receipt: str) -> dict[str, Any]:
        info = self.preflight(source, receipt)
        identity = "job-" + uuid.uuid4().hex[:12]
        output = self.catalog.path(self.config["output_root"]) / identity
        output.mkdir(parents=True, exist_ok=False)
        inputs = {
            name: {
                "path": self.config[name],
                "sha256": sha256_file(self.catalog.path(self.config[name])),
            }
            for name in ("runtime", "tracker", "event_rule")
        }
        write_json(output / "web-config.json", self.config)
        write_json(output / "input-pins.json", inputs)
        write_json(output / "code-provenance.json", code_identity())
        write_json(output / "environment.json", environment())
        state = {
            "schema_version": "web-pipeline-session-v1",
            "id": identity,
            "status": "queued",
            "stage": "queued",
            "started_at": now(),
            **info,
        }
        write_json(output / "session.json", state)
        self.active[identity] = state
        self.executor.submit(
            self.run, Path(source).resolve(), Path(receipt).resolve(), output, state
        )
        return state.copy()

    def run(self, source: Path, receipt: Path, output: Path, state: dict[str, Any]) -> None:
        from ai_exam_monitoring.inference.events import aggregate
        from ai_exam_monitoring.inference.person import PersonDetector, crop_boxes
        from ai_exam_monitoring.inference.runtime import run_video
        from ai_exam_monitoring.inference.runtime_config import load_runtime_config, media_deadline
        from ai_exam_monitoring.inference.tracking import assignments, tracker_factory
        from ai_exam_monitoring.inference.video import RecordedVideo

        def update(**values: Any) -> None:
            with self.lock:
                state.update(values)
                write_json(output / "session.json", state)

        def pin(path: Path) -> dict[str, str]:
            return {
                "path": path.relative_to(self.catalog.root).as_posix(),
                "sha256": sha256_file(path),
            }

        try:
            update(status="running", stage="runtime")
            for value in read_json(output / "input-pins.json").values():
                self.catalog.pin(value)
            config_path = self.catalog.path(self.config["runtime"])
            run_video(config_path, self.catalog.root, source, receipt, output / "runtime")
            runtime = load_runtime_config(config_path, self.catalog.root)
            predictions = rows(output / "runtime/predictions.jsonl")
            metadata = predictions[0]
            parents = [r for r in predictions if r.get("record_type") == "frame"]
            parent_map = {f["frame_index"]: f for f in parents}
            parent_pins = {
                name: pin(output / "runtime" / name)
                for name in ("session.json", "predictions.jsonl", "runtime-config.json")
            }
            namespace = parent_pins["session.json"]["sha256"]
            cfg = load_yaml(self.catalog.path(self.config["tracker"]))
            settings = {
                **cfg["tracker_policy"],
                "frame_rate": 10,
                "expected_max_time_lost_updates": int(
                    10 / 30 * cfg["tracker_policy"]["track_buffer"]
                ),
            }
            tracker = tracker_factory(settings, cfg["arm_policy"], self.catalog.root)
            detector = PersonDetector(runtime)
            video = RecordedVideo(source)
            if not video.fps.is_integer() or int(video.fps) % 10:
                raise ValueError("C10 cần FPS nguyên chia hết cho 10")
            stride = int(video.fps) // 10
            track_dir = output / "tracking"
            track_dir.mkdir()
            all_assignments = []
            cadence = []
            next_id = 0
            update(stage="tracking", completed_samples=0)
            for frame in video.frames():
                media_deadline(state)
                if frame.index % stride:
                    continue
                row = parent_map.get(frame.index)
                if row is None:
                    obs = []
                    for i, detection in enumerate(detector.predict(frame.image)):
                        box, _ = crop_boxes(detection, frame.image.size, runtime.raw["crop"])
                        obs.append(
                            {
                                "anchor_id": f"f{frame.index:08d}-a{i:03d}",
                                "person_box": list(box),
                                "detector_confidence": detection.confidence,
                            }
                        )
                    row = {
                        "frame_index": frame.index,
                        "video_time_ms": frame.time_ms,
                        "width": frame.image.width,
                        "height": frame.image.height,
                        "observations": obs,
                    }
                assigned, next_id = assignments(row, tracker, next_id)
                cadence.append(row)
                all_assignments.append(
                    {
                        "schema_version": "track-assignments-v1",
                        "arm_id": "C10",
                        "parent_session_sha256": namespace,
                        "frame_index": frame.index,
                        "video_time_ms": frame.time_ms,
                        "assignments": assigned,
                    }
                )
                update(completed_samples=len(cadence), current_frame=frame.index)
            if sha256_file(source) != state["source_sha256"]:
                raise ValueError("Source changed during processing")
            for name, values in (
                ("assignments.jsonl", all_assignments),
                ("detections.jsonl", cadence),
            ):
                (track_dir / name).write_text(
                    "".join(json.dumps(r) + "\n" for r in values), encoding="utf-8"
                )
            write_json(
                track_dir / "session.json",
                {
                    "schema_version": "tracking-session-v1",
                    "status": "completed",
                    "arm_id": "C10",
                    "source_sha256": state["source_sha256"],
                    "media_delete_by": state["media_delete_by"],
                    "input_pins": {
                        **parent_pins,
                        "cadence_cache": pin(track_dir / "detections.jsonl"),
                    },
                },
            )
            checksum_artifacts(track_dir)
            update(stage="events")
            rule_path = self.catalog.path(self.config["event_rule"])
            rule = load_yaml(rule_path)
            projection = [r for r in all_assignments if r["frame_index"] in parent_map]
            candidates, accounting = aggregate(
                parents,
                projection,
                metadata,
                rule,
                namespace,
                metadata["pins"]["checkpoint"]["sha256"],
            )
            event_dir = output / "events"
            event_dir.mkdir()
            provenance = {
                "parent_pins": parent_pins,
                "source_sha256": state["source_sha256"],
                "model_pins": metadata["pins"],
                "rule_sha256": sha256_file(rule_path),
                "pins": {
                    "rule": pin(rule_path),
                    "assignments": pin(track_dir / "assignments.jsonl"),
                    "tracker_session": pin(track_dir / "session.json"),
                },
            }
            for event in candidates:
                event.update(provenance=provenance, media_delete_by=state["media_delete_by"])
            (event_dir / "events.jsonl").write_text(
                "".join(json.dumps(e) + "\n" for e in candidates), encoding="utf-8"
            )
            write_json(event_dir / "accounting.json", accounting)
            write_json(event_dir / "provenance.json", provenance)
            write_json(
                event_dir / "session.json",
                {
                    "schema_version": "temporal-event-session-v1",
                    "status": "completed",
                    "event_run_id": state["id"],
                    "event_count": len(candidates),
                    "media_delete_by": state["media_delete_by"],
                    "quality_acceptance": "pending_owner_review",
                    "counts_by_behavior": {
                        b: sum(e["event"]["behavior"] == b for e in candidates)
                        for b in metadata["target_order"]
                    },
                },
            )
            checksum_artifacts(event_dir)
            identity = event_dir.relative_to(self.catalog.root).as_posix()
            self.catalog.sources[identity] = source
            update(status="completed", stage="completed", review_id=identity, ended_at=now())
        except Exception as exc:
            update(
                status="failed",
                error_type=type(exc).__name__,
                error="Không hoàn tất pipeline. Kiểm tra receipt, pins và artifacts của phiên.",
                ended_at=now(),
            )
        finally:
            checksum_artifacts(output)
