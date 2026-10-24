"""Person-only detector and approved integer context geometry."""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from importlib import import_module
from importlib.metadata import version

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError

from .runtime_config import RuntimeConfig


@dataclass(frozen=True)
class PersonDetection:
    xyxy: tuple[float, float, float, float]
    confidence: float


def crop_boxes(
    detection: PersonDetection, size: tuple[int, int], margins: dict[str, float],
) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    w, h = size
    values = detection.xyxy
    if (w <= 0 or h <= 0 or len(values) != 4
            or any(not math.isfinite(v) for v in values)
            or not 0 <= detection.confidence <= 1
            or values[0] >= values[2] or values[1] >= values[3]):
        raise DataContractError("Invalid person detection")
    person = (max(0, math.floor(values[0])), max(0, math.floor(values[1])),
              min(w, math.ceil(values[2])), min(h, math.ceil(values[3])))
    x1, y1, x2, y2 = person
    if x1 >= x2 or y1 >= y2:
        raise DataContractError("Person box lies outside image")
    bw, bh = x2 - x1, y2 - y1
    context = (max(0, math.floor(x1 - bw * margins["left"])),
               max(0, math.floor(y1 - bh * margins["top"])),
               min(w, math.ceil(x2 + bw * margins["right"])),
               min(h, math.ceil(y2 + bh * margins["bottom"])))
    return person, context


class PersonDetector:
    def __init__(self, config: RuntimeConfig):
        receipt = json.loads(config.pin("detector_receipt").read_text(encoding="utf-8"))
        for package, expected in receipt["packages"].items():
            if version(package) != expected:
                raise DataContractError(f"Runtime package changed: {package}")
        if receipt["weights_sha256"] != config.raw["pins"]["detector_weights"]["sha256"]:
            raise DataContractError("Detector receipt/weights mismatch")
        # Set before import: no analytics, synchronization, or implicit model downloads.
        os.environ["YOLO_OFFLINE"] = "true"
        settings_dir = config.workspace / "outputs/runtime-settings"
        settings_dir.mkdir(parents=True, exist_ok=True)
        os.environ["YOLO_CONFIG_DIR"] = str(settings_dir)
        ultralytics = import_module("ultralytics")
        ultralytics.settings.update({"sync": False})
        self.model = ultralytics.YOLO(str(config.pin("detector_weights")), task="detect")
        names = {str(k): v for k, v in self.model.names.items()}
        if names != receipt["taxonomy"] or names.get("0") != "person":
            raise DataContractError("Detector taxonomy mismatch")
        self.variables = config.raw["detector"]

    def predict(self, image: Image.Image) -> list[PersonDetection]:
        results = self.model.predict(source=image, classes=[0], verbose=False, save=False,
                                     stream=False, **self.variables)
        if len(results) != 1:
            raise DataContractError("Expected exactly one detector frame result")
        detections = []
        if results[0].boxes is not None:
            for box in results[0].boxes:
                if int(box.cls.item()) != 0:
                    raise DataContractError("Non-person detection in person-only adapter")
                coords = [float(v) for v in box.xyxy[0].tolist()]
                if len(coords) != 4:
                    raise DataContractError("Invalid detector coordinates")
                detections.append(PersonDetection((coords[0], coords[1], coords[2], coords[3]),
                                                  float(box.conf.item())))
        return detections
