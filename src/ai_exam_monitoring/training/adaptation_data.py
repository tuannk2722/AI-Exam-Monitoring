"""Exact cohort and whole-family enrollment for approved adaptation experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import PilotRecord, record_to_dict

from .adaptation_config import AdaptationConfig, FilePin, local_path
from .artifacts import digest_json
from .data import crop_path, image_tensor, labels, verify_dataset


@dataclass
class ImageCohort:
    name: str
    role: str
    records: list[PilotRecord]
    paths: list[Path]
    values: torch.Tensor
    mask: torch.Tensor
    groups: list[str]

    @property
    def ids(self) -> list[str]:
        return [r.sample_id for r in self.records]

    def batch(self, indices: list[int], config: AdaptationConfig) -> torch.Tensor:
        return torch.stack([image_tensor(self.paths[i], config) for i in indices])


def _waiver(config: AdaptationConfig, workspace: Path, ready: dict[str, Any]) -> None:
    """V2 is an explicit owner-authorized research revision, never fake independence."""
    protocol = config.protocol.read_json(workspace)
    if protocol.get("schema_version") != "matched-protocol-v2":
        raise DataContractError("Waiver readiness requires protocol v2")
    value = ready.get("waiver_approval")
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise DataContractError("Require exact waiver approval pin")
    approval = FilePin(**value).read_json(workspace)
    if (
        protocol.get("waiver_approval") != value
        or approval.get("status") != "approved"
        or approval.get("owner") != config.owner
        or approval.get("waive_independence") is not True
        or approval.get("waive_support_shortfalls") is not True
        or approval.get("final_test_inference_authorized") is not False
        or protocol.get("independence_claim") is not False
        or protocol.get("final_test_inference_authorized") is not False
        or protocol.get("M4_status") != "INCONCLUSIVE"
    ):
        raise DataContractError("Waiver scope/owner/policy mismatch")


def validate_readiness(config: AdaptationConfig, workspace: Path) -> dict[str, Any]:
    ready = config.readiness.read_json(workspace)
    if (
        ready.get("schema_version") not in {"adaptation-readiness-v1", "adaptation-readiness-v2"}
        or ready.get("status") != "approved"
        or ready.get("owner") != config.owner
        or ready.get("scope") != config.run_kind
        or ready.get("protocol_sha256") != config.protocol.sha256
        or ready.get("cohorts_sha256") != digest_json(config.to_dict()["cohorts"])
        or not ready.get("decision_ref")
    ):
        raise DataContractError("Readiness does not bind exact data/protocol/action")
    revised = ready["schema_version"] == "adaptation-readiness-v2"
    if revised:
        _waiver(config, workspace, ready)
    gates = ready.get("gates", {})
    required: tuple[str, ...] = (
        ("G0", "G1", "G2", "G3") if config.run_kind == "promotion" else ("G0",)
    )
    if revised and config.run_kind == "promotion":
        required = ("G0", "G1")
        if any(gates.get(gate) != "owner_waived" for gate in ("G2", "G3")):
            raise DataContractError("Waived gates must not claim verified PASS")
    if any(gates.get(gate) is not True for gate in required):
        raise DataContractError("Required readiness gate is not approved")
    evidence = ready.get("evidence_pins")
    if not isinstance(evidence, list) or not evidence:
        raise DataContractError("Readiness requires source/acceptance evidence pins")
    for pin in evidence:
        FilePin(**pin).verify(workspace)
    if config.run_kind == "promotion" and not revised:
        support = ready.get("holdout_support", {})
        requirements = {"independent_groups": 10, "verified_contexts": 2}
        for target in config.target_order:
            for key, minimum in (
                ("positive", 100),
                ("negative", 100),
                ("positive_groups", 5),
                ("negative_groups", 5),
            ):
                value = support.get(target, {}).get(key)
                if type(value) is not int or value < minimum:
                    raise DataContractError("G3 target/group support insufficient")
        for key, minimum in requirements.items():
            if type(support.get(key)) is not int or support[key] < minimum:
                raise DataContractError("G3 independent groups/contexts insufficient")
    return ready


def prepare_cohorts(
    config: AdaptationConfig, workspace: Path
) -> tuple[list[ImageCohort], dict[str, Any]]:
    ready = validate_readiness(config, workspace)
    revised = ready["schema_version"] == "adaptation-readiness-v2"
    protocol = config.protocol.read_json(workspace)
    if (
        protocol.get("schema_version")
        != ("matched-protocol-v2" if revised else "matched-protocol-v1")
        or protocol.get("status") != "frozen"
        or protocol.get("owner") != config.owner
        or protocol.get("target_order") != config.target_order
        or not protocol.get("decision_ref")
        or set(protocol.get("cohorts", {})) != {c.name for c in config.cohorts}
    ):
        raise DataContractError("Unfrozen or mismatched cohort protocol")
    cache: dict[str, list[PilotRecord]] = {}
    cohorts = []
    families = protocol.get("family_assignments", {})
    reserved = protocol.get("reserved_holdout", {})
    if not isinstance(reserved.get("source_sha256"), list) or not isinstance(
        reserved.get("family_ids"), list
    ):
        raise DataContractError("Protocol must explicitly reserve holdout identities")
    for spec in config.cohorts:
        root = local_path(workspace, spec.data.dataset)
        key = digest_json(spec.data.__dict__)
        if key not in cache:
            cache[key] = verify_dataset(root, spec.data)
        all_rows = {r.sample_id: r for r in cache[key]}
        if not set(spec.sample_ids) <= set(all_rows):
            raise DataContractError("Cohort member missing from accepted manifest")
        rows = [all_rows[s] for s in spec.sample_ids]
        expected_usage = "train" if spec.role == "train" else "val"
        if any(r.usage != expected_usage or not any(r.target_mask) for r in rows):
            raise DataContractError("Wrong split/review-only/test/all-unknown cohort member")
        receipt = protocol["cohorts"][spec.name]
        if receipt.get("role") != spec.role or receipt.get("records_sha256") != digest_json(
            [record_to_dict(r) for r in rows]
        ):
            raise DataContractError("Cohort record/label/geometry/order pin changed")
        groups = []
        for row in rows:
            group = families.get(row.sample_id, {})
            if (
                not isinstance(group.get("family_id"), str)
                or not group["family_id"]
                or not group.get("evidence_refs")
                or group.get("owner_accepted") is not True
            ):
                raise DataContractError("Whole-family membership lacks owner evidence")
            if (spec.role == "selection" and not revised
                    and group.get("independence_verified") is not True):
                raise DataContractError("New-development independence not verified")
            if (
                row.source.image_sha256 in reserved["source_sha256"]
                or group["family_id"] in reserved["family_ids"]
            ):
                raise DataContractError("Holdout identity enrolled in training/development")
            groups.append(group["family_id"])
        values, mask = labels(rows)
        cohorts.append(
            ImageCohort(
                spec.name, spec.role, rows, [crop_path(root, r) for r in rows], values, mask, groups
            )
        )
    train = next(c for c in cohorts if c.role == "train")
    for other in cohorts:
        if other is train:
            continue
        for a, b in (
            (set(train.ids), set(other.ids)),
            (set(train.groups), set(other.groups)),
            (
                {r.source.image_sha256 for r in train.records},
                {r.source.image_sha256 for r in other.records},
            ),
            (
                {r.crop.crop_sha256 for r in train.records if r.crop},
                {r.crop.crop_sha256 for r in other.records if r.crop},
            ),
        ):
            if a & b:
                raise DataContractError("Train/development ID/source/crop/family leakage")
    return cohorts, protocol
