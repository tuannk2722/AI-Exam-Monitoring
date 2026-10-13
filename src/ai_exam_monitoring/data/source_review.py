"""Pinned ZIP inspection and pending review artifacts; never labels/groups/splits approval."""

from __future__ import annotations

import hashlib
import io
import json
import math
import re
import zipfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import numpy as np
from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .image_similarity import difference_hash
from .pilot_schema import PixelBox
from .source_layout import IMAGE_EXTENSIONS, validate_source_names
from .yolo import YoloAnnotation


def member_key(name: str) -> str:
    """Technical locator without publishing potentially identifying upstream names."""
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


def _safe_member(name: str) -> None:
    path = PurePosixPath(name)
    if (
        path.is_absolute()
        or "\\" in name
        or ":" in name
        or any(p in {".", "..", ""} for p in name.rstrip("/").split("/"))
    ):
        raise DataContractError("Unsafe ZIP member path")


@dataclass(frozen=True)
class SourceAnnotation:
    line: int
    class_id: int
    class_name: str
    box: PixelBox


@dataclass(frozen=True)
class SourceImage:
    member_sha256: str
    image_sha256: str
    label_sha256: str
    original_split: str
    image_bytes: bytes
    image: Image.Image
    annotations: tuple[SourceAnnotation, ...]


class PinnedYoloZip:
    """Read by technical member key; pin ZIP, reject ambiguous images/labels and bad files."""

    def __init__(self, path: Path, expected_sha256: str, names: dict[int, str]):
        validate_source_names(names)
        if sha256_file(path) != expected_sha256:
            raise DataContractError("Source ZIP SHA differs from approved input")
        self.names = names
        self.stream = zipfile.ZipFile(path)
        self.entries: dict[str, zipfile.ZipInfo] = {}
        try:
            for info in self.stream.infolist():
                _safe_member(info.filename)
                if info.is_dir():
                    continue
                if info.filename in self.entries:
                    old = self.entries[info.filename]
                    if info.filename != "data.yaml" or self.stream.read(info) != self.stream.read(
                        old
                    ):
                        raise DataContractError("Ambiguous duplicate ZIP member")
                    continue
                self.entries[info.filename] = info
            self.lookup = {member_key(name): name for name in self.entries}
        except BaseException:
            self.stream.close()
            raise

    def close(self) -> None:
        self.stream.close()

    def image_keys(self) -> list[str]:
        return sorted(
            member_key(name)
            for name in self.entries
            if Path(name).suffix.lower() in IMAGE_EXTENSIONS and "/images/" in name
        )

    def lineage_key(self, key: str) -> str:
        name = self.lookup[key]
        stem = re.sub(r"\.rf\.[0-9a-f]+$", "", PurePosixPath(name).stem)
        return member_key(stem)

    def read(self, key: str, expected_image_sha256: str | None = None) -> SourceImage:
        name = self.lookup.get(key)
        if name is None or key not in self.image_keys_set:
            raise DataContractError("Unknown source image member key")
        raw = self.stream.read(self.entries[name])
        digest = hashlib.sha256(raw).hexdigest()
        if expected_image_sha256 is not None and digest != expected_image_sha256:
            raise DataContractError("Source image bytes differ from shortlist pin")
        label = name.replace("/images/", "/labels/").rsplit(".", 1)[0] + ".txt"
        if label not in self.entries:
            raise DataContractError("Missing paired source label")
        label_bytes = self.stream.read(self.entries[label])
        with Image.open(io.BytesIO(raw)) as opened:
            opened.load()
            image = opened.convert("RGB")
        annotations = []
        # A malformed line rejects the whole source file; no partial annotations returned.
        for line_no, line in enumerate(label_bytes.decode("utf-8-sig").splitlines(), 1):
            if not line.strip():
                continue
            yolo = YoloAnnotation.parse(line)
            if yolo.class_id not in self.names:
                raise DataContractError("Source class ID outside declared namespace")
            annotations.append(
                SourceAnnotation(
                    line_no,
                    yolo.class_id,
                    self.names[yolo.class_id],
                    PixelBox(
                        max(0, math.floor((yolo.x_center - yolo.width / 2) * image.width)),
                        max(0, math.floor((yolo.y_center - yolo.height / 2) * image.height)),
                        min(image.width, math.ceil((yolo.x_center + yolo.width / 2) * image.width)),
                        min(
                            image.height,
                            math.ceil((yolo.y_center + yolo.height / 2) * image.height),
                        ),
                    ),
                )
            )
        return SourceImage(
            key,
            digest,
            hashlib.sha256(label_bytes).hexdigest(),
            name.split("/")[0],
            raw,
            image,
            tuple(annotations),
        )

    @property
    def image_keys_set(self) -> set[str]:
        if not hasattr(self, "_image_keys"):
            self._image_keys = set(self.image_keys())
        return self._image_keys


def scene_descriptor(image: Image.Image) -> tuple[int, ...]:
    """Small spatial RGB descriptor for ranking inspection, not scene/session classification."""
    return tuple(image.convert("RGB").resize((12, 8), Image.Resampling.BILINEAR).tobytes())


