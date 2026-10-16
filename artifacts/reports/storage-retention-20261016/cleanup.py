"""One-time, owner-approved retention migration; dry-run before exact-plan apply."""
from __future__ import annotations

import argparse
import json
import stat
import subprocess
from collections import Counter
from pathlib import Path

import yaml

from ai_exam_monitoring.common.history import create, member_path, restore, verify
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import verify_payload

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASELINE = "999c0cce08a6f9a4002693d29be578fcba803dc8"
CURRENT = (
    "data/processed/pilot-b/pilot-b-20261016-v10",
    "data/processed/e004/E004-c345-development-20261016",
)
RETIRED_ARCHIVES = (
    "e004-v9-execution-20261013",
    "e004-rc1-execution-20261014",
    "e004-c345-execution-20261016",
)
BACKUP = "archive/current-assets-20261016.zip"


def write(name: str, value: object) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf8")


def files(folder: str) -> list[Path]:
    return [p for p in (ROOT / folder).rglob("*")
            if p.is_file() and "__pycache__" not in p.parts]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def entry(path: Path, reason: str) -> dict:
    return {"path": relative(path), "sha256": sha256_file(path),
            "bytes": path.stat().st_size, "reason": reason}


def measure() -> dict:
    seen = set()
    logical = unique = 0
    for folder in (".dvc/cache", "archive", ".venv", "outputs", "data", "artifacts"):
        for p in files(folder):
            s = p.stat()
            logical += s.st_size
            key = (s.st_dev, s.st_ino)
            if key not in seen:
                unique += s.st_size
                seen.add(key)
    return {"logical_bytes": logical, "unique_file_bytes": unique,
            "scope": "cache/archive/venv/outputs/data/artifacts; not allocated disk clusters"}


def plan() -> None:
    if (HERE / "plan.json").exists():
        raise RuntimeError("Plan exists; do not overwrite the reviewed inventory")
    if subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip() != BASELINE:
        raise RuntimeError("Unexpected baseline")
    for folder in CURRENT:
        verify_payload(ROOT / folder)
    protected = set()
    # Keep sources, review material, cohort/reserve packages and all small run metadata.
    for folder in ("data/raw", "data/interim", "data/processed/e004-cohorts", *CURRENT):
        protected.update(files(folder))
    for p in files("outputs"):
        if p.suffix.lower() not in {".pt", ".pth"}:
            protected.add(p)
        elif ("smoke" not in p.relative_to(ROOT / "outputs").parts[0].lower()
              and "orphan-snapshot" not in p.relative_to(ROOT / "outputs").parts[0]):
            if p.name != "last.pt":
                protected.add(p)
    deletions = {}
    for p in files("outputs"):
        if p.suffix.lower() not in {".pt", ".pth"} or p in protected:
            continue
        run_folder = ROOT / "outputs" / p.relative_to(ROOT / "outputs").parts[0]
        run = json.loads((run_folder / "run.json").read_text(encoding="utf8"))
        if "orphan-snapshot" in run_folder.name:
            current_run = json.loads((ROOT / "outputs/E004-C345-W-H/run.json").read_text())
            assert current_run["status"] == "FINISHED"
        elif run["status"] != "FINISHED":
            raise RuntimeError(f"Unfinished run: {run_folder}")
        deletions[p] = "retired_resume_or_smoke_weights; metadata retained"
    for folder in ("data/processed/pilot-b", "data/processed/e004"):
        for p in files(folder):
            if "crops" in p.parts and p not in protected:
                deletions[p] = (
                    "historical_crop_payload; metadata retained; no reproduction guarantee")
            elif p not in protected:
                protected.add(p)
    registry = json.loads((ROOT / "archive/index.json").read_text())
    archive_status = []
    for bundle in registry["bundles"]:
        p = member_path(ROOT, bundle["path"])
        assert sha256_file(p) == bundle["sha256"]
        retired = bundle["name"] in RETIRED_ARCHIVES
        archive_status.append({"path": bundle["path"], "sha256": bundle["sha256"],
                               "availability": "retired" if retired else "local_retained"})
        if retired:
            deletions[p] = "retired_execution_archive; current assets backed up separately"
        pointer = yaml.safe_load(Path(str(p) + ".dvc").read_text())
        md5 = pointer["outs"][0]["md5"]
        cache = ROOT / ".dvc/cache/files/md5" / md5[:2] / md5[2:]
        if cache.exists() and cache.stat().st_nlink == 1:
            assert sha256_file(cache) == bundle["sha256"]
            deletions[cache] = "archive_cache_copy; retained ZIP or explicitly retired execution"
    assert not protected.intersection(deletions)
    write("plan.json", {"baseline_commit": BASELINE, "owner_authorization":
        "Owner approved current-assets retention and historical tradeoff on 2026-10-16",
        "before": measure(), "archives": archive_status,
        "protected": [entry(p, "current_asset_or_source_or_metadata") for p in sorted(protected)],
        "delete": [entry(p, reason) for p, reason in sorted(deletions.items())]})
    print("Planned", len(deletions), "files; protected", len(protected), flush=True)


