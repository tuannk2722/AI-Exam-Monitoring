"""Assemble this study's visual screening notes; never assign accepted labels."""
from __future__ import annotations

import hashlib
import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ID = "E004-crop-bundle-audit-20261014"
REPORT = ROOT / "artifacts/reports" / ID
OUT = ROOT / "outputs" / ID
RECORDS = ROOT / "data/interim" / ID / "records.json"

# Observations from all 48 boards. Track notes are screening, not per-frame labels.
NOTES = {
    "g1_B_mid_glasses": ("anchor_device", "Thiết bị nhỏ/che khuất, nhiều người; cần kiểm đúng người và phone/calculator trên frame gốc."),
    "g1_C_front_glasses": ("calculator", "Máy tính có bàn phím rõ: ứng viên hard negative tốt. Nhìn máy tính trên bài riêng không tự thành looking P; có frame cắt đầu."),
    "g1_L_front_white": ("desk_phone", "Điện thoại cạnh máy tính trên bàn riêng; tay che mặt và người lân cận. Rà looking độc lập."),
    "g1_L_mid_white": ("anchor_device", "Đầu người phía trước che bàn; camera dịch chuyển. Cần phân biệt điện thoại của target và hàng bên cạnh."),
    "g1_M_front_polo": ("desk_phone", "Điện thoại trắng cầm tay/trên bài, xen kẽ viết bài; nhãn looking cần xét vùng bài riêng."),
    "g1_M_mid_white": ("desk_phone", "Có phone và calculator trên bàn/cầm tay; trạng thái looking đề xuất thay đổi dù đều thao tác vùng riêng."),
    "g1_R_front_glasses": ("desk_phone", "Phone và calculator xanh tách biệt; hữu ích phân biệt vật thể, nhiều frame không rõ mắt."),
    "g1_R_mid_white": ("anchor_device", "Phone/calculator và người tiền cảnh chồng lấn; CB-0218 che khuất mạnh, cần kiểm nguồn."),
    "g2_back_white": ("anchor_device", "Hàng sau, nhiều người trong crop; thiết bị xa và một phần. Chưa đủ để chuyển unknown."),
    "g2_front_left_black": ("desk_phone", "Phone trên bàn/cầm tay rõ ở nhiều frame; looking P cả khi viết bài cần rà lại."),
    "g2_front_white": ("desk_phone", "Nhiều phone và calculator ở bàn target; một chuỗi dài phụ thuộc thời gian, không coi là 87 tình huống độc lập."),
    "g2_mid_green10": ("desk_phone", "Phone và calculator trên bàn/cầm tay; cần tách nhãn hướng nhìn khỏi sự hiện diện phone."),
    "g2_mid_jacket": ("desk_phone", "Phone và calculator rõ; nhiều frame nhìn vùng riêng, một số quay ngang như CB-0473–0476 cần review hướng nhìn."),
    "g2_mid_white_glasses": ("anchor_device", "Phone/calculator nhỏ, bị che một phần; không truyền nhãn phone theo chuỗi khi vật mất khỏi crop."),
    "g2_middle_beige": ("anchor_device", "Phone ở tay/bàn nhưng crop nhiều người, chi tiết nhỏ và có frame mờ như CB-0524."),
    "g2_right_yellow": ("recrop", "Target áo vàng tiền cảnh bị cắt bàn/tay; phone nổi bật phía sau thuộc người khác. Ưu tiên recrop từ nguồn, không suy N từ không thấy."),
    "g5_front_left_gray": ("desk_phone", "Phone trên bài riêng rõ nhiều frame, đầu/mặt bị cắt hoặc che. Những U cuối chuỗi vẫn có vật cần xem lại."),
    "g5_front_right_white": ("recrop", "Cắt đầu và bàn nặng; CB-0601–0603 gần như chỉ tay/thân. Có thể dùng evidence phone sau review, looking chưa đủ."),
    "g5_front_striped": ("recrop", "Calculator hard negative tiềm năng nhưng đầu bị cắt; cần phục hồi context trước chốt looking."),
    "g5_mid_black": ("recrop", "Vật không luôn thấy; tư thế đứng/di chuyển cuối chuỗi làm target và vùng bài không ổn định."),
    "g5_mid_jersey": ("recrop", "Phone và calculator hữu ích; cuối chuỗi mờ/cắt đầu và camera trôi, cần kiểm lại anchor từng đoạn."),
    "g5_mid_navy": ("desk_phone", "Phone trên bàn và calculator; có quay ngang CB-0647, không gộp looking P cho cả chuỗi."),
    "g5_mid_redshirt": ("recrop", "CB-0648 frame 44 crop vào người áo trắng; các crop tiếp theo vào áo đỏ. Không coi một anchor ID là một người xuyên suốt."),
    "g5_mid_white": ("recrop", "Phone/calculator có ích, nhưng một số crop cắt đầu/che mặt; rà geometry trước nhãn looking."),
    "g4_front_gray": ("gaze", "Có nhìn phía trước/ngoài trang trong nhóm looking N; vật trên bàn cần native để phân loại, không tự đổi U."),
    "g4_front_pink": ("desk_phone", "Phone trên bàn/cầm tay; có quay ngang, ngẩng và cúi viết. Các U về cuối vẫn có evidence, cần review theo frame."),
    "g4_front_suitblue": ("gaze", "Nhãn N gồm cả nhìn lên phía trước; cần xác định vùng bài và ngữ cảnh, không lấy tên scenario own_work làm evidence."),
    "g4_front_suitgray": ("gaze", "Nhìn ngang/lên và viết xen kẽ; N không đồng nhất với hướng nhìn trong crop. Phone của hàng sau không thuộc target."),
    "g4_mid_red": ("recrop", "CB-0734–0735 người áo đỏ chưa ở vị trí crop ổn định; sau đó có quay đầu/ngẩng. Cần phục hồi anchor theo nguồn."),
    "g3_front_left": ("gaze", "Góc cao, cúi viết/lật sách và quay ngang; vật nhỏ chưa đủ kết luận phone. Có ích cho context sau review."),
    "g3_front_mid": ("gaze", "Góc cao, lật giấy/viết và người bên cạnh; cần phân vùng bài riêng, giữ phone unknown khi thiếu evidence."),
    "g3_front_right": ("gaze", "Sách, hộp bút, tay gần mặt; không tự gọi vật nhỏ là phone. Tư thế đa dạng nhưng gaze còn mơ hồ."),
}


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    records = json.loads(RECORDS.read_text(encoding="utf-8"))
    tracks = json.loads((REPORT / "tracks.json").read_text(encoding="utf-8"))
    assert {t["anchor"] for t in tracks} == set(NOTES)
    notes = []
    cards = []
    batches: Counter[str] = Counter()
    for r in records:
        s = r["supplied"]
        batch, note = NOTES[s["anchor_id"]]
        batches[batch] += 1
        entry = {
            "sample_id": r["sample_id"], "anchor": s["anchor_id"],
            "parent": s["parent_id"], "frame": s["frame_num"],
            "screening": "crop_viewed_on_board", "batch": batch,
            "track_screening_note": note,
            "supplied_labels": {"phone": s["phone"], "looking": s["looking"]},
            "accepted_labels": None, "assigned_split": None,
            "disposition": "retain_pending_review", "looking_contract_review": True,
            "crop_sha256": r["fingerprint"]["sha256"],
        }
        notes.append(entry)
        sid = r["sample_id"]
        crop = "../../" + r["local_crop"]
        source = "../../" + r["local_source"]
        for local in (r["local_crop"], r["local_source"]):
            assert (ROOT / local).is_file()
        search = html.escape(f'{sid} {s["anchor_id"]} {batch} {s["phone"]}/{s["looking"]}')
        cards.append(
            f'<article id="{sid}" data-search="{search}"><h2>{sid}</h2>'
            f'<a href="{crop}"><img loading="lazy" src="{crop}" width="224" height="224" alt="{sid}"></a>'
            f'<p>{html.escape(s["anchor_id"])} · frame {s["frame_num"]}</p>'
            f'<p>Nhãn ZIP (phone/looking): <b>{s["phone"]}/{s["looking"]}</b> · {batch}</p>'
            f'<p>{html.escape(note)}</p><p>Box nguồn: {s["bbox_xyxy"]}</p>'
            f'<a href="{source}">Frame gốc</a> · <a href="{r["board"]}">Board</a></article>'
        )
    dump(REPORT / "visual-screening.json", notes)
    dump(REPORT / "review-batches.json", {
        "status": "draft_screening_not_annotation_acceptance", "retained": len(records),
        "batch_counts": dict(batches),
        "tracks": [dict(t, batch=NOTES[t["anchor"]][0], note=NOTES[t["anchor"]][1]) for t in tracks],
        "source_frames_visually_checked": [records[i-1]["local_source"] for i in [27,543,648,649,734,749]],
        "all_source_frames_technical_only": 212,
    })
    page = '''<!doctype html><html lang="vi"><meta charset="utf-8"><title>Audit 765 crop</title>
<style>body{font:16px system-ui;margin:24px;background:#f3f5f7;color:#172330}header{position:sticky;top:0;background:#fff;padding:12px;border-bottom:2px solid #345}input{padding:10px;width:min(600px,90%)}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}article{padding:16px;background:white;border:1px solid #ccc}h2{font-size:18px}img{max-width:100%}a{color:#1553a0}p{line-height:1.5}</style>
<header><h1>765 crop · Audit toàn bộ · Draft</h1><p>Đã xem đủ crop; ghi chú theo track, chưa nghiệm thu nhãn. Giữ unknown; chưa chia split. Click ảnh để xem 224 gốc, mở frame để đối chiếu box.</p>
<input id="q" aria-label="Lọc mẫu" placeholder="Lọc CB-0648, g2_right_yellow, recrop, P/U…"><p id="count">765 / 765</p></header><main>'''
    page += "\n".join(cards)
    page += '''</main><script>const cards=[...document.querySelectorAll('article')];document.querySelector('#q').addEventListener('input',e=>{const q=e.target.value.toLowerCase().trim();let n=0;for(const c of cards){const show=c.dataset.search.toLowerCase().includes(q);c.hidden=!show;if(show)n++;}document.querySelector('#count').textContent=n+' / '+cards.length;});</script></html>'''
    (OUT / "index.html").write_text(page, encoding="utf-8")
    assert len(notes) == len({n["sample_id"] for n in notes}) == 765
    dump(REPORT / "assembly-checks.json", {
        "rows": len(notes), "tracks": len(NOTES), "gallery_cards": len(cards),
        "crop_and_source_links": "PASS", "retained_all": True,
        "records_sha256": hashlib.sha256(RECORDS.read_bytes()).hexdigest(),
        "visual_scope": "765 crop screening; 6 source frames visual; 212 source frames technical",
    })
    print(dict(batches))


if __name__ == "__main__":
    main()
