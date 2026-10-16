"""Versioned owner closure and requested source crops; no training release mutation."""

import hashlib
import html
import json
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "E004-new-bundle-audit-20261015"
OUT = ROOT / "outputs" / HERE.name
DATA = ROOT / "data/interim" / HERE.name
SOURCE = (
    ROOT
    / "data/interim/E004-new-bundle-audit-20261015/new-yt-videos-run-001-accepted-frames/derived/17e642e8e71392e7c926"
)

RESOLUTIONS = {
    "NB-0013": (
        "N/N",
        "Owner chốt N/N cho mẫu này sau xem ảnh rõ. Ghi nhận adjudication riêng về tay che; không suy rằng ảnh nét luôn đủ absence hoặc áp N cho mọi tay khuất.",
    ),
    "NB-0015": (
        "N/N",
        "Owner áp cùng quyết định với NB-0013. Đây là quyết định nhãn cụ thể của owner, không mở rộng ngoại lệ tay khuất cho toàn dataset.",
    ),
    "NB-0030": (
        "N/N",
        "Giữ N/N: tay viết và tay giữ giấy còn quan sát được dù ít nét. Độ nét không thay thế visibility; không lấy mẫu này để tự gán N mọi bàn tay bị che.",
    ),
    "NB-0032": (
        "N/P",
        "Theo owner, đầu ngẩng và tay giơ ở trước mặt ngoài vùng bài. Đối chiếu NB-0048 N/P; khác NB-0080 N/N nhìn tờ bài đang cầm. Không đặt quy tắc mọi vật giơ lên đều P.",
    ),
    "NB-0063": (
        "U/N",
        "Looking N theo owner: hướng về giấy riêng. Source cho thấy tay không có thiết bị, nhưng input hiện tại cắt bàn tay bên trái nên phone U; không truyền evidence ngoài input vào nhãn N.",
    ),
    "NB-0067": (
        "N/P",
        "Anchor là người áo xanh tiền cảnh. Theo owner và xem lại gáy/hướng đầu, đang quay sang bên cạnh; hai tay không có thiết bị mơ hồ.",
    ),
    "NB-0034-R1": (
        "N/N",
        "Chốt looking N theo adjudication owner về vùng nhìn riêng; bỏ kết luận P quá mạnh từ hướng nghiêng ở ảnh nhỏ. Không tuyên bố nhìn thấy mắt rõ.",
    ),
    "NB-0041-R1": (
        "N/N",
        "Theo owner: góc quay chưa ra khỏi vùng bài riêng, chốt N/N; không dùng việc đầu hơi xoay để tự gán P.",
    ),
    "NBX-004": ("U/N", "Theo owner: bàn và một tay bị che, phone U; nhìn bài N."),
    "NBX-005": ("U/N", "Theo owner: bàn và một tay bị che, phone U; nhìn bài N."),
}

