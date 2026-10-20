"""Prepare local evidence boards and source similarity triage, without labels."""

import json
from collections import defaultdict
from pathlib import Path

from intake import HERE, MEDIA, ROOT, dump, sha
from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.data.image_similarity import difference_hash

FONT = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)


def boards(rows, prefix, per_page=4, width=640, height=390):
    out = MEDIA / "boards"
    out.mkdir(exist_ok=True)
    index = []
    for start in range(0, len(rows), per_page):
        page = rows[start : start + per_page]
        canvas = Image.new("RGB", (width * 2, height * ((per_page + 1) // 2)), "white")
        draw = ImageDraw.Draw(canvas)
        for i, row in enumerate(page):
            x, y = i % 2 * width, i // 2 * height
            with Image.open(ROOT / row["path"]) as im:
                im = im.convert("RGB")
                im.thumbnail((width, height - 26))
                canvas.paste(im, (x, y + 26))
            draw.text((x + 5, y + 3), row["id"], fill="black", font=FONT)
            index.append(
                {
                    "id": row["id"],
                    "board": f"{prefix}-{start // per_page + 1:03}.jpg",
                    "cell": i + 1,
                }
            )
        canvas.save(out / f"{prefix}-{start // per_page + 1:03}.jpg", quality=95)
    dump(HERE / f"{prefix}-boards.json", index)


def main():
    additional = json.loads((HERE / "additional-inventory.json").read_text(encoding="utf-8"))
    boards([{"id": Path(r["path"]).name, "path": r["path"]} for r in additional], "additional")
    queue = json.loads((HERE / "intake-ledger.json").read_text(encoding="utf-8"))
    unique = {}
    source_members = defaultdict(list)
    for r in queue:
        path = ROOT / r["source_path"]
        with Image.open(path) as im:
            rgb = im.convert("RGB")
            key = str(rgb.size) + sha(rgb.tobytes())
            source_members[key].append(r["id"])
            if key not in unique:
                unique[key] = {
                    "path": r["source_path"],
                    "id": r["id"],
                    "rgb_key": key,
                    "dhash": difference_hash(rgb),
                }
    values = list(unique.values())
    matches = []
    for i, a in enumerate(values):
        for b in values[i + 1 :]:
            distance = (a["dhash"] ^ b["dhash"]).bit_count()
            if distance <= 10:
                matches.append(
                    {
                        "a": a["id"],
                        "b": b["id"],
                        "distance": distance,
                        "a_members": source_members[a["rgb_key"]],
                        "b_members": source_members[b["rgb_key"]],
                    }
                )
    dump(
        HERE / "source-similarity.json",
        {
            "same_source": [v for v in source_members.values() if len(v) > 1],
            "near_source_pairs": sorted(matches, key=lambda r: r["distance"]),
            "note": "Triage only: same source does not mean same anchor or duplicate crop.",
        },
    )
    boards(
        [{"id": r["id"], "path": r["crop_path"]} for r in queue],
        "all-crops",
        per_page=12,
        width=410,
        height=310,
    )
    print("source families", len(values), "source pairs", len(matches))


if __name__ == "__main__":
    main()
