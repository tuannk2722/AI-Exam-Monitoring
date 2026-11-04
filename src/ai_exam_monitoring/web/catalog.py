"""Read immutable event evidence and join exact frame/anchor assignments."""

from __future__ import annotations

import io
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import preview_input


def read_json(path: Path) -> dict[str, Any]:
    value: dict[str, Any] = json.loads(path.read_text(encoding="utf-8-sig"))
    return value


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class Catalog:
    def __init__(self, workspace: Path):
        self.root = workspace.resolve()
        self.loaded: dict[str, dict[str, Any]] = {}
        self.sources: dict[str, Path] = {}

    def path(self, relative: str) -> Path:
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Đường dẫn phải thuộc workspace")
        return path

    def pin(self, pin: dict[str, str]) -> Path:
        path = self.path(pin["path"])
        if not path.is_file() or sha256_file(path) != pin["sha256"]:
            raise ValueError(f"Thiếu input hoặc SHA256 không khớp: {pin['path']}")
        return path

    def discover(self) -> list[dict[str, Any]]:
        result = []
        for path in sorted((self.root / "outputs").glob("**/session.json")):
            if "_scratch" in path.parts:
                continue
            try:
                session = read_json(path)
                if session.get("schema_version") not in {
                    "temporal-event-session-v1",
                    "recorded-session-v1",
                    "web-pipeline-session-v1",
                }:
                    continue
                result.append(
                    {
                        **session,
                        "id": path.parent.relative_to(self.root).as_posix(),
                        "reviewable": (path.parent / "events.jsonl").is_file()
                        and session.get("status") == "completed",
                    }
                )
            except (ValueError, OSError):
                continue
        return sorted(result, key=lambda s: (not s["reviewable"], s["id"]))

    def load(self, identity: str) -> dict[str, Any]:
        if identity in self.loaded:
            return self.loaded[identity]
        directory = self.path(identity)
        if not directory.is_relative_to(self.root / "outputs"):
            raise ValueError("Phiên phải ở outputs")
        session = read_json(directory / "session.json")
        if session.get("status") != "completed":
            raise ValueError("Phiên chưa hoàn tất")
        checks = read_json(directory / "checksums.json")
        for name in ("session.json", "events.jsonl", "accounting.json", "provenance.json"):
            self.pin({"path": f"{identity}/{name}", "sha256": checks[name]})
        provenance = read_json(directory / "provenance.json")
        parents = {k: self.pin(v) for k, v in provenance["parent_pins"].items()}
        assignment_path = self.pin(provenance["pins"]["assignments"])
        tracker_path = self.pin(provenance["pins"]["tracker_session"])
        self.pin(provenance["pins"]["rule"])
        predictions = rows(parents["predictions.jsonl"])
        metadata = predictions[0]
        frames = [r for r in predictions if r.get("record_type") == "frame"]
        assigned = rows(assignment_path)
        by_index = {r["frame_index"]: r for r in assigned}
        for frame in frames:
            match = by_index[frame["frame_index"]]
            if match["video_time_ms"] != frame["video_time_ms"]:
                raise ValueError("Thời gian tracking/runtime không khớp")
            mapping = {r["anchor_id"]: r for r in match["assignments"]}
            if len(mapping) != len(frame["observations"]):
                raise ValueError("Số anchor không khớp")
            for obs in frame["observations"]:
                track = mapping[obs["anchor_id"]]
                if obs["person_box"] != track["person_box"]:
                    raise ValueError("Geometry tracking/runtime không khớp")
                obs["track_id"] = track["track_id"]
        tracker = read_json(tracker_path)
        cache = tracker.get("input_pins", {}).get("cadence_cache")
        cadence = rows(self.pin(cache)) if cache else []
        acceptance = None
        for receipt in (self.root / "artifacts/reports").glob("*/owner-acceptance-*.json"):
            record = read_json(receipt)
            if record.get("pins", {}).get("events", {}).get("sha256") == checks["events.jsonl"]:
                acceptance = record
                break
        value = {
            "id": identity,
            "session": session,
            "provenance": provenance,
            "events_sha256": checks["events.jsonl"],
            "metadata": metadata,
            "runtime": read_json(parents["session.json"]),
            "frames": frames,
            "assignments": assigned,
            "cadence": cadence,
            "events": rows(directory / "events.jsonl"),
            "accounting": read_json(directory / "accounting.json"),
            "acceptance": acceptance,
            "runtime_dir": parents["session.json"].parent.relative_to(self.root).as_posix(),
            "cache_dir": self.path(cache["path"]).parent.relative_to(self.root).as_posix()
            if cache
            else None,
        }
        self.loaded[identity] = value
        return value

    def media_allowed(self, data: dict[str, Any]) -> None:
        deadline = datetime.fromisoformat(data["session"]["media_delete_by"])
        if deadline.tzinfo is None or datetime.now(UTC) >= deadline:
            raise PermissionError("Đã hết hạn lưu trữ media; chỉ còn metadata và provenance")

    def connect_source(self, identity: str, source: Path) -> None:
        data = self.load(identity)
        self.media_allowed(data)
        if source.suffix.lower() != ".mp4" or not source.is_file():
            raise ValueError("Cần file MP4 local")
        if sha256_file(source) != data["provenance"]["source_sha256"]:
            raise ValueError("SHA256 video không khớp nguồn của phiên")
        self.sources[identity] = source.resolve()

    def frame_image(self, data: dict[str, Any], index: int) -> Image.Image:
        self.media_allowed(data)
        allowed = {r["frame_index"] for r in data["assignments"]}
        if index not in allowed:
            raise ValueError("Frame không thuộc phiên")
        candidates = [self.path(data["runtime_dir"]) / f"f{index:08d}-source.png"]
        if data["cache_dir"]:
            candidates.append(self.path(data["cache_dir"]) / "frames" / f"f{index:08d}.png")
        for path in candidates:
            if path.is_file():
                # Reuse producer checksums, including cached cadence frame checksums.
                manifest = path.parent / "checksums.json"
                key = path.name
                if not manifest.is_file():
                    manifest = path.parent.parent / "checksums.json"
                    key = "frames/" + key
                expected = read_json(manifest).get(key)
                if not expected or sha256_file(path) != expected:
                    raise ValueError("Ảnh evidence không khớp checksum")
                with Image.open(path) as image:
                    return image.convert("RGB")
        source = self.sources.get(data["id"])
        if source is None:
            raise FileNotFoundError("Frame chưa có ảnh tĩnh. Kết nối video gốc đúng SHA256.")
        if sha256_file(source) != data["provenance"]["source_sha256"]:
            raise ValueError("Video nguồn đã thay đổi sau khi kết nối")
        from importlib import import_module

        cv = import_module("cv2")
        cap = cv.VideoCapture(str(source))
        try:
            cap.set(cv.CAP_PROP_POS_FRAMES, index)
            ok, bgr = cap.read()
            if not ok or int(cap.get(cv.CAP_PROP_POS_FRAMES)) != index + 1:
                raise ValueError("Không giải mã đúng frame nguồn")
            stamp = next(
                r["video_time_ms"] for r in data["assignments"] if r["frame_index"] == index
            )
            if abs(float(cap.get(cv.CAP_PROP_POS_MSEC)) - stamp) > 0.01:
                raise ValueError("Timestamp video không khớp evidence")
            return Image.fromarray(cv.cvtColor(bgr, cv.COLOR_BGR2RGB))
        finally:
            cap.release()

    def image(self, identity: str, index: int, anchor: str | None, kind: str) -> bytes:
        data = self.load(identity)
        image = self.frame_image(data, index)
        if anchor:
            frame = next((f for f in data["frames"] if f["frame_index"] == index), None)
            obs = (
                next((o for o in frame["observations"] if o["anchor_id"] == anchor), None)
                if frame
                else None
            )
            if obs is None:
                raise ValueError("Mốc này không có crop/classifier G0")
            image = image.crop(tuple(obs["context_box"]))
            if kind == "input":
                config = read_json(self.pin(data["metadata"]["pins"]["resolved_config"]))
                fill = tuple(config["fill"])
                image = preview_input(image, config["image_size"], (fill[0], fill[1], fill[2]))
        stream = io.BytesIO()
        image.save(stream, format="PNG")
        self.media_allowed(data)
        return stream.getvalue()