# One entry per circled position; frame 21 is already represented by accepted NA-008.
SPECS = [
    (
        "NC-001",
        9,
        "Người áo xanh hàng sau bên trái",
        [590, 10, 1060, 420],
        "U/N",
        "Vật trắng trong tay chỉ lộ cạnh/lưng, chưa phân biệt thiết bị; đầu hướng vật/giấy riêng.",
    ),
    (
        "NC-002",
        19,
        "Người tóc dài tiền cảnh bên trái",
        [0, 175, 810, 1080],
        "N/N",
        "Calculator hồng có phím và màn nhỏ rõ; tay còn lại cầm bút, đầu nhìn bài riêng.",
    ),
    (
        "NC-003",
        16,
        "Người đeo kính bên trái",
        [335, 60, 735, 520],
        "U/N",
        "Thiết bị trong tay lộ cạnh/lưng, không lấy thông tin frame 3 để phân loại; nhìn vùng riêng.",
    ),
    (
        "NC-004",
        16,
        "Người áo xanh giữa phía trước",
        [620, 0, 1240, 700],
        "N/N",
        "Hai tay viết/giữ giấy, không có vật mơ hồ của anchor; đầu cúi bài.",
    ),
    (
        "NC-005",
        14,
        "Người áo xanh tiền cảnh trái",
        [0, 100, 650, 870],
        "N/N",
        "Tay viết và tay nâng gần mặt không có thiết bị; đầu cúi giấy riêng. Không lấy vật trên bàn người tiền cảnh phải làm phone của anchor.",
    ),
    (
        "NC-006",
        14,
        "Người đeo kính ở giữa",
        [620, 0, 1150, 560],
        "N/N",
        "Hai tay quanh giấy và calculator có keypad; mặt hướng bài riêng.",
    ),
    (
        "NC-007",
        13,
        "Người tóc dài hàng giữa phía trái",
        [305, 190, 600, 440],
        "N/N",
        "Tay viết và tay giữ giấy rõ; đầu cúi vào bài.",
    ),
    (
        "NC-008",
        13,
        "Người áo xanh đeo kính giữa phải",
        [975, 205, 1225, 438],
        "N/N",
        "Hai tay quanh giấy, không có thiết bị mơ hồ; mặt hướng bài riêng.",
    ),
    (
        "NC-009",
        13,
        "Người khoác trắng xanh sau bên phải",
        [1175, 160, 1425, 400],
        "N/N",
        "Kiểm native và input: tay cầm bút ở trước, tay còn lại đặt trên bài đều thấy, không có thiết bị mơ hồ; đầu hướng bài riêng.",
    ),
    (
        "NC-010",
        13,
        "Người áo xanh phía trước bên phải",
        [1385, 235, 1655, 590],
        "U/N",
        "Tay bị người nam tiền cảnh che một phần; đầu hướng giấy riêng.",
    ),
    (
        "NC-011",
        13,
        "Người đeo kính chống trán phía phải",
        [1560, 215, 1755, 480],
        "N/N",
        "Tay tựa trán và tay trên bài; không thấy thiết bị mơ hồ, hướng đầu vào bài.",
    ),
    (
        "NC-012",
        3,
        "Người đeo kính bên trái",
        [350, 65, 755, 530],
        "N/N",
        "Mặt calculator có hàng phím còn thấy trong crop, hai tay quanh máy; nhìn thiết bị riêng.",
    ),
    (
        "NC-013",
        2,
        "Người đeo kính phía phải",
        [1360, 470, 1920, 985],
        "U/N",
        "Vật trong tay chỉ thấy lưng/cạnh, thiếu đặc trưng loại thiết bị; đầu hướng vật/bài riêng.",
    ),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p):
    return p.relative_to(ROOT).as_posix()


