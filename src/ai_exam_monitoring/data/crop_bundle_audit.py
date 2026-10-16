"""Read-only integrity primitives for external crop bundles, never label acceptance."""

from __future__ import annotations

import hashlib
import io
import math
import stat
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.image_similarity import difference_hash


def safe_member(name: str) -> None:
    """Reject absolute/traversal/Windows alias paths before any extraction."""
    path = PurePosixPath(name)
    if (
        not name
        or path.is_absolute()
        or "\\" in name
        or ":" in name
        or any(p in {"", ".", ".."} or p.endswith((" ", ".")) for p in name.rstrip("/").split("/"))
    ):
        raise DataContractError("Unsafe archive member")


def read_pinned_zip(path: Path, digest: str) -> dict[str, bytes]:
    """Verify pin and every member CRC, rejecting ambiguous paths and symlinks."""
    if sha256_file(path) != digest:
        raise DataContractError("Archive SHA mismatch")
    result: dict[str, bytes] = {}
    seen: set[str] = set()
    with zipfile.ZipFile(path) as archive:
        for entry in archive.infolist():
            safe_member(entry.filename)
            key = entry.filename.rstrip("/").casefold()
            if key in seen or stat.S_ISLNK(entry.external_attr >> 16):
                raise DataContractError("Ambiguous archive path or symbolic link")
            seen.add(key)
            if not entry.is_dir():
                result[entry.filename] = archive.read(entry)
    return result


def image_fingerprint(raw: bytes) -> dict[str, Any]:
    """Fully decode original orientation; retain EXIF flags, do not repair images."""
    with Image.open(io.BytesIO(raw)) as image:
        image.load()
        rgb = image.convert("RGB")
        dims = f"{rgb.width}x{rgb.height}:".encode("ascii")
        return {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "rgb_sha256": hashlib.sha256(dims + rgb.tobytes()).hexdigest(),
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
            "frames": getattr(image, "n_frames", 1),
            "exif_orientation": image.getexif().get(274),
            "dhash": difference_hash(rgb),
        }


def candidate_issues(row: dict[str, Any]) -> list[str]:
    """Validate an external proposal's geometry/state, not canonical PilotRecord."""
    issues: list[str] = []
    for field in ("crop_file", "source_frame"):
        try:
            safe_member(row[field])
        except (KeyError, TypeError, AttributeError, DataContractError):
            issues.append(f"invalid_{field}")
    for field in ("phone", "looking"):
        if row.get(field) not in ("P", "N", "U"):
            issues.append(f"invalid_{field}")
    for field in ("source_width", "source_height", "crop_width", "crop_height", "frame_num"):
        if type(row.get(field)) is not int or row[field] <= 0:
            issues.append(f"invalid_{field}")
    box = row.get("bbox_xyxy")
    if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
        issues.append("invalid_box")
    elif not issues:
        x0, y0, x1, y1 = box
        if not (0 <= x0 < x1 <= row["source_width"] and 0 <= y0 < y1 <= row["source_height"]):
            issues.append("box_outside_source")
        center = row.get("anchor_center_xy")
        if (
            not isinstance(center, list)
            or len(center) != 2
            or any(type(v) not in (int, float) or not math.isfinite(v) for v in center)
            or not (x0 <= center[0] < x1 and y0 <= center[1] < y1)
        ):
            issues.append("center_outside_box")
    if row.get("split") is not None or row.get("training_ready") is not False:
        issues.append("unexpected_assignment")
    if row.get("label_status") != "provisional" or type(row.get("review_only")) is not bool:
        issues.append("unexpected_review_state")
    if not row.get("parent_id") or row.get("parent_id") != row.get("source_group"):
        issues.append("parent_group_mismatch")
    return issues