def descriptor_distance(a: Sequence[int], b: Sequence[int]) -> float:
    if len(a) != 288 or len(b) != 288:
        raise DataContractError("Expected 12x8 RGB scene descriptors")
    return sum(abs(x - y) for x, y in zip(a, b, strict=True)) / 288


def fingerprint(source: SourceImage) -> dict[str, Any]:
    return {
        "member_sha256": source.member_sha256,
        "source_sha256": source.image_sha256,
        "label_sha256": source.label_sha256,
        "original_split": source.original_split,
        "size": list(source.image.size),
        "dhash": difference_hash(source.image),
        "scene_descriptor": list(scene_descriptor(source.image)),
        "source_class_hints": sorted({a.class_name for a in source.annotations}),
        "source_annotation_count": len(source.annotations),
        "canonical_targets": [None, None],
        "canonical_mask": [0, 0],
        "usage": "review_only",
        "independence_proven": False,
    }


def diverse_inspection(
    rows: Sequence[dict[str, Any]], seeds: Sequence[dict[str, Any]], limit: int
) -> list[dict[str, Any]]:
    """Deterministic farthest-first preview budget, no automatic group/split/label decision."""
    if type(limit) is not int or limit < 0:
        raise DataContractError("Inspection limit must be nonnegative")
    seen = {r["source_sha256"] for r in seeds}
    candidates = {r["source_sha256"]: r for r in rows if r["source_sha256"] not in seen}
    ordered = [candidates[k] for k in sorted(candidates)]
    if not ordered or limit == 0:
        return []
    if any(len(r["scene_descriptor"]) != 288 for r in [*ordered, *seeds]):
        raise DataContractError("Expected 12x8 RGB scene descriptors")
    vectors = np.asarray([r["scene_descriptor"] for r in ordered], dtype=np.int16)
    distances = np.full(len(ordered), np.inf)
    for seed in seeds:
        delta = np.abs(vectors - np.asarray(seed["scene_descriptor"], dtype=np.int16)).mean(1)
        distances = np.minimum(distances, delta)
    chosen: list[dict[str, Any]] = []
    for _ in range(min(limit, len(ordered))):
        index = int(np.argmax(distances))
        row = ordered[index]
        chosen.append(row)
        delta = np.abs(vectors - vectors[index]).mean(1)
        distances = np.minimum(distances, delta)
        distances[index] = -np.inf
    return chosen


def preview_input(image: Image.Image, size: int, fill: tuple[int, int, int]) -> Image.Image:
    """Same RGB letterbox geometry as training; a preview does not approve visibility."""
    if type(size) is not int or size <= 0:
        raise DataContractError("Preview size must be positive")
    if len(fill) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in fill):
        raise DataContractError("Invalid RGB fill")
    image = image.convert("RGB")
    scale = size / max(image.size)
    dims = (
        max(1, min(size, round(image.width * scale))),
        max(1, min(size, round(image.height * scale))),
    )
    result = Image.new("RGB", (size, size), fill)
    result.paste(
        image.resize(dims, Image.Resampling.BILINEAR),
        ((size - dims[0]) // 2, (size - dims[1]) // 2),
    )
    return result


def write_pending_crop(
    source: SourceImage,
    person: PixelBox,
    context: PixelBox,
    candidate_id: str,
    output: Path,
    *,
    states: tuple[str, str],
    reason: str,
    input_size: int,
    fill: tuple[int, int, int],
) -> dict[str, Any]:
    """Explicit geometry/state proposal only. Owner approval must be imported separately."""
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", candidate_id) is None:
        raise DataContractError("Unsafe candidate ID")
    if len(states) != 2 or any(s not in {"P", "N", "U"} for s in states) or not reason.strip():
        raise DataContractError("Invalid draft states/reason")
    bounds = PixelBox(0, 0, source.image.width, source.image.height)
    if not bounds.contains(context) or not context.contains(person):
        raise DataContractError("Person/context geometry outside source or containment mismatch")
    destination = output / candidate_id
    if destination.exists():
        raise DataContractError("Pending review output already exists")
    destination.mkdir(parents=True)
    (destination / "source.bin").write_bytes(source.image_bytes)
    source.image.save(destination / "source.png")
    crop = source.image.crop(context.xyxy)
    prepared = preview_input(crop, input_size, fill)
    crop.save(destination / "crop.png")
    prepared.save(destination / "input.png")
    row = {
        "candidate_id": candidate_id,
        "source_sha256": source.image_sha256,
        "source_member_sha256": source.member_sha256,
        "label_sha256": source.label_sha256,
        "person_xyxy": list(person.xyxy),
        "context_xyxy": list(context.xyxy),
        "crop_sha256": sha256_file(destination / "crop.png"),
        "input_sha256": sha256_file(destination / "input.png"),
        "input_pixel_sha256": hashlib.sha256(prepared.tobytes()).hexdigest(),
        "input_size": input_size,
        "fill": list(fill),
        "draft_states": list(states),
        "draft_reason": reason,
        "canonical_targets": [None, None],
        "canonical_mask": [0, 0],
        "usage": "review_only",
        "split": None,
        "owner_approved": False,
        "independence_proven": False,
        "proposed_role": "unassigned_pending_family_review",
    }
    (destination / "proposal.json").write_text(
        json.dumps(row, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return row
