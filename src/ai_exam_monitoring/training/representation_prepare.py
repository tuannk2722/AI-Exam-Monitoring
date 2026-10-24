"""Materialize approved representation campaigns without changing accepted datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import record_to_dict

from .adaptation_config import DatasetSpec, FilePin, config_from_dict, local_path
from .adaptation_model import create_e005_initial_head
from .artifacts import code_identity, digest_json, write_json
from .data import verify_dataset


def pin(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.resolve().relative_to(root.resolve()).as_posix(),
            "sha256": sha256_file(path)}


def read_pin(root: Path, value: dict[str, str]) -> Any:
    return json.loads(FilePin(**value).verify(root).read_text(encoding="utf-8"))


def prepare(design_path: Path, root: Path, phase: str) -> dict[str, Any]:
    root = root.resolve()
    design = json.loads(design_path.read_text(encoding="utf-8"))
    if phase not in {"smoke", "research"}:
        raise DataContractError("Unknown campaign phase")
    authority = read_pin(root, design["authorization"])
    if (authority.get("status") != "approved"
            or authority.get("proposal") != design["proposal"]
            or authority.get("final_test_inference_authorized") is not False
            or authority.get("cloud_upload_authorized") is not True
            or authority.get("research_authorized_after_smoke") is not True):
        raise DataContractError("Approved design/cloud execution scope required")
    proposal_path = FilePin(**design["proposal"]).verify(root)
    proposal = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
    budget = proposal["budgets"][authority["budget_tier"]]
    pointer = read_pin(root, design["dataset_pointer"])
    if (pointer["dataset_version"] != authority["dataset_version"]
            or pointer["payload_sha256"] != authority["payload_sha256"]):
        raise DataContractError("Authorized dataset identity mismatch")
    spec = DatasetSpec(pointer["package"], pointer["dataset_version"], pointer["split_version"],
                       "pilot-b-targets-v1", pointer["payload_sha256"])
    records = verify_dataset(local_path(root, spec.dataset), spec)
    expected = proposal["dataset"]["expected_records"]
    if any(sum(r.usage == role for r in records) != count for role, count in expected.items()):
        raise DataContractError("Approved dataset counts differ")
    allocation = read_pin(root, design["allocation"])
    if (allocation.get("status") != "owner_approved_A"
            or not isinstance(allocation.get("rows"), list)):
        raise DataContractError("Unsupported allocation schema/status")
    assignments = {r["id"]: r for r in allocation["rows"]}
    if len(assignments) != len(records) or set(assignments) != {r.sample_id for r in records}:
        raise DataContractError("Allocation membership differs")
    sources = read_pin(root, design["provenance"])
    provenance = {r["id"]: r for r in sources}
    if len(provenance) != len(records) or set(provenance) != set(assignments):
        raise DataContractError("Provenance membership differs")
    release_approval = read_pin(root, design["release_approval"])
    if (release_approval.get("decision") != "accepted_local_release"
            or release_approval.get("dataset_version") != spec.dataset_version
            or release_approval.get("counts") != expected):
        raise DataContractError("Release approval identity/counts mismatch")
    folder = local_path(root, design["config_dir"]) / phase
    if folder.exists():
        raise DataContractError("Immutable phase exists; use its plan instead of preparing again")
    smoke_pin = None
    if phase == "research":
        smoke_pin = pin(root, local_path(root, design["smoke_receipt"]))
        smoke = read_pin(root, smoke_pin)
        if (smoke.get("status") != "PASS" or smoke.get("code_sha256") != code_identity()["sha256"]
                or smoke.get("payload_sha256") != spec.payload_sha256
                or smoke.get("design_sha256") != sha256_file(design_path)):
            raise DataContractError("Actual current smoke receipt required")
    cohorts, receipts, families = [], {}, {}
    slices: dict[str, dict[str, list[str]]] = {}
    for name, usage in (("train", "train"), ("selection", "val")):
        rows = sorted((r for r in records if r.usage == usage), key=lambda r: r.sample_id)
        cohorts.append({"name": name, "role": name, "sample_ids": [r.sample_id for r in rows],
                        "data": spec.__dict__})
        receipts[name] = {"role": name,
                          "records_sha256": digest_json([record_to_dict(r) for r in rows])}
        slices[name] = {}
        for row in rows:
            assignment = assignments[row.sample_id]
            if (row.group is None or assignment["group_id"] != row.group.leakage_group_id
                    or assignment["split"] != usage):
                raise DataContractError("Allocation role/group changed")
            families[row.sample_id] = {
                "family_id": assignment["group_id"], "owner_accepted": True,
                "independence_verified": False,
                "evidence_refs": [design["allocation"]["path"], design["authorization"]["path"]],
            }
            source = provenance[row.sample_id]
            origin = (source.get("upstream_v12_source") or {}).get("source_id", "unresolved_new")
            keys = ["upstream:" + origin]
            if source.get("owner_provenance_confirmation"):
                keys.append("owner_confirmed_generated")
            if row.crop is None:
                raise DataContractError("Missing crop geometry")
            pb, cb = row.crop.person_box, row.crop.context_box
            fraction = ((pb.xmax-pb.xmin)*(pb.ymax-pb.ymin)
                        / ((cb.xmax-cb.xmin)*(cb.ymax-cb.ymin)))
            keys.append("small_anchor_fraction" if fraction < .7 else "large_anchor_fraction")
            size = max(row.source.image_width, row.source.image_height)
            keys.append("native_long_edge_gt224" if size > 224 else "native_long_edge_le224")
            for key in keys:
                slices[name].setdefault(key, []).append(row.sample_id)
    folder.mkdir(parents=True)
    protocol_path = folder / "protocol.json"
    write_json(protocol_path, {
        "schema_version": "representation-protocol-v4", "status": "frozen",
        "owner": authority["owner"], "decision_ref": design["authorization"]["path"],
        "target_order": proposal["targets"], "cohorts": receipts, "family_assignments": families,
        "reserved_holdout": {"status": "not_applicable_zero_test", "sample_ids": [],
                             "source_sha256": [], "family_ids": []},
        "independence_claim": False, "final_test_inference_authorized": False,
        "slice_enrollment": slices, "provenance_pin": design["provenance"],
    })
    readiness_path = folder / "readiness.json"
    write_json(readiness_path, {
        "schema_version": "representation-readiness-v4", "status": "approved",
        "owner": authority["owner"], "scope": phase, "independence_claim": False,
        "protocol_sha256": sha256_file(protocol_path), "cohorts_sha256": digest_json(cohorts),
        "execution_authorization": design["authorization"], "smoke_receipt": smoke_pin,
        "evidence_pins": [design[k] for k in ("authorization", "proposal", "dataset_pointer",
                                             "allocation", "provenance", "release_approval")],
    })
    template_path = FilePin(**design["template"]).verify(root)
    template = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    approvals: dict[str, Any] = {
        "status": "approved", "owner": authority["owner"], "scope": "local_classifier_research",
        "run_kind": phase, "code_sha256": code_identity()["sha256"],
        "owner_authorization": design["authorization"], "final_test_inference_authorized": False,
        "configs": {}, "config_signatures": {},
    }
    common = proposal["common"]
    arms = proposal["arms"]

    def resolved_arm(name: str) -> dict[str, Any]:
        arm = dict(arms[name])
        parent = arm.pop("same_as", None)
        return {**(resolved_arm(parent) if parent else {}), **arm}

    items = (design["smoke_runs"] if phase == "smoke" else [
        {"arm": arm, "seed": seed}
        for seed in [proposal["screening"]["seed"], *budget["confirmation_seeds"]]
        for arm in budget["screening_arms"]
    ])
    plan_items = []
    for item in items:
        arm_name, seed = item["arm"], item["seed"]
        arm = resolved_arm(arm_name)
        ident = item.get("id", f"E007-V13-{arm_name}-S{seed}")
        encoder = arm["encoder"]
        weights = design["pretrained"][encoder]
        for field in ("weights", "license"):
            FilePin(**weights[field]).verify(root)
        head_path = local_path(root, design["initialization_dir"]) / f"head-{encoder}-{seed}.pt"
        if not head_path.exists():
            create_e005_initial_head(head_path, seed, in_dim=arm["feature_dim"],
                                     hidden_dim=common["head"]["hidden_dim"],
                                     dropout=common["head"]["dropout"])
        raw = {**template, "schema_version": "representation-adaptation-v4",
               "experiment_id": ident, "owner": authority["owner"], "run_kind": phase,
               "hypothesis": f"V13 {arm_name}: approved representation study; seed {seed}",
               "cohorts": cohorts, "protocol": pin(root, protocol_path),
               "readiness": pin(root, readiness_path),
               "execution_authorization": design["authorization"],
               "approval_ref": (folder / "approval.json").relative_to(root).as_posix(),
               "weights": weights["weights"], "weights_license": weights["license"],
               "encoder_source": weights.get("source"), "head_initialization": pin(root, head_path),
               "weights_id": "IMAGENET1K_V1" if encoder == "resnet18" else "DINOv2_VITS14",
               "model": "resnet18_single_crop_v3" if encoder == "resnet18" else "dinov2_vits14_v4",
               "device": "cuda", "precision": "float32", "seed": seed,
               "image_size": arm["image_size"], "batch_size": common["batch_size"],
               "head_learning_rate": common["head_learning_rate"],
               "layer4_learning_rate": arm["backbone_learning_rate"],
               "max_epochs": item.get("epochs", common["max_epochs"]),
               "warmup_epochs": common["warmup_head_only_epochs"],
               "pos_weight": common["loss"]["pos_weight"],
               "trainable_scope": ("head_and_last_two_blocks" if encoder == "dinov2_vits14"
                                   and arm_name == "D1" else arm["trainable_scope"]),
               "augmentation": {**common["augmentation"],
                                "random_erasing_prob": arm["random_erasing_prob"]},
               "wall_time_seconds": (budget["smoke_minutes"]*60 if phase == "smoke"
                                     else budget["run_including_reload_minutes"]*60)}
        config = config_from_dict(raw)
        path = folder / f"{ident}.yaml"
        path.write_text(yaml.safe_dump(config.to_dict(), sort_keys=False), encoding="utf-8")
        approvals["configs"][ident] = digest_json(config.to_dict())
        approvals["config_signatures"][ident] = config.match_signature()
        plan_items.append({"id": ident, "arm": arm_name, "seed": seed, "config": pin(root, path)})
    write_json(folder / "approval.json", approvals)
    plan = {"phase": phase, "design": pin(root, design_path), "items": plan_items,
            "code_sha256": code_identity()["sha256"], "budget": budget}
    write_json(folder / "plan.json", plan)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--phase", choices=["smoke", "research"], required=True)
    args = parser.parse_args()
    prepare(args.design, args.workspace, args.phase)


if __name__ == "__main__":
    main()
