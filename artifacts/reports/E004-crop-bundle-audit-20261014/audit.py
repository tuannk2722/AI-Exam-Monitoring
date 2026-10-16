"""Full supplied-bundle audit worksheet; no model inference or dataset promotion."""
from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFont, JpegImagePlugin

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.crop_bundle_audit import (
    candidate_issues,
    image_fingerprint,
    read_pinned_zip,
)
from ai_exam_monitoring.data.pilot_schema import read_records

ROOT = Path(__file__).resolve().parents[3]
ID = "E004-crop-bundle-audit-20261014"
cfg_path = ROOT / "configs/datasets" / f"{ID}.yaml"
cfg = yaml.safe_load(cfg_path.read_text(encoding="utf8"))
report, out, interim = (ROOT / cfg[k] for k in ("report", "output", "interim"))
if (report / "summary.json").exists():
    raise RuntimeError("Preserve previous audit output")
out.mkdir(parents=True, exist_ok=True)
interim.mkdir(parents=True, exist_ok=True)
(out / "boards").mkdir(exist_ok=True)
(out / "sources").mkdir(exist_ok=True)


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def jsonlines(raw):
    return [json.loads(x) for x in raw.decode("utf-8-sig").splitlines() if x.strip()]


archives = {}
inventory = []
for spec in cfg["inputs"]:
    blobs = read_pinned_zip(ROOT / spec["path"], spec["sha256"])
    name = Path(spec["path"]).name
    archives[name] = blobs
    for member, raw in blobs.items():
        inventory.append(dict(archive=name, member=member, bytes=len(raw),
                              sha256=hashlib.sha256(raw).hexdigest()))
    print("CRC/SHA PASS", name, len(blobs), flush=True)
write(report / "archive-inventory.json", inventory)
meta = archives["crop_manifest_and_review.zip"]
rows = jsonlines(meta["manifest.jsonl"])
rows.sort(key=lambda r: (r["parent_id"], r["anchor_id"], r["frame_num"]))
assert len(rows) == len({r["crop_file"] for r in rows}) == 765
assert len({(r["parent_id"], r["anchor_id"], r["frame_num"]) for r in rows}) == 765
frame_archive = archives["youtube-videos-accepted-frames.zip"]
frames = jsonlines(frame_archive["manifest.jsonl"])
assert len(frames) == len({r["file_path"] for r in frames}) == 212
frame_map = {r["file_path"]: r for r in frames}
decisions = json.loads(frame_archive["review_decisions.json"])
latest = {}
for decision in sorted(decisions, key=lambda d: d["updated_at"]):
    latest[decision["asset_id"]] = decision
assert all(latest[f["asset_id"]]["decision"] == "accepted" for f in frames)
csv_rows = list(csv.DictReader(io.StringIO(meta["manifest.csv"].decode("utf-8-sig"))))
assert len(csv_rows) == 765
csv_map = {r["crop_file"]: r for r in csv_rows}
assert len(csv_map) == 765
for row in rows:
    other = csv_map[row["crop_file"]]
    for key, value in other.items():
        if key == "bbox_xyxy":
            expected = ",".join(str(v) for v in row[key])
        else:
            expected = "" if row[key] is None else str(row[key])
        assert expected == value, (row["crop_file"], key)
images = {}
for name, blobs in archives.items():
    if not name.startswith("crop_part_"):
        continue
    for member, raw in blobs.items():
        if member.startswith("crops/"):
            assert member not in images
            images[member] = raw
        else:
            assert raw == meta[member], (name, member, "metadata copies differ")
assert set(images) == {r["crop_file"] for r in rows}
for parent in {r["parent_id"] for r in rows}:
    section = jsonlines(meta[f"labels_{parent}.jsonl"])
    assert sorted(section, key=lambda r: r["crop_file"]) == sorted(
        [r for r in rows if r["parent_id"] == parent], key=lambda r: r["crop_file"])
frame_inventory = jsonlines(meta["frame_inventory.jsonl"])
assert len(frame_inventory) == 212
assert {f["source_frame"] for f in frame_inventory} == set(frame_map)
for frame in frame_inventory:
    found = [r for r in rows if r["source_frame"] == frame["source_frame"]]
    assert len(found) == frame["crop_count"]
    assert {r["anchor_id"] for r in found} == set(frame["anchor_ids"])

