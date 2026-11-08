"""Build and launch the isolated, measured B0 video-upload deployment."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.inference.execution import verify_execution_packages
from ai_exam_monitoring.inference.execution_processor import load_execution_selection
from ai_exam_monitoring.inference.runtime_config import (
    load_runtime_config,
    media_deadline,
    verify_media,
)
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import code_identity, write_json

CONFIG = "configs/web/LAPTOP-VIDEO-20261108"

def input_files(root: Path) -> dict[str, Any]:
    """Read the exact deployment dependencies; this is not a model approval."""
    raw = json.loads((root / CONFIG / "inputs.json").read_text(encoding="utf-8"))
    files = raw.get("files")
    if (raw.get("schema_version") != "video-web-inputs-v1"
            or not isinstance(files, dict) or not files):
        raise DataContractError("Invalid video web input manifest")
    for name, pin in files.items():
        path = PurePosixPath(name)
        if (not name.startswith("outputs/") or path.as_posix() != name
                or ".." in path.parts or "\\" in name or ":" in name
                or path.suffix not in {".pt", ".zip", ".json"}
                or not (root / name).resolve().is_relative_to(root / "outputs")
                or not isinstance(pin, dict) or set(pin) != {"sha256", "bytes"}
                or not isinstance(pin["sha256"], str)
                or re.fullmatch(r"[0-9a-f]{64}", pin["sha256"]) is None
                or type(pin["bytes"]) is not int or pin["bytes"] <= 0):
            raise DataContractError(f"Invalid deployment input: {name}")
    return files


def restore(root: Path, archive: Path | None = None) -> None:
    """Restore only missing pinned inputs, never source/config or changed files."""
    root = root.resolve()
    files = input_files(root)
    missing = []
    for name, pin in files.items():
        path = root / name
        if path.is_symlink():
            raise DataContractError(f"Deployment input is a symlink: {name}")
        if path.exists():
            if (not path.is_file() or path.stat().st_size != pin["bytes"]
                    or sha256_file(path) != pin["sha256"]):
                raise DataContractError(f"Existing input differs; refusing overwrite: {name}")
        else:
            missing.append(name)
    if missing and archive is None:
        raise DataContractError("Missing model inputs; use RUN.ps1 -Artifacts <video-web.zip>: "
                                + ", ".join(missing))
    if missing:
        assert archive is not None
        # Validate every requested member before installing any payload.
        with tempfile.TemporaryDirectory(prefix="video-web-inputs-") as folder:
            staged = Path(folder)
            with zipfile.ZipFile(archive) as source:
                names = source.namelist()
                for index, name in enumerate(missing):
                    if names.count(name) != 1:
                        raise DataContractError(f"Missing/duplicate deployment member: {name}")
                    member = source.getinfo(name)
                    if member.file_size != files[name]["bytes"]:
                        raise DataContractError(f"Deployment input size mismatch: {name}")
                    target = staged / str(index)
                    with source.open(member) as src, target.open("xb") as dst:
                        shutil.copyfileobj(src, dst)
                    if sha256_file(target) != files[name]["sha256"]:
                        raise DataContractError(f"Deployment input checksum mismatch: {name}")
            created = []
            try:
                for index, name in enumerate(missing):
                    target = root / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as dst:
                        created.append(target)
                        with (staged / str(index)).open("rb") as src:
                            shutil.copyfileobj(src, dst)
            except BaseException:
                for target in created:
                    target.unlink(missing_ok=True)
                raise
    print(json.dumps(dict(status="inputs_ready", restored=len(missing), inputs=len(files))))


def selected(root: Path) -> tuple[Any, dict[str, Any], Any]:
    monitor = load_yaml(root / CONFIG / "monitor.yaml")
    runtime = load_runtime_config(root / monitor["models"]["B0"]["runtime"], root)
    execution, settings = load_execution_selection(
        FilePin(**monitor["execution"]).verify(root), root, runtime)
    return runtime, execution, settings


def dependencies(root: Path) -> bool:
    for line in (root / "requirements/video-web.txt").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, expected = line.split("==")
        try:
            if version(name) != expected:
                return False
        except PackageNotFoundError:
            return False
    return True


def check(root: Path, *, web: bool = False) -> None:
    runtime, execution, settings = selected(root)
    receipt = json.loads(runtime.pin("detector_receipt").read_text(encoding="utf-8"))
    verify_execution_packages(receipt["packages"], execution["packages"], settings)
    if web:
        if not dependencies(root):
            raise DataContractError("Install the pinned web dependencies only")
        for module in ("fastapi", "uvicorn", "jinja2"):
            import_module(module)
    print(json.dumps(dict(device=settings.device, batch_size=settings.batch_size,
                          precision="float32", status="ready")))


def receipt(root: Path, source: Path, delete_by: str, *, confirmed: bool) -> Path:
    if not confirmed or source.suffix.lower() != ".mp4" or not source.is_file():
        raise DataContractError("Confirm rights/non-holdout and choose a local MP4")
    digest = sha256_file(source)
    if digest in {"5b26664dd6a761366771ca6d1f3a388efa67bb2a2e18d1fc62549a22978943f6",
                  "61972be2648d1551f61b739ea6a43c0e12aaa8923dba6d17ab0b89a74766ca70"}:
        raise DataContractError("Retired media cannot receive a renewed deadline")
    runtime = selected(root)[0]
    value = dict(schema_version="runtime-media-approval-v2", status="approved",
                 runtime_id=runtime.raw["runtime_id"], use_scope="local_prototype_qa",
                 source_sha256=digest, test_or_holdout=False, rights_confirmed=True,
                 third_party_processing=False, access="repository_owner", retention_days=7,
                 decision_ref=f"{CONFIG}/README.md", media_delete_by=delete_by)
    media_deadline(value)
    path = root / "outputs/receipts" / f"{digest}.json"
    if path.exists():
        old = verify_media(source, path, runtime)
        if old != value:
            raise DataContractError("Existing source receipt differs; do not renew or overwrite it")
    else:
        write_json(path, value)
    verify_media(source, path, runtime)
    print("Upload this receipt JSON: " + str(path))
    return path


def collect(root: Path) -> set[Path]:
    config = load_yaml(root / CONFIG / "web.yaml")
    runtime_paths = [config["runtime"], "configs/runtime/RUNTIME-E009-20261107/B0.yaml"]
    files = {p for p in (root / "src/ai_exam_monitoring").rglob("*")
             if p.is_file() and p.suffix in {".py", ".html", ".css", ".js"}}
    files.update((root / CONFIG).glob("*"))
    files.add(root / "requirements/video-web.txt")
    files.add(root / "RUN.ps1")
    files.add(root / "README.md")
    files.update(root / config[key] for key in ("tracker", "event_rule"))
    pins = []
    for runtime_path in runtime_paths:
        runtime = load_runtime_config(root / runtime_path, root)
        files.add(root / runtime_path)
        approval = root / runtime.raw["approval_ref"]
        files.add(approval)
        files.update(runtime.pin(n) for n in runtime.raw["pins"])
        pins.append(json.loads(approval.read_text(encoding="utf-8"))["decision_ref"])
        selection = json.loads(runtime.pin("detector_selection").read_text(encoding="utf-8"))
        pins.extend([selection["decision_ref"], *selection["evidence"].values()])
        resolved = json.loads(runtime.pin("resolved_config").read_text(encoding="utf-8"))
        pins.extend(resolved[n] for n in ("encoder_source", "weights_license"))
    monitor = load_yaml(root / config["monitor_config"])
    execution_path = FilePin(**monitor["execution"]).verify(root)
    files.add(execution_path)
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    pins.extend(execution[n] for n in ("decision_ref", "parity", "profile", "profile_code"))
    files.update(FilePin(**pin).verify(root) for pin in pins)
    for name, value in input_files(root).items():
        path = root / name
        if (path not in files or not path.is_file() or path.stat().st_size != value["bytes"]
                or sha256_file(path) != value["sha256"]):
            raise DataContractError(f"Deployment input closure mismatch: {name}")
    for path in files:
        if (not path.resolve().is_relative_to(root) or path.is_symlink() or not path.is_file()
                or path.suffix.lower() in {".mp4", ".jpg", ".png", ".jpeg"}
                or path.resolve().is_relative_to(root / "data")):
            raise DataContractError("Deployment input outside model/config/source scope")
    return files


def build(root: Path, output: Path) -> dict[str, Any]:
    files = collect(root)
    if not output.is_relative_to(root / "outputs") or output == root / "outputs":
        raise DataContractError("Require a new deployment directory below outputs")
    output.mkdir(parents=True, exist_ok=False)
    manifest = dict(schema_version="video-web-transfer-v1", code=code_identity(),
                    files={p.relative_to(root).as_posix():
                           dict(sha256=sha256_file(p), bytes=p.stat().st_size)
                           for p in sorted(files)})
    archive = output / "video-web.zip"
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED, compresslevel=3) as z:
        for path in sorted(files):
            z.write(path, path.relative_to(root).as_posix())
        z.writestr("manifest.json", json.dumps(manifest, indent=2))
    manifest["archive"] = dict(sha256=sha256_file(archive), bytes=archive.stat().st_size)
    write_json(output / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "restore", "check", "deps", "receipt"))
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--delete-by")
    parser.add_argument("--rights-confirmed", action="store_true")
    parser.add_argument("--not-test-or-holdout", action="store_true")
    parser.add_argument("--web", action="store_true")
    args = parser.parse_args()
    root = args.workspace.resolve()
    if args.action == "build":
        if args.output is None:
            parser.error("build requires --output")
        print(json.dumps(build(root, args.output.resolve())["archive"]))
    elif args.action == "restore":
        restore(root, args.archive)
    elif args.action == "deps":
        raise SystemExit(0 if dependencies(root) else 2)
    elif args.action == "check":
        check(root, web=args.web)
    else:
        if args.source is None or args.delete_by is None:
            parser.error("receipt requires --source and --delete-by")
        receipt(root, args.source.resolve(), args.delete_by,
                confirmed=args.rights_confirmed and args.not_test_or_holdout)


if __name__ == "__main__":
    main()
