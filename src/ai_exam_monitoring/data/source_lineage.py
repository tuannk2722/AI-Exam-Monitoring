"""Conservative source links for quarantine; components never prove independence."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError


def lineage_components(
    inventory: Sequence[dict[str, Any]], assessments: Sequence[dict[str, Any]],
    parent_non_test: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Link identical bytes, same-export filename lineage hints and reviewed scenes.

    Filename lineage is only a conservative quarantine edge. Neither an unlinked
    component nor a visual scene name is promoted to an independent group.
    """
    keys = [(r["source_id"], r["member_sha256"]) for r in inventory]
    if len(set(keys)) != len(keys):
        raise DataContractError("Duplicate source/member inventory key")
    indices = {key: i for i, key in enumerate(keys)}
    roots = list(range(len(inventory)))

    def find(i: int) -> int:
        while roots[i] != i:
            roots[i] = roots[roots[i]]
            i = roots[i]
        return i

    def join(a: int, b: int) -> None:
        roots[find(b)] = find(a)

    first: dict[tuple[str, ...], int] = {}
    edge_types: dict[int, set[str]] = defaultdict(set)
    for i, row in enumerate(inventory):
        for key in (
            ("exact_source_bytes", row["source_sha256"]),
            ("same_export_lineage_hint", row["archive_sha256"], row["lineage_hint_sha256"]),
        ):
            if key in first:
                join(first[key], i)
                edge_types[i].add(key[0])
            else:
                first[key] = i
    reviews: dict[int, dict[str, Any]] = {}
    scene_first: dict[str, int] = {}
    for assessment in assessments:
        key = (assessment["source_id"], assessment["member_sha256"])
        if key not in indices:
            raise DataContractError("Assessment missing from inventory")
        i = indices[key]
        if i in reviews or inventory[i]["source_sha256"] != assessment["source_sha256"]:
            raise DataContractError("Duplicate assessment or source pin mismatch")
        reviews[i] = assessment
        scene = assessment["draft_scene_boundary"]
        if scene in scene_first:
            join(scene_first[scene], i)
            edge_types[i].add("reviewed_shared_scene")
        else:
            scene_first[scene] = i

    parent = {row["source_sha256"]: row for row in parent_non_test}
    if any("test" in row["usages"] for row in parent_non_test):
        raise DataContractError("This source triage only accepts non-test parent fingerprints")
    grouped: dict[int, list[int]] = defaultdict(list)
    for i in range(len(inventory)):
        grouped[find(i)].append(i)
    result = []
    for members in grouped.values():
        reviewed = [reviews[i] for i in members if i in reviews]
        if not reviewed:
            continue
        exact_parent = [parent[inventory[i]["source_sha256"]] for i in members
                        if inventory[i]["source_sha256"] in parent]
        roles = sorted({r["draft_role"] for r in reviewed})
        result.append({
            "review_ids": sorted(r["review_id"] for r in reviewed),
            "scene_boundaries": sorted({r["draft_scene_boundary"] for r in reviewed}),
            "member_keys": sorted([list(keys[i]) for i in members]),
            "source_sha256": sorted({inventory[i]["source_sha256"] for i in members}),
            "edge_types": sorted({e for i in members for e in edge_types[i]}),
            "reserve_role_proposals": roles,
            "reserve_role_conflict": len(roles) > 1,
            "confirmed_train_scene_overlap": any(
                r["confirmed_parent_scene_overlap"] for r in reviewed
            ),
            "exact_non_test_parent_samples": sorted({
                sample for row in exact_parent for sample in row["sample_ids"]
            }),
            "quarantine": True, "independence_proven": False,
            "video_id": None, "session_id": None, "room_id": None,
        })
    return sorted(result, key=lambda r: r["review_ids"])
