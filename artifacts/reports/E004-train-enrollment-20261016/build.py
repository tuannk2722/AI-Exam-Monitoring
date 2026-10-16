"""Owner-authorized package assembly via canonical codec/exporter APIs."""

import json
import subprocess
from collections import Counter
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from ai_exam_monitoring.common.history import restore
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import test_freeze_attestation, verify_payload
from ai_exam_monitoring.data.pilot_package import build_pilot_package
from ai_exam_monitoring.data.pilot_schema import (
    DERIVED_SCHEMA_VERSION,
    GroupReview,
    ReviewEvidence,
    read_records,
    record_to_dict,
)
from ai_exam_monitoring.training.data import verify_dataset

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CONFIG = ROOT / "configs/datasets/E004-c345-20261016.json"
APPROVAL = HERE / "owner-enrollment-approval.json"
PREFIX = "outputs/_scratch/e004-v9-consolidation-20261013/sources"
RESTORE = Path("\\\\?\\" + str(ROOT / "outputs/_scratch/c345-restore"))
DATA = ROOT / "data/interim/E004-train-enrollment-20261016"
CANONICAL = ROOT / "data/processed/pilot-b/pilot-b-20261016-v10"
DEVELOPMENT = ROOT / "data/processed/e004/E004-c345-development-20261016"


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


if CANONICAL.exists() or DEVELOPMENT.exists():
    raise RuntimeError("Output already exists; preserve packages")
parent = ROOT / "data/processed/pilot-b/pilot-b-20261013-v9"
parent_dev = ROOT / "data/processed/e004/E004-v9-development-20261013"
verify_payload(parent)
verify_payload(parent_dev)
base = read_records(parent / "review-ledger.jsonl")
base_dev = read_records(parent_dev / "review-ledger.jsonl")
pending = read_records(DATA / "pending-ledger.jsonl")
accepted = read(HERE.parent / "E004-accepted-coverage-20261016/accepted-ledger.json")
assert len(pending) == len(accepted) == 345
approval = {
    "status": "approved", "owner": "repository-owner", "reviewer": "repository-owner",
    "recorded_at": "2026-10-16", "decision": "approve_c345_geometry_group_enrollment_and_research",
    "authority": "Owner replies: Duyệt batch geometry và group đề xuất; Duyệt thiết kế, compute và giới hạn research",
    "geometry": pin(HERE / "geometry-proposals.json"),
    "group_proposal": pin(HERE / "lineage-proposal.md"),
    "experiment_design": pin(HERE / "experiment-proposal.md"),
    "derivative_contract": pin(HERE / "owner-direction.md"),
    "new_train_ids": sorted(r.sample_id for r in pending),
    "new_group": "E004-CROP-TRAIN-Q001", "preserve_parent_roles_and_content": True,
    "waive_independence": True, "waive_support_shortfalls": True,
    "waiver_scope": "Research only with acknowledged coverage/independence limitations; not quality or promotion waiver",
    "final_test_inference_authorized": False,
    "compute": {"device": "cpu", "threads": 4, "run_wall_time_seconds": 7200,
                "smoke": "technical validation before one E004-C345-W-H research run"},
}
write(APPROVAL, approval)
ref = APPROVAL.relative_to(ROOT).as_posix()
review = ReviewEvidence("repository-owner", "2026-10-16", ref)
roots = {}
for row in base:
    roots[row.source.source_id] = RESTORE / PREFIX / row.source.source_id
backup = read(HERE.parent / "E004-v9-consolidation-20261013/backup-receipt.json")
restored = restore(ROOT / backup["archive"], RESTORE, prefixes=(PREFIX,),
                   expected_sha256=backup["sha256"])
write(HERE / "source-restore-receipt.json", {"archive": backup["archive"],
      "sha256": backup["sha256"], "prefix": PREFIX, "files": restored,
      "purpose": "source integrity/export only; protected media not visually reviewed"})
new_rows = []
crop_inputs = {r.sample_id: parent / r.crop.crop_relpath for r in base
               if r.crop and (parent / r.crop.crop_relpath).is_file()}