def write(name, value):
    (HERE / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    assert not (HERE / "result-pins.json").exists(), "Sealed result"
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    old_pins = json.loads((OLD / "result-pins.json").read_text(encoding="utf-8"))
    for p, digest in old_pins["files"].items():
        assert sha(ROOT / p) == digest, p
    closure_path = HERE / "closure-receipt.json"
    if not closure_path.exists():
        shutil.copyfile(OLD / "owner-review.md", HERE / "owner-review-input.md")
        rows = json.loads((OLD / "candidate-ledger.json").read_text(encoding="utf-8"))
        closed = []
        changes = []
        for row in rows:
            if not row["selected"]:
                continue
            before = row["draft_labels"]
            labels, reason = RESOLUTIONS.get(
                row["id"], (before, "Owner approve các crop không nhận xét.")
            )
            row.update(
                final_labels=labels,
                closure_reason=reason,
                status="finalized_labels_and_existing_crop",
                approval_basis="owner_specific_review"
                if row["id"] in RESOLUTIONS
                else "owner_approval_unmentioned",
                training_ready=False,
            )
            if labels != before:
                changes.append(
                    {"id": row["id"], "before": before, "after": labels, "reason": reason}
                )
            for field in ("source", "crop", "input"):
                assert sha(ROOT / row[field]) == row[field + "_sha256"]
            closed.append(row)
        assert len(closed) == 92 and len(changes) == 9
        write("closed-ledger.json", closed)
        write("label-deltas.json", changes)
        write(
            "closure-receipt.json",
            {
                "schema": "research-crop-batch-closure-v1",
                "date": "2026-10-16",
                "scope": "92 shortlist crops: labels and existing crop only; not canonical release/train acceptance",
                "retained": 92,
                "label_changes": 9,
                "explicit_review_rows": 10,
                "unmentioned_approved": 82,
                "label_counts": dict(Counter(r["final_labels"] for r in closed)),
                "files": {
                    rel(p): sha(p)
                    for p in [
                        HERE / "closed-ledger.json",
                        HERE / "owner-review-input.md",
                        HERE / "label-deltas.json",
                        OLD / "result-pins.json",
                    ]
                },
            },
        )
    closed = json.loads((HERE / "closed-ledger.json").read_text(encoding="utf-8"))
    rows = []
    mapping = []
    for ident, frame, description, box, labels, reason in SPECS:
        source = SOURCE / f"frame_{frame:05d}.jpg"
        with Image.open(source) as im:
            assert 0 <= box[0] < box[2] <= im.width and 0 <= box[1] < box[3] <= im.height
            native = im.convert("RGB").crop(box)
        crop = DATA / f"{ident}.png"
        native.save(crop)
        inp = OUT / f"{ident}-input.png"
        preview_input(native, 224, (124, 116, 104)).save(inp)
        rows.append(
            {
                "id": ident,
                "frame_num": frame,
                "anchor_description": description,
                "source": rel(source),
                "source_sha256": sha(source),
                "crop": rel(crop),
                "crop_sha256": sha(crop),
                "input": rel(inp),
                "input_sha256": sha(inp),
                "context_xyxy": box,
                "draft_labels": labels,
                "reason": reason,
                "status": "draft_owner_review_required",
                "training_ready": False,
                "assigned_split": None,
                "canonical_targets": [None, None],
                "canonical_mask": [0, 0],
            }
        )
        mapping.append(
            {
                "marked_image": f"1frame_{frame:05d}.jpg",
                "anchor": description,
                "result": ident,
                "action": "new_crop",
            }
        )
    mapping.append(
        {
            "marked_image": "1frame_00021.jpg",
            "anchor": "Người đeo kính phía trước với calculator hồng",
            "result": "NA-008",
            "action": "already_in_closed_batch_same_frame_and_anchor",
        }
    )
    write("additions-ledger.json", rows)
    write("marked-anchor-map.json", mapping)
    refs = DATA / "owner-marked"
    refs.mkdir(exist_ok=True)
    marked_pins = {}
    for frame in sorted({r["frame_num"] for r in rows} | {21}):
        path = Path("C:/Users/OS/Downloads/temp") / f"1frame_{frame:05d}.jpg"
        target = refs / path.name
        shutil.copyfile(path, target)
        marked_pins[rel(target)] = sha(target)
    write("marked-input-pins.json", marked_pins)
    board = Image.new("RGB", (1120, 780), "white")
    draw = ImageDraw.Draw(board)
    for i, row in enumerate(rows):
        x, y = i % 5 * 224, i // 5 * 260
        draw.text((x + 3, y + 3), row["id"] + " " + row["draft_labels"], fill="black")
        with Image.open(ROOT / row["input"]) as im:
            board.paste(im, (x, y + 28))
    board.save(OUT / "additions-board.jpg")
    review = HERE / "owner-review.md"
    if not review.exists():
        lines = [
            "# Review 13 crop bổ sung theo vòng đỏ",
            "",
            "92 crop trước đã chốt; NA-008 đã có đúng frame 21 nên không tạo trùng. Chỉ các crop dưới đây là Draft. Thứ tự phone / looking.",
            "",
            "| ID | Frame | Nhãn Draft | Quyết định / ngoại lệ |",
            "|---|---|---|---|",
        ]
        lines += [f"| {r['id']} | {r['frame_num']} | {r['draft_labels']} | |" for r in rows]
        review.write_text("\n".join(lines) + "\n", encoding="utf-8")
    cards = []
    for row in rows + closed:
        new = row["id"].startswith("NC-")
        state = "draft" if new else "closed"
        labels = row["draft_labels"] if new else row["final_labels"]
        reason = row["reason"] if new else row["closure_reason"]
        cards.append(
            f'<article data-state="{state}" data-id="{row["id"]}"><h2>{row["id"]} · {labels}</h2><p>{"Bổ sung · Draft" if new else "Đã chốt theo owner"}</p><img width="224" height="224" loading="lazy" src="../../{html.escape(row["input"], quote=True)}" alt="{row["id"]}"><p>{html.escape(reason)}</p><a href="../../{row["crop"]}">Crop gốc</a> · <a href="../../{row["source"]}">Frame sạch</a></article>'
        )
    template = (HERE / "gallery-template.html").read_text(encoding="utf-8")
    (OUT / "index.html").write_text(template.replace("__CARDS__", "".join(cards)), encoding="utf-8")
    print("Closed 92, changed 9; additions 13, marked mappings 14")


if __name__ == "__main__":
    main()
