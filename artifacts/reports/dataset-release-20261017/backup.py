"""Local V11 snapshot using the repository history API; no remote upload."""

import json
import subprocess
from pathlib import Path

from ai_exam_monitoring.common.history import create, restore, verify
from ai_exam_monitoring.common.provenance import sha256_file

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
NAME = "dataset-release-20261017-v11"
ARCHIVE = ROOT / "archive" / (NAME + ".zip")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def main():
    assert not ARCHIVE.exists(), "Never reseal an existing archive"
    assert read(HERE / "package-validation.json")["status"] == "PASS"
    paths = set()
    folders = [
        ROOT / read(HERE / "package-pointers.json")["package"],
        HERE,
        HERE.parent / "train-val-plan-20261017",
        HERE.parent / "frame-crop-audit-20261016",
        HERE.parent / "frame-crop-additional-20261017",
        ROOT / "data/interim/frame-crop-audit-20261016/frames",
        ROOT / "src",
        ROOT / "tests",
        ROOT / "requirements",
    ]
    for folder in folders:
        for p in folder.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                paths.add(p.relative_to(ROOT).as_posix())
    for r in read(HERE / "new-crop-provenance.json"):
        paths.update((r["source"], r["crop"]))
    for r in read(HERE.parent / "E004-accepted-coverage-20261016/accepted-ledger.json"):
        paths.add(r["source"])
    paths.update(
        [
            "configs/datasets/pilot-b-20261017-v11.json",
            "pyproject.toml",
            "artifacts/reports/E004-accepted-coverage-20261016/accepted-ledger.json",
        ]
    )
    manifest = create(
        ROOT, ARCHIVE, paths, name=NAME, progress=lambda n: print("Archived", n, flush=True)
    )
    digest = sha256_file(ARCHIVE)
    verify(ARCHIVE, expected_sha256=digest)
    destination = Path(
        "\\\\?\\" + str(ROOT / "outputs/_scratch/dataset-release-20261017/backup-restore")
    )
    assert not destination.exists()
    count = restore(ARCHIVE, destination, expected_sha256=digest)
    assert count == len(manifest.files)
    for entry in manifest.files:
        assert sha256_file(destination / entry.path) == entry.sha256
    subprocess.run([str(ROOT / ".venv/Scripts/dvc.exe"), "add", str(ARCHIVE)], cwd=ROOT, check=True)
    receipt = {
        "archive": ARCHIVE.relative_to(ROOT).as_posix(),
        "sha256": digest,
        "files": len(manifest.files),
        "unique_blobs": len({r.sha256 for r in manifest.files}),
        "original_bytes": sum(r.size for r in manifest.files),
        "archive_bytes": ARCHIVE.stat().st_size,
        "byte_exact_restore": "PASS",
        "restored_files": count,
        "scope": "local_only; same drive; no upload",
        "source_dependency": read(HERE / "source-restore-receipt.json"),
        "note": (
            "New release/crops/frames and 345 parent frame sources included. H"
            "istorical source cache remains in retained pinned dependency arch"
            "ive. Git supplies documentation and receipts created after snapsh"
            "ot."
        ),
    }
    write(HERE / "backup-receipt.json", receipt)
    index = ROOT / "archive/index.json"
    registry = read(index)
    assert not any(r["name"] == NAME for r in registry["bundles"])
    registry["bundles"].append(
        {
            "name": NAME,
            **{
                k: receipt[k]
                for k in ["sha256", "files", "unique_blobs", "original_bytes", "archive_bytes"]
            },
            "path": receipt["archive"],
            "scope": "local_only",
            "owner_authorization": (
                "Owner requested V11 release and project lifecycle; local preservation only."
            ),
            "validation": {
                "byte_exact_restore": "PASS",
                "restored_files": count,
                "receipt": (HERE / "backup-receipt.json").relative_to(ROOT).as_posix(),
            },
        }
    )
    write(index, registry)
    print("Backup and byte-exact restore PASS", flush=True)


if __name__ == "__main__":
    main()
