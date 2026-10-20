"""Inventory worksheet for the owner-supplied frame audit; no label acceptance."""

import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

from PIL import Image, ImageDraw

from ai_exam_monitoring.data.image_similarity import difference_hash

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
DATA = ROOT / "data/interim/youtube-frame-audit-20261018"
ZIP = Path("D:/dataset-foundry-starter/exports/youtube-crawl-accepted-frames.zip")


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def put(path, blob):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == blob, path
    else:
        path.write_bytes(blob)


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    rows, groups, boards = [], [], []
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        names = z.namelist()
        assert len(names) == len(set(names))
        for name in names:
            p = PurePosixPath(name)
            assert not p.is_absolute() and ".." not in p.parts and ":" not in name
        manifest = [json.loads(line) for line in z.read("manifest.jsonl").splitlines()]
        by_member = {"assets/" + x["file_path"]: x for x in manifest}
        decisions = {x["asset_id"]: x for x in json.loads(z.read("review_decisions.json"))}
        members = [n for n in names if n.lower().endswith(".jpg")]
        assert set(members) == set(by_member)
        folders = list(dict.fromkeys(PurePosixPath(n).parent.name for n in members))
        for gi, folder in enumerate(folders, 1):
            gid = f"Y{gi:02}"
            group = {"group": gid, "folder": folder, "frame_ids": []}
            for name in sorted(n for n in members if PurePosixPath(n).parent.name == folder):
                p = PurePosixPath(name)
                blob = z.read(name)
                m = by_member[name]
                assert sha(blob) == m["sha256"] and len(blob) == m["bytes"]
                assert decisions[m["asset_id"]]["decision"] == "accepted"
                with Image.open(io.BytesIO(blob)) as original:
                    original.load()
                    im = original.convert("RGB")
                assert im.size == (m["width"], m["height"])
                dest = DATA / "frames" / gid / p.name
                put(dest, blob)
                fid = f"{gid}-F{int(p.stem.split('_')[-1]):05}"
                rows.append(
                    {
                        "frame_id": fid,
                        "group": gid,
                        "member": name,
                        "source_path": dest.relative_to(ROOT).as_posix(),
                        "sha256": sha(blob),
                        "rgb_sha256": sha(im.tobytes()),
                        "dhash": f"{difference_hash(im):016x}",
                        "width": im.width,
                        "height": im.height,
                        "asset_id": m["asset_id"],
                        "origin": m["origin"],
                        "visual_review_status": "pending",
                    }
                )
                group["frame_ids"].append(fid)
            groups.append(group)
        metadata = {n: sha(z.read(n)) for n in names if "/" not in n}
    refs = []
    for i in range(1, 7):
        found = list(Path("C:/Users/OS/Downloads/temp").glob(f"*-{i}.png"))
        assert len(found) == 1, (i, found)
        blob = found[0].read_bytes()
        dest = DATA / "references" / f"reference-{i:02}.png"
        put(dest, blob)
        refs.append(
            {
                "reference_id": f"reference-{i:02}",
                "sha256": sha(blob),
                "path": dest.relative_to(ROOT).as_posix(),
            }
        )
    by_id = {r["frame_id"]: r for r in rows}
    (DATA / "boards").mkdir(exist_ok=True)
    for group in groups:
        ids = group["frame_ids"]
        for offset in range(0, len(ids), 4):
            chosen = ids[offset : offset + 4]
            board = Image.new("RGB", (1280, 390 * ((len(chosen) + 1) // 2)), "white")
            d = ImageDraw.Draw(board)
            for j, fid in enumerate(chosen):
                r = by_id[fid]
                x, y = j % 2 * 640, j // 2 * 390
                with Image.open(ROOT / r["source_path"]) as im:
                    board.paste(im, (x, y + 25))
                d.text((x + 8, y + 5), fid, fill="black")
            dest = DATA / "boards" / f"{group['group']}-{offset // 4 + 1:02}.png"
            board.save(dest)
            boards.append({"path": dest.relative_to(ROOT).as_posix(), "frame_ids": chosen})
    overview = Image.new("RGB", (1280, 1170), "white")
    d = ImageDraw.Draw(overview)
    for j, group in enumerate(groups):
        r = by_id[group["frame_ids"][0]]
        x, y = j % 2 * 640, j // 2 * 390
        with Image.open(ROOT / r["source_path"]) as im:
            overview.paste(im, (x, y + 25))
        d.text((x + 8, y + 5), r["frame_id"], fill="black")
    overview.save(DATA / "boards/overview.png")
    duplicates = {}
    for key in ("sha256", "rgb_sha256"):
        buckets = defaultdict(list)
        for row in rows:
            buckets[row[key]].append(row["frame_id"])
        duplicates[key] = [ids for ids in buckets.values() if len(ids) > 1]
    result = {
        "archive": {"name": ZIP.name, "sha256": sha(ZIP.read_bytes()), "bytes": ZIP.stat().st_size},
        "metadata_sha256": metadata,
        "frames": rows,
        "groups": groups,
        "references": refs,
        "boards": boards,
        "exact_duplicates": duplicates,
        "rights": "Owner xác nhận toàn quyền sử dụng; audit/crop local ngày 18/10/2026.",
        "acceptance": "Accepted trong ZIP là chọn frame nguồn, chưa là nhãn/crop/release.",
        "checks": {
            "zip_crc": "PASS",
            "manifest_membership": "PASS",
            "source_hashes": "PASS",
            "decode": "PASS",
        },
    }
    save(REPORT / "inventory.json", result)
    print(
        json.dumps(
            {
                "frames": len(rows),
                "groups": Counter(r["group"] for r in rows),
                "duplicates": duplicates,
                "archive_sha256": result["archive"]["sha256"],
            }
        )
    )


if __name__ == "__main__":
    main()
