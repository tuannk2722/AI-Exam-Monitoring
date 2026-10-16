"""Materialize this manual audit's evidence; never annotate images automatically."""

import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
OLD = ROOT / "artifacts/reports/E004-crop-bundle-refinement-20261015"
OUT = ROOT / "outputs" / REPORT.name
DETAILS = {
    "12": [18, 30, 52, 69, 72, 114],
    "01": [1, 2, 3, 4, 5, 6, 13, 24, 31, 50, 51, 53],
    "02": [54, 59, 62, 63, 65, 70, 72, 74, 76, 78, 80, 81],
    "03": [82, 84, 86, 91, 93, 94, 95, 96, 97],
    "04": [77, 79, 98, 99, 102, 103, 104, 108, 109, 114, 115, 116],
    "05": [117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 138, 139],
    "06": [142, 143, 145, 147, 148, 149, 150, 151, 152, 153, 154, 159],
    "07": [157, 158, 160, 162, 167, 168, 171, 172, 175, 176, 184, 189],
    "08": [190, 191, 194, 197, 200, 201, 205, 206, 208, 209, 210, 211],
    "09": [212, 213, 214, 215, 219, 221, 222, 224, 225, 226, 227, 228],
    "10": [230, 231, 232, 233, 235, 236, 237, 239, 240, 241, 244, 245],
    "11a": [7, 8, 9, 10, 11, 12, 128, 129, 130, 131, 133, 134],
    "11b": [136, 137, 140, 155, 156, 173, 174, 192, 193, 198, 202, 203],
}
RULES = {
    "SCREEN": ("P", "Mặt trước mobile đủ nhận dạng"),
    "BACK": ("U", "Chỉ lưng/cạnh, thiếu đặc trưng"),
    "PART": ("U", "Vật còn lộ một phần, chưa phân loại"),
    "BLUR": ("U", "Mờ/nhỏ mất đặc trưng loại vật"),
    "OCC": ("U", "Tay/vùng liên quan bị che"),
    "CALC": ("N", "Calculator rõ và đủ absence còn lại"),
    "CLEAR": ("N", "Vùng quan sát đủ, không thấy mobile"),
    "COVER": ("N", "Ngoại lệ vật bị che hoàn toàn"),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare():
    if (REPORT / "input-pins.json").exists():
        raise RuntimeError("Pinned input exists; prepare a new revision instead.")
    OUT.mkdir(parents=True, exist_ok=True)
    snapshot = REPORT / "owner-review-input.md"
    if not snapshot.exists():
        shutil.copyfile(OLD / "owner-review.md", snapshot)
    rows = [r for r in read(OLD / "candidate-ledger.json") if r["disposition"] == "shortlist"]
    assert len(rows) == 247
    write(
        REPORT / "input-pins.json",
        {
            "upstream_result_pins": sha(OLD / "result-pins.json"),
            "upstream_ledger": sha(OLD / "candidate-ledger.json"),
            "owner_review_snapshot": sha(snapshot),
            "scope": (
                "247 upstream shortlisted candidates; 658 non-shortlist records remain "
                "historical only"
            ),
        },
    )
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
    for start in range(0, len(rows), 16):
        board = Image.new("RGB", (1008, 1040), "white")
        draw = ImageDraw.Draw(board)
        for j, row in enumerate(rows[start : start + 16]):
            x, y = (j % 4) * 252, (j // 4) * 260
            im = Image.open(ROOT / row["input"]).convert("RGB")
            assert im.size == (224, 224)
            board.paste(im, (x + 14, y + 32))
            draw.text(
                (x + 4, y + 1), f"{start + j + 1:03} {row['candidate_id']}", fill="black", font=font
            )
            draw.text((x + 4, y + 17), row["draft_labels"], fill="black", font=font)
        board.save(OUT / f"inputs-{start // 16 + 1:02}.png")
    write(REPORT / "review-order.json", [dict(ordinal=i + 1, **r) for i, r in enumerate(rows)])


def details(ordinals, name):
    rows = read(REPORT / "review-order.json")
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)
    board = Image.new("RGB", (1200, 420 * ((len(ordinals) + 2) // 3)), "white")
    draw = ImageDraw.Draw(board)
    for j, ordinal in enumerate(ordinals):
        row = rows[ordinal - 1]
        x, y = (j % 3) * 400, (j // 3) * 420
        im = Image.open(ROOT / row["source"]).convert("RGB").crop(row["context_xyxy"])
        im = ImageOps.contain(im, (396, 380))
        board.paste(im, (x + (400 - im.width) // 2, y + 35))
        draw.text(
            (x + 3, y + 3),
            f"{ordinal:03} {row['candidate_id']} {row['draft_labels']}",
            fill="black",
            font=font,
        )
    board.save(OUT / f"{name}.png")


def assemble():
    if (REPORT / "result-pins.json").exists():
        raise RuntimeError("Pinned result exists; do not overwrite results or owner review.")
    originals = read(REPORT / "review-order.json")
    decisions = {}
    for line in (REPORT / "manual-review.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        ordinal, labels, rule, note = line.split("|", 3)
        assert int(ordinal) not in decisions
        assert re.fullmatch("[PNU]/[PNU]", labels)
        assert RULES[rule][0] == labels[0]
        decisions[int(ordinal)] = (labels, rule, note)
    assert set(decisions) == set(range(1, 248))
    comments = {}
    for line in (REPORT / "owner-review-input.md").read_text(encoding="utf-8-sig").splitlines():
        fields = line.split("|")
        if len(fields) >= 5 and fields[1].strip() in {r["candidate_id"] for r in originals}:
            comments[fields[1].strip()] = "|".join(fields[3:-1]).strip()
    assert set(comments) == {r["candidate_id"] for r in originals}
    looking_notes = {
        52: (
            "Đầu hướng xuống trang giấy/thiết bị trong vùng bài riêng, không còn lý "
            "do U chỉ vì nhìn nghiêng."
        ),
        80: (
            "Hai tay che một phần mặt nhưng hướng đầu cúi vào giấy riêng còn xác định"
            " được; không tự U vì che mắt."
        ),
        94: "Đầu anchor ngoài crop, không có evidence hướng nhìn của chính anchor.",
        106: (
            "Đầu và mặt ngẩng khỏi trang giấy, hướng ra trước ngoài vùng bài; mắt mờ "
            "không tự làm U."
        ),
        117: (
            "Đầu/mặt quay sang bên khỏi trang giấy trên bàn; có context, không cần "
            "thấy rõ con ngươi."
        ),
        120: (
            "Tay che mặt; hướng xuống/ra trước sát ranh giới vùng bài, chưa đủ chốt N"
            " hoặc P. Không nhận P chỉ từ tư thế."
        ),
        126: (
            "Đứng chỉnh tóc, hướng mặt/đích nhìn chưa rõ so với vùng bài; không suy "
            "looking từ đứng lên."
        ),
        131: (
            "Hướng đầu hơi ra trước nhưng đích nhìn không rõ. Không đủ P cũng chưa đủ"
            " N; giữ U thay vì chọn N mặc định."
        ),
        184: "Đầu/mặt ngẩng hướng ra trước trong khi vùng giấy ở dưới, đủ nhìn ngoài vùng riêng.",
        200: (
            "Anchor áo hồng phía giữa/sau quay đầu sang trái khỏi vùng giấy; không "
            "lấy hướng của hai người khác."
        ),
        201: (
            "Anchor áo trắng đeo kính phía trước quay đầu sang phải; người áo đen "
            "phía sau không là anchor."
        ),
        235: (
            "Đầu cúi nghiêng nhưng vùng bài tương ứng bị cắt/che; chưa đủ kết luận nhìn ra ngoài."
        ),
        236: (
            "Đầu hướng vào tập giấy trong tay riêng; quay nghiêng không tự thành nhìn"
            " ngoài vùng bài."
        ),
        237: "Hướng đầu vào tập giấy dựng trong tay riêng, không có evidence nhìn ngoài.",
        240: (
            "Đầu và thân cúi hẳn dưới mặt bàn, ngoài vùng giấy riêng có thể đối chiếu"
            " trong context."
        ),
        244: (
            "Đầu/nhìn hướng về vật trong tay tại vùng riêng; nhìn own-device không tự"
            " looking positive."
        ),
    }
    default_looking = {
        "N": (
            "Hướng đầu vào giấy/thiết bị trong vùng riêng đủ rõ ở crop này; không suy"
            " từ nhãn hành động nguồn."
        ),
        "P": (
            "Hướng đầu ngẩng/quay khỏi vùng bài riêng có context trong crop; không "
            "suy ý định hoặc duration."
        ),
        "U": "Hướng đầu hoặc đích nhìn so với vùng bài chưa đủ rõ trong crop này.",
    }
    ledger = []
    for row in originals:
        ordinal = row["ordinal"]
        labels, rule, note = decisions[ordinal]
        item = {
            k: row[k]
            for k in (
                "ordinal",
                "candidate_id",
                "sample_id",
                "parent_id",
                "anchor_id",
                "frame_num",
                "description",
                "cohort",
                "source",
                "source_sha256",
                "crop",
                "crop_sha256",
                "input",
                "input_sha256",
                "context_xyxy",
            )
        }
        item.update(
            prior_draft_labels=row["draft_labels"],
            draft_labels=labels,
            phone_changed=labels[0] != row["draft_labels"][0],
            looking_changed=labels[2] != row["draft_labels"][2],
            label_changed=labels != row["draft_labels"],
            evidence_code=rule,
            evidence_category=RULES[rule][1],
            phone_reason=note,
            looking_reason=looking_notes.get(ordinal, default_looking[labels[2]]),
            owner_comment=comments[row["candidate_id"]],
            disposition="withheld" if labels == "U/U" else "shortlist",
            geometry_review_required=ordinal in (200, 201),
            status="draft_review_only",
            assigned_split=None,
            training_ready=False,
            canonical_targets=[None, None],
            canonical_mask=[0, 0],
            evidence_crop_sha256=row["crop_sha256"],
            input_board=f"outputs/{REPORT.name}/inputs-{(ordinal - 1) // 16 + 1:02}.png",
            source_detail_boards=[
                f"outputs/{REPORT.name}/detail-{key}.png"
                for key, values in DETAILS.items()
                if ordinal in values
            ],
            semantics_ref=f"artifacts/reports/{REPORT.name}/owner-direction.md",
        )
        ledger.append(item)
    write(REPORT / "candidate-ledger.json", ledger)
    summary = {
        "status": "draft_not_dataset_acceptance",
        "audited": len(ledger),
        "labels_before": dict(Counter(r["prior_draft_labels"] for r in ledger)),
        "labels_after": dict(Counter(r["draft_labels"] for r in ledger)),
        "label_changed": sum(r["label_changed"] for r in ledger),
        "phone_changed": sum(r["phone_changed"] for r in ledger),
        "looking_changed": sum(r["looking_changed"] for r in ledger),
        "phone_transitions": dict(
            Counter(r["prior_draft_labels"][0] + "->" + r["draft_labels"][0] for r in ledger)
        ),
        "evidence_categories": dict(Counter(r["evidence_code"] for r in ledger)),
        "dispositions": dict(Counter(r["disposition"] for r in ledger)),
        "source_detail_count": sum(bool(r["source_detail_boards"]) for r in ledger),
        "unique_frames_in_audited_crops": len({r["source"] for r in ledger}),
        "owner_comments": sum(bool(r["owner_comment"]) for r in ledger),
        "geometry_attention": [r["candidate_id"] for r in ledger if r["geometry_review_required"]],
        "not_reaudited_non_shortlist": 658,
    }
    write(REPORT / "summary.json", summary)
    template = (REPORT / "gallery-template.html").read_text(encoding="utf-8")
    payload = json.dumps(ledger, ensure_ascii=False).replace("<", "\\u003c")
    (OUT / "index.html").write_text(template.replace("__DATA__", payload), encoding="utf-8")
    lines = [
        "# Đối chiếu review owner",
        "",
        (
            "Snapshot nguyên văn ở [owner-review-input.md](owner-review-input.md). "
            "Các dòng có nhận xét được đối chiếu riêng dưới đây; tất cả 247 dòng đã "
            "xem lại, kể cả dòng trống. Nhãn mới là Draft."
        ),
        "",
    ]
    for r in ledger:
        if not r["owner_comment"]:
            continue
        lines += [
            f"## {r['candidate_id']} — {r['prior_draft_labels']} → {r['draft_labels']}",
            "",
            "> " + r["owner_comment"],
            "",
            r["phone_reason"],
            "",
            r["looking_reason"],
            "",
        ]
        if r["geometry_review_required"]:
            lines += [
                (
                    "Có nhiều người nổi bật: giữ cờ geometry/attribution trước package; "
                    "classifier RGB chưa nhận anchor box. Không coi label Draft là crop đã "
                    "nghiệm thu."
                ),
                "",
            ]
    (REPORT / "owner-resolution.md").write_text("\n".join(lines), encoding="utf-8")
    lines = [
        "# Delta và batch review mới",
        "",
        (
            "Đã đối chiếu review owner; không yêu cầu annotate lại toàn bộ. Có thể "
            "nghiệm thu batch và ghi ngoại lệ. File này không nằm trong result-pins "
            "để owner tiếp tục ghi chú."
        ),
        "",
        "| ID | Trước | Sau | Quy tắc | Quyết định owner / ngoại lệ |",
        "|---|---|---|---|---|",
    ]
    lines += [
        f"| {r['candidate_id']} | {r['prior_draft_labels']} | "
        f"{r['draft_labels']} | {r['evidence_code']} | |"
        for r in ledger
    ]
    (REPORT / "owner-review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def validate():
    existing_pins = REPORT / "result-pins.json"
    if existing_pins.exists():
        for path, expected in read(existing_pins)["files"].items():
            assert sha(ROOT / path) == expected, f"Pinned result drift: {path}"
    ledger = read(REPORT / "candidate-ledger.json")
    originals = {r["candidate_id"]: r for r in read(REPORT / "review-order.json")}
    assert len(ledger) == len(originals) == 247
    assert len({r["candidate_id"] for r in ledger}) == 247
    pins = read(REPORT / "input-pins.json")
    assert pins["upstream_result_pins"] == sha(OLD / "result-pins.json")
    assert pins["upstream_ledger"] == sha(OLD / "candidate-ledger.json")
    assert pins["owner_review_snapshot"] == sha(REPORT / "owner-review-input.md")
    oldpins = read(OLD / "result-pins.json")["files"]
    for path, expected in oldpins.items():
        assert sha(ROOT / path) == expected, path
    hash_checks = 0
    for row in ledger:
        old = originals[row["candidate_id"]]
        assert row["prior_draft_labels"] == old["draft_labels"]
        assert row["phone_reason"] and row["looking_reason"]
        assert RULES[row["evidence_code"]][0] == row["draft_labels"][0]
        assert row["canonical_targets"] == [None, None] and row["canonical_mask"] == [0, 0]
        assert row["assigned_split"] is None and row["training_ready"] is False
        assert (row["draft_labels"] == "U/U") == (row["disposition"] == "withheld")
        for field in ("source", "crop", "input"):
            assert row[field] == old[field] and row[field + "_sha256"] == old[field + "_sha256"]
            assert sha(ROOT / row[field]) == row[field + "_sha256"], row["candidate_id"]
            hash_checks += 1
        assert Image.open(ROOT / row["input"]).size == (224, 224)
        for path in [row["input_board"], *row["source_detail_boards"]]:
            assert (ROOT / path).is_file()
    html = (OUT / "index.html").read_text(encoding="utf-8")
    assert "__DATA__" not in html
    embedded = re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S)
    assert json.loads(embedded.group(1)) == ledger
    result = {
        "status": "PASS",
        "records": 247,
        "media_hash_checks": hash_checks,
        "upstream_result_pins": len(oldpins),
        "input_224_checks": 247,
        "all_unknown_unknown_withheld": True,
        "production_changed": False,
        "limitation": (
            "Integrity/software checks do not prove visual ground truth or owner acceptance."
        ),
    }
    write(REPORT / "validation.json", result)
    files = [
        "input-pins.json",
        "owner-review-input.md",
        "manual-review.txt",
        "candidate-ledger.json",
        "summary.json",
        "owner-direction.md",
        "rubric.md",
        "owner-resolution.md",
        "validation.json",
    ]
    mapping = {
        str((REPORT / f).relative_to(ROOT)).replace("\\", "/"): sha(REPORT / f) for f in files
    }
    mapping[f"outputs/{REPORT.name}/index.html"] = sha(OUT / "index.html")
    write(
        REPORT / "result-pins.json",
        {"status": "draft_audit_handoff_not_acceptance", "files": mapping},
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "prepare"
    {"prepare": prepare, "assemble": assemble, "validate": validate}[action]()
