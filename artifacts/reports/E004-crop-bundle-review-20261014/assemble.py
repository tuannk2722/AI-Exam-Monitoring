"""Join manual evidence and render local review; never creates accepted labels."""

import hashlib
import json
import os
from collections import Counter
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "outputs" / HERE.name
OLD = "E004-crop-bundle-audit-20261014"
config = yaml.safe_load(
    (ROOT / "configs/datasets" / f"{HERE.name}.yaml").read_text(encoding="utf-8")
)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(name, value):
    (HERE / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


records = read(ROOT / "data/interim" / OLD / "records.json")
owner = read(HERE / "review-input.json")
notes = read(HERE / "manual-observations.json")
derivatives = read(HERE / "derivatives.json")
redundancy_review = read(HERE / "redundancy-visual-review.json")
redundancy_map = {
    r["candidate_id"]: r["representative_id"]
    for r in redundancy_review
    if r["decision"] == "propose_redundant_alternative"
}
replacements = {r["original_id"]: r for r in derivatives if "original_id" in r}
frames = {r["path"]: r for r in owner["frames"]}
assert digest(HERE / "owner-review-original.md") == owner["owner_snapshot_sha256"]
ledger = []
for base in records:
    cid = base["sample_id"]
    o = [owner["rows"][i - 1] for i in owner["mapping"][cid]]
    explicit = o[0]["explicit_labels"] if o else None
    note = notes[cid]
    comparison = (
        "no_explicit_owner_label"
        if explicit is None
        else ("label_agreement" if explicit == note["draft_labels"] else "draft_disagreement")
    )
    if cid == "CB-0648":
        comparison = "conditional_owner_anchor_mismatch"
    row = {
        "sample_id": cid,
        "parent_id": base["supplied"]["parent_id"],
        "anchor_id": base["supplied"]["anchor_id"],
        "frame_num": base["supplied"]["frame_num"],
        "frame_id": frames[base["local_source"]]["frame_id"],
        "source": base["local_source"],
        "source_sha256": base["source_sha256"],
        "crop": base["local_crop"],
        "crop_sha256": base["fingerprint"]["sha256"],
        "context_xyxy": base["supplied"]["bbox_xyxy"],
        "supplied_labels": base["supplied"]["phone"] + "/" + base["supplied"]["looking"],
        "owner_rows": owner["mapping"][cid],
        "owner_explicit_labels": explicit,
        "owner_comments": [x["raw"] for x in o],
        "comparison": comparison,
        **note,
        "replacement_id": replacements[cid]["candidate_id"] if cid in replacements else None,
        "crop_visual_pass": (
            "48 boards, 224 px per crop; native source inspection for ambiguity/recrop"
        ),
        "source_visual_pass": (
            "212 source frames, overview 960x540; selected native coordinate views"
        ),
        "status": "draft_review_only",
        "assigned_split": None,
        "canonical_targets": [None, None],
        "canonical_mask": [0, 0],
    }
    ledger.append(row)
save("crop-review-ledger.json", ledger)
for row in derivatives:
    base = next(
        r for r in ledger if r["sample_id"] == row.get("original_id", row.get("source_crop_id"))
    )
    row["reason"] = row.get(
        "reason", base["reason"] + " Đề xuất geometry mới; nhãn cần nghiệm thu đúng SHA mới."
    )
    row["visual_pass"] = (
        "All 197 derivative previews inspected at 224; native source context compared"
    )
    row["canonical_targets"] = [None, None]
    row["canonical_mask"] = [0, 0]
    row["assigned_split"] = None
    row["frame_id"] = base["frame_id"]
    row["comparison"] = "new_crop_pending_owner"
save("derivative-review.json", derivatives)

# Conservative reversible shortlist proposal: only equal parent, named anchor,
# exact state pair and review class; compare against a retained representative.
# Existing audit's dHash <=5 screening criterion, not an acceptance threshold.
candidates = [
    {**r, "candidate_id": r["sample_id"], "input": r["crop"]}
    for r in ledger
    if r["replacement_id"] is None
]
candidates += derivatives
candidates.sort(key=lambda r: r["candidate_id"])
kept = []
duplicates = []
withheld = []


def dhash(path):
    im = Image.open(path).convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    px = list(im.getdata())
    return sum(
        (px[y * 9 + x] > px[y * 9 + x + 1]) << (y * 8 + x) for y in range(8) for x in range(8)
    )


for row in candidates:
    row["dhash"] = dhash(ROOT / row["input"])
    if row["draft_labels"] == "U/U" or row["candidate_id"] == "CB-0734":
        row["selection"] = "withheld_insufficient_evidence"
        withheld.append(row)
        continue
    match = None
    for prev in kept:
        if redundancy_map.get(row["candidate_id"]) != prev["candidate_id"]:
            continue
        if (row["parent_id"], row["anchor_id"], row["draft_labels"], row["comparison"]) != (
            prev["parent_id"],
            prev["anchor_id"],
            prev["draft_labels"],
            prev["comparison"],
        ):
            continue
        distance = (row["dhash"] ^ prev["dhash"]).bit_count()
        if distance <= config["redundancy"]["dhash_max_distance"]:
            match = (prev, distance)
            break
    if match:
        row["selection"] = "redundant_alternative_retained"
        row["representative_id"] = match[0]["candidate_id"]
        row["distance"] = match[1]
        duplicates.append(row)
    else:
        row["selection"] = "proposed_shortlist"
        kept.append(row)
save(
    "shortlist-proposal.json",
    {
        "status": "Draft, no split or acceptance",
        "method": (
            "Same parent+anchor+states+review class, dHash <=5 to retained "
            "representative; all originals retained"
        ),
        "keep_ids": [r["candidate_id"] for r in kept],
        "alternatives": [
            {
                "candidate_id": r["candidate_id"],
                "representative_id": r["representative_id"],
                "distance": r["distance"],
            }
            for r in duplicates
        ],
        "withheld_ids": [r["candidate_id"] for r in withheld],
    },
)
lookup = {r["candidate_id"]: r for r in candidates}
(OUT / "duplicates-final").mkdir(exist_ok=True)
for off in range(0, len(duplicates), 8):
    board = Image.new("RGB", (960, 1088), "white")
    draw = ImageDraw.Draw(board)
    for slot, row in enumerate(duplicates[off : off + 8]):
        x, y = slot % 2 * 480, slot // 2 * 272
        rep = lookup[row["representative_id"]]
        draw.text(
            (x + 2, y + 2),
            row["candidate_id"] + " -> " + rep["candidate_id"] + " d=" + str(row["distance"]),
            fill="black",
        )
        for dx, item in [(0, row), (240, rep)]:
            im = Image.open(ROOT / item["input"]).convert("RGB")
            im.thumbnail((224, 224))
            board.paste(im, (x + dx, y + 36))
    board.save(OUT / f"duplicates-final/{off // 8 + 1:02}.png")

frame_ledger = []
for row in owner["frames"]:
    deriv = [r["candidate_id"] for r in derivatives if r["source"] == row["path"]]
    frame_ledger.append(
        {
            **row,
            "sha256": digest(ROOT / row["path"]),
            "overview_reviewed": True,
            "crop_ids_reviewed": row["crop_ids"],
            "derivative_ids": deriv,
            "scope": (
                "All listed anchors reviewed; not exhaustive detector annotation of every person"
            ),
        }
    )
save("frame-review-ledger.json", frame_ledger)
summary = {
    "original_crops": len(ledger),
    "source_frames": len(frame_ledger),
    "source_parents": len({r["parent_id"] for r in ledger}),
    "recrops": len(replacements),
    "new_crops": len(derivatives) - len(replacements),
    "draft_derivatives": len(derivatives),
    "owner_comparison": dict(Counter(r["comparison"] for r in ledger)),
    "shortlist": len(kept),
    "redundant_alternatives": len(duplicates),
    "withheld": len(withheld),
    "shortlist_labels": dict(Counter(r["draft_labels"] for r in kept)),
    "shortlist_by_parent": dict(Counter(r["parent_id"] for r in kept)),
    "all_originals_preserved": True,
    "accepted_new_records": 0,
    "assigned_splits": 0,
}
save("summary.json", summary)


# Inline data, no server/fetch/network dependency. Media use repository-relative links.
def link(path):
    return Path(os.path.relpath(ROOT / path, OUT)).as_posix()


cards = []
for row in ledger:
    active = replacements.get(row["sample_id"])
    eff = lookup[active["candidate_id"] if active else row["sample_id"]]
    original = link(row["crop"])
    derived = link(active["crop"]) if active else None
    target = active or row
    # Source overlay marks original and proposed context, not a detector/person box.
    overlay = Image.open(ROOT / row["source"]).convert("RGB")
    draw = ImageDraw.Draw(overlay)
    draw.rectangle(row["context_xyxy"], outline="#ff9900", width=4)
    if active:
        draw.rectangle(active["context_xyxy"], outline="#00ff66", width=4)
    (OUT / "source-overlays").mkdir(exist_ok=True)
    overlay_path = OUT / "source-overlays" / f"{row['sample_id']}.jpg"
    overlay.save(overlay_path, quality=90)
    cards.append(
        {
            "id": row["sample_id"],
            "anchor": row["anchor_id"],
            "parent": row["parent_id"],
            "owner": row["owner_explicit_labels"] or "Nhận xét / chưa có nhãn",
            "old": row["draft_labels"],
            "labels": target["draft_labels"],
            "reason": row["reason"],
            "newReason": eff.get("reason", ""),
            "comparison": row["comparison"],
            "selection": eff["selection"],
            "representative": eff.get("representative_id"),
            "original": original,
            "derived": derived,
            "preview": link(active["input"]) if active else original,
            "source": link(row["source"]),
            "overlay": Path(os.path.relpath(overlay_path, OUT)).as_posix(),
            "replacement": row["replacement_id"],
            "comments": row["owner_comments"],
            "sha": target["crop_sha256"],
        }
    )
for row in derivatives:
    if "original_id" in row:
        continue
    eff = lookup[row["candidate_id"]]
    cards.append(
        {
            "id": row["candidate_id"],
            "anchor": row["anchor_id"],
            "parent": row["parent_id"],
            "owner": "Mẫu mới",
            "old": "—",
            "labels": row["draft_labels"],
            "reason": row["reason"],
            "newReason": "",
            "comparison": "new_crop_pending_owner",
            "selection": eff["selection"],
            "representative": eff.get("representative_id"),
            "original": link(row["crop"]),
            "derived": None,
            "preview": link(row["input"]),
            "source": link(row["source"]),
            "overlay": link(row["source"]),
            "replacement": None,
            "comments": [],
            "sha": row["crop_sha256"],
        }
    )
payload = json.dumps(cards, ensure_ascii=False).replace("</", "<\\/")
template = (HERE / "gallery-template.html").read_text(encoding="utf-8")
(OUT / "index.html").write_text(template.replace("PAYLOAD", payload), encoding="utf-8")
exceptions = [
    r
    for r in ledger
    if r["comparison"] in {"draft_disagreement", "conditional_owner_anchor_mismatch"}
]
lines = [
    "# Ngoại lệ nhãn Draft so với cột nhãn owner",
    "",
    (
        "Bảng này so sánh đúng crop gốc; bản recrop có SHA và proposal riêng. Các "
        "nhận xét có điều kiện không tự thành approval."
    ),
    "",
    "| ID | Owner | Audit crop gốc | Lý do |",
    "|---|---|---|---|",
]
for row in exceptions:
    lines.append(
        f"| {row['sample_id']} | {row['owner_explicit_labels']} | "
        f"{row['draft_labels']} | {row['reason']} |"
    )
(HERE / "exceptions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(summary))
