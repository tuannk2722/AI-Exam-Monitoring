"""Prepare immutable owner snapshot and frame review boards for this study."""

import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
ID = REPORT.name
OLD = "E004-crop-bundle-audit-20261014"
OUT = ROOT / "outputs" / ID
OUT.mkdir(parents=True, exist_ok=True)
records = json.loads((ROOT / "data/interim" / OLD / "records.json").read_text())
source = ROOT / "artifacts/reports" / OLD / "README.md"
snapshot = REPORT / "owner-review-original.md"
if not snapshot.exists():
    snapshot.write_bytes(source.read_bytes())
text = snapshot.read_text(encoding="utf-8")
rows = []
for line in text.split("## Kết quả review của onwer", 1)[1].splitlines():
    if not line.startswith("| CB-"):
        continue
    cells = [x.strip() for x in line.strip("|").split("|")]
    ids = []
    for part in cells[0].split(","):
        nums = [int(x) for x in re.findall(r"\d+", part)]
        if "->" in part:
            ids.extend(range(nums[0], nums[1] + 1))
        else:
            ids.extend(nums)
    label = cells[1] if re.fullmatch("[PNU]/[PNU]", cells[1]) else None
    rows.append(
        {
            "row": len(rows) + 1,
            "ids": [f"CB-{i:04}" for i in ids],
            "explicit_labels": label,
            "cells": cells,
            "raw": line,
        }
    )
mapping = {r["sample_id"]: [x["row"] for x in rows if r["sample_id"] in x["ids"]] for r in records}
frames = sorted({r["local_source"] for r in records})
frame_rows = []
for i, path in enumerate(frames):
    frame_rows.append(
        {
            "frame_id": f"F-{i + 1:03}",
            "path": path,
            "crop_ids": [r["sample_id"] for r in records if r["local_source"] == path],
            "board": f"frames/{i // 4 + 1:02}.jpg",
        }
    )
(OUT / "frames").mkdir(exist_ok=True)
for offset in range(0, len(frame_rows), 4):
    board = Image.new("RGB", (1920, 1152), "white")
    draw = ImageDraw.Draw(board)
    for slot, row in enumerate(frame_rows[offset : offset + 4]):
        x, y = (slot % 2) * 960, (slot // 2) * 576
        im = Image.open(ROOT / row["path"]).convert("RGB")
        im.thumbnail((960, 540))
        board.paste(im, (x, y + 36))
        draw.text(
            (x + 5, y + 4),
            row["frame_id"]
            + " "
            + str(Path(row["path"]).parent.name)
            + " "
            + Path(row["path"]).name,
            fill="black",
        )
    board.save(OUT / f"frames/{offset // 4 + 1:02}.jpg", quality=95)
payload = {
    "owner_snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    "rows": rows,
    "mapping": mapping,
    "missing": [k for k, v in mapping.items() if not v],
    "overlap": {k: v for k, v in mapping.items() if len(v) > 1},
    "user_followup": (
        "No additional decisions for missing IDs or malformed label row; inspect and draft."
    ),
    "frames": frame_rows,
}
(REPORT / "review-input.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {
            "frames": len(frames),
            "owner_rows": len(rows),
            "missing": payload["missing"],
            "overlap": payload["overlap"],
        }
    )
)
