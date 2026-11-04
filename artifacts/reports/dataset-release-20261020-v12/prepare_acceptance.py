"""Pin the final owner review and prepare V12 membership without assigning new splits."""

import json
import re
from collections import Counter
from pathlib import Path

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent / "crop-review-consolidation-20261019"
PARENT = ROOT / "data/processed/pilot-b/pilot-b-20261017-v11"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(name, value):
    (HERE / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    snapshot = HERE / "owner-final-review.md"
    source = AUDIT / "README.md"
    if snapshot.exists():
        assert snapshot.read_bytes() == source.read_bytes(), "Owner review changed"
    else:
        snapshot.write_bytes(source.read_bytes())
    final = {r["id"]: dict(r) for r in read(AUDIT / "final-draft-cohort.json")}
    original = {r["id"]: r for r in read(AUDIT / "resolved-ledger.json")}
    delta = {r["id"]: r for r in read(AUDIT / "delta-review.json")}
    text = snapshot.read_text(encoding="utf-8")
    review = text.split("## Kết quả review của owner\n", 1)[1]
    decisions = []
    excluded = []
    for line in review.splitlines():
        if not line.startswith("|"):
            continue
        cells = [s.strip() for s in line.strip("|").split("|")]
        if cells[0] == "ID" or cells[0].startswith("---"):
            continue
        cid, decision = cells
        if cid == "V6R2-EX-010-R06, V6-EX-027":
            assert "V6-EX-027 N/P" in decision and "V6R2-EX-010-R06" in decision
            del final["V6R2-EX-010-R06"]
            excluded.append("V6R2-EX-010-R06")
            row = original["V6-EX-027"]
            final[row["id"]] = {
                "id": row["id"],
                "parent": row["id"],
                "path": row["crop_path"],
                "source": row["source_path"],
                "box": list(row["context_box"].values()),
                "states": ["N", "P"],
                "kind": "existing",
                "acceptance": "owner_approved_exception",
            }
        else:
            assert cid in final and cid in delta, cid
            if decision == "exclude":
                del final[cid]
                excluded.append(cid)
            else:
                assert re.fullmatch("[PNU]/[PNU]", decision), decision
                final[cid]["states"] = decision.split("/")
                final[cid]["acceptance"] = "owner_approved_exception"
        decisions.append({"id": cid, "decision": decision})
    assert len(decisions) == 15
    # Owner clarified the prior near-duplicate conflict in this release turn.
    del final["V6-EX-022"]
    excluded.append("V6-EX-022")
    decisions.append(
        {
            "id": "V6-EX-022 / V6-EX-027",
            "decision": "Owner chat: Chỉ giữ V6-EX-027",
        }
    )
    base = {r.sample_id: r for r in read_records(PARENT / "review-ledger.jsonl")}
    legacy_ids = {r["id"] for r in original.values() if r["audit"] == "legacy836"}
    assert len(legacy_ids) == 836 and legacy_ids <= base.keys()
    assert all(base[cid].usage in {"train", "val"} for cid in legacy_ids)
    for row in final.values():
        row["acceptance"] = "owner_approved"
        row["review_ref"] = "artifacts/reports/dataset-release-20261020-v12/owner-final-review.md"
        row["crop_sha256"] = sha256_file(ROOT / row["path"])
        row["source_sha256"] = sha256_file(ROOT / row["source"])
        assert row["states"] != ["U", "U"]
        if row["parent"] in base:
            parent = base[row["parent"]]
            row["inherited_role"] = parent.usage
            row["inherited_group"] = parent.group.leakage_group_id
        else:
            row["inherited_role"] = None
            row["inherited_group"] = None
    write("accepted-audit-cohort.json", list(final.values()))
    write(
        "owner-crop-acceptance.json",
        {
            "status": "accepted_crop_labels_geometry_and_membership",
            "authority": (
                "Owner chat: reviewed; unmentioned crops approved; finalize and release V12."
            ),
            "snapshot_sha256": sha256_file(snapshot),
            "exceptions": decisions,
            "excluded_proposals": excluded,
            "accepted_audit_crops": len(final),
            "new_split_assignment_approved": False,
            "training_authorized": False,
            "test_inference_authorized": False,
        },
    )
    preserved = [r for r in base.values() if r.sample_id not in legacy_ids]
    stats = {
        "parent_records": len(base),
        "audited_legacy": len(legacy_ids),
        "accepted_audit_crops": len(final),
        "audit_inherited_roles": dict(
            Counter(r["inherited_role"] or "unassigned" for r in final.values())
        ),
        "preserved_outside_audit": dict(Counter(r.usage for r in preserved)),
        "new_source_groups": dict(
            Counter(
                re.search(r"Y\d\d", r["id"]).group()
                for r in final.values()
                if r["inherited_role"] is None
            )
        ),
        "source_G17_parent": [
            {"id": r.sample_id, "role": r.usage, "group": r.group.leakage_group_id}
            for r in base.values()
            if "G17" in r.sample_id
        ],
    }
    write("preflight-summary.json", stats)
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
