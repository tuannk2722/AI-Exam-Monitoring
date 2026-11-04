"""In-memory exact-frame JPEG fan-out; no subscriber queues or persisted schema."""

from __future__ import annotations

import io
from dataclasses import dataclass
from threading import Condition

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.inference.streaming import FrameStamp


@dataclass(frozen=True)
class PreviewSnapshot:
    revision: int
    epoch: int
    stamp: FrameStamp | None
    jpeg: bytes | None
    closed: bool


class PreviewBuffer:
    """One producer, any number of readers, one retained encoded frame.

    Call reset immediately on seek/source invalidation. Encoding happens outside
    the lock; a second epoch check prevents a concurrent reset publishing stale
    pixels. Subscribers wait for revisions, then read the newest full snapshot.
    They never enqueue every frame and cannot consume another viewer's update.
    """

    def __init__(self, session_id: str, *, quality: int):
        if not session_id.strip() or type(quality) is not int or not 1 <= quality <= 95:
            raise DataContractError("Require a session ID and JPEG quality from 1 to 95")
        self._session_id = session_id
        self._quality = quality
        self._condition = Condition()
        self._snapshot = PreviewSnapshot(0, 0, None, None, False)

    def snapshot(self) -> PreviewSnapshot:
        with self._condition:
            return self._snapshot

    def wait(self, after_revision: int, timeout: float) -> PreviewSnapshot:
        """Blocking reader primitive; async transports must wait off the event loop."""
        if after_revision < -1 or timeout < 0:
            raise DataContractError("Invalid preview cursor or wait timeout")
        with self._condition:
            self._condition.wait_for(
                lambda: self._snapshot.revision > after_revision or self._snapshot.closed,
                timeout=timeout,
            )
            return self._snapshot

    def reset(self, epoch: int) -> None:
        with self._condition:
            current = self._snapshot
            if type(epoch) is not int or epoch <= current.epoch or current.closed:
                raise DataContractError("Preview reset requires a newer active epoch")
            self._snapshot = PreviewSnapshot(current.revision + 1, epoch, None, None, False)
            self._condition.notify_all()

    def close(self) -> None:
        with self._condition:
            current = self._snapshot
            if current.closed:
                return
            self._snapshot = PreviewSnapshot(current.revision + 1, current.epoch,
                                             None, None, True)
            self._condition.notify_all()

    def publish(self, stamp: FrameStamp, annotated: Image.Image) -> bool:
        """Caller supplies an annotation rendered on this exact source frame.

        Returns False for an invalidated/closed epoch, including reset mid-encode.
        Bad session/geometry/order is an error, not a silently accepted overlay.
        """
        if stamp.session_id != self._session_id or annotated.size != (stamp.width, stamp.height):
            raise DataContractError("Preview identity or geometry mismatch")
        with self._condition:
            if self._snapshot.closed or stamp.epoch != self._snapshot.epoch:
                return False
        output = io.BytesIO()
        annotated.convert("RGB").save(output, format="JPEG", quality=self._quality)
        with self._condition:
            current = self._snapshot
            if current.closed or stamp.epoch != current.epoch:
                return False
            if current.stamp is not None and (
                stamp.sequence <= current.stamp.sequence
                or stamp.source_time_ms <= current.stamp.source_time_ms
                or stamp.captured_ns <= current.stamp.captured_ns
                or (stamp.width, stamp.height) != (current.stamp.width, current.stamp.height)
            ):
                raise DataContractError("Preview frame identity must advance within epoch")
            self._snapshot = PreviewSnapshot(current.revision + 1, current.epoch,
                                             stamp, output.getvalue(), False)
            self._condition.notify_all()
            return True
