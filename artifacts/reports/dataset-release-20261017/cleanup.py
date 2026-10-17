"""Remove only inventoried task scratch/cache after verifying retained payloads."""

import json
import shutil
from pathlib import Path

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import verify_payload

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def main():
    assert not (HERE / "cleanup-receipt.json").exists(), "Do not repeat a closed cleanup"
    backup = json.loads((HERE / "backup-receipt.json").read_text(encoding="utf8"))
    assert backup["byte_exact_restore"] == "PASS"
    assert sha256_file(ROOT / backup["archive"]) == backup["sha256"]
    package = ROOT / "data/processed/pilot-b/pilot-b-20261017-v11"
    parent = ROOT / "data/processed/e004/E004-c345-development-20261016"
    for folder in (package, parent):
        verify_payload(folder)
    roots = [ROOT / "outputs/_scratch/dataset-release-20261017"]
    for relative in ["src", "tests", "scripts", "artifacts/reports/dataset-release-20261017"]:
        roots.extend((ROOT / relative).rglob("__pycache__"))
    roots.extend(
        ROOT / name
        for name in [".ruff_cache", ".pytest_cache", ".mypy_cache"]
        if (ROOT / name).exists()
    )
    roots = sorted({p.resolve() for p in roots if p.exists()}, key=str)
    for p in roots:
        assert p.is_relative_to(ROOT.resolve()) and p != ROOT.resolve()
        assert p.name in {
            "__pycache__",
            ".ruff_cache",
            ".pytest_cache",
            ".mypy_cache",
            "dataset-release-20261017",
        }
    inventory = []
    for folder in roots:
        for p in folder.rglob("*"):
            if p.is_file():
                inventory.append(
                    {
                        "path": p.relative_to(ROOT).as_posix(),
                        "sha256": sha256_file(p),
                        "bytes": p.stat().st_size,
                    }
                )
    manifest = HERE / "cleanup-manifest.json"
    manifest.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf8")
    print(
        "Cleanup dry-run:",
        len(inventory),
        "files",
        sum(r["bytes"] for r in inventory),
        "bytes",
        flush=True,
    )
    for folder in roots:
        shutil.rmtree("\\\\?\\" + str(folder))
    for folder in (package, parent):
        verify_payload(folder)
    receipt = {
        "status": "PASS",
        "exact_inventory": manifest.relative_to(ROOT).as_posix(),
        "inventory_sha256": sha256_file(manifest),
        "removed_roots": [p.relative_to(ROOT).as_posix() for p in roots],
        "files": len(inventory),
        "bytes": sum(r["bytes"] for r in inventory),
        "protected_parent_and_release_payload_before_after": "PASS",
        "accepted_inputs_retired": False,
        "backup_retained": backup["archive"],
    }
    (HERE / "cleanup-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf8"
    )
    print("Cleanup PASS", flush=True)


if __name__ == "__main__":
    main()
