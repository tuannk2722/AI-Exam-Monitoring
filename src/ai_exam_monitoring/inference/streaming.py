"""Internal streaming primitives; no capture, model, transport or persisted schema.

One buffer belongs to one source session. Capture and freshness checks must use
the same process monotonic clock. Callers transfer payload ownership on publish;
mutable image bytes must not be reused or changed while inference owns them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from threading import Lock
from typing import Generic, TypeVar

from ai_exam_monitoring.common.errors import DataContractError

T = TypeVar("T")


def _nonnegative_integer(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise DataContractError(f"{name} must be a nonnegative integer")


@dataclass(frozen=True)
class FrameStamp:
    """Exact decoded frame identity, before any resize, rotation or overlay."""

    session_id: str
    epoch: int
    sequence: int
    source_time_ms: float
    captured_ns: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if not self.session_id.strip():
            raise DataContractError("Frame requires a session ID")
        for name in ("epoch", "sequence", "captured_ns", "width", "height"):
            _nonnegative_integer(getattr(self, name), name)
        if self.width == 0 or self.height == 0:
            raise DataContractError("Frame dimensions must be positive")
        if not math.isfinite(self.source_time_ms) or self.source_time_ms < 0:
            raise DataContractError("Source time must be finite and nonnegative")


@dataclass(frozen=True)
class StreamFrame(Generic[T]):
    stamp: FrameStamp
    payload: T


@dataclass(frozen=True)
class BufferStats:
    accepted: int
    taken: int
    dropped: int
    pending: bool


class LatestFrameBuffer(Generic[T]):
    """Thread-safe, nonblocking single pending slot, not a lossless file queue.

    A taken frame is owned by the consumer and never replaced. The runner must
    separately reject its eventual result after an epoch change. Counters are
    lifetime totals; reset discards only the pending frame and advances epoch.
    """

    def __init__(self, session_id: str, *, epoch: int = 0) -> None:
        if not session_id.strip():
            raise DataContractError("Buffer requires a session ID")
        _nonnegative_integer(epoch, "epoch")
        self._session_id = session_id
        self._epoch = epoch
        self._lock = Lock()
        self._pending: StreamFrame[T] | None = None
        self._last: FrameStamp | None = None
        self._accepted = 0
        self._taken = 0
        self._dropped = 0

    def publish(self, frame: StreamFrame[T]) -> None:
        stamp = frame.stamp
        with self._lock:
            if stamp.session_id != self._session_id or stamp.epoch != self._epoch:
                raise DataContractError("Frame belongs to another session or inactive epoch")
            previous = self._last
            if previous is not None:
                if (stamp.sequence <= previous.sequence
                        or stamp.source_time_ms <= previous.source_time_ms
                        or stamp.captured_ns <= previous.captured_ns):
                    raise DataContractError("Frame sequence and clocks must advance within epoch")
                if (stamp.width, stamp.height) != (previous.width, previous.height):
                    raise DataContractError("Geometry change requires a new epoch")
            if self._pending is not None:
                self._dropped += 1
            self._pending = frame
            self._last = stamp
            self._accepted += 1

    def take(self) -> StreamFrame[T] | None:
        with self._lock:
            frame = self._pending
            self._pending = None
            if frame is not None:
                self._taken += 1
            return frame

    def reset(self, *, epoch: int) -> None:
        """Invalidate pending work on reconnect/seek; epochs cannot be reused."""
        _nonnegative_integer(epoch, "epoch")
        with self._lock:
            if epoch <= self._epoch:
                raise DataContractError("Reset requires a newer epoch")
            if self._pending is not None:
                self._dropped += 1
            self._pending = None
            self._last = None
            self._epoch = epoch

    def stats(self) -> BufferStats:
        with self._lock:
            return BufferStats(
                self._accepted, self._taken, self._dropped, self._pending is not None
            )


def can_overlay(
    displayed: FrameStamp,
    result: FrameStamp,
    *,
    now_ns: int,
    max_age_ns: int,
) -> bool:
    """Require the exact frame and an explicit freshness budget, never track ID.

    The caller also verifies that displayed.epoch is the active source epoch.
    This predicate neither transforms boxes nor propagates labels between frames.
    """
    _nonnegative_integer(now_ns, "now_ns")
    _nonnegative_integer(max_age_ns, "max_age_ns")
    return displayed == result and 0 <= now_ns - result.captured_ns <= max_age_ns
