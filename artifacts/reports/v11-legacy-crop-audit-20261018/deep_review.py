"""Worksheet: verify selected sources and render flagged source/native/input QA."""

import hashlib
import io
import json
import zipfile
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCRATCH = ROOT / "outputs/_scratch/v11-legacy-crop-audit-20261018"
PACKAGE = ROOT / "data/processed/pilot-b/pilot-b-20261017-v11"
ARCHIVE = ROOT / "archive/e004-v9-consolidation-20261013.zip"
ARCHIVE_SHA = "8883c176060c82b31c7436dea341867448204e157a20f111c3560eae389342b3"


def main():
    assert sha256_file(ARCHIVE) == ARCHIVE_SHA
    rows = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    notes = {}
    for line in (HERE / "visual-notes.psv").read_text(encoding="utf-8-sig").splitlines():
        b, c, labels, action, reason = line.split("|", 4)
        key = (int(b), int(c))
        assert key not in notes
        notes[key] = {"states": labels, "action": action, "reason": reason}
    assert len(notes) == len(rows) == 836
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
    flagged = []
    source_checks = []
    source_cache = {}
    with zipfile.ZipFile(ARCHIVE) as archive:
        inventory = json.loads(archive.read("manifest.json"))
        available = {r["sha256"] for r in inventory["files"]}
        for row in rows:
            source = row["source"]
            digest = source["image_sha256"]
            assert digest in available
            if digest not in source_cache:
                content = archive.read("blobs/" + digest)
                assert hashlib.sha256(content).hexdigest() == digest
                with Image.open(io.BytesIO(content)) as image:
                    image.load()
                    source_cache[digest] = image.convert("RGB")
            image = source_cache[digest]
            assert image.size == (source["image_width"], source["image_height"])
            context = row["crop"]["context_box"]
            xyxy = tuple(context[k] for k in ["xmin", "ymin", "xmax", "ymax"])
            with Image.open(PACKAGE / row["crop"]["crop_relpath"]) as crop:
                assert image.crop(xyxy).tobytes() == crop.convert("RGB").tobytes(), row["sample_id"]
            source_checks.append(
                {"sample_id": row["sample_id"], "source_sha256": digest, "roi_pixel_parity": True}
            )
            note = notes[(int(row["board"][6:9]), row["cell"])]
            if note["action"] not in {"inspect", "recrop"}:
                continue
            idx = len(flagged)
            flagged.append(
                {
                    "sample_id": row["sample_id"],
                    "board": f"deep-{idx // 6 + 1:03d}.jpg",
                    "cell": idx % 6 + 1,
                    "first_pass": note,
                }
            )
        # Release unneeded source images before rendering, while retaining selected ones.
        selected = {r["sample_id"]: r for r in rows}
        for start in range(0, len(flagged), 6):
            group = flagged[start : start + 6]
            board = Image.new("RGB", (1880, 1455), "#ddddee")
            draw = ImageDraw.Draw(board)
            for i, item in enumerate(group):
                row = selected[item["sample_id"]]
                x, y = i % 2 * 940, i // 2 * 485
                draw.rectangle((x, y, x + 938, y + 483), fill="white", outline="#333333")
                draw.text(
                    (x + 5, y + 5),
                    f"{i + 1:02d} {row['sample_id']}  ({row['board']}:{row['cell']})",
                    font=font,
                    fill="black",
                )
                source = source_cache[row["source"]["image_sha256"]].copy()
                pen = ImageDraw.Draw(source)
                for name, color in [("context_box", "orange"), ("person_box", "#00ff33")]:
                    box = row["crop"][name]
                    pen.rectangle(
                        tuple(box[k] for k in ["xmin", "ymin", "xmax", "ymax"]),
                        outline=color,
                        width=max(2, source.width // 250),
                    )
                scale = min(340 / source.width, 410 / source.height)
                source = source.resize(
                    (round(source.width * scale), round(source.height * scale)),
                    Image.Resampling.BILINEAR,
                )
                board.paste(
                    source, (x + (344 - source.width) // 2, y + 35 + (410 - source.height) // 2)
                )
                with Image.open(PACKAGE / row["crop"]["crop_relpath"]) as crop:
                    crop = crop.convert("RGB")
                    scale = min(350 / crop.width, 410 / crop.height)
                    enlarged = crop.resize(
                        (round(crop.width * scale), round(crop.height * scale)),
                        Image.Resampling.BILINEAR,
                    )
                    board.paste(
                        enlarged,
                        (
                            x + 350 + (350 - enlarged.width) // 2,
                            y + 35 + (410 - enlarged.height) // 2,
                        ),
                    )
                    board.paste(preview_input(crop, 224, (124, 116, 104)), (x + 710, y + 105))
                old = "/".join(s[0].upper() for s in row["current_states"])
                draw.text(
                    (x + 5, y + 458),
                    f"source: green anchor / orange context  |  native  | 224   old {old}",
                    font=small,
                    fill="black",
                )
            board.save(SCRATCH / group[0]["board"], quality=94, subsampling=0)
            print(group[0]["board"], flush=True)
    for name, value in [
        ("deep-index.json", flagged),
        (
            "source-validation.json",
            {
                "archive": ARCHIVE.relative_to(ROOT).as_posix(),
                "archive_sha256": ARCHIVE_SHA,
                "records": source_checks,
                "unique_sources": len(source_cache),
                "test_or_reserve_visual_access": False,
            },
        ),
    ]:
        (HERE / name).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(Counter(x["first_pass"]["action"] for x in flagged))


if __name__ == "__main__":
    main()
