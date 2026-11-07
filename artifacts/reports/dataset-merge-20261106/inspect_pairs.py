"""Generate local pair boards from pinned intake; no automatic deduplication."""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
SCRATCH = ROOT / "outputs/_scratch/dataset-merge-20261106"


def main():
    inv = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    sim = json.loads((REPORT / "similarity-triage.json").read_text(encoding="utf-8"))
    new = inv["imports"] + inv["native_included"]
    lookup = {r["id"]: r for r in new + inv["parent"]}
    arrays = []
    for row in new:
        with Image.open(ROOT / row["path"]) as im:
            arrays.append(np.asarray(im.convert("RGB").resize((48, 48)), dtype=np.float32).reshape(-1))
    a = np.stack(arrays)
    a -= a.mean(axis=1, keepdims=True)
    a /= np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-8)
    correlations = a @ a.T
    pairs = {}
    for i, row in enumerate(new):
        for j in range(i + 1, len(new)):
            dh = (row["dhash"] ^ new[j]["dhash"]).bit_count()
            corr = float(correlations[i, j])
            if dh <= 10 or corr >= .94:
                pairs[tuple(sorted((row["id"], new[j]["id"])))] = {
                    "dhash": dh, "rgb_correlation_48": corr,
                }
    pairs_list = [{"ids": list(k), **v} for k, v in sorted(pairs.items())]
    (REPORT / "new-pair-triage.json").write_text(
        json.dumps(pairs_list, indent=2) + "\n", encoding="utf-8")
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 14)

    def board(entries, prefix, count=8):
        for start in range(0, len(entries), count):
            subset = entries[start:start + count]
            sheet = Image.new("RGB", (1056, count * 212), "#eeeeee")
            draw = ImageDraw.Draw(sheet)
            for i, (ids, title) in enumerate(subset):
                for j, sid in enumerate(ids):
                    row = lookup[sid]
                    x, y = j * 176, i * 212
                    with Image.open(ROOT / row["path"]) as im:
                        sheet.paste(preview_input(im.convert("RGB"), 168, (124, 116, 104)), (x + 4, y))
                    label = row.get("owner_label", row.get("split", ""))
                    draw.text((x + 3, y + 170), sid + " " + label, fill="black", font=font)
                draw.text((4, i * 212 + 191), title, fill="black", font=font)
            sheet.save(SCRATCH / f"{prefix}-{start // count + 1:02d}.jpg", quality=95)

    board([(p["ids"], f'dHash={p["dhash"]} corr={p["rgb_correlation_48"]:.3f}')
           for p in pairs_list], "duplicates", 8)
    board([([r["id"]] + [c["id"] for c in r["nearest"] if c["kind"] == "parent"],
            "Parent dHash: " + str([c["distance"] for c in r["nearest"] if c["kind"] == "parent"]))
           for r in sim], "parent-nearest", 8)
    print(json.dumps({"new_pairs": len(pairs_list), "parent_queries": len(sim)}))


if __name__ == "__main__":
    main()
