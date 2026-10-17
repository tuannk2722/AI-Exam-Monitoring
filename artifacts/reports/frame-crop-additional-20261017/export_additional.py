"""Task worksheet: export reviewed proposals using the existing pending-crop API."""

import hashlib
import html
import json
import zipfile
from collections import Counter
from pathlib import Path

from choices import CHOICES, GROUP_NOTES, REJECTED, TRIAL_CHOICES
from PIL import Image, ImageDraw

from ai_exam_monitoring.data.pilot_schema import PixelBox
from ai_exam_monitoring.data.source_review import (
    SourceImage,
    member_key,
    preview_input,
    write_pending_crop,
)

R = Path.cwd()
P = R / "artifacts/reports/frame-crop-additional-20261017"
OUTPUT = R / "data/interim/frame-crop-additional-20261017"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


inv = json.loads(
    (R / "artifacts/reports/frame-crop-audit-20261016/inventory.json").read_text(encoding="utf-8")
)
sources = {x["path"]: x for x in inv["frames"]}
marked = json.loads((P / "inventory.json").read_text(encoding="utf-8"))
accepted_path = R / "artifacts/reports/frame-crop-audit-20261016/owner-accepted-20261017.json"
accepted = json.loads(accepted_path.read_text(encoding="utf-8"))["records"]
rows = []
exports = []
for g, a, f, p, c, s, n in sorted(CHOICES):
    cid = f"{g}-{a}-F{f:05}"
    sp = f"data/interim/frame-crop-audit-20261016/frames/{g}/frame_{f:05}.jpg"
    src = sources[sp]
    blob = (R / sp).read_bytes()
    assert sha(R / sp) == src["sha256"]
    im = Image.open(R / sp).convert("RGB")
    dst = OUTPUT / "candidates" / cid
    if dst.exists():
        row = json.loads((dst / "proposal.json").read_text(encoding="utf-8"))
        assert (
            row["person_xyxy"] == p
            and row["context_xyxy"] == c
            and row["draft_states"] == list(s)
            and row["draft_reason"] == n
        )
    else:
        row = write_pending_crop(
            SourceImage(member_key(src["member"]), src["sha256"], "", "unassigned", blob, im, ()),
            PixelBox(*p),
            PixelBox(*c),
            cid,
            OUTPUT / "candidates",
            states=tuple(s),
            reason=n,
            input_size=224,
            fill=(114, 114, 114),
        )
    crop = Image.open(dst / "crop.png").convert("RGB")
    inp = Image.open(dst / "input.png").convert("RGB")
    assert crop.tobytes() == im.crop(c).tobytes()
    assert inp.tobytes() == preview_input(crop, 224, (114, 114, 114)).tobytes()
    assert (
        sha(dst / "crop.png") == row["crop_sha256"]
        and sha(dst / "input.png") == row["input_sha256"]
    )
    rel = Path("crops") / f"part_{src['part']:02}" / g / a / f"{cid}.png"
    target = OUTPUT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert sha(target) == row["crop_sha256"]
    else:
        target.write_bytes((dst / "crop.png").read_bytes())
    overlay = im.copy()
    d = ImageDraw.Draw(overlay)
    d.rectangle(c, outline="#ffb000", width=2)
    d.rectangle(p, outline="#00ddff", width=2)
    d.text((c[0], max(0, c[1] - 12)), cid, fill="#ff0000")
    overlay.save(dst / "context.jpg", quality=96)
    row.update(
        group=g,
        anchor=a,
        part=src["part"],
        frame_number=f,
        source_path=sp,
        source_member=src["member"],
        source_archive_sha256=inv["archives"][src["part"] - 1]["sha256"],
        crop_path=(OUTPUT / rel).relative_to(R).as_posix(),
        proposal_path=(dst / "proposal.json").relative_to(R).as_posix(),
        native_size=list(crop.size),
        local_anchor_only=True,
        related_accepted_candidates=[x["candidate_id"] for x in accepted if x["group"] == g],
        qa="native crop and 224 px input visually reviewed; exact ROI/input parity verified",
    )
    rows.append(row)
    exports.extend(
        [rel, Path("candidates") / cid / "input.png", Path("candidates") / cid / "context.jpg"]
    )