decoded_sources = {}
source_fingerprints = {}
for frame in frames:
    raw = frame_archive["assets/" + frame["file_path"]]
    fp = image_fingerprint(raw)
    assert fp["sha256"] == frame["sha256"] and len(raw) == frame["bytes"]
    assert (fp["width"], fp["height"]) == (frame["width"], frame["height"])
    source_fingerprints[frame["file_path"]] = fp
    decoded_sources[frame["file_path"]] = Image.open(io.BytesIO(raw)).convert("RGB")
    path = interim / "source" / frame["file_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
print("212 source frames decoded and exact SHA verified", flush=True)

records = []
font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 13)
for i, row in enumerate(rows):
    sid = f"CB-{i+1:04}"
    raw = images[row["crop_file"]]
    fp = image_fingerprint(raw)
    issues = candidate_issues(row)
    frame = frame_map[row["source_frame"]]
    assert frame["asset_id"] == row["source_asset_id"]
    assert frame["origin"] == row["origin"] and frame["parent_id"] == row["parent_id"]
    assert (frame["width"], frame["height"]) == (row["source_width"], row["source_height"])
    assert (fp["width"], fp["height"], fp["mode"]) == (224, 224, "RGB")
    crop_path = interim / "crops" / f"{sid}.jpg"
    crop_path.parent.mkdir(exist_ok=True)
    crop_path.write_bytes(raw)
    source = decoded_sources[row["source_frame"]]
    x0, y0, x1, y1 = row["bbox_xyxy"]
    native = source.crop((x0, y0, x1, y1))
    resized = native.resize((224, 224), Image.Resampling.LANCZOS)
    original = Image.open(io.BytesIO(raw))
    # Quantization/sampling come from supplied JPEG, not a guessed quality setting.
    encoded = io.BytesIO()
    resized.save(encoded, "JPEG", qtables=original.quantization,
                 subsampling=JpegImagePlugin.get_sampling(original))
    recreated = Image.open(io.BytesIO(encoded.getvalue())).convert("RGB")
    mae = float(np.abs(np.asarray(resized).astype(float) - np.asarray(original)).mean())
    reproduction = dict(rgb_equal=recreated.tobytes() == original.convert("RGB").tobytes(),
                        jpeg_bytes_equal=encoded.getvalue() == raw,
                        pre_jpeg_mae=mae, native_size=list(native.size),
                        square_box=native.width == native.height,
                        requires_upscale=min(native.size) < 224)
    if not reproduction["rgb_equal"]:
        issues.append("resize_reproduction_mismatch")
    records.append(dict(sample_id=sid, supplied=row, fingerprint=fp, issues=issues,
                        source_sha256=frame["sha256"], reproduction=reproduction,
                        local_crop=crop_path.relative_to(ROOT).as_posix(),
                        local_source=(interim / "source" / row["source_frame"]).relative_to(ROOT).as_posix(),
                        usage="review_only", assigned_split=None,
                        board=f"boards/{i//16+1:02}.png"))
    if (i+1) % 100 == 0:
        print("crop/source audit", i+1, flush=True)
