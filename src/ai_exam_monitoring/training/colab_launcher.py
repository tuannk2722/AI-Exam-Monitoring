"""Standard-library bootstrap for a pinned private bundle and its canonical campaign.

The notebook mounts Drive and calls this module from the SHA-verified ZIP.
No model, training loop or Google authentication implementation lives here.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from collections.abc import Callable
from pathlib import Path, PurePosixPath
from typing import Any


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def child(root: Path, name: str) -> Path:
    p = PurePosixPath(name)
    target = (root / name).resolve()
    if (not name or p.is_absolute() or ".." in p.parts or "\\" in name or ":" in name
            or not target.is_relative_to(root.resolve())):
        raise RuntimeError("Unsafe bundle/bootstrap path")
    return target


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    os.replace(temporary, path)


def extract_bundle(archive: Path, expected_sha256: str, root: Path) -> dict[str, Any]:
    if sha256(archive) != expected_sha256:
        raise RuntimeError("Bundle SHA differs from the notebook")
    with zipfile.ZipFile(archive) as stream:
        names = stream.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError("Duplicate bundle members")
        manifest = json.loads(stream.read("bundle-manifest.json"))
        files = manifest["files"]
        if (manifest.get("schema_version") != "private-colab-bundle-v1"
                or not isinstance(files, dict) or set(names) != {*files, "bundle-manifest.json"}):
            raise RuntimeError("Bundle allowlist differs from archive contents")
        root.mkdir(parents=True, exist_ok=True)
        for name, digest in files.items():
            target = child(root, name)
            info = stream.getinfo(name)
            if stat.S_ISLNK(info.external_attr >> 16) or info.is_dir():
                raise RuntimeError("Symlink/directory bundle member")
            if target.exists():
                if not target.is_file() or sha256(target) != digest:
                    raise RuntimeError("Bundle extraction would overwrite divergent input")
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name+".tmp")
            with stream.open(name) as source, temporary.open("wb") as output:
                shutil.copyfileobj(source, output)
            if sha256(temporary) != digest:
                raise RuntimeError("Bundle member verification failed")
            os.replace(temporary, target)
        save(root/"bundle-manifest.json", manifest)
    return dict(manifest)


def committed_state(backup: Path) -> dict[str, Any]:
    manifest = json.loads((backup/"mirror-manifest.json").read_text(encoding="utf-8"))
    row = manifest["files"]["runs/campaign.json"]
    for p in (backup/"runs/campaign.json", child(backup, "versions/"+row["sha256"])):
        if p.is_file() and sha256(p) == row["sha256"]:
            return dict(json.loads(p.read_text(encoding="utf-8")))
    raise RuntimeError("No verified committed campaign state")


def export_metadata(backup: Path, output: Path, bootstrap: Path) -> None:
    allowed = {".json", ".yaml", ".yml", ".log", ".txt", ".svg"}
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        manifest_path = backup/"mirror-manifest.json"
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for name, row in manifest["files"].items():
                if PurePosixPath(name).suffix not in allowed:
                    continue
                candidates = (child(backup, name), child(backup, "versions/"+row["sha256"]))
                source = next((p for p in candidates if p.is_file()
                               and sha256(p) == row["sha256"]), None)
                if source is None:
                    raise RuntimeError("Metadata export input pin mismatch: "+name)
                archive.write(source, name)
            archive.write(manifest_path, "mirror-manifest.json")
        if bootstrap.is_dir():
            for p in sorted(bootstrap.rglob("*")):
                if p.is_file() and not p.is_symlink() and p.suffix in allowed:
                    archive.write(p, "bootstrap/"+p.relative_to(bootstrap).as_posix())


def launch(
    archive: Path, expected_sha256: str, storage: Path, *, attempt_started_at: float,
    resume: bool = False, prior_process_stopped: bool = False,
    workspace: Path = Path("/content/e009-workspace"),
    venv: Path = Path("/content/e009-venv"),
    deadline_callback: Callable[[float], None] | None = None,
) -> None:
    storage, workspace = storage.resolve(), workspace.resolve()
    if not storage.is_dir() or storage.is_relative_to(workspace):
        raise RuntimeError("Mounted private Drive folder required")
    journal = storage/"E009-launch.json"
    bootstrap = storage/"E009-bootstrap"
    backup = storage/"E009-V15-COLAB-20261106"
    if resume:
        if not prior_process_stopped or not journal.is_file():
            raise RuntimeError("Resume requires the original journal and a stopped old runtime")
        state = json.loads(journal.read_text(encoding="utf-8"))
        if state["bundle_sha256"] != expected_sha256:
            raise RuntimeError("Cannot change the bundle during recovery")
        if state.get("setup_in_progress"):
            raise RuntimeError("Interrupted setup: preserve logs and review its remaining budget")
    else:
        if journal.exists() or workspace.exists() or backup.exists() or venv.exists():
            raise RuntimeError("E009 already exists; use the documented recovery mode")
        state = {"bundle_sha256": expected_sha256, "started_at": attempt_started_at,
                 "setup_elapsed_seconds": 0., "setup_in_progress": False}
        save(journal, state)
    first = float(state["started_at"])
    deadline = first+12*3600
    if deadline <= time.time():
        raise RuntimeError("Original 12-hour budget exhausted; timestamp must not reset")
    if deadline_callback:
        deadline_callback(deadline)
    if not ((3, 11) <= sys.version_info[:2] < (3, 13)):
        raise RuntimeError("Select Python 3.11/3.12 in Colab; do not relax this guard")
    bootstrap.mkdir(exist_ok=True)
    log = bootstrap/f"setup-{int(attempt_started_at)}.log"
    setup_started = time.time()
    state["setup_elapsed_seconds"] += max(
        0., setup_started-(attempt_started_at if resume else first))
    state["setup_in_progress"] = True
    save(journal, state)
    try:
        if shutil.disk_usage(storage).free < 50_000_000_000:
            raise RuntimeError("Private Drive filesystem reports less than the required 50 GB free")
        if shutil.disk_usage(workspace.parent).free < 25_000_000_000:
            raise RuntimeError("Insufficient local Colab disk for input/cache/checkpoints")
        manifest = extract_bundle(archive, expected_sha256, workspace)
        setup_until = min(deadline, setup_started+40*60-float(state["setup_elapsed_seconds"]))
        if not resume:
            setup_until = min(setup_until, first+40*60)
        python = venv/"bin/python"
        new_environment = not python.exists()
        env = bootstrap/"environment-first.txt"
        commands = []
        if new_environment:
            commands.append([sys.executable, "-m", "venv", str(venv)])
        if env.exists() and state.get("freeze_sha256") != sha256(env):
            raise RuntimeError("Recorded environment closure changed")
        if new_environment or not state.get("environment_ready"):
            dependency_command = ([str(python), "-m", "pip", "install", "--extra-index-url",
                                   "https://download.pytorch.org/whl/cu128", "-r", str(env)]
                                  if env.exists() else [str(python), "-m", "pip", "install",
                                                        "-r", "requirements/classifier-colab.txt"])
            commands.extend([
                dependency_command,
                [str(python), "-m", "pip", "install", "--no-deps", "-e", "."],
            ])
        with log.open("a", encoding="utf-8") as stream:
            subprocess.run(["nvidia-smi"], stdout=stream, stderr=subprocess.STDOUT,
                           check=True, timeout=max(1., min(15., setup_until-time.time())))
            for command in commands:
                remaining = setup_until-time.time()
                if remaining <= 0:
                    raise TimeoutError("Cumulative setup budget exhausted")
                subprocess.run(command, cwd=workspace, stdout=stream, stderr=subprocess.STDOUT,
                               check=True, timeout=remaining)
        if time.time() >= setup_until:
            raise TimeoutError("Cumulative setup budget exhausted")
        freeze = subprocess.check_output([str(python), "-m", "pip", "freeze"], cwd=workspace,
                                         text=True, timeout=max(1., setup_until-time.time()))
        if env.exists() and env.read_text(encoding="utf-8") != freeze:
            raise RuntimeError("Recovery pip freeze differs; no silent environment migration")
        env.write_text(freeze, encoding="utf-8")
        save(bootstrap/f"setup-{int(attempt_started_at)}.json", {
            "python": sys.version, "platform": platform.platform(),
            "bundle_sha256": expected_sha256, "code_sha256": manifest["code_sha256"],
            "attempt_started_at": attempt_started_at, "original_started_at": first})
        state["environment_ready"] = True
        state["freeze_sha256"] = sha256(env)
        if time.time() >= setup_until:
            raise TimeoutError("Cumulative setup budget exhausted during environment recording")
    finally:
        state["setup_elapsed_seconds"] += time.time()-setup_started
        state["setup_in_progress"] = False
        save(journal, state)
        if sys.exc_info()[0] is not None:
            metadata = storage/f"E009-V15-results-metadata-{int(attempt_started_at)}.zip"
            export_metadata(backup, metadata, bootstrap)
            print(f"Setup stopped; metadata: {metadata}", flush=True)
    if resume and backup.exists():
        persisted = committed_state(backup)
        if persisted["started_at"] != first:
            raise RuntimeError("Campaign and launch journal clocks differ")
    command = [str(python), "-m", "ai_exam_monitoring.training.representation_campaign",
               "--design", str(workspace/manifest["design"]["path"]),
               "--workspace", str(workspace), "--storage", str(storage),
               "--gpu-started-at", str(first)]
    if resume and backup.exists():
        command.extend(["--resume", "--prior-process-stopped"])
    try:
        subprocess.run(command, cwd=workspace, check=True, timeout=max(1., deadline-time.time()))
    finally:
        metadata = storage/f"E009-V15-results-metadata-{int(attempt_started_at)}.zip"
        export_metadata(backup, metadata, bootstrap)
        print(f"Metadata: {metadata}", flush=True)
        print(f"Full checkpoints and recovery: {backup}", flush=True)
