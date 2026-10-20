"""Render manually selected geometry for visual QA using the existing input helper."""

import json
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
DATA = ROOT / "data/interim/youtube-frame-audit-20261018"


def main():
    rows = json.loads((REPORT / "selections.json").read_text(encoding="utf-8"))
    inv = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    frames = {r["frame_id"]: r for r in inv["frames"]}
    for group in inv["groups"]:
        selected = [r for r in rows if r["group"] == group["group"]]
        for start in range(0, len(selected), 8):
            page = selected[start : start + 8]
            board = Image.new("RGB", (1280, 535 * ((len(page) + 3) // 4)), "#e9e9e9")
            draw = ImageDraw.Draw(board)
            for i, row in enumerate(page):
                im = Image.open(ROOT / frames[row["frame_id"]]["source_path"]).convert("RGB")
                crop = im.crop(row["context_xyxy"])
                inp = preview_input(crop, 224, (114, 114, 114))
                dest = DATA / "trials" / row["candidate_id"]
                dest.mkdir(parents=True, exist_ok=True)
                crop.save(dest / "crop.png")
                inp.save(dest / "input.png")
                x, y = i % 4 * 320, i // 4 * 535
                draw.text(
                    (x + 6, y + 4),
                    row["candidate_id"] + " " + "/".join(row["draft_states"]),
                    fill="black",
                )
                draw.text(
                    (x + 6, y + 21),
                    f"Native {crop.width}x{crop.height}; below input224",
                    fill="black",
                )
                crop.thumbnail((306, 255))
                board.paste(crop, (x + 7, y + 40))
                board.paste(inp, (x + 45, y + 302))
            board.save(DATA / "boards" / f"{group['group']}-qa-{start // 8 + 1:02}.png")
    print(f"Rendered {len(rows)} trials")


if __name__ == "__main__":
    main()
