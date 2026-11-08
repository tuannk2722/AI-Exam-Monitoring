from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

DOCUMENTS = {
    "docs/system.md", "docs/data.md", "docs/training.md", "docs/development.md",
}
REQUIRED = DOCUMENTS | {
    "README.md",
    "AGENTS.md",
    "docs/00-INDEX.md",
    "docs/templates/task-template.md",
    "configs/datasets/pilot_b_release_v4.yaml",
    "data/processed/pilot-b/pilot-b-20261005-v4.dvc",
    "src/ai_exam_monitoring/data/pilot_schema.py",
    "src/ai_exam_monitoring/data/pilot_package.py",
    "src/ai_exam_monitoring/data/integrity.py",
    "src/ai_exam_monitoring/common/history.py",
    "archive/index.json",
    "src/ai_exam_monitoring/data/v7_release_acceptance.py",
    "src/ai_exam_monitoring/training/train.py",
    "src/ai_exam_monitoring/training/evaluate.py",
    "configs/datasets/pilot_b_release_v5.yaml",
    "configs/datasets/pilot_b_release_v6.yaml",
    "configs/datasets/pilot_b_release_v7.yaml",
    "configs/datasets/pilot_b_v5_release_proposal_20261007.yaml",
    "artifacts/reports/pilot-b-v5-proposal-20261007/membership-proposals.json",
    "artifacts/reports/pilot-b-v5-proposal-20261007/group-components.json",
    "artifacts/reports/pilot-b-v5-release-20261007/owner-approval.json",
    "data/processed/pilot-b/pilot-b-20261007-v5.dvc",
    "data/processed/pilot-b/pilot-b-20261007-v6.dvc",
}
FORBIDDEN_TRACKED_SUFFIXES = {
    ".pt", ".pth", ".onnx", ".engine", ".mp4", ".avi", ".mov", ".mkv",
    ".env", ".jpg", ".jpeg", ".png", ".npy", ".pyc", ".pyo", ".pem", ".key", ".p12",
}
FORBIDDEN_TRACKED_DIRS = {
    ".venv", "venv", "__pycache__", "data/raw", "data/interim", "data/processed",
    "artifacts/models", "artifacts/predictions", "artifacts/evidence",
    ".dvc/cache", ".dvc/tmp",
}


def forbidden_path(relative: str, archive_pointers: set[str] | None = None) -> bool:
    path = Path(relative)
    name = path.name.lower()
    normalized = relative.lower()
    data_metadata = path.suffix.lower() == ".dvc" or name == ".gitignore"
    return (
        path.suffix.lower() in FORBIDDEN_TRACKED_SUFFIXES
        or name == ".env"
        or (name.startswith(".env.") and name != ".env.example")
        or name in {"credentials.json", "service-account.json", "service_account.json",
                    "token.json", "id_rsa", "id_ed25519"}
        or normalized == ".dvc/config.local"
        or (normalized.startswith("archive/")
            and normalized not in {"archive/index.json", "archive/.gitignore"}
            and relative not in (archive_pointers or set()))
        or any(normalized.startswith(f"{directory}/") and name != ".gitkeep"
               and not (directory in {"data/raw", "data/interim", "data/processed"}
                        and data_metadata)
               for directory in FORBIDDEN_TRACKED_DIRS)
    )


def tracked_paths(root: Path) -> list[str] | None:
    # A ZIP nested inside another checkout must not inherit that checkout's index.
    # .git can also be a file (Git worktree).
    if not (root / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "-z"],
        check=True, capture_output=True,
    )
    return result.stdout.decode("utf-8", errors="surrogateescape").split("\0")[:-1]


def archive_registry(root: Path) -> set[str]:
    """Validate metadata only; CI must not require local binary payloads."""
    value = json.loads((root / "archive/index.json").read_text(encoding="utf-8"))
    if value.get("schema_version") != 1 or not isinstance(value.get("bundles"), list):
        raise ValueError("invalid archive registry schema")
    pointers: set[str] = set()
    names: set[str] = set()
    for bundle in value["bundles"]:
        name, path = bundle["name"], bundle["path"]
        if (not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name)
                or name in names or path != f"archive/{name}.zip"
                or not re.fullmatch(r"[a-f0-9]{64}", bundle["sha256"])):
            raise ValueError("invalid/duplicate archive identity")
        names.add(name)
        pointer = path + ".dvc"
        metadata = yaml.safe_load((root / pointer).read_text(encoding="utf-8"))
        outs = metadata["outs"]
        if (len(outs) != 1 or outs[0]["path"] != f"{name}.zip"
                or not re.fullmatch(r"[a-f0-9]{32}", outs[0]["md5"])
                or type(outs[0].get("size")) is not int
                or outs[0]["size"] != bundle["archive_bytes"]):
            raise ValueError(f"archive pointer differs from registry: {pointer}")
        pointers.add(pointer)
    return pointers


