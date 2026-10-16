"""Inspect this supplied bundle without trusting or executing its annotations."""

import csv
import hashlib
import io
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFont, ImageOps

from ai_exam_monitoring.data.crop_bundle_audit import image_fingerprint, safe_member

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
ID = REPORT.name
RAW = ROOT / "data/raw" / ID
DATA = ROOT / "data/interim" / ID
OUT = ROOT / "outputs" / ID


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path):
    return path.relative_to(ROOT).as_posix()


def boards(rows, field, directory, width, height, count=12):
    target = OUT / directory
    target.mkdir(parents=True, exist_ok=True)
    cols = 4 if count == 12 else 2
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)
    for start in range(0, len(rows), count):
        page = Image.new(
            "RGB", (cols * width, ((count + cols - 1) // cols) * (height + 34)), "white"
        )
        draw = ImageDraw.Draw(page)
        for j, row in enumerate(rows[start : start + count]):
            x, y = (j % cols) * width, (j // cols) * (height + 34)
            im = ImageOps.contain(Image.open(ROOT / row[field]).convert("RGB"), (width, height))
            page.paste(im, (x + (width - im.width) // 2, y + 34))
            draw.text((x + 3, y + 3), row["id"], fill="black", font=font)
            draw.text((x + 3, y + 18), row.get("caption", ""), fill="black", font=font)
        page.save(target / f"{start // count + 1:02}.jpg", quality=94)


def main():
    if (REPORT / "input-pins.json").exists():
        raise RuntimeError("Input pinned; create a new revision.")
    for path in (RAW, DATA, OUT):
        path.mkdir(parents=True, exist_ok=True)
    names = [
        "crop_metadata_review.zip",
        "crop_review_candidates.zip",
        "crop_main_part_01_A_source.zip",
        "crop_main_part_02_B_view_A.zip",
        "crop_main_part_03_B_view_B.zip",
        "crop_main_part_04_B_view_C.zip",
        "crop_main_part_05_B_view_D.zip",
    ]
    sources = [Path("C:/Users/OS/Downloads") / n for n in names]
    sources.append(
        Path("D:/dataset-foundry-starter/exports/new-yt-videos-run-001-accepted-frames.zip")
    )
    archives = []
    for source in sources:
        dest = RAW / source.name
        shutil.copyfile(source, dest)
        assert sha(dest) == sha(source)
        with ZipFile(dest) as archive:
            assert archive.testzip() is None
            names_seen = set()
            for info in archive.infolist():
                safe_member(info.filename)
                path = info.filename
                assert path.casefold() not in names_seen
                names_seen.add(path.casefold())
                if info.is_dir():
                    continue
                target = DATA / dest.stem / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(info))
            archives.append(
                dict(
                    name=dest.name,
                    path=rel(dest),
                    sha256=sha(dest),
                    members=len(archive.infolist()),
                    crc="PASS",
                )
            )
    metadata = DATA / "crop_metadata_review"
    rows = [
        json.loads(line)
        for line in (metadata / "manifest.jsonl").read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    frame_meta = list(
        csv.DictReader(
            io.StringIO((metadata / "frame_inventory.csv").read_text(encoding="utf-8-sig"))
        )
    )
    frame_lookup = {(r["source_id"], r["frame_name"]): r for r in frame_meta}
    crops = []
    crop_lookup = defaultdict(list)
    for part in names[1:]:
        for path in (DATA / Path(part).stem / "crops").rglob("*.jpg"):
            crop_lookup[path.relative_to(DATA / Path(part).stem).as_posix()].append(path)
    assert len(crop_lookup) == len(rows) == 80
    for i, row in enumerate(rows, 1):
        matches = crop_lookup[row["crop_path"]]
        assert len(matches) == 1
        crop = matches[0]
        source = (
            DATA
            / "new-yt-videos-run-001-accepted-frames/derived"
            / row["video_id"]
            / row["frame_name"]
        )
        fp = image_fingerprint(crop.read_bytes())
        sfp = image_fingerprint(source.read_bytes())
        box = [int(row["crop_" + axis]) for axis in ("x0", "y0", "x1", "y1")]
        assert 0 <= box[0] < box[2] <= sfp["width"] and 0 <= box[1] < box[3] <= sfp["height"]
        assert (int(row["original_width"]), int(row["original_height"])) == (
            sfp["width"],
            sfp["height"],
        )
        rec = dict(
            id=f"NB-{i:04}",
            source_group=row["source_group"],
            view=row["camera_view"],
            anchor_id=row["anchor_id"],
            frame_num=int(row["frame_index"]),
            source=rel(source),
            source_sha256=sfp["sha256"],
            crop=rel(crop),
            crop_sha256=fp["sha256"],
            input=rel(crop),
            context_xyxy=box,
            fingerprint=fp,
            caption=row["anchor_id"][:29],
            supplied_metadata=row,
            draft_labels=None,
            status="pending_visual_review",
            assigned_split=None,
            canonical_targets=[None, None],
            canonical_mask=[0, 0],
            training_ready=False,
        )
        crops.append(rec)
    frames = []
    for i, path in enumerate(
        sorted((DATA / "new-yt-videos-run-001-accepted-frames/derived").rglob("*.jpg")), 1
    ):
        fp = image_fingerprint(path.read_bytes())
        meta = frame_lookup.get((path.parent.name, path.name), {})
        related = [r["id"] for r in crops if r["source"] == rel(path)]
        frames.append(
            dict(
                id=f"NF-{i:03}",
                source=rel(path),
                source_sha256=fp["sha256"],
                parent_id=path.parent.name,
                frame_num=int(path.stem.split("_")[1]),
                source_group=meta.get("source_group"),
                view_hint=meta.get("view_group"),
                caption=path.parent.name[:7] + " " + path.stem,
                fingerprint=fp,
                supplied_crop_ids=related,
                visual_status="pending",
            )
        )
    write(
        REPORT / "input-pins.json",
        dict(
            archives=archives,
            rights="owner confirmed full rights in task request; no re-query",
            labels="all supplied annotations unreviewed",
        ),
    )
    write(REPORT / "crop-inventory.json", crops)
    write(REPORT / "frame-inventory.json", frames)
    for group in ("A", "B"):
        boards(
            [r for r in crops if r["source_group"] == group], "input", "crops-" + group, 252, 224
        )
        boards(
            [r for r in frames if r["source_group"] == group],
            "source",
            "frames-" + group,
            960,
            540,
            4,
        )
    write(
        REPORT / "structural-summary.json",
        dict(
            crops=len(crops),
            frames=len(frames),
            crop_groups=dict(Counter(r["source_group"] for r in crops)),
            frame_groups=dict(Counter(r["source_group"] for r in frames)),
            crop_views=dict(Counter(r["view"] for r in crops)),
            orphan_frames_metadata=sum(r["source_group"] is None for r in frames),
            crop_dimensions=dict(
                Counter(str((r["fingerprint"]["width"], r["fingerprint"]["height"])) for r in crops)
            ),
        ),
    )
    print((REPORT / "structural-summary.json").read_text())


if __name__ == "__main__":
    main()
