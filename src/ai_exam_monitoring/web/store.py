"""Human decisions live separately from immutable machine evidence."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STATUSES = {"candidate", "confirmed", "dismissed", "uncertain"}


def validate_review(value: dict[str, Any], event_ids: set[str]) -> None:
    if not isinstance(value.get("decisions"), dict):
        raise ValueError("Thiếu decisions")
    if not isinstance(value.get("summary", ""), str):
        raise ValueError("Ghi chú tổng kết không hợp lệ")
    if value.get("disposition", "pending") not in {
        "pending",
        "accepted_with_limitations",
        "revisit",
    }:
        raise ValueError("Disposition không hợp lệ")
    for identity, decision in value["decisions"].items():
        if identity not in event_ids or not isinstance(decision, dict):
            raise ValueError("Event không thuộc phiên này")
        if not isinstance(decision.get("status"), str) or decision["status"] not in STATUSES:
            raise ValueError("Trạng thái review không hợp lệ")
        if (
            not isinstance(decision.get("note", ""), str)
            or not isinstance(decision.get("flagged", False), bool)
            or not isinstance(decision.get("reasons", []), list)
            or not all(isinstance(x, str) for x in decision.get("reasons", []))
        ):
            raise ValueError("Ghi chú/lý do/cờ review không hợp lệ")


class ReviewStore:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with closing(sqlite3.connect(path)) as db, db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS reviews "
                "(evidence TEXT PRIMARY KEY, revision INTEGER NOT NULL, payload TEXT NOT NULL)"
            )

    def get(self, evidence: str) -> dict[str, Any]:
        with closing(sqlite3.connect(self.path)) as db:
            row = db.execute(
                "SELECT revision, payload FROM reviews WHERE evidence=?", (evidence,)
            ).fetchone()
        if row is None:
            return {
                "schema_version": "event-human-review-v1",
                "events_sha256": evidence,
                "revision": 0,
                "decisions": {},
                "summary": "",
                "disposition": "pending",
            }
        value: dict[str, Any] = json.loads(row[1])
        return {**value, "revision": row[0]}

    def save(self, evidence: str, value: dict[str, Any], event_ids: set[str]) -> dict[str, Any]:
        if (
            value.get("schema_version") != "event-human-review-v1"
            or value.get("events_sha256") != evidence
        ):
            raise ValueError("JSON không cùng version hoặc SHA256 evidence")
        validate_review(value, event_ids)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute(
                "SELECT revision FROM reviews WHERE evidence=?", (evidence,)
            ).fetchone()
            revision = old[0] if old else 0
            if value.get("revision") != revision:
                raise FileExistsError("Review đã đổi ở tab khác. Tải lại trước khi lưu.")
            result = {
                k: value.get(k, default)
                for k, default in (("decisions", {}), ("summary", ""), ("disposition", "pending"))
            }
            result["decisions"] = {
                identity: {
                    "status": decision["status"],
                    "note": decision.get("note", ""),
                    "reasons": decision.get("reasons", []),
                    "flagged": decision.get("flagged", False),
                }
                for identity, decision in value["decisions"].items()
            }
            result.update(
                schema_version="event-human-review-v1",
                events_sha256=evidence,
                revision=revision + 1,
                updated_at=datetime.now(UTC).isoformat(),
            )
            db.execute(
                "INSERT OR REPLACE INTO reviews VALUES (?, ?, ?)",
                (evidence, revision + 1, json.dumps(result, ensure_ascii=False)),
            )
        return result