def web_delivery(root: Path, *, require_git: bool) -> set[str]:
    """Verify the small measured inputs needed by the optional laptop deployment."""
    execution = "configs/web/LAPTOP-VIDEO-20261108/execution.json"
    if not (root / execution).is_file():
        return set()
    required = {execution, "RUN.ps1", "configs/web/LAPTOP-VIDEO-20261108/inputs.json"}
    raw = json.loads((root / execution).read_text(encoding="utf-8"))
    for key in ("decision_ref", "parity", "profile", "profile_code"):
        pin = raw[key]
        relative = pin["path"]
        path = (root / relative).resolve()
        if (not path.is_relative_to(root.resolve())
                or (path.suffix != ".json" and key != "decision_ref")):
            raise ValueError("invalid web metadata path")
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin["sha256"]:
            raise ValueError(f"web metadata bytes differ: {relative}")
        if require_git and (root / ".git").exists():
            result = subprocess.run(["git", "-C", str(root), "show", f":{relative}"],
                                    check=True, capture_output=True)
            if hashlib.sha256(result.stdout).hexdigest() != pin["sha256"]:
                raise ValueError(f"Git index web metadata bytes differ: {relative}")
        required.add(relative)
    return required


def main(root: Path | None = None, *, require_git: bool = False) -> int:
    root = root or Path(__file__).resolve().parents[1]
    failures: list[str] = []
    try:
        pointers = archive_registry(root)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, yaml.YAMLError) as error:
        pointers = set()
        failures.append(f"invalid archive registry/pointer: {error}")
    required = REQUIRED | pointers
    try:
        required |= web_delivery(root, require_git=require_git)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        failures.append(f"invalid web delivery metadata: {error}")
    approval_path = "artifacts/reports/pilot-b-v5-release-20261007/owner-approval.json"
    try:
        approval = json.loads((root / approval_path).read_text(encoding="utf-8"))
        for key in ("membership", "groups", "proposal_config"):
            pin = approval[key]
            relative = pin["path"]
            if relative not in REQUIRED:
                raise ValueError("unexpected v5 dependency path")
            payload = (root / relative).read_bytes()
            if hashlib.sha256(payload).hexdigest() != pin["sha256"]:
                raise ValueError(f"local bytes differ: {relative}")
            if require_git and (root / ".git").exists():
                staged = subprocess.run(["git", "-C", str(root), "show", f":{relative}"],
                                        check=True, capture_output=True).stdout
                if hashlib.sha256(staged).hexdigest() != pin["sha256"]:
                    raise ValueError(f"Git index bytes differ: {relative}")
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        failures.append(f"invalid pinned v5 dependency: {error}")
    for relative in sorted(required):
        if not (root / relative).is_file():
            failures.append(f"missing required file: {relative}")
    try:
        paths = tracked_paths(root)
    except (OSError, subprocess.CalledProcessError):
        failures.append("cannot read Git index; install Git and verify repository access/integrity")
    else:
        if paths is None:
            print("WARNING: no .git metadata (ZIP mode); Git tracking safety NOT verified")
            if require_git:
                failures.append("Git metadata required for tracking safety check")
        else:
            print("Checking Git index (including staged files; ignored/untracked files excluded)")
            if require_git:
                managed = {p.relative_to(root).as_posix()
                           for folder in ("src", "tests", "scripts", "docs", "configs",
                                          "requirements", ".github")
                           for p in (root / folder).rglob("*")
                           if p.is_file() and "__pycache__" not in p.parts
                           and not any(part.endswith(".egg-info") for part in p.parts)
                           and p.suffix in {".py", ".md", ".json", ".yaml", ".yml", ".txt"}}
                for relative in sorted((required | managed | {"pyproject.toml"}) - set(paths)):
                    failures.append(f"required delivery file not in Git index: {relative}")
            for relative in sorted(set(paths)):
                if forbidden_path(relative, pointers):
                    failures.append(f"large/sensitive path tracked by Git: {relative}")
    index = root / "docs/00-INDEX.md"
    if index.is_file():
        index_text = index.read_text(encoding="utf-8")
        links = set(re.findall(r"\[[^\]]+\]\(([^)]+)\)", index_text))
        for document in sorted(DOCUMENTS):
            if Path(document).name not in links:
                failures.append(f"documentation index does not reference {document}")
        for link in sorted(links):
            if "://" not in link and not link.startswith("#"):
                target = link.split("#", 1)[0]
                if not (index.parent / target).is_file():
                    failures.append(f"documentation index has missing target: {target}")
    for failure in failures:
        print(f"ERROR: {failure}")
    print(f"Repository check complete; failures={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check repository structure and Git-tracked paths")
    parser.add_argument("--require-git", action="store_true", help="fail in ZIP/no-Git mode")
    sys.exit(main(require_git=parser.parse_args().require_git))
