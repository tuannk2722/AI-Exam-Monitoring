"""One-time V11 assembly worksheet; all contracts use the canonical exporter."""

import json
import subprocess
from collections import Counter
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from ai_exam_monitoring.common.history import restore
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import test_freeze_attestation, verify_payload
from ai_exam_monitoring.data.pilot_package import build_pilot_package
from ai_exam_monitoring.data.pilot_schema import (
    DERIVED_SCHEMA_VERSION,
    ContextReview,
    CropRef,
    GroupReview,
    PilotRecord,
    PixelBox,
    ReviewEvidence,
    RightsReview,
    SourceRef,
    TargetReview,
    read_records,
    record_to_dict,
)
from ai_exam_monitoring.training.data import verify_dataset

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PLAN = HERE.parent / "train-val-plan-20261017"
PARENT = ROOT / "data/processed/e004/E004-c345-development-20261016"
OUT = ROOT / "data/processed/pilot-b/pilot-b-20261017-v11"
SCRATCH = ROOT / "outputs/_scratch/dataset-release-20261017"
RESTORE = Path("\\\\?\\" + str(SCRATCH / "sources"))
PREFIX = "outputs/_scratch/e004-v9-consolidation-20261013/sources"
CONFIG = ROOT / "configs/datasets/pilot-b-20261017-v11.json"
APPROVAL = HERE / "owner-release-approval.json"
SPLIT = "owner-train-val-20261017"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def main():
    assert not OUT.exists(), "Never overwrite an existing release"
    accepted = read(PLAN / "owner-acceptance.json")
    assert sha256_file(PLAN / "allocation.json") == accepted["allocation"]["sha256"]
    pins = read(PLAN / "input-pins.json")
    assert sha256_file(PARENT / "review-ledger.jsonl") == pins["package_ledger_sha256"]
    for path, digest in pins["accepted_receipts"].items():
        assert sha256_file(ROOT / path) == digest
    verify_payload(PARENT)
    parent_digest = sha256_file(PARENT / "checksums.sha256")
    base = read_records(PARENT / "review-ledger.jsonl")
    allocation = read(PLAN / "allocation.json")
    assignments = {r["sample_id"]: r for r in allocation["assignments"]}
    assert len(assignments) == 1451
    approval = {
        "decision_id": "DATASET-RELEASE-20261017",
        "status": "approved",
        "reviewer": "repository-owner",
        "recorded_at": "2026-10-17",
        "owner_message": (
            "hay tien hanh release dataset version moi di! sau do tien hanh la"
            "m sach codebase, commit,... cac kieu theo dung rule cua project."
        ),
        "authority_note": (
            "Owner explicitly requested release, cleanup and commit after acce"
            "pting exact allocation and quality gates."
        ),
        "allocation_acceptance": pin(PLAN / "owner-acceptance.json"),
        "allocation": pin(PLAN / "allocation.json"),
        "crop_acceptances": [pin(ROOT / p) for p in pins["accepted_receipts"]],
        "parent": pin(PARENT / "checksums.sha256"),
        "new_crop_rights": (
            "Owner confirmed full use rights for the 27 classroom videos; loca"
            "l classifier research only."
        ),
        "scope": (
            "Materialize accepted allocation and existing accepted labels/geom"
            "etry into V11; local backup, cleanup and commit."
        ),
        "training_authorized": False,
        "test_inference_authorized": False,
        "protected_access": (
            "Integrity hashing/decode/copy only; no visual review, features, inference or tuning."
        ),
    }
    write(APPROVAL, approval)
    ref = APPROVAL.relative_to(ROOT).as_posix()
    review = ReviewEvidence("repository-owner", "2026-10-17", ref)
    backup = read(HERE.parent / "E004-v9-consolidation-20261013/backup-receipt.json")
    restored = restore(
        ROOT / backup["archive"], RESTORE, prefixes=(PREFIX,), expected_sha256=backup["sha256"]
    )
    write(
        HERE / "source-restore-receipt.json",
        {
            "archive": backup["archive"],
            "sha256": backup["sha256"],
            "prefix": PREFIX,
            "files": restored,
            "purpose": "Source integrity/export only; no protected visual review/inference",
        },
    )
    roots = {r.source.source_id: RESTORE / PREFIX / r.source.source_id for r in base}
    old345 = {
        r["id"]: r
        for r in read(HERE.parent / "E004-accepted-coverage-20261016/accepted-ledger.json")
    }
    for row in base:
        if row.sample_id in old345:
            roots[row.source.source_id] = (ROOT / old345[row.sample_id]["source"]).parent.parent
    crops = {
        r.sample_id: PARENT / r.crop.crop_relpath
        for r in base
        if r.crop and (PARENT / r.crop.crop_relpath).is_file()
    }
    receipt98 = ROOT / list(pins["accepted_receipts"])[0]
    receipt172 = ROOT / list(pins["accepted_receipts"])[1]
    index = {
        r["candidate_id"]: r
        for r in read(HERE.parent / "frame-crop-audit-20261016/review-index.json")
    }
    inventory = read(HERE.parent / "frame-crop-audit-20261016/inventory.json")
    frames = {r["path"]: r for r in inventory["frames"]}
    archives = {i + 1: a["sha256"] for i, a in enumerate(inventory["archives"])}
    new = []
    provenance = []
    for receipt in (receipt98, receipt172):
        for entry in read(receipt)["records"]:
            cid = entry["candidate_id"]
            geometry = entry if "person_xyxy" in entry else index.get(cid)
            if geometry is None:
                geometry = read(
                    ROOT
                    / "data/interim/frame-crop-owner-review-20261017/candidates"
                    / cid
                    / "proposal.json"
                )
            source = ROOT / entry["source_path"]
            crop = ROOT / entry.get("accepted_crop_path", entry.get("crop_path", ""))
            assert sha256_file(source) == entry["source_sha256"]
            assert sha256_file(crop) == entry["crop_sha256"] == geometry["crop_sha256"]
            frame = frames[entry["source_path"]]
            assert frame["sha256"] == entry["source_sha256"]
            with Image.open(source) as image:
                width, height = image.size
            crop_review = ReviewEvidence(
                "repository-owner",
                "2026-10-17",
                receipt.relative_to(ROOT).as_posix() + "#" + cid,
                entry["crop_sha256"],
            )
            assignment = assignments[cid]
            assert assignment["states"] == entry["review_states"]
            states = [
                TargetReview(
                    {"P": "positive", "N": "negative", "U": "unknown"}[state],
                    entry.get(
                        "resolution_reason", entry.get("reason", "Owner accepted crop review")
                    ),
                    crop_review if state != "U" else None,
                )
                for state in entry["review_states"]
            ]
            sid = f"owner-frames-part{entry['part']:02d}-20261016"
            root = ROOT / "data/interim/frame-crop-audit-20261016/frames"
            roots[sid] = root
            row = PilotRecord(
                sample_id=cid,
                dataset_version=OUT.name,
                selection_version="owner-enrollment-20261017",
                crop_policy_version="owner-reviewed-crops-20261017",
                schema_version=DERIVED_SCHEMA_VERSION,
                source=SourceRef(
                    sid,
                    archives[entry["part"]],
                    source.relative_to(root).as_posix(),
                    entry["source_sha256"],
                    width,
                    height,
                    aliases=(frame["member"],),
                ),
                crop=CropRef(
                    entry["anchor"],
                    PixelBox(*geometry["person_xyxy"]),
                    PixelBox(*geometry["context_xyxy"]),
                    f"crops/{cid}.png",
                    entry["crop_sha256"],
                    crop_review,
                ),
                phone_use=states[0],
                looking_around=states[1],
                work_context_review=ContextReview(
                    "unknown", "No separate confirmed working-context approval"
                ),
                rights=RightsReview(
                    "owner-confirmed-use-rights", ref, ("local_classifier_research",), review
                ),
                group=GroupReview(
                    assignment["proposed_group"],
                    (ref, "artifacts/reports/train-val-plan-20261017/allocation.json"),
                    review,
                    video_id=entry["group"],
                ),
                disposition="approved",
                usage=assignment["proposed_role"],
                split=assignment["proposed_role"],
                split_version=SPLIT,
                owner_decision_ref=ref,
                release_review=crop_review,
                use_scope="local_classifier_research",
            )
            new.append(row)
            crops[cid] = crop
            provenance.append(
                {
                    "sample_id": cid,
                    "source": entry["source_path"],
                    "crop": crop.relative_to(ROOT).as_posix(),
                    "acceptance": pin(receipt),
                    "geometry_sha256": entry["crop_sha256"],
                }
            )
    assert len(new) == 270
    rows = []
    for old in base:
        row = replace(
            old,
            dataset_version=OUT.name,
            selection_version="owner-enrollment-20261017",
            crop_policy_version="owner-reviewed-crops-20261017",
            schema_version=DERIVED_SCHEMA_VERSION,
            split_version=SPLIT if old.split else None,
        )
        if old.sample_id in assignments:
            a = assignments[old.sample_id]
            row = replace(
                row,
                usage=a["proposed_role"],
                split=a["proposed_role"],
                group=replace(
                    old.group,
                    leakage_group_id=a["proposed_group"],
                    evidence_refs=old.group.evidence_refs + (ref,),
                    review=review,
                ),
            )
        rows.append(row)
    rows.extend(new)
    assert Counter(r.usage for r in rows) == {
        "train": 1185,
        "val": 266,
        "test": 11,
        "review_only": 332,
        "excluded": 29,
    }
    assert {r.sample_id for r in rows if r.usage in {"train", "val"}} == set(assignments)
    state_codes = {"positive": "P", "negative": "N", "unknown": "U"}
    for row in rows:
        if row.sample_id in assignments:
            a = assignments[row.sample_id]
            assert [state_codes[row.phone_use.state], state_codes[row.looking_around.state]] == a[
                "states"
            ]
            assert (
                row.crop.crop_sha256 == a["crop_sha256"]
                and row.source.image_sha256 == a["source_sha256"]
            )
            assert (
                row.usage == a["proposed_role"]
                and row.group.leakage_group_id == a["proposed_group"]
            )
    before = {r.sample_id: r for r in base}
    for row in rows:
        if row.sample_id not in before:
            continue
        old = before[row.sample_id]
        fields = [
            "source",
            "crop",
            "phone_use",
            "looking_around",
            "work_context_review",
            "rights",
            "disposition",
        ]
        assert all(getattr(old, f) == getattr(row, f) for f in fields), row.sample_id
        if old.usage not in {"train", "val"}:
            a, b = record_to_dict(old), record_to_dict(row)
            for f in (
                "dataset_version",
                "selection_version",
                "crop_policy_version",
                "schema_version",
                "split_version",
            ):
                a.pop(f)
                b.pop(f)
            assert a == b, row.sample_id
    write(
        CONFIG,
        {
            "status": "owner_authorized_dataset_release",
            "dataset_version": OUT.name,
            "split_version": SPLIT,
            "parent": pin(PARENT / "checksums.sha256"),
            "allocation": pin(PLAN / "allocation.json"),
            "approval": pin(APPROVAL),
            "output": OUT.relative_to(ROOT).as_posix(),
            "expected_ledger_records": 1823,
            "expected_manifest_records": 1462,
            "expected_usage_counts": dict(Counter(r.usage for r in rows)),
            "quality_gates_ref": pin(PLAN / "owner-acceptance.json"),
            "semantics_revision": (
                "Existing accepted labels preserved; new270 reference owner crop a"
                "cceptances and scoped visible-absence semantics."
            ),
            "training_authorized": False,
            "test_inference_authorized": False,
        },
    )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = {
        "status": "accepted",
        "dataset_version": OUT.name,
        "git_commit": commit,
        "workspace_dirty": True,
        "owner_decision_ref": ref,
        "schema_config_review_ref": ref,
        "split_config_review_ref": ref,
        "leakage_review_ref": ref,
        "test_freeze_ref": "release.json#test_freeze",
        "config_ref": CONFIG.relative_to(ROOT).as_posix(),
        "config_sha256": sha256_file(CONFIG),
        "approved_use_scope": ["local_classifier_research"],
        "use_scope": "local_classifier_research",
        "expected_source_counts": dict(Counter(r.source.source_id for r in rows)),
        "source_attribution_refs": [ref],
        "training_run_approved": False,
        "limitations": [
            "Development validation; not independent holdout or model acceptance.",
            (
                "178 prior training samples move to validation: declare model expo"
                "sure in future evaluation."
            ),
            "Conservative grouping does not prove classroom/session independence.",
            (
                "Parent test/reserve preserved; integrity decode/copy only, no vis"
                "ual review/inference."
            ),
        ],
        "test_freeze": test_freeze_attestation(
            rows,
            config_sha256=sha256_file(CONFIG),
            approval_sha256=sha256_file(APPROVAL),
            owner_decision_ref=ref,
            approval=approval,
            commit=commit,
            protocol=(
                "Preserve original test identity/content; package version changes "
                "only; no test inference"
            ),
        ),
    }
    selection = [
        json.loads(line)
        for line in (PARENT / "selection.jsonl").read_text(encoding="utf8").splitlines()
    ]
    for row in new:
        s = row.source
        selection.append(
            {
                "sample_id": row.sample_id,
                "source_id": s.source_id,
                "archive_sha256": s.archive_sha256,
                "source_image_relpath": s.image_relpath,
                "source_image_sha256": s.image_sha256,
                "source_label_relpath": None,
                "source_label_sha256": None,
                "source_label_line_1based": None,
                "source_class_id": None,
            }
        )
    write(HERE / "new-crop-provenance.json", provenance)
    build_pilot_package(rows, OUT, roots, crops, selection, metadata, [r.sample_id for r in rows])
    verify_payload(OUT)
    loaded = verify_dataset(
        OUT,
        SimpleNamespace(
            dataset=OUT.relative_to(ROOT).as_posix(),
            dataset_version=OUT.name,
            split_version=SPLIT,
            encoding_version="pilot-b-targets-v1",
            payload_sha256=sha256_file(OUT / "checksums.sha256"),
        ),
    )
    assert len(loaded) == 1462
    rebuild = SCRATCH / "rebuild"
    build_pilot_package(
        rows,
        rebuild,
        roots,
        crops,
        selection,
        read(OUT / "release.json"),
        [r.sample_id for r in rows],
    )
    verify_payload(rebuild)
    assert (OUT / "checksums.sha256").read_bytes() == (rebuild / "checksums.sha256").read_bytes()
    verify_payload(PARENT)
    assert sha256_file(PARENT / "checksums.sha256") == parent_digest
    write(
        HERE / "package-pointers.json",
        {
            "dataset_version": OUT.name,
            "package": OUT.relative_to(ROOT).as_posix(),
            "payload_sha256": sha256_file(OUT / "checksums.sha256"),
            "split_version": SPLIT,
            "ledger_counts": dict(Counter(r.usage for r in rows)),
            "manifest_records": len(loaded),
        },
    )
    write(
        HERE / "package-validation.json",
        {
            "status": "PASS",
            "schema_and_loader": "PASS",
            "deterministic_rebuild": "PASS",
            "accepted_allocation_exact_records": 1451,
            "new_accepted_crop_bytes_preserved": 270,
            "parent_label_geometry_rights_source_preserved": 1553,
            "protected_records_preserved": 372,
            "test_identity_labels_crop_group_preserved": 11,
            "test_record_serialization_note": (
                "Dataset/selection/crop-policy/split version fields change; origin"
                "al parent bytes untouched."
            ),
            "parent_payload_preserved": "PASS",
            "payload": pin(OUT / "checksums.sha256"),
            "training_or_inference_executed": False,
        },
    )
    print("V11 export, loader, preservation and deterministic rebuild PASS", flush=True)


if __name__ == "__main__":
    main()
