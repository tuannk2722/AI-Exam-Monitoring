"""Local source grids: coordinates refer to a 640-pixel-wide preview."""

import json

from intake import HERE, MEDIA, ROOT
from PIL import Image, ImageDraw
from prepare_review import boards


def main():
    ledger = {
        r["id"]: r
        for r in json.loads((HERE / "consolidated-ledger.json").read_text(encoding="utf-8"))
    }
    ids = [
        "V7-OE-S077-A01",
        "V7-OE-S061-A01",
        "V6R2-EX-010",
        "V7-C-125",
        "SCB-read-015",
        "SCB-write-018",
        "SCB-write-019",
        "SCB-write-023",
        "SCB-write-027",
        "V7-C-004",
        "V7-C-010",
        "V7-OE-S099-A01",
        "V6-SB-003",
        "V7-B-016",
        "V7-B-022",
        "V7-OE-S081-A01",
        "V7-D-005",
        "E004-EX-C172",
        "V7-OE-S093-A01",
        "V7-B-035",
    ]
    out = MEDIA / "coordinate-previews"
    out.mkdir(exist_ok=True)
    rows = []
    for identifier in ids:
        with Image.open(ROOT / ledger[identifier]["source_path"]) as source:
            im = source.convert("RGB").resize((640, round(source.height * 640 / source.width)))
        draw = ImageDraw.Draw(im)
        for x in range(0, 640, 50):
            draw.line((x, 0, x, im.height), fill=(100, 190, 190), width=1)
            draw.text((x + 2, 2), str(x), fill="red", stroke_width=1, stroke_fill="white")
        for y in range(50, im.height, 50):
            draw.line((0, y, 640, y), fill=(100, 190, 190), width=1)
            draw.text((2, y + 2), str(y), fill="red", stroke_width=1, stroke_fill="white")
        path = out / (identifier + ".png")
        im.save(path)
        rows.append({"id": identifier, "path": str(path.relative_to(ROOT))})
    boards(rows, "coordinate-sources", 4, 640, 680)


if __name__ == "__main__":
    main()
