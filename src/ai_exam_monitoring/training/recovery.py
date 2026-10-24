"""Atomic epoch recovery snapshots to an explicitly supplied private storage path."""

from __future__ import annotations

import hashlib
import io
import json
import os
import tarfile
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError


def mirror_epoch(output: Path, destination: Path, record: dict[str, Any]) -> None:
    """The trainer calls this synchronously at a committed epoch, never mid-write."""
    destination.mkdir(parents=True, exist_ok=True)
    names = ("last.pt", "initialization.json", "resolved-config.json", "code-provenance.json",
             "environment.json")
    payloads = {name: (output / name).read_bytes() for name in names}
    payloads["run.json"] = json.dumps(record, indent=2, allow_nan=False).encode()
    checks = {name: hashlib.sha256(value).hexdigest() for name, value in payloads.items()}
    payloads["checksums.json"] = json.dumps(checks).encode()
    temporary = destination / f"{output.name}.tar.tmp"
    with tarfile.open(temporary, "w") as archive:
        for name, value in payloads.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(value)
            archive.addfile(entry, io.BytesIO(value))
    os.replace(temporary, destination / f"{output.name}.tar")


def restore_epoch(snapshot: Path, output: Path) -> None:
    """Restore only into a new directory; the trainer still verifies identity/environment."""
    if output.exists():
        raise DataContractError("Recovery output already exists")
    with tarfile.open(snapshot, "r") as archive:
        members = archive.getmembers()
        allowed = {"last.pt", "initialization.json", "resolved-config.json", "code-provenance.json",
                   "environment.json", "run.json", "checksums.json"}
        if (len(members) != len(allowed) or {m.name for m in members} != allowed
                or any(not m.isfile() for m in members)):
            raise DataContractError("Unexpected recovery snapshot members")
        payloads = {}
        for member in members:
            stream = archive.extractfile(member)
            if stream is None:
                raise DataContractError("Missing recovery member")
            payloads[member.name] = stream.read()
    checks = json.loads(payloads["checksums.json"])
    if set(checks) != allowed - {"checksums.json"} or any(
        hashlib.sha256(payloads[name]).hexdigest() != digest for name, digest in checks.items()
    ):
        raise DataContractError("Recovery checksum mismatch")
    output.mkdir(parents=True)
    for name, value in payloads.items():
        (output / name).write_bytes(value)
