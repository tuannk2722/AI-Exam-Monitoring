"""Build a complete, offline visual review workspace without changing any labels."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import PilotRecord, read_records
from ai_exam_monitoring.data.source_review import preview_input


def accepted_records(records: list[PilotRecord]) -> list[PilotRecord]:
    """Include approved review-only and test too; never filter on old split."""
    result = sorted((r for r in records if r.disposition == "approved"),
                    key=lambda r: r.sample_id)
    if len({r.sample_id for r in records}) != len(records):
        raise ValueError("Duplicate sample ID")
    if any(r.crop is None or r.crop.review is None for r in result):
        raise ValueError("Approved crop missing reviewed pixels")
    return result


def visual_features(image: Image.Image) -> np.ndarray[Any, Any]:
    """Layout, color and edges only; no label, source, split or model scores."""
    rgb = np.asarray(image.convert("RGB").resize((8, 8)), dtype=np.float32) / 255
    gray = rgb.mean(axis=2)
    return np.concatenate((rgb.ravel(), np.diff(gray, axis=0).ravel(),
                           np.diff(gray, axis=1).ravel(),
                           [np.log(image.width / image.height) * 3])).astype(np.float32)


def visual_groups(features: np.ndarray[Any, Any], count: int) -> list[list[int]]:
    """Deterministic farthest-first k-means, then nearest-neighbor review order."""
    if not len(features) or count < 1:
        raise ValueError("Empty inventory or invalid group count")
    centers = [features[0]]
    nearest = np.full(len(features), np.inf)
    for _ in range(1, min(count, len(features))):
        nearest = np.minimum(nearest, ((features - centers[-1]) ** 2).sum(axis=1))
        if nearest.max() == 0:
            break
        centers.append(features[int(nearest.argmax())])
    matrix = np.asarray(centers)
    assignment = np.zeros(len(features), dtype=int)
    for _ in range(20):
        distances = ((features[:, None, :] - matrix[None, :, :]) ** 2).sum(axis=2)
        updated = distances.argmin(axis=1)
        unchanged = np.array_equal(updated, assignment)
        assignment = updated
        for k in range(len(matrix)):
            members = features[assignment == k]
            if len(members):
                matrix[k] = members.mean(axis=0)
        if unchanged:
            break
    groups = []
    for k in range(len(matrix)):
        remaining = np.flatnonzero(assignment == k).tolist()
        if not remaining:
            continue
        first = min(remaining, key=lambda i: (float(((features[i] - matrix[k]) ** 2).sum()), i))
        order = [first]
        remaining.remove(first)
        while remaining:
            last = order[-1]
            next_id = min(remaining, key=lambda i: (
                float(((features[i] - features[last]) ** 2).sum()), i))
            order.append(next_id)
            remaining.remove(next_id)
        groups.append(order)
    return groups


def _path(workspace: Path, value: str) -> Path:
    path = (workspace / value).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise ValueError("Path outside workspace")
    return path


def _json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(config_path: Path, workspace: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    package = _path(workspace, config["package"])
    ledger = package / "review-ledger.jsonl"
    if sha256_file(ledger) != config["ledger_sha256"]:
        raise ValueError("Ledger pin mismatch")
    records = read_records(ledger)
    accepted = accepted_records(records)
    if len(accepted) != config["expected_accepted"]:
        raise ValueError("Accepted inventory mismatch")
    if any(r.usage == "test" for r in accepted) and not config["allow_test_visual_review"]:
        raise ValueError("Test visual access not authorized")
    recipe_path = _path(workspace, config["recipe"])
    if sha256_file(recipe_path) != config["recipe_sha256"]:
        raise ValueError("Recipe pin mismatch")
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    size, fill = recipe["image_size"], tuple(recipe["fill"])
    if size != 224:
        raise ValueError("UI currently requires a 224 pixel preview")
    # Verify all input bytes before creating the workspace; do not silently skip failures.
    for r in accepted:
        assert r.crop is not None
        crop_path = _path(package, r.crop.crop_relpath)
        if sha256_file(crop_path) != r.crop.crop_sha256:
            raise ValueError(f"Crop SHA mismatch: {r.sample_id}")
        with Image.open(crop_path) as im:
            im.verify()
    output = _path(workspace, config["output"])
    report = _path(workspace, config["report"])
    if output.exists() or report.exists():
        raise ValueError("Refusing to overwrite review workspace/report")
    output.mkdir(parents=True)
    report.mkdir(parents=True)
    (output / "images").mkdir()
    rows: list[dict[str, Any]] = []
    features = []
    for index, r in enumerate(accepted):
        assert r.crop is not None
        source = package / r.crop.crop_relpath
        original = f"images/{index:04d}-crop{source.suffix.lower()}"
        prepared = f"images/{index:04d}-224.png"
        shutil.copyfile(source, output / original)
        with Image.open(source) as im:
            rgb = im.convert("RGB")
            preview_input(rgb, size, fill).save(output / prepared)
            features.append(visual_features(rgb))
            w, h = rgb.size
        scale = size / max(w, h)
        notes = []
        if scale > 1:
            notes.append(f"Phóng {scale:.2f}×: đối chiếu chi tiết đầu/tay/vật ở bản 224.")
        if r.crop.derivation:
            notes.append("Crop là derivative: nếu cần thêm chi tiết, kiểm lại ROI từ frame gốc.")
        notes.append("Nếu thiếu vùng cần quan sát: ghi rõ cần mở rộng đầu/vai/tay/bàn; "
                     "không suy nhãn từ độ nét hoặc kích thước.")
        rows.append({"id": r.sample_id, "sha256": r.crop.crop_sha256,
                     "anchor": [
                         (r.crop.person_box.xmin - r.crop.context_box.xmin)
                         / (r.crop.context_box.xmax - r.crop.context_box.xmin),
                         (r.crop.person_box.ymin - r.crop.context_box.ymin)
                         / (r.crop.context_box.ymax - r.crop.context_box.ymin),
                         (r.crop.person_box.xmax - r.crop.context_box.xmin)
                         / (r.crop.context_box.xmax - r.crop.context_box.xmin),
                         (r.crop.person_box.ymax - r.crop.context_box.ymin)
                         / (r.crop.context_box.ymax - r.crop.context_box.ymin)],
                     "original": original, "input": prepared, "width": w, "height": h,
                     "scale": round(scale, 4), "suggestion": " ".join(notes),
                     "old_usage": r.usage, "old_labels": list(r.target_values),
                     "source": r.source.source_id,
                     "lineage": r.group.leakage_group_id if r.group else None,
                     "blockers": list(r.ineligibility_reasons),
                     "preview_sha256": sha256_file(output / prepared)})
    groups = []
    for i, members in enumerate(visual_groups(np.stack(features), config["groups"]), 1):
        group_id = f"G{i:02d}"
        ratios = [rows[j]["width"] / rows[j]["height"] for j in members]
        aspect = "dọc" if np.median(ratios) < .8 else (
            "ngang" if np.median(ratios) > 1.25 else "gần vuông")
        groups.append({"id": group_id, "title": f"{group_id} · Crop {aspect}",
                       "members": [rows[j]["id"] for j in members],
                       "note": "Nhóm gần nhau về bố cục/màu/cạnh, không phải nhãn hành vi. "
                       "So sánh hướng đầu với thân/bàn; phân biệt vật trong tay/trên bàn. "
                       "Ghi nhu cầu bổ sung mẫu tương phản hoặc góc nhìn nếu thấy thiếu."})
        for rank, j in enumerate(members):
            rows[j].update(group=group_id, rank=rank)
    cohort = hashlib.sha256(json.dumps(
        [(r["id"], r["sha256"]) for r in rows], separators=(",", ":")
    ).encode()).hexdigest()
    payload = {"schema": "crop-review-workspace-v1", "cohort": cohort,
               "image_size": size, "fill": fill, "records": rows, "groups": groups}
    _json(output / "inventory.json", payload)
    # Script data instead of fetch allows offline file:// use.
    (output / "inventory.js").write_text("window.AUDIT=" + json.dumps(
        payload, ensure_ascii=False).replace("<", "\\u003c") + ";\n", encoding="utf-8")
    templates = Path(__file__).with_name("review_workspace_assets")
    for name in ("index.html", "review.js", "review.css"):
        shutil.copyfile(templates / name, output / name)
    summary = {"cohort": cohort, "total_accepted": len(rows),
               "old_roles": dict(Counter(r.usage for r in accepted)),
               "excluded": [r.sample_id for r in records if r.disposition != "approved"],
               "groups": len(groups), "test_visual_access": [
                   r.sample_id for r in accepted if r.usage == "test"],
               "coverage": "Every approved ledger ID exactly once, irrespective of usage",
               "changes_to_labels_splits_release": False,
               "input_pins": {str(config_path.relative_to(workspace)): sha256_file(config_path),
                              config["recipe"]: sha256_file(recipe_path),
                              str(ledger.relative_to(workspace)): sha256_file(ledger)},
               "inventory_sha256": sha256_file(output / "inventory.json")}
    _json(report / "inventory-check.json", summary)
    _json(report / "accepted-inventory.json", [
        {k: r[k] for k in ("id", "sha256", "group", "old_usage", "preview_sha256")}
        for r in rows])
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = build(args.config.resolve(), args.workspace.resolve())
    print(json.dumps({k: result[k] for k in ("total_accepted", "old_roles", "groups")}))


if __name__ == "__main__":
    main()
