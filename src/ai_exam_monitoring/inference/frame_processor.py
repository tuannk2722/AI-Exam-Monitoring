"""Shared per-frame inference, without session I/O or temporal assumptions."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError

from .person import PersonDetection, crop_boxes
from .video import VideoFrame, validate_time


class Detector(Protocol):
    def predict(self, image: Image.Image) -> list[PersonDetection]: ...


class Classifier(Protocol):
    thresholds: list[float]

    def predict(self, image: Image.Image) -> list[float]: ...
    def preview(self, image: Image.Image) -> Image.Image: ...


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

    One owner executes model calls serially. No device/batch/threshold overrides.
    The optional sink is for the legacy QA writer, not live evidence persistence.
    """

    def __init__(self, detector: Detector, classifier: Classifier,
                 crop_policy: dict[str, Any]):
        self.detector = detector
        self.classifier = classifier
        self.crop_policy = dict(crop_policy)
        self.thresholds = list(classifier.thresholds)
        if len(self.thresholds) != 2 or any(not math.isfinite(v) for v in self.thresholds):
            raise DataContractError("Invalid operating thresholds")

    def detect(self, frame: VideoFrame) -> DetectedFrame:
        if type(frame.index) is not int or frame.index < 0:
            raise DataContractError("Invalid source frame index")
        validate_time(frame.time_ms, None)
        anchors = []
        for index, detection in enumerate(self.detector.predict(frame.image)):
            person, context = crop_boxes(detection, frame.image.size, self.crop_policy)
            anchors.append(Anchor(f"f{frame.index:08d}-a{index:03d}", person, context,
                                  detection.confidence))
        return DetectedFrame(frame, tuple(anchors))

    def classify(self, detected: DetectedFrame,
                 sink: ObservationSink | None = None) -> dict[str, Any]:
        frame = detected.frame
        observations = []
        for anchor in detected.anchors:
            crop = frame.image.crop(anchor.context_box)
            scores = self.classifier.predict(crop)
            if len(scores) != 2 or any(not math.isfinite(v) or not 0 <= v <= 1 for v in scores):
                raise DataContractError("Invalid behavior scores")
            observation = {
                "anchor_id": anchor.anchor_id, "person_box": anchor.person_box,
                "context_box": anchor.context_box, "detector_confidence": anchor.confidence,
                "scores": scores,
                "above_threshold": [s >= t for s, t in zip(scores, self.thresholds, strict=True)],
            }
            observations.append(observation)
            if sink is not None:
                sink(observation, crop)
        return {"record_type": "frame", "frame_index": frame.index,
                "video_time_ms": frame.time_ms, "width": frame.image.width,
                "height": frame.image.height, "observations": observations}

    def process(self, frame: VideoFrame,
                sink: ObservationSink | None = None) -> dict[str, Any]:
        return self.classify(self.detect(frame), sink)
