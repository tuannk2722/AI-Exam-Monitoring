"""Import pinned owner crop decisions into a new review-only PilotRecord ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records, write_records
from ai_exam_monitoring.data.review_acceptance import accept_reviews


def build(
    ledger: Path, ledger_sha256: str, decisions: Path, decisions_sha256: str,
    output: Path, workspace: Path,
) -> None:
    workspace = workspace.resolve()
    destination = output.resolve()
    if destination.exists() or not destination.is_relative_to(workspace / "data/interim"):
        raise DataContractError("Require new review output under data/interim")
    for path, digest in ((ledger, ledger_sha256), (decisions, decisions_sha256)):
        if sha256_file(path) != digest:
            raise DataContractError("Review input pin mismatch")
    evidence_ref = decisions.resolve().relative_to(workspace).as_posix()
    records = accept_reviews(
        read_records(ledger), json.loads(decisions.read_text(encoding="utf-8")),
        ledger_sha256=ledger_sha256, evidence_ref=evidence_ref, workspace=workspace,
    )
    # Validate every record/media before creating any output. mkdir refuses races.
    destination.mkdir(parents=True, exist_ok=False)
    write_records(destination / "ledger.jsonl", records)
    receipt = {
        "ledger_input_sha256": ledger_sha256,
        "owner_decisions_ref": evidence_ref,
        "owner_decisions_sha256": decisions_sha256,
        "ledger_output_sha256": sha256_file(destination / "ledger.jsonl"),
        "module_sha256": sha256_file(
            workspace / "src/ai_exam_monitoring/data/review_acceptance.py"
        ),
        "cli_sha256": sha256_file(Path(__file__)),
        "accepted_label_geometry_records": len(records),
        "known_target_cells": sum(sum(r.target_mask) for r in records),
        "both_unknown_records": sum(not any(r.target_mask) for r in records),
        "usage": "review_only", "split": None,
        "new_train_val_test_assignments": 0,
        "new_independent_groups_proven": 0,
    }
    (destination / "receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--ledger-sha256", required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--decisions-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    build(args.ledger, args.ledger_sha256, args.decisions, args.decisions_sha256,
          args.output, args.workspace)
