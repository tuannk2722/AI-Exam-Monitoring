"""Verified incremental persistence and non-resettable campaign time limits."""

from __future__ import annotations

import math
import os
import re
import shutil
import time
from pathlib import Path, PurePosixPath
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .artifacts import write_json


def safe_child(root: Path, relative: str) -> Path:
    parts = PurePosixPath(relative)
    path = (root / relative).resolve()
    if (not relative or "\\" in relative or ":" in relative or parts.is_absolute()
            or ".." in parts.parts or not path.is_relative_to(root.resolve())):
        raise DataContractError("Unsafe campaign persistence path")
    return path


class IncrementalMirror:
    """Hash every publication; verify all stored bytes before explicit recovery.

    Unchanged files are skipped using the owned manifest and local stat cache.
    The cache is an I/O optimization, never evidence for recovering another process.
    """

    def __init__(self, destination: Path):
        import json

        self.destination = destination.resolve()
        self.destination.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.destination / "mirror-manifest.json"
        self.files: dict[str, Any] = {}
        self.cache: dict[str, tuple[int, int, str]] = {}
        if self.manifest_path.exists():
            payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != "incremental-campaign-mirror-v1":
                raise DataContractError("Unknown campaign mirror manifest")
            self.files = payload["files"]
            if not isinstance(self.files, dict):
                raise DataContractError("Invalid campaign mirror files")
            for name in self.files:
                safe_child(self.destination, name)
                row = self.files[name]
                if (not isinstance(row, dict) or set(row) != {"bytes", "sha256"}
                        or type(row["bytes"]) is not int or row["bytes"] < 0
                        or re.fullmatch(r"[0-9a-f]{64}", str(row["sha256"])) is None):
                    raise DataContractError("Invalid persisted file pin")

    def verified_file(self, name: str) -> Path:
        row = self.files[name]
        # Retaining the previous immutable bytes makes publication interruption-safe:
        # an old manifest still resolves even if the current visible file was replaced.
        for path in (safe_child(self.destination, name),
                     safe_child(self.destination, "versions/"+row["sha256"])):
            if (path.is_file() and path.stat().st_size == row["bytes"]
                    and sha256_file(path) == row["sha256"]):
                return path
        raise DataContractError(f"Persisted campaign bytes changed: {name}")

    def sync(self, trees: list[tuple[Path, str]], *, deadline: float) -> dict[str, Any]:
        started = time.time()
        copied = skipped = size = 0
        for source, prefix in trees:
            if not source.exists():
                continue
            entries = sorted(source.rglob("*")) if source.is_dir() else [source]
            for path in entries:
                if time.time() >= deadline:
                    raise TimeoutError("Persistence deadline exhausted")
                if path.is_symlink():
                    raise DataContractError("Symlink in campaign persistence scope")
                if not path.is_file() or path.name.endswith((".tmp", ".partial", ".sync-tmp")):
                    continue
                relative = (PurePosixPath(prefix) / path.relative_to(source).as_posix()
                            if source.is_dir() else PurePosixPath(prefix)).as_posix()
                target = safe_child(self.destination, relative)
                stat = path.stat()
                cached = self.cache.get(str(path))
                digest = (cached[2] if cached and cached[:2] == (stat.st_size, stat.st_mtime_ns)
                          else sha256_file(path))
                self.cache[str(path)] = (stat.st_size, stat.st_mtime_ns, digest)
                row = {"bytes": stat.st_size, "sha256": digest}
                if self.files.get(relative) == row and target.is_file():
                    if target.stat().st_size != stat.st_size:
                        raise DataContractError("Previously published campaign file changed size")
                    skipped += 1
                    continue
                if relative in self.files:
                    previous = self.verified_file(relative)
                    version = safe_child(self.destination,
                                         "versions/"+self.files[relative]["sha256"])
                    if not version.exists():
                        version.parent.mkdir(exist_ok=True)
                        version_temp = version.with_suffix(".tmp")
                        shutil.copyfile(previous, version_temp)
                        if sha256_file(version_temp) != self.files[relative]["sha256"]:
                            raise DataContractError("Previous publication not preserved")
                        os.replace(version_temp, version)
                    if sha256_file(version) != self.files[relative]["sha256"]:
                        raise DataContractError("Previous version is corrupt")
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_name(target.name + ".sync-tmp")
                shutil.copyfile(path, temporary)
                if sha256_file(temporary) != digest:
                    raise DataContractError("Campaign copy verification failed")
                os.replace(temporary, target)
                self.files[relative] = row
                copied += 1
                size += stat.st_size
        write_json(self.manifest_path, {"schema_version": "incremental-campaign-mirror-v1",
                                        "files": self.files})
        if time.time() > deadline:
            raise TimeoutError("Persistence exceeded approved deadline")
        return {"copied_files": copied, "skipped_files": skipped, "copied_bytes": size,
                "elapsed_seconds": time.time() - started}

    def verify(self) -> None:
        for name in self.files:
            self.verified_file(name)

    def restore(self, workspace: Path, mappings: dict[str, Path]) -> None:
        self.verify()
        for name, row in self.files.items():
            prefix, separator, tail = name.partition("/")
            if not separator or prefix not in mappings:
                raise DataContractError("Unexpected recovery namespace")
            target = safe_child(mappings[prefix], tail)
            if not target.is_relative_to(workspace.resolve()):
                raise DataContractError("Restore outside campaign workspace")
            if target.exists():
                if sha256_file(target) != row["sha256"]:
                    raise DataContractError("Recovery would overwrite divergent local bytes")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.verified_file(name), target)
            if sha256_file(target) != row["sha256"]:
                raise DataContractError("Restored campaign file changed")


def phase_deadline(
    started_at: float, budget: dict[str, Any], phase: str, phase_start: float
) -> float:
    if not all(math.isfinite(v) for v in (started_at, phase_start)):
        raise DataContractError("Nonfinite campaign clock")
    if phase_start < started_at:
        raise DataContractError("Phase predates campaign")
    if phase == "smoke":
        return float(min(started_at + (budget["setup_and_environment_minutes"]
                                 + budget["actual_gpu_smoke_minutes"]) * 60,
                         phase_start + budget["actual_gpu_smoke_minutes"] * 60))
    if phase == "research":
        return float(min(started_at + budget["training_deadline_minutes_from_first_launch"] * 60,
                         phase_start + budget["research_pool_minutes"] * 60))
    raise DataContractError("Unknown campaign phase")


def admit_run(now: float, until: float, cap_seconds: float, completed: int, maximum: int) -> None:
    if (not all(math.isfinite(v) for v in (now, until, cap_seconds)) or cap_seconds <= 0
            or completed >= maximum or now + cap_seconds > until):
        raise TimeoutError("Insufficient approved budget for another complete run")