assert len(rows) == len(set(x["candidate_id"] for x in rows))
assert not (set(x["crop_sha256"] for x in rows) & set(x["crop_sha256"] for x in accepted))
assert len(set(x["crop_sha256"] for x in rows)) == len(rows)
ledger = {
    "status": "draft_pending_owner_review",
    "date": "2026-10-17",
    "accepted_parent_sha256": sha(accepted_path),
    "additional_archive_sha256": marked["archive_sha256"],
    "target_order": ["phone_use", "looking_around"],
    "semantics_ref": "docs/data.md; E004-PHONE-OCCLUSION-20261015; specific G27 owner attribution 2026-10-17",
    "scope": "review-only, no V10 enrollment, no split/train/test access; local anchors within each video only",
    "records": rows,
}
save(P / "review-index.json", ledger)
save(OUTPUT / "metadata.json", ledger)
save(
    P / "rejected-trials.json",
    {
        "reason_scope": "Rejected trial candidates; not a count of all marked people. Original bytes and final accepted batch untouched.",
        "rejected": REJECTED,
        "trials": [
            {
                "group": g,
                "anchor": a,
                "frame": f,
                "person_xyxy": p,
                "context_xyxy": c,
                "states": s,
                "reason": n,
            }
            for g, a, f, p, c, s, n in TRIAL_CHOICES
        ],
    },
)
coverage = []
for m in marked["records"]:
    best = m["matches"][0]
    g = best["group"]
    sp = best["source_path"]
    assert sha(R / sp) == best["source_sha256"]
    assert sha(R / m["marked_path"]) == m["sha256"]
    coverage.append(
        {
            "marked_member": m["member"],
            "marked_sha256": m["sha256"],
            "source_path": sp,
            "source_sha256": best["source_sha256"],
            "group": g,
            "mapping_review": "visually checked against original source sequence",
            "selected_from_this_frame": [x["candidate_id"] for x in rows if x["source_path"] == sp],
            "already_accepted_from_this_frame": [
                x["candidate_id"] for x in accepted if x["source_path"] == sp
            ],
            "group_review_note": GROUP_NOTES[g],
            "review_scope": "Frame and marked leads inspected; nearby-frame choices grouped in gallery. This is frame coverage, not exhaustive person annotation.",
        }
    )
save(P / "marked-frame-coverage.json", {"count": len(coverage), "records": coverage})
parts = [
    '<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Crop bổ sung · owner review</title><style>body{font:16px system-ui;background:#eff2f5;margin:24px}nav{position:sticky;top:0;background:white;padding:12px;z-index:1}a{margin-right:12px}article{background:white;border:1px solid #bbc;padding:16px;margin:18px 0;scroll-margin-top:70px}.images{display:flex;align-items:flex-start;gap:18px;flex-wrap:wrap}figure{margin:0}img.source{max-width:640px;max-height:420px}img.crop{max-width:360px;max-height:420px}img.input{width:224px;height:224px}details{margin:12px 0}h2{scroll-margin-top:80px}.small{font-size:14px;color:#444}</style>'
]
parts.append(
    f"<h1>{len(rows)} crop bổ sung — Draft chờ owner review</h1><p>Đã xem 187 ảnh đánh dấu thuộc 19 video. Crop lấy từ frame gốc không có nét vẽ. Thứ tự nhãn: phone / looking. Nhãn hiển thị là đề xuất; chưa nhập dataset hoặc train.</p><p>Khung xanh: person anchor; khung vàng: context crop. Mỗi người trong cùng video nằm cạnh nhau. Không suy danh tính giữa video. Các khung nhỏ/che một phần vẫn cần owner đánh giá khả năng dùng; không dùng upscaling để tạo thêm evidence.</p>"
)
groups = sorted(set(x["group"] for x in rows))
parts.append("<nav>" + "".join(f'<a href="#{g}">{g}</a>' for g in groups) + "</nav>")
for g in groups:
    parts.append(f'<h2 id="{g}">{g}</h2><p>{html.escape(GROUP_NOTES[g])}</p>')
    for x in [x for x in rows if x["group"] == g]:
        cid = x["candidate_id"]
        rel = Path(x["crop_path"]).relative_to(OUTPUT.relative_to(R)).as_posix()
        base = f"candidates/{cid}"
        parts.append(
            f'<article id="{cid}"><h3>{cid} · {"/".join(x["draft_states"])}</h3><p>{html.escape(x["draft_reason"])}</p><div class="images"><figure><img class="crop" loading="lazy" src="{rel}"><figcaption>Crop native {x["native_size"][0]} × {x["native_size"][1]}</figcaption></figure><figure><img class="input" loading="lazy" src="{base}/input.png"><figcaption>Input 224 × 224</figcaption></figure></div><details><summary>Frame gốc và vị trí anchor</summary><img class="source" loading="lazy" src="{base}/context.jpg"></details><p class="small">SHA crop: {x["crop_sha256"]}</p></article>'
        )
parts.append("</html>")
(OUTPUT / "index.html").write_text("".join(parts), encoding="utf-8")
exports += [Path("index.html"), Path("metadata.json")]
with zipfile.ZipFile(OUTPUT / "additional-review.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for rel in sorted(exports):
        z.write(OUTPUT / rel, rel.as_posix())
with zipfile.ZipFile(OUTPUT / "additional-review.zip") as z:
    assert z.testzip() is None and len(z.namelist()) == len(exports)
validation = {
    "status": "PASS",
    "crop_count": len(rows),
    "videos": len(groups),
    "local_anchors": len(set((x["group"], x["anchor"]) for x in rows)),
    "marked_frames": len(coverage),
    "states": dict(Counter("".join(x["draft_states"]) for x in rows)),
    "exact_source_crop_and_input_parity": True,
    "duplicate_crop_hashes": 0,
    "exact_duplicates_with_accepted_98": 0,
    "review_index_sha256": sha(P / "review-index.json"),
    "zip_sha256": sha(OUTPUT / "additional-review.zip"),
    "owner_acceptance": False,
    "enrollment_performed": False,
}
save(P / "validation.json", validation)
print(json.dumps(validation))
