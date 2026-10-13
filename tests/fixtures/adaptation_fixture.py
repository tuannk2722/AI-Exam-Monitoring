"""Synthetic-only packages and random weights; never used by production code."""

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import torch
import yaml
from PIL import Image
from test_pilot_schema import evidence, usable_record
from torchvision.models import resnet18

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import TargetReview, record_to_dict, write_records
from ai_exam_monitoring.training.adaptation_config import (
    AdaptationConfig,
    CohortSpec,
    DatasetSpec,
    FilePin,
)
from ai_exam_monitoring.training.adaptation_model import create_initial_head
from ai_exam_monitoring.training.artifacts import digest_json, write_json


def pin(root, path):
    return FilePin(path.relative_to(root).as_posix(), sha256_file(path))


def fixture(root: Path, *, epochs=2, model="resnet18_layer4"):
    root.mkdir(parents=True, exist_ok=True)
    package = root / "data/fixture"
    (package / "crops").mkdir(parents=True)
    rows = []
    for i in range(10):
        split = "train" if i < 6 else "val"
        ident = f"SYNTHETIC-{i:02d}"
        row = usable_record(
            ident, image_sha=hashlib.sha256(ident.encode()).hexdigest(), split=split
        )
        image = Image.fromarray(
            np.random.default_rng(i).integers(0, 256, (80, 70, 3), dtype=np.uint8)
        )
        path = package / row.crop.crop_relpath
        image.save(path)
        review = evidence(sha256_file(path))
        row = replace(
            row,
            dataset_version="synthetic-v1",
            split_version="synthetic-split-v1",
            crop=replace(row.crop, crop_sha256=sha256_file(path), review=review),
            phone_use=TargetReview("positive" if i % 2 else "negative", "synthetic", review),
            looking_around=TargetReview("positive" if i % 3 else "negative", "synthetic", review),
            group=replace(row.group, leakage_group_id=f"synthetic-group-{i}"),
            use_scope="local_classifier_research",
            rights=replace(row.rights, approved_use_scope=("local_classifier_research",)),
        )
        rows.append(row)
    for name in ("manifest.jsonl", "review-ledger.jsonl"):
        write_records(package / name, rows)
    assignments = [
        {
            "sample_id": r.sample_id,
            "split": r.split,
            "split_version": r.split_version,
            "leakage_group_id": r.group.leakage_group_id,
            "test_freeze_ref": r.test_freeze_ref,
        }
        for r in rows
    ]
    (package / "split-assignment.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in assignments), encoding="utf8"
    )
    write_json(
        package / "release.json",
        {
            "status": "accepted",
            "test_freeze": {
                "status": "frozen",
                "manifest_sha256": sha256_file(package / "manifest.jsonl"),
                "split_assignment_sha256": sha256_file(package / "split-assignment.jsonl"),
                "test_manifest_sha256": hashlib.sha256(b"").hexdigest(),
                "test_sample_ids": [],
            },
        },
    )
    files = sorted(p for p in package.rglob("*") if p.is_file())
    (package / "checksums.sha256").write_text(
        "".join(sha256_file(p) + "  " + p.relative_to(package).as_posix() + "\n" for p in files),
        encoding="utf8",
    )
    data = DatasetSpec(
        "data/fixture",
        "synthetic-v1",
        "synthetic-split-v1",
        "pilot-b-targets-v1",
        sha256_file(package / "checksums.sha256"),
    )
    cohorts = (
        CohortSpec("train", "train", data, tuple(r.sample_id for r in rows[:6])),
        CohortSpec("development", "selection", data, tuple(r.sample_id for r in rows[6:])),
        CohortSpec("diagnostic", "diagnostic", data, tuple(r.sample_id for r in rows[6:8])),
    )
    protocol = {
        "schema_version": "matched-protocol-v1",
        "status": "frozen",
        "owner": "synthetic-owner",
        "decision_ref": "synthetic-fixture-only",
        "target_order": ["phone_use", "looking_around"],
        "cohorts": {
            c.name: {
                "role": c.role,
                "records_sha256": digest_json(
                    [record_to_dict(r) for r in rows if r.sample_id in c.sample_ids]
                ),
            }
            for c in cohorts
        },
        "family_assignments": {
            r.sample_id: {
                "family_id": r.group.leakage_group_id,
                "owner_accepted": True,
                "independence_verified": True,
                "evidence_refs": ["synthetic-fixture-only"],
            }
            for r in rows
        },
        "reserved_holdout": {"source_sha256": [], "family_ids": []},
        "slice_enrollment": {},
    }
    write_json(root / "protocol.json", protocol)
    write_json(root / "license.json", {"scope": "synthetic-fixture-only", "random_weights": True})
    write_json(
        root / "readiness.json",
        {
            "schema_version": "adaptation-readiness-v1",
            "status": "approved",
            "owner": "synthetic-owner",
            "scope": "smoke",
            "protocol_sha256": sha256_file(root / "protocol.json"),
            "cohorts_sha256": digest_json(json.loads(json.dumps([asdict(c) for c in cohorts]))),
            "decision_ref": "synthetic-fixture-only",
            "gates": {"G0": True},
            "evidence_pins": [asdict(pin(root, root / "license.json"))],
        },
    )
    with torch.random.fork_rng():
        torch.manual_seed(7)
        torch.save(resnet18(weights=None).state_dict(), root / "synthetic-weights.pt")
    create_initial_head(root / "head.pt", 42)
    config = AdaptationConfig(
        schema_version="matched-adaptation-v1",
        experiment_id="SYNTHETIC-adaptation",
        owner="synthetic-owner",
        hypothesis="Synthetic software fixture only",
        approval_ref="approval.json",
        run_kind="smoke",
        model=model,
        cohorts=cohorts,
        protocol=pin(root, root / "protocol.json"),
        readiness=pin(root, root / "readiness.json"),
        weights=pin(root, root / "synthetic-weights.pt"),
        weights_license=pin(root, root / "license.json"),
        head_initialization=pin(root, root / "head.pt"),
        weights_id="IMAGENET1K_V1",
        device="cpu",
        seed=42,
        image_size=32,
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
        fill=[124, 116, 104],
        transform="rgb_letterbox_bilinear_v1",
        target_order=["phone_use", "looking_around"],
        batch_size=4,
        threads=1,
        workers=0,
        optimizer="AdamW",
        head_learning_rate=0.001,
        layer4_learning_rate=0.0001,
        weight_decay=0.0001,
        max_epochs=epochs,
        patience=10,
        min_delta=0.0001,
        threshold=0.5,
        wall_time_seconds=300,
        objective="global_known_normalized_minibatch_bce_v1",
        bn_policy="all_eval_affine_follows_model_policy",
        sampling="uniform_permutation_no_drop_v1",
        checkpoint_policy="atomic_epoch_boundary_v1",
    )
    approve(root, config)
    return config, rows


def approve(root, config):
    write_json(
        root / config.approval_ref,
        {
            "status": "approved",
            "owner": config.owner,
            "scope": "local_classifier_research",
            "run_kind": config.run_kind,
            "matched_signature": config.match_signature(),
            "configs": {config.experiment_id: digest_json(config.to_dict())},
        },
    )
    (root / "config.yaml").write_text(yaml.safe_dump(config.to_dict()), encoding="utf8")
