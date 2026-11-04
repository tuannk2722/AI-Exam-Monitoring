"""Worksheet audit read-only: exact cohort, pins, blind native/input boards."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.data.pilot_schema import read_records, record_to_dict
from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCRATCH = ROOT / "outputs/_scratch/v11-legacy-crop-audit-20261018"
PACKAGE = ROOT / "data/processed/pilot-b/pilot-b-20261017-v11"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    old_path = ROOT / "data/processed/pilot-b/pilot-b-20261013-v9/review-ledger.jsonl"
    old = {r.sample_id: record_to_dict(r) for r in read_records(old_path)}
    current = {
        r.sample_id: record_to_dict(r) for r in read_records(PACKAGE / "review-ledger.jsonl")
    }
    roles_path = ROOT / "artifacts/reports/E004-v9-consolidation-20261013/role-membership.json"
    roles = json.loads(roles_path.read_text(encoding="utf-8"))
    development = {r["sample_id"] for r in roles if r["reserved_role"] == "new_development"}
    if len(development) != 71:
        raise ValueError(f"Development scope differs: {len(development)}")
    baseline = {s for s, r in old.items() if r["usage"] in {"train", "val"}}
    assert len(baseline) == 765 and not baseline & development
    selected = baseline | development
    assert len(selected) == 836
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
    rows = []
    # Sort by source then technical ID, never by score or current label.
    for sid in sorted(selected, key=lambda s: (current[s]["source"]["source_id"], s)):
        r, parent = current[sid], old[sid]
        assert r["usage"] in {"train", "val"}
        assert parent["usage"] != "test" and r["test_freeze_ref"] is None
        for field in ["source", "phone_use", "looking_around"]:
            assert r[field] == parent[field], (sid, field)
        for key, value in parent["crop"].items():
            assert r["crop"][key] == value, (sid, key)
        path = PACKAGE / r["crop"]["crop_relpath"]
        assert sha(path) == r["crop"]["crop_sha256"]
        with Image.open(path) as image:
            image.load()
            assert image.size == (
                r["crop"]["context_box"]["xmax"] - r["crop"]["context_box"]["xmin"],
                r["crop"]["context_box"]["ymax"] - r["crop"]["context_box"]["ymin"],
            )
            inp = preview_input(image, 224, (124, 116, 104))
            pixel_sha = hashlib.sha256(inp.tobytes()).hexdigest()
            dims = image.size
        rows.append(
            {
                "sample_id": sid,
                "cohort": "v9_baseline" if sid in baseline else "v9_development",
                "v9_usage": parent["usage"],
                "v11_usage": r["usage"],
                "source": r["source"],
                "crop": r["crop"],
                "current_states": [r[t]["state"] for t in ["phone_use", "looking_around"]],
                "current_reasons": [r[t]["reason"] for t in ["phone_use", "looking_around"]],
                "group_id": r["group"]["leakage_group_id"],
                "native_dimensions": dims,
                "input_rgb_sha256": pixel_sha,
                "board": f"board-{len(rows) // 12 + 1:03d}.jpg",
                "cell": len(rows) % 12 + 1,
            }
        )
    SCRATCH.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(rows), 12):
        group = rows[start : start + 12]
        board = Image.new("RGB", (1692, 1320), "#e0e0e0")
        draw = ImageDraw.Draw(board)
        for i, row in enumerate(group):
            x, y = i % 3 * 564, i // 3 * 330
            draw.rectangle((x, y, x + 562, y + 328), fill="white", outline="#444444")
            draw.text((x + 8, y + 5), f"{i + 1:02d}  {row['sample_id']}", fill="black", font=font)
            with Image.open(PACKAGE / row["crop"]["crop_relpath"]) as image:
                image = image.convert("RGB")
                # Native view can enlarge for inspection; no sharpening or AI edits.
                scale = min(312 / image.width, 270 / image.height)
                shown = image.resize(
                    (round(image.width * scale), round(image.height * scale)),
                    Image.Resampling.BILINEAR,
                )
                board.paste(
                    shown, (x + (320 - shown.width) // 2, y + 32 + (270 - shown.height) // 2)
                )
                board.paste(preview_input(image, 224, (124, 116, 104)), (x + 332, y + 48))
            draw.text(
                (x + 8, y + 306),
                f"native {row['native_dimensions']}  |  input 224",
                fill="black",
                font=small,
            )
        board.save(SCRATCH / group[0]["board"], quality=94, subsampling=0)
    dump(HERE / "cohort.json", rows)
    pins = [
        old_path,
        roles_path,
        PACKAGE / "manifest.jsonl",
        PACKAGE / "review-ledger.jsonl",
        PACKAGE / "checksums.sha256",
    ]
    dump(
        HERE / "input-pins.json",
        {
            "scope": (
                "Owner chọn 836 crop baseline V9 + development, 18/10/2026; không test/reserve."
            ),
            "files": {p.relative_to(ROOT).as_posix(): sha(p) for p in pins},
            "count": len(rows),
            "cohorts": dict(Counter(r["cohort"] for r in rows)),
            "current_roles": dict(Counter(r["v11_usage"] for r in rows)),
            "source_counts": dict(Counter(r["source"]["source_id"] for r in rows)),
            "crop_sha_parity": True,
            "geometry_parity": True,
            "label_parity": True,
            "test_or_reserve_opened": False,
        },
    )
    print(
        json.dumps(
            {
                "count": len(rows),
                "boards": (len(rows) + 11) // 12,
                "roles": dict(Counter(r["v11_usage"] for r in rows)),
            }
        )
    )


if __name__ == "__main__":
    main()
