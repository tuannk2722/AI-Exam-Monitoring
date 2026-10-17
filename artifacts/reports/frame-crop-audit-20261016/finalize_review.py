"""Đóng gói review local và kiểm exact pixels; không enrollment hoặc owner acceptance."""

import hashlib
import html
import json
import shutil
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.pilot_schema import read_records
from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "artifacts/reports/frame-crop-audit-20261016"
DATA = ROOT / "data/interim/frame-crop-audit-20261016"
PARENT = ROOT / "data/processed/pilot-b/pilot-b-20261016-v10"


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def esc(value):
    return html.escape(str(value), quote=True)


def finalize():
    inv = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    draft = json.loads((REPORT / "selection-draft.json").read_text(encoding="utf-8"))
    crops = json.loads((REPORT / "crop-proposals.json").read_text(encoding="utf-8"))
    assert len(inv["frames"]) == 536 and len(draft) == len(inv["groups"]) == 27
    assert len({r["candidate_id"] for r in crops}) == len(crops)
    frames = {r["frame_id"]: r for r in inv["frames"]}
    by_frame = defaultdict(list)
    by_group = defaultdict(list)
    pixel_hashes = defaultdict(list)
    for row in inv["frames"]:
        blob = (ROOT / row["path"]).read_bytes()
        assert sha(blob) == row["sha256"]
        image = Image.open(ROOT / row["path"]).convert("RGB")
        assert image.size == (row["width"], row["height"])
        assert sha(image.tobytes()) == row["rgb_sha256"]
    review = DATA / "review"
    (review / "overlays").mkdir(parents=True, exist_ok=True)
    exported = []
    for row in crops:
        cid = row["candidate_id"]
        folder = DATA / "candidates" / cid
        src = Image.open(ROOT / row["source_path"]).convert("RGB")
        person, context = row["person_xyxy"], row["context_xyxy"]
        x0, y0, x1, y1 = context
        assert 0 <= x0 <= person[0] < person[2] <= x1 <= src.width
        assert 0 <= y0 <= person[1] < person[3] <= y1 <= src.height
        crop = Image.open(folder / "crop.png").convert("RGB")
        model_input = Image.open(folder / "input.png").convert("RGB")
        assert crop.size == (x1 - x0, y1 - y0)
        assert crop.tobytes() == src.crop(context).tobytes()
        assert sha((folder / "crop.png").read_bytes()) == row["crop_sha256"]
        assert sha((folder / "input.png").read_bytes()) == row["input_sha256"]
        assert model_input.size == (224, 224)
        assert model_input.tobytes() == preview_input(crop, 224, tuple(row["fill"])).tobytes()
        assert sha(model_input.tobytes()) == row["input_pixel_sha256"]
        assert sha((ROOT / row["source_path"]).read_bytes()) == row["source_sha256"]
        assert row["usage"] == "review_only" and row["split"] is None
        assert not row["owner_approved"] and row["canonical_mask"] == [0, 0]
        assert row["canonical_targets"] == [None, None] and row["draft_states"] != ["U", "U"]
        pixel_hashes[(crop.size, sha(crop.tobytes()))].append(cid)
        rel = Path("crops") / f"part_{row['part']:02}" / row["group"] / row["anchor"] / f"{cid}.png"
        dest = DATA / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            assert dest.read_bytes() == (folder / "crop.png").read_bytes()
        else:
            shutil.copyfile(folder / "crop.png", dest)
        overlay = src.copy()
        pen = ImageDraw.Draw(overlay)
        pen.rectangle((x0, y0, x1 - 1, y1 - 1), outline="#f48c06", width=2)
        pen.rectangle(
            (person[0], person[1], person[2] - 1, person[3] - 1), outline="#00e676", width=2
        )
        overlay.save(review / "overlays" / f"{cid}.jpg", quality=94)
        item = dict(
            row,
            export_path=rel.as_posix(),
            native_width=crop.width,
            native_height=crop.height,
            agent_crop_qa="source/native/input224 reviewed; Draft only",
        )
        exported.append(item)
        by_frame[row["frame_id"]].append(cid)
        by_group[row["group"]].append(item)
    duplicates = [v for v in pixel_hashes.values() if len(v) > 1]
    assert not duplicates
    write_json(REPORT / "review-index.json", exported)
    board_map = {}
    for board in inv["boards"]:
        assert (ROOT / board["path"]).is_file()
        for fid in board["frame_ids"]:
            assert fid not in board_map
            board_map[fid] = board["path"]
    assert set(board_map) == set(frames)
    audits = []
    for frame in inv["frames"]:
        group = frame["group"]
        selected = by_frame[frame["frame_id"]]
        rejected = [
            r
            for r in draft[group].get("rejected_after_crop_qa", [])
            if r["proposal"][1] == int(frame["frame_id"].split("F")[-1])
        ]
        audits.append(
            dict(
                frame_id=frame["frame_id"],
                source_path=frame["path"],
                group=group,
                part=frame["part"],
                board_path=board_map[frame["frame_id"]],
                source_sha256=frame["sha256"],
                visual_pass="reviewed_in_source_sequence",
                decision="crop_proposed" if selected else "no_additional_crop_proposed",
                selected_candidate_ids=selected,
                selected_reasons=[
                    r["draft_reason"] for r in by_group[group] if r["frame_id"] == frame["frame_id"]
                ],
                rejected_crop_reasons=[r["reason"] for r in rejected],
                sequence_note=draft[group]["note"],
                scope="Lựa chọn crop classifier; không phải annotation mọi người. Không chọn không đồng nghĩa frame lỗi hoặc mọi người đều không hợp lệ.",
            )
        )
    write_json(REPORT / "frame-audit.json", audits)
    active = {r["candidate_id"] for r in crops}
    inactive = []
    for path in sorted((DATA / "candidates").glob("*/proposal.json")):
        if path.parent.name not in active:
            row = json.loads(path.read_text(encoding="utf-8"))
            row["status"] = "not_in_final_review_batch"
            inactive.append(row)
    write_json(REPORT / "superseded-proposals.json", inactive)
    parent = read_records(PARENT / "review-ledger.jsonl")
    overlap = []
    for g in inv["groups"]:
        matches = [r for r in parent if g["folder"] in r.source.image_relpath]
        exact = [
            f["frame_id"]
            for f in inv["frames"]
            if f["group"] == g["group"]
            and any(r.source.image_sha256 == f["sha256"] for r in parent)
        ]
        overlap.append(
            {"group": g["group"], "folder_matches": len(matches), "exact_source_sha_frames": exact}
        )
    family_hints = [["G01", "G08", "G10", "G19"], ["G04", "G11"], ["G18", "G20"], ["G22", "G23"]]
    write_json(
        REPORT / "lineage-review.json",
        {
            "parent": PARENT.relative_to(ROOT).as_posix(),
            "parent_records": len(parent),
            "scope": "Metadata-only đối chiếu exact source SHA và tên thư mục; chưa near-duplicate đối với toàn bộ V10.",
            "matches": overlap,
            "visual_scene_hints_not_confirmed": family_hints,
            "owner_direction": "Owner trả lời 17/10/2026: chưa có mapping lớp/buổi; giữ nhóm theo video trước.",
            "independence_proven": False,
            "cross_video_person_identity_inferred": False,
            "limitation": "Không trùng exact SHA hoặc folder không chứng minh mới/độc lập; nguồn có thể resize, đổi tên hoặc cùng phòng.",
        },
    )
    part_counts = Counter(r["part"] for r in crops)
    state_counts = Counter("".join(r["draft_states"]) for r in crops)
    anchors = Counter((r["group"], r["anchor"]) for r in crops)
    result = {
        "status": "PASS technical checks; Draft visual batch, owner acceptance pending",
        "source_frames": len(frames),
        "source_groups": len(inv["groups"]),
        "source_boards_reviewed": len(board_map) and len(inv["boards"]),
        "selected_crops": len(crops),
        "selected_frames": sum(bool(v) for v in by_frame.values()),
        "local_anchors": len(anchors),
        "crops_per_part": dict(sorted(part_counts.items())),
        "draft_states_phone_looking": dict(state_counts),
        "max_crops_per_local_anchor": max(anchors.values()),
        "rejected_after_crop_qa": sum(
            len(d.get("rejected_after_crop_qa", [])) for d in draft.values()
        ),
        "inactive_candidate_revisions": len(inactive),
        "checks": {
            "source_file_and_rgb_sha": True,
            "source_geometry_bounds_and_containment": True,
            "native_crop_exact_pixels_and_sha": True,
            "input224_exact_preview_and_sha": True,
            "review_only_no_canonical_labels_or_splits": True,
            "all_frames_in_audit": True,
            "exact_crop_rgb_duplicates": duplicates,
        },
        "parent_metadata_sha256": {
            p.name: sha(p.read_bytes()) for p in sorted(PARENT.iterdir()) if p.is_file()
        },
        "no_media_from_existing_test_or_reserve_opened": True,
        "limitations": [
            "Không kiểm near-duplicate toàn bộ V10; mapping lớp/session chưa có.",
            "Nhãn P/N/U là đề xuất, không phải ground truth hoặc kết luận gian lận.",
            "Không chứng minh không còn anchor hữu ích trong các frame không chọn.",
        ],
    }
    write_json(REPORT / "validation.json", result)
    style = """
body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f2f5fa;color:#152238;line-height:1.5}
header{background:#12263a;color:white;padding:28px 4%;}main{max-width:1480px;margin:auto;padding:24px}
a{color:#075ea8}header a{color:#b5e3ff}nav{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}
section{background:white;margin:24px 0;padding:22px;border-radius:14px;border:1px solid #dce3ed}
h1{margin:0;font-size:28px}h2{margin:0 0 8px}h3{margin-bottom:10px;color:#15586b}
.cards{display:flex;gap:18px;flex-wrap:wrap;align-items:stretch}
.card{width:340px;border:1px solid #d7e0eb;border-radius:10px;padding:14px;background:#fbfcfe}
.crop{display:block;max-width:100%;max-height:320px;width:auto;height:auto;margin:12px auto;background:#eee}
.input{width:224px;height:224px}.badge{display:inline-block;background:#e2edf6;border-radius:5px;padding:3px 7px;margin:3px}
.small{font-size:13px;color:#526278}details{padding:9px 0}summary{cursor:pointer;font-weight:600}
.frames{display:flex;flex-wrap:wrap;gap:12px}.frame{width:240px;padding:8px;border:1px solid #dde4ee}
.frame img{width:240px;height:160px;object-fit:contain;background:#e9eef5}.warn{background:#fff2d6;padding:12px;border-radius:8px}
footer{padding:24px}.links{display:flex;gap:14px;flex-wrap:wrap}.anchor{border-top:1px solid #dce4ed;margin-top:20px;padding-top:5px}
"""
    pieces = [
        f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Review crop 5 ZIP</title><style>{style}</style></head><body>',
        f"<header><h1>Review crop từ 5 ZIP</h1><p>{len(frames)} frame · 27 video/nhóm nguồn · {len(crops)} crop · {len(anchors)} anchor cục bộ</p>",
        "<p>Draft để bạn nghiệm thu. Thứ tự nhãn: <b>phone / looking</b>. P = có evidence, N = đề xuất không có trong vùng quan sát, U = chưa rõ. Không suy diễn gian lận.</p>",
        "<p>Crop giữ pixel gốc; ảnh 224 px là bản xem trước. Bấm crop để xem PNG đầy đủ. Cùng anchor được xếp cạnh nhau; không nhận dạng người giữa các video.</p>",
        '<div class="links"><a href="crops-review.zip">Tải bộ crop + metadata</a><a href="../../../artifacts/reports/frame-crop-audit-20261016/README.md">Báo cáo</a></div></header><main>',
        '<div class="warn">Chưa có mapping lớp/buổi học: giữ nhóm theo video theo lựa chọn của bạn. Các crop còn U chỉ đề xuất supervision cho target có evidence sau nghiệm thu. Không có nhãn hoặc split canonical mới.</div>',
        "<nav>"
        + "".join(f'<a href="#{g["group"]}">{g["group"]}</a>' for g in inv["groups"])
        + "</nav>",
    ]
    for group in inv["groups"]:
        gid = group["group"]
        items = by_group[gid]
        pieces += [
            f'<section id="{gid}"><h2>ZIP {group["part"]:02} · {gid}</h2>',
            f'<p class="small">Thư mục video: {esc(group["folder"])} · {len(group["frames"])} frame · {len(items)} crop</p>',
            f"<p>{esc(draft[gid]['note'])}</p>",
        ]
        if not items:
            pieces.append(
                '<p class="warn">Không giữ crop: ảnh nguồn quá mờ để đạt yêu cầu rõ người/hành vi.</p>'
            )
        for anchor in sorted({r["anchor"] for r in items}):
            pieces.append(f'<div class="anchor"><h3>{gid} / {anchor}</h3><div class="cards">')
            for r in items:
                if r["anchor"] != anchor:
                    continue
                cid = r["candidate_id"]
                pieces += [
                    f'<article class="card" id="{cid}"><b>{cid}</b><br>',
                    f'<span class="badge">phone {r["draft_states"][0]}</span><span class="badge">looking {r["draft_states"][1]}</span>',
                    f'<a href="{r["export_path"]}" target="_blank"><img class="crop" src="{r["export_path"]}" alt="{cid}" loading="lazy"></a>',
                    f"<p>{esc(r['draft_reason'])}</p>",
                    f'<p class="small">Native {r["native_width"]} × {r["native_height"]} px · frame {r["frame_id"]}</p>',
                    f'<div class="links"><a href="frames/{gid}/frame_{int(r["frame_id"].split("F")[-1]):05}.jpg" target="_blank">Frame gốc</a><a href="review/overlays/{cid}.jpg" target="_blank">Khung anchor/context</a></div>',
                    f'<details><summary>Input 224 px và geometry</summary><img class="input" src="candidates/{cid}/input.png" alt="Input {cid}"><p class="small">Xanh: person {r["person_xyxy"]}<br>Cam: context {r["context_xyxy"]}<br>Crop SHA: {r["crop_sha256"]}</p></details></article>',
                ]
            pieces.append("</div></div>")
        rejects = draft[gid].get("rejected_after_crop_qa", [])
        if rejects:
            pieces.append(
                f"<details><summary>{len(rejects)} đề xuất đã bỏ sau QA crop</summary><ul>"
            )
            for r in rejects:
                a, frame = r["proposal"][:2]
                pieces.append(f"<li>{a} / F{frame:05}: {esc(r['reason'])}</li>")
            pieces.append("</ul></details>")
        pieces.append(
            f'<details><summary>Xem toàn bộ {len(group["frames"])} frame của video</summary><p class="small">Frame không chọn thêm không đồng nghĩa frame hỏng. Nhận xét mức chuỗi ở trên; không annotate exhaustively mọi người.</p><div class="frames">'
        )
        for fid in group["frames"]:
            r = frames[fid]
            url = Path(r["path"]).relative_to(DATA.relative_to(ROOT)).as_posix()
            selected = by_frame[fid]
            pieces.append(
                f'<div class="frame"><b>{fid}</b><a href="{url}" target="_blank"><img src="{url}" alt="{fid}" loading="lazy"></a><p class="small">'
                + (
                    " · ".join(f'<a href="#{cid}">{cid}</a>' for cid in selected)
                    if selected
                    else "Đã xem trong chuỗi; không đề xuất thêm crop."
                )
                + "</p></div>"
            )
        pieces.append("</div></details></section>")
    pieces.append(
        "</main><footer>Local only · crop nguyên bản, không sinh hoặc bổ sung bộ phận · owner acceptance chưa thực hiện.</footer></body></html>"
    )
    (DATA / "index.html").write_text("\n".join(pieces), encoding="utf-8")
    package_readme = (
        f"Bộ crop Draft — {len(crops)} ảnh PNG native, nhóm theo ZIP/video/anchor.\n"
        "P/N/U theo thứ tự phone_use, looking_around chỉ là đề xuất.\n"
        "Chưa owner acceptance, chưa split/enrollment. Không suy diễn gian lận.\n"
        "review-index.json có SHA, geometry và nguồn ZIP/member cho từng crop.\n"
    )
    with zipfile.ZipFile(
        DATA / "crops-review.zip", "w", compression=zipfile.ZIP_DEFLATED
    ) as bundle:
        for r in exported:
            bundle.write(DATA / r["export_path"], r["export_path"])
        bundle.write(REPORT / "review-index.json", "review-index.json")
        bundle.write(REPORT / "lineage-review.json", "lineage-review.json")
        bundle.writestr("README.txt", package_readme.encode("utf-8"))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    finalize()
