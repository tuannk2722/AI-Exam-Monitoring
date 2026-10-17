"""Worksheet audit nguồn; geometry/review do agent quan sát, không auto acceptance."""

import collections
import hashlib
import io
import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.image_similarity import difference_hash

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "artifacts/reports/frame-crop-audit-20261016"
DATA = ROOT / "data/interim/frame-crop-audit-20261016"
BOARDS = DATA / "review/boards"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare():
    BOARDS.mkdir(parents=True, exist_ok=True)
    rows, archives, groups, boards = [], [], [], []
    for part in range(1, 6):
        path = Path(f"C:/Users/OS/Downloads/frames_part_{part:02}.zip")
        archives.append(
            {"name": path.name, "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size}
        )
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            names = z.namelist()
            assert len(names) == len(set(names))
            for member in sorted(names):
                p = Path(member)
                assert not p.is_absolute() and ".." not in p.parts and p.suffix.lower() == ".jpg"
                folder = p.parent.name
                group = next((g for g in groups if g["folder"] == folder), None)
                if group is None:
                    group = {
                        "group": f"G{len(groups) + 1:02}",
                        "folder": folder,
                        "part": part,
                        "frames": [],
                    }
                    groups.append(group)
                blob = z.read(member)
                with Image.open(io.BytesIO(blob)) as src:
                    src.load()
                    im = src.convert("RGB")
                fid = f"P{part:02}-{group['group']}-F{int(p.stem.split('_')[-1]):05}"
                dest = DATA / "frames" / group["group"] / p.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    assert dest.read_bytes() == blob
                else:
                    dest.write_bytes(blob)
                row = {
                    "frame_id": fid,
                    "part": part,
                    "group": group["group"],
                    "folder": folder,
                    "member": member,
                    "sha256": digest(blob),
                    "rgb_sha256": digest(im.tobytes()),
                    "width": im.width,
                    "height": im.height,
                    "dhash": f"{difference_hash(im):016x}",
                    "path": dest.relative_to(ROOT).as_posix(),
                }
                rows.append(row)
                group["frames"].append(fid)
    by_id = {r["frame_id"]: r for r in rows}
    for group in groups:
        for offset in range(0, len(group["frames"]), 9):
            ids = group["frames"][offset : offset + 9]
            canvas = Image.new("RGB", (1920, 390 * ((len(ids) + 2) // 3)), "white")
            draw = ImageDraw.Draw(canvas)
            for j, fid in enumerate(ids):
                r = by_id[fid]
                im = Image.open(ROOT / r["path"])
                im.thumbnail((640, 360))
                x, y = (j % 3) * 640, (j // 3) * 390
                canvas.paste(im, (x, y + 26))
                draw.text((x + 8, y + 5), fid, fill="black")
            dest = BOARDS / f"{group['group']}-board-{offset // 9 + 1:02}.jpg"
            canvas.save(dest, quality=95)
            boards.append({"path": dest.relative_to(ROOT).as_posix(), "frame_ids": ids})
    duplicates = {}
    for field in ["sha256", "rgb_sha256"]:
        d = collections.defaultdict(list)
        for r in rows:
            d[r[field]].append(r["frame_id"])
        duplicates[field] = [v for v in d.values() if len(v) > 1]
    result = {
        "archives": archives,
        "frames": rows,
        "groups": groups,
        "boards": boards,
        "exact_duplicates": duplicates,
        "rights": "Owner xác nhận toàn quyền sử dụng trong yêu cầu ngày 16/10/2026; audit/crop local.",
        "group_status": "Thư mục nguồn chỉ là nhóm review, chưa xác nhận room/session hoặc independence.",
    }
    (REPORT / "inventory.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "frames": len(rows),
                "groups": len(groups),
                "boards": len(boards),
                "sizes": dict(collections.Counter(f"{r['width']}x{r['height']}" for r in rows)),
                "exact_duplicates": duplicates,
                "groups_summary": [
                    {k: v for k, v in g.items() if k != "frames"} | {"count": len(g["frames"])}
                    for g in groups
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    prepare()
