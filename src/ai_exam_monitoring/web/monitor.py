"""Local upload/session ownership for the approved instantaneous-video slice."""

from __future__ import annotations

import copy
import json
import re
import threading
import time
import uuid
from pathlib import Path
from typing import Any, BinaryIO

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.inference.online_video import OnlineVideoRunner, create_online_video
from ai_exam_monitoring.inference.runtime_config import (
    load_runtime_config,
    media_deadline,
    verify_media,
    verify_media_receipt,
)
from ai_exam_monitoring.inference.video import RecordedVideo
from ai_exam_monitoring.training.artifacts import (
    code_identity,
    environment,
    now,
    write_json,
)

from .preview import PreviewBuffer

ACTIVE = {"uploading", "ready", "starting", "running", "paused", "stopping"}
TERMINAL = {"completed", "stopped", "failed"}
SESSION_FILES = {"source.mp4", "source.part", "receipt.json", "session.json",
                 "runtime-config.json", "web-config.json", "code-provenance.json",
                 "environment.json", "checksums.json"}


class Monitor:
    def __init__(self, root: Path, config_path: Path):
        self.root = root.resolve()
        self.config = load_yaml(config_path)
        expected = {"schema_version", "runtime", "output_root", "max_upload_bytes",
                    "max_receipt_bytes", "jpeg_quality", "transport_interval_ms"}
        if (set(self.config) != expected
                or self.config["schema_version"] != "online-video-web-config-v1"):
            raise ValueError("Cấu hình giám sát không hợp lệ")
        for key in ("max_upload_bytes", "max_receipt_bytes", "transport_interval_ms"):
            if type(self.config[key]) is not int or self.config[key] <= 0:
                raise ValueError("Giới hạn giám sát phải là số nguyên dương")
        PreviewBuffer("config-check", quality=self.config["jpeg_quality"])
        self.directory: Path = (self.root / self.config["output_root"]).resolve()
        if not self.directory.is_relative_to(self.root / "outputs"):
            raise ValueError("Phiên giám sát phải nằm trong outputs")
        self.runtime_path: Path = (self.root / self.config["runtime"]).resolve()
        if not self.runtime_path.is_relative_to(self.root):
            raise ValueError("Cấu hình runtime phải nằm trong workspace")
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.record: dict[str, Any] | None = None
        self.preview: PreviewBuffer | None = None
        self.runner: OnlineVideoRunner | None = None
        self.worker: threading.Thread | None = None
        self.latest: dict[str, Any] | None = None
        self.captured_ns: int | None = None
        self.writing = False
        self.closed = False
        self.last_command: dict[str, Any] | None = None
        self._recover()

    def path(self, identity: str) -> Path:
        if not re.fullmatch(r"session-[0-9a-f]{32}", identity):
            raise ValueError("Mã phiên không hợp lệ")
        path = self.directory / identity
        if path.resolve() != path or not path.is_relative_to(self.directory):
            raise ValueError("Đường dẫn phiên không hợp lệ")
        return path

    def _remove(self, directory: Path, names: set[str]) -> None:
        # Only this adapter's named files, never arbitrary recursive deletion.
        for name in names:
            path = directory / name
            if path.exists() and (path.resolve().parent != directory or not path.is_file()):
                raise ValueError("Payload phiên không hợp lệ")
        for name in names:
            (directory / name).unlink(missing_ok=True)

    def _recover(self) -> None:
        for directory in self.directory.glob("session-*"):
            if not re.fullmatch(r"session-[0-9a-f]{32}", directory.name):
                continue
            directory = self.path(directory.name)
            session = directory / "session.json"
            if not session.is_file():
                continue
            record = json.loads(session.read_text(encoding="utf-8"))
            if record.get("schema_version") != "online-video-web-session-v1":
                continue
            self._remove(directory, {"source.part"})
            if record["status"] in ACTIVE:
                record.update(status="failed", error_type="ServerInterrupted", ended_at=now())
                write_json(session, record)
            try:
                media_deadline(record)
            except Exception:
                self._remove(directory, {"source.mp4", "receipt.json"})

    def busy(self) -> bool:
        with self.lock:
            return bool(self.writing or (self.worker and self.worker.is_alive())
                        or (self.record and self.record["status"] in ACTIVE))

    def _current(self, identity: str) -> dict[str, Any]:
        if self.record is None or self.record["id"] != identity:
            raise FileNotFoundError("Phiên không còn là phiên hiện hành; hãy tải lại trạng thái")
        return self.record

    def _save(self) -> None:
        if self.record is not None:
            write_json(self.path(self.record["id"]) / "session.json", self.record)

    def create(self, receipt: dict[str, Any], size: int) -> dict[str, Any]:
        with self.lock:
            if self.closed or self.busy():
                raise FileExistsError("Hãy dừng hoặc xóa phiên hiện tại trước khi chọn video mới")
            if type(size) is not int or not 0 < size <= self.config["max_upload_bytes"]:
                raise ValueError("Video rỗng hoặc vượt giới hạn dung lượng")
            encoded = json.dumps(receipt, ensure_ascii=False, allow_nan=False).encode("utf-8")
            if len(encoded) > self.config["max_receipt_bytes"]:
                raise ValueError("Receipt vượt giới hạn dung lượng")
            source_sha = receipt.get("source_sha256")
            if not isinstance(source_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha):
                raise ValueError("Receipt thiếu SHA256 nguồn hợp lệ")
            runtime = load_runtime_config(self.runtime_path, self.root)
            verify_media_receipt(receipt, runtime, source_sha256=source_sha)
            media_deadline(receipt)
            identity = "session-" + uuid.uuid4().hex
            directory = self.path(identity)
            directory.mkdir(exist_ok=False)
            (directory / "receipt.json").write_bytes(encoded)
            write_json(directory / "runtime-config.json", runtime.raw)
            write_json(directory / "web-config.json", self.config)
            write_json(directory / "code-provenance.json", code_identity())
            write_json(directory / "environment.json", environment())
            if self.preview is not None:
                self.preview.close()
            self.preview = PreviewBuffer(identity, quality=self.config["jpeg_quality"])
            self.runner, self.latest, self.captured_ns = None, None, None
            self.last_command = None
            self.record = {
                "schema_version": "online-video-web-session-v1", "id": identity,
                "status": "uploading", "created_at": now(), "epoch": 0,
                "command_id": 0, "source_sha256": source_sha, "expected_bytes": size,
                "received_bytes": 0, "media_delete_by": receipt["media_delete_by"],
                "runtime_id": runtime.raw["runtime_id"], "runtime_sha256": runtime.sha256,
                "input_pins": {name: sha256_file(directory / name) for name in (
                    "receipt.json", "runtime-config.json", "web-config.json",
                    "code-provenance.json", "environment.json")},
                "processed": 0, "dropped": 0, "stale_results": 0,
            }
            self._save()
            return self.state()

    def begin_upload(self, identity: str) -> BinaryIO:
        with self.lock:
            record = self._current(identity)
            media_deadline(record)
            if record["status"] != "uploading" or self.writing:
                raise FileExistsError("Phiên không nhận thêm lượt upload")
            handle = (self.path(identity) / "source.part").open("xb")
            self.writing = True
            return handle

    def write_chunk(self, identity: str, handle: BinaryIO, chunk: bytes) -> None:
        with self.lock:
            record = self._current(identity)
            media_deadline(record)
            if self.closed or record["status"] != "uploading":
                raise ValueError("Upload đã dừng")
            total = record["received_bytes"] + len(chunk)
            if total > record["expected_bytes"] or total > self.config["max_upload_bytes"]:
                raise ValueError("Upload vượt dung lượng đã khai báo")
            handle.write(chunk)
            record["received_bytes"] = total

    def finish_upload(self, identity: str, digest: str) -> dict[str, Any]:
        with self.lock:
            record = self._current(identity)
            directory = self.path(identity)
            if (record["received_bytes"] != record["expected_bytes"]
                    or digest != record["source_sha256"]):
                raise ValueError("Dung lượng hoặc SHA256 video không khớp receipt")
            runtime = load_runtime_config(self.runtime_path, self.root)
            if runtime.sha256 != record["runtime_sha256"]:
                raise ValueError("Cấu hình runtime đã thay đổi")
            verify_media(directory / "source.part", directory / "receipt.json", runtime)
            media_deadline(record)
            (directory / "source.part").rename(directory / "source.mp4")
            video = RecordedVideo(directory / "source.mp4")
            record.update(status="ready", frame_count=video.count, fps=video.fps,
                          duration_ms=video.count / video.fps * 1000)
            self.writing = False
            self._save()
            return self.state()

    def abort_upload(self, identity: str, error: str) -> None:
        with self.lock:
            record = self._current(identity)
            self.writing = False
            self._remove(self.path(identity), {"source.part", "source.mp4"})
            record.update(status="failed", error_type=error, ended_at=now())
            self._save()

    def start(self, identity: str) -> dict[str, Any]:
        with self.lock:
            record = self._current(identity)
            if record["status"] in {"starting", "running", "paused"}:
                return self.state()
            if record["status"] != "ready" or self.closed:
                raise FileExistsError("Phiên chưa sẵn sàng hoặc đã kết thúc")
            media_deadline(record)
            directory = self.path(identity)
            for name, digest in record["input_pins"].items():
                if sha256_file(directory / name) != digest:
                    raise ValueError("Metadata phiên đã thay đổi")
            runtime = load_runtime_config(self.runtime_path, self.root)
            if runtime.sha256 != record["runtime_sha256"]:
                raise ValueError("Cấu hình runtime đã thay đổi")
            self.runner = create_online_video(self.runtime_path, self.root,
                                              directory / "source.mp4",
                                              directory / "receipt.json", session_id=identity)
            record.update(status="starting", started_at=now())
            self._save()
            self.runner.start()
            self.worker = threading.Thread(target=self._pump, name="monitor-preview")
            self.worker.start()
            return self.state()

    def _pump(self) -> None:
        assert self.runner is not None and self.preview is not None and self.record is not None
        runner, preview = self.runner, self.preview
        try:
            while True:
                before = runner.snapshot()
                result = runner.take_result()
                # Rendering/encoding outside the manager lock keeps stop/seek responsive.
                published = False
                if result is not None:
                    published = preview.publish(result.stamp, result.annotated())
                with self.lock:
                    state = runner.snapshot()
                    if state.epoch > preview.snapshot().epoch and not preview.snapshot().closed:
                        preview.reset(state.epoch)
                        self.latest, self.captured_ns = None, None
                    if published and result is not None and result.stamp.epoch == state.epoch:
                        self.latest = result.observations
                        self.captured_ns = result.stamp.captured_ns
                    # Completion can race take_result. Drain once more after a terminal
                    # snapshot before exposing EOF or leaving the final frame behind.
                    if state.status in TERMINAL and before.status not in TERMINAL:
                        continue
                    self.record.update(status=state.status, epoch=state.epoch,
                                       source_frame_index=state.source_frame_index,
                                       source_time_ms=state.source_time_ms,
                                       processed=state.processed, dropped=state.buffer.dropped,
                                       stale_results=state.stale_results,
                                       error_type=state.error_type)
                    if state.status in TERMINAL:
                        self.record["ended_at"] = now()
                    self._save()
                    if state.status in TERMINAL:
                        break
                time.sleep(self.config["transport_interval_ms"] / 1000)
        except Exception as exc:
            runner.stop()
            runner.join()
            with self.lock:
                self.record.update(status="failed", error_type=type(exc).__name__, ended_at=now())
                self.latest, self.captured_ns = None, None
                preview.close()
                self._save()
        finally:
            runner.join()

    def command(self, identity: str, value: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            record = self._current(identity)
            if value == self.last_command:
                return self.state()
            if (type(value.get("command_id")) is not int
                    or value["command_id"] != record["command_id"] + 1
                    or type(value.get("epoch")) is not int or value["epoch"] != record["epoch"]):
                raise FileExistsError("Lệnh cũ hoặc sai epoch; hãy tải lại trạng thái")
            action = value.get("action")
            if action not in {"pause", "resume", "seek", "stop"} or self.runner is None:
                raise ValueError("Lệnh điều khiển không hợp lệ")
            if action == "seek":
                frame_index = value.get("frame_index")
                if type(frame_index) is not int:
                    raise ValueError("Vị trí tua phải là frame index nguyên")
                self.runner.seek(frame_index)
                assert self.preview is not None
                self.preview.reset(self.runner.snapshot().epoch)
                self.latest, self.captured_ns = None, None
            elif action == "stop":
                self.runner.stop()
                assert self.preview is not None
                self.preview.close()
                self.latest, self.captured_ns = None, None
            elif action == "pause":
                self.runner.pause()
            else:
                self.runner.resume()
            state = self.runner.snapshot()
            record.update(command_id=value["command_id"], epoch=state.epoch, status=state.status)
            self.last_command = copy.deepcopy(value)
            self._save()
            return self.state()

    def state(self) -> dict[str, Any]:
        with self.lock:
            if self.record is not None:
                try:
                    media_deadline(self.record)
                except Exception:
                    if self.runner is not None:
                        self.runner.stop()
                    if self.preview is not None:
                        self.preview.close()
                    self.latest, self.captured_ns = None, None
                    self.record.update(status="failed", error_type="MediaExpired")
                    if not self.writing and not (self.worker and self.worker.is_alive()):
                        self._remove(self.path(self.record["id"]), {"source.mp4", "receipt.json"})
                    self._save()
            return {
                "session": copy.deepcopy(self.record), "observations": copy.deepcopy(self.latest),
                "result_age_ms": ((time.perf_counter_ns() - self.captured_ns) / 1e6
                                  if self.captured_ns is not None else None),
                "preview_revision": self.preview.snapshot().revision if self.preview else 0,
                "receiving": self.writing,
                "limits": {"upload_bytes": self.config["max_upload_bytes"],
                           "receipt_bytes": self.config["max_receipt_bytes"]},
            }

    def delete(self, identity: str) -> None:
        with self.lock:
            directory = self.path(identity)
            if self.record and identity == self.record["id"]:
                if self.writing or (self.worker and self.worker.is_alive()):
                    raise FileExistsError("Hãy đợi phiên dừng hoàn toàn trước khi xóa")
            if not directory.is_dir():
                raise FileNotFoundError("Không tìm thấy phiên")
            if any(p.name not in SESSION_FILES for p in directory.iterdir()):
                raise ValueError("Có file ngoài scope; không tự xóa thư mục phiên")
            self._remove(directory, SESSION_FILES)
            directory.rmdir()
            if self.record and identity == self.record["id"]:
                if self.preview:
                    self.preview.close()
                self.record = self.latest = None
                self.preview, self.runner, self.captured_ns = None, None, None

    def close(self) -> None:
        with self.lock:
            self.closed = True
            if self.runner:
                self.runner.stop()
            if self.preview:
                self.preview.close()
        if self.worker:
            self.worker.join()
