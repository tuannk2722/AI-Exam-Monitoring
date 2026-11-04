"""Prepare D2 census review without inferring identity from overlap."""

from __future__ import annotations

import argparse
import csv
import html
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import checksum_artifacts, write_json

from .detector_review import read_object
from .runtime_config import media_deadline


def reviewed_groups(anchors: list[str], relations: list[dict[str, Any]]) -> list[list[str]]:
    universe = set(anchors)
    if len(universe) != len(anchors):
        raise DataContractError("Duplicate anchor")
    groups: list[list[str]] = []
    used: set[str] = set()
    for r in relations:
        members = set(r["anchors"])
        if not members & universe:
            continue
        if len(members) != 2 or not members <= universe:
            raise DataContractError("Invalid cross-frame relation")
        if r["status"] != "owner_confirmed" or r["relation"] != "same_person":
            continue
        if members & used:
            raise DataContractError("Overlapping same groups require explicit reconciliation")
        groups.append(sorted(members))
        used.update(members)
    groups.extend([[a] for a in anchors if a not in used])
    for r in relations:
        if r["status"] == "owner_confirmed" and r["relation"] == "different_person":
            if any(set(r["anchors"]) <= set(g) for g in groups):
                raise DataContractError("Same/different conflict")
    return sorted(groups)


def build(config: Path, workspace: Path, output: Path) -> None:
    workspace, output = workspace.resolve(), output.resolve()
    if output.exists() or not output.is_relative_to(workspace / "outputs"):
        raise DataContractError("Require new census output")
    raw = load_yaml(config)
    if raw.get("schema_version") != "d2-census-build-v1":
        raise DataContractError("Unsupported census config")
    paths = {k: FilePin(**v).verify(workspace) for k, v in raw["pins"].items()}
    cohort = read_object(paths["cohort"])
    media_deadline(cohort)
    rows = read_object(paths["predictions"])["records"]
    relations: list[dict[str, Any]] = sum(
        [read_object(paths[k])["relations"] for k in ("exception_review", "pair_review")], []
    )
    keepers = read_object(paths["keeper_review"])["records"]
    with paths["pair_table"].open(encoding="utf-8", newline="") as handle:
        pairs = [r for r in csv.DictReader(handle) if float(r["iou"]) > 0]
    output.mkdir(parents=True, exist_ok=False)
    frames, sections, nav = [], [], []
    for frame in cohort["frames"]:
        media_deadline(cohort)
        fi = frame["frame_index"]
        selected = {r["anchor_id"]: r for r in rows if r["frame_index"] == fi}
        groups = reviewed_groups(list(selected), relations)
        source = FilePin(**frame["source_png"]).verify(workspace)
        with Image.open(source) as img:
            overlay = img.convert("RGB")
        draw = ImageDraw.Draw(overlay)
        people, entries = [], []
        for i, group in enumerate(groups, 1):
            gid = f"p{i:03d}"
            color = (255, 180, 0) if len(group) > 1 else (0, 255, 255)
            for a in group:
                box = selected[a]["person_box"]
                draw.rectangle(box, outline=color, width=2)
                draw.text(
                    (box[0] + 2, box[1] + 2),
                    f"{gid}/{selected[a]['box_id']}",
                    fill=color,
                    stroke_width=1,
                    stroke_fill="black",
                )
            keeper = next(
                (k["keeper_anchor"] for k in keepers if set(k["anchors"]) == set(group)), None
            )
            people.append(
                {
                    "person_id": gid,
                    "anchors": group,
                    "status": "same_relation_accepted" if len(group) > 1 else "draft_singleton",
                    "keeper_anchor": keeper,
                    "role": "unknown",
                    "location_boxes": [selected[a]["person_box"] for a in group],
                }
            )
            entries.append(
                f"<li>{gid}: {', '.join(a.split('-')[-1] for a in group)}"
                + (f" — same accepted; keeper {keeper}" if keeper else " — draft")
                + "</li>"
            )
        overlay.save(output / f"f{fi:08d}.png")
        related = [r for r in relations if set(r["anchors"]) <= set(selected)]
        unknown_pairs = [
            r
            for r in pairs
            if int(r["frame_index"]) == fi
            and not any(set(t["anchors"]) == {r["anchor_a"], r["anchor_b"]} for t in related)
        ]
        frames.append(
            {
                "frame_index": fi,
                "source_png": frame["source_png"],
                "people": people,
                "accepted_relations": related,
                "overlap_candidates_unknown": unknown_pairs,
                "complete_visible_person_census": False,
                "owner_decision": None,
                "missing_people": None,
                "false_boxes": None,
            }
        )
        rel = html.escape(Path(os.path.relpath(source, output)).as_posix())
        nav.append(f'<a href="#f{fi}">{fi / 30:g}s</a>')
        different = [r["anchors"] for r in related if r["relation"] == "different_person"]
        sections.append(
            f'<section id="f{fi}"><h2>{fi / 30:g} giây — frame {fi}</h2>'
            f"<p>{len(groups)} nhóm draft; không phải số người accepted.</p>"
            f'<a href="{rel}">Mở source gốc</a><br><img src="{rel}">'
            f'<a href="f{fi:08d}.png"><img src="f{fi:08d}.png"></a>'
            f"<details><summary>Nhóm và keeper</summary><ul>{''.join(entries)}</ul></details>"
            f"<p>Quan hệ khác người đã chốt: {html.escape(str(different))}</p>"
            "<p>Review: người có trong source nhưng chưa có nhóm? "
            "Nhóm trùng khác? Box không có người? "
            "Ghi giây + mã p/b hoặc vị trí người thiếu. Chưa rõ giữ pending.</p></section>"
        )
    write_json(
        output / "census-draft.json",
        {
            "schema_version": "d2-census-review-v1",
            "status": "draft",
            "config_sha256": sha256_file(config),
            "pins": raw["pins"],
            "media_delete_by": cohort["media_delete_by"],
            "frames": frames,
        },
    )
    (output / "index.html").write_text(
        '<!doctype html><html lang="vi"><meta charset="utf-8"><title>D2 census review</title>'
        "<style>body{font:17px system-ui;margin:24px}img{max-width:100%}"
        "section{border-top:2px solid #aaa;margin-top:32px}"
        "nav a{margin:8px;display:inline-block}</style>"
        "<h1>Census D2 — Draft</h1><p>Chỉ gộp 4 cặp same đã accepted; giữ 4 different và keeper. "
        "Các nhóm còn lại chưa được xác nhận độc lập; không suy người từ overlap. "
        "Mã p chỉ trong frame. "
        "Mọi người diagnostic, role unknown. Không hỏi lại nhãn hành vi.</p><nav>"
        + " ".join(nav)
        + '</nav><a href="census-draft.json">Manifest/pins</a>'
        + "".join(sections)
        + "</html>",
        encoding="utf-8",
    )
    checksum_artifacts(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    args = parser.parse_args()
    build(args.config, args.workspace, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
