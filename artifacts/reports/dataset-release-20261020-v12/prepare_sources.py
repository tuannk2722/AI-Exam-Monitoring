"""Materialize exact pinned source bytes; protected sources are integrity-only."""

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
DEST = ROOT / "data/interim/dataset-release-20261020-v12/sources"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    base = read_records(ROOT / "data/processed/pilot-b/pilot-b-20261017-v11/review-ledger.jsonl")
    backup = read(HERE.parent / "dataset-release-20261017/backup-receipt.json")
    sources = [backup, backup["source_dependency"]]
    archives = []
    blobs = {}
    for pin in sources:
        path = ROOT / pin["archive"]
        assert sha256_file(path) == pin["sha256"]
        archive = zipfile.ZipFile(path)
        archives.append(archive)
        manifest = json.loads(archive.read("manifest.json"))
        for entry in manifest["files"]:
            blobs.setdefault(entry["sha256"], archive)
    copied = []
    try:
        for row in base:
            for rel, digest in [
                (row.source.image_relpath, row.source.image_sha256),
                (row.source.label_relpath, row.source.label_sha256),
            ]:
                if rel is None:
                    continue
                target = (DEST / row.source.source_id / rel).resolve()
                assert target.is_relative_to(DEST.resolve())
                if target.exists():
                    assert sha256_file(target) == digest
                    continue
                assert digest in blobs, (row.sample_id, rel, digest)
                payload = blobs[digest].read("blobs/" + digest)
                assert hashlib.sha256(payload).hexdigest() == digest
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
                copied.append({"path": target.relative_to(ROOT).as_posix(), "sha256": digest})
    finally:
        for archive in archives:
            archive.close()
    youtube_root = ROOT / "data/interim/youtube-frame-audit-20261018/frames"
    for group in youtube_root.iterdir():
        if not group.is_dir():
            continue
        for source in group.glob("*.jpg"):
            target = DEST / "youtube-crawl-20261018" / group.name / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert sha256_file(target) == sha256_file(source)
            else:
                shutil.copyfile(source, target)
    roots = {r.source.source_id: str(DEST / r.source.source_id) for r in base}
    roots["youtube-crawl-20261018"] = str(DEST / "youtube-crawl-20261018")
    (HERE / "source-roots.json").write_text(json.dumps(roots, indent=2), encoding="utf-8")
    (HERE / "source-restore.json").write_text(
        json.dumps(
            {
                "archives": sources,
                "files_copied": copied,
                "scope": (
                    "Exact source/label bytes for release; "
                    "test integrity copy only, no visual review."
                ),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("Source roots ready:", len(roots), "restored files:", len(copied))


if __name__ == "__main__":
    main()
