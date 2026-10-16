"""Enrollment evidence worksheet using the canonical codec; no acceptance or run."""

import hashlib
import html
import json
import math
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.pilot_schema import (
    DERIVED_SCHEMA_VERSION,
    ContextReview,
    CropDerivation,
    CropRef,
    PilotRecord,
    PixelBox,
    ReviewEvidence,
    RightsReview,
    SourceRef,
    TargetReview,
    write_records,
)

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / HERE.name
DATA = ROOT / "data/interim" / HERE.name
REPORTS = HERE.parent
inputs = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    inputs[path.relative_to(ROOT).as_posix()] = sha(path)
    return json.loads(path.read_text(encoding="utf8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


if (HERE / "result-pins.json").exists():
    raise RuntimeError("Preserve pinned evidence")
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
accepted = REPORTS / "E004-accepted-coverage-20261016"
for path, digest in read(accepted / "result-pins.json")["files"].items():
    assert sha(ROOT / path) == digest, path
rows = read(accepted / "accepted-ledger.json")
boxes = read(HERE / "person-box-percent-draft.json")["boxes"]
assert len(rows) == len(boxes) == 345
old_pin = read(REPORTS / "E004-crop-bundle-audit-20261014/input-pins.json")[-1]
new_pin = read(REPORTS / "E004-new-bundle-audit-20261015/input-pins.json")["archives"][-1]
for pin in (old_pin, new_pin):
    assert sha(ROOT / pin["path"]) == pin["sha256"]

records, geometry, cards, derivations = [], [], [], []
counts = Counter()
for index, (row, percent) in enumerate(zip(rows, boxes, strict=True)):
    cid = row["id"]
    for key in ("source", "crop", "input"):
        assert sha(ROOT / row[key]) == row[key + "_sha256"]
    with Image.open(ROOT / row["source"]) as source, Image.open(ROOT / row["crop"]) as crop:
        frame_size = source.size
        roi = source.convert("RGB").crop(row["context_xyxy"])
        actual = crop.convert("RGB")
        native = actual.size == roi.size and actual.tobytes() == roi.tobytes()
        review_ref = row["approval_ref"]
        if review_ref == "approval-13.json":
            review_ref = "artifacts/reports/E004-accepted-coverage-20261016/approval-13.json"
        label_review = ReviewEvidence("repository-owner", "2026-10-16", review_ref,
                                      row["crop_sha256"])
        derivation = None if native else CropDerivation(
            row["source_sha256"], hashlib.sha256(roi.tobytes()).hexdigest(),
            actual.width, actual.height, crop.format,
            f"artifacts/reports/{HERE.name}/derivative-provenance.json#{cid}", label_review)
        counts["native" if native else "reviewed_import"] += 1
        suffix = ".jpg" if derivation and crop.format == "JPEG" else ".png"
        context = PixelBox(*row["context_xyxy"])
        x0, y0, x1, y1 = context.xyxy
        a, b, c, d = percent
        person = PixelBox(x0 + math.floor((x1-x0)*a/100), y0 + math.floor((y1-y0)*b/100),
                          x0 + math.ceil((x1-x0)*c/100), y0 + math.ceil((y1-y0)*d/100))
        geometry.append({"id": cid, "source_sha256": row["source_sha256"],
                         "crop_sha256": row["crop_sha256"], "person_xyxy": person.xyxy,
                         "context_xyxy": context.xyxy, "status": "draft_owner_review_required",
                         "method": "manual_visual_estimate_source_ROI_board",
                         "board": f"outputs/{HERE.name}/geometry-{index//20+1:02}.jpg"})
        overlay = roi.copy()
        draw = ImageDraw.Draw(overlay)
        draw.rectangle((person.xmin-x0, person.ymin-y0, person.xmax-x0-1, person.ymax-y0-1),
                       outline="#00ff60", width=max(2, roi.width//160))
        overlay.save(OUT / f"{cid}-geometry.jpg", quality=92)
        entry = {"id": cid, "source": row["source"], "source_sha256": row["source_sha256"],
                 "context_xyxy": context.xyxy, "native_roi_rgb_sha256": hashlib.sha256(roi.tobytes()).hexdigest(),
                 "crop": row["crop"], "crop_sha256": row["crop_sha256"],
                 "format": crop.format, "dimensions": actual.size, "native_pixel_exact": native,
                 "approval_ref": review_ref, "upstream_ledger": row["upstream_ledger"]}
        derivations.append(entry)
    old = row["batch"] == "old240"
    archive = old_pin if old else new_pin
    source_id = "E004-crop-bundle-20261014" if old else "E004-new-bundle-20261015"
    label_states = [{"P": "positive", "N": "negative", "U": "unknown"}[x]
                    for x in row["final_labels"].split("/")]
    record = PilotRecord(
        cid, "E004-enrollment-preparation-20261016", "E004-accepted345-20261016",
        "E004-reviewed-import-20261016",
        SourceRef(source_id, archive["sha256"], row["source"], row["source_sha256"],
                  *frame_size),
        *(TargetReview(state, f"Accepted labels; exact upstream evidence: {review_ref}#{cid}",
                       label_review if state != "unknown" else None) for state in label_states),
        ContextReview("unknown", "No separate working-context approval inferred from labels"),
        RightsReview("owner-confirmed-use-rights", review_ref, ("local_classifier_research",),
                     ReviewEvidence("repository-owner", "2026-10-16", review_ref)),
        crop=CropRef(cid, person, context, f"crops/{cid}{suffix}", row["crop_sha256"],
                     review=None, derivation=derivation),
        ineligibility_reasons=("draft_person_geometry", "lineage_release_review_pending"),
        schema_version=DERIVED_SCHEMA_VERSION,
    )
    records.append(record)
    esc = html.escape
    cards.append(f'<article id="{cid}"><h3>{cid} — {row["final_labels"]}</h3>'
                 f'<p>{esc(row.get("anchor_description") or row.get("anchor_key") or cid)}</p>'
                 f'<img src="{cid}-geometry.jpg" alt="Draft person box">'
                 f'<p>Person Draft: {person.xyxy}<br>Context accepted: {context.xyxy}</p>'
                 f'<a href="../../{esc(row["source"])}">Frame gốc</a> · '
                 f'<a href="../../{esc(row["crop"])}">Crop accepted</a> · '
                 f'<a href="../../{esc(row["input"])}">Input accepted</a></article>')

write_records(DATA / "pending-ledger.jsonl", records)
write(HERE / "geometry-proposals.json", geometry)
write(HERE / "derivative-provenance.json", derivations)
write(HERE / "preparation-summary.json", {
    "count": len(records), "representation": dict(counts),
    "geometry": "345 manual visual drafts, not owner accepted", "training_ready": False,
    "labels_unchanged": True, "crop_bytes_unchanged": True,
    "selection_visual_comparison": "71 selection crops viewed against seven representative new parent scenes; no matching scene observed, not proof of independence",
    "protected_media_access": False,
})
write(HERE / "input-pins.json", inputs)
(OUT / "index.html").write_text(
    '<!doctype html><html lang="vi"><meta charset="utf-8"><title>Geometry review 345 crop</title>'
    '<style>body{font:16px system-ui;margin:24px;background:#eef2f5}main{display:grid;'
    'grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:16px}article{background:white;'
    'padding:14px}img{width:100%;height:300px;object-fit:contain}input{padding:12px}</style>'
    '<h1>345 person boxes Draft — crop/nhãn accepted giữ nguyên</h1>'
    '<p>Khung xanh là person box được đề xuất, không thay context crop. Đây là ước lượng thủ công '
    'từ ROI nguồn; cần nghiệm thu geometry. Không phải annotation detector hoàn chỉnh.</p>'
    '<input placeholder="Tìm ID" oninput="document.querySelectorAll(\'article\').forEach(x=>'
    'x.hidden=!x.id.toLowerCase().includes(this.value.toLowerCase()))">'
    '<main>' + ''.join(cards) + '</main></html>', encoding="utf8")
print(dict(counts), "pending canonical records", len(records))