def backup(*, reuse: bool = False) -> None:
    value = json.loads((HERE / "plan.json").read_text())
    paths = [r["path"] for r in value["protected"]]
    # Git retains source/config/reports; include these in the standalone current-assets backup too.
    for folder in ("src", "tests", "docs", "configs", "requirements", "artifacts/reports"):
        paths.extend(relative(p) for p in files(folder) if not p.is_relative_to(HERE))
    paths.extend(("pyproject.toml", "AGENTS.md", "STORAGE_OPTIMIZATION.md"))
    archive = ROOT / BACKUP
    if not reuse:
        create(ROOT, archive, paths, name="current-assets-20261016",
               progress=lambda n: print("backup", n, flush=True))
    digest = sha256_file(archive)
    manifest = verify(archive, expected_sha256=digest)
    # Full extraction plus verification exercises the restore path, not only ZIP readability.
    scratch = ROOT / "outputs/_scratch/storage-retention-restore"
    destination = Path("\\\\?\\" + str(scratch))
    assert not destination.exists()
    restored = restore(archive, destination, expected_sha256=digest)
    for row in manifest.files:
        assert sha256_file(member_path(destination, row.path)) == row.sha256
    assert restored == len(manifest.files)
    write("backup-verification.json", {"path": BACKUP, "sha256": digest,
        "files": restored, "archive_bytes": archive.stat().st_size,
        "restore_verified": True, "same_drive": True, "off_device": False,
        "restore_scratch": relative(scratch)})
    print("Backup verified", restored, flush=True)


def apply() -> None:
    # An interrupted tool connection does not prove its subprocess has stopped.
    # Exclusive creation prevents a second apply from racing an existing process.
    lock = HERE / "apply.lock"
    with lock.open("x", encoding="utf8") as handle:
        handle.write("apply in progress; inspect process and receipt before recovery\n")
    try:
        _apply_locked()
    finally:
        lock.unlink()


def _apply_locked() -> None:
    if (HERE / "receipt.json").exists():
        raise RuntimeError("Already applied")
    value = json.loads((HERE / "plan.json").read_text())
    saved = json.loads((HERE / "backup-verification.json").read_text())
    assert saved["restore_verified"] and sha256_file(ROOT / BACKUP) == saved["sha256"]
    supplement = json.loads((HERE / "dependency-backup-verification.json").read_text())
    covered = {}
    for receipt in (saved, supplement):
        assert receipt["restore_verified"]
        manifest = verify(ROOT / receipt["path"], expected_sha256=receipt["sha256"])
        covered.update({r.path: r.sha256 for r in manifest.files})
    assert all(covered.get(r["path"]) == r["sha256"] for r in value["protected"])
    tracked = set(subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0"))
    # Complete preflight before the first unlink; paths must remain inside the workspace.
    for i, row in enumerate(value["protected"] + value["delete"], 1):
        p = member_path(ROOT, row["path"])
        assert not p.is_symlink() and p.stat().st_size == row["bytes"]
        assert sha256_file(p) == row["sha256"], row["path"]
        if i % 1000 == 0:
            print("preflight", i, flush=True)
    for row in value["delete"]:
        assert row["path"] not in tracked
        assert row["path"].startswith(("outputs/", "data/processed/", "archive/", ".dvc/cache/"))
        assert member_path(ROOT, row["path"]).stat().st_nlink == 1
    for row in value["delete"]:
        p = member_path(ROOT, row["path"])
        # No shared inode can be chmodded; history hardlink/cache was excluded by plan.
        assert p.stat().st_nlink == 1
        p.chmod(p.stat().st_mode | stat.S_IWRITE)
        p.unlink()
    for row in value["protected"]:
        assert sha256_file(member_path(ROOT, row["path"])) == row["sha256"]
    for folder in CURRENT:
        verify_payload(ROOT / folder)
    write("receipt.json", {"status": "complete", "deleted_files": len(value["delete"]),
        "deleted_logical_bytes": sum(r["bytes"] for r in value["delete"]),
        "reasons": dict(Counter(r["reason"] for r in value["delete"])),
        "protected_files_verified": len(value["protected"]),
        "current_packages_integrity": "PASS", "backup": saved,
        "dependency_backup": supplement,
        "historical_reproduction": "not guaranteed for retired payloads; no hash resealing",
        "after_before_scratch_cleanup": measure()})
    print("Applied; protected bytes and package integrity PASS", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("plan", "backup", "verify-backup", "apply"),
                        default="plan", nargs="?")
    args = parser.parse_args()
    {"plan": plan, "backup": backup, "verify-backup": lambda: backup(reuse=True),
     "apply": apply}[args.mode]()
