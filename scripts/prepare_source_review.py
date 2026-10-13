"""Build pinned inspection inventory/boards, not dataset membership or model predictions."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import (
    PinnedYoloZip,
    descriptor_distance,
    diverse_inspection,
    fingerprint,
    scene_descriptor,
)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


def boards(reader: PinnedYoloZip, rows: list[dict[str, Any]], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
    for start in range(0, len(rows), 6):
        board = Image.new("RGB", (1440, 1110), "white")
        for pos, row in enumerate(rows[start : start + 6]):
            source = reader.read(row["member_sha256"], row["source_sha256"])
            image = source.image.copy()
            draw = ImageDraw.Draw(image)
            for annotation in source.annotations:
                if annotation.class_name == row["priority_hint"]:
                    draw.rectangle(annotation.box.xyxy, outline="red", width=2)
            image.thumbnail((710, 323))
            x, y = (pos % 2) * 720, (pos // 2) * 370
            board.paste(image, (x, y + 45))
            canvas = ImageDraw.Draw(board)
            canvas.text((x + 5, y + 3), row["review_id"], font=font, fill="black")
            canvas.text((x + 5, y + 24), row["priority_hint"], font=font, fill="black")
        board.save(output / f"board-{start // 6 + 1:02d}.png")


def prepare(config_path: Path, workspace: Path) -> None:
    config = load_yaml(config_path)
    if config["status"] != "authorized_draft_preparation":
        raise DataContractError("Require data-preparation direction")
    audit_path = workspace / config["source_audit"]
    if sha256_file(audit_path) != config["source_audit_sha256"]:
        raise DataContractError("Source audit input changed")
    manifest = workspace / config["parent_manifest"]
    if sha256_file(manifest) != config["parent_manifest_sha256"]:
        raise DataContractError("Parent manifest changed")
    output = (workspace / config["output"]).resolve()
    if not output.is_relative_to((workspace / "data/interim").resolve()) or output.exists():
        raise DataContractError("Preparation needs new output under data/interim")
    output.mkdir(parents=True)
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    old = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
    old_sources: dict[str, list[dict[str, Any]]] = {}
    for row in old:
        if row["usage"] == "test":
            continue
        old_sources.setdefault(row["source"]["image_sha256"], []).append(row)
    old_visual: list[dict[str, Any]] = []
    with zipfile.ZipFile(workspace / "archive/history-20261010.zip") as history:
        available = set(history.namelist())
        for digest, records in old_sources.items():
            name = "blobs/" + digest
            if name not in available:
                continue
            raw = history.read(name)
            if hashlib.sha256(raw).hexdigest() != digest:
                raise DataContractError("Historical source blob SHA differs")
            with Image.open(io.BytesIO(raw)) as image:
                descriptor = scene_descriptor(image)
            old_visual.append(
                {
                    "source_sha256": digest,
                    "scene_descriptor": list(descriptor),
                    "sample_ids": [r["sample_id"] for r in records],
                    "groups": sorted({r["group"]["leakage_group_id"] for r in records}),
                    "usages": sorted({r["usage"] for r in records}),
                }
            )
    old_visual.sort(key=lambda row: row["source_sha256"])
    old_vectors = np.asarray([row["scene_descriptor"] for row in old_visual], dtype=np.int16)
    write_json(output / "non-test-parent-scene-fingerprints.json", old_visual)
    all_selected = []
    for source_config in config["sources"]:
        key = source_config["audit_key"]
        cached = audit["sources"][key]
        flag_ids = {r["source_sha256"] for r in cached["dhash64_le4_existing_screening"]["details"]}
        reader = PinnedYoloZip(
            Path(source_config["archive"]), source_config["archive_sha256"], source_config["names"]
        )
        try:
            rows = []
            invalid = []
            for index, member in enumerate(reader.image_keys(), 1):
                try:
                    source = reader.read(member)
                    row = fingerprint(source)
                    row.update(
                        {
                            "source_id": source_config["id"],
                            "archive_sha256": source_config["archive_sha256"],
                            "lineage_hint_sha256": reader.lineage_key(member),
                            "cached_overlap_flag": source.image_sha256 in flag_ids,
                        }
                    )
                    distances = np.abs(
                        old_vectors - np.asarray(row["scene_descriptor"], dtype=np.int16)
                    ).mean(1)
                    nearest = [old_visual[int(i)] for i in np.argsort(distances, kind="stable")[:3]]
                    row["nearest_parent_scene_for_visual_review"] = [
                        {
                            "source_sha256": old["source_sha256"],
                            "sample_ids": old["sample_ids"],
                            "groups": old["groups"],
                            "usages": old["usages"],
                            "descriptor_distance": descriptor_distance(
                                row["scene_descriptor"], old["scene_descriptor"]
                            ),
                            "confirmed_overlap": False,
                        }
                        for old in nearest
                    ]
                    rows.append(row)
                except (DataContractError, OSError, UnicodeError) as exc:
                    invalid.append({"member_sha256": member, "error": str(exc)})
                if index % 1500 == 0:
                    print(source_config["id"], index, "inspected", flush=True)
            bysha = {r["source_sha256"]: r for r in rows}
            seeds = []
            for previous in cached["draft_shortlist"]:
                row = {
                    **bysha[previous["source_sha256"]],
                    "review_id": previous["id"],
                    "priority_hint": previous["priority_hint"],
                    "selection": "original_shortlist40",
                }
                seeds.append(row)
            chosen = list(seeds)
            for hint in source_config["inspection_hints"]:
                eligible = [
                    r
                    for r in rows
                    if hint in r["source_class_hints"] and not r["cached_overlap_flag"]
                ]
                new = diverse_inspection(eligible, chosen, config["expanded_inspection_per_hint"])
                for row in new:
                    chosen.append(
                        {
                            **row,
                            "review_id": source_config["id"].upper()[:3]
                            + "-X-"
                            + row["source_sha256"][:12],
                            "priority_hint": hint,
                            "selection": "farthest_first_visual_inspection_not_group_proof",
                        }
                    )
            write_json(output / (source_config["id"] + "-inventory.json"), rows)
            write_json(output / (source_config["id"] + "-invalid.json"), invalid)
            write_json(output / (source_config["id"] + "-inspection.json"), chosen)
            boards(reader, chosen, output / source_config["id"])
            all_selected.extend(chosen)
            print(
                source_config["id"], "selection", len(chosen), "invalid", len(invalid), flush=True
            )
        finally:
            reader.close()
    write_json(output / "inspection-selection.json", all_selected)
    write_json(
        output / "preparation.json",
        {
            "config_sha256": sha256_file(config_path),
            "source_audit_sha256": sha256_file(audit_path),
            "original_shortlist": 40,
            "total_inspection_images": len(all_selected),
            "candidate_model_scores_used": False,
            "test11_media_read": False,
            "new_independent_groups_proven": 0,
            "canonical_assignments_created": False,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    prepare(args.config, args.workspace.resolve())
