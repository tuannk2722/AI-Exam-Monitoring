"""Owner-review closure worksheet; preserve the audited parent export."""

import hashlib
import html
import json
import re
import zipfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from PIL import Image

from ai_exam_monitoring.data.pilot_schema import PixelBox
from ai_exam_monitoring.data.source_review import (
    SourceImage,
    member_key,
    preview_input,
    write_pending_crop,
)

ROOT = Path.cwd()
REPORT = ROOT / "artifacts/reports/frame-crop-additional-20261017"
OUTPUT = ROOT / "data/interim/frame-crop-additional-20261017"
ROWS = json.loads((REPORT / "review-index.json").read_text(encoding="utf-8"))["records"]
LOOKUP = {r["candidate_id"]: r for r in ROWS}
REVISIONS = [
    (
        "G04-B07-F00037",
        "G04-B07-F00037-R02",
        [153, 67, 249, 156],
        [135, 57, 251, 180],
        "NN",
        "Tách anchor nam: giữ đầu, tay và trang bài; bỏ đầu/thân nữ bên cạnh, còn phần tay ở mép phải.",
    ),
    (
        "G04-B07-F00037",
        "G04-B15-F00037",
        [214, 72, 329, 242],
        [211, 62, 338, 250],
        "NN",
        "Tách anchor nữ áo tím, đặt giữa crop và giữ hai tay/vùng viết. Còn một phần người nam ở mép trái; cắt hết phần đó sẽ mất tay của anchor.",
    ),
    (
        "G05-B02-F00015",
        "G05-B02-F00015-R02",
        [184, 166, 250, 230],
        [181, 157, 258, 242],
        "NP",
        "Chuyển khung sang anchor nữ bên phải, mặt quay sang trái ngoài trang bài theo owner; giữ hai tay/vùng bàn. Nữ bên trái đã có G05-B01 nên không thêm bản trùng.",
    ),
    (
        "G23-B09-F00011",
        "G23-B09-F00011-R02",
        [190, 30, 363, 270],
        [190, 18, 377, 287],
        "NN",
        "Dịch mép trái để bỏ mặt người tiền cảnh; giữ đầu, hai tay và vùng bài của anchor. Nhãn N/N theo owner.",
    ),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare_revisions():
    result = []
    for parent, cid, person, context, states, reason in REVISIONS:
        old = LOOKUP[parent]
        path = ROOT / old["source_path"]
        blob = path.read_bytes()
        im = Image.open(path).convert("RGB")
        assert sha(path) == old["source_sha256"]
        dest = OUTPUT / "candidates" / cid
        if dest.exists():
            row = json.loads((dest / "proposal.json").read_text(encoding="utf-8"))
            assert (
                row["person_xyxy"] == person
                and row["context_xyxy"] == context
                and row["draft_states"] == list(states)
            )
        else:
            row = write_pending_crop(
                SourceImage(
                    member_key(old["source_member"]),
                    old["source_sha256"],
                    "",
                    "unassigned",
                    blob,
                    im,
                    (),
                ),
                PixelBox(*person),
                PixelBox(*context),
                cid,
                OUTPUT / "candidates",
                states=tuple(states),
                reason=reason,
                input_size=224,
                fill=(114, 114, 114),
            )
        crop = Image.open(dest / "crop.png").convert("RGB")
        inp = Image.open(dest / "input.png").convert("RGB")
        assert crop.tobytes() == im.crop(context).tobytes()
        assert inp.tobytes() == preview_input(crop, 224, (114, 114, 114)).tobytes()
        result.append((parent, cid, row))
    return result


if __name__ == "__main__":
    print("Prepared", len(prepare_revisions()), "revisions; exact ROI/input parity PASS")

# Closure follows the owner's conditional approval and delegated exception review.

EXCLUDED = {
    "G01-B01-F00009": "Dấu *: mặt nhỏ và mờ, tay che vùng mặt; không đủ xác nhận hướng nhìn ngoài bài ở chính crop. Ghi nhận đề xuất U/P của owner nhưng áp dụng điều kiện loại khi looking không rõ.",
    "G01-B03-F00009": "Dấu *: đầu hơi hướng trước, mặt và mắt thiếu chi tiết; không đủ phân biệt nhìn bài với nhìn ngoài bài. Không giữ N theo giả định cũ.",
    "G01-B05-F00009": "Dấu *: đầu hơi ngẩng nhưng mắt mờ và tay sát mặt; không đủ kết luận P/N ổn định từ crop.",
    "G03-B04-F00008": "Dấu *: đầu quay cạnh nhưng tay che mắt/mặt; sách dựng trùng hướng quay. Không xác định đang nhìn sách hay ngoài sách, nên loại thay vì suy P từ góc đầu hoặc N từ việc cầm sách.",
    "G06-B02-F00003": "Owner đề nghị loại nếu chữ ảnh hưởng. Chữ phủ sát/chồng vùng tóc và đầu; không có bằng chứng chứng minh vô hại, cắt bỏ chữ sẽ mất đầu. Loại, không inpaint hoặc tạo nhãn U/N để cứu crop.",
    "G06-B03-F00003": "Chữ phủ sát/chồng vùng tóc và đầu, kèm che khuất. Không thể bảo đảm vô hại hoặc bỏ chữ bằng crop mà giữ đủ đầu; loại theo điều kiện owner.",
    "G06-B08-F00005": "Dấu *: mũ/khẩu trang và ảnh mờ làm thiếu dấu hiệu mắt, hướng đầu gần phía trước; chưa đủ phân biệt khỏi vùng bài.",
    "G08-B04-F00001": "Dấu *: mặt quá nhỏ, hướng trước và cúi nhẹ khó phân biệt; không giữ P khi chưa có bằng chứng rõ.",
    "G08-B06-F00001": "Dấu *: hai người chồng nhau; cô lập người nam trước sẽ cắt vùng tay/bài hoặc vẫn giữ người sau. Hướng nhìn cũng không rõ, nên loại theo quyền owner cho phép.",
}
SPECIAL = {
    "G10-B04-F00001": "N/N theo owner, đối chiếu G10-A01-F00008 và các crop viết bài cùng video: tay viết và tay giữ trang đều thấy; không thấy mobile hoặc thiết bị mơ hồ. Không dùng việc các crop khác là N làm bằng chứng duy nhất.",
    "G11-B01-F00008": "N/N theo owner: tay còn lại đặt sát mặt, không mất hoàn toàn; khung hiện tại đã bỏ device người cạnh bên.",
    "G11-B04-F00008": "N/N: đối chiếu crop và frame gốc thấy lưới phím của calculator, không chỉ một mặt kính đen của phone. Phần bàn/tay quan sát còn lại không có phone rõ; giấy che một phần áp dụng ngoại lệ absence đã duyệt.",
}


def write_once(path, payload):
    if path.exists():
        assert path.read_bytes() == payload, f"Would mutate existing closure: {path}"
    else:
        path.write_bytes(payload)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def close():
    parent = REPORT / "review-index.json"
    validation = json.loads((REPORT / "validation.json").read_text(encoding="utf-8"))
    assert sha(parent) == validation["review_index_sha256"]
    assert sha(OUTPUT / "additional-review.zip") == validation["zip_sha256"]
    snapshot = REPORT / "owner-review-input.md"
    comments = {}
    for line in snapshot.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("| G"):
            continue
        columns = [x.strip() for x in line.split("|")]
        for cid in re.findall(r"G\d+-B\d+-F\d+", columns[1]):
            assert cid in LOOKUP and cid not in comments
            comments[cid] = {"result": columns[2], "note": columns[3]}
    assert len(comments) == 34
    assert {cid for cid, c in comments.items() if "*" in c["note"]} <= EXCLUDED.keys()
    for old in ROWS:
        assert sha(ROOT / old["crop_path"]) == old["crop_sha256"]
        assert sha(ROOT / old["source_path"]) == old["source_sha256"]
    parents = {item[0] for item in REVISIONS}
    records = []
    decisions = []
    for old in ROWS:
        cid = old["candidate_id"]
        comment = comments.get(cid)
        states = old["draft_states"]
        if comment and re.fullmatch("[PNU]/[PNU]", comment["result"]):
            states = comment["result"].split("/")
        if cid == "G11-B04-F00008":
            states = ["N", "N"]
        action = "exclude" if cid in EXCLUDED else ("replace" if cid in parents else "keep")
        reason = EXCLUDED.get(
            cid,
            SPECIAL.get(
                cid,
                comment["note"]
                if comment
                else "Owner đã review toàn bộ và duyệt các crop không nêu trong bảng.",
            ),
        )
        decisions.append(
            {
                "original_candidate_id": cid,
                "action": action,
                "original_states": old["draft_states"],
                "review_states": states if action != "exclude" else None,
                "owner_comment": comment,
                "resolution_reason": reason,
                "replacements": [x[1] for x in REVISIONS if x[0] == cid],
            }
        )
        if action != "keep":
            continue
        row = dict(old)
        for key in ["canonical_targets", "canonical_mask"]:
            row.pop(key, None)
        row.update(
            review_states=states,
            owner_approved=True,
            decision_status="accepted",
            approval_basis="owner_default_approval"
            if comment is None
            else "owner_review_and_delegated_resolution",
            resolution_reason=reason,
            original_candidate_id=cid,
            input_path=(OUTPUT / "candidates" / cid / "input.png").relative_to(ROOT).as_posix(),
            enrollment_approved=False,
        )
        records.append(row)
    for parent_id, cid, proposal in prepare_revisions():
        old = LOOKUP[parent_id]
        row = dict(old)
        row.update(proposal)
        for key in ["canonical_targets", "canonical_mask"]:
            row.pop(key, None)
        row.update(
            candidate_id=cid,
            anchor=cid.split("-")[1],
            original_candidate_id=parent_id,
            review_states=proposal["draft_states"],
            owner_approved=True,
            decision_status="accepted",
            approval_basis="owner_requested_recrop_and_delegated_finalization",
            resolution_reason=proposal["draft_reason"],
            crop_path=(OUTPUT / "candidates" / cid / "crop.png").relative_to(ROOT).as_posix(),
            input_path=(OUTPUT / "candidates" / cid / "input.png").relative_to(ROOT).as_posix(),
            proposal_path=(OUTPUT / "candidates" / cid / "proposal.json")
            .relative_to(ROOT)
            .as_posix(),
            native_size=list(Image.open(OUTPUT / "candidates" / cid / "crop.png").size),
            enrollment_approved=False,
        )
        records.append(row)
    records.sort(key=lambda x: (x["group"], x["anchor"], x["frame_number"], x["candidate_id"]))
    assert len(records) == 172 and len({x["candidate_id"] for x in records}) == 172
    assert len({x["crop_sha256"] for x in records}) == 172
    assert len([d for d in decisions if d["action"] == "exclude"]) == 9
    assert len([d for d in decisions if d["action"] == "replace"]) == 3
    receipt = {
        "date": "2026-10-17",
        "status": "accepted_crop_labels_membership_only",
        "parent_review_index_sha256": sha(REPORT / "review-index.json"),
        "owner_review_input_sha256": sha(snapshot),
        "authority": "Owner duyệt các crop không nêu; yêu cầu kiểm dấu *, giữ khi đủ bằng chứng và loại khi không rõ; cho phép chốt ít ngoại lệ để tránh thêm vòng review.",
        "scope": "Không enrollment, assignment/split, train hoặc test; không sửa bộ 98 đã chốt.",
        "count": len(records),
        "default_approved_count": 146,
        "reviewed_original_ids": 34,
        "excluded_original_ids": 9,
        "replaced_original_ids": 3,
        "replacement_outputs": 4,
        "records": records,
        "decisions": decisions,
    }
    write_once(REPORT / "owner-accepted.json", json_bytes(receipt))
    page = [
        '<!doctype html><html lang="vi"><meta charset="utf-8"><title>172 crop bổ sung đã chốt</title><style>body{font:16px system-ui;max-width:1180px;margin:auto;padding:24px;background:#edf0f4}article{background:white;padding:16px;margin:16px 0}img{max-width:360px;max-height:360px;margin:8px;vertical-align:top}h2{font-size:19px}a{color:#1255a3}</style><h1>172 crop bổ sung đã chốt</h1><p>Phone / looking_around. 146 crop duyệt mặc định; 34 ID đã đối chiếu. Loại 9, thay 3 crop bằng 4 khung cắt. Chưa enrollment/split/train. Ảnh trái: native crop; ảnh phải: input 224 px.</p>'
    ]
    exported = []
    for row in records:
        crop = ROOT / row["crop_path"]
        inp = ROOT / row["input_path"]
        source = ROOT / row["source_path"]
        assert sha(crop) == row["crop_sha256"] and sha(inp) == row["input_sha256"]
        im = Image.open(source).convert("RGB")
        ci = Image.open(crop).convert("RGB")
        assert im.crop(row["context_xyxy"]).tobytes() == ci.tobytes()
        assert (
            Image.open(inp).convert("RGB").tobytes()
            == preview_input(ci, 224, (114, 114, 114)).tobytes()
        )
        cp = crop.relative_to(OUTPUT).as_posix()
        ip = inp.relative_to(OUTPUT).as_posix()
        exported.extend([crop, inp])
        page.append(
            f'<article id="{row["candidate_id"]}"><h2>{row["candidate_id"]} · {"/".join(row["review_states"])}</h2><img loading="lazy" src="{cp}" alt="Native crop"><img loading="lazy" src="{ip}" alt="Input 224"><p>{html.escape(row["resolution_reason"])}</p></article>'
        )
    page.append("</html>")
    write_once(OUTPUT / "accepted.html", "\n".join(page).encode("utf-8"))
    archive = OUTPUT / "accepted-172.zip"
    assert not archive.exists(), "Do not reseal an existing archive"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in exported:
            z.write(f, f.relative_to(OUTPUT).as_posix())
        z.write(OUTPUT / "accepted.html", "accepted.html")
        z.write(REPORT / "owner-accepted.json", "owner-accepted.json")
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist()) == 346

    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.refs = []

        def handle_starttag(self, tag, attrs):
            self.refs.extend(v for k, v in attrs if k in ("src", "href"))

    parser = Links()
    parser.feed((OUTPUT / "accepted.html").read_text(encoding="utf-8"))
    for link in parser.refs:
        u = urlsplit(link)
        assert not u.scheme and (OUTPUT / unquote(u.path)).is_file()
    assert sha(REPORT / "review-index.json") == validation["review_index_sha256"]
    assert sha(OUTPUT / "additional-review.zip") == validation["zip_sha256"]
    result = {
        "status": "PASS",
        "accepted_count": 172,
        "default_approved_count": 146,
        "owner_review_ids": 34,
        "excluded": 9,
        "replaced_originals": 3,
        "new_geometry_outputs": 4,
        "states": dict(Counter("/".join(r["review_states"]) for r in records)),
        "owner_receipt_sha256": sha(REPORT / "owner-accepted.json"),
        "accepted_html_sha256": sha(OUTPUT / "accepted.html"),
        "accepted_zip_sha256": sha(archive),
        "exact_source_crop_input_parity": True,
        "all_parent_crop_hashes_preserved": True,
        "parent_ledger_and_zip_preserved": True,
        "zip_crc_and_membership": True,
        "gallery_links": len(parser.refs),
        "enrollment_performed": False,
    }
    write_once(REPORT / "owner-accepted-validation.json", json_bytes(result))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    close()
