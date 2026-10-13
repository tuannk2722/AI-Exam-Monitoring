"""Workspace-local append-only use-once access, keyed by payload, not output/model."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError

from .adaptation_config import sha
from .artifacts import digest_json, now


def _path(workspace: Path, payload_sha256: str) -> Path:
    sha(payload_sha256)
    return workspace.resolve() / "outputs" / "holdout-access" / f"{payload_sha256}.jsonl"


def reserve(workspace: Path, payload_sha256: str, request: dict[str, Any]) -> str:
    path = _path(workspace, payload_sha256)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "status": "reserved",
        "payload_sha256": payload_sha256,
        "request": request,
        "created_at": now(),
        "previous_sha256": None,
    }
    token = digest_json(row)
    row["entry_sha256"] = token
    try:
        # Exclusive creation is the cross-process arbitration. A crash/partial file
        # still exists and blocks reuse; recovery requires a new owner protocol.
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as error:
        raise DataContractError(
            "Holdout already reserved/failed/consumed; automatic repeat blocked"
        ) from error
    return token


def history(workspace: Path, payload_sha256: str) -> list[dict[str, Any]]:
    try:
        rows = [
            json.loads(line)
            for line in _path(workspace, payload_sha256).read_text(encoding="utf-8").splitlines()
        ]
        previous = None
        for i, row in enumerate(rows):
            body = {k: v for k, v in row.items() if k != "entry_sha256"}
            if (
                row["payload_sha256"] != payload_sha256
                or row["previous_sha256"] != previous
                or row["entry_sha256"] != digest_json(body)
                or row["status"] not in ({"reserved"} if i == 0 else {"failed", "consumed"})
            ):
                raise DataContractError("Corrupt holdout access chain")
            previous = row["entry_sha256"]
        if not rows or len(rows) > 2:
            raise DataContractError("Invalid access lifecycle")
        return rows
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise DataContractError("Unreadable holdout access receipt") from error


def finish(
    workspace: Path, payload_sha256: str, token: str, *, success: bool, evidence: dict[str, Any]
) -> None:
    rows = history(workspace, payload_sha256)
    if len(rows) != 1 or rows[0]["entry_sha256"] != token:
        raise DataContractError("Holdout access token/state changed")
    row = {
        "status": "consumed" if success else "failed",
        "payload_sha256": payload_sha256,
        "created_at": now(),
        "previous_sha256": token,
        "evidence": evidence,
    }
    row["entry_sha256"] = digest_json(row)
    with _path(workspace, payload_sha256).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
