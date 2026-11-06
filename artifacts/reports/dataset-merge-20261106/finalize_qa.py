"""Record this batch's human/agent review and preserve the delivered source snapshot."""

import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
BATCH = ROOT / "data/interim/dataset-merge-20261106"
SCRATCH = ROOT / "outputs/_scratch/dataset-merge-20261106"


def save(name, value):
    path = REPORT / name
    if path.exists():
        raise RuntimeError(f"Review already exists: {path}")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    inv = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    draft = json.loads((REPORT / "geometry-proposals.json").read_text(encoding="utf-8"))
    # Visual correction of missing/clipped hair, arms, or visible legs; no recrop.
    replacements = {
        11: [0, 0, 202, 186],
        70: [76, 0, 664, 1081], 71: [103, 0, 558, 853],
        72: [9, 0, 462, 667], 73: [92, 0, 520, 853],
        75: [6, 0, 859, 1091], 76: [30, 0, 833, 993],
        77: [249, 0, 863, 953],
        93: [0, 0, 1122, 1402],
        103: [191, 110, 908, 1440], 104: [182, 130, 850, 1425],
        108: [93, 167, 880, 1410], 109: [103, 180, 900, 1410],
        122: [0, 40, 1254, 1180],
        138: [0, 0, 783, 1003],
        152: [0, 130, 1254, 1254],
        155: [12, 97, 1128, 1100],
        162: [53, 0, 591, 487],
        186: [0, 30, 920, 1382], 187: [0, 30, 920, 1398],
        188: [0, 30, 920, 1392], 189: [0, 30, 940, 1374],
        190: [0, 30, 940, 1337], 191: [0, 30, 940, 1367],
        192: [220, 20, 900, 1040], 193: [220, 20, 900, 1040],
        194: [220, 20, 900, 1040],
        204: [0, 0, 1021, 1540],
        211: [0, 3, 516, 449], 218: [9, 10, 170, 216],
        228: [110, 20, 425, 590],
        243: [26, 0, 166, 245], 246: [0, 0, 399, 811],
        247: [9, 6, 163, 370],
    }
    # Other corrections are one edge of an already correct anchor proposal.
    edges = {
        3: {0: 0}, 6: {1: 0}, 7: {0: 0}, 8: {0: 0},
        9: {0: 0, 3: 225}, 10: {0: 0, 3: 1221},
        14: {0: 0, 3: 220}, 15: {0: 0, 3: 220},
        28: {0: 0, 1: 0}, 29: {1: 50}, 35: {0: 0},
        54: {0: 90}, 55: {0: 350}, 64: {0: 0},
        65: {0: 0}, 68: {3: 1240}, 84: {0: 400},
        85: {0: 285}, 88: {0: 0}, 89: {0: 0},
        92: {0: 130}, 100: {0: 330}, 117: {0: 240},
        120: {2: 1800}, 139: {0: 100}, 143: {0: 0},
        149: {0: 0}, 151: {0: 0}, 175: {1: 0},
        197: {2: 859}, 212: {0: 0}, 213: {0: 20, 3: 600},
        214: {0: 0, 2: 320}, 215: {2: 170, 3: 461},
        217: {0: 0, 2: 376, 3: 597}, 219: {0: 0, 2: 463, 3: 545},
        220: {0: 0, 2: 458, 3: 605}, 223: {0: 0},
        225: {0: 0}, 229: {0: 0}, 235: {2: 696},
        239: {2: 340}, 245: {0: 10},
    }
    rows = []
    for row, proposal in zip(inv["imports"], draft["rows"], strict=True):
        assert row["id"] == proposal["id"]
        number = int(row["id"].split("N")[-1])
        box = list(replacements.get(number, proposal["person_box"]) or [])
        if len(box) != 4:
            raise RuntimeError(f"Unresolved person box {row['id']}")
        for edge, value in edges.get(number, {}).items():
            box[edge] = value
        w, h = row["size"]
        box = [max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3])]
        assert 0 <= box[0] < box[2] <= w and 0 <= box[1] < box[3] <= h, (row["id"], box, [w, h])
        rows.append({
            "id": row["id"], "crop_sha256": row["sha256"],
            "original_name": row["original_name"], "owner_label": row["owner_label"],
            "final_label": row["owner_label"], "membership": "include",
            "person_box": box, "geometry_corrected": box != proposal["person_box"],
            "geometry_review": "visible anchor including visible limbs; detector draft visually checked",
            "phone_reason": "Owner filename decision checked on crop; mobile belongs to anchor"
                if row["owner_label"][0] == "P" else
                "Owner filename decision checked; no visible mobile/suspect object of anchor; calculator/wallet are not mobile",
            "looking_reason": "Owner filename decision checked against head, body and work context",
            "provenance_boundary": "delivered owner derivative; upstream generation recipe not verified",
        })
    for row in inv["native_included"]:
        label = "PU" if row["id"] == "S06-F00096-P01" else row["owner_label"]
        rows.append({
            "id": row["id"], "crop_sha256": row["sha256"],
            "owner_label": row["owner_label"], "final_label": label, "membership": "include",
            "geometry_review": "owner-selected native geometry preserved",
            "phone_reason": "Owner README decision verified with crop and attribution; U preserved where device remains ambiguous",
            "looking_reason": "Owner changed looking P to U after source/crop review in conversation"
                if row["id"] == "S06-F00096-P01" else
                "Owner README decision checked against head, body and work context",
        })
    archive = ROOT / "data/raw/owner-crops-20261106/imports.zip"
    if archive.exists():
        raise RuntimeError("Raw input archive already exists")
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_STORED) as z:
        for row in inv["imports"]:
            path = ROOT / row["path"]
            assert sha256_file(path) == row["sha256"]
            info = zipfile.ZipInfo(path.name, (2026, 11, 6, 0, 0, 0))
            z.writestr(info, path.read_bytes())
    save("owner-direction.json", {
        "reviewer": "repository-owner", "recorded_at": "2026-11-06",
        "authorization_source": "Direct user instructions and two replies in this conversation",
        "scope": "review crops, resolve clear label errors, merge new local dataset and allocate train/val for future E009",
        "native_membership": "116 unique IDs in reviewed README; other 274 exclude",
        "imports": "252 filename-labeled crops supplied by owner",
        "named_lineage": "Owner confirms frame/crop-named files derive from exactly that frame/crop",
        "thematic_28": "Generated to address model mistakes, no exact parent crop",
        "label_exception": {"S06-F00096-P01": "P/U; explicit owner reply"},
        "parent_exclude": ["V6-SB-048-ADD01", "G08-B01-F00001"],
        "parent_relabel": {"G09-B05-F00043": "N/P"},
        "allocation_delegated": True, "approved_use_scope": ["local_classifier_research"],
        "rights_basis": "Owner provides inputs and explicitly requests their enrollment for local research; no public redistribution license asserted",
        "training_authorized_by_this_receipt": False, "media_uploaded": False,
        "no_test_v15": True,
    })
    save("visual-review.json", {
        "reviewer": "agent-under-owner-delegation", "reviewed_at": "2026-11-06",
        "semantics": "V12-RECONCILE-PHONE-20261023", "rows": rows,
        "views": "All 368 crop inputs at 336 letterbox, native detail for device/head exceptions; 252 person-box overlays; source frames for looking exception",
        "work_context": "unknown unless inherited; N/N does not imply confirmed_normal",
        "exact_duplicates": inv["exact_duplicates"],
        "near_pair_review": "50 dHash <=10 or RGB correlation >=0.94 pairs reviewed, plus five nearest V14 crops for every new crop (1840 pairs)",
        "same_pose_context_variants": [
            {"ids": ["M15-N069", "M15-N079"], "difference": "book on desk"},
            {"ids": ["M15-N074", "M15-N081"], "difference": "book on desk"},
            {"ids": ["M15-N078", "M15-N082"], "difference": "book on desk"},
        ],
        "near_pair_decision": "Retain distinct head/device/context interventions; all siblings stay in one source family, not independent observations",
        "known_hard_negatives_inspected_native": [
            "M15-N148", "M15-N152", "M15-N158", "M15-N163", "M15-N172", "M15-N174",
            "M15-N177", "M15-N197", "M15-N205", "S09-F00018-P03",
        ],
        "input_archive": {"path": archive.relative_to(ROOT).as_posix(), "sha256": sha256_file(archive)},
    })
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
    corrected = [r for r in rows[:252] if r["geometry_corrected"]]
    paths = {r["id"]: r["path"] for r in inv["imports"]}
    for start in range(0, len(corrected), 12):
        sheet = Image.new("RGB", (1408, 1176), "#eee")
        draw = ImageDraw.Draw(sheet)
        for i, row in enumerate(corrected[start:start + 12]):
            with Image.open(ROOT / paths[row["id"]]) as source:
                im = source.convert("RGB")
            ImageDraw.Draw(im).rectangle(row["person_box"], outline="#00ff40", width=max(2, im.width // 100))
            x, y = i % 4 * 352, i // 4 * 392
            sheet.paste(preview_input(im, 336, (124, 116, 104)), (x + 8, y))
            draw.text((x + 8, y + 340), row["id"] + " " + str(row["person_box"]), fill="black", font=font)
        sheet.save(SCRATCH / f"geometry-final-{start // 12 + 1:02d}.jpg", quality=95)
    print(json.dumps({"reviewed": len(rows), "geometry_corrected": len(corrected), "archive_sha256": sha256_file(archive)}))


if __name__ == "__main__":
    main()
