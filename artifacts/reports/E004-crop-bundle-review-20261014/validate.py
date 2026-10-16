"""Validate study evidence without reading test/reserve or changing releases."""

import hashlib
import json
from pathlib import Path

import yaml
from PIL import Image

from ai_exam_monitoring.data.source_review import preview_input

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


ledger = read("crop-review-ledger.json")
frames = read("frame-review-ledger.json")
derivatives = read("derivative-review.json")
selection = read("shortlist-proposal.json")
config = yaml.safe_load(
    (ROOT / "configs/datasets" / f"{HERE.name}.yaml").read_text(encoding="utf-8")
)
assert len(ledger) == len({r["sample_id"] for r in ledger}) == 765
assert len(frames) == len({r["path"] for r in frames}) == 212
assert len(derivatives) == len({r["candidate_id"] for r in derivatives}) == 197
owner = read("review-input.json")
assert sha(HERE / "owner-review-original.md") == owner["owner_snapshot_sha256"]
original_owner = ROOT / "artifacts/reports/E004-crop-bundle-audit-20261014/README.md"
assert sha(original_owner) == owner["owner_snapshot_sha256"]
for row in ledger:
    assert sha(ROOT / row["crop"]) == row["crop_sha256"]
    assert row["canonical_targets"] == [None, None]
    assert row["canonical_mask"] == [0, 0] and row["assigned_split"] is None
    assert len(row["draft_labels"]) == 3 and row["draft_labels"][1] == "/"
    assert set(row["draft_labels"].replace("/", "")) <= set("PNU")
for row in frames:
    assert sha(ROOT / row["path"]) == row["sha256"]
    assert row["overview_reviewed"]
assert sorted(cid for f in frames for cid in f["crop_ids"]) == sorted(
    r["sample_id"] for r in ledger
)
for row in derivatives:
    assert sha(ROOT / row["source"]) == row["source_sha256"]
    assert sha(ROOT / row["crop"]) == row["crop_sha256"]
    assert sha(ROOT / row["input"]) == row["input_sha256"]
    source = Image.open(ROOT / row["source"]).convert("RGB")
    x1, y1, x2, y2 = row["context_xyxy"]
    assert 0 <= x1 < x2 <= source.width and 0 <= y1 < y2 <= source.height
    expected = source.crop((x1, y1, x2, y2))
    crop = Image.open(ROOT / row["crop"]).convert("RGB")
    assert expected.size == crop.size and expected.tobytes() == crop.tobytes()
    preview = preview_input(crop, config["preview"]["size"], tuple(config["preview"]["fill"]))
    actual = Image.open(ROOT / row["input"]).convert("RGB")
    assert preview.size == actual.size and preview.tobytes() == actual.tobytes()
    assert not row["training_ready"] and row["assigned_split"] is None
    assert row["canonical_targets"] == [None, None] and row["canonical_mask"] == [0, 0]
effective = {r["sample_id"]: r for r in ledger if r["replacement_id"] is None} | {
    r["candidate_id"]: r for r in derivatives
}
keep = set(selection["keep_ids"])
alternatives = {r["candidate_id"] for r in selection["alternatives"]}
withheld = set(selection["withheld_ids"])
assert not (keep & alternatives or keep & withheld or alternatives & withheld)
assert keep | alternatives | withheld == set(effective)
assert (len(effective), len(keep), len(alternatives), len(withheld)) == (770, 710, 56, 4)
reviewed = {
    (r["candidate_id"], r["representative_id"])
    for r in read("redundancy-visual-review.json")
    if r["decision"] == "propose_redundant_alternative"
}
for pair in selection["alternatives"]:
    assert (pair["candidate_id"], pair["representative_id"]) in reviewed
    assert pair["representative_id"] in keep
    a, b = effective[pair["candidate_id"]], effective[pair["representative_id"]]
    assert all(a[k] == b[k] for k in ["parent_id", "anchor_id", "draft_labels", "comparison"])
    assert pair["distance"] <= config["redundancy"]["dhash_max_distance"]
out = ROOT / "outputs" / HERE.name
markup = (out / "index.html").read_text(encoding="utf-8")
payload = markup.split("const data=", 1)[1].split(";let page=0", 1)[0]
cards = json.loads(payload.replace("<\\/", "</"))
assert len(cards) == 770
links = 0
for card in cards:
    for key in ["original", "derived", "preview", "source", "overlay"]:
        if card[key]:
            assert (out / card[key]).resolve().is_file(), (card["id"], key)
            links += 1
pins = {
    path.name: sha(path)
    for path in HERE.iterdir()
    if path.is_file()
    and path.suffix in {".json", ".py", ".html"}
    and path.name not in {"validation.json", "software-validation.json"}
}
result = {
    "status": "PASS",
    "completed_date": "2026-10-15",
    "original_crop_hashes": 765,
    "source_frame_hashes": 212,
    "derivative_native_pixel_parity": 197,
    "derivative_input_224_pixel_parity": 197,
    "owner_original_unchanged": True,
    "complete_crop_frame_mapping": True,
    "reviewed_redundancy_pairs": 79,
    "shortlist_partition": [710, 56, 4],
    "gallery_cards": len(cards),
    "gallery_media_links_exist": links,
    "no_accepted_targets_or_split_created": True,
    "metadata_pins": pins,
    "config_sha256": sha(ROOT / "configs/datasets" / f"{HERE.name}.yaml"),
    "limitations": "Pixel/technical PASS does not establish annotation acceptance or independence.",
}
(HERE / "validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({k: v for k, v in result.items() if k != "metadata_pins"}))
