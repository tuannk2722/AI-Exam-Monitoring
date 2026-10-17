"""Tạo batch Draft từ geometry quan sát; tái dùng native crop và letterbox hiện hành."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.pilot_schema import PixelBox
from ai_exam_monitoring.data.source_review import SourceImage, member_key, write_pending_crop

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "artifacts/reports/frame-crop-audit-20261016"
DATA = ROOT / "data/interim/frame-crop-audit-20261016"
SCRATCH = DATA / "review/qa"


def build():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    inventory = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    choices = json.loads((REPORT / "selection-draft.json").read_text(encoding="utf-8"))
    lookup = {(r["group"], int(r["frame_id"].split("F")[-1])): r for r in inventory["frames"]}
    rows = []
    for group, detail in choices.items():
        for choice in detail["candidates"]:
            anchor, frame, person, context, states, reason = choice[:6]
            source = lookup[group, frame]
            fid = source["frame_id"]
            cid = f"{group}-{anchor}-F{frame:05}" + (f"-R{choice[6]:02}" if len(choice) > 6 else "")
            folder = DATA / "candidates" / cid
            if folder.exists():
                row = json.loads((folder / "proposal.json").read_text(encoding="utf-8"))
                assert (
                    row["person_xyxy"] == person
                    and row["context_xyxy"] == context
                    and row["draft_states"] == list(states)
                    and row["draft_reason"] == reason
                )
            else:
                blob = (ROOT / source["path"]).read_bytes()
                assert hashlib.sha256(blob).hexdigest() == source["sha256"]
                image = Image.open(ROOT / source["path"]).convert("RGB")
                src = SourceImage(
                    member_key(source["member"]),
                    source["sha256"],
                    "",
                    "unassigned",
                    blob,
                    image,
                    (),
                )
                row = write_pending_crop(
                    src,
                    PixelBox(*person),
                    PixelBox(*context),
                    cid,
                    DATA / "candidates",
                    states=tuple(states),
                    reason=reason,
                    input_size=224,
                    fill=(114, 114, 114),
                )
            row.update(
                {
                    "frame_id": fid,
                    "group": group,
                    "anchor": anchor,
                    "part": source["part"],
                    "source_path": source["path"],
                    "source_archive": inventory["archives"][source["part"] - 1],
                    "source_member": source["member"],
                    "source_annotation_present": False,
                    "review_scope": "Draft thị giác, chưa owner acceptance",
                    "group_note": detail["note"],
                }
            )
            rows.append(row)
    rows.sort(key=lambda r: (r["part"], r["group"], r["anchor"], r["frame_id"]))
    (REPORT / "crop-proposals.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for part in sorted({r["part"] for r in rows}):
        subset = [r for r in rows if r["part"] == part]
        for offset in range(0, len(subset), 6):
            batch = subset[offset : offset + 6]
            canvas = Image.new("RGB", (1500, 360 * ((len(batch) + 2) // 3)), "#dedede")
            draw = ImageDraw.Draw(canvas)
            for j, r in enumerate(batch):
                x, y = (j % 3) * 500, (j // 3) * 360
                crop = Image.open(DATA / "candidates" / r["candidate_id"] / "crop.png")
                crop.thumbnail((270, 320))
                canvas.paste(crop, (x, y + 30))
                canvas.paste(
                    Image.open(DATA / "candidates" / r["candidate_id"] / "input.png"),
                    (x + 274, y + 30),
                )
                draw.text(
                    (x + 4, y + 5),
                    r["candidate_id"] + " " + "".join(r["draft_states"]),
                    fill="black",
                )
            canvas.save(SCRATCH / f"P{part:02}-cropQA-{offset // 6 + 1:02}.jpg", quality=96)
    print(f"{len(rows)} crops prepared")


if __name__ == "__main__":
    build()
