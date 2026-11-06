"""Worksheet: explicit reviewed geometry -> unlabeled local crop review bundle."""

from __future__ import annotations

import argparse
import hashlib
import html
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.crop_bundle_audit import read_pinned_zip
from ai_exam_monitoring.data.pilot_schema import PixelBox
from ai_exam_monitoring.data.source_review import preview_input


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = Path(__file__).resolve().parent
    geometry = json.loads((report / "geometry.json").read_text(encoding="utf-8"))
    intake = json.loads((report / "intake-checks.json").read_text(encoding="utf-8"))
    inventory = json.loads((report / "inventory.json").read_text(encoding="utf-8"))
    out = args.output
    if out.exists() or not geometry:
        raise DataContractError("Review output already exists or geometry is empty")
    # Batch worksheet only: reuse ZIP/geometry/preview primitives, without draft labels.
    sources = read_pinned_zip(args.archive, intake["archive_sha256"])
    frame_pins = {f["member"]: f["sha256"] for f in inventory}
    sizes = {}
    for member, digest in frame_pins.items():
        data = sources[member]
        if hashlib.sha256(data).hexdigest() != digest:
            raise DataContractError("Source frame SHA mismatch")
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            sizes[member] = image.size
    ids = set()
    for item in geometry:
        cid = item["crop_id"]
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", cid) is None or cid in ids:
            raise DataContractError("Unsafe or duplicate crop ID")
        ids.add(cid)
        if item["source_sha256"] != frame_pins[item["member"]]:
            raise DataContractError("Geometry source pin differs from inventory")
        person, context = PixelBox(*item["person"]), PixelBox(*item["context"])
        if not (PixelBox(0, 0, *sizes[item["member"]]).contains(context)
                and context.contains(person)):
            raise DataContractError("Context must contain person inside source frame")
    out.mkdir(parents=True)
    (out / "crops").mkdir()
    (out / "inputs").mkdir()
    rows = []
    for item in sorted(geometry, key=lambda r: r["crop_id"]):
        with Image.open(io.BytesIO(sources[item["member"]])) as opened:
            image = opened.convert("RGB")
        crop = image.crop(tuple(item["context"]))
        crop_path = out / "crops" / f"{item['crop_id']}.png"
        input_path = out / "inputs" / f"{item['crop_id']}.png"
        crop.save(crop_path)
        preview_input(crop, 336, (124, 116, 104)).save(input_path)
        rows.append({
            "crop_id": item["crop_id"], "source_member": item["member"],
            "source_sha256": item["source_sha256"], "source_size": list(image.size),
            "person_box": item["person"], "context_box": item["context"],
            "crop_path": crop_path.relative_to(out).as_posix(),
            "crop_sha256": sha256_file(crop_path),
            "crop_rgb_sha256": hashlib.sha256(crop.tobytes()).hexdigest(),
            "native_size": list(crop.size),
            "input_path": input_path.relative_to(out).as_posix(),
            "input_sha256": sha256_file(input_path),
        })
    del sources
    by_id = {r["crop_id"]: r for r in geometry}
    for row in rows:
        item = by_id[row["crop_id"]]
        row.update(source_id=item["source_id"], anchor_id=item["anchor_id"],
                   anchor_scope=item["anchor_scope"], trial_id=item["trial_id"],
                   original_context_v1=item["original_context"],
                   review_status="pending_owner_crop_review")
    (out / "frames").mkdir()
    (out / "overlays").mkdir()
    grouped = {}
    for r in rows:
        grouped.setdefault(r["source_member"], []).append(r)
    frame_cards = []
    with zipfile.ZipFile(args.archive) as stream:
        for frame in inventory:
            data = stream.read(frame["member"])
            assert hashlib.sha256(data).hexdigest() == frame["sha256"]
            name = f"{frame['source_id']}-{frame['frame_id']}"
            (out / "frames" / f"{name}.jpg").write_bytes(data)
            im = Image.open(io.BytesIO(data)).convert("RGB")
            scale = min(1.0, 1440 / im.width)
            im = im.resize((round(im.width * scale), round(im.height * scale)))
            draw = ImageDraw.Draw(im)
            selected = grouped.get(frame["member"], [])
            for row in selected:
                for key, color in [("context_box", "#00ff88"), ("person_box", "#ff4444")]:
                    draw.rectangle(tuple(round(v * scale) for v in row[key]),
                                   outline=color, width=2)
                x, y = row["person_box"][:2]
                draw.text((round(x * scale), max(0, round(y * scale) - 14)),
                          row["crop_id"].split("-")[-1], fill="yellow",
                          stroke_width=1, stroke_fill="black")
            im.save(out / "overlays" / f"{name}.jpg", quality=94)
            frame["selected_crop_count"] = len(selected)
            frame["frame_path"] = f"frames/{name}.jpg"
            frame["overlay_path"] = f"overlays/{name}.jpg"
            frame_cards.append(f'<article data-source="{frame["source_id"]}">'
                               f'<b>{name} · {len(selected)} crop</b>'
                               f'<a href="frames/{name}.jpg"><img loading="lazy" '
                               f'src="overlays/{name}.jpg" alt="{name}"></a></article>')
    (out / "manifest.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    (out / "frames.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    header = '''<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Review crop · 05/11/2026</title><style>
body{font:15px system-ui;background:#eef1f5;color:#172333;margin:24px}
header{position:sticky;top:0;background:#eef1f5;padding:12px;z-index:1}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(700px,1fr));gap:18px}
article{background:white;padding:14px;border-radius:12px;overflow:auto}
.pair{display:flex;gap:12px}.pair img{max-width:336px;max-height:336px;object-fit:contain}
.pair figure{margin:10px 0;width:336px}.pair a{display:flex;width:336px;height:336px;
align-items:center;justify-content:center}a{color:#075a99}select,input{padding:8px;margin:5px}
article[hidden]{display:none}#frames img{width:100%;max-height:400px;object-fit:contain}
</style><header><h1>Crop chờ review</h1>
<p>Chưa gán nhãn hoặc P/N/U; chưa chia tập, release hay train.
Native giữ nguyên pixel ROI. Preview 336 px dùng fill G0 [124,116,104].</p>
<p><a href="#crops">Crop</a> · <a href="#frames">Toàn bộ frame nguồn</a> ·
<a href="manifest.json">Provenance/geometry</a></p>
<select id="source"><option value="">Tất cả nguồn</option>__OPTIONS__</select>
<input id="query" placeholder="Tìm ID crop hoặc frame" aria-label="Tìm ID">
<p>Đỏ: person; xanh: context trên overlay. ID Pxx chỉ là người trong frame,
không xác nhận cùng danh tính qua frame. Bấm ảnh native để xem độ phân giải gốc.</p>
</header><main id="crops">'''
    sources = sorted({r["source_id"] for r in rows})
    header = header.replace("__OPTIONS__", "".join(f'<option>{s}</option>' for s in sources))
    cards = []
    for row in rows:
        name = f"{row['source_id']}-{by_id[row['crop_id']]['frame_id']}"
        cid = html.escape(row["crop_id"])
        cards.append(f'<article id="{cid}" data-source="{row["source_id"]}">'
                     f'<b>{cid}</b> · native {row["native_size"][0]} × '
                     f'{row["native_size"][1]} px · '
                     f'<a href="overlays/{name}.jpg">Frame + khung</a> · '
                     f'<a href="frames/{name}.jpg">Frame gốc</a>'
                     '<div class="pair"><figure>'
                     f'<a href="{row["crop_path"]}"><img loading="lazy" '
                     f'src="{row["crop_path"]}" alt="{cid} native"></a>'
                     '<figcaption>Native ROI</figcaption></figure><figure>'
                     f'<img loading="lazy" src="{row["input_path"]}" '
                     f'alt="{cid} input 336"><figcaption>Input 336 px</figcaption>'
                     '</figure></div></article>')
    footer = '''</main><h2>Toàn bộ 373 frame nguồn</h2><main id="frames">__FRAMES__</main>
<script>function filter(){let s=document.querySelector('#source').value;
let q=document.querySelector('#query').value.trim().toLowerCase();
document.querySelectorAll('article').forEach(a=>a.hidden=!!((s&&a.dataset.source!==s)||
(q&&!a.textContent.toLowerCase().includes(q))));}
document.querySelector('#source').onchange=filter;
document.querySelector('#query').oninput=filter;</script></html>'''
    (out / "index.html").write_text(header + "".join(cards)
                                    + footer.replace("__FRAMES__", "".join(frame_cards)),
                                    encoding="utf-8")
    summary = {"status": "unlabeled_crop_review_only", "crop_count": len(rows),
               "source_frame_count": len(inventory),
               "used_frame_count": sum(f["selected_crop_count"] > 0 for f in inventory),
               "crops_by_source": dict(Counter(r["source_id"] for r in rows)),
               "archive_sha256": intake["archive_sha256"],
               "geometry_sha256": sha256_file(report / "geometry.json"),
               "manifest_sha256": sha256_file(out / "manifest.json")}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    # Verify native bytes after export, independently of the encoder's PNG checksums.
    with zipfile.ZipFile(args.archive) as stream:
        for row in rows:
            source = Image.open(io.BytesIO(stream.read(row["source_member"]))).convert("RGB")
            expected = source.crop(tuple(row["context_box"]))
            actual = Image.open(out / row["crop_path"]).convert("RGB")
            assert expected.size == actual.size and expected.tobytes() == actual.tobytes()
            assert sha256_file(out / row["crop_path"]) == row["crop_sha256"]
            assert not set(row) & {"labels", "targets", "masks", "split"}
    if sha256_file(args.archive) != intake["archive_sha256"]:
        raise DataContractError("Source archive changed during review export")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
