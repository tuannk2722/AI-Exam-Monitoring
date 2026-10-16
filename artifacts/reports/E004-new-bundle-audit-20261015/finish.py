"""Task worksheet: manual geometry proposals and reproducible review artifacts."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ID = HERE.name
OUT = ROOT / "outputs" / ID
DER = ROOT / "data/interim" / ID / "root-B"


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def write(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


# Exact source rectangles, not person bounding boxes. Final labels follow input review.
RECROPS = {
    34: ([475, 275, 540, 383], "N/P"),
    35: ([585, 275, 681, 372], "U/P"),
    36: ([770, 312, 857, 436], "U/P"),
    37: ([120, 215, 252, 345], "N/N"),
    38: ([210, 210, 338, 352], "N/U"),
    41: ([325, 310, 555, 520], "N/P"),
    54: ([300, 300, 389, 405], "N/N"),
    62: ([850, 277, 944, 406], "N/N"),
    69: ([540, 250, 787, 489], "N/P"),
    77: ([1080, 185, 1210, 306], "U/N"),
    79: ([565, 150, 650, 305], "U/P"),
}
ADDITIONS = [
    (
        "NBX-001",
        2,
        [870, 375, 975, 555],
        "N/N",
        "Người áo đen phía trước bên phải, tay chống trán và tay viết",
    ),
    (
        "NBX-002",
        2,
        [397, 263, 495, 373],
        "U/U",
        "Người áo xám hàng cuối sát tường; tay khuất, góc đầu chưa đủ rõ để phân biệt hướng bài hay ngoài bài",
    ),
    (
        "NBX-003",
        6,
        [487, 148, 585, 277],
        "N/N",
        "Người áo đen giữa phía sau, tay chống đầu và tay viết",
    ),
    (
        "NBX-004",
        133,
        [680, 195, 802, 324],
        "N/N",
        "Người áo trắng sau cặp nam giữa lớp, hai tay quanh giấy",
    ),
    (
        "NBX-005",
        7,
        [794, 264, 878, 366],
        "N/N",
        "Người phía sau giữa, tay chống trán và tay trên giấy",
    ),
    (
        "NBX-006",
        14,
        [449, 157, 549, 272],
        "U/N",
        "Người áo xám phía sau bên trái, tay khuất một phần, cúi vùng bài",
    ),
    (
        "NBX-007",
        127,
        [986, 302, 1141, 514],
        "U/P",
        "Người áo xanh sau người tiền cảnh bên phải; một tay khuất và mặt bị người trước che, không chọn vì attribution yếu",
    ),
    (
        "NBX-008",
        133,
        [613, 127, 705, 223],
        "N/P",
        "Người áo xanh hàng cuối giữa, hai tay ở bàn, đầu ngẩng khỏi giấy",
    ),
]


def main():
    assert not (HERE / "result-pins.json").exists(), "Sealed audit"
    inventory = read("crop-inventory.json")
    frames = read("frame-inventory.json")
    by_id = {r["id"]: r for r in inventory}
    by_frame = {r["frame_num"]: r for r in frames if r["source_group"] == "B"}
    b_rows = []
    for line in (HERE / "source-B-manual.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        num, labels, reason = line.split("|", 2)
        num = int(num)
        row = dict(by_id[f"NB-{num:04d}"])
        row.update(
            draft_labels=labels,
            phone_reason=reason,
            looking_reason="Xem nhận xét chung cùng dòng.",
            status="draft_visual_review",
            disposition="recrop"
            if num in RECROPS
            else ("withheld_uu" if labels == "U/U" else "keep"),
            visual_evidence=[
                "supplied_224",
                "same_frame_native_context",
                "source_B_agent_overview",
            ],
        )
        b_rows.append(row)
    assert len(b_rows) == 58
    DER.mkdir(parents=True, exist_ok=True)
    previews = OUT / "root-B"
    previews.mkdir(exist_ok=True)
    derivative_rows = []
    specs = []
    for num, (box, labels) in RECROPS.items():
        original = by_id[f"NB-{num:04d}"]
        specs.append(
            (
                original["id"] + "-R1",
                original["frame_num"],
                box,
                labels,
                "Sửa khung của "
                + original["id"]
                + ": ưu tiên đúng anchor, đủ đầu và vùng tay hữu ích.",
                original["id"],
                original["anchor_id"],
            )
        )
    for ident, frame, box, labels, desc in ADDITIONS:
        specs.append((ident, frame, box, labels, desc, None, ident))
    for ident, frame, box, labels, desc, replaces, anchor in specs:
        source = by_frame[frame]
        with Image.open(ROOT / source["source"]) as image:
            image = image.convert("RGB")
            x1, y1, x2, y2 = box
            assert 0 <= x1 < x2 <= image.width and 0 <= y1 < y2 <= image.height
            crop = image.crop(box)
        native = DER / f"{ident}.png"
        crop.save(native)
        inp = previews / f"{ident}-input.png"
        preview_input(crop, 224, (124, 116, 104)).save(inp)
        derivative_rows.append(
            {
                "id": ident,
                "frame_num": frame,
                "source_group": "B",
                "source": source["source"],
                "source_sha256": source["source_sha256"],
                "crop": rel(native),
                "crop_sha256": sha(native),
                "input": rel(inp),
                "input_sha256": sha(inp),
                "context_xyxy": box,
                "anchor_id": anchor,
                "anchor_description": desc,
                "replaces": replaces,
                "draft_labels": labels,
                "phone_reason": desc,
                "looking_reason": "Nhãn đề xuất từ input 224; xem source khi kiểm attribution.",
                "disposition": "keep",
                "status": "draft_visual_review",
                "training_ready": False,
                "assigned_split": None,
            }
        )
    for start in range(0, len(derivative_rows), 10):
        group = derivative_rows[start : start + 10]
        board = Image.new("RGB", (1120, 520), "white")
        draw = ImageDraw.Draw(board)
        for i, row in enumerate(group):
            x, y = (i % 5) * 224, (i // 5) * 260
            draw.text((x + 3, y + 3), row["id"] + " " + row["draft_labels"], fill="black")
            with Image.open(ROOT / row["input"]) as image:
                board.paste(image, (x, y + 30))
        board.save(previews / f"board-{start // 10 + 1:02d}.jpg")
    write(
        "source-B-review.json",
        {
            "status": "draft_root_integration",
            "supplied_reviews": b_rows,
            "derivative_reviews": derivative_rows,
            "coverage": {
                "supplied_224_root": 58,
                "native_context_root": 58,
                "full_frames_native_root": [2, 6, 7, 14, 127, 133, 270, 332],
                "source_overview_agent_reported": 111,
                "note": "Agent B báo đã xem 111/111 overview trước khi ngắt do quota; không có ledger per-frame của agent B. Root kiểm lại toàn bộ crop/native và các frame sửa/bổ sung.",
            },
        },
    )
    print(f"B: {len(b_rows)} supplied; {len(derivative_rows)} derivatives")


if __name__ == "__main__":
    main()
