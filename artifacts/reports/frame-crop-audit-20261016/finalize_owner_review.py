"""Companion review: preserve original batch; record approvals and proposed corrections."""

import hashlib
import html
import json
import os
from collections import Counter
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.data.pilot_schema import PixelBox, read_records
from ai_exam_monitoring.data.source_review import (
    SourceImage,
    member_key,
    preview_input,
    write_pending_crop,
)

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "artifacts/reports/frame-crop-audit-20261016"
OLD = ROOT / "data/interim/frame-crop-audit-20261016"
OUT = ROOT / "data/interim/frame-crop-owner-review-20261017"

# States are [phone_use, looking_around]. These are case decisions, not a new rubric.
CASES = [
    (
        "G01-A01-F00001-R02",
        "NN",
        "keep",
        "Tay chống cằm và tay còn lại ở vùng viết; không thấy vật cầm mơ hồ. Không tự động U chỉ vì bàn tay bị đầu che một phần.",
        "CB-0055-R1,CB-0742-R1",
    ),
    (
        "G02-A02-F00015",
        "NP",
        "keep",
        "Vật trên trang có bố cục màn hình nhỏ và vùng phím; tay còn lại không có vật mơ hồ. Đề xuất calculator → phone N; hướng đầu lệch khỏi vùng bài giữ P.",
        "CB-0604-R1,CB-0026",
    ),
    (
        "G03-A02-F00018",
        "NP",
        "keep",
        "Vật cầm có nếp gấp và mép bao mềm, không chỉ là một mặt lưng thiết bị hình chữ nhật. Giữ N/P từ chính crop; không dùng tên hoạt động ở frame khác để suy ra vật.",
        "NC-009",
    ),
    (
        "G04-A02-F00014-R03",
        "NN",
        "keep",
        "Cánh tay gập/khoanh trên bàn, phần bị che nằm trong tư thế tay rõ; không có vật mơ hồ. Đủ evidence còn lại để N theo hướng owner đã duyệt cho occlusion, không phải mọi tay khuất đều N.",
        "NB-0013,NB-0015",
    ),
    (
        "G04-A03-F00074-R02",
        "UN",
        "keep",
        "Theo owner: chỉ thấy mặt lưng/cạnh vật đang cầm; không truyền nhận diện calculator từ frame khác.",
        "NC-003,NC-012",
    ),
    (
        "G05-A01-F00039",
        "PN",
        "keep",
        "Mặt lưng có các vòng ống kính tách biệt trong cụm camera và vòng trên ốp; đặc điểm nhận diện mạnh hơn một chấm tối hoặc cạnh đen. Giữ phone P, nhìn vào vùng thao tác N.",
        "CB-0024-R1",
    ),
    (
        "G06-A03-F00012",
        "NN",
        "recrop",
        "Khung cũ giữ phone ở bàn người bên cạnh nhưng cắt gần hết người đó, khiến RGB input dễ gán nhầm anchor. Đề xuất R02 bỏ vùng bàn bên cạnh, giữ đầu, hai tay và tờ giấy; không chỉ sửa lời giải thích.",
        "",
    ),
    (
        "G08-A01-F00009-R02",
        "NN",
        "keep",
        "Theo owner: tay cầm bút, không có vật gây nhiễu; chốt N/N.",
        "",
    ),
    (
        "G08-A01-F00014-R02",
        "NN",
        "keep",
        "Một tay khoanh, tay kia cầm bút; phần tay và bàn còn lại đủ rõ, không có thiết bị mơ hồ. Đề xuất phone N.",
        "NB-0013,NC-009",
    ),
    (
        "G09-A02-F00043",
        "NP",
        "keep",
        "Băng bó tự nó không phải evidence cho thiết bị hoặc unknown. Tư thế tay và vùng hoạt động còn lại đủ quan sát, không thấy vật mơ hồ; đề xuất phone N, giữ looking P. Không suy luận tác động model khi chưa đo.",
        "NB-0015",
    ),
    (
        "G09-A02-F00105",
        "NN",
        "keep",
        "Tương tự F00043 nhưng đánh giá ảnh này độc lập: băng bó không tạo một vật cầm chưa rõ, vùng bài đủ quan sát; đề xuất N/N.",
        "NB-0015",
    ),
    ("G10-A01-F00008", "NN", "keep", "Theo owner: chống đầu, tay/bàn rõ; chốt N/N.", ""),
    (
        "G10-A01-F00013",
        "NP",
        "keep",
        "Theo owner: tay/bàn rõ, hướng đầu ra ngoài vùng bài; chốt N/P.",
        "",
    ),
    (
        "G13-A06-F00021",
        "NP",
        "keep",
        "Tay chống mặt và phần tay/vùng bàn còn thấy không có vật mơ hồ. Người phía trước che một phần không tự động làm phone U khi evidence còn lại đủ; đề xuất N/P.",
        "CB-0745-R1,G2-A12-F005",
    ),
    (
        "G14-A02-F00047",
        "UN",
        "keep",
        "Thiết bị cầm chỉ lộ mặt/cạnh chưa đủ nhận diện. Laptop không thuộc phone_use và không nâng phone lên P. Đầu vẫn hướng vào vùng thao tác/bài của anchor; đề xuất U/N.",
        "NC-003,CB-0390",
    ),
    (
        "G14-A04-F00011",
        "UN",
        "keep",
        "Vật cầm có mặt lưng/viền nhưng thiếu camera, màn hình hay phím đủ phân biệt; laptop cạnh đó không giải quyết vật đang cầm. Đề xuất U/N.",
        "NC-003,CB-0390",
    ),
    (
        "G14-A05-F00012",
        "UN",
        "keep",
        "Vật cầm chỉ lộ mặt lưng/cạnh; calculator trên bàn không chứng minh vật cầm cũng là calculator hoặc phone. Đề xuất U/N.",
        "CB-0390",
    ),
    (
        "G14-A07-F00018",
        "UN",
        "keep",
        "Các chấm tối ở góc thiết bị nhỏ và nhòe trong input 224; chưa tách được đặc điểm camera đủ chắc so với mặt lưng/ốp khác. Đề xuất U/N, không gọi camera chỉ từ vài chấm.",
        "CB-0024-R1",
    ),
    (
        "G14-A09-F00027",
        "UN",
        "keep",
        "Mặt lưng vật cầm chưa phân biệt được; phần vật sát mép crop cũng không đủ để khẳng định laptop. Bỏ lý do suy ra laptop từ frame rộng; đề xuất U/N.",
        "NC-003,CB-0390",
    ),
    (
        "G14-A10-F00018",
        "UN",
        "withhold",
        "Vật anchor cầm là U, đồng thời crop giữ thiết bị/người bên cạnh khá nổi bật. Khung thử hẹp hơn vẫn dính thiết bị và cắt sát tay. Đề xuất tạm loại khỏi đợt nhập này; U/N là nhận xét nếu giữ, không phải crop đã đạt QA.",
        "NC-003",
    ),
    (
        "G16-A02-F00027",
        "UN",
        "keep",
        "Đầu cúi trong vùng bài, tay che mặt không phải looking_around P; đề xuất looking N. Phone giữ U vì vật trên bàn chưa đủ rõ để phân biệt.",
        "CB-0168",
    ),
    (
        "G17-A01-F00012",
        "UU",
        "withhold",
        "Ngồi nghiêng không đủ chứng minh nhìn ngoài vùng bài; ảnh xa/mờ chưa tách chắc hướng đầu. Đề xuất tạm loại vì evidence yếu, không khẳng định ảnh làm giảm kết quả model. U/U chỉ lưu bất định, không phải nhãn để nhập.",
        "",
    ),
    (
        "G18-A01-F00001",
        "PN",
        "keep",
        "Mặt lưng có cụm camera lớn với các thành phần tách được, không chỉ bóng đen trên một mặt phẳng. Giữ P/N từ ảnh này, không truyền sang người hoặc frame khác.",
        "CB-0024-R1",
    ),
    (
        "G18-A02-F00007",
        "UN",
        "keep",
        "Vật cầm nhỏ chỉ rõ dạng khối/cạnh, chưa có đặc trưng phân biệt phone với thiết bị khác. Đề xuất U/N.",
        "NC-003",
    ),
    (
        "G18-A02-F00010",
        "UP",
        "keep",
        "Ảnh này cũng chưa nhận diện được vật cầm; đề xuất phone U. Đầu quay ra ngoài vùng bài rõ hơn F00007, giữ looking P.",
        "NC-003",
    ),
    (
        "G18-A03-F00001",
        "UN",
        "keep",
        "Owner chốt trong hội thoại ngày 17/10: F00001 là U/N; không lan nhãn looking từ F00010.",
        "NC-003",
    ),
    (
        "G18-A03-F00010",
        "UP",
        "keep",
        "Owner xác nhận ngày 17/10: F00010 là U/P. Thiết bị chưa rõ nhưng đầu quay sang trái, ra khỏi vùng bài/thao tác. Quyết định này làm rõ dòng U/N chung trong README.",
        "NC-003",
    ),
    (
        "G19-A01-F00039",
        "NN",
        "keep",
        "Owner chốt phone N vì tay/bàn rõ; looking N không bị nêu sửa nên giữ như bản gốc.",
        "",
    ),
    (
        "G19-A01-F00052",
        "NP",
        "keep",
        "Owner chốt phone N vì tay/bàn rõ; looking P không bị nêu sửa nên giữ như bản gốc.",
        "",
    ),
    (
        "G20-A02-F00001",
        "UP",
        "keep",
        "Vật cầm ngang tối màu, chi tiết góc nhỏ chưa phân biệt chắc camera hay dấu trên vỏ. Đề xuất phone U; giữ looking P theo đầu quay ra ngoài vùng thao tác.",
        "CB-0024-R1,NC-003",
    ),
    (
        "G20-A02-F00020",
        "UN",
        "keep",
        "Mặt lưng tối và chi tiết sáng nhỏ chưa đủ nhận diện độc lập ở input; không lấy kết luận vật từ F00001. Đề xuất U/N.",
        "CB-0024-R1,NC-003",
    ),
    (
        "G20-A03-F00073",
        "PN",
        "keep",
        "Các vòng ống kính lớn tách biệt trên mặt lưng sáng vẫn thấy ở input; đủ hơn một mặt lưng trơn hoặc chấm nhòe. Giữ P/N.",
        "CB-0024-R1",
    ),
    (
        "G21-A01-F00007",
        "NP",
        "keep",
        "Theo owner chốt N/P. Vật nâu có dạng gấp/mềm, không cần khẳng định chính xác là bìa hay ví để ghi nhận không phải thiết bị gây nhiễu trong crop này.",
        "",
    ),
    (
        "G22-A01-F00013-R02",
        "NN",
        "keep",
        "Theo owner: khoanh một tay, phần tay/bàn rõ và không có vật mơ hồ; chốt N/N.",
        "",
    ),
    (
        "G23-A03-F00009",
        "NN",
        "keep",
        "Quan sát bút, trang/vật liệu giấy và tay, không có mặt thiết bị chưa rõ trong tay anchor. Giữ N/N; không gán unknown chỉ vì có vật đang cầm.",
        "NC-009",
    ),
    (
        "G27-A01-F00016-R02",
        "NP",
        "keep",
        "Tay khoanh có hình học rõ, phần bàn/tay còn lại không có vật mơ hồ. Đề xuất phone N; giữ looking P. Không mở rộng thành mọi crop khoanh tay đều N.",
        "NB-0013,NB-0015",
    ),
    (
        "G27-A02-F00022",
        "UP",
        "keep",
        "Phone nhìn thấy trên bàn phía sau/bên phải anchor nhưng chưa rõ vùng hoạt động thuộc anchor trong cảnh bàn dùng chung, không có tương tác. Crop chỉ còn một người nổi bật không tạo thêm evidence attribution. Giữ U/P; không khẳng định phone thuộc người khác.",
        "",
    ),
    (
        "G27-A03-F00031",
        "UP",
        "keep",
        "Phone rõ ở phía trái mặt bàn trước anchor đứng, nhưng bàn dùng chung và không thấy tương tác hoặc vùng bài riêng. Chưa đủ chốt P/N cho anchor; giữ U/P. Không cắt bỏ phone chỉ để biến thành negative.",
        "",
    ),
]
EXPLICIT = {
    "G04-A03-F00074-R02",
    "G08-A01-F00009-R02",
    "G10-A01-F00008",
    "G10-A01-F00013",
    "G18-A03-F00001",
    "G18-A03-F00010",
    "G19-A01-F00039",
    "G19-A01-F00052",
    "G21-A01-F00007",
    "G22-A01-F00013-R02",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def link(path):
    return Path(os.path.relpath(path, OUT)).as_posix()


def main():
    rows = json.loads((REPORT / "review-index.json").read_text(encoding="utf-8"))
    scope = json.loads((REPORT / "owner-review-scope-20261017.json").read_text(encoding="utf-8"))
    snapshot = REPORT / "owner-review-input-20261017.md"
    assert sha(snapshot) == scope["readme_sha256"] == sha(REPORT / "README.md")
    cases = {cid: (states, action, reason, refs) for cid, states, action, reason, refs in CASES}
    assert len(cases) == len(CASES) == 38 and set(cases) == set(scope["mentioned_ids"])
    comps = json.loads((REPORT / "v10-comparison-20261017.json").read_text(encoding="utf-8"))
    comp_lookup = {r["sample_id"]: r for r in comps}
    v10 = ROOT / "data/processed/pilot-b/pilot-b-20261016-v10"
    baseline = {r.sample_id: r for r in read_records(v10 / "review-ledger.jsonl")}
    for c in comps:
        record = baseline[c["sample_id"]]
        assert record.split == "train"
        assert c["sha256"] == sha(ROOT / c["path"]) == record.crop.crop_sha256
        assert c["labels"] == [record.phone_use.state, record.looking_around.state]
    old = next(r for r in rows if r["candidate_id"] == "G06-A03-F00012")
    replacement = "G06-A03-F00012-R02"
    person, context = [309, 130, 448, 253], [300, 116, 471, 260]
    reason = cases[old["candidate_id"]][2]
    folder = OUT / "candidates" / replacement
    if not folder.exists():
        blob = (ROOT / old["source_path"]).read_bytes()
        source = SourceImage(
            member_key(old["source_member"]),
            sha(ROOT / old["source_path"]),
            "",
            "unassigned",
            blob,
            Image.open(ROOT / old["source_path"]).convert("RGB"),
            (),
        )
        write_pending_crop(
            source,
            PixelBox(*person),
            PixelBox(*context),
            replacement,
            OUT / "candidates",
            states=("N", "N"),
            reason=reason,
            input_size=224,
            fill=(114, 114, 114),
        )
    proposal = json.loads((folder / "proposal.json").read_text(encoding="utf-8"))
    assert proposal["person_xyxy"] == person and proposal["context_xyxy"] == context
    assert proposal["draft_states"] == ["N", "N"] and proposal["draft_reason"] == reason
    assert proposal["source_sha256"] == old["source_sha256"]
    native = Image.open(ROOT / old["source_path"]).convert("RGB").crop(context)
    assert Image.open(folder / "crop.png").convert("RGB").tobytes() == native.tobytes()
    prepared = preview_input(native, 224, (114, 114, 114))
    assert Image.open(folder / "input.png").convert("RGB").tobytes() == prepared.tobytes()
    assert (
        sha(folder / "crop.png") == proposal["crop_sha256"]
        and sha(folder / "input.png") == proposal["input_sha256"]
    )
    ledger = []
    for r in rows:
        cid = r["candidate_id"]
        mentioned = cid in cases
        assert sha(OLD / r["export_path"]) == r["crop_sha256"]
        assert sha(OLD / "candidates" / cid / "input.png") == r["input_sha256"]
        assert sha(ROOT / r["source_path"]) == r["source_sha256"]
        states, action, reason, refs = cases.get(
            cid,
            (
                "".join(r["draft_states"]),
                "keep",
                "Owner mặc định approve vì ID không được nêu trong nhận xét.",
                "",
            ),
        )
        references = refs.split(",") if refs else []
        assert set(references) <= comp_lookup.keys(), references
        status = (
            "approved_explicit"
            if cid in EXPLICIT
            else ("proposed_after_review" if mentioned else "approved_default")
        )
        item = {
            "candidate_id": cid,
            "part": r["part"],
            "group": r["group"],
            "anchor": r["anchor"],
            "original_states": r["draft_states"],
            "review_states": list(states),
            "action": action,
            "decision_status": status,
            "reason": reason,
            "v10_comparators": references,
            "original_crop_sha256": r["crop_sha256"],
            "source_path": r["source_path"],
            "source_sha256": r["source_sha256"],
            "review_crop_path": (OLD / r["export_path"]).relative_to(ROOT).as_posix(),
            "review_input_path": (OLD / "candidates" / cid / "input.png")
            .relative_to(ROOT)
            .as_posix(),
            "included_in_proposed_batch": action != "withhold",
            "usage": "review_only",
            "split": None,
            "enrollment_approved": False,
        }
        if action == "recrop":
            item.update(
                replacement_candidate_id=replacement,
                review_crop_path=(folder / "crop.png").relative_to(ROOT).as_posix(),
                review_input_path=(folder / "input.png").relative_to(ROOT).as_posix(),
                replacement_proposal_path=(folder / "proposal.json").relative_to(ROOT).as_posix(),
                replacement_crop_sha256=proposal["crop_sha256"],
            )
        ledger.append(item)
    counts = dict(Counter(r["decision_status"] for r in ledger))
    summary = {
        "total_original": len(ledger),
        "decision_counts": counts,
        "proposed_active_count": sum(r["included_in_proposed_batch"] for r in ledger),
        "actions": dict(Counter(r["action"] for r in ledger)),
        "label_changes_including_withheld": sum(
            r["original_states"] != r["review_states"] for r in ledger
        ),
        "scope": "Review only; no enrollment, split, training, or broader rubric change.",
    }
    dump(
        REPORT / "owner-review-decisions-20261017.json",
        {
            "summary": summary,
            "owner_input_sha256": sha(snapshot),
            "conversation_clarification": {
                "date": "2026-10-17",
                "owner_reply": "Chốt F00010 là U/P; F00001 là U/N",
                "applies_to": {"G18-A03-F00010": ["U", "P"], "G18-A03-F00001": ["U", "N"]},
                "supersedes": "Only looking_around for G18-A03-F00010 in the README combined row.",
            },
            "records": ledger,
        },
    )
    status_names = {
        "approved_default": "Owner đã duyệt mặc định",
        "approved_explicit": "Owner đã chốt nhãn",
        "proposed_after_review": "Đề xuất sau đối chiếu — chờ owner chốt",
    }
    action_names = {
        "keep": "Giữ crop",
        "recrop": "Thay bằng R02",
        "withhold": "Tạm loại khỏi đợt nhập",
    }
    cards = []
    for r in ledger:
        cid = r["candidate_id"]
        esc = html.escape
        crop = link(ROOT / r["review_crop_path"])
        inp = link(ROOT / r["review_input_path"])
        refs = " · ".join(
            f'<a href="#v10-{esc(ref)}">{esc(ref)}</a>' for ref in r["v10_comparators"]
        )
        previous = ""
        if r["action"] == "recrop":
            original = next(x for x in rows if x["candidate_id"] == cid)
            previous = f'<figure><img loading="lazy" src="{link(OLD / original["export_path"])}"><figcaption>Khung cũ (không sửa bytes)</figcaption></figure>'
        cards.append(
            (
                r["decision_status"],
                f'<article id="{cid}"><h2>{cid}</h2><p><b>{"/".join(r["original_states"])} → {"/".join(r["review_states"])}</b> · {action_names[r["action"]]} · {status_names[r["decision_status"]]}</p><div class="images">{previous}<figure><img loading="lazy" src="{crop}"><figcaption>Crop native {r.get("replacement_candidate_id", cid)}</figcaption></figure><figure><img loading="lazy" width="224" height="224" src="{inp}"><figcaption>Input 224 × 224</figcaption></figure></div><p>{esc(r["reason"])}</p><p><a href="{link(ROOT / r["source_path"])}">Frame gốc cùng thời điểm</a> · Đối chiếu V10 train: {refs or "—"}</p></article>',
            )
        )
    comp_html = "".join(
        f'<article id="v10-{c["sample_id"]}"><h3>{c["sample_id"]} · {"/".join(s[0].upper() for s in c["labels"])}</h3><img loading="lazy" src="{link(ROOT / c["path"])}"><p>V10 train · accepted; chỉ dùng đối chiếu evidence, không tự động sao nhãn.</p></article>'
        for c in comps
    )
    page = '<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Đối chiếu owner review 17/10/2026</title><style>body{font:16px system-ui;max-width:1180px;margin:auto;padding:24px;background:#f1f4f8;color:#14243a}article{background:white;padding:20px;margin:18px 0;border:1px solid #cad4e0;border-radius:10px}h2{font-size:20px}.images{display:flex;align-items:flex-start;gap:16px;flex-wrap:wrap}figure{margin:0}img{max-width:400px;max-height:400px;object-fit:contain}figcaption{font-size:13px;color:#465367}a{color:#1257a1}summary{cursor:pointer;font-weight:bold;padding:18px}p{line-height:1.6}</style><h1>Đối chiếu owner review · 17/10/2026</h1><p>Thứ tự nhãn: phone_use / looking_around. 62 crop duyệt mặc định + 10 ID đã có quyết định rõ; 28 ID còn lại là đề xuất. Phương án: giữ 98 crop (gồm G06 R02), tạm loại G14-A10 và G17-A01. Chưa nhập dataset. Giữ nhóm theo video/anchor.</p><p><b>G18-A03: F00001 U/N; F00010 U/P — đã được owner xác nhận.</b></p><p><a href="#comparisons">33 ví dụ V10 train</a></p>'
    page += "".join(card for status, card in cards if status != "approved_default")
    page += (
        "<details><summary>62 crop owner đã duyệt mặc định — mở để kiểm tra</summary>"
        + "".join(card for status, card in cards if status == "approved_default")
        + '</details><h2 id="comparisons">Ví dụ đối chiếu V10 train</h2>'
        + comp_html
        + "</html>"
    )
    (OUT / "index.html").write_text(page, encoding="utf-8")
    report = """# Kết luận đối chiếu owner review — 17/10/2026

Phạm vi: xử lý 38 ID được nêu trong README; ghi nhận 62 crop còn lại được owner mặc định approve. Đã xem crop native, input 224 và frame cùng thời điểm của các ngoại lệ; đối chiếu 33 ví dụ **train** của V10 cùng hướng xử lý occlusion đã được duyệt. Không mở test/reserve, không chạy model và không mở rộng tìm anchor mới trong lượt này.

## Phương án đề xuất

- **72 ID đã có approval**: 62 mặc định và 10 có nhãn owner chốt rõ. Approval ở đây là review crop/nhãn, không phải enrollment/split.
- **28 ID đã có kết luận đề xuất**, chưa tự ghi thành owner acceptance: 25 giữ khung, 1 recrop, 2 tạm loại.
- Sau khi owner đồng ý phần đề xuất: **98 crop** trong danh sách giữ, gồm **G06-A03-F00012-R02** thay khung cũ. Tạm loại G14-A10-F00018 vì crop còn gây nhiễu anchor/thiết bị và G17-A01-F00012 vì evidence yếu.
- G18-A03-F00001 **U/N**, F00010 **U/P** theo câu trả lời owner trong hội thoại ngày 17/10. Chỉ F00010 looking được làm rõ so với dòng gộp trong README.

[Mở gallery đối chiếu](../../../data/interim/frame-crop-owner-review-20261017/index.html) · [Ledger đủ 100 ID](owner-review-decisions-20261017.json) · [Snapshot nguyên văn nhận xét](owner-review-input-20261017.md) · [33 ví dụ V10 train và SHA](v10-comparison-20261017.json).

## Các điểm cần thống nhất

**Tay khoanh, chống cằm, băng bó:** không phải lý do tự động gán phone U. NB-0013/NB-0015, CB-0055-R1, CB-0742-R1 và NC-009 có negative được duyệt khi phần evidence còn lại đủ rõ. Ngược lại, NBX-004/NBX-005, NC-010 và G4-A03-F105/F125 cho thấy mất evidence quan trọng vẫn có thể U. Đây là đối chiếu từng ảnh, không thay contract thành “tay khuất luôn N”. Băng bó không tự tạo ambiguity về phone; chưa có thử nghiệm để nói các ảnh ấy sẽ làm model nhầm hay cải thiện.

**Mặt lưng thiết bị:** NC-003 U/N và NC-012 N/N của cùng anchor cho thấy phải xét từng frame; không lấy calculator ở frame trước để sửa vật mặt lưng ở frame sau. CB-0024-R1 và CB-0390 cũng giữ U khi camera/loại vật chưa rõ. Đề xuất giữ P cho G05-A01, G18-A01, G20-A03 vì cụm ống kính còn tách được; chuyển các mặt lưng/cạnh thiếu đặc trưng sang U theo bảng. G14-A07 được đề xuất U vì các chấm nhỏ/nhòe chưa đủ chắc; đây là nhận định thị giác cần owner chốt, không phải ngưỡng pixel mới.

**Laptop và looking:** laptop không làm phone_use thành P. Vật trong tay vẫn được xét riêng. G14-A09 không đủ thấy laptop trong crop nên bỏ lý do suy từ frame rộng. Đầu cúi/che mặt hoặc thân nghiêng không tự chứng minh looking P: G14-A02 và G16-A02 đề xuất looking N; G17-A01 tạm loại vì khó phân biệt chắc.

**Thiết bị của ai:** không cần chứng minh quyền sở hữu ngoài đời; cần attribution hành vi/vùng hoạt động cho anchor. Quy tắc này áp dụng cả crop, vì crop bỏ người khác không tạo ra evidence mới rằng vật thuộc anchor. Tuy nhiên, người xem chỉ nhận RGB crop nên không thể dùng lời giải thích dựa trên phần bị cắt mất để cứu một negative gây hiểu nhầm. Vì vậy G06 phải sửa khung. G14-A10 tạm loại vì khung thử vẫn dính thiết bị bên cạnh hoặc cắt sát tay. G27-A02/A03 đề xuất giữ U/P: phone rõ nhưng vùng bàn dùng chung và thiếu tương tác/vùng bài riêng để gán chắc cho anchor; không khẳng định phone thuộc người khác. Owner có thể chốt khác nếu xác nhận evidence không gian trong chính crop đủ — chưa tự nâng thành P.

## Kết luận từng ID được nêu

P/N/U lần lượt là positive/negative/unknown; thứ tự phone_use / looking_around. U bị mask cho target đó khi và chỉ khi đi qua quy trình enrollment; hồ sơ này chưa tạo canonical labels.

| ID | Cũ → kết luận | Xử lý | Trạng thái | Cơ sở |
|---|---|---|---|---|
"""
    for r in ledger:
        if r["candidate_id"] not in cases:
            continue
        report += (
            f"| {r['candidate_id']} | {'/'.join(r['original_states'])} → {'/'.join(r['review_states'])} | {action_names[r['action']]} | {status_names[r['decision_status']]} | {r['reason']}"
            + (f" Đối chiếu: {', '.join(r['v10_comparators'])}." if r["v10_comparators"] else "")
            + " |\n"
        )
    report += """
## Bảo toàn và bước tiếp theo

README có nhận xét, 100 crop gốc, metadata batch và V10 được giữ nguyên. Revision G06 dùng ROI nguồn nguyên pixel, không chỉnh nội dung ảnh; proposal mới còn review_only, owner_approved false, canonical masks [0, 0], split null. Khung người chỉ bao phần cơ thể nhìn thấy; không bắt buộc lấy phần chân đã bị bàn che. Gallery giữ thứ tự video/anchor và cho xem khung cũ cạnh R02.

28 kết luận đề xuất cần owner nghiệm thu theo quy trình của repo; không yêu cầu duyệt lại 72 ID đã chốt. Chưa đóng nguồn video là “đã lấy đủ crop”: đợt bổ sung chờ danh sách owner gửi sau. Mapping lớp/buổi vẫn chưa có, giữ nhóm theo video. Near-duplicate/family và enrollment là bước riêng, không được coi exact SHA khác nhau là bằng chứng độc lập.

Kiểm tra kỹ thuật được lưu tại [validation](owner-review-validation-20261017.json): coverage 100 ID; SHA crop/input/source gốc; snapshot README; nhãn và split train của 33 comparator; ROI/input parity của G06 R02; tham chiếu HTML local. Kiểm tra phần mềm không thay owner acceptance.

Worksheet tạo companion: `finalize_owner_review.py`; `review_owner.py` chỉ dựng scope/board từ snapshot và dừng nếu README đã đổi. Không chạy lại worksheet batch gốc để áp dụng nhãn mới. Các khung thử không được chọn chỉ là evidence thử geometry, không thuộc 98 crop đề xuất.
"""
    (REPORT / "OWNER-REVIEW-20261017.md").write_text(report, encoding="utf-8")
    from html.parser import HTMLParser
    from urllib.parse import unquote

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.refs = []
            self.ids = []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if "id" in a:
                self.ids.append(a["id"])
            for key in ("src", "href"):
                if key in a:
                    self.refs.append(a[key])

    parsed = Links()
    parsed.feed(page)
    assert len(parsed.ids) == len(set(parsed.ids))
    for ref in parsed.refs:
        if ref.startswith("#"):
            assert ref[1:] in parsed.ids
        else:
            assert (OUT / unquote(ref)).exists(), ref
    assert counts == {
        "proposed_after_review": 28,
        "approved_explicit": 10,
        "approved_default": 62,
    } or counts == {"approved_default": 62, "approved_explicit": 10, "proposed_after_review": 28}
    assert len(ledger) == 100 and summary["proposed_active_count"] == 98
    dump(
        REPORT / "owner-review-validation-20261017.json",
        {
            "status": "PASS",
            "summary": summary,
            "original_crop_source_input_sha_checked": 100,
            "owner_snapshot_sha256": sha(snapshot),
            "original_review_index_sha256": sha(REPORT / "review-index.json"),
            "v10_ledger_sha256": sha(v10 / "review-ledger.jsonl"),
            "train_only_comparators_checked": len(comps),
            "g06_native_roi_input_parity": "PASS",
            "html_local_references": len(parsed.refs),
            "html_unique_ids": len(parsed.ids),
            "gallery_sha256": sha(OUT / "index.html"),
            "decision_ledger_sha256": sha(REPORT / "owner-review-decisions-20261017.json"),
            "enrollment_performed": False,
        },
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
