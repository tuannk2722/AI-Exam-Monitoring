"""Build a private, allowlisted portable campaign bundle; never uploads by itself."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .adaptation_config import FilePin, local_path
from .artifacts import code_identity, write_json
from .representation_prepare import pin, read_pin


def build(design_path: Path, root: Path, output: Path) -> dict[str, Any]:
    root, output = root.resolve(), output.resolve()
    if output.exists() or not output.is_relative_to(root / "outputs"):
        raise DataContractError("Bundle requires a new output path under outputs")
    design = json.loads(design_path.read_text(encoding="utf-8"))
    authority = read_pin(root, design["authorization"])
    if authority.get("cloud_upload_authorized") is not True:
        raise DataContractError("Cloud upload scope missing")
    pointer = read_pin(root, design["dataset_pointer"])
    paths = {design_path.resolve(), root / "pyproject.toml", root / "README.md",
             root / "requirements/classifier-colab.txt"}
    paths.update((root / "src/ai_exam_monitoring").rglob("*.py"))
    paths.update(p for p in local_path(root, pointer["package"]).rglob("*") if p.is_file())
    for key in ("authorization", "proposal", "dataset_pointer", "allocation", "provenance",
                "release_approval", "template"):
        paths.add(FilePin(**design[key]).verify(root))
    for encoder in design["pretrained"].values():
        for value in encoder.values():
            paths.add(FilePin(**value).verify(root))
    for value in design.get("supporting_inputs", []):
        paths.add(FilePin(**value).verify(root))
    files = {}
    for path in sorted(paths):
        if not path.is_file() or not path.resolve().is_relative_to(root) or path.is_symlink():
            raise DataContractError("Missing/outside/symlink bundle member")
        files[path.relative_to(root).as_posix()] = sha256_file(path)
    manifest = {"schema_version": "private-colab-bundle-v1", "design": pin(root, design_path),
                "files": files, "code_sha256": code_identity()["sha256"],
                "dataset_payload_sha256": pointer["payload_sha256"],
                "visibility": "private", "cloud_authorization": design["authorization"]}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as archive:
        for name in files:
            archive.write(root / name, name)
        archive.writestr("bundle-manifest.json", json.dumps(manifest, indent=2))
    receipt = {"bundle": pin(root, output), "bytes": output.stat().st_size,
               "manifest": manifest, "upload_status": "not_uploaded"}
    write_json(output.with_suffix(".json"), receipt)
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = build(args.design, args.workspace, args.output)
    print(json.dumps({k: receipt[k] for k in ("bundle", "bytes", "upload_status")}))


if __name__ == "__main__":
    main()
