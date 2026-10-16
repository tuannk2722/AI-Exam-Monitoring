"""Validate audit integrity without accessing any held-out dataset or model."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from PIL import Image, ImageChops

from ai_exam_monitoring.data.source_review import preview_input

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "outputs" / HERE.name


def read(p):
    return json.loads(p.read_text(encoding="utf8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


pins = read(HERE / "input-pins.json")
for path, expected in read(HERE / "result-pins.json")["files"].items():
    assert sha(ROOT / path) == expected, path
assert sha(HERE / "owner-review-original.md") == pins["owner_snapshot_sha256"]
assert (
    sha(ROOT / "artifacts/reports/E004-crop-bundle-review-20261014/README.md")
    == pins["owner_snapshot_sha256"]
)
for p, h in pins["files"].items():
    assert sha(ROOT / p) == h, p
for p, h in read(HERE / "reference-pins.json").items():
    assert sha(ROOT / p) == h, p

rows = read(HERE / "candidate-ledger.json")
assert len(rows) == 905
assert len({r["candidate_id"] for r in rows}) == 905
supplied = [r for r in rows if r["cohort"] == "supplied"]
assert {r["sample_id"] for r in supplied} == {f"CB-{i:04}" for i in range(1, 766)}
selected = [r for r in rows if r["disposition"] == "shortlist"]
assert len(selected) == 247
cache = {}
native = 0
paths = 0
for r in rows:
    assert r["assigned_split"] is None and not r["training_ready"]
    assert r["canonical_targets"] == [None, None] and r["canonical_mask"] == [0, 0]
    assert r["draft_labels"] in {f"{p}/{look}" for p in "PNU" for look in "PNU"}
    assert r["evidence_crop_sha256"] == r["crop_sha256"]
    assert r["revision_visual_status"] != "pending"
    if r["disposition"] == "shortlist":
        assert r["draft_labels"] != "U/U"
    for k in ["source", "crop", "input"]:
        p = ROOT / r[k]
        assert p.is_file(), p
        if p not in cache:
            cache[p] = sha(p)
        assert cache[p] == r[k + "_sha256"], p
        paths += 1
    with Image.open(ROOT / r["input"]) as inp:
        assert inp.size == (224, 224) and inp.mode == "RGB"
    # Original JPEG crops use the supplied rasterization; prior audit owns its reproduction check.
    if r["crop"].endswith(".png"):
        with (
            Image.open(ROOT / r["source"]) as src,
            Image.open(ROOT / r["crop"]) as crop,
            Image.open(ROOT / r["input"]) as inp,
        ):
            box = r["context_xyxy"]
            x1, y1, x2, y2 = box
            assert 0 <= x1 < x2 <= src.width and 0 <= y1 < y2 <= src.height
            expected = src.convert("RGB").crop(box)
            assert (
                crop.size == expected.size
                and not ImageChops.difference(crop.convert("RGB"), expected).getbbox()
            )
            prepared = preview_input(crop.convert("RGB"), 224, (124, 116, 104))
            assert not ImageChops.difference(prepared, inp.convert("RGB")).getbbox()
        native += 1
    if r["disposition"] == "alternative":
        assert all(
            any(
                x["candidate_id"] == c
                and x["anchor_id"] == r["anchor_id"]
                and x["disposition"] == "shortlist"
                for x in rows
            )
            for c in r["representative_candidates"]
        )

frames = read(HERE / "frame-coverage.json")
assert len(frames) == 212 and len({f["frame_id"] for f in frames}) == 212
assert all(f["refinement_visual_pass"].startswith("viewed") for f in frames)
for f in frames:
    assert (ROOT / f["path"]).exists()
    for c in f["new_candidates"]:
        assert any(r["candidate_id"] == c and r["source"] == f["path"] for r in rows)
assert sum(len(f["new_candidates"]) for f in frames) == 135

html = (OUT / "index.html").read_text(encoding="utf8")
data = json.loads(html.split("const DATA=", 1)[1].split(";\nconst $=", 1)[0])
assert len(data) == len(rows)
for d in data:
    for k in ["input", "source", "crop", "overlay"]:
        if d[k]:
            assert (OUT / d[k]).resolve().is_file(), d[k]
            paths += 1
for path in HERE.glob("*.md"):
    link_root = (
        ROOT / "artifacts/reports/E004-crop-bundle-review-20261014"
        if path.name == "owner-review-original.md"
        else path.parent
    )
    for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf8")):
        if "://" not in link and not link.startswith("#"):
            target = link_root / link.split("#")[0]
            if target == HERE / "validation.json":
                continue  # Generated only after all assertions in this script pass.
            assert target.exists(), (path.name, link)
for p in [HERE / "visual-decisions.json", HERE / "new-observations.json", HERE / "README.md"]:
    text = p.read_text(encoding="utf8")
    assert "\ufffd" not in text and not re.search(r"\w\?\w", text), p
result = dict(
    status="PASS",
    candidates=len(rows),
    frames=212,
    selected=len(selected),
    selected_anchors=len({r["anchor_id"] for r in selected}),
    dispositions=dict(Counter(r["disposition"] for r in rows)),
    native_png_source_and_input_parity=native,
    path_checks=paths,
    all_905_source_crop_input_hashes=True,
    owner_snapshot_unchanged=True,
    canonical_targets_null=True,
    split_unassigned=True,
    scope="audit study only; not data/model acceptance",
    worksheet_python="repository .venv; no model inference",
)
(HERE / "validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
)
print(json.dumps(result))
