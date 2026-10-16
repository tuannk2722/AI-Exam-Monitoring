import json
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path("D:/ai-exam-monitoring-final")
REPORT = ROOT / "artifacts/reports/E004-new-bundle-audit-20261015"
OUT = ROOT / "outputs/E004-new-bundle-audit-20261015/agent-A"
DATA = ROOT / "data/interim/E004-new-bundle-audit-20261015/agent-A"
DATA.mkdir(exist_ok=True)
inventory = json.loads((REPORT / "crop-inventory.json").read_text(encoding="utf-8"))
frames = {
    r["frame_num"]: r
    for r in json.loads((REPORT / "frame-inventory.json").read_text(encoding="utf-8"))
    if r["source_group"] == "A"
}
plans = [
    ("NB-0012-R1", 7, [0, 20, 1290, 1080]),
    ("NB-0018-R1", 10, [0, 0, 1300, 1080]),
    ("NA-001", 2, [825, 170, 1230, 620]),
    ("NA-002", 2, [70, 350, 415, 810]),
    ("NA-003", 14, [240, 220, 1780, 1080]),
    ("NA-004", 22, [810, 0, 1920, 1080]),
    ("NA-005", 24, [0, 0, 1320, 1080]),
    ("NA-006", 24, [770, 0, 1920, 860]),
    ("NA-007", 9, [1350, 0, 1840, 570]),
    ("NA-008", 21, [450, 0, 1920, 1080]),
]
records = []
for ident, num, box in plans:
    src = frames[num]["source"]
    crop = Image.open(ROOT / src).convert("RGB").crop(box)
    cp = DATA / (ident + ".png")
    ip = OUT / (ident + "-input.png")
    crop.save(cp)
    preview_input(crop, 224, (124, 116, 104)).save(ip)
    records.append(
        {
            "id": ident,
            "frame_num": num,
            "source": src,
            "context_xyxy": box,
            "crop": cp.relative_to(ROOT).as_posix(),
            "input": ip.relative_to(ROOT).as_posix(),
        }
    )
board = Image.new("RGB", (1120, 508), "white")
draw = ImageDraw.Draw(board)
for i, r in enumerate(records):
    x = (i % 5) * 224
    y = (i // 5) * 254
    draw.text((x + 2, y + 2), r["id"], fill="black")
    board.paste(Image.open(ROOT / r["input"]), (x, y + 25))
board.save(OUT / "derivatives-board.jpg", quality=95)
(REPORT / "source-A-derivatives.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
