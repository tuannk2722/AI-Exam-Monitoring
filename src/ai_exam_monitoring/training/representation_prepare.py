"""Materialize approved representation campaigns without changing accepted datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import (
    MULTILABEL_ENCODING_VERSION,
    MULTILABEL_TARGET_ORDER,
    TARGET_ENCODING_VERSION,
    TARGET_ORDER,
    record_to_dict,
)

from .adaptation_config import DatasetSpec, FilePin, config_from_dict, local_path
from .adaptation_model import create_e005_initial_head
from .artifacts import code_identity, digest_json, write_json
from .data import verify_dataset


def pin(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.resolve().relative_to(root.resolve()).as_posix(),
            "sha256": sha256_file(path)}


def read_pin(root: Path, value: dict[str, str]) -> Any:
    return json.loads(FilePin(**value).verify(root).read_text(encoding="utf-8"))


def is_multiseed(design: dict[str, Any]) -> bool:
    return bool(design.get("config_schema") == "dinov2-adaptation-v6")


def campaign_budget(
    design: dict[str, Any], proposal: dict[str, Any], profile: str | None = None
) -> dict[str, Any]:
    if not is_multiseed(design):
        raise DataContractError("Hardware-selected profile budgets require V6")
    if profile not in {"full", "core"}:
        raise DataContractError("V6 requires an explicit hardware-selected profile")
    selected, budget = proposal["profiles"][profile], proposal["budget"]
    return {**budget, "screening_arms": selected["screening_arms"],
            "smoke_arms": selected["smoke_arms"],
            "screening_seeds": proposal["screening"]["seeds"],
            "confirmation_seeds": proposal["confirmation"]["additional_seeds"],
            "max_research_runs": selected["max_research_runs"],
            "smoke_minutes": budget["actual_gpu_smoke_minutes"],
            "run_including_reload_minutes": budget[
                "per_research_run_including_reload_and_sync_minutes"]}


def smoke_receipt_path(design: dict[str, Any], root: Path, profile: str | None = None) -> Path:
    if is_multiseed(design) and profile not in {"full", "core"}:
        raise DataContractError("Missing V6 profile")
    return local_path(root, design["smoke_receipt"].replace("{profile}", profile or ""))


def prepare(
    design_path: Path, root: Path, phase: str, *, profile: str | None = None
) -> dict[str, Any]:
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
    if tuple(proposal["targets"]) not in (TARGET_ORDER, MULTILABEL_TARGET_ORDER):
        raise DataContractError("Unsupported proposal target contract")
    if proposal["targets"] == list(MULTILABEL_TARGET_ORDER):
        from .calibration import validate_objectives

        validate_objectives(proposal.get("calibration_objectives"), proposal["targets"])
    multi = is_multiseed(design)
    budget = (campaign_budget(design, proposal, profile) if multi
              else proposal["budgets"][authority["budget_tier"]])
    for value in design.get("supporting_inputs", []):
        FilePin(**value).verify(root)
    pointer = read_pin(root, design["dataset_pointer"])
    if (pointer["dataset_version"] != authority["dataset_version"]
            or pointer["payload_sha256"] != authority["payload_sha256"]):
        raise DataContractError("Authorized dataset identity mismatch")
    spec = DatasetSpec(pointer["package"], pointer["dataset_version"], pointer["split_version"],
                       MULTILABEL_ENCODING_VERSION
                       if proposal["targets"] == list(MULTILABEL_TARGET_ORDER)
                       else TARGET_ENCODING_VERSION, pointer["payload_sha256"])
    records = verify_dataset(local_path(root, spec.dataset), spec)
    expected = proposal["dataset"]["expected_records"]
    if any(sum(r.usage == role for r in records) != count for role, count in expected.items()):
        raise DataContractError("Approved dataset counts differ")
    allocation = read_pin(root, design["allocation"])
    if (allocation.get("status") not in {"owner_approved_A", "owner_delegated_allocation"}
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
    folder = local_path(root, design["config_dir"])
    if multi:
        folder /= str(profile)
    folder /= phase
    if folder.exists():
        raise DataContractError("Immutable phase exists; use its plan instead of preparing again")
    smoke_pin = None
    if phase == "research":
        smoke_pin = pin(root, smoke_receipt_path(design, root, profile))
        smoke = read_pin(root, smoke_pin)
        if (smoke.get("status") != "PASS" or smoke.get("code_sha256") != code_identity()["sha256"]
                or smoke.get("payload_sha256") != spec.payload_sha256
                or smoke.get("design_sha256") != sha256_file(design_path)
                or (multi and smoke.get("profile") != profile)):
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
            if multi:
                size = max(cb.xmax-cb.xmin, cb.ymax-cb.ymin)
                boundary = source.get("source_boundary", row.source.source_id)
                keys.extend(["boundary:" + boundary,
                             "cohort_origin:" + source["cohort_origin"]])
                edge_bin = ("le224" if size <= 224 else "225to336" if size <= 336
                            else "337to448" if size <= 448 else "gt448")
                keys.append("native_edge:" + edge_bin)
                if source.get("train_only_generated_or_imported"):
                    keys.append("train_only_generated_or_imported")
                if all(v is not None for v in row.target_values):
                    keys.append("joint:" + "".join("P" if v else "N" for v in row.target_values))
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
        **({"calibration_objectives": proposal["calibration_objectives"]}
           if proposal["targets"] == list(MULTILABEL_TARGET_ORDER) else {}),
        **({"group_bootstrap": proposal["group_bootstrap"]}
           if "group_bootstrap" in proposal else {}),
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

    screening_seeds = (budget["screening_seeds"] if multi else [proposal["screening"]["seed"]])
    smoke_items = ([{"arm": arm, "seed": screening_seeds[0],
                     "id": f"{design['run_prefix']}-SMOKE-{arm}-{mode}",
                     "epochs": proposal["smoke"]["epochs_per_run"]}
                    for arm in budget["smoke_arms"] for mode in ("FULL", "RESUME")]
                   if multi else design["smoke_runs"])
    items = (smoke_items if phase == "smoke" else [
        {"arm": arm, "seed": seed}
        for seed in [*screening_seeds, *budget["confirmation_seeds"]]
        for arm in budget["screening_arms"]
    ])
    plan_items = []
    for item in items:
        arm_name, seed = item["arm"], item["seed"]
        arm = resolved_arm(arm_name)
        prefix = design.get("run_prefix", "E007-V13")
        ident = item.get("id", f"{prefix}-{arm_name}-S{seed}")
        encoder = arm["encoder"]
        weights = design["pretrained"][encoder]
        for field in ("weights", "license"):
            FilePin(**weights[field]).verify(root)
        head_key = (f"{encoder}-{arm['feature_dim']}" if "pooling" in arm else encoder)
        head_path = local_path(root, design["initialization_dir"]) / f"head-{head_key}-{seed}.pt"
        if not head_path.exists():
            create_e005_initial_head(head_path, seed, in_dim=arm["feature_dim"],
                                     hidden_dim=common["head"]["hidden_dim"],
                                     dropout=common["head"]["dropout"],
                                     target_order=tuple(proposal["targets"]))
        raw = {**template, "schema_version": design.get(
                   "config_schema", "representation-adaptation-v4"),
               "experiment_id": ident, "owner": authority["owner"], "run_kind": phase,
               "hypothesis": f"{spec.dataset_version} {arm_name}: study; seed {seed}",
               "cohorts": cohorts, "protocol": pin(root, protocol_path),
               "target_order": proposal["targets"],
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
               "weight_decay": common.get("weight_decay", template["weight_decay"]),
               "patience": common.get("patience", template["patience"]),
               "min_delta": common.get("min_delta", template["min_delta"]),
               "head_hidden_dim": common["head"]["hidden_dim"],
               "head_dropout": common["head"]["dropout"],
               "label_smoothing": common["loss"].get(
                   "label_smoothing", template["label_smoothing"]),
               "max_epochs": item.get("epochs", common["max_epochs"]),
               "warmup_epochs": common["warmup_head_only_epochs"],
               "pos_weight": common["loss"]["pos_weight"],
               "trainable_scope": ("head_and_last_blocks" if multi else
                                   "head_and_last_two_blocks" if encoder == "dinov2_vits14"
                                   and arm_name == "D1" else arm["trainable_scope"]),
               "augmentation": {**common["augmentation"],
                                "random_erasing_prob": arm.get("random_erasing_prob",
                                                              common["augmentation"].get(
                                                                  "random_erasing_prob", 0.0))},
               "wall_time_seconds": (budget["smoke_minutes"]*60 if phase == "smoke"
                                     else budget["run_including_reload_minutes"]*60)}
        if "pooling" in arm:
            raw["pooling"] = arm["pooling"]
            raw["anchor_padding_ratio"] = 0.0
        if multi:
            raw.update(model=encoder+"_v6", encoder_variant=encoder,
                       train_last_blocks=arm["train_last_blocks"],
                       train_final_norm=arm["train_final_norm"], pooling=common["pooling"],
                       anchor_padding_ratio=0.0,
                       weights_id="DINOv2_VITB14" if encoder == "dinov2_vitb14"
                       else "DINOv2_VITS14")
            for key in ("device", "precision", "threads", "workers", "optimizer",
                        "lr_scheduler", "min_lr_ratio"):
                if key in common:
                    raw[key] = common[key]
            if "transform" in common:
                raw.update(transform=common["transform"]["name"],
                           **{key: common["transform"][key] for key in ("mean", "std", "fill")})
            raw["objective"] = common["loss"].get("objective", raw["objective"])
            raw["selection_metric"] = "val_macro_ap"
            raw["threshold"] = proposal.get("analysis", {}).get("fixed_threshold_report", .5)
        config = config_from_dict(raw)
        path = folder / f"{ident}.yaml"
        path.write_text(yaml.safe_dump(config.to_dict(), sort_keys=False), encoding="utf-8")
        approvals["configs"][ident] = digest_json(config.to_dict())
        approvals["config_signatures"][ident] = config.match_signature()
        plan_items.append({"id": ident, "arm": arm_name, "seed": seed, "config": pin(root, path)})
    write_json(folder / "approval.json", approvals)
    plan = {"phase": phase, "design": pin(root, design_path), "items": plan_items,
            "code_sha256": code_identity()["sha256"], "budget": budget}
    if multi:
        plan["profile"] = profile
    write_json(folder / "plan.json", plan)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--phase", choices=["smoke", "research"], required=True)
    parser.add_argument("--profile", choices=["full", "core"])
    args = parser.parse_args()
    prepare(args.design, args.workspace, args.phase, profile=args.profile)


if __name__ == "__main__":
    main()
