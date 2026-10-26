"""Draft detector-to-person associations for owner review, never accepted IoU identity."""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import checksum_artifacts, write_json

from .detector_review import read_object
from .pair_geometry import overlap
from .runtime_config import media_deadline


def rank_people(box: list[float], people: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for person in people:
        score = max(overlap(box, b)["iou"] for b in person["location_boxes"])
        if score > 0:
            ranked.append({"person_id": person["person_id"], "iou_hint": score})
    return sorted(ranked, key=lambda r: (-r["iou_hint"], r["person_id"]))


def build(config: Path, workspace: Path, output: Path) -> None:
    workspace, output = workspace.resolve(), output.resolve()
    if output.exists() or not output.is_relative_to(workspace / "outputs"):
        raise DataContractError("New review output required")
    raw = load_yaml(config)
    paths = {k: FilePin(**v).verify(workspace) for k, v in raw["pins"].items()}
    run = read_object(paths["run"])
    media_deadline(run)
    if run["status"] != "completed":
        raise DataContractError("Comparison not complete")
    checks = read_object(paths["checksums"])
    for k in ("run", "detections", "census"):
        if checks[paths[k].name] != raw["pins"][k]["sha256"]:
            raise DataContractError("Comparison checksum mismatch")
    census = read_object(paths["census"])
    frames = read_object(paths["detections"])["frames"]
    output.mkdir(parents=True, exist_ok=False)
    sections = []
    records = []
    navigation = []
    for frame in frames:
        media_deadline(run)
        fi, arm = frame["frame_index"], frame["arm"]
        people = next(f["people"] for f in census["frames"] if f["frame_index"] == fi)
        source = FilePin(**frame["source"]).verify(workspace)
        with Image.open(source) as src:
            image = src.convert("RGB")
        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)
        rows = []
        mapped = set()
        entries = []
        for box in frame["boxes"]:
            ranked = rank_people(box["xyxy_float"], people)
            proposed = ranked[0]["person_id"] if ranked else None
            if proposed:
                mapped.add(proposed)
            ident = box["anchor_id"]
            short = ident.split("-")[-1]
            draw.rectangle(box["person_box"], outline="cyan", width=2)
            draw.text(
                tuple(box["person_box"][:2]),
                f"{short}->{proposed or '?'}",
                fill="cyan",
                stroke_width=1,
                stroke_fill="black",
            )
            crop_name = f"{ident}-crop.png"
            image.crop(box["context_box"]).save(output / crop_name)
            row = {
                **box,
                "ranked_candidates": ranked,
                "proposed_person_id": proposed,
                "accepted_person_id": None,
                "status": "draft",
                "crop_review": "pending",
            }
            rows.append(row)
            entries.append(
                f'<li>{short} → {proposed}; <a href="{crop_name}">context crop</a>'
                f'<details><summary>Crop và các nhóm giao nhau</summary><img src="{crop_name}">'
                f"<pre>{html.escape(str(ranked))}</pre></details></li>"
            )
        uncovered = [p["person_id"] for p in people if p["person_id"] not in mapped]
        reference = image.copy()
        refdraw = ImageDraw.Draw(reference)
        for p in people:
            for b in p["location_boxes"]:
                refdraw.rectangle(b, outline="orange", width=2)
                refdraw.text(
                    tuple(b[:2]), p["person_id"], fill="orange", stroke_width=1, stroke_fill="black"
                )
        refname = f"{arm}-f{fi:08d}-reference.png"
        reference.save(output / refname)
        name = f"{arm}-f{fi:08d}-mapping.png"
        overlay.save(output / name)
        section = f"{arm}-f{fi}"
        navigation.append(f'<a href="#{section}">{arm}/{fi / 30:g}s</a>')
        link = html.escape(Path(os.path.relpath(source, output)).as_posix())
        sections.append(
            f'<section id="{section}"><h2>{arm} — {fi / 30:g} giây</h2>'
            f"<p>Chưa có box đề xuất tới: {uncovered}. Chỉ shortlist, chưa xác nhận miss.</p>"
            f'<a href="{link}">Source</a><h3>Census accepted (cam)</h3><img src="{refname}">'
            f'<h3>Mapping draft (cyan)</h3><img src="{name}">'
            "<details><summary>Box → người và context crops</summary><ul>"
            + "".join(entries)
            + "</ul></details></section>"
        )
        records.append(
            {
                "frame_index": fi,
                "arm": arm,
                "boxes": rows,
                "draft_uncovered": uncovered,
                "status": "draft",
                "complete_owner_matching": False,
            }
        )
    write_json(
        output / "matching-draft.json",
        {
            "status": "draft",
            "pins": raw["pins"],
            "media_delete_by": run["media_delete_by"],
            "frames": records,
            "winner": None,
        },
    )
    (output / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Matching review</title>'
        "<style>body{font:17px system-ui;margin:24px}img{max-width:100%}"
        "nav a{display:inline-block;margin:8px}"
        "section{border-top:2px solid #aaa;margin-top:30px}</style>"
        "<h1>Review matching V8S/V10S — Draft</h1>"
        "<p>p là mã census trong frame; b là box của model. "
        "Đề xuất bằng overlap chỉ để shortlist, không là ground truth. Xem source và người thật; "
        "chỉnh p nếu sai hoặc ghi box giả/chưa rõ. "
        "Nhóm chưa có box: xác nhận miss hoặc chỉ box đúng. "
        "Context crop: đánh dấu thiếu evidence/sai anchor nếu có. Không có inference G0.</p><nav>"
        + " ".join(navigation)
        + '</nav><a href="matching-draft.json">Manifest</a>'
        + "".join(sections),
        encoding="utf-8",
    )
    checksum_artifacts(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for k in ("config", "output"):
        parser.add_argument("--" + k, type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    args = parser.parse_args()
    build(args.config, args.workspace, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
