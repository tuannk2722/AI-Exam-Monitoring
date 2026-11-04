"""One-time retained-payload verification; no model inference."""
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(entry):
    name, value = entry
    path = ROOT / name
    assert path.stat().st_size == value["bytes"], name
    assert sha(path) == value["sha256"], name
    return name


protected = json.loads((REPORT / "protected-before.json").read_text(encoding="utf-8"))
with ThreadPoolExecutor(max_workers=8) as pool:
    for index, name in enumerate(pool.map(verify, protected.items())):
        if index % 5000 == 0:
            print("Protected verified:", index, flush=True)
manifest = json.loads((REPORT / "cleanup-manifest.json").read_text(encoding="utf-8"))
assert all(not (ROOT / row["path"]).exists() for row in manifest["delete"])
sizes = {}
logical, unique, identities = 0, 0, set()
for parent, dirs, files in os.walk(ROOT):
    for name in files:
        path = Path(parent) / name
        stat = path.stat()
        logical += stat.st_size
        part = path.relative_to(ROOT).parts[0]
        sizes[part] = sizes.get(part, 0) + stat.st_size
        key = (stat.st_dev, stat.st_ino)
        if key not in identities:
            unique += stat.st_size
            identities.add(key)
result = {
    "protected_files_verified": len(protected), "protected_status": "PASS",
    "deleted_files_absent": len(manifest["delete"]),
    "workspace_logical_bytes_after": logical,
    "workspace_unique_file_bytes_after": unique,
    "top_level_bytes_after": sizes,
    "note": "Logical/unique file bytes are not NTFS allocated clusters; disk free delta is separate.",
}
(REPORT / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
