"""Screen new video frames against non-test V11 sources for manual lineage review."""

import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.image_similarity import difference_hash
from ai_exam_monitoring.data.pilot_schema import read_records

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MEDIA = ROOT / "data/interim/dataset-release-20261020-v12"


def main():
    base = read_records(ROOT / "data/processed/pilot-b/pilot-b-20261017-v11/review-ledger.jsonl")
    roots = json.loads((HERE / "source-roots.json").read_text())
    protected = {r.source.image_sha256 for r in base if r.usage == "test"}
    old = {}
    for row in base:
        if row.source.image_sha256 in protected:
            continue
        item = old.setdefault(
            row.source.image_sha256,
            {
                "path": str(Path(roots[row.source.source_id]) / row.source.image_relpath),
                "ids": [],
                "roles": [],
                "groups": [],
            },
        )
        item["ids"].append(row.sample_id)
        item["roles"].append(row.usage)
        item["groups"].append(row.group.leakage_group_id if row.group else None)
    for item in old.values():
        with Image.open(item["path"]) as image:
            item["dhash"] = difference_hash(image.convert("RGB"))
    groups = defaultdict(list)
    all_nearest = []
    for path in sorted((MEDIA / "sources/youtube-crawl-20261018").glob("*/*.jpg")):
        with Image.open(path) as image:
            fingerprint = difference_hash(image.convert("RGB"))
        matches = sorted(old.items(), key=lambda kv: (fingerprint ^ kv[1]["dhash"]).bit_count())[:3]
        for digest, item in matches:
            pair = {
                "new": str(path.relative_to(ROOT)),
                "old": str(Path(item["path"]).relative_to(ROOT)),
                "distance": (fingerprint ^ item["dhash"]).bit_count(),
                "old_sha256": digest,
                "ids": item["ids"],
                "roles": item["roles"],
                "groups": item["groups"],
            }
            groups[path.parent.name].append(pair)
            all_nearest.append(pair)
    selected = []
    for group, candidates in groups.items():
        seen = set()
        for pair in sorted(candidates, key=lambda p: p["distance"]):
            if pair["old_sha256"] not in seen:
                seen.add(pair["old_sha256"])
                selected.append(dict(pair, video=group))
            if len(seen) == 3:
                break
    boards = MEDIA / "lineage-boards"
    boards.mkdir(exist_ok=True)
    for number, pair in enumerate(selected, 1):
        canvas = Image.new("RGB", (1200, 520), "white")
        draw = ImageDraw.Draw(canvas)
        draw.text(
            (5, 5),
            f"L{number:02} {pair['video']} distance={pair['distance']} "
            f"{pair['ids'][:3]} roles={sorted(set(pair['roles']))}",
            fill="black",
        )
        for side, key in enumerate(["new", "old"]):
            with Image.open(ROOT / pair[key]) as image:
                image = image.convert("RGB")
                image.thumbnail((590, 470))
                canvas.paste(image, (side * 600, 35))
        canvas.save(boards / f"L{number:02}.jpg", quality=95)
        pair["comparison_id"] = f"L{number:02}"
    (HERE / "lineage-screening.json").write_text(
        json.dumps(
            {
                "non_test_source_count": len(old),
                "protected_sources_excluded": len(protected),
                "nearest": all_nearest,
                "manual_queue": selected,
                "note": "Advisory hashes only; no independence assertion or automatic split.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print([(p["comparison_id"], p["video"], p["distance"], p["ids"][:2]) for p in selected])


if __name__ == "__main__":
    main()
