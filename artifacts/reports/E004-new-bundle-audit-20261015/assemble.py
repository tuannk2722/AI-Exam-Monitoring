"""Assemble reviewed research ledger, forensic checks and local HTML gallery."""

import hashlib
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / HERE.name


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def write(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def duplicates(rows, key):
    groups = defaultdict(list)
    for r in rows:
        groups[r[key]].append(r["id"])
    return [v for v in groups.values() if len(v) > 1]


def main():
    assert not (HERE / "result-pins.json").exists(), "Audit sealed"
    inventories = read("crop-inventory.json")
    frames = read("frame-inventory.json")
    originals = {r["id"]: r for r in inventories}
    rows = []
    for group in "AB":
        review = read(f"source-{group}-review.json")
        for kind in ("supplied_reviews", "derivative_reviews"):
            for record in review[kind]:
                row = dict(originals.get(record["id"], {}))
                row.update(record)
                row["source_group"] = group
                row["kind"] = (
                    "supplied"
                    if kind == "supplied_reviews"
                    else ("recrop" if "-R1" in row["id"] else "additional")
                )
                row["status"] = "draft_owner_review_required"
                row["training_ready"] = False
                row["assigned_split"] = None
                row["canonical_targets"] = [None, None]
                row["canonical_mask"] = [0, 0]
                row["input_sha256"] = sha(ROOT / row["input"])
                if row["id"] == "NB-0014":
                    row["disposition"] = "superseded_better_context"
                    row["selection_reason"] = (
                        "Cùng anchor/trạng thái với NA-008; chọn NA-008 có calculator và hai tay đầy đủ hơn, không nhân đôi N/N."
                    )
                if row["draft_labels"] == "U/U":
                    row["disposition"] = "withheld_uu"
                if row["id"] == "NBX-007":
                    row["disposition"] = "withheld_geometry"
                if row["id"] == "NA-008":
                    row["replaces"] = "NB-0014"
                if row["kind"] == "recrop":
                    row["replaces"] = row["id"].removesuffix("-R1")
                if row["source_group"] == "B" and row["kind"] == "recrop":
                    notes = {
                        "NB-0034-R1": "Anchor kẹp tóc phía trái: tay tựa má và tay trên bàn không có vật mơ hồ; đầu hướng sang bên ngoài bài. Khung mới giảm người bên phải.",
                        "NB-0035-R1": "Anchor tóc dài giữa khung quay sang bên, vùng tay dưới mép vẫn thiếu nên phone U; không dùng nụ cười để gán looking.",
                        "NB-0036-R1": "Anchor áo xám ngẩng đầu hướng ngoài giấy; vùng bàn tay vẫn bị người trước che nên phone U.",
                        "NB-0037-R1": "Anchor áo xanh cúi vào giấy riêng, hai tay quanh bút thấy rõ; khung bỏ phần lớn người đeo kính bên phải.",
                        "NB-0038-R1": "Anchor áo xám đeo kính giữa khung có hai tay trên bàn; ranh giới hướng nhìn giữa hai vùng giấy chưa chắc nên looking U.",
                        "NB-0041-R1": "Đã lấy đủ đỉnh đầu. Hai tay trên giấy, một tay cầm bút; đầu quay sang người bên trái ngoài giấy nên N/P.",
                        "NB-0054-R1": "Đúng người áo xanh sát tường: một tay chống trán, một tay viết, đầu cúi bài; người đeo kính tiền cảnh không còn là trung tâm.",
                        "NB-0062-R1": "Đúng người áo xanh hàng sau bên phải: tay viết và tay đặt giấy, đầu cúi về vùng bài riêng.",
                        "NB-0069-R1": "Khung đủ đầu và hai tay với bút/giấy; đầu quay ra sau khỏi bàn riêng nên N/P, không lấy thiết bị người cạnh làm bằng chứng.",
                        "NB-0077-R1": "Anchor áo trắng phía sau đã ở trung tâm; đầu cúi giấy. Tay chồng lấn người áo xám nên phone U, không suy absence.",
                        "NB-0079-R1": "Anchor áo xanh bên trái quay ngang, một tay giơ sau đầu; tay kia thiếu quan sát nên phone U.",
                    }
                    row["phone_reason"] = notes[row["id"]]
                    row["looking_reason"] = ""
                row["selected"] = row["disposition"] == "keep"
                rows.append(row)
    assert len(rows) == 109 and len({r["id"] for r in rows}) == 109
    assert {r["id"] for r in rows if r["kind"] == "supplied"} == set(originals)
    verified = 0
    transform_errors = []
    for row in rows:
        for field in ("source", "crop", "input"):
            assert sha(ROOT / row[field]) == row[field + "_sha256"], (row["id"], field)
        with Image.open(ROOT / row["input"]) as im:
            assert im.size == (224, 224)
            inp = np.array(im.convert("RGB"))
        with Image.open(ROOT / row["source"]) as im:
            box = row["context_xyxy"]
            x1, y1, x2, y2 = box
            assert 0 <= x1 < x2 <= im.width and 0 <= y1 < y2 <= im.height
            roi = im.convert("RGB").crop(box)
        if row["kind"] != "supplied":
            with Image.open(ROOT / row["crop"]) as im:
                assert np.array_equal(np.array(roi), np.array(im.convert("RGB")))
            assert np.array_equal(np.array(preview_input(roi, 224, (124, 116, 104))), inp)
            verified += 1
        else:
            errors = {}
            for method in (
                Image.Resampling.BILINEAR,
                Image.Resampling.BICUBIC,
                Image.Resampling.LANCZOS,
            ):
                resize = np.array(roi.resize((224, 224), method)).astype(float)
                errors[method.name] = round(float(np.abs(resize - inp.astype(float)).mean()), 4)
            transform_errors.append(
                {"id": row["id"], "rgb_mae_by_resampler": errors, "best_mae": min(errors.values())}
            )
    near = []
    for i, a in enumerate(inventories):
        for b in inventories[i + 1 :]:
            distance = (a["fingerprint"]["dhash"] ^ b["fingerprint"]["dhash"]).bit_count()
            if distance <= 6:
                near.append(
                    {
                        "a": a["id"],
                        "b": b["id"],
                        "dhash_distance": distance,
                        "decision": "screen_only_not_automatic_removal",
                    }
                )
    # No protected train/test media are opened for this audit.
    previous = json.loads(
        (HERE.parent / "E004-crop-closure-20261015/candidate-ledger.json").read_text(
            encoding="utf-8"
        )
    )
    old_source = {r["source_sha256"] for r in previous}
    old_crops = {r["crop_sha256"] for r in previous}
    for frame in frames:
        frame["visual_status"] = "overview_screened"
        frame["visual_reviewer"] = (
            "source_A_agent_with_per_frame_notes"
            if frame["source_group"] == "A"
            else "source_B_agent_completion_message"
        )
    selected = [r for r in rows if r["selected"]]
    summary = {
        "status": "draft_not_owner_accepted",
        "supplied_crops": 80,
        "source_frames": 132,
        "review_rows": len(rows),
        "derivatives": 29,
        "selected": len(selected),
        "selected_by_kind": dict(Counter(r["kind"] for r in selected)),
        "selected_label_counts": dict(Counter(r["draft_labels"] for r in selected)),
        "dispositions": dict(Counter(r["disposition"] for r in rows)),
        "native_derivatives_and_preprocessing_exact": verified,
        "source_exact_duplicates": duplicates(frames, "source_sha256"),
        "crop_exact_duplicates": duplicates(inventories, "crop_sha256"),
        "same_source_bytes_as_old247": [
            r["id"] for r in frames if r["source_sha256"] in old_source
        ],
        "same_crop_bytes_as_old247": [
            r["id"] for r in inventories if r["crop_sha256"] in old_crops
        ],
        "near_duplicate_pairs": near,
        "supplied_crop_reconstruction": "MAE diagnostic only; JPEG encoder/resampler unknown; no exact pixel parity claim",
        "supplied_reconstruction_max_best_mae": max(r["best_mae"] for r in transform_errors),
        "training_ready": False,
    }
    write("candidate-ledger.json", rows)
    write("frame-coverage.json", frames)
    write("crop-reconstruction.json", transform_errors)
    write("summary.json", summary)
    review = [
        "# Owner review bộ mới",
        "",
        "Toàn bộ nhãn là Draft. Thứ tự: phone / looking. Các trường hợp không chọn vẫn ở gallery để đối chiếu; originals giữ nguyên. Có thể approve batch shortlist và ghi ngoại lệ, không cần annotate lại từng dòng.",
        "",
        "| ID | Nhãn Draft | Loại | Quyết định / ngoại lệ |",
        "|---|---|---|---|",
    ]
    review += [f"| {r['id']} | {r['draft_labels']} | {r['kind']} | |" for r in selected]
    review_path = HERE / "owner-review.md"
    if not review_path.exists():
        review_path.write_text("\n".join(review) + "\n", encoding="utf-8")
    cards = []
    for row in rows:
        ident = html.escape(row["id"])
        reason = html.escape(
            row.get("phone_reason", "")
            + " "
            + row.get("looking_reason", "")
            + " "
            + row.get("selection_reason", "")
        )
        links = " ".join(
            f'<a href="../../{html.escape(row[k], quote=True)}">{k}</a>' for k in ("crop", "source")
        )
        cards.append(
            f'<article data-selected="{str(row["selected"]).lower()}" data-search="{ident} {row["draft_labels"]} {row["kind"]} {row["source_group"]}"><h2>{ident} · {row["draft_labels"]}</h2><p>{row["source_group"]} · {row["kind"]} · {row["disposition"]}</p><a href="../../{html.escape(row["input"], quote=True)}"><img loading="lazy" width="224" height="224" src="../../{html.escape(row["input"], quote=True)}" alt="{ident}"></a><p>{reason}</p><p>{links}</p></article>'
        )
    frame_links = " ".join(
        f'<a href="frames-{g}/{n:02d}.jpg">{g}-{n:02d}</a>'
        for g, count in (("A", 6), ("B", 28))
        for n in range(1, count + 1)
    )
    page = (
        '<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Audit bộ crop mới</title><style>body{font:16px system-ui;margin:24px;background:#eef2f5;color:#182536}header{position:sticky;top:0;background:#eef2f5;padding:12px;z-index:1}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px}article{background:white;padding:18px;border-radius:10px}h2{font-size:19px}article p{line-height:1.5}img{display:block;margin:auto}input,select{padding:8px}a{color:#165b99}article[hidden]{display:none}</style><header><h1>Audit bộ mới · Draft</h1><p>80 crop gốc · 132 frame · 29 derivative. Nhãn phone / looking. Chưa nghiệm thu và chưa dùng train.</p><select id="mode"><option value="selected">Shortlist</option><option value="all">Toàn bộ gồm bản thay thế / loại</option></select> <input id="query" placeholder="ID, P/N, recrop, additional…"><span id="count"></span><p><a href="../../artifacts/reports/'
        + HERE.name
        + '/owner-review.md">Ghi quyết định owner</a></p></header><details><summary>Bảng toàn bộ frame gốc</summary>'
        + frame_links
        + "</details><main>"
        + "".join(cards)
        + '</main><script>const mode=document.getElementById("mode"),query=document.getElementById("query"),count=document.getElementById("count");function filter(){let n=0;for(const card of document.querySelectorAll("article")){const show=(mode.value==="all"||card.dataset.selected==="true")&&card.dataset.search.toLowerCase().includes(query.value.trim().toLowerCase());card.hidden=!show;if(show)n++;}count.textContent=" · "+n+" crop";}mode.addEventListener("change",filter);query.addEventListener("input",filter);filter();</script></html>'
    )
    (OUT / "index.html").write_text(page, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
