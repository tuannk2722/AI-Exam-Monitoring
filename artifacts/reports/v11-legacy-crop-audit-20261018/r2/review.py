"""R2 worksheet: fresh source/native/input boards, preserving all R1 evidence."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import preview_input

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
ROOT = HERE.parents[3]
PACKAGE = ROOT / "data/processed/pilot-b/pilot-b-20261017-v11"
REVIEW = ROOT / "data/interim/v11-legacy-crop-audit-20261018-r2"
R1_MEDIA = ROOT / "data/interim/v11-legacy-crop-audit-20261018"


def main():
    rows = json.loads((PARENT / "cohort.json").read_text(encoding="utf-8"))
    assert len(rows) == 836
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / "boards").mkdir(exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
    index = []
    for start in range(0, len(rows), 6):
        group = rows[start : start + 6]
        name = f"r2-{start // 6 + 1:03d}.jpg"
        board = Image.new("RGB", (1680, 1380), "#eeeeee")
        draw = ImageDraw.Draw(board)
        for i, row in enumerate(group):
            sid = row["sample_id"]
            x, y = i % 2 * 840, i // 2 * 460
            draw.rectangle((x, y, x + 838, y + 458), fill="white", outline="black")
            draw.text((x + 5, y + 5), f"{i + 1:02d}  {sid}", font=font, fill="black")
            with Image.open(R1_MEDIA / "source" / f"{sid}.jpg") as source:
                source = source.convert("RGB")
                source.thumbnail((285, 380), Image.Resampling.BILINEAR)
                board.paste(
                    source, (x + (290 - source.width) // 2, y + 35 + (380 - source.height) // 2)
                )
            path = PACKAGE / row["crop"]["crop_relpath"]
            assert sha256_file(path) == row["crop"]["crop_sha256"]
            with Image.open(path) as crop:
                crop = crop.convert("RGB")
                scale = min(300 / crop.width, 380 / crop.height)
                shown = crop.resize(
                    (round(crop.width * scale), round(crop.height * scale)),
                    Image.Resampling.BILINEAR,
                )
                board.paste(
                    shown, (x + 292 + (300 - shown.width) // 2, y + 35 + (380 - shown.height) // 2)
                )
                inp = preview_input(crop, 224, (124, 116, 104))
                assert hashlib.sha256(inp.tobytes()).hexdigest() == row["input_rgb_sha256"]
                board.paste(inp, (x + 610, y + 112))
            draw.text(
                (x + 5, y + 433),
                "source: green person / orange context | native | exact 224",
                font=small,
                fill="black",
            )
            index.append({"sample_id": sid, "board": name, "cell": i + 1})
        board.save(REVIEW / "boards" / name, quality=96, subsampling=0)
    pins = {p.name: sha256_file(p) for p in PARENT.iterdir() if p.is_file()}
    for name, data in [("review-index.json", index), ("parent-pins.json", pins)]:
        (HERE / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Fresh R2 boards: {(len(rows) + 5) // 6}; crops: {len(rows)}")


if __name__ == "__main__":
    main()
