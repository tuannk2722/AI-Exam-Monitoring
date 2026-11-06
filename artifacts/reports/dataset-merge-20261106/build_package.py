"""Materialize the reviewed batch using the active strict codec/exporter.

This worksheet contains batch wiring; package rules remain in pilot_package.
Existing accepted payloads and pinned review evidence are read-only inputs.
"""

import hashlib
import json
import subprocess
import sys
import zipfile
from collections import Counter
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import verify_payload
from ai_exam_monitoring.data.pilot_package import build_pilot_package
from ai_exam_monitoring.data.pilot_schema import (
    DERIVED_SCHEMA_VERSION, ContextReview, CropDerivation, CropRef, GroupReview,
    PilotRecord, PixelBox, ReviewEvidence, RightsReview, SourceRef, TargetReview,
    read_records, validate_records, write_records,
)
from ai_exam_monitoring.training.data import verify_dataset

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
REL = REPORT.relative_to(ROOT).as_posix()
BATCH = ROOT / "data/interim/dataset-merge-20261106"
PARENT = ROOT / "data/processed/pilot-b/pilot-b-20261024-v14"
DATASET = "pilot-b-20261106-v15"
SPLIT = "owner-delegated-group-train-val-20261106-v15"
OUTPUT = ROOT / "data/processed/pilot-b" / DATASET
OWNER = f"{REL}/owner-direction.json"
VISUAL = f"{REL}/visual-review.json"
LINEAGE = f"{REL}/group-lineage.json"
ALLOCATION = f"{REL}/allocation.json"
STATES = {"P": "positive", "N": "negative", "U": "unknown"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    if path.exists():
        raise RuntimeError(f"Do not overwrite a package input/output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def evidence(ref, digest=None):
    return ReviewEvidence("agent-under-owner-delegation", "2026-11-06", ref, digest)


def main():
    if OUTPUT.exists() or (REPORT / "package-pointers.json").exists():
        raise RuntimeError("V15 already materialized; never overwrite")
    parent_pins = load(ROOT / "artifacts/reports/dataset-release-20261024-v14/package-pointers.json")
    for name in ("payload", "manifest", "release", "ledger", "config"):
        assert sha256_file(ROOT / parent_pins[name]["path"]) == parent_pins[name]["sha256"]
    verify_payload(PARENT)
    print("parent V14 payload/pins PASS", flush=True)
    inv = load(REPORT / "inventory.json")
    visual = load(REPORT / "visual-review.json")
    reviews = {r["id"]: r for r in visual["rows"]}
    allocation = load(REPORT / "allocation.json")
    assignments = {r["id"]: r for r in allocation["rows"]}
    lineage = {r["id"]: r for r in load(REPORT / "group-lineage.json")["rows"]}
    readme = ROOT / "artifacts/reports/accepted-frames-crops-20261105/README.md"
    assert sha256_file(readme) == inv["readme_sha256"]
    for row in inv["imports"]:
        assert sha256_file(ROOT / row["path"]) == row["sha256"]
    source_archive = ROOT / visual["input_archive"]["path"]
    assert sha256_file(source_archive) == visual["input_archive"]["sha256"]
    with zipfile.ZipFile(source_archive) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {Path(r["path"]).name for r in inv["imports"]}
        for row in inv["imports"]:
            assert hashlib.sha256(z.read(Path(row["path"]).name)).hexdigest() == row["sha256"]
    native_geometry = load(ROOT / "data/interim/accepted-frames-crops-20261105/manifest.json")
    frame_pins = load(ROOT / "artifacts/reports/accepted-frames-crops-20261105/inventory.json")
    frame_by_member = {r["member"]: r for r in frame_pins}
    zip_path = Path("D:/dataset-foundry-starter/exports/accepted_frames.zip")
    zip_sha = "c836bfb05348ebb814d859c1d260beae5238dc3d94a0c3ee6c5f8a8e74f3d088"
    assert sha256_file(zip_path) == zip_sha
    frames_root = BATCH / "source-frames"
    frames_root.mkdir()
    with zipfile.ZipFile(zip_path) as z:
        for member in sorted({r["source_member"] for r in native_geometry}):
            target = (frames_root / member).resolve()
            assert target.is_relative_to(frames_root.resolve())
            raw = z.read(member)
            assert hashlib.sha256(raw).hexdigest() == frame_by_member[member]["sha256"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    roots = load(ROOT / "artifacts/reports/dataset-release-20261024-v14/source-roots.json")
    roots.update({"accepted-frames-20261105": frames_root.relative_to(ROOT).as_posix(),
                  "owner-crops-20261106": (BATCH / "imports").relative_to(ROOT).as_posix()})
    crop_inputs = {}
    records = []
    parent = read_records(PARENT / "review-ledger.jsonl")
    for r in parent:
        changes = dict(dataset_version=DATASET, selection_version="owner-crop-audit-20261106",
                       crop_policy_version="reviewed-context-20261106-v15")
        if r.crop:
            original_crop = PARENT / r.crop.crop_relpath
            if not original_crop.exists():
                original_crop = ROOT / roots[r.source.source_id] / r.source.image_relpath
            assert sha256_file(original_crop) == r.crop.crop_sha256
            crop_inputs[r.sample_id] = original_crop
        if r.sample_id in {"V6-SB-048-ADD01", "G08-B01-F00001"}:
            changes.update(disposition="excluded", usage="excluded", split=None, split_version=None,
                           exclusion_reason="Owner explicit exclusion on 2026-11-06", owner_decision_ref=OWNER,
                           release_review=evidence(OWNER), test_freeze_ref=None, ineligibility_reasons=())
        elif r.usage != "excluded":
            assignment = assignments[r.sample_id]
            changes.update(usage=assignment["split"], split=assignment["split"], split_version=SPLIT,
                           owner_decision_ref=OWNER, release_review=evidence(OWNER), test_freeze_ref=None)
            if r.sample_id == "G09-B05-F00043":
                review = evidence(OWNER + "#parent-relabel", r.crop.crop_sha256)
                changes.update(phone_use=TargetReview("negative", "Owner explicit N/P decision", review),
                               looking_around=TargetReview("positive", "Owner explicit N/P decision", review))
        records.append(replace(r, **changes))
    rights = RightsReview("owner-provided-local-research", OWNER, ("local_classifier_research",), evidence(OWNER))
    for g in native_geometry:
        sid = g["crop_id"]
        frame = frame_by_member[g["source_member"]]
        source = SourceRef("accepted-frames-20261105", zip_sha, g["source_member"],
                           g["source_sha256"], *g["source_size"], aliases=(f"source-family:{g['source_id']}",))
        include = sid in reviews
        review = evidence(VISUAL + "#" + sid, g["crop_sha256"]) if include else None
        crop = CropRef(g["anchor_id"], PixelBox(*g["person_box"]), PixelBox(*g["context_box"]),
                       f"crops/{sid}.png", g["crop_sha256"], review)
        kwargs = dict(disposition="excluded", usage="excluded", owner_decision_ref=OWNER,
                      exclusion_reason="Not named in owner README; default exclude per owner instruction")
        label = "UU"
        group = None
        if include:
            row = reviews[sid]
            label = row["final_label"]
            a = assignments[sid]
            group = GroupReview(a["group"], (LINEAGE, ALLOCATION), evidence(LINEAGE), video_id=frame["parent_id"])
            kwargs = dict(disposition="approved", usage=a["split"], split=a["split"], split_version=SPLIT,
                          owner_decision_ref=OWNER, release_review=evidence(OWNER), use_scope="local_classifier_research")
            crop_inputs[sid] = ROOT / "data/interim/accepted-frames-crops-20261105" / g["crop_path"]
            with Image.open(frames_root / g["source_member"]) as original, Image.open(crop_inputs[sid]) as approved:
                assert original.convert("RGB").crop(tuple(g["context_box"])).tobytes() == approved.convert("RGB").tobytes()
        targets = [TargetReview(STATES[s], "Owner reviewed native crop; scoped semantics 23/10" if include else
                                "Excluded membership; target not assigned", review) for s in label]
        records.append(PilotRecord(
            sid, DATASET, "owner-crop-audit-20261106", "reviewed-context-20261106-v15", source,
            *targets, ContextReview("unknown", "No separate work-context review"), rights,
            crop=crop, group=group, schema_version=DERIVED_SCHEMA_VERSION, **kwargs))
    for row in inv["imports"]:
        sid = row["id"]
        w, h = row["size"]
        r, a = reviews[sid], assignments[sid]
        digest = row["sha256"]
        ev = evidence(VISUAL + "#" + sid, digest)
        source = SourceRef("owner-crops-20261106", visual["input_archive"]["sha256"], Path(row["path"]).name,
                           digest, w, h, aliases=(row["original_name"], LINEAGE + "#" + sid))
        derivation = CropDerivation(digest, row["rgb_sha256"], w, h, row["format"],
                                    VISUAL + "#delivered-blob-source-boundary", ev)
        suffix = ".jpg" if row["format"] == "JPEG" else ".png"
        crop = CropRef("owner-selected-anchor", PixelBox(*r["person_box"]), PixelBox(0, 0, w, h),
                       f"crops/{sid}{suffix}", digest, ev, derivation)
        group = GroupReview(a["group"], (LINEAGE, ALLOCATION), evidence(LINEAGE))
        targets = [TargetReview(STATES[s], r["phone_reason"] if t == 0 else r["looking_reason"], ev)
                   for t, s in enumerate(r["final_label"])]
        records.append(PilotRecord(
            sid, DATASET, "owner-crop-audit-20261106", "reviewed-context-20261106-v15", source,
            *targets, ContextReview("unknown", "No separate work-context review"), rights, crop=crop,
            group=group, disposition="approved", usage=a["split"], split=a["split"], split_version=SPLIT,
            owner_decision_ref=OWNER, release_review=evidence(OWNER), use_scope="local_classifier_research",
            schema_version=DERIVED_SCHEMA_VERSION))
        crop_inputs[sid] = ROOT / row["path"]
    validate_records(records)
    assert len(records) == 1999 and Counter(r.usage for r in records) == {
        "train": 1377, "val": 344, "excluded": 278}
    write_records(BATCH / "review-ledger.jsonl", records)
    save(REPORT / "source-roots.json", roots)
    save(REPORT / "input-pins.json", {
        "parent": parent_pins, "readme": pin(readme),
        "raw_imports": visual["input_archive"], "raw_frames": {"path": str(zip_path), "sha256": zip_sha},
        "inventory": pin(REPORT / "inventory.json"), "visual_review": pin(REPORT / "visual-review.json"),
        "allocation": pin(REPORT / "allocation.json"), "lineage": pin(REPORT / "group-lineage.json"),
    })
    config_path = ROOT / "configs/datasets" / (DATASET + ".json")
    config = {
        "dataset_version": DATASET, "parent": "pilot-b-20261024-v14", "parent_payload": parent_pins["payload"],
        "owner_direction": pin(REPORT / "owner-direction.json"), "allocation": pin(REPORT / "allocation.json"),
        "visual_review": pin(REPORT / "visual-review.json"), "lineage": pin(REPORT / "group-lineage.json"),
        "candidate_ledger": pin(BATCH / "review-ledger.jsonl"), "output": OUTPUT.relative_to(ROOT).as_posix(),
        "use_scope": "local_classifier_research", "split_version": SPLIT, "test_count": 0,
        "counts": {"train": 1377, "val": 344, "excluded": 278},
        "intended_next_experiment": "E009; recipe/run approval is separate",
    }
    save(config_path, config)
    code_paths = [Path(__file__), REPORT / "prepare_qa.py", REPORT / "inspect_pairs.py",
                  REPORT / "propose_geometry.py", REPORT / "finalize_qa.py", REPORT / "allocate.py",
                  ROOT / "src/ai_exam_monitoring/data/pilot_schema.py",
                  ROOT / "src/ai_exam_monitoring/data/pilot_package.py"]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = {
        "dataset_version": DATASET, "parent_dataset_version": "pilot-b-20261024-v14", "status": "accepted",
        "git_commit": commit, "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
        "config_ref": config_path.relative_to(ROOT).as_posix(), "config_sha256": sha256_file(config_path),
        "owner_decision_ref": OWNER, "schema_config_review_ref": OWNER,
        "split_config_review_ref": ALLOCATION, "test_freeze_ref": OWNER + "#no-test-v15",
        "test_freeze": {"status": "not_applicable_zero_test", "independent_holdout": "future_separate_protocol"},
        "leakage_review_ref": LINEAGE, "approved_use_scope": ["local_classifier_research"],
        "use_scope": "local_classifier_research", "semantics_review_ref": "artifacts/reports/v12-reconcile-20261022/owner-policy-20261023.md",
        "source_attribution_refs": [OWNER, LINEAGE], "expected_source_counts": dict(Counter(r.source.source_id for r in records)),
        "tooling_sha256": {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in code_paths},
        "environment": {"python": sys.version, **{p: version(p) for p in ("numpy", "scipy", "Pillow")}},
        "limitations": allocation["limitations"] + [
            "No classifier inference, training, final test or upload performed",
            "Owner-supplied/generated files preserve delivered bytes; no reproducible upstream generation recipe asserted",
            "Acceptance is exercised by agent within explicit owner delegation, not owner review of every computed box/split",
            "Correlated contextual variants retained and bounded to training families; crop count is not independent sample count",
        ],
    }
    result = build_pilot_package(records, OUTPUT, {k: ROOT / v for k, v in roots.items()}, crop_inputs,
                                 [], metadata, [r.sample_id for r in records])
    print("export PASS", flush=True)
    verify_payload(OUTPUT)
    dataset_variables = SimpleNamespace(dataset=OUTPUT.relative_to(ROOT).as_posix(), dataset_version=DATASET,
                                        split_version=SPLIT, encoding_version="pilot-b-targets-v1",
                                        payload_sha256=sha256_file(OUTPUT / "checksums.sha256"))
    loaded = verify_dataset(OUTPUT, dataset_variables)
    assert len(loaded) == 1721
    # Parent semantic/geometry/source records stay exact except three explicit decisions,
    # version/enrollment fields and reviewed split assignments.
    final = {r.sample_id: r for r in records}
    for r in parent:
        now = final[r.sample_id]
        assert now.source == r.source and now.crop == r.crop and now.work_context_review == r.work_context_review
        assert now.group == r.group and now.rights == r.rights
        if r.sample_id != "G09-B05-F00043":
            assert now.phone_use == r.phone_use and now.looking_around == r.looking_around
    for name in ("payload", "manifest", "release", "ledger", "config"):
        assert sha256_file(ROOT / parent_pins[name]["path"]) == parent_pins[name]["sha256"]
    pointers = {"dataset": OUTPUT.relative_to(ROOT).as_posix(),
                **{name: pin(OUTPUT / filename) for name, filename in
                   (("payload", "checksums.sha256"), ("manifest", "manifest.jsonl"),
                    ("release", "release.json"), ("ledger", "review-ledger.jsonl"))},
                "config": pin(config_path)}
    save(REPORT / "package-pointers.json", pointers)
    save(REPORT / "export-validation.json", {
        "status": "PASS", "strict_codec": "PASS", "exporter_source_crop_preflight": "PASS",
        "payload_integrity": "PASS", "strict_training_loader": "PASS",
        "records": len(records), "used": len(loaded), "usage": dict(Counter(r.usage for r in records)),
        "parent_pins_source_geometry_targets_preserved_except_explicit_label": "PASS",
        "all_368_new_crops_enrolled": True, "native_excluded": 274, "parent_excluded_total": 4,
        "raw_import_snapshot_verified": True, "new_test_records": 0,
        "export_result_keys": sorted(result),
    })
    print(json.dumps({"dataset": str(OUTPUT), "used": len(loaded), "payload_sha256": pointers["payload"]["sha256"]}))


if __name__ == "__main__":
    main()
