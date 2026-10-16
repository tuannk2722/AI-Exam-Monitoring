"""Contact sheets for exact inputs and source detail comparisons."""

import json
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "outputs" / HERE.name / "qa"
OUT.mkdir(parents=True, exist_ok=True)
rows = json.loads((HERE / "expansion-ledger.json").read_text(encoding="utf8"))
for start in range(0, len(rows), 18):
    canvas = Image.new("RGB", (1440, 780), "white")
    d = ImageDraw.Draw(canvas)
    for i, r in enumerate(rows[start : start + 18]):
        x, y = i % 6 * 240, i // 6 * 260
        d.text((x + 2, y + 2), r["candidate_id"], fill="black")
        with Image.open(ROOT / r["input"]) as im:
            canvas.paste(im, (x, y + 26))
    canvas.save(OUT / f"new-{start // 18 + 1:02}.png")
tracks = json.loads((HERE / "track-inventory.json").read_text(encoding="utf8"))
selected = [
    1,
    6,
    8,
    9,
    12,
    14,
    16,
    17,
    24,
    26,
    43,
    46,
    55,
    57,
    59,
    62,
    65,
    74,
    97,
    98,
    103,
    111,
    224,
    228,
    238,
]
byid = {int(r["sample_id"].split("-")[1]): r for t in tracks for r in t["rows"]}
for start in range(0, len(selected), 6):
    canvas = Image.new("RGB", (1500, 1000), "white")
    d = ImageDraw.Draw(canvas)
    for i, k in enumerate(selected[start : start + 6]):
        r = byid[k]
        x, y = i % 3 * 500, i // 3 * 500
        with Image.open(ROOT / r["source"]) as src:
            im = src.convert("RGB").crop(r["context_xyxy"])
        im.thumbnail((490, 450))
        canvas.paste(im, (x, y + 30))
        d.text((x + 3, y + 4), r["candidate_id"], fill="black")
    canvas.save(OUT / f"detail-{start // 6 + 1:02}.png")
print("8 new-input boards and 5 source-detail boards")
