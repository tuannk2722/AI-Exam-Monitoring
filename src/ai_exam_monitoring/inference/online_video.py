"""Bounded, media-clock file playback with exact-frame instantaneous observations.

Internal adapter, not an artifact/wire schema or a C10/temporal event runner.
One decoder and one serial model worker; no frame list or unbounded result queue.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from threading import Condition, Thread
from typing import Any, Protocol

from PIL import Image, ImageDraw

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import TARGET_ORDER

from .frame_processor import FrameProcessor
from .runtime_config import load_runtime_config, media_deadline, verify_media
from .streaming import BufferStats, FrameStamp, LatestFrameBuffer, StreamFrame
from .video import FrameSampler, RecordedVideo, VideoFrame, validate_time


class VideoSource(Protocol):
    count: int

    def frames(self) -> Iterator[VideoFrame]: ...


@dataclass(frozen=True)
class OnlineResult:
    stamp: FrameStamp
    image: Image.Image
    observations: dict[str, Any]
    finished_ns: int
    target_order: tuple[str, ...] = TARGET_ORDER

    def annotated(self) -> Image.Image:
        """Render only on the image owned by this result, never a newer preview."""
        image = self.image.copy()
        draw = ImageDraw.Draw(image)
        for obs in self.observations["observations"]:
            labels = [name for name, above in zip(self.target_order, obs["above_threshold"],
                                                  strict=True)
                      if above]
            box = obs["person_box"]
            draw.rectangle(box, outline="orange" if labels else "lime", width=2)
            draw.text((box[0], box[1]), ", ".join(labels) or "person", fill="white")
        return image


@dataclass(frozen=True)
class PlaybackState:
    status: str
    epoch: int
    source_frame_index: int | None
    source_time_ms: float | None
    buffer: BufferStats
    processed: int
    stale_results: int
    replaced_results: int
    error_type: str | None


class OnlineVideoRunner:
    """Single-use playback session; start is idempotent, restart needs a new runner.

    All source access belongs to the decoder thread. Seek reopens and decodes to
    the exact index instead of trusting backend keyframe seek/approximate PTS.
    Stop is cooperative: it interrupts waits, but cannot kill a model/native read.
    Call join to await release; never interpret stopping as already released.
    All timestamps use perf_counter_ns, a monotonic high-resolution clock even
    on Windows/Python 3.11 where monotonic_ns can have coarse timer resolution.
    """

    def __init__(
        self, session_id: str, source: VideoSource,
        processor_factory: Callable[[], FrameProcessor], *, sampling_hz: float,
        guard: Callable[[], None], verify_source: Callable[[], None],
    ):
        FrameSampler(sampling_hz)
        if type(source.count) is not int or source.count < 1:
            raise DataContractError("Require a finite nonempty file source")
        self.session_id = session_id
        self.source = source
        self._factory = processor_factory
        self._hz = sampling_hz
        self._guard = guard
        self._verify_source = verify_source
        self._condition = Condition()
        self._buffer: LatestFrameBuffer[Image.Image] = LatestFrameBuffer(session_id)
        self._status = "idle"
        self._epoch = 0
        self._seek_index = 0
        self._origin_ns: int | None = None
        self._pause_ns: int | None = None
        self._source_index: int | None = None
        self._source_time: float | None = None
        self._eof = False
        self._halt = False
        self._processed = self._stale = self._replaced = 0
        self._error: str | None = None
        self._result: OnlineResult | None = None
        self._worker: Thread | None = None

    def start(self) -> None:
        with self._condition:
            if self._status != "idle":
                return
            self._status = "starting"
            self._worker = Thread(target=self._run, name="online-video-inference")
            self._worker.start()

    def pause(self) -> None:
        with self._condition:
            if self._status == "paused":
                return
            if self._status != "running":
                raise DataContractError("Pause requires running playback")
            self._pause_ns = time.perf_counter_ns()
            self._status = "paused"
            self._condition.notify_all()

    def resume(self) -> None:
        with self._condition:
            if self._status == "running":
                return
            if self._status != "paused" or self._pause_ns is None:
                raise DataContractError("Resume requires paused playback")
            if self._origin_ns is not None:
                self._origin_ns += time.perf_counter_ns() - self._pause_ns
            self._pause_ns = None
            self._status = "running"
            self._condition.notify_all()

    def seek(self, frame_index: int) -> None:
        with self._condition:
            if (type(frame_index) is not int or not 0 <= frame_index < self.source.count
                    or self._status not in {"running", "paused"}):
                raise DataContractError("Seek requires active playback and an existing frame index")
            self._epoch += 1
            self._buffer.reset(epoch=self._epoch)
            self._result = None
            self._seek_index = frame_index
            self._origin_ns = None
            self._source_index = self._source_time = None
            self._eof = False
            self._condition.notify_all()

    def stop(self) -> None:
        with self._condition:
            if self._status in {"completed", "stopped", "failed"} or self._halt:
                return
            self._halt = True
            self._epoch += 1
            self._buffer.reset(epoch=self._epoch)
            self._result = None
            self._status = "stopped" if self._worker is None else "stopping"
            self._condition.notify_all()

    def join(self, timeout: float | None = None) -> bool:
        """True only once both decoder and model worker have exited."""
        with self._condition:
            worker = self._worker
        if worker is not None:
            worker.join(timeout)
            return not worker.is_alive()
        return True

    def snapshot(self) -> PlaybackState:
        with self._condition:
            return PlaybackState(self._status, self._epoch, self._source_index,
                                 self._source_time, self._buffer.stats(), self._processed,
                                 self._stale, self._replaced, self._error)

    def take_result(self) -> OnlineResult | None:
        """Transfer one result; consumers compare epoch again before presentation.

        Use perf_counter_ns() - result.stamp.captured_ns for result age. Already
        taken snapshots belong to the consumer and cannot be revoked on seek.
        """
        # Enforce expiry even if the consumer asks after completion or a long pause.
        try:
            self._guard()
        except Exception as exc:
            self._fail(exc)
            raise
        with self._condition:
            result, self._result = self._result, None
            return result

    def _fail(self, exc: BaseException) -> None:
        with self._condition:
            if self._error is None:
                self._error = type(exc).__name__
            self._halt = True
            self._result = None
            self._epoch += 1
            self._buffer.reset(epoch=self._epoch)
            # Final status is assigned after resource release in _run.
            self._status = "stopping" if self._worker and self._worker.is_alive() else "failed"
            self._condition.notify_all()

    def _wait_due(self, epoch: int, relative_ms: float) -> bool:
        """Called with condition held; commands interrupt media-clock waits."""
        while not self._halt and epoch == self._epoch:
            self._guard()
            if self._status == "paused":
                self._condition.wait(0.25)
                continue
            if self._origin_ns is None:
                self._origin_ns = time.perf_counter_ns()
            delay = (self._origin_ns + int(relative_ms * 1_000_000) - time.perf_counter_ns()) / 1e9
            if delay <= 0:
                return True
            self._condition.wait(min(delay, 0.25))
        return False

    def _decode(self) -> None:
        try:
            while True:
                with self._condition:
                    if self._halt:
                        return
                    epoch, target = self._epoch, self._seek_index
                sampler = FrameSampler(self._hz)
                previous: float | None = None
                size: tuple[int, int] | None = None
                base: float | None = None
                count = 0
                frames = self.source.frames()
                try:
                    for frame in frames:
                        captured_ns = time.perf_counter_ns()
                        self._guard()
                        with self._condition:
                            if self._halt:
                                return
                            if epoch != self._epoch:
                                break
                        if frame.index != count or count >= self.source.count:
                            raise DataContractError("Missing or duplicated source frame")
                        count += 1
                        validate_time(frame.time_ms, previous)
                        previous = frame.time_ms
                        if size is not None and size != frame.image.size:
                            raise DataContractError("Video dimensions changed within epoch")
                        size = frame.image.size
                        if frame.index < target:
                            continue
                        if base is None:
                            base = frame.time_ms
                        with self._condition:
                            if not self._wait_due(epoch, frame.time_ms - base):
                                break
                            self._source_index, self._source_time = frame.index, frame.time_ms
                            if sampler.include(frame.time_ms):
                                stamp = FrameStamp(self.session_id, epoch, frame.index,
                                                   frame.time_ms, captured_ns, *size)
                                self._buffer.publish(StreamFrame(stamp, frame.image))
                                self._condition.notify_all()
                    else:
                        with self._condition:
                            if epoch == self._epoch:
                                if count != self.source.count:
                                    raise DataContractError("Incomplete decoded session")
                                self._eof = True
                                self._condition.notify_all()
                                # Stay alive until inference drains EOF or a seek arrives.
                                while not self._halt and epoch == self._epoch:
                                    self._guard()
                                    self._condition.wait(0.25)
                finally:
                    close = getattr(frames, "close", None)
                    if close is not None:
                        close()
        except BaseException as exc:
            self._fail(exc)

    def _run(self) -> None:
        decoder: Thread | None = None
        try:
            self._guard()
            self._verify_source()
            with self._condition:
                if self._halt:
                    return
            processor = self._factory()
            self._guard()
            with self._condition:
                if self._halt:
                    return
                self._status = "running"
                decoder = Thread(target=self._decode, name="online-video-decode")
                decoder.start()
            while True:
                with self._condition:
                    self._guard()
                    if self._halt:
                        break
                    if self._status == "paused":
                        self._condition.wait(0.25)
                        continue
                    frame = self._buffer.take()
                    if frame is None:
                        if self._eof:
                            # Atomic with seek: no command can reopen completed playback.
                            self._status = "stopping"
                            break
                        self._condition.wait(0.25)
                        continue
                stamp = frame.stamp
                row = processor.process(VideoFrame(stamp.sequence, stamp.source_time_ms,
                                                   frame.payload))
                self._guard()
                result = OnlineResult(stamp, frame.payload, row, time.perf_counter_ns(),
                                      tuple(getattr(processor, "target_order", TARGET_ORDER)))
                with self._condition:
                    self._processed += 1
                    if self._halt or stamp.epoch != self._epoch:
                        self._stale += 1
                    else:
                        if self._result is not None:
                            self._replaced += 1
                        self._result = result
            self._verify_source()
            self._guard()
        except BaseException as exc:
            self._fail(exc)
        finally:
            with self._condition:
                stopped = self._halt
                self._halt = True
                self._condition.notify_all()
            if decoder is not None:
                decoder.join()
            with self._condition:
                self._status = "failed" if self._error else "stopped" if stopped else "completed"
                self._condition.notify_all()


def create_online_video(
    config_path: Path, workspace: Path, source: Path, media_approval: Path,
    *, session_id: str, execution_selection: Path | None = None,
) -> OnlineVideoRunner:
    """Guarded production factory; no camera access, model fallback or artifact writes.

    Models load on start. Source and approval must describe an authorized local
    prototype clip; this API does not grant run permission or renew its deadline.
    """
    workspace, source = workspace.resolve(), source.resolve()
    if not source.is_file() or source.suffix.lower() != ".mp4":
        raise DataContractError("Require an existing local MP4")
    config = load_runtime_config(config_path, workspace)
    execution = None
    if execution_selection is not None:
        from .execution_processor import load_execution_selection

        execution = load_execution_selection(execution_selection, workspace, config)[0]
    rights = verify_media(source, media_approval, config)
    media_deadline(rights)
    hz = config.raw.get("sampling_hz")
    if not isinstance(hz, (float, int)) or not math.isfinite(hz) or hz <= 0:
        raise DataContractError("Online file playback requires explicit runtime sampling_hz")

    def guard() -> None:
        media_deadline(rights)

    def verify() -> None:
        if sha256_file(source) != rights["source_sha256"]:
            raise DataContractError("Video changed during playback")

    def processor() -> FrameProcessor:
        from .classifier import BundleClassifier
        from .person import PersonDetector

        # Revalidate pins at actual start, including approval changed after creation.
        current = load_runtime_config(config_path, workspace)
        if current.sha256 != config.sha256:
            raise DataContractError("Runtime config changed before playback")
        current_rights = verify_media(source, media_approval, current)
        if current_rights != rights:
            raise DataContractError("Media receipt changed before playback")
        if execution_selection is not None:
            from .execution_processor import create_execution_processor, load_execution_selection

            selected, settings = load_execution_selection(execution_selection, workspace, current)
            if selected != execution:
                raise DataContractError("Execution selection changed before playback")
            return create_execution_processor(current, settings, selected["packages"])
        classifier = BundleClassifier(current)
        return FrameProcessor(PersonDetector(current), classifier, current.raw["crop"])

    return OnlineVideoRunner(session_id, RecordedVideo(source), processor, sampling_hz=hz,
                             guard=guard, verify_source=verify)
