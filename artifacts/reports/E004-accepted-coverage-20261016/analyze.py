"""Frozen coverage worksheet; does not enroll records or access protected media."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REPORTS = HERE.parent
inputs = {}
if (HERE / "result-pins.json").exists():
    raise RuntimeError("Preserve sealed report; use a new analysis identity")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    inputs[path.relative_to(ROOT).as_posix()] = sha(path)
    return json.loads(path.read_text(encoding="utf8"))


def write(name, value):
    (HERE / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
    )


def stats(rows):
    pairs = Counter(r["final_labels"] for r in rows)
    return {
        "count": len(rows),
        "pairs": dict(sorted(pairs.items())),
        "phone": dict(Counter(r["final_labels"][0] for r in rows)),
        "looking": dict(Counter(r["final_labels"][2] for r in rows)),
        "both_known": sum("U" not in r["final_labels"] for r in rows),
    }


def duplicates(rows, field):
    groups = defaultdict(list)
    for row in rows:
        groups[row[field]].append(row["id"])
    return [ids for ids in groups.values() if len(ids) > 1]


checked_pins = 0
for folder in ("E004-crop-closure-20261015", "E004-new-bundle-closure-20261016"):
    for path, expected in read(REPORTS / folder / "result-pins.json")["files"].items():
        assert sha(ROOT / path) == expected, path
        checked_pins += 1

ledger = []
batch_stats = {}
specs = [
    ("old240", "E004-crop-closure-20261015/candidate-ledger.json", 240),
    ("new92", "E004-new-bundle-closure-20261016/closed-ledger.json", 92),
    ("additions13", "E004-new-bundle-closure-20261016/additions-ledger.json", 13),
]
for batch, rel, expected in specs:
    rows = read(REPORTS / rel)
    if batch == "old240":
        rows = [r for r in rows if r["closure_disposition"] == "retained"]
    assert len(rows) == expected
    normalized = []
    for r in rows:
        row = {
            "id": r.get("id", r.get("candidate_id")),
            "batch": batch,
            "upstream_ledger": "artifacts/reports/" + rel,
            "final_labels": r["draft_labels"] if batch == "additions13" else r["final_labels"],
            "approval_ref": "approval-13.json" if batch == "additions13" else "artifacts/reports/" + rel,
            "status": "accepted_labels_and_existing_crop",
            "parent_video_id": Path(r["source"]).parent.name,
            "anchor_key": r.get("anchor_id"),
            "anchor_description": r.get("anchor_description", r.get("description")),
            "frame_num": r["frame_num"],
            "context_xyxy": r["context_xyxy"],
            "preferred_role": "train",
            "assigned_split": None,
            "training_ready": False,
        }
        for key in ("source", "crop", "input"):
            path = ROOT / r[key]
            digest = sha(path)
            assert digest == r[key + "_sha256"], r[key]
            row[key], row[key + "_sha256"] = r[key], digest
        with Image.open(ROOT / row["input"]) as im:
            rgb = im.convert("RGB")
            assert rgb.size == (224, 224), row["id"]
            row["input_rgb_sha256"] = hashlib.sha256(rgb.tobytes()).hexdigest()
        normalized.append(row)
    batch_stats[batch] = stats(normalized)
    ledger.extend(normalized)
assert len(ledger) == len({r["id"] for r in ledger}) == 345

package = ROOT / "data/processed/e004/E004-v9-development-20261013"
checkfile = package / "checksums.sha256"
inputs[checkfile.relative_to(ROOT).as_posix()] = sha(checkfile)
checks = dict(line.split("  ", 1)[::-1] for line in checkfile.read_text().splitlines())
manifest = package / "manifest.jsonl"
assert sha(manifest) == checks["manifest.jsonl"]
inputs[manifest.relative_to(ROOT).as_posix()] = sha(manifest)
baseline = [json.loads(line) for line in manifest.read_text(encoding="utf8").splitlines()]
run = ROOT / "outputs/E004-RC1-W-H"
run_checks = read(run / "checksums.json")
assert sha(run / "resolved-config.json") == run_checks["resolved-config.json"]
config = read(run / "resolved-config.json")
train_spec = next(c for c in config["cohorts"] if c["name"] == "train")
assert sha(checkfile) == train_spec["data"]["payload_sha256"]
cohorts = {c["name"]: set(c["sample_ids"]) for c in config["cohorts"]}
train = [r for r in baseline if r["sample_id"] in cohorts["train"]]
selection = [r for r in baseline if r["sample_id"] in cohorts["selection"]]
assert len(train) == 716 and len(selection) == 71
codec = {None: "U", 0: "N", 1: "P"}
base_labels = [{"final_labels": "/".join(codec[v] for v in r["target_values"])} for r in train]

# Metadata comparison only: no protected test/reserve images are opened.
canonical = ROOT / "data/processed/pilot-b/pilot-b-20261013-v9/manifest.jsonl"
inputs[canonical.relative_to(ROOT).as_posix()] = sha(canonical)
pointer = read(REPORTS / "E004-v9-consolidation-20261013/v9-release-pointer.json")
assert sha(canonical) == pointer["manifest_sha256"]
canonical_checks = canonical.parent / "checksums.sha256"
assert sha(canonical_checks) == pointer["checksums_sha256"]
inputs[canonical_checks.relative_to(ROOT).as_posix()] = sha(canonical_checks)
assert sha(canonical) == dict(
    line.split("  ", 1)[::-1] for line in canonical_checks.read_text().splitlines()
)["manifest.jsonl"]
canonical_rows = [json.loads(line) for line in canonical.read_text(encoding="utf8").splitlines()]
overlap = []
for r in ledger:
    for b in baseline + canonical_rows:
        matches = []
        if r["source_sha256"] == b["source"]["image_sha256"]:
            matches.append("source_sha256")
        if b.get("crop") and r["crop_sha256"] == b["crop"]["crop_sha256"]:
            matches.append("crop_sha256")
        if matches:
            overlap.append({"new_id": r["id"], "baseline_id": b["sample_id"], "split": b["split"], "matches": matches})

parents = {}
for parent in sorted({r["parent_video_id"] for r in ledger}):
    rows = [r for r in ledger if r["parent_video_id"] == parent]
    parents[parent] = {
        **stats(rows),
        "source_frames": len({r["source_sha256"] for r in rows}),
        "recorded_anchor_keys": len({r["anchor_key"] for r in rows if r["anchor_key"]}),
        "missing_anchor_key": sum(r["anchor_key"] is None for r in rows),
    }

summary = {
    "status": "accepted_crop_inventory_and_conditional_train_projection",
    "batches": batch_stats,
    "accepted_new": stats(ledger),
    "existing_train": stats(base_labels),
    "conditional_train_if_all_eligible": stats(base_labels + ledger),
    "existing_selection_unchanged": len(selection),
    "parents": parents,
    "exact_crop_duplicates_new": duplicates(ledger, "crop_sha256"),
    "exact_input_rgb_duplicates_new": duplicates(ledger, "input_rgb_sha256"),
    "exact_metadata_overlap": overlap,
    "lineage_limit": "Distinct parent video IDs are not proof of independent rooms, people or source lineage. No perceptual cross-baseline or protected-media audit performed.",
    "upstream_pin_files_verified": checked_pins,
}
write("approval-13.json", {
    "date": "2026-10-16", "reviewer": "repository-owner",
    "authority": "Current user message: approve all 13 new crops",
    "scope": "Labels and existing crop bytes for NC-001 through NC-013; training priority for new accepted crops. Not a canonical release or experiment approval.",
    "supersedes_status_only": "Draft status in frozen E004-new-bundle-closure-20261016/additions-ledger.json",
    "ids": [r["id"] for r in ledger if r["batch"] == "additions13"],
    "upstream_sha256": inputs["artifacts/reports/E004-new-bundle-closure-20261016/additions-ledger.json"],
})
write("accepted-ledger.json", ledger)
write("summary.json", summary)
write("input-pins.json", inputs)
print(json.dumps(summary, ensure_ascii=False, indent=2))
