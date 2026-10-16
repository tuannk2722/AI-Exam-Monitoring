"""Render manually proposed anchor/frame geometry for visual QA, never infer labels."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.source_review import preview_input

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "outputs" / HERE.name
DATA = ROOT / "data/interim" / HERE.name


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


plan = json.loads((HERE / "expansion-plan.json").read_text(encoding="utf-8"))
extras = {
    "G5": (
        "2b68c2a8bc91941576a8",
        [
            ("Nữ áo đen sát tường", [80, 160, 330, 410], [1, 97, 109]),
            ("Nữ áo navy đeo kính sát tường", [320, 170, 570, 430], [1, 97, 109]),
            ("Nữ áo kem hàng sau sát tường", [300, 15, 550, 250], [1, 99]),
            ("Nữ áo vàng hàng sau", [520, 70, 740, 290], [1, 97]),
            ("Nữ áo hồng hàng sau", [620, 0, 850, 210], [1, 109]),
            ("Nữ áo trắng sau người áo jersey", [760, 180, 1030, 470], [1, 99, 112]),
            ("Nữ áo đen hàng sau giữa", [1160, 115, 1440, 355], [1, 99, 112]),
            ("Nam áo xanh lá bên phải", [1420, 130, 1680, 430], [1, 99, 109]),
            ("Nam áo đen bàn trước khi camera pan trái", [550, 310, 960, 800], [47, 65]),
            ("Nam polo trắng mép trái khi camera pan trái", [0, 245, 350, 745], [47, 65]),
            ("Nữ áo xám sau người áo đỏ", [620, 65, 880, 340], [47, 65]),
            ("Nam áo đen sau người áo đỏ", [290, 80, 550, 390], [47, 65]),
            ("Nữ áo đỏ hàng cuối khi camera pan trái", [1510, 0, 1720, 170], [47]),
        ],
    ),
    "G4": (
        "9284c725e608c9241824",
        [
            ("Nữ áo xanh nhạt bên trái", [280, 355, 450, 550], [1, 105, 125]),
            ("Nam áo xám bên trái", [220, 275, 375, 475], [1, 105, 125]),
            ("Nữ áo tím giữa bên trái", [500, 225, 645, 395], [1, 105, 125]),
            ("Nam áo navy phía sau giữa", [655, 215, 820, 375], [1, 105, 125]),
            ("Nữ áo tối màu trước nam navy", [630, 315, 815, 490], [1, 105, 125]),
            ("Nữ áo đen đỏ cạnh cửa sổ", [1155, 170, 1325, 345], [1, 105, 125]),
            ("Nam vest bàn đầu bên phải", [1350, 200, 1535, 410], [1, 105, 125]),
            ("Nữ áo nâu bên phải", [1500, 200, 1690, 375], [1, 105, 125]),
        ],
    ),
    "G3": (
        "c4501991dd89a572c461",
        [
            ("Người áo vàng bên trái", [140, 145, 280, 295], [1, 14]),
            ("Người áo vàng đỏ phía sau", [280, 140, 390, 260], [1, 14]),
            ("Người áo be phía sau giữa", [380, 125, 480, 260], [1, 14]),
            ("Người áo xám chữ xanh", [475, 110, 570, 245], [1, 14]),
            ("Người áo đen sọc trắng giữa trái", [310, 190, 440, 340], [1, 3]),
            ("Người áo xanh xám giữa", [440, 195, 560, 330], [1, 3]),
            ("Người áo đen đỏ giữa", [550, 190, 660, 325], [1, 14]),
            ("Người áo đen sát lối đi trái", [155, 265, 315, 390], [1, 21]),
            ("Người áo hồng cạnh cửa sổ", [625, 125, 730, 240], [1, 14]),
            ("Người áo nâu giữa phải", [735, 175, 845, 310], [1, 14]),
        ],
    ),
}
existing = {a["id"] for a in plan["anchors"]}
for group, (parent, specs) in extras.items():
    for n, (desc, box, frames) in enumerate(specs, 1):
        aid = f"{group}-A{n:02}"
        if aid not in existing:
            plan["anchors"].append(
                dict(id=aid, parent=parent, description=desc, box=box, frames=frames)
            )
dump(HERE / "expansion-plan.json", plan)
for sub in [DATA / "crops", OUT / "inputs", OUT / "expansion", OUT / "overlays"]:
    sub.mkdir(parents=True, exist_ok=True)
ledger = []
for anchor in plan["anchors"]:
    board = Image.new("RGB", (len(anchor["frames"]) * 320, 370), "white")
    draw = ImageDraw.Draw(board)
    for j, frame in enumerate(anchor["frames"]):
        cid = f"{anchor['id']}-F{frame:03}"
        source = (
            ROOT
            / "data/interim/E004-crop-bundle-audit-20261014/source/derived"
            / anchor["parent"]
            / f"frame_{frame:05}.jpg"
        )
        with Image.open(source) as im:
            im = im.convert("RGB")
            box = anchor.get("frame_boxes", {}).get(str(frame), anchor["box"])
            x1, y1, x2, y2 = box
            assert 0 <= x1 < x2 <= im.width and 0 <= y1 < y2 <= im.height, (cid, im.size, box)
            crop = im.crop(box)
            cp = DATA / "crops" / f"{cid}.png"
            crop.save(cp)
            inp = preview_input(crop, 224, (124, 116, 104))
            ip = OUT / "inputs" / f"{cid}.png"
            inp.save(ip)
            draw.text((j * 320 + 5, 5), cid, fill="black")
            # Display native crop at most 300 px wide/high, separate from exact model preview.
            shown = crop.copy()
            shown.thumbnail((310, 310))
            board.paste(shown, (j * 320, 30))
            overlay = im.copy()
            ImageDraw.Draw(overlay).rectangle(box, outline="red", width=4)
            op = OUT / "overlays" / f"{cid}.jpg"
            overlay.save(op, quality=92)
        ledger.append(
            dict(
                candidate_id=cid,
                anchor_id=anchor["id"],
                parent_id=anchor["parent"],
                description=anchor["description"],
                frame_num=frame,
                context_xyxy=box,
                source=source.relative_to(ROOT).as_posix(),
                source_sha256=sha(source),
                crop=cp.relative_to(ROOT).as_posix(),
                crop_sha256=sha(cp),
                input=ip.relative_to(ROOT).as_posix(),
                input_sha256=sha(ip),
                overlay=op.relative_to(ROOT).as_posix(),
                draft_labels=None,
                status="pending_visual_qa",
                split=None,
                training_ready=False,
            )
        )
    board.save(OUT / "expansion" / f"{anchor['id']}.jpg", quality=95)
dump(HERE / "expansion-ledger.json", ledger)
print(json.dumps({"anchors": len(plan["anchors"]), "crops": len(ledger)}))
