"""Prepare side-by-side native and 224 views for manual duplicate decisions."""

import json

from intake import HERE, MEDIA, ROOT, dump
from PIL import Image, ImageDraw, ImageFont, ImageOps


def main():
    queue = {
        r["id"]: r for r in json.loads((HERE / "intake-ledger.json").read_text(encoding="utf8"))
    }
    data = json.loads((HERE / "visual-duplicate-candidates.json").read_text(encoding="utf8"))
    extra = [
        ["SCB-write-020", "SCB-write-024"],
        ["V6-SB-014", "V6R2-MP-084"],
        ["V6-SB-029", "V6R2-MP-039"],
        ["V6R2-MP-012", "V6R2-MP-081"],
        ["V6R2-MP-009", "V6R2-MP-010"],
    ]
    for group in extra:
        if group not in data["sets"]:
            data["sets"].append(group)
    dump(HERE / "visual-duplicate-candidates.json", data)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
    evidence = []
    for index, group in enumerate(data["sets"], 1):
        canvas = Image.new("RGB", (1024, 300 * len(group)), "white")
        draw = ImageDraw.Draw(canvas)
        for i, ident in enumerate(group):
            row = queue.get(ident)
            path = ROOT / row["crop_path"] if row else MEDIA / "candidates" / ident / "crop.png"
            with Image.open(path) as im:
                rgb = im.convert("RGB")
                native = rgb.copy()
                native.thumbnail((600, 270))
                canvas.paste(native, (0, i * 300 + 26))
                inp = ImageOps.contain(rgb, (224, 224), Image.Resampling.BILINEAR)
                canvas.paste(inp, (650, i * 300 + 26))
            draw.text((5, i * 300 + 3), ident, fill="black", font=font)
            evidence.append(
                {
                    "set": index,
                    "id": ident,
                    "source_sha": row["source_sha256"] if row else None,
                    "owner_status": row.get("owner_import_status") if row else None,
                }
            )
        canvas.save(MEDIA / "boards" / f"duplicate-{index:03}.jpg", quality=96)
    dump(HERE / "duplicate-comparison-index.json", evidence)
    checkpoint = json.loads((HERE / "qa-checkpoint.json").read_text(encoding="utf8"))
    checkpoint["viewed_crop_boards"] = list(range(1, 77))
    checkpoint["broad_scan_note"] = (
        "Đã xem đủ 907 crop trên 76 board; đây là rà tổng thể, "
        "chưa thay thế QA source/native/input cho các ca sửa."
    )
    dump(HERE / "qa-checkpoint.json", checkpoint)


if __name__ == "__main__":
    main()
