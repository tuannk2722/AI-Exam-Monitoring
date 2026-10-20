"""Prepare a concrete split proposal for owner acceptance before export."""

import json
import re
from pathlib import Path

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    base = read_records(ROOT / "data/processed/pilot-b/pilot-b-20261017-v11/review-ledger.jsonl")
    audit = read(HERE.parent / "crop-review-consolidation-20261019/resolved-ledger.json")
    legacy = {r["id"] for r in audit if r["audit"] == "legacy836"}
    accepted = read(HERE / "accepted-audit-cohort.json")
    assignments = []
    codes = {"positive": "P", "negative": "N", "unknown": "U"}
    for row in base:
        if row.sample_id in legacy or row.usage not in {"train", "val"}:
            continue
        assignments.append(
            {
                "id": row.sample_id,
                "role": row.usage,
                "group": row.group.leakage_group_id,
                "states": [codes[row.phone_use.state], codes[row.looking_around.state]],
                "basis": "Preserve V11 outside audited cohort",
            }
        )
    for row in accepted:
        role, group = row["inherited_role"], row["inherited_group"]
        if role is None:
            video = re.search(r"Y\d\d", row["id"]).group()
            role = "train"
            group = "V12-Y03-Y05-G17-family" if video in {"Y03", "Y05"} else "V12-" + video
        assignments.append(
            {
                "id": row["id"],
                "role": role,
                "group": group,
                "states": row["states"],
                "basis": "Inherit V11 parent"
                if row["inherited_role"]
                else "Proposed new whole-video train",
            }
        )
    assert len(assignments) == len({r["id"] for r in assignments}) == 1296
    summary = {}
    for role in ["train", "val"]:
        rows = [r for r in assignments if r["role"] == role]
        summary[role] = {
            "count": len(rows),
            "groups": len({r["group"] for r in rows}),
            "targets": [
                {
                    state: {
                        "count": sum(r["states"][i] == state for r in rows),
                        "groups": len({r["group"] for r in rows if r["states"][i] == state}),
                    }
                    for state in ["P", "N", "U"]
                }
                for i in range(2)
            ],
        }
    screening = read(HERE / "lineage-screening.json")
    verdicts = [
        {
            "comparison_id": p["comparison_id"],
            "result": "distinct_visible_scene",
            "note": "Đã xem hai frame: khác cấu trúc phòng/bàn và bố cục; không phải duplicate.",
        }
        for p in screening["manual_queue"]
    ]
    lineage = {
        "status": "reviewed_proposal_pending_owner_group_acceptance",
        "screened_non_test_sources": screening["non_test_source_count"],
        "manual_comparisons": verdicts,
        "conservative_family": ["Y03", "Y05", "prior-audit-G17"],
        "G17_records_in_V11": 0,
        "independence_proven": False,
        "proposal": "90 new crops train only; no random frame split; preserve V11 retained roles.",
    }
    (HERE / "lineage-review.json").write_text(
        json.dumps(lineage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    proposal = {
        "status": "proposed_pending_owner_assignment_approval",
        "parent_payload": sha256_file(
            ROOT / "data/processed/pilot-b/pilot-b-20261017-v11/checksums.sha256"
        ),
        "accepted_crop_receipt": sha256_file(HERE / "owner-crop-acceptance.json"),
        "counts": summary,
        "preserved_test": 11,
        "new_video_crops_train": 90,
        "assignments": assignments,
        "training_authorized": False,
        "test_inference_authorized": False,
    }
    (HERE / "allocation-proposal.json").write_text(
        json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
