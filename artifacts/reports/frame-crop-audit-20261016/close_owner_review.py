import hashlib
import html
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path.cwd()
p = ROOT / "artifacts/reports/frame-crop-audit-20261016"
out = ROOT / "data/interim/frame-crop-accepted-20261017"
out.mkdir(exist_ok=True)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


prior = p / "owner-review-decisions-20261017.json"
data = json.loads(prior.read_text(encoding="utf-8"))
validation = json.loads((p / "owner-review-validation-20261017.json").read_text())
assert sha(prior) == validation["decision_ledger_sha256"]
changes = {"G23-A03-F00009": ["U", "N"], "G27-A02-F00022": ["P", "P"], "G27-A03-F00031": ["P", "P"]}
accepted = []
excluded = []
for old in data["records"]:
    r = dict(old)
    cid = r["candidate_id"]
    r["review_states"] = changes.get(cid, r["review_states"])
    r["decision_status"] = "owner_approved"
    r["owner_approved"] = True
    r["approval_scope"] = "crop geometry, labels and batch membership; no enrollment/split"
    if cid in changes:
        r["reason"] = "Owner quyết định ngày 17/10: " + (
            "vật màu trắng trong tay chưa phân biệt được, U/N."
            if cid.startswith("G23")
            else "phone trong crop được owner gán cho anchor; P/P."
        )
    if not r["included_in_proposed_batch"]:
        r["decision_status"] = "owner_excluded"
        excluded.append(r)
        continue
    r["original_candidate_id"] = cid
    r["candidate_id"] = r.get("replacement_candidate_id", cid)
    src = ROOT / r["review_crop_path"]
    expected = r.get("replacement_crop_sha256", r["original_crop_sha256"])
    assert sha(src) == expected
    dst = (
        out
        / "crops"
        / f"part_{r['part']:02}"
        / r["group"]
        / r["anchor"]
        / (r["candidate_id"] + ".png")
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        assert sha(dst) == expected
    else:
        shutil.copyfile(src, dst)
    r["accepted_crop_path"] = dst.relative_to(ROOT).as_posix()
    r["crop_sha256"] = expected
    accepted.append(r)
assert len(accepted) == 98 and len(excluded) == 2
receipt = {
    "date": "2026-10-17",
    "owner_message": "Tôi đã review và đưa ra quyết định cho các crop mới thay đổi, những crop mà tôi không nhắc đến bên dưới thì approved. G23-A03-F00009: U/N. G27-A02-F00022, G27-A03-F00031: P/P. Hãy chốt 98 crop mới này.",
    "parent_decisions_sha256": sha(prior),
    "explicit_label_corrections": changes,
    "scope": "Accept 98 crop geometry/labels/membership; exclude two; no enrollment, split or training. G27 attribution accepted for these two crops; no blanket nearest-phone assignment.",
    "records": accepted,
    "excluded": excluded,
}
raw = json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
dest = p / "owner-accepted-20261017.json"
if dest.exists():
    assert dest.read_text(encoding="utf-8") == raw
else:
    dest.write_text(raw, encoding="utf-8")
(out / "metadata.json").write_text(raw, encoding="utf-8")
page = '<!doctype html><html lang="vi"><meta charset="utf-8"><title>98 crop đã duyệt</title><style>body{font:16px system-ui;max-width:1100px;margin:auto;padding:24px;background:#eef2f6}article{background:white;padding:16px;margin:14px 0}img{max-width:360px;max-height:400px}h2{font-size:18px}</style><h1>98 crop đã được owner duyệt · 17/10/2026</h1><p>Phone / looking. G23-A03 U/N; G27-A02 và A03 P/P. G06 R02 thay bản cũ; G14-A10 và G17-A01 bị loại. Chưa enrollment/split/train.</p>'
for r in accepted:
    page += f'<article id="{r["candidate_id"]}"><h2>{r["candidate_id"]} · {"/".join(r["review_states"])}</h2><img loading="lazy" src="{Path(r["accepted_crop_path"]).relative_to(out.relative_to(ROOT)).as_posix()}"><p>{html.escape(r["reason"])}</p></article>'
(out / "index.html").write_text(page + "</html>", encoding="utf-8")
with zipfile.ZipFile(out / "accepted-98.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted((out / "crops").rglob("*.png")):
        z.write(f, f.relative_to(out).as_posix())
    z.write(out / "metadata.json", "metadata.json")
    z.write(out / "index.html", "index.html")
with zipfile.ZipFile(out / "accepted-98.zip") as z:
    assert z.testzip() is None and sum(x.endswith(".png") for x in z.namelist()) == 98
(p / "OWNER-ACCEPTED-20261017.md").write_text(
    """# Chốt 98 crop — owner duyệt ngày 17/10/2026

Owner duyệt toàn bộ phương án trước, với ba sửa cuối: **G23-A03-F00009 U/N** vì vật trắng trong tay chưa rõ; **G27-A02-F00022 và G27-A03-F00031 P/P** vì owner xác nhận phone trong crop gắn với anchor. Không còn 28 đề xuất chờ duyệt của vòng này.

Giữ **98 crop**, gồm **G06-A03-F00012-R02** thay khung cũ. Loại G14-A10-F00018 và G17-A01-F00012. G18-A03-F00001 U/N, F00010 U/P giữ đúng quyết định trước. Nhóm theo video và anchor; không ghép danh tính/lớp khi chưa có mapping.

[Receipt và đủ 98 nhãn/SHA](owner-accepted-20261017.json) · [Gallery đã chốt](../../../data/interim/frame-crop-accepted-20261017/index.html) · [ZIP 98 crop và metadata](../../../data/interim/frame-crop-accepted-20261017/accepted-98.zip).

Receipt này supersede trạng thái chờ duyệt của OWNER-REVIEW-20261017.md và ledger đề xuất, không sửa bytes các hồ sơ đó. Approval chỉ cho crop/nhãn/membership; chưa nhập V10, chưa assignment/split hoặc train. Crop bổ sung từ additional.zip là batch review riêng.

Phone U có mask 0 nên không tạo nhãn negative đối nghịch trong loss/metric; nó loại target phone khỏi supervision. Tuy vậy, dùng U cho positive owner đã xác nhận sẽ mất tín hiệu học hợp lệ. Vì vậy hai G27 được chốt P theo quyết định cụ thể; không dùng số người còn trong crop để tự gán mọi thiết bị lân cận cho mọi anchor khác.

Kiểm: 98 PNG exact SHA từ crop đã review (gồm revision G06), đúng ba correction cuối và hai ID loại; ZIP CRC/membership PASS. Không sửa dataset hiện hành.
""",
    encoding="utf-8",
)
(p / "owner-accepted-validation-20261017.json").write_text(
    json.dumps(
        {
            "status": "PASS",
            "count": 98,
            "excluded": 2,
            "receipt_sha256": sha(dest),
            "zip_sha256": sha(out / "accepted-98.zip"),
            "original_proposal_preserved": sha(prior) == validation["decision_ledger_sha256"],
            "enrollment_performed": False,
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print("Closed 98 accepted crops; 2 excluded")
