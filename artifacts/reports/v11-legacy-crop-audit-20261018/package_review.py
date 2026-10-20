"""Worksheet: join manual evidence, verify coverage, package local owner review."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from deep_review import ARCHIVE, ARCHIVE_SHA, HERE, PACKAGE, ROOT, SCRATCH
from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import preview_input

REVIEW = ROOT / "data/interim/v11-legacy-crop-audit-20261018"
STATE = {"P": "positive", "N": "negative", "U": "unknown"}


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_notes(name: str) -> dict:
    notes = {}
    for line in (HERE / name).read_text(encoding="utf-8-sig").splitlines():
        board, cell, labels, action, reason = line.split("|", 4)
        key = int(board), int(cell)
        assert key not in notes
        assert labels in {f"{a}/{b}" for a in STATE for b in STATE}
        assert reason.strip()
        notes[key] = dict(states=labels, action=action, reason=reason)
    return notes


def main() -> None:
    rows = json.loads((HERE / "cohort.json").read_text(encoding="utf-8"))
    first = read_notes("visual-notes.psv")
    deep = read_notes("deep-notes.psv")
    index = json.loads((HERE / "deep-index.json").read_text(encoding="utf-8"))
    assert len(first) == len(rows) == 836 and len(deep) == len(index) == 259
    assert set(first) == {(int(r["board"][6:9]), r["cell"]) for r in rows}
    assert set(deep) == {(int(r["board"][5:8]), r["cell"]) for r in index}
    deeper = {r["sample_id"]: r for r in index}
    confirmations = {
        r["sample_id"]: r
        for r in json.loads((HERE / "confirmation-notes.json").read_text(encoding="utf-8"))
    }
    assert len(confirmations) == 38
    decisions = []
    confirmation_candidates = []
    for row in rows:
        original = first[(int(row["board"][6:9]), row["cell"])]
        evidence = deeper.get(row["sample_id"])
        note = deep[(int(evidence["board"][5:8]), evidence["cell"])] if evidence else original
        if note["action"] == "exclude":
            confirmation_candidates.append({"sample_id": row["sample_id"]})
            assert row["sample_id"] in confirmations
        confirmation = confirmations.get(row["sample_id"])
        if confirmation:
            assert confirmation["confirmed_source_native_input"]
            note = confirmation
        assert note["action"] in {"keep", "recrop", "exclude"}
        states = [STATE[s] for s in note["states"].split("/")]
        assert note["action"] != "keep" or states != ["unknown", "unknown"]
        decisions.append(
            {
                "sample_id": row["sample_id"],
                "status": "Draft",
                "cohort": row["cohort"],
                "v11_usage": row["v11_usage"],
                "current_states": row["current_states"],
                "proposed_states": states,
                "label_delta": row["current_states"] != states,
                "action": note["action"],
                "reason": note["reason"],
                "enrollment_proposal": "retain_geometry"
                if note["action"] == "keep"
                else "withhold",
                "after_recrop_requires_fresh_review": note["action"] == "recrop",
                "first_pass_evidence": {"board": row["board"], "cell": row["cell"]},
                "deep_evidence": {"board": evidence["board"], "cell": evidence["cell"]}
                if evidence
                else None,
                "crop_sha256": row["crop"]["crop_sha256"],
                "input_rgb_sha256": row["input_rgb_sha256"],
                "confirmation_evidence": confirmation["evidence"] if confirmation else None,
            }
        )
    assert len({d["sample_id"] for d in decisions}) == 836
    pins = json.loads((HERE / "input-pins.json").read_text(encoding="utf-8"))
    for path, digest in pins["files"].items():
        assert sha256_file(ROOT / path) == digest, path
    assert sha256_file(ARCHIVE) == ARCHIVE_SHA
    REVIEW.mkdir(parents=True, exist_ok=True)
    for directory in ["input", "source", "boards"]:
        (REVIEW / directory).mkdir(exist_ok=True)
    rgb_groups, input_groups, source_groups = (
        defaultdict(list),
        defaultdict(list),
        defaultdict(list),
    )
    with zipfile.ZipFile(ARCHIVE) as archive:
        for row in rows:
            sid = row["sample_id"]
            with Image.open(PACKAGE / row["crop"]["crop_relpath"]) as image:
                image = image.convert("RGB")
                rgb_key = f"{image.size}:{hashlib.sha256(image.tobytes()).hexdigest()}"
                rgb_groups[rgb_key].append(sid)
                inp = preview_input(image, 224, (124, 116, 104))
                assert hashlib.sha256(inp.tobytes()).hexdigest() == row["input_rgb_sha256"]
                inp.save(REVIEW / "input" / f"{sid}.png")
            input_groups[row["input_rgb_sha256"]].append(sid)
            source_groups[row["source"]["image_sha256"]].append(sid)
            content = archive.read("blobs/" + row["source"]["image_sha256"])
            assert hashlib.sha256(content).hexdigest() == row["source"]["image_sha256"]
            with Image.open(io.BytesIO(content)) as image:
                source = image.convert("RGB")
            draw = ImageDraw.Draw(source)
            for name, color in [("context_box", "orange"), ("person_box", "#00ff33")]:
                box = row["crop"][name]
                draw.rectangle(
                    tuple(box[k] for k in ["xmin", "ymin", "xmax", "ymax"]),
                    outline=color,
                    width=max(2, source.width // 250),
                )
            source.thumbnail((720, 540), Image.Resampling.BILINEAR)
            source.save(REVIEW / "source" / f"{sid}.jpg", quality=94, subsampling=0)
    # Preserve the actual boards used for review; only regenerate when scratch is available.
    for path in SCRATCH.glob("*.jpg"):
        shutil.copy2(path, REVIEW / "boards" / path.name)
    for row in rows:
        assert (REVIEW / "boards" / row["board"]).is_file()
    for item in index:
        assert (REVIEW / "boards" / item["board"]).is_file()
    # Supplementary source/native/input boards for every exclusion, including first-pass cases.
    selected = {r["sample_id"]: r for r in rows}
    excluded = confirmation_candidates
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    for start in range(0, len(excluded), 6):
        board = Image.new("RGB", (1880, 1455), "#ddddee")
        draw = ImageDraw.Draw(board)
        for i, decision in enumerate(excluded[start : start + 6]):
            row = selected[decision["sample_id"]]
            x, y = i % 2 * 940, i // 2 * 485
            draw.rectangle((x, y, x + 938, y + 483), fill="white", outline="black")
            draw.text((x + 5, y + 5), f"{i + 1:02d} {row['sample_id']}", font=font, fill="black")
            for path, width, offset in [
                (REVIEW / "source" / f"{row['sample_id']}.jpg", 340, 0),
                (PACKAGE / row["crop"]["crop_relpath"], 350, 350),
            ]:
                with Image.open(path) as image:
                    image = image.convert("RGB")
                    image.thumbnail((width, 410), Image.Resampling.BILINEAR)
                    board.paste(
                        image,
                        (
                            x + offset + (width - image.width) // 2,
                            y + 35 + (410 - image.height) // 2,
                        ),
                    )
            with Image.open(REVIEW / "input" / f"{row['sample_id']}.png") as inp:
                board.paste(inp, (x + 710, y + 105))
            draw.text(
                (x + 5, y + 458), "source / native / exact input 224", font=font, fill="black"
            )
        board.save(
            REVIEW / "boards" / f"exclude-{start // 6 + 1:03d}.jpg", quality=94, subsampling=0
        )

    def groups(mapping: dict) -> list:
        return [v for v in mapping.values() if len(v) > 1]

    def cross_role(group: list) -> bool:
        return len({selected[s]["v11_usage"] for s in group}) > 1

    overlap = {
        "scope": "836 selected crops only; exact hashes, not exhaustive near-duplicate detection",
        "exact_native_rgb_groups": groups(rgb_groups),
        "exact_input_rgb_groups": groups(input_groups),
        "same_source_groups": groups(source_groups),
        "same_source_cross_train_val_groups": [g for g in groups(source_groups) if cross_role(g)],
        "same_leakage_group_cross_train_val": [],
    }
    group_members = defaultdict(list)
    for row in rows:
        group_members[row["group_id"]].append(row["sample_id"])
    overlap["same_leakage_group_cross_train_val"] = [
        g for g in groups(group_members) if cross_role(g)
    ]
    kept = [d for d in decisions if d["action"] == "keep"]
    summary = {
        "status": "Draft; owner acceptance pending",
        "count": len(decisions),
        "reviewed_native_and_input": 836,
        "deep_source_native_input": 259,
        "exclusion_confirmation_count": len(excluded),
        "actions": dict(Counter(d["action"] for d in decisions)),
        "actions_by_current_role": {
            a: dict(Counter(d["v11_usage"] for d in decisions if d["action"] == a))
            for a in ["keep", "recrop", "exclude"]
        },
        "kept_label_delta": sum(d["label_delta"] for d in kept),
        "kept_no_label_delta": sum(not d["label_delta"] for d in kept),
        "current_states_all": dict(
            Counter("/".join(s[0].upper() for s in d["current_states"]) for d in decisions)
        ),
        "proposed_states_kept": dict(
            Counter("/".join(s[0].upper() for s in d["proposed_states"]) for d in kept)
        ),
        "kept_target_transitions": {
            t: dict(Counter(f"{d['current_states'][i]}->{d['proposed_states'][i]}" for d in kept))
            for i, t in enumerate(["phone_use", "looking_around"])
        },
        "exact_native_rgb_duplicate_groups": len(overlap["exact_native_rgb_groups"]),
        "exact_input_rgb_duplicate_groups": len(overlap["exact_input_rgb_groups"]),
        "same_source_cross_train_val_groups": len(overlap["same_source_cross_train_val_groups"]),
        "same_leakage_group_cross_train_val": len(overlap["same_leakage_group_cross_train_val"]),
        "accepted_package_mutated": False,
        "test_or_reserve_visual_access": False,
    }
    for name, value in [
        ("decisions.json", decisions),
        ("summary.json", summary),
        ("overlap.json", overlap),
    ]:
        dump(HERE / name, value)
    gallery_rows = []
    for row, decision in zip(rows, decisions, strict=True):
        gallery_rows.append(
            {
                **decision,
                "source_id": row["source"]["source_id"],
                "native": "../../../"
                + (PACKAGE / row["crop"]["crop_relpath"]).relative_to(ROOT).as_posix(),
            }
        )
    template = (HERE / "gallery.html").read_text(encoding="utf-8")
    data = json.dumps(gallery_rows, ensure_ascii=False).replace("<", "\\u003c")
    (REVIEW / "index.html").write_text(template.replace("/*AUDIT_DATA*/[]", data), encoding="utf-8")
    dump(
        HERE / "review-pointer.json",
        {
            "status": "Draft",
            "gallery": (REVIEW / "index.html").relative_to(ROOT).as_posix(),
            "media_in_git": False,
            "source_original": ARCHIVE.relative_to(ROOT).as_posix(),
            "source_original_sha256": ARCHIVE_SHA,
            "gallery_sha256": sha256_file(REVIEW / "index.html"),
            "rebuild": (
                "Run prepare.py, deep_review.py, then package_review.py "
                "using .venv/Scripts/python.exe -X utf8"
            ),
        },
    )
    dump(
        REVIEW / "current.json",
        {"report": HERE.relative_to(ROOT).as_posix(), "status": "Draft", "count": 836},
    )
    # Portable, readable per-crop proposals; state order is always phone / looking.
    lines = [
        "# Đề xuất từng crop — Draft",
        "",
        "Chưa sửa V11. `recrop` và `exclude` đều đề xuất withheld; "
        "nhãn ở ca recrop chỉ là evidence hiện tại, phải duyệt lại geometry mới.",
        "",
        "| ID | Vai trò V11 | Hiện tại | Đề xuất | Hành động | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for d in decisions:
        old = "/".join(s[0].upper() for s in d["current_states"])
        new = "/".join(s[0].upper() for s in d["proposed_states"])
        lines.append(
            f"| {d['sample_id']} | {d['v11_usage']} | {old} | {new} | "
            f"{d['action']} | {d['reason']} |"
        )
    (HERE / "DECISIONS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
