"""Shared per-frame inference, without session I/O or temporal assumptions."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import MULTILABEL_TARGET_ORDER, TARGET_ORDER

from .person import PersonDetection, crop_boxes
from .profiling import StageProfiler
from .video import VideoFrame, validate_time


class Detector(Protocol):
    def predict(self, image: Image.Image) -> list[PersonDetection]: ...


class Classifier(Protocol):
    thresholds: list[float]

    def predict(self, image: Image.Image) -> list[float]: ...
    def preview(self, image: Image.Image) -> Image.Image: ...


@runtime_checkable
class BatchClassifier(Classifier, Protocol):
    def predict_batch(self, images: Sequence[Image.Image]) -> list[list[float]]: ...


@dataclass(frozen=True)
class Anchor:
    anchor_id: str
    person_box: tuple[int, int, int, int]
    context_box: tuple[int, int, int, int]
    confidence: float


@dataclass(frozen=True)
class DetectedFrame:
    """Owns the exact image and anchors; callers must not mutate image bytes."""

    frame: VideoFrame
    anchors: tuple[Anchor, ...]


ObservationSink = Callable[[dict[str, Any], Image.Image], None]


class FrameProcessor:
    """Separate detection and classification so future tracking can snapshot anchors.

    One owner executes model calls serially. Legacy callers keep batch size one.
    The optional sink is for the legacy QA writer, not live evidence persistence.
    """

    def __init__(self, detector: Detector, classifier: Classifier,
                 crop_policy: dict[str, Any], *, batch_size: int = 1,
                 profiler: StageProfiler | None = None):
        if type(batch_size) is not int or not 1 <= batch_size <= 100:
            raise DataContractError("Require batch size 1..100")
        if batch_size > 1 and not isinstance(classifier, BatchClassifier):
            raise DataContractError("Batch execution requires a batch-capable classifier")
        self.batch_size = batch_size
        self.profiler = profiler
        self.detector = detector
        self.classifier = classifier
        self.crop_policy = dict(crop_policy)
        self.target_order = tuple(getattr(classifier, "target_order", TARGET_ORDER))
        self.thresholds = list(classifier.thresholds)
        if (self.target_order not in (TARGET_ORDER, MULTILABEL_TARGET_ORDER)
                or len(self.thresholds) != len(self.target_order)
                or any(not math.isfinite(v) or not 0 <= v <= math.nextafter(1., 2.)
                       for v in self.thresholds)):
            raise DataContractError("Invalid operating thresholds")

    def detect(self, frame: VideoFrame) -> DetectedFrame:
        if type(frame.index) is not int or frame.index < 0:
            raise DataContractError("Invalid source frame index")
        validate_time(frame.time_ms, None)
        anchors = []
        with self.profiler.measure("detect") if self.profiler else nullcontext():
            detections = self.detector.predict(frame.image)
        for index, detection in enumerate(detections):
            person, context = crop_boxes(detection, frame.image.size, self.crop_policy)
            anchors.append(Anchor(f"f{frame.index:08d}-a{index:03d}", person, context,
                                  detection.confidence))
        return DetectedFrame(frame, tuple(anchors))

    def classify(self, detected: DetectedFrame,
                 sink: ObservationSink | None = None) -> dict[str, Any]:
        frame = detected.frame
        observations = []
        for start in range(0, len(detected.anchors), self.batch_size):
            chunk = detected.anchors[start:start + self.batch_size]
            with self.profiler.measure("crop") if self.profiler else nullcontext():
                crops = [frame.image.crop(anchor.context_box) for anchor in chunk]
            with self.profiler.measure("classify") if self.profiler else nullcontext():
                if self.batch_size == 1:
                    rows = [self.classifier.predict(crops[0])]
                else:
                    assert isinstance(self.classifier, BatchClassifier)
                    rows = self.classifier.predict_batch(crops)
            if len(rows) != len(chunk):
                raise DataContractError("Classifier batch count differs from anchors")
            for anchor, crop, scores in zip(chunk, crops, rows, strict=True):
                if (len(scores) != len(self.target_order)
                        or any(not math.isfinite(v) or not 0 <= v <= 1 for v in scores)):
                    raise DataContractError("Invalid behavior scores")
                observation = {
                    "anchor_id": anchor.anchor_id, "person_box": anchor.person_box,
                    "context_box": anchor.context_box, "detector_confidence": anchor.confidence,
                    "scores": scores,
                    "above_threshold": [s >= t for s, t in
                                        zip(scores, self.thresholds, strict=True)],
                }
                observations.append(observation)
                if sink is not None:
                    sink(observation, crop)
        return {"record_type": "frame", "frame_index": frame.index,
                "video_time_ms": frame.time_ms, "width": frame.image.width,
                "height": frame.image.height, "observations": observations}

    def process(self, frame: VideoFrame,
                sink: ObservationSink | None = None) -> dict[str, Any]:
        with self.profiler.measure("frame") if self.profiler else nullcontext():
            return self.classify(self.detect(frame), sink)