lookup = {r["id"]: r for r in accepted}
for row in pending:
    entry = lookup[row.sample_id]
    source_path = ROOT / entry["source"]
    source_root = source_path.parent.parent
    roots[row.source.source_id] = source_root
    assert row.crop is not None
    crop_review = replace(review, crop_sha256=row.crop.crop_sha256)
    new_rows.append(replace(
        row, source=replace(row.source, image_relpath=source_path.relative_to(source_root).as_posix()),
        crop=replace(row.crop, review=crop_review),
        group=GroupReview("E004-CROP-TRAIN-Q001", (ref,), review,
                          video_id=entry["parent_video_id"]),
        disposition="approved", usage="train", split="train", split_version="temporary",
        ineligibility_reasons=(), owner_decision_ref=ref, release_review=crop_review,
        use_scope="local_classifier_research",
    ))
    crop_inputs[row.sample_id] = ROOT / entry["crop"]
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
config = {
    "status": "owner_authorized_assembly", "parent": pin(parent / "checksums.sha256"),
    "parent_development": pin(parent_dev / "checksums.sha256"), "approval": pin(APPROVAL),
    "canonical_output": CANONICAL.relative_to(ROOT).as_posix(),
    "development_output": DEVELOPMENT.relative_to(ROOT).as_posix(),
    "expected_new_train": 345, "expected_train": 1061,
    "preserve_labels_crops_groups_evaluation": True,
    "semantics_revision": "E004-PHONE-OCCLUSION-20261015 for new rows only; parent unchanged",
}
write(CONFIG, config)
pointers = {}
for folder, old_rows, selection_path in (
    (CANONICAL, base, parent / "selection.jsonl"),
    (DEVELOPMENT, base_dev, parent_dev / "selection.jsonl"),
):
    version = folder.name
    rows = [replace(r, dataset_version=version, selection_version="E004-c345-enrollment-20261016",
                    crop_policy_version="E004-c345-reviewed-import-20261016",
                    schema_version=DERIVED_SCHEMA_VERSION,
                    split_version="E004-c345-preserved-20261016" if r.split else None)
            for r in old_rows + new_rows]
    old_by_id = {r.sample_id: r for r in old_rows}
    for row in rows:
        if row.sample_id in old_by_id:
            before = record_to_dict(old_by_id[row.sample_id])
            after = record_to_dict(row)
            after["crop"] and after["crop"].pop("derivation", None)
            for field in ("dataset_version", "selection_version", "crop_policy_version",
                          "schema_version", "split_version"):
                before.pop(field)
                after.pop(field)
            assert json.loads(json.dumps(before)) == json.loads(json.dumps(after)), row.sample_id
    metadata = {
        "status": "accepted", "dataset_version": version, "git_commit": commit,
        "workspace_dirty": True, "owner_decision_ref": ref, "schema_config_review_ref": ref,
        "split_config_review_ref": ref, "leakage_review_ref": ref,
        "test_freeze_ref": "release.json#test_freeze", "config_ref": CONFIG.relative_to(ROOT).as_posix(),
        "config_sha256": sha256_file(CONFIG), "approved_use_scope": ["local_classifier_research"],
        "use_scope": "local_classifier_research", "expected_source_counts": dict(Counter(r.source.source_id for r in rows)),
        "limitations": ["Owner-approved research quarantine; independence not proven; M4 inconclusive",
                        "New rows use scoped visible-absence semantics; parent labels unchanged",
                        "Parent test/reserve preserved; integrity decode/copy only, no visual review/inference"],
        "source_attribution_refs": [ref], "training_run_approved": False,
        "test_freeze": test_freeze_attestation(rows, config_sha256=sha256_file(CONFIG),
            approval_sha256=sha256_file(APPROVAL), owner_decision_ref=ref, approval=approval,
            commit=commit, protocol="Preserve original test identity; no new test access or inference"),
    }
    selection = [json.loads(line) for line in selection_path.read_text(encoding="utf8").splitlines()]
    build_pilot_package(rows, folder, roots, crop_inputs, selection, metadata,
                        [r.sample_id for r in rows])
    verify_payload(folder)
    loader = verify_dataset(folder, SimpleNamespace(
        dataset=folder.relative_to(ROOT).as_posix(), dataset_version=version,
        split_version="E004-c345-preserved-20261016", encoding_version="pilot-b-targets-v1",
        payload_sha256=sha256_file(folder / "checksums.sha256")))
    assert sum(r.usage == "train" for r in loader) == 1061
    pointers[version] = {"package": folder.relative_to(ROOT).as_posix(),
        "payload_sha256": sha256_file(folder / "checksums.sha256"),
        "ledger_counts": dict(Counter(r.usage for r in rows)), "manifest_records": len(loader),
        "parent_record_content_preserved": len(old_rows), "loader": "PASS"}
    print(version, pointers[version], flush=True)
write(HERE / "package-pointers.json", pointers)