for start in range(0, len(records), 16):
    board = Image.new("RGB", (960, 1088), "white")
    draw = ImageDraw.Draw(board)
    for j, record in enumerate(records[start:start+16]):
        x, y = (j % 4)*240, (j // 4)*272
        row = record["supplied"]
        draw.text((x+4, y+2), f"{record['sample_id']} f{row['frame_num']} {row['phone']}/{row['looking']}", fill="black", font=font)
        draw.text((x+4, y+20), row["anchor_id"], fill="black", font=font)
        board.paste(Image.open(ROOT/record["local_crop"]), (x+4, y+44))
    board.save(out / "boards" / f"{start//16+1:02}.png")
write(interim / "records.json", records)
write(report / "source-fingerprints.json", source_fingerprints)

duplicates = {}
for kind in ("sha256", "rgb_sha256"):
    groups = defaultdict(list)
    for record in records:
        groups[record["fingerprint"][kind]].append(record["sample_id"])
    duplicates[kind] = [v for v in groups.values() if len(v)>1]
near = []
for i, a in enumerate(records):
    for b in records[i+1:]:
        distance = (a["fingerprint"]["dhash"] ^ b["fingerprint"]["dhash"]).bit_count()
        if distance <= cfg["similarity"]["dhash_max_distance"]:
            near.append(dict(a=a["sample_id"], b=b["sample_id"], distance=distance,
                             same_parent=a["supplied"]["parent_id"]==b["supplied"]["parent_id"],
                             same_anchor=a["supplied"]["anchor_id"]==b["supplied"]["anchor_id"]))
write(report / "duplicate-audit.json", dict(exact=duplicates, dhash_pairs=near,
      note="dHash screening, distinct from supplied pHash flags; no automatic deletion/group acceptance"))

# Metadata-only match covers V9 review-only/reserve/test, with no protected media decode.
parent = ROOT / cfg["parent_v9"]
ledger = read_records(parent / "review-ledger.jsonl")
exact_overlap = []
for record in records:
    for old in ledger:
        if old.crop is not None and (record["fingerprint"]["sha256"] == old.crop.crop_sha256
                or record["source_sha256"] == old.source.image_sha256):
            exact_overlap.append(dict(sample_id=record["sample_id"], old_id=old.sample_id,
                                      old_usage=old.usage, old_group=old.group.leakage_group_id if old.group else None))
exp = ROOT/cfg["experiment"]
current = [r for r in read_records(exp/"manifest.jsonl") if r.usage in ("train", "val")]
old_fps = []
for r in current:
    raw=(exp/r.crop.crop_relpath).read_bytes()
    fp=image_fingerprint(raw)
    assert fp["sha256"] == r.crop.crop_sha256
    old_fps.append((r,fp))
nearest=[]
for record in records:
    best = min(old_fps, key=lambda item: ((record['fingerprint']['dhash'] ^ item[1]['dhash']).bit_count(),item[0].sample_id))
    distance=(record['fingerprint']['dhash'] ^ best[1]['dhash']).bit_count()
    nearest.append(dict(sample_id=record['sample_id'], old_id=best[0].sample_id,
                        old_usage=best[0].usage, distance=distance,
                        flagged=distance <= cfg['similarity']['dhash_max_distance']))
write(report/'parent-overlap.json',dict(metadata_ledger_records=len(ledger),
      exact_matches=exact_overlap, non_test_reference_crops=len(old_fps),nearest_non_test=nearest,
      holdout_near_similarity='not_measured_no_media_access',
      independence='unproven; no absence-of-leakage claim from hash nonmatch'))

supplied_summary=json.loads(meta['summary.json'])
assert supplied_summary['total_crops']==len(records)
labels=Counter(r['supplied']['phone']+'/'+r['supplied']['looking'] for r in records)
scenarios=Counter(r['supplied']['scenario'] for r in records)
assert dict(labels)==supplied_summary['labels'] and dict(scenarios)==supplied_summary['scenarios']
assert sum(r['supplied']['review_only'] for r in records)==supplied_summary['review_only']
temporal=list(csv.DictReader(io.StringIO(meta['temporal_similarity_flags.csv'].decode('utf-8-sig'))))
by_crop={r['crop_file']:r for r in rows}
for pair in temporal:
    r=by_crop[pair['crop_file']]
    prev=by_crop[pair['compared_to']]
    assert r['temporal_near_duplicate'] and r['temporal_near_duplicate_of']==pair['compared_to']
    assert r['temporal_phash_distance']==int(pair['phash_hamming'])
    assert r['parent_id']==prev['parent_id']==pair['parent_id']
    assert r['anchor_id']==prev['anchor_id']==pair['anchor_id']
    assert abs(r['frame_num']-prev['frame_num'])==int(pair['frame_gap'])
assert len(temporal)==sum(r['temporal_near_duplicate'] for r in rows)==32
track_summary=[]
for parent_id,anchor in sorted({(r['parent_id'],r['anchor_id']) for r in rows}):
    subset=[r for r in records if (r['supplied']['parent_id'],r['supplied']['anchor_id'])==(parent_id,anchor)]
    track_summary.append(dict(parent=parent_id,anchor=anchor,count=len(subset),
                              ids=[r['sample_id'] for r in subset],
                              labels=dict(Counter(r['supplied']['phone']+'/'+r['supplied']['looking'] for r in subset)),
                              first_frame=subset[0]['supplied']['frame_num'],last_frame=subset[-1]['supplied']['frame_num']))
write(report/'tracks.json',track_summary)
summary=dict(status='audit_not_release',archives=7,crops=765,frames=212,parents=5,anchor_tracks=len(track_summary),
             crc_all_members='PASS',manifest_csv_section_join='PASS',frame_inventory_join='PASS',
             frame_sha_and_acceptance_join='PASS',all_decode='PASS',labels_provisional=dict(labels),
             scenarios_provisional=dict(scenarios),review_only_supplied=380,training_ready=False,
             geometry_issues=[dict(sample_id=r['sample_id'],issues=r['issues']) for r in records if r['issues']],
             source_crop_reproduction=dict(Counter('exact' if r['reproduction']['rgb_equal'] else 'mismatch' for r in records)),
             jpeg_bytes_equal=sum(r['reproduction']['jpeg_bytes_equal'] for r in records),
             nonsquare_boxes=sum(not r['reproduction']['square_box'] for r in records),
             upscale_boxes=sum(r['reproduction']['requires_upscale'] for r in records),
             exact_duplicate_groups={k:len(v) for k,v in duplicates.items()},dhash_pairs=len(near),
             cross_parent_dhash_pairs=sum(not r['same_parent'] for r in near),
             parent_exact_matches=len(exact_overlap),parent_non_test_near_flags=sum(r['flagged'] for r in nearest),
             supplied_temporal_flags_consistent=len(temporal),
             source_metadata_caveats=['manifest review_status unreviewed; accepted decisions joined by asset_id',
                                      'frame mime_detected inherited video/mp4; actual files decode JPEG',
                                      'rights user-confirmed; upstream fair-use text is not independent license proof'])
write(report/'summary.json',summary)
write(report/'dependency-pins.json',{p.relative_to(ROOT).as_posix():sha256_file(p) for p in
      [cfg_path,parent/'review-ledger.jsonl',exp/'manifest.jsonl',ROOT/'docs/data.md',
       ROOT/'src/ai_exam_monitoring/data/crop_bundle_audit.py']})
print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
