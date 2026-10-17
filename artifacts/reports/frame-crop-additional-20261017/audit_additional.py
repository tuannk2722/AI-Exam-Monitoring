import hashlib
import json
import re
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

R = Path.cwd()
P = R / "artifacts/reports/frame-crop-additional-20261017"
OUTPUT = R / "data/interim/frame-crop-additional-20261017"
(OUTPUT / "marked").mkdir(exist_ok=True)
(OUTPUT / "boards").mkdir(exist_ok=True)
zpath = Path(r"C:\Users\OS\Downloads\additional.zip")
z = zipfile.ZipFile(zpath)
assert z.testzip() is None
inv = json.loads(
    (R / "artifacts/reports/frame-crop-audit-20261016/inventory.json").read_text(encoding="utf-8")
)
sources = inv["frames"]
arr = np.array(
    [
        np.asarray(Image.open(R / s["path"]).convert("RGB").resize((64, 36)), dtype=np.float32)
        for s in sources
    ]
)
rows = []
for member in z.infolist():
    if member.is_dir():
        continue
    name = Path(member.filename).name
    blob = z.read(member)
    dst = OUTPUT / "marked" / name
    if dst.exists():
        assert dst.read_bytes() == blob
    else:
        dst.write_bytes(blob)
    im = Image.open(dst).convert("RGB")
    a = np.asarray(im.resize((64, 36)), dtype=np.float32)
    delta = np.mean(np.abs(arr - a), axis=3).reshape(len(sources), -1)
    score = np.mean(np.sort(delta, axis=1)[:, : int(delta.shape[1] * 0.8)], axis=1)
    idx = np.argsort(score)[:3]
    rows.append(
        {
            "member": member.filename,
            "marked_path": dst.relative_to(R).as_posix(),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "size": list(im.size),
            "owner_group": int(name.split("frame")[0]),
            "frame_number": int(re.search(r"frame_(\d+)", name)[1]),
            "matches": [
                {
                    "group": sources[int(i)]["group"],
                    "frame_id": sources[int(i)]["frame_id"],
                    "source_path": sources[int(i)]["path"],
                    "source_sha256": sources[int(i)]["sha256"],
                    "score": round(float(score[i]), 4),
                }
                for i in idx
            ],
        }
    )
rows.sort(key=lambda r: (r["owner_group"], r["frame_number"]))
for group in sorted(set(r["owner_group"] for r in rows)):
    batch = [r for r in rows if r["owner_group"] == group]
    for start in range(0, len(batch), 6):
        part = batch[start : start + 6]
        can = Image.new("RGB", (1280, 390 * ((len(part) + 1) // 2)), "#eee")
        d = ImageDraw.Draw(can)
        for j, r in enumerate(part):
            x = j % 2 * 640
            y = j // 2 * 390
            im = Image.open(R / r["marked_path"])
            im.thumbnail((640, 360))
            can.paste(im, (x, y + 27))
            d.text(
                (x + 5, y + 5),
                Path(r["member"]).name
                + " -> "
                + r["matches"][0]["frame_id"]
                + " score "
                + str(r["matches"][0]["score"]),
                fill="black",
            )
        can.save(OUTPUT / "boards" / f"M{group:02}-{start // 6 + 1:02}.jpg", quality=95)
first = [
    next(r for r in rows if r["owner_group"] == g)
    for g in sorted(set(r["owner_group"] for r in rows))
]
for off in range(0, len(first), 6):
    can = Image.new("RGB", (1280, 390 * ((len(first[off : off + 6]) + 1) // 2)), "#eee")
    d = ImageDraw.Draw(can)
    for j, r in enumerate(first[off : off + 6]):
        x = j % 2 * 640
        y = j // 2 * 390
        im = Image.open(R / r["marked_path"])
        im.thumbnail((640, 360))
        can.paste(im, (x, y + 27))
        d.text(
            (x + 5, y + 5),
            Path(r["member"]).name + " -> " + r["matches"][0]["frame_id"],
            fill="black",
        )
    can.save(OUTPUT / "boards" / f"overview-{off // 6 + 1:02}.jpg", quality=95)
(P / "inventory.json").write_text(
    json.dumps(
        {
            "archive_sha256": hashlib.sha256(zpath.read_bytes()).hexdigest(),
            "archive_bytes": zpath.stat().st_size,
            "crc": "PASS",
            "matching": "trimmed thumbnail RGB difference, candidate only; verify visually",
            "records": rows,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print("images", len(rows))
print(
    "\n".join(
        f"M{g:02}: {len([r for r in rows if r['owner_group'] == g])} images -> "
        + str(sorted(set(r["matches"][0]["group"] for r in rows if r["owner_group"] == g)))
        for g in sorted(set(r["owner_group"] for r in rows))
    )
)
print("max score", max(r["matches"][0]["score"] for r in rows))
