"""Build review-only source/crop/input artifacts from pinned explicit draft geometry."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import PixelBox
from ai_exam_monitoring.data.source_review import PinnedYoloZip, write_pending_crop


def build(
    config_path: Path, geometry_path: Path, geometry_sha: str, output: Path, workspace: Path
) -> None:
    if sha256_file(geometry_path) != geometry_sha:
        raise DataContractError("Draft geometry pin mismatch")
    config = load_yaml(config_path)
    if config["status"] != "authorized_draft_preparation":
        raise DataContractError("Require authorized preparation direction")
    destination = output.resolve()
    if (
        not destination.is_relative_to((workspace / "data/interim").resolve())
        or destination.exists()
    ):
        raise DataContractError("Review batch needs new output under data/interim")
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    if geometry["target_order"] != ["phone_use", "looking_around"]:
        raise DataContractError("Draft target order mismatch")
    if geometry["input_size"] != config["input_size"] or geometry["fill"] != config["fill"]:
        raise DataContractError("Preview preprocessing mismatch")
    proposals = geometry["candidates"]
    if len({r["candidate_id"] for r in proposals}) != len(proposals):
        raise DataContractError("Duplicate draft candidate IDs")
    readers = {}
    rows: list[dict[str, Any]] = []
    font = ImageFont.load_default(size=16)
    try:
        for source in config["sources"]:
            readers[source["id"]] = PinnedYoloZip(
                Path(source["archive"]), source["archive_sha256"], source["names"]
            )
        for draft in proposals:
            if draft["owner_approved"] is not False:
                raise DataContractError("This builder only handles unaccepted drafts")
            source = readers[draft["source_id"]].read(
                draft["member_sha256"], draft["source_sha256"]
            )
            if len(draft["draft_states"]) != 2 or len(config["fill"]) != 3:
                raise DataContractError("Draft states/fill dimensions mismatch")
            states = (draft["draft_states"][0], draft["draft_states"][1])
            row = write_pending_crop(
                source,
                PixelBox(*draft["person_xyxy"]),
                PixelBox(*draft["context_xyxy"]),
                draft["candidate_id"],
                destination,
                states=states,
                reason=draft["reason"],
                input_size=config["input_size"],
                fill=(config["fill"][0], config["fill"][1], config["fill"][2]),
            )
            row.update(
                {
                    k: draft[k]
                    for k in (
                        "source_id",
                        "review_id",
                        "draft_scene_boundary",
                        "role_proposal",
                        "phenotype",
                    )
                }
            )
            row["input224_qa"] = "pending_visual_review"
            row["source_annotations_are_hints_only"] = True
            target = destination / row["candidate_id"]
            annotated = source.image.copy()
            draw = ImageDraw.Draw(annotated)
            draw.rectangle(draft["context_xyxy"], outline=(0, 220, 0), width=3)
            draw.rectangle(draft["person_xyxy"], outline=(255, 0, 0), width=3)
            annotated.thumbnail((700, 450))
            annotated.save(target / "source-overlay.png")
            (target / "proposal.json").write_text(
                json.dumps(row, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                encoding="utf-8",
            )
            rows.append(row)
        for start in range(0, len(rows), 6):
            board = Image.new("RGB", (1600, 1005), "white")
            canvas = ImageDraw.Draw(board)
            for index, row in enumerate(rows[start : start + 6]):
                x, y = (index % 2) * 800, (index // 2) * 335
                target = destination / row["candidate_id"]
                canvas.text(
                    (x + 5, y + 3),
                    row["candidate_id"] + " draft " + "/".join(row["draft_states"]),
                    fill="black",
                    font=font,
                )
                canvas.text((x + 5, y + 24), row["phenotype"], fill="black", font=font)
                for offset, filename, size in [
                    (0, "source-overlay.png", (340, 225)),
                    (345, "crop.png", (225, 225)),
                    (575, "input.png", (224, 224)),
                ]:
                    with Image.open(target / filename) as image:
                        picture = image.convert("RGB")
                        picture.thumbnail(size)
                    board.paste(picture, (x + offset, y + 65))
                canvas.text(
                    (x, y + 292),
                    "source: green context/red anchor | native crop preview | input 224",
                    fill="black",
                    font=font,
                )
            board.save(destination / f"board-{start // 6 + 1:02d}.png")
        cards = []
        for row in rows:
            ident = row["candidate_id"]
            cards.append(
                f'<article id="{ident}"><h2>{ident} — Draft {"/".join(row["draft_states"])}</h2>'
                f"<p>{html.escape(row['draft_scene_boundary'])} · "
                f"{html.escape(row['role_proposal'])} · {html.escape(row['phenotype'])}</p>"
                f'<div><a href="{ident}/source.png"><img class="source" '
                f'src="{ident}/source-overlay.png"></a>'
                f'<a href="{ident}/crop.png"><img src="{ident}/crop.png"></a>'
                f'<img width="224" height="224" src="{ident}/input.png"></div>'
                f"<p>{html.escape(row['draft_reason'])}</p>"
                f'<p><a href="{ident}/proposal.json">Metadata và hashes</a> '
                "· source → crop native → input 224</p></article>"
            )
        content = (
            '<!doctype html><meta charset="utf-8"><title>E004 review batch</title><style>'
            "body{font:16px system-ui;margin:24px;max-width:1400px}"
            "article{border-top:1px solid #ccc;padding:16px 0}"
            "img{max-width:300px;max-height:300px;object-fit:contain;"
            "vertical-align:top;margin:4px}.source{max-width:600px;max-height:400px}"
            "h2{font-size:20px}</style>"
        )
        content += (
            "<h1>E004 — Batch cần owner nghiệm thu</h1><p>Toàn bộ là Draft, canonical targets "
            "null/mask 0, review_only; chưa train/development/test. Target order: phone_use / "
            "looking_around. Khung đỏ: anchor; xanh: context. Bấm ảnh để xem native. "
            "Quyền sử dụng nguồn đã xác nhận; review ở đây tập trung crop/nhãn/group/role.</p>"
        )
        content += (
            "<p>Input QA và exceptions cuối cùng xem trong báo cáo cùng batch; "
            "state hiện trên thẻ là đề xuất trước QA, không phải ground truth.</p>"
            + "\n".join(cards)
        )
        (destination / "review.html").write_text(content, encoding="utf-8")
        (destination / "batch.json").write_text(
            json.dumps(
                {
                    "status": "draft_review_only",
                    "config_sha256": sha256_file(config_path),
                    "geometry_sha256": geometry_sha,
                    "builder_sha256": sha256_file(Path(__file__)),
                    "source_module_sha256": sha256_file(
                        workspace / "src/ai_exam_monitoring/data/source_review.py"
                    ),
                    "candidates": rows,
                    "model_inference_used": False,
                    "test11_media_used": False,
                    "owner_accepted": False,
                    "independent_groups_proven": 0,
                },
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    finally:
        for reader in readers.values():
            reader.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--geometry-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    build(args.config, args.geometry, args.geometry_sha256, args.output, args.workspace.resolve())
