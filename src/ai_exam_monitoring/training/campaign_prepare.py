"""Materialize exact configs from an explicitly authorized local campaign design."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records, record_to_dict

from .adaptation_config import config_from_dict
from .adaptation_model import create_e005_initial_head
from .artifacts import code_identity, digest_json, write_json
from .campaign import read_json


def pin(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.resolve().relative_to(root).as_posix(), "sha256": sha256_file(path)}


def prepare(design_path: Path, root: Path) -> None:
    root = root.resolve()
    design = read_json(design_path)
    folder = root / design["config_dir"]
    if any((folder / name).exists() for name in ("campaign.json", "protocol.json")):
        raise ValueError("Campaign preparation exists; use a new revision, never overwrite pins")
    authority = root / design["owner_authorization"]
    auth = read_json(authority)
    if auth["status"] != "approved" or auth["final_test_inference_authorized"] is not False:
        raise ValueError("Approved closed-test owner scope required")
    auth_pin = pin(root, authority)
    pointers = read_json(root / design["dataset_pointer"])
    package = root / pointers["package"]
    if sha256_file(package / "checksums.sha256") != pointers["payload_sha256"]:
        raise ValueError("Dataset pointer changed")
    records = read_records(package / "manifest.jsonl")
    allocation = read_json(root / design["allocation"])
    assignments = {r["id"]: r for r in allocation["assignments"]}
    cohorts = []
    receipts = {}
    families = {}
    selected = []
    for name, usage in (("train", "train"), ("selection", "val")):
        rows = sorted((r for r in records if r.usage == usage), key=lambda r: r.sample_id)
        selected.extend(rows)
        cohorts.append({
            "name": name, "role": name, "sample_ids": [r.sample_id for r in rows],
            "data": {
                "dataset": pointers["package"], "dataset_version": pointers["dataset_version"],
                "split_version": pointers["split_version"],
                "encoding_version": rows[0].target_encoding_version,
                "payload_sha256": pointers["payload_sha256"],
            },
        })
        receipts[name] = {"role": name, "records_sha256": digest_json(
            [record_to_dict(r) for r in rows])}
        for row in rows:
            assignment = assignments[row.sample_id]
            if (assignment["role"] != usage or row.group is None
                    or assignment["group"] != row.group.leakage_group_id):
                raise ValueError("Allocation/manifest group or role mismatch")
            families[row.sample_id] = {
                "family_id": assignment["group"], "owner_accepted": True,
                "independence_verified": False,
                "evidence_refs": [design["release_approval"], design["owner_authorization"]],
            }
    old_protocol = read_json(root / design["parent_protocol"])
    reserved = copy.deepcopy(old_protocol["reserved_holdout"])
    # Preserve holdout reservation; only compare IDs, never open test crop bytes.
    if set(reserved["sample_ids"]) != {r.sample_id for r in records if r.usage == "test"}:
        raise ValueError("Holdout reservation IDs changed")
    val = [r for r in selected if r.usage == "val"]
    slices: dict[str, list[str]] = {}
    for r in val:
        slices.setdefault(f"source:{r.source.source_id}", []).append(r.sample_id)
        name = "owner_frames" if r.source.source_id.startswith("owner-frames") else "audited_legacy"
        slices.setdefault(name, []).append(r.sample_id)
    protocol_path = folder / "protocol.json"
    write_json(protocol_path, {
        "schema_version": "matched-protocol-v2", "status": "frozen",
        "owner": auth["owner"], "decision_ref": design["owner_authorization"],
        "waiver_approval": auth_pin, "independence_claim": False,
        "final_test_inference_authorized": False, "M4_status": "INCONCLUSIVE",
        "target_order": ["phone_use", "looking_around"], "cohorts": receipts,
        "family_assignments": families, "reserved_holdout": reserved,
        "slice_enrollment": {"selection": slices}, "quality_gates_pin": auth_pin,
    })
    evidence = [pin(root, root / design[key]) for key in (
        "owner_authorization", "dataset_pointer", "release_approval", "allocation")]
    smoke_id = design["smoke"]["id"]
    smoke_result = {
        "status": "PASS", "run": smoke_id, "reload_parity": "PASS",
        "checkpoint_resume": "PASS", "stage_transition": "PASS",
    }
    smoke_bytes = (json.dumps(smoke_result, ensure_ascii=False, indent=2,
                              allow_nan=False) + "\n").encode()
    smoke_path = root / design["smoke_result"]
    if smoke_path.exists():
        if read_json(smoke_path) != smoke_result:
            raise ValueError("Observed smoke receipt does not match required checks")
        smoke_pin = pin(root, smoke_path)
    else:
        # Match write_json's platform text newline translation before first execution.
        import os

        smoke_pin = {"path": design["smoke_result"], "sha256": hashlib.sha256(
            smoke_bytes.replace(b"\n", os.linesep.encode())).hexdigest()}
    for kind in ("smoke", "research"):
        write_json(folder / f"{kind}-readiness.json", {
            "schema_version": "adaptation-readiness-v2", "status": "approved",
            "owner": auth["owner"], "scope": kind,
            "protocol_sha256": sha256_file(protocol_path),
            "cohorts_sha256": digest_json(cohorts),
            "decision_ref": design["owner_authorization"], "waiver_approval": auth_pin,
            "gates": {"G0": True, "G1": True, "G2": "owner_waived", "G3": "owner_waived"},
            "evidence_pins": evidence + ([smoke_pin] if kind == "research" else []),
            "condition": "Research blocked until actual smoke PASS receipt exists.",
        })
    approvals: dict[str, dict[str, Any]] = {}
    for kind in ("smoke", "research"):
        approvals[kind] = {
            "status": "approved", "owner": auth["owner"], "scope": "local_classifier_research",
            "run_kind": kind, "configs": {}, "config_signatures": {},
            "code_sha256": code_identity()["sha256"], "owner_authorization": auth_pin,
            "final_test_inference_authorized": False,
        }
    items = [design["smoke"]] + design["screening"] + design["confirmation"]
    head_pins: dict[tuple[int, int], dict[str, str]] = {}
    resolved = []
    for item in items:
        kind = "smoke" if item["recipe"] == "SMOKE" else "research"
        raw = yaml.safe_load((root / item["template"]).read_text(encoding="utf-8"))
        raw.update(design["common"])
        raw.update(item["overrides"])
        raw.update({
            "experiment_id": item["id"], "hypothesis": item["hypothesis"],
            "seed": item["seed"], "run_kind": kind, "cohorts": cohorts,
            "approval_ref": (folder / f"{kind}-approval.json").relative_to(root).as_posix(),
            "protocol": pin(root, protocol_path),
            "readiness": pin(root, folder / f"{kind}-readiness.json"),
        })
        key = (raw["seed"], raw["head_hidden_dim"])
        if key not in head_pins:
            path = root / design["initialization_dir"] / f"head-{key[0]}-{key[1]}.pt"
            create_e005_initial_head(path, key[0], in_dim=512, hidden_dim=key[1],
                                     dropout=raw["head_dropout"])
            head_pins[key] = pin(root, path)
        raw["head_initialization"] = head_pins[key]
        config = config_from_dict(raw)
        path = folder / f"{item['id']}.yaml"
        path.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True), encoding="utf-8")
        approvals[kind]["configs"][item["id"]] = digest_json(config.to_dict())
        approvals[kind]["config_signatures"][item["id"]] = config.match_signature()
        resolved.append({"id": item["id"], "recipe": item["recipe"], "seed": item["seed"],
                         "config": pin(root, path)})
    for kind, approval in approvals.items():
        write_json(folder / f"{kind}-approval.json", approval)
    by_id = {r["id"]: r for r in resolved}
    write_json(folder / "campaign.json", {
        "title": design.get("title", "Kết quả training tự động"),
        "code_sha256": code_identity()["sha256"], "report_dir": design["report_dir"],
        "smoke_result": design["smoke_result"], "smoke": by_id[smoke_id],
        "screening": [by_id[r["id"]] for r in design["screening"]],
        "confirmation": [by_id[r["id"]] for r in design["confirmation"]],
        "repeat_recipes": design["repeat_recipes"],
        "verified_smoke": (
            pin(root, root / design["verified_smoke"]) if design.get("verified_smoke") else None
        ),
        "evidence_pins": evidence + [pin(root, design_path), pin(root, protocol_path)] + [
            pin(root, folder / f"{k}-approval.json") for k in ("smoke", "research")],
    })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    prepare(args.design, args.workspace)


if __name__ == "__main__":
    main()
