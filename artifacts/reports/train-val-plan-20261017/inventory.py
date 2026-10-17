"""Read-only planning inventory: only current train/val and accepted new crops."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.image_similarity import difference_hash
from ai_exam_monitoring.data.pilot_schema import read_records, record_to_dict

ROOT = Path.cwd()
REPORT = ROOT / "artifacts/reports/train-val-plan-20261017"
SCRATCH = ROOT / "outputs/_scratch/train-val-20261017"
PACKAGE = ROOT / "data/processed/e004/E004-c345-development-20261016"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, value):
    (REPORT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


all_old = [record_to_dict(x) for x in read_records(PACKAGE / "review-ledger.jsonl")]
rows = []
for r in all_old:
    if r["usage"] not in ("train", "val"):
        continue
    rows.append(
        dict(
            id=r["sample_id"],
            origin="existing",
            prior_usage=r["usage"],
            group=r["group"]["leakage_group_id"],
            video=r["group"]["video_id"],
            source_id=r["source"]["source_id"],
            source_sha=r["source"]["image_sha256"],
            crop_sha=r["crop"]["crop_sha256"],
            path=(PACKAGE / r["crop"]["crop_relpath"]).relative_to(ROOT).as_posix(),
            states=[
                {"positive": "P", "negative": "N", "unknown": "U"}[r[t]["state"]]
                for t in ("phone_use", "looking_around")
            ],
        )
    )
for f in [
    "artifacts/reports/frame-crop-audit-20261016/owner-accepted-20261017.json",
    "artifacts/reports/frame-crop-additional-20261017/owner-accepted.json",
]:
    for r in json.loads((ROOT / f).read_text(encoding="utf-8"))["records"]:
        rows.append(
            dict(
                id=r["candidate_id"],
                origin="new270",
                prior_usage="review_only",
                group="NEW-" + r["group"],
                video="NEW-" + r["group"],
                source_id="owner-frames-20261016",
                source_sha=r["source_sha256"],
                crop_sha=r["crop_sha256"],
                path=r.get("accepted_crop_path", r.get("crop_path")),
                source_path=r["source_path"],
                states=r["review_states"],
            )
        )
assert len(rows) == 1451 and len({r["id"] for r in rows}) == 1451
for r in rows:
    path = ROOT / r["path"]
    assert sha(path) == r["crop_sha"]
    with Image.open(path) as im:
        im = im.convert("RGB")
        r["size"] = list(im.size)
        r["rgb_sha"] = hashlib.sha256(str(im.size).encode() + im.tobytes()).hexdigest()
        r["dhash"] = difference_hash(im)
old = [r for r in rows if r["origin"] == "existing"]
new = [r for r in rows if r["origin"] == "new270"]
pairs = []
for r in new:
    dist = sorted(((r["dhash"] ^ x["dhash"]).bit_count(), x["id"]) for x in old)
    pairs.append(dict(new_id=r["id"], group=r["group"], nearest=dist[:3]))
save("pool-inventory.json", rows)
save("nearest-existing.json", pairs)
lookup = {r["id"]: r for r in rows}
selected = []
for g in sorted({r["group"] for r in new}):
    selected.extend(
        sorted(
            [p for p in pairs if p["group"] == g], key=lambda p: (p["nearest"][0][0], p["new_id"])
        )[:2]
    )
for off in range(0, len(selected), 6):
    board = Image.new("RGB", (1200, 720), "white")
    d = ImageDraw.Draw(board)
    for j, p in enumerate(selected[off : off + 6]):
        x = j % 3 * 400
        y = j // 3 * 360
        a = lookup[p["new_id"]]
        distance, bid = p["nearest"][0]
        b = lookup[bid]
        for k, r in enumerate([a, b]):
            im = Image.open(ROOT / r["path"]).convert("RGB")
            im.thumbnail((195, 295))
            board.paste(im, (x + 200 * k, y + 45))
            d.text((x + 200 * k, y + 20), r["id"], fill="black")
        d.text((x, y), f"dHash {distance}", fill="black")
    board.save(SCRATCH / f"nearest-{off // 6 + 1:02}.jpg")
# Representative source frames for all 25 new video groups.
representatives = [
    next(r for r in new if r["group"] == g) for g in sorted({r["group"] for r in new})
]
for off in range(0, len(representatives), 9):
    board = Image.new("RGB", (1200, 750), "white")
    d = ImageDraw.Draw(board)
    for j, r in enumerate(representatives[off : off + 9]):
        x = j % 3 * 400
        y = j // 3 * 250
        im = Image.open(ROOT / r["source_path"])
        im.thumbnail((395, 220))
        board.paste(im, (x, y + 25))
        d.text((x, y), r["group"], fill="black")
    board.save(SCRATCH / f"scenes-{off // 9 + 1}.jpg")
save(
    "input-pins.json",
    {
        "commit_before_planning": "c00b159",
        "package_ledger_sha256": sha(PACKAGE / "review-ledger.jsonl"),
        "accepted_receipts": {
            f: sha(ROOT / f)
            for f in [
                "artifacts/reports/frame-crop-audit-20261016/owner-accepted-20261017.json",
                "artifacts/reports/frame-crop-additional-20261017/owner-accepted.json",
            ]
        },
        "allowed_image_reads": {"existing_train_val": len(old), "new_accepted": len(new)},
        "excluded_from_pixel_access": dict(
            Counter(r["usage"] for r in all_old if r["usage"] not in ("train", "val"))
        ),
        "scope": "No protected images, features, predictions or model comparison",
    },
)
print(
    "Inventory",
    len(rows),
    "nearest minimum",
    min(x["nearest"][0][0] for x in pairs),
    "pairs <=6",
    sum(x["nearest"][0][0] <= 6 for x in pairs),
)
