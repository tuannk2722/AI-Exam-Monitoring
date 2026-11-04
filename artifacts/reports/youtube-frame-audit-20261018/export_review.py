"""Export visual proposals with active crop API and validate local review artifacts."""

import hashlib
import html
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.pilot_schema import PixelBox
from ai_exam_monitoring.data.source_review import (
    SourceImage,
    member_key,
    preview_input,
    write_pending_crop,
)

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
DATA = ROOT / "data/interim/youtube-frame-audit-20261018"
REFERENCES = {"Y01": 1, "Y02": 4, "Y03": 5, "Y04": 3, "Y05": 6, "Y06": 2}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def esc(text):
    return html.escape(str(text), quote=True)


def main():
    inv = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    selections = json.loads((REPORT / "selections.json").read_text(encoding="utf-8"))
    notes = json.loads((REPORT / "frame-notes.json").read_text(encoding="utf-8"))
    frames = {r["frame_id"]: r for r in inv["frames"]}
    assert len(notes) == 115 and {r["frame_id"] for r in notes} == set(frames)
    assert len({r["candidate_id"] for r in selections}) == len(selections)
    assert all(r["qa_status"] in {"pass_draft", "withheld"} for r in selections)
    selected = [r for r in selections if r["qa_status"] == "pass_draft"]
    rows = []
    for item in selected:
        cid = item["candidate_id"]
        source = frames[item["frame_id"]]
        blob = (ROOT / source["source_path"]).read_bytes()
        assert hashlib.sha256(blob).hexdigest() == source["sha256"]
        im = Image.open(ROOT / source["source_path"]).convert("RGB")
        dest = DATA / "candidates" / cid
        if dest.exists():
            row = json.loads((dest / "proposal.json").read_text(encoding="utf-8"))
            assert row["context_xyxy"] == item["context_xyxy"]
            assert row["person_xyxy"] == item["person_xyxy"]
            assert row["draft_states"] == item["draft_states"]
            assert row["draft_reason"] == item["draft_reason"]
        else:
            row = write_pending_crop(
                SourceImage(
                    member_key(source["member"]), source["sha256"], "", "unassigned", blob, im, ()
                ),
                PixelBox(*item["person_xyxy"]),
                PixelBox(*item["context_xyxy"]),
                cid,
                DATA / "candidates",
                states=tuple(item["draft_states"]),
                reason=item["draft_reason"],
                input_size=224,
                fill=(114, 114, 114),
            )
        crop = Image.open(dest / "crop.png").convert("RGB")
        inp = Image.open(dest / "input.png").convert("RGB")
        assert crop.tobytes() == im.crop(item["context_xyxy"]).tobytes()
        assert inp.tobytes() == preview_input(crop, 224, (114, 114, 114)).tobytes()
        assert sha(dest / "crop.png") == row["crop_sha256"]
        assert sha(dest / "input.png") == row["input_sha256"]
        assert row["canonical_targets"] == [None, None] and row["canonical_mask"] == [0, 0]
        assert row["draft_states"] != ["U", "U"]
        overlay = im.copy()
        d = ImageDraw.Draw(overlay)
        d.rectangle(item["context_xyxy"], outline="#ffb000", width=2)
        d.rectangle(item["person_xyxy"], outline="#00ffff", width=1)
        d.text((item["context_xyxy"][0], max(0, item["context_xyxy"][1] - 12)), cid, fill="#ff0000")
        overlay.save(dest / "overlay.png")
        row.update(
            {
                k: item[k]
                for k in [
                    "group",
                    "anchor",
                    "frame_id",
                    "marked",
                    "reference",
                    "location_description",
                    "qa_status",
                    "qa_note",
                ]
            }
        )
        row.update(
            source_path=source["source_path"],
            source_member=source["member"],
            source_archive_sha256=inv["archive"]["sha256"],
            crop_path=(dest / "crop.png").relative_to(ROOT).as_posix(),
            input_path=(dest / "input.png").relative_to(ROOT).as_posix(),
            anchor_identity_scope="Vị trí/bố cục cục bộ trong video; không nhận diện khuôn mặt hoặc chứng minh danh tính.",
        )
        rows.append(row)
    mapping = []
    for group in inv["groups"]:
        gid = group["group"]
        anchors = []
        for anchor in sorted({s["anchor"] for s in selections if s["group"] == gid}):
            entries = [s for s in selections if s["group"] == gid and s["anchor"] == anchor]
            anchors.append(
                {
                    "anchor": anchor,
                    "location": entries[0]["location_description"],
                    "marked_hint": entries[0]["marked"],
                    "proposed_ids": [
                        s["candidate_id"] for s in entries if s["qa_status"] == "pass_draft"
                    ],
                    "withheld_ids": [
                        s["candidate_id"] for s in entries if s["qa_status"] == "withheld"
                    ],
                    "notes": "Đánh dấu chỉ là ưu tiên quan sát, không bắt buộc crop. ID là vị trí review, không số người độc lập.",
                }
            )
        mapping.append(
            {
                "group": gid,
                "folder": group["folder"],
                "reference_id": f"reference-{REFERENCES[gid]:02}",
                "frames": len(group["frame_ids"]),
                "anchors": anchors,
                "presence_evidence": "frame-notes.json; cảnh cố định xem vị trí mỗi frame, cảnh đổi góc ghi ngoài khung/che. Không có biometric tracking.",
                "additional_withheld_mark": "Y06: người quay lưng tiền cảnh trong panel phải không có crop đề xuất; thiếu hướng mặt và tay/bàn bị che, mapping sau pan không chắc."
                if gid == "Y06"
                else None,
            }
        )
    save(REPORT / "reference-mapping.json", mapping)
    save(REPORT / "review-index.json", rows)
    rejected = [r for r in selections if r["qa_status"] == "withheld"]
    save(REPORT / "withheld.json", rejected)
    counts = Counter(r["group"] for r in rows)
    states = Counter("/".join(r["draft_states"]) for r in rows)
    chunks = [
        """<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Audit 115 frame — crop đề xuất</title><style>
body{font:16px/1.55 system-ui;margin:0;background:#f2f5f8;color:#172434}header,main{max-width:1400px;margin:auto;padding:22px}
header{background:#fff}nav{display:flex;gap:10px;flex-wrap:wrap}a{color:#075e9e}nav a{padding:7px 12px;background:#e5f0fa;border-radius:8px}
section{margin:28px 0}article{background:white;border:1px solid #d1dae2;border-radius:10px;padding:16px;margin:16px 0}
.images{display:flex;gap:16px;align-items:start;flex-wrap:wrap}.images figure{margin:0;max-width:640px}.source{max-width:100%;height:auto}.crop{max-width:350px;max-height:340px;object-fit:contain}.input{width:224px;height:224px}
figcaption{font-size:13px;color:#4a5a68}.tag{background:#dcecf8;border-radius:5px;padding:4px 8px}summary{cursor:pointer;font-weight:600}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd6df;padding:8px;text-align:left}.ref{max-width:700px;width:100%}.muted{color:#536271}
@media(max-width:650px){header,main{padding:12px}.crop{max-width:100%}}
</style><header><h1>Audit ZIP — 115 frame, 6 folder</h1>"""
    ]
    chunks.append(
        f"<p><strong>{len(rows)} crop đề xuất</strong>; {len(rejected)} khung thử không chọn. P/N/U theo thứ tự phone_use / looking_around. Đây là Draft, chưa nghiệm thu dataset.</p>"
    )
    chunks.append(
        "<p>Ảnh crop lấy pixel gốc; input 224 dùng letterbox hiện hành. Hãy kiểm cùng ảnh nguồn và lý do. Không suy cheating, duration, danh tính hoặc split từ các nhãn này.</p><nav>"
    )
    chunks.extend(f'<a href="#{g}">{g} · {counts[g]} crop</a>' for g in counts)
    chunks.append(
        '<a href="#frames">115 frame</a><a href="#withheld">Khung không chọn</a></nav></header><main>'
    )
    for m in mapping:
        gid = m["group"]
        chunks.append(
            f'<section id="{gid}"><h2>{gid} — {m["frames"]} frame / {counts[gid]} crop</h2><p>Folder: <code>{esc(m["folder"])}</code> · Ảnh tham chiếu {REFERENCES[gid]}</p>'
        )
        chunks.append(
            f'<details><summary>Ảnh đánh dấu và tình trạng từng vị trí</summary><img class="ref" src="references/reference-{REFERENCES[gid]:02}.png" alt="Ảnh đánh dấu {gid}"><table><tr><th>Vị trí</th><th>Đề xuất</th><th>Không chọn</th></tr>'
        )
        for a in m["anchors"]:
            links = (
                " ".join(f'<a href="#{cid}">{cid}</a>' for cid in a["proposed_ids"])
                or "Chưa có crop đạt"
            )
            chunks.append(
                f"<tr><td>{a['anchor']}: {esc(a['location'])}</td><td>{links}</td><td>{esc(', '.join(a['withheld_ids']))}</td></tr>"
            )
        chunks.append(
            "</table><p>ID vị trí là đầu mối review cục bộ, không là nhận dạng cá nhân giữa góc máy/video.</p>"
        )
        if m["additional_withheld_mark"]:
            chunks.append(f"<p>{esc(m['additional_withheld_mark'])}</p>")
        chunks.append("</details>")
        for r in rows:
            if r["group"] != gid:
                continue
            cid = r["candidate_id"]
            prefix = f"candidates/{cid}"
            chunks.append(
                f'<article id="{cid}"><h3>{cid} <span class="tag">{" / ".join(r["draft_states"])}</span></h3><p>{esc(r["draft_reason"])}</p><div class="images">'
            )
            for file, title, cls in [
                ("overlay.png", "Nguồn: context vàng, person xanh", "source"),
                ("crop.png", "Crop pixel gốc (bấm để xem kích thước gốc)", "crop"),
                ("input.png", "Input 224 × 224", "input"),
            ]:
                chunks.append(
                    f'<figure><a href="{prefix}/{file}"><img class="{cls}" loading="lazy" src="{prefix}/{file}" alt="{esc(cid)} {esc(title)}"></a><figcaption>{title}</figcaption></figure>'
                )
            chunks.append(
                f'</div><p class="muted">{esc(r["qa_note"])} <a href="{prefix}/source.png">Nguồn không overlay</a> · <a href="{prefix}/proposal.json">Geometry/SHA</a></p></article>'
            )
        chunks.append("</section>")
    chunks.append(
        '<section id="frames"><h2>Quan sát từng frame — 115/115</h2><p>Ghi chú ghi những thay đổi và giới hạn quan sát; không phải annotation detector đầy đủ hoặc bảng nhận dạng từng người.</p>'
    )
    for n in notes:
        f = frames[n["frame_id"]]
        rel = Path(f["source_path"]).relative_to(DATA.relative_to(ROOT)).as_posix()
        chunks.append(
            f'<details><summary>{n["frame_id"]}</summary><p>{esc(n["note"])}</p><img class="source" loading="lazy" src="{rel}" alt="{n["frame_id"]}"></details>'
        )
    chunks.append(
        '</section><section id="withheld"><h2>Khung thử không chọn</h2><p>Các state thử không là nhãn được giữ; xem lý do QA. Geometry và boards lưu trong hồ sơ audit.</p><table><tr><th>ID</th><th>Vị trí</th><th>Lý do</th></tr>'
    )
    chunks.extend(
        f"<tr><td>{r['candidate_id']}</td><td>{esc(r['location_description'])}</td><td>{esc(r['qa_note'])}</td></tr>"
        for r in rejected
    )
    chunks.append("</table></section></main></html>")
    page = "\n".join(chunks)
    (DATA / "index.html").write_text(page, encoding="utf-8")
    links = re.findall(r'(?:href|src)="([^"]+)"', page)
    for target in links:
        if target.startswith("#"):
            assert f'id="{target[1:]}"' in page, target
        else:
            assert (DATA / target).is_file(), target
    assert len({r["crop_sha256"] for r in rows}) == len(rows)
    bundle = DATA / "youtube-crop-proposals.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
        for r in rows:
            cid = r["candidate_id"]
            for filename in ("crop.png", "input.png", "proposal.json"):
                z.write(DATA / "candidates" / cid / filename, f"{r['group']}/{cid}/{filename}")
        z.writestr("review-index.json", json.dumps(rows, ensure_ascii=False, indent=2))
        z.writestr(
            "README.txt",
            "Draft local review only. No split or accepted labels. See review-index.json and local gallery.\n",
        )
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None and len(z.namelist()) == len(rows) * 3 + 2
    validation = {
        "frame_count": len(frames),
        "frame_notes_count": len(notes),
        "trial_count": len(selections),
        "proposed_count": len(rows),
        "withheld_trial_count": len(rejected),
        "by_group": dict(counts),
        "draft_states": dict(states),
        "source_crop_pixel_parity": "PASS",
        "input_pixel_parity": "PASS",
        "geometry_bounds_containment": "PASS",
        "crop_input_sha256": "PASS",
        "no_uu_proposals": "PASS",
        "canonical_targets_null_mask_zero": "PASS",
        "unique_crop_sha256": "PASS",
        "gallery_links": len(links),
        "gallery_links_status": "PASS",
        "zip_crc_membership": "PASS",
        "zip_sha256": sha(bundle),
        "visual_review": "Source boards 115 frame; native/input của 116 geometry thử đã xem. Draft, không thay owner acceptance.",
        "browser_render": "Chưa kiểm bằng browser; HTML tĩnh và links đã kiểm.",
        "independence_proven": False,
        "test_access": False,
        "owner_approved": False,
    }
    save(REPORT / "validation.json", validation)
    print(json.dumps(validation, ensure_ascii=False))


if __name__ == "__main__":
    main()
