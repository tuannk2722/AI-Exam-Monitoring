"""Local recorded-video decoding with explicit frame/time integrity checks."""
from __future__ import annotations

import math
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError


@dataclass(frozen=True)
class VideoFrame:
    index: int
    time_ms: float
    image: Image.Image


def validate_time(value: float, previous: float | None) -> None:
    if not math.isfinite(value) or value < 0 or (previous is not None and value <= previous):
        raise DataContractError("Require finite, nonnegative, strictly increasing timestamps")


class RecordedVideo:
    def __init__(self, path: Path):
        self.path = path
        self.cv = import_module("cv2")
        cap = self.cv.VideoCapture(str(path))
        try:
            if not cap.isOpened():
                raise DataContractError("Cannot open recorded video")
            count = float(cap.get(self.cv.CAP_PROP_FRAME_COUNT))
            self.fps = float(cap.get(self.cv.CAP_PROP_FPS))
            if (not math.isfinite(count) or count < 1 or count != int(count)
                    or not math.isfinite(self.fps) or self.fps <= 0):
                raise DataContractError("Video requires valid frame count and FPS")
            self.count = int(count)
        finally:
            cap.release()

    def frames(self) -> Iterator[VideoFrame]:
        cap = self.cv.VideoCapture(str(self.path))
        previous: float | None = None
        size: tuple[int, int] | None = None
        try:
            if not cap.isOpened():
                raise DataContractError("Cannot reopen video")
            for index in range(self.count):
                ok, bgr = cap.read()
                if not ok or bgr is None:
                    raise DataContractError("Video decode stopped before declared frame count")
                stamp = float(cap.get(self.cv.CAP_PROP_POS_MSEC))
                validate_time(stamp, previous)
                previous = stamp
                image = Image.fromarray(self.cv.cvtColor(bgr, self.cv.COLOR_BGR2RGB))
                if size is not None and size != image.size:
                    raise DataContractError("Video dimensions changed during session")
                size = image.size
                yield VideoFrame(index, stamp, image)
            ok, _ = cap.read()
            if ok:
                raise DataContractError("Video contains more frames than declared")
        finally:
            cap.release()


def qa_indices(times: Sequence[float], limit: int) -> set[int]:
    if not times or limit < 1:
        raise DataContractError("QA sampling requires frames and positive limit")
    previous = None
    for value in times:
        validate_time(value, previous)
        previous = value
    if len(times) <= limit:
        return set(range(len(times)))
    if limit == 1:
        return {0}
    return {min(range(len(times)), key=lambda i: abs(times[i] - target))
            for target in (times[0] + (times[-1] - times[0]) * j / (limit - 1)
                           for j in range(limit))}


def sample_indices(times: Sequence[float], hz: float) -> list[int]:
    """First decoded frame at/after each sampling boundary; retain source indices."""
    if not math.isfinite(hz) or hz <= 0:
        raise DataContractError("Sampling rate must be finite and positive")
    result: list[int] = []
    previous = None
    boundary = times[0] if times else 0.
    interval = 1000 / hz
    for index, stamp in enumerate(times):
        validate_time(stamp, previous)
        previous = stamp
        if stamp >= boundary:
            result.append(index)
            boundary += (math.floor((stamp - boundary) / interval) + 1) * interval
    return result
