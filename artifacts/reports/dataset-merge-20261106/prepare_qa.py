"""Worksheet intake for the owner-authorized 2026-11-06 crop review.

No labels are inferred here. Filename/README decisions are inputs, not QA results.
Similarity is review triage and never creates a leakage group or split.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.image_similarity import difference_hash
from ai_exam_monitoring.data.pilot_schema import read_records
from ai_exam_monitoring.data.source_review import preview_input


ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
BATCH = ROOT / "data/interim/dataset-merge-20261106"
SCRATCH = ROOT / "outputs/_scratch/dataset-merge-20261106"
PARENT = ROOT / "data/processed/pilot-b/pilot-b-20261024-v14"
OLD_BATCH = ROOT / "data/interim/accepted-frames-crops-20261105"


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def features(path: Path) -> dict:
    with Image.open(path) as image:
        image.load()
        rgb = image.convert("RGB")
        return {
            "sha256": sha256_file(path),
            "rgb_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(),
            "size": list(rgb.size), "format": image.format,
            "dhash": difference_hash(rgb),
        }


def boards(rows: list[dict], prefix: str) -> None:
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
    for start in range(0, len(rows), 12):
        subset = rows[start:start + 12]
        sheet = Image.new("RGB", (4 * 352, 3 * 418), "#eeeeee")
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(subset):
            x, y = (i % 4) * 352, (i // 4) * 418
            with Image.open(ROOT / row["path"]) as original:
                image = preview_input(original.convert("RGB"), 336, (124, 116, 104))
            sheet.paste(image, (x + 8, y + 4))
            name = row["original_name"]
            text = f'{row["id"]} {row["owner_label"]} {row["size"]}\n'
            text += "\n".join(name[j:j + 37] for j in range(0, len(name), 37))
            draw.text((x + 8, y + 343), text, fill="black", font=font)
        sheet.save(SCRATCH / f"{prefix}-{start // 12 + 1:02d}.jpg", quality=95)


def main() -> None:
    if BATCH.exists() or (REPORT / "inventory.json").exists():
        raise RuntimeError("Intake already exists; do not overwrite reviewed inputs")
    (BATCH / "imports").mkdir(parents=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    readme = ROOT / "artifacts/reports/accepted-frames-crops-20261105/README.md"
    decisions = {}
    mentions = []
    for line in readme.read_text(encoding="utf-8").splitlines():
        if "| include " not in line:
            continue
        cells = line.split("|")
        label = cells[2].strip().split()[-1].replace("/", "")
        for crop_id in re.findall(r"S\d{2}-F\d{5}-P\d{2}", cells[1]):
            if crop_id in decisions and decisions[crop_id] != label:
                raise RuntimeError(f"Conflicting README decisions: {crop_id}")
            decisions[crop_id] = label
            mentions.append(crop_id)
    geometry = json.loads((OLD_BATCH / "manifest.json").read_text(encoding="utf-8"))
    assert not set(decisions) - {r["crop_id"] for r in geometry}
    selected = []
    for row in geometry:
        if row["crop_id"] not in decisions:
            continue
        path = OLD_BATCH / row["crop_path"]
        info = features(path)
        assert info["sha256"] == row["crop_sha256"]
        selected.append({
            "id": row["crop_id"], "kind": "reviewed_native",
            "original_name": path.name, "owner_label": decisions[row["crop_id"]],
            "path": path.relative_to(ROOT).as_posix(), **info,
        })
    imports = []
    files = sorted(Path("C:/Users/OS/Downloads/temp").iterdir())
    for i, file in enumerate(files, 1):
        match = re.fullmatch(r"(.+)_([NPU]{2})\.(png|jpg|jpeg)", file.name, re.I)
        if not file.is_file() or match is None:
            raise RuntimeError(f"Unexpected input: {file.name}")
        crop_id = f"M15-N{i:03d}"
        output = BATCH / "imports" / f"{crop_id}{file.suffix.lower()}"
        shutil.copyfile(file, output)
        info = features(output)
        assert info["sha256"] == sha256_file(file)
        imports.append({
            "id": crop_id, "kind": "owner_import",
            "original_name": file.name, "owner_label": match[2].upper(),
            "path": output.relative_to(ROOT).as_posix(), **info,
        })
    parent = []
    for record in read_records(PARENT / "manifest.jsonl"):
        assert record.crop is not None
        path = PARENT / record.crop.crop_relpath
        info = features(path)
        assert info["sha256"] == record.crop.crop_sha256
        parent.append({
            "id": record.sample_id, "kind": "parent", "split": record.split,
            "group": record.group.leakage_group_id,
            "path": path.relative_to(ROOT).as_posix(), **info,
        })
    all_rows = imports + selected + parent
    duplicate_sets = {}
    for key in ("sha256", "rgb_sha256"):
        clusters = defaultdict(list)
        for row in all_rows:
            clusters[(str(row["size"]), row[key])].append(row["id"])
        duplicate_sets[key] = [v for v in clusters.values() if len(v) > 1]
    nearest = []
    for query in imports + selected:
        candidates = []
        for kind, pool in (("parent", parent), ("new", imports + selected)):
            rank = sorted(
                ((query["dhash"] ^ r["dhash"]).bit_count(), r["id"])
                for r in pool if r["id"] != query["id"]
            )[:5]
            candidates.extend({"id": sid, "distance": d, "kind": kind} for d, sid in rank)
        nearest.append({"id": query["id"], "nearest": candidates})
    inventory = {
        "readme_sha256": sha256_file(readme), "mentions": len(mentions),
        "repeated_mentions": {k: n for k, n in Counter(mentions).items() if n > 1},
        "native_included": selected,
        "native_excluded": sorted(r["crop_id"] for r in geometry if r["crop_id"] not in decisions),
        "imports": imports, "parent": parent,
        "owner_label_counts": dict(Counter(r["owner_label"] for r in imports + selected)),
        "exact_duplicates": duplicate_sets,
        "semantics": "V12-RECONCILE-PHONE-20261023",
        "status": "intake_only_qa_pending_no_split",
    }
    save_json(REPORT / "inventory.json", inventory)
    save_json(REPORT / "similarity-triage.json", nearest)
    boards(imports, "imports")
    boards(selected, "native")
    print(json.dumps({
        "imports": len(imports), "native": len(selected), "excluded": len(inventory["native_excluded"]),
        "label_counts": inventory["owner_label_counts"], "exact_duplicates": duplicate_sets,
        "boards": len(list(SCRATCH.glob("*.jpg"))),
    }, indent=2))


if __name__ == "__main__":
    main()
