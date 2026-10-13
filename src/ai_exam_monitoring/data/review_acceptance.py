"""Import exact owner label/geometry decisions without granting dataset usage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .pilot_schema import (
    TARGET_ORDER,
    PilotRecord,
    ReviewEvidence,
    TargetReview,
    TargetState,
    validate_records,
)


def _keys(value: Any, expected: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise DataContractError(f"Invalid {name} fields")
    return value


def _local(workspace: Path, relative: str) -> Path:
    path = (workspace / relative).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise DataContractError("Review media must stay inside workspace")
    return path


def accept_reviews(
    records: Sequence[PilotRecord],
    decisions: Mapping[str, Any],
    *,
    ledger_sha256: str,
    evidence_ref: str,
    workspace: Path,
) -> list[PilotRecord]:
    """Validate the complete batch and return a new, still review-only ledger.

    The caller verifies the ledger and decision file hashes before decoding.
    A decision binds the source, exact crop, displayed input and original ledger
    (including geometry). No rights/group/context/release approval is inferred.
    """
    validate_records(records)
    _keys(
        decisions,
        {"schema_version", "scope", "target_order", "ledger_sha256", "reviewer",
         "reviewed_at", "decisions"},
        "review receipt",
    )
    if (
        decisions["schema_version"] != "crop-review-acceptance-v1"
        or decisions["scope"] != "labels_and_geometry_only"
        or decisions["target_order"] != list(TARGET_ORDER)
        or decisions["ledger_sha256"] != ledger_sha256
    ):
        raise DataContractError("Review scope/order/ledger pin mismatch")
    entries = decisions["decisions"]
    if not isinstance(entries, list) or not entries or not records:
        raise DataContractError("Require a nonempty, explicit batch of owner decisions")
    by_id: dict[str, dict[str, Any]] = {}
    for raw in entries:
        row = _keys(
            raw,
            {"sample_id", "states", "reason", "geometry_accepted", "source_sha256",
             "crop_sha256", "input_relpath", "input_sha256"},
            "crop decision",
        )
        ident = row["sample_id"]
        if not isinstance(ident, str) or ident in by_id:
            raise DataContractError("Duplicate or invalid decision ID")
        if (
            row["geometry_accepted"] is not True
            or not isinstance(row["states"], list)
            or len(row["states"]) != 2
            or any(s not in ("P", "N", "U") for s in row["states"])
            or not isinstance(row["reason"], str)
            or not row["reason"].strip()
        ):
            raise DataContractError("Require explicit geometry and two reviewed states/reason")
        by_id[ident] = row
    if set(by_id) != {r.sample_id for r in records}:
        raise DataContractError("Owner decisions must match exact ledger membership")

    states: dict[str, TargetState] = {"P": "positive", "N": "negative", "U": "unknown"}
    result = []
    for record in records:
        if (
            record.usage != "review_only" or record.disposition != "pending"
            or record.crop is None or record.crop.review is not None
            or record.target_mask != (0, 0)
        ):
            raise DataContractError("Import requires pending, unsupervised review-only records")
        row = by_id[record.sample_id]
        if (
            row["source_sha256"] != record.source.image_sha256
            or row["crop_sha256"] != record.crop.crop_sha256
        ):
            raise DataContractError("Owner decision refers to another source/crop version")
        for path, digest in (
            (record.source.image_relpath, record.source.image_sha256),
            (record.crop.crop_relpath, record.crop.crop_sha256),
            (row["input_relpath"], row["input_sha256"]),
        ):
            if not isinstance(path, str) or not isinstance(digest, str):
                raise DataContractError("Invalid review media pin")
            if sha256_file(_local(workspace, path)) != digest:
                raise DataContractError("Review source/crop/input bytes changed")
        review = ReviewEvidence(
            decisions["reviewer"], decisions["reviewed_at"],
            f"{evidence_ref}#{record.sample_id}", record.crop.crop_sha256,
        )
        targets = [TargetReview(states[s], row["reason"], review) for s in row["states"]]
        result.append(replace(
            record,
            phone_use=targets[0], looking_around=targets[1],
            crop=replace(record.crop, review=review),
            disposition="approved", owner_decision_ref=review.evidence_ref,
        ))
    validate_records(result)
    return result
