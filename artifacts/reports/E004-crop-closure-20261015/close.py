"""Materialize owner batch closure without altering upstream sealed artifacts."""

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "E004-device-consistency-20261015"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    assert not (HERE / "closure-receipt.json").exists(), "Closure already sealed"
    for name in ("result-pins.json", "handoff-pins.json"):
        pins = json.loads((OLD / name).read_text(encoding="utf-8"))
        for path, digest in pins["files"].items():
            assert sha(ROOT / path) == digest, path
    snapshot = HERE / "owner-review-input.md"
    snapshot.write_bytes((OLD / "owner-review.md").read_bytes())
    rows = json.loads((OLD / "candidate-ledger.json").read_text(encoding="utf-8"))
    findings = json.loads((HERE / "exception-findings.json").read_text(encoding="utf-8"))
    exceptions = {r["candidate_id"]: r for r in findings["rows"]}
    changes = []
    for row in rows:
        ident = row["candidate_id"]
        before = row["draft_labels"]
        finding = exceptions.get(ident)
        labels = finding["recommended_labels"] if finding else before
        excluded = labels == "U/U" or (finding and finding["recommendation"].startswith("exclude"))
        row["final_labels"] = labels
        row["previous_draft_labels"] = before
        row["closure_disposition"] = "excluded" if excluded else "retained"
        row["status"] = "excluded_from_batch" if excluded else "finalized_labels_and_existing_crop"
        row["closure_authority"] = (
            "owner_requested_exception_resolution"
            if finding
            else "owner_batch_approval_unmentioned"
        )
        row["closure_reason"] = (
            finding["reason"]
            if finding
            else "Owner approve các crop không được đề cập; giữ nhãn và crop đã review."
        )
        row["assigned_split"] = None
        row["training_ready"] = False
        if before != labels:
            changes.append(
                {"id": ident, "before": before, "after": labels, "reason": row["closure_reason"]}
            )
        for field in ("source", "crop", "input"):
            assert sha(ROOT / row[field]) == row[field + "_sha256"], (ident, field)
    kept = [r for r in rows if r["closure_disposition"] == "retained"]
    assert len(rows) == 247 and len(kept) == 240 and len(changes) == 3
    write("candidate-ledger.json", rows)
    write("label-deltas.json", changes)
    receipt = {
        "schema": "research-crop-batch-closure-v1",
        "date": "2026-10-16",
        "scope": "Nhãn và crop hiện có của batch 247; không phải canonical release hoặc training acceptance.",
        "owner_direction": "Các crop không đề cập đều approve; kiểm kỹ và giải quyết ngoại lệ, bỏ U/U; có thể loại hai crop G5 nếu QA không phù hợp.",
        "exception_authority": "Kết luận audit theo yêu cầu owner; không giả là owner trực tiếp ghi nhãn mới cho từng ngoại lệ.",
        "retained": len(kept),
        "excluded": len(rows) - len(kept),
        "label_counts_retained": dict(Counter(r["final_labels"] for r in kept)),
        "excluded_ids": [r["candidate_id"] for r in rows if r["closure_disposition"] == "excluded"],
        "changed_labels": changes,
        "remaining_release_gates": [
            "person geometry không được suy từ context box",
            "lineage/group membership",
            "split và training config approval",
        ],
        "training_ready": False,
        "files": {
            p.relative_to(ROOT).as_posix(): sha(p)
            for p in [
                snapshot,
                HERE / "exception-findings.json",
                HERE / "candidate-ledger.json",
                HERE / "label-deltas.json",
                OLD / "candidate-ledger.json",
                OLD / "result-pins.json",
                OLD / "handoff-pins.json",
            ]
        },
    }
    write("closure-receipt.json", receipt)
    print(
        json.dumps(
            {k: receipt[k] for k in ("retained", "excluded", "label_counts_retained")},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
