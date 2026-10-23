"""Reconcile sparse owner exports for audit; never mutate a release or infer labels."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from PIL import Image

from ai_exam_monitoring.data.pilot_schema import PilotRecord


def merge_review(
    records: list[PilotRecord], inventory: dict[str, Any], review: dict[str, Any]
) -> list[dict[str, Any]]:
    """Blank/missing fields inherit; explicit U remains U, independent of done."""
    rows = inventory["records"]
    expected = {r.sample_id: r for r in records if r.disposition == "approved"}
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(expected):
        raise ValueError("Inventory does not match approved ledger")
    pins = {r["id"]: r["sha256"] for r in rows}
    for sample_id, record in expected.items():
        if record.crop is None or record.crop.crop_sha256 != pins[sample_id]:
            raise ValueError(f"Inventory SHA mismatch: {sample_id}")
    cohort = hashlib.sha256(json.dumps(
        [(r["id"], r["sha256"]) for r in rows], separators=(",", ":")
    ).encode()).hexdigest()
    if (inventory["cohort"] != cohort or review.get("cohort") != cohort
            or review.get("schema") != "crop-review-draft-v1"):
        raise ValueError("Review cohort/schema mismatch")
    exported = review.get("inventory")
    if exported is not None and (
        len(exported) != len(pins)
        or {r["id"]: r["sha256"] for r in exported} != pins
    ):
        raise ValueError("Exported inventory mismatch")
    decisions = review.get("decisions")
    if not isinstance(decisions, dict) or set(decisions) - set(pins):
        raise ValueError("Unknown review IDs")
    output = []
    labels = {1: "P", 0: "N", None: "U"}
    for row in rows:
        sample_id = row["id"]
        decision = decisions.get(sample_id, {})
        if decision and decision.get("sha256") != pins[sample_id]:
            raise ValueError(f"Review SHA mismatch: {sample_id}")
        if any(decision.get(k, "") not in ("", "P", "N", "U")
               for k in ("phone", "looking")):
            raise ValueError(f"Invalid label: {sample_id}")
        action = decision.get("action", "")
        if action not in ("", "keep", "remove", "recrop", "unsure"):
            raise ValueError(f"Invalid action: {sample_id}")
        for key in ("note", "angle", "tags"):
            if not isinstance(decision.get(key, ""), str):
                raise ValueError(f"Invalid text: {sample_id}")
        old = [labels[v] for v in expected[sample_id].target_values]
        new = [decision.get(k) or old[i] for i, k in enumerate(("phone", "looking"))]
        output.append({
            **row, "old_pnu": old, "effective_pnu": new,
            "label_origin": ["owner_delta" if decision.get(k) else "v12_inherited"
                             for k in ("phone", "looking")],
            "effective_action": action or "keep", "owner_delta": decision,
            "needs_geometry_review": action == "recrop" or bool(decision.get("note")),
            "audit_status": "pending_visual_review",
        })
    return output


def rgb_digest(image: Image.Image) -> str:
    """Include dimensions to avoid differently shaped rasters sharing a pixel hash."""
    rgb = image.convert("RGB")
    return hashlib.sha256(
        f"{rgb.width}x{rgb.height}:RGB:".encode() + rgb.tobytes()
    ).hexdigest()


def apply_review_only_policy(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Withdraw old review-only rows without substantive owner input.

    Label/action/note input reopens review, never grants training eligibility.
    An explicit state identical to the old state still counts as owner input.
    UI timestamps, empty objects, angle, tags and done are not enrollment requests.
    """
    result = []
    for row in rows:
        decision = row["owner_delta"]
        substantive = any(decision.get(k) for k in ("phone", "looking", "action", "note"))
        withdraw = row["old_usage"] == "review_only" and not substantive
        result.append({**row,
                       "effective_action": "remove" if withdraw else row["effective_action"],
                       "membership_reason": "owner_withdraw_unmodified_review_only" if withdraw
                       else "owner_delta_or_previously_used",
                       "needs_geometry_review": False if withdraw
                       else row["needs_geometry_review"]})
    return result
