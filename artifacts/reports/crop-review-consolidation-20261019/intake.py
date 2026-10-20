"""Snapshot owner review and build a lossless work queue; no visual decisions."""

import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.data.image_similarity import difference_hash

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MEDIA = ROOT / "data/interim/crop-review-consolidation-20261019"
OLD = ROOT / "artifacts/reports/v11-legacy-crop-audit-20261018"
YT = ROOT / "artifacts/reports/youtube-frame-audit-20261018"


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    snapshots = HERE / "owner-inputs"
    snapshots.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    pins = []
    sources = [
        (OLD / "r2/DECISIONS.md", "legacy-review.md"),
        (YT / "README.md", "youtube-review.md"),
    ]
    for source, name in sources:
        blob = source.read_bytes()
        dest = snapshots / name
        if dest.exists():
            assert dest.read_bytes() == blob, (
                "Owner input changed; preserve snapshot and create revision"
            )
        else:
            dest.write_bytes(blob)
        pins.append(
            {
                "source": str(source.relative_to(ROOT)),
                "snapshot": str(dest.relative_to(ROOT)),
                "sha256": sha(blob),
            }
        )
    decisions = json.loads((OLD / "r2/decisions.json").read_text(encoding="utf-8"))
    cohort = {
        r["sample_id"]: r for r in json.loads((OLD / "cohort.json").read_text(encoding="utf-8"))
    }
    legacy = {}
    for line_no, line in enumerate(
        (snapshots / "legacy-review.md").read_text(encoding="utf-8").splitlines(), 1
    ):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] in cohort:
            assert cells[0] not in legacy
            legacy[cells[0]] = {
                "line": line_no,
                "cells": cells,
                "owner_comments": cells[5:],
                "raw": line,
            }
    assert len(legacy) == len(decisions) == 836
    yt = json.loads((YT / "review-index.json").read_text(encoding="utf-8"))
    yt_ids = {r["candidate_id"] for r in yt}
    yt_comments = {}
    for line_no, line in enumerate(
        (snapshots / "youtube-review.md").read_text(encoding="utf-8").splitlines(), 1
    ):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells[0].startswith("Y") or len(cells) != 3:
            continue
        for sid in re.findall(r"Y\d{2}-A\d{2}-F\d{5}(?:-R\d{2})?", cells[0]):
            assert sid in yt_ids and sid not in yt_comments, sid
            yt_comments[sid] = {"line": line_no, "owner_comments": cells[1:], "raw": line}
    queue = []
    states = {"positive": "P", "negative": "N", "unknown": "U"}
    for d in decisions:
        sid = d["sample_id"]
        owner = legacy[sid]
        c = cohort[sid]
        comments = " | ".join(owner["owner_comments"]).strip(" |")
        queue.append(
            {
                "id": sid,
                "audit": "legacy836",
                "parent_action": d["action"],
                "parent_states": [states[s] for s in d["observed_states"]],
                "owner_review": owner,
                "owner_default_approval": not bool(comments),
                "work_status": "pending_visual_review",
                "crop_path": "data/processed/pilot-b/pilot-b-20261017-v11/"
                + c["crop"]["crop_relpath"],
                "source_preview_path": (
                    f"data/interim/v11-legacy-crop-audit-20261018/source/{sid}.jpg"
                ),
                "source_path": "data/interim/crop-review-consolidation-20261019/sources/"
                + c["source"]["image_sha256"]
                + ".bin",
                "source_sha256": c["source"]["image_sha256"],
                "crop_sha256": c["crop"]["crop_sha256"],
                "context_box": c["crop"]["context_box"],
                "person_box": c["crop"]["person_box"],
                "group_id": c["group_id"],
            }
        )
    for r in yt:
        sid = r["candidate_id"]
        queue.append(
            {
                "id": sid,
                "audit": "youtube71",
                "parent_action": "keep",
                "parent_states": r["draft_states"],
                "owner_review": yt_comments.get(sid),
                "owner_default_approval": sid not in yt_comments,
                "work_status": "pending_visual_review",
                **{
                    k: r[k]
                    for k in [
                        "crop_path",
                        "source_path",
                        "crop_sha256",
                        "context_xyxy",
                        "person_xyxy",
                    ]
                },
            }
        )
    source_dir = MEDIA / "sources"
    source_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(ROOT / "archive/e004-v9-consolidation-20261013.zip") as z:
        for row in queue:
            if row["audit"] != "legacy836":
                continue
            dest = ROOT / row["source_path"]
            if not dest.exists():
                content = z.read("blobs/" + row["source_sha256"])
                assert sha(content) == row["source_sha256"]
                dest.write_bytes(content)
            assert sha(dest.read_bytes()) == row["source_sha256"]
    dump(HERE / "intake-ledger.json", queue)
    archive = Path("C:/Users/OS/Downloads/additional.zip")
    blob = archive.read_bytes()
    pins.append({"source": str(archive), "sha256": sha(blob), "bytes": len(blob)})
    marks = MEDIA / "additional"
    marks.mkdir(exist_ok=True)
    additional = []
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for info in z.infolist():
            if info.is_dir():
                continue
            assert info.filename.endswith(".jpg")
            dest = marks / Path(info.filename).name
            b = z.read(info)
            if dest.exists():
                assert dest.read_bytes() == b
            else:
                dest.write_bytes(b)
            with Image.open(dest) as im:
                im.load()
                additional.append(
                    {
                        "member": info.filename,
                        "path": str(dest.relative_to(ROOT)),
                        "sha256": sha(b),
                        "size": list(im.size),
                        "status": "pending_visual_mapping",
                    }
                )
    dump(HERE / "additional-inventory.json", additional)
    dump(HERE / "input-pins.json", pins)
    fingerprints = []
    for row in queue:
        path = ROOT / row["crop_path"]
        assert sha(path.read_bytes()) == row["crop_sha256"], row["id"]
        with Image.open(path) as im:
            rgb = im.convert("RGB")
            fingerprints.append(
                {
                    "id": row["id"],
                    "sha256": row["crop_sha256"],
                    "size": list(rgb.size),
                    "rgb_sha256": sha(rgb.tobytes()),
                    "dhash": difference_hash(rgb),
                }
            )
    pairs = []
    for i, a in enumerate(fingerprints):
        for b in fingerprints[i + 1 :]:
            distance = (a["dhash"] ^ b["dhash"]).bit_count()
            exact = a["size"] == b["size"] and a["rgb_sha256"] == b["rgb_sha256"]
            if distance <= 8 or exact:
                pairs.append(
                    {
                        "a": a["id"],
                        "b": b["id"],
                        "distance": distance,
                        "exact_rgb": exact,
                        "decision": "pending_visual_review",
                    }
                )
    dump(HERE / "fingerprints.json", fingerprints)
    dump(
        HERE / "duplicate-triage.json",
        sorted(pairs, key=lambda r: (not r["exact_rgb"], r["distance"], r["a"], r["b"])),
    )
    summary = {
        "records": len(queue),
        "legacy_comments": sum(
            bool(" | ".join(v["owner_comments"]).strip(" |")) for v in legacy.values()
        ),
        "youtube_comments": len(yt_comments),
        "additional_images": len(additional),
        "duplicate_pairs_to_review": len(pairs),
        "exact_rgb_pairs": sum(p["exact_rgb"] for p in pairs),
        "parent_actions": dict(Counter(q["parent_action"] for q in queue)),
        "status": "intake_only_not_visual_completion",
    }
    dump(HERE / "intake-summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
