"""Package manual R2 observations; never infer annotations or edit releases."""

import hashlib
import html
import json
import os
from collections import Counter
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import preview_input

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
ROOT = HERE.parents[3]
MEDIA = ROOT / "data/interim/v11-legacy-crop-audit-20261018-r2"
OLD_MEDIA = ROOT / "data/interim/v11-legacy-crop-audit-20261018"
PACKAGE = ROOT / "data/processed/pilot-b/pilot-b-20261017-v11"
STATE = {"P": "positive", "N": "negative", "U": "unknown"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(name, value):
    (HERE / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def relative(path):
    return Path(os.path.relpath(path, MEDIA)).as_posix()


def main():
    cohort = read(PARENT / "cohort.json")
    previous = {r["sample_id"]: r for r in read(PARENT / "decisions.json")}
    index = read(HERE / "review-index.json")
    codes = read(HERE / "reason-codes.json")
    lookup = {(int(r["board"][3:6]), r["cell"]): r for r in index}
    by_id = {r["sample_id"]: r for r in cohort}
    assert len(lookup) == len(by_id) == 836
    notes = {}
    for line in (HERE / "review-notes.psv").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        b, c, state, action, reasons, note = line.split("|")
        key = int(b), int(c)
        assert key not in notes and key in lookup
        assert action in {"keep", "recrop", "exclude"}
        targets = state.split("/")
        assert len(targets) == 2 and all(t in STATE for t in targets)
        reason_codes = reasons.split(",")
        assert len(reason_codes) == 3 and all(r in codes for r in reason_codes)
        phone_code, look_code, geometry_code = reason_codes
        assert phone_code[0].upper() == targets[0]
        expected = (
            "N"
            if look_code == "l_own"
            else "P"
            if look_code in {"l_front", "l_side", "l_other", "l_below"}
            else "U"
        )
        assert expected == targets[1]
        assert not (action == "keep" and state == "U/U")
        notes[key] = targets, action, reason_codes, note
    assert notes.keys() == lookup.keys()
    for name, digest in read(HERE / "parent-pins.json").items():
        assert sha256_file(PARENT / name) == digest, name
    for path, digest in read(PARENT / "input-pins.json")["files"].items():
        assert sha256_file(ROOT / path) == digest, path
    decisions = []
    cards = []
    table = [
        "# Quyết định audit R2 — Draft",
        "",
        "Thứ tự phone / looking. `keep`: giữ geometry, nhãn là đề xuất. "
        "`recrop`: tạm rút crop hiện tại, thử geometry mới và duyệt lại cả hai nhãn. "
        "`exclude`: đề xuất rút supervision. Chưa áp dụng vào V11.",
        "",
        "[Rubric](RUBRIC.md) · [Tổng quan](README.md) · "
        "[Gallery](../../../../data/interim/v11-legacy-crop-audit-20261018-r2/index.html)",
        "",
        "| ID | V11 | R2 quan sát | Xử lý | Lý do |",
        "|---|---|---|---|---|",
    ]
    for entry in index:
        key = int(entry["board"][3:6]), entry["cell"]
        targets, action, reason_codes, note = notes[key]
        sid = entry["sample_id"]
        row = by_id[sid]
        assert row["v11_usage"] in {"train", "val"}
        native = PACKAGE / row["crop"]["crop_relpath"]
        assert sha256_file(native) == row["crop"]["crop_sha256"]
        with Image.open(native) as im:
            inp = preview_input(im.convert("RGB"), 224, (124, 116, 104))
            assert hashlib.sha256(inp.tobytes()).hexdigest() == row["input_rgb_sha256"]
        input_path = OLD_MEDIA / "input" / f"{sid}.png"
        with Image.open(input_path) as im:
            assert im.mode == "RGB" and im.size == (224, 224)
            assert hashlib.sha256(im.tobytes()).hexdigest() == row["input_rgb_sha256"]
        source = OLD_MEDIA / "source" / f"{sid}.jpg"
        assert source.is_file() and (MEDIA / "boards" / entry["board"]).is_file()
        proposed = [STATE[s] for s in targets]
        old = previous[sid]
        d = {
            "sample_id": sid,
            "status": "Draft",
            "cohort": row["cohort"],
            "v11_usage": row["v11_usage"],
            "current_states": row["current_states"],
            "observed_states": proposed,
            "proposed_supervision_states": proposed if action == "keep" else None,
            "action": action,
            "reason_codes": reason_codes,
            "reason": note,
            "reason_definitions": [codes[c] for c in reason_codes],
            "label_delta": proposed != row["current_states"],
            "r1_states": old["proposed_states"],
            "r1_action": old["action"],
            "changed_from_r1": proposed != old["proposed_states"] or action != old["action"],
            "after_recrop_requires_fresh_review": action == "recrop",
            "repair_status": "not_created" if action == "recrop" else "not_requested",
            "geometry_guidance": codes[reason_codes[2]],
            "evidence": entry,
            "crop_sha256": row["crop"]["crop_sha256"],
            "input_rgb_sha256": row["input_rgb_sha256"],
        }
        decisions.append(d)
        short = "/".join(s[0].upper() for s in row["current_states"])
        table.append(f"| {sid} | {short} | {'/'.join(targets)} | {action} | {note} |")
        imgs = "".join(
            f'<a href="{relative(p)}"><img loading="lazy" src="{relative(p)}" '
            f'alt="{sid} {label}"></a>'
            for p, label in [(source, "source"), (native, "native"), (input_path, "input 224")]
        )
        cards.append(
            f'<article data-action="{action}" data-id="{sid.lower()}">'
            f"<h2>{sid} — {short} → {'/'.join(targets)} · {action}</h2>"
            f'<p>{html.escape(note)}</p><div class="images">{imgs}</div>'
            f"<p>Trái: source có box; giữa: native; phải: PNG 224. "
            f'<a href="boards/{entry["board"]}">Bảng {key[0]}, ô {key[1]}</a>.</p>'
            f"<p>{html.escape(d['geometry_guidance'])}</p></article>"
        )
    summary = {
        "status": "Draft",
        "count": len(decisions),
        "actions": dict(Counter(d["action"] for d in decisions)),
        "observed_pairs": dict(Counter("/".join(d["observed_states"]) for d in decisions)),
        "kept_label_delta": sum(d["action"] == "keep" and d["label_delta"] for d in decisions),
        "kept_no_label_delta": sum(
            d["action"] == "keep" and not d["label_delta"] for d in decisions
        ),
        "changed_from_r1": sum(d["changed_from_r1"] for d in decisions),
        "phone_p_final": sum(d["observed_states"][0] == "positive" for d in decisions),
        "phone_p_candidates_rechecked": 64,
        "new_recrops_created": 0,
        "accepted_v11_mutated": False,
        "test_or_reserve_opened": False,
    }
    write("decisions.json", decisions)
    write("summary.json", summary)
    (HERE / "DECISIONS.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    template = (HERE / "gallery.html").read_text(encoding="utf-8")
    (MEDIA / "index.html").write_text(
        template.replace("<!-- CARDS -->", "\n".join(cards)), encoding="utf-8"
    )
    media_files = sorted(p for p in MEDIA.rglob("*") if p.suffix in {".jpg", ".png"})
    (HERE / "media-checksums.sha256").write_text(
        "".join(f"{sha256_file(p)}  {p.relative_to(MEDIA).as_posix()}\n" for p in media_files),
        encoding="utf-8",
    )
    write(
        "validation.json",
        {
            "status": "PASS",
            "unique_manual_notes": 836,
            "native_sha_checks": 836,
            "input_rgb_checks": 836,
            "gallery_cards": len(cards),
            "parent_pins_unchanged": True,
            "release_metadata_pins_unchanged": True,
            "state_reason_consistency": True,
            "kept_unknown_unknown": 0,
            "media_checksum_count": len(media_files),
            "browser_render_checked": False,
            "new_geometry_reviewed": 0,
            "owner_acceptance": "pending",
        },
    )
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
