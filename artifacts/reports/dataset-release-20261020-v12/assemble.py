"""V12 release worksheet using the canonical codec, exporter and integrity checks."""

import json
import subprocess
from collections import Counter
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import test_freeze_attestation, verify_payload
from ai_exam_monitoring.data.pilot_package import build_pilot_package
from ai_exam_monitoring.data.pilot_schema import (
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
    validate_records,
)
from ai_exam_monitoring.training.data import verify_dataset

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / "crop-review-consolidation-20261019"
PARENT = ROOT / "data/processed/pilot-b/pilot-b-20261017-v11"
OUT = ROOT / "data/processed/pilot-b/pilot-b-20261020-v12"
CONFIG = ROOT / "configs/datasets/pilot-b-20261020-v12.json"
SPLIT = "owner-train-val-20261020-v12"
REF = "artifacts/reports/dataset-release-20261020-v12/owner-release-approval.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path.exists():
        assert path.read_text(encoding="utf-8") == payload, path
    else:
        path.write_text(payload, encoding="utf-8")


def pin(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path)}


def main():
    assert not OUT.exists(), "Never overwrite an accepted package"
    approval = read(ROOT / REF)
    assert approval["status"] == "approved"
    for p in approval["inputs"]:
        assert sha256_file(ROOT / p["path"]) == p["sha256"], p
    verify_payload(PARENT)
    parent_digest = sha256_file(PARENT / "checksums.sha256")
    base = read_records(PARENT / "review-ledger.jsonl")
    by_id = {r.sample_id: r for r in base}
    accepted = read(HERE / "accepted-audit-cohort.json")
    accepted_ids = {r["id"] for r in accepted}
    originals = read(AUDIT / "resolved-ledger.json")
    legacy_ids = {r["id"] for r in originals if r["audit"] == "legacy836"}
    allocations = {r["id"]: r for r in read(HERE / "allocation-proposal.json")["assignments"]}
    geometries = {r["candidate_id"]: r for r in read(AUDIT / "geometry-review.json")}
    yt = {
        r["candidate_id"]: r
        for r in read(HERE.parent / "youtube-frame-audit-20261018/review-index.json")
    }
    inventory = read(HERE.parent / "youtube-frame-audit-20261018/inventory.json")
    frames = {r["sha256"]: r for r in inventory["frames"]}
    roots = read(HERE / "source-roots.json")
    review = ReviewEvidence("repository-owner", "2026-10-20", REF)
    common = {
        "dataset_version": OUT.name,
        "selection_version": "owner-audit-closure-20261020",
        "crop_policy_version": "owner-reviewed-crops-20261020",
    }
    rows = []
    crops = {}
    for old in base:
        if old.sample_id in legacy_ids and old.sample_id in accepted_ids:
            continue
        row = replace(old, **common, split_version=SPLIT if old.split else None)
        if old.sample_id in legacy_ids:
            row = replace(
                row,
                disposition="excluded",
                usage="excluded",
                split=None,
                split_version=None,
                exclusion_reason="Owner accepted audit exclusion or replacement; see V12 closure.",
                owner_decision_ref=REF,
                release_review=review,
                ineligibility_reasons=(),
            )
        if row.crop and (PARENT / row.crop.crop_relpath).exists():
            crops[row.sample_id] = PARENT / row.crop.crop_relpath
        rows.append(row)
    provenance = []
    states = {"P": "positive", "N": "negative", "U": "unknown"}
    for entry in accepted:
        cid = entry["id"]
        assert sha256_file(ROOT / entry["path"]) == entry["crop_sha256"]
        assert sha256_file(ROOT / entry["source"]) == entry["source_sha256"]
        evidence = ReviewEvidence(
            "repository-owner", "2026-10-20", REF + "#" + cid, entry["crop_sha256"]
        )
        targets = [
            TargetReview(
                states[state],
                "Owner final audit decision; see accepted-audit-cohort.",
                evidence if state != "U" else None,
            )
            for state in entry["states"]
        ]
        parent = by_id.get(entry["parent"])
        geometry = geometries.get(cid) or yt.get(cid)
        if parent:
            source, rights = parent.source, parent.rights
            if cid == parent.sample_id:
                crop = replace(parent.crop, review=evidence)
                context = parent.work_context_review
            else:
                assert geometry is not None
                crop = CropRef(
                    cid,
                    PixelBox(*geometry["person_xyxy"]),
                    PixelBox(*geometry["context_xyxy"]),
                    f"crops/{cid}.png",
                    entry["crop_sha256"],
                    evidence,
                )
                context = ContextReview(
                    "unknown", "No separate working-context approval for recrop"
                )
        else:
            assert geometry is not None
            frame = frames[entry["source_sha256"]]
            rel = (
                Path(frame["source_path"])
                .relative_to("data/interim/youtube-frame-audit-20261018/frames")
                .as_posix()
            )
            with Image.open(ROOT / entry["source"]) as image:
                width, height = image.size
            source = SourceRef(
                "youtube-crawl-20261018",
                inventory["archive"]["sha256"],
                rel,
                entry["source_sha256"],
                width,
                height,
                aliases=(frame["member"],),
            )
            rights = RightsReview(
                "owner-confirmed-use-rights", REF, ("local_classifier_research",), review
            )
            crop = CropRef(
                cid,
                PixelBox(*geometry["person_xyxy"]),
                PixelBox(*geometry["context_xyxy"]),
                f"crops/{cid}.png",
                entry["crop_sha256"],
                evidence,
            )
            context = ContextReview("unknown", "No separate working-context approval")
        assignment = allocations[cid]
        if parent:
            group = parent.group
            assert group.leakage_group_id == assignment["group"]
        else:
            group = GroupReview(
                assignment["group"],
                (REF, "artifacts/reports/dataset-release-20261020-v12/lineage-review.json"),
                review,
                video_id=frames[entry["source_sha256"]]["group"],
            )
        row = PilotRecord(
            sample_id=cid,
            **common,
            schema_version="pilot-b-manifest-v2",
            source=source,
            crop=crop,
            phone_use=targets[0],
            looking_around=targets[1],
            work_context_review=context,
            rights=rights,
            group=group,
            disposition="approved",
            usage=assignment["role"],
            split=assignment["role"],
            split_version=SPLIT,
            owner_decision_ref=REF,
            release_review=evidence,
            use_scope="local_classifier_research",
        )
        rows.append(row)
        crops[cid] = ROOT / entry["path"]
        provenance.append(
            {
                "id": cid,
                "parent": entry["parent"],
                "crop": pin(crops[cid]),
                "source": pin(ROOT / entry["source"]),
                "states": entry["states"],
            }
        )
    validate_records(rows)
    assert Counter(r.usage for r in rows) == {
        "train": 1092,
        "val": 204,
        "test": 11,
        "review_only": 332,
        "excluded": 418,
    }
    assert len(rows) == 2057
    assert {r.sample_id for r in rows if r.usage in {"train", "val"}} == set(allocations)
    for row in rows:
        if row.sample_id not in legacy_ids and row.sample_id in by_id:
            a, b = record_to_dict(by_id[row.sample_id]), record_to_dict(row)
            for name in (*common, "split_version"):
                a.pop(name)
                b.pop(name)
            assert a == b, row.sample_id
    selection = []
    for row in rows:
        s = row.source
        selection.append(
            {
                "sample_id": row.sample_id,
                "source_id": s.source_id,
                "archive_sha256": s.archive_sha256,
                "source_image_relpath": s.image_relpath,
                "source_image_sha256": s.image_sha256,
                "source_label_relpath": s.label_relpath,
                "source_label_sha256": s.label_sha256,
                "source_label_line_1based": s.label_line_1based,
                "source_class_id": s.source_class_id,
            }
        )
    write(
        CONFIG,
        {
            "status": "owner_authorized_dataset_release",
            "dataset_version": OUT.name,
            "split_version": SPLIT,
            "parent": pin(PARENT / "checksums.sha256"),
            "allocation": pin(HERE / "allocation-proposal.json"),
            "approval": pin(ROOT / REF),
            "output": OUT.relative_to(ROOT).as_posix(),
            "expected_ledger_records": len(rows),
            "expected_manifest_records": 1307,
            "expected_usage_counts": dict(Counter(r.usage for r in rows)),
            "quality_gates_ref": pin(HERE.parent / "train-val-plan-20261017/owner-acceptance.json"),
            "semantics_revision": (
                "Owner-reviewed phone/looking audit; scoped visible-absence semantics retained."
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
        "owner_decision_ref": REF,
        "schema_config_review_ref": REF,
        "split_config_review_ref": REF,
        "leakage_review_ref": REF,
        "test_freeze_ref": "release.json#test_freeze",
        "config_ref": CONFIG.relative_to(ROOT).as_posix(),
        "config_sha256": sha256_file(CONFIG),
        "approved_use_scope": ["local_classifier_research"],
        "use_scope": "local_classifier_research",
        "expected_source_counts": dict(Counter(r.source.source_id for r in rows)),
        "source_attribution_refs": [REF],
        "training_run_approved": False,
        "limitations": [
            "Development validation, not independent holdout; prior V11 model exposure remains.",
            (
                "V12 labels/membership differ from V11; do not compare metrics as "
                "identical ground truth."
            ),
            "Conservative video/scene grouping does not prove person/session independence.",
            "Test content/evidence unchanged; integrity copy only, no visual review/inference.",
        ],
    }
    metadata["test_freeze"] = test_freeze_attestation(
        rows,
        config_sha256=sha256_file(CONFIG),
        approval_sha256=sha256_file(ROOT / REF),
        owner_decision_ref=REF,
        approval=approval,
        commit=commit,
        protocol=(
            "Preserve V11 test identity/content/evidence; only version fields "
            "change; no inference"
        ),
    )
    write(HERE / "crop-provenance.json", provenance)
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
    assert len(loaded) == 1307
    rebuild = ROOT / "outputs/_scratch/dataset-release-20261020-v12/rebuild"
    assert not rebuild.exists()
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
            "codec_exporter_loader": "PASS",
            "deterministic_rebuild": "PASS",
            "parent_payload_preserved": parent_digest,
            "outside_audit_preserved_records": 987,
            "test_content_evidence_preserved": 11,
            "test_visual_or_inference_access": False,
            "records": len(rows),
            "manifest": len(loaded),
            "config": pin(CONFIG),
        },
    )
    print("V12 PASS:", len(rows), "ledger,", len(loaded), "manifest")


if __name__ == "__main__":
    main()
