"""Prepare immutable owner snapshot and per-anchor visual worksheets (no labels inferred)."""

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = ROOT / "artifacts/reports/E004-crop-bundle-review-20261014"
OUT = ROOT / "outputs" / HERE.name


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


snapshot = HERE / "owner-review-original.md"
if not snapshot.exists():
    snapshot.write_bytes((OLD / "README.md").read_bytes())
assert sha(snapshot) == sha(OLD / "README.md"), "Owner review changed; use new revision"
records = json.loads((OLD / "crop-review-ledger.json").read_text(encoding="utf-8"))
derivatives = json.loads((OLD / "derivatives.json").read_text(encoding="utf-8"))
replacement = {r["original_id"]: r for r in derivatives if r.get("original_id")}
groups = defaultdict(list)
for row in records:
    d = replacement.get(row["sample_id"])
    effective = dict(row)
    if d:
        effective.update({k: d[k] for k in ["crop", "crop_sha256", "context_xyxy", "draft_labels"]})
        effective["candidate_id"] = d["candidate_id"]
        effective["input"] = d["input"]
    else:
        effective["candidate_id"] = row["sample_id"]
        effective["input"] = row["crop"]
    groups[row["anchor_id"]].append(effective)
(OUT / "tracks").mkdir(parents=True, exist_ok=True)
inventory = []
for n, (anchor, rows) in enumerate(groups.items(), 1):
    boards = []
    for start in range(0, len(rows), 24):
        chunk = rows[start : start + 24]
        canvas = Image.new("RGB", (6 * 240, 4 * 260), "white")
        draw = ImageDraw.Draw(canvas)
        for i, row in enumerate(chunk):
            x, y = i % 6 * 240, i // 6 * 260
            with Image.open(ROOT / row["input"]) as im:
                canvas.paste(im.convert("RGB"), (x, y + 30))
            draw.text(
                (x + 2, y + 2),
                f"{row['candidate_id']} f{row['frame_num']} {row['draft_labels']}",
                fill="black",
            )
        path = OUT / "tracks" / f"{n:02}-{start // 24 + 1:02}.jpg"
        canvas.save(path, quality=94)
        boards.append(path.relative_to(ROOT).as_posix())
    inventory.append(
        {
            "anchor_id": anchor,
            "count": len(rows),
            "boards": boards,
            "rows": rows,
            "revision_visual_status": "pending",
        }
    )
dump(HERE / "track-inventory.json", inventory)
dump(
    HERE / "input-pins.json",
    {
        "owner_snapshot_sha256": sha(snapshot),
        "files": {
            str(p.relative_to(ROOT)): sha(p)
            for p in [
                OLD / "crop-review-ledger.json",
                OLD / "derivatives.json",
                OLD / "frame-review-ledger.json",
            ]
        },
    },
)
print(
    json.dumps(
        {
            "tracks": len(inventory),
            "crops": len(records),
            "boards": sum(len(t["boards"]) for t in inventory),
        }
    )
)
