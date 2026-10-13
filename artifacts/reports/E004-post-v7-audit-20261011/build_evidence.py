"""Phương pháp audit snapshot; không là trainer, không cấp approval.

Chạy từ repository root với .venv/Scripts/python.exe -X utf8 <file này>.
Đọc metadata active/archive và hai ZIP Downloads, chỉ ghi hồ sơ audit này.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.image_similarity import difference_hash
from ai_exam_monitoring.data.pilot_schema import read_records
from ai_exam_monitoring.data.yolo import YoloAnnotation

ROOT = Path.cwd()
OUT = ROOT / "artifacts/reports/E004-post-v7-audit-20261011"
PINS = {}
ARCHIVE = zipfile.ZipFile(ROOT / "archive/history-20261010.zip")
ENTRIES = {r["path"]: r for r in json.loads(ARCHIVE.read("manifest.json"))["files"]}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    active = ROOT / path
    if active.is_file():
        raw, locator = active.read_bytes(), "active"
    else:
        entry = ENTRIES[path]
        raw = ARCHIVE.read("blobs/" + entry["sha256"])
        assert len(raw) == entry["size"] and sha(raw) == entry["sha256"], path
        locator = "archive/history-20261010.zip#" + path
    PINS[path] = {"sha256": sha(raw), "size": len(raw), "locator": locator}
    if path.endswith(".jsonl"):
        return [json.loads(line) for line in raw.splitlines() if line.strip()]
    return json.loads(raw)


def dump(name, obj):
    (OUT / name).write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def pin_context():
    paths = [
        "AGENTS.md",
        "docs/data.md",
        "docs/training.md",
        "docs/system.md",
        "docs/decisions.md",
        "docs/reference.md",
        "docs/operations.md",
        "configs/experiments/E004-plan.yaml",
        "configs/experiments/E003.yaml",
        "configs/datasets/pilot_b_release_v7.yaml",
    ]
    paths += [
        "src/ai_exam_monitoring/training/" + name + ".py"
        for name in ("config", "model", "train", "metrics", "evaluate")
    ]
    for path in paths:
        raw = (ROOT / path).read_bytes()
        PINS[path] = {"sha256": sha(raw), "size": len(raw), "locator": "active"}
    for name in (
        "ADR-011-person-unit-phone-definition.md",
        "ADR-012-formulation-b-multilabel.md",
        "ADR-013-pilot-b-packaging-contract.md",
        "ADR-017-e004-classifier-promotion-gates.md",
        "ADR-018-v7-mobile-phone-boundary.md",
    ):
        path = "docs/decisions/" + name
        raw = subprocess.check_output(["git", "show", "ab34b32:" + path], cwd=ROOT)
        PINS[path] = {"sha256": sha(raw), "size": len(raw), "locator": "git:ab34b32:" + path}
    assert (
        PINS["configs/experiments/E004-plan.yaml"]["sha256"]
        == "8c7e2d19fd65b0f475f8801bc71bbab688424e8721f5d73dff607640934f2b09"
    )


def support(rows):
    return {
        "records": len(rows),
        "registered_groups": len({r["group_id"] for r in rows}),
        "fully_known": sum(r["phone"] != "U" and r["looking"] != "U" for r in rows),
        "combinations": dict(Counter(r["phone"] + r["looking"] for r in rows)),
        **{t: {s: sum(r[t] == s for r in rows) for s in "PNU"} for t in ("phone", "looking")},
    }


def group_by(rows, key):
    groups = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    return {k: support(v) for k, v in sorted(groups.items())}


def run_metadata():
    v7path = "data/processed/pilot-b/pilot-b-20261010-v7/manifest.jsonl"
    v6path = "data/processed/pilot-b/pilot-b-20261007-v6/manifest.jsonl"
    v7, v6 = load(v7path), load(v6path)
    ledger = load("data/processed/pilot-b/pilot-b-20261010-v7/review-ledger.jsonl")
    parent_ledger = load("data/processed/pilot-b/pilot-b-20261007-v6/review-ledger.jsonl")
    assert len(read_records(ROOT / v7path)) == len(v7) == 749
    assert len(read_records(ROOT / v6path)) == len(v6) == 378
    release = load("artifacts/reports/pilot-b-v7-release-20261010/release-pointer.json")
    for key in (
        "manifest",
        "ledger",
        "release_metadata",
        "split_assignment",
        "owner_approval",
        "verification",
        "rebuild_verification",
    ):
        pin = release[key]
        load(pin["path"])
        assert PINS[pin["path"]]["sha256"] == pin["sha256"], key
    assert (
        PINS[v7path]["sha256"] == "3fc53fedf12b34d0e271effb6af3046b2073b1ceebad3a6300d0e256e3dd1ede"
    )
    prov = {
        r["sample_id"]: r
        for r in load("artifacts/reports/pilot-b-v7-release-20261010/new-source-provenance.jsonl")
    }
    r5path = "outputs/v7-owner-review-r5-20261009/review-proposals.jsonl"
    r8path = "outputs/v7-r8-owner-review-20261009-r6/review-proposals.jsonl"
    stagepath = "outputs/v7-owner-execution-20261010-r3/staging-crops.jsonl"
    drafts = [(r5path, load(r5path)), (r8path, load(r8path)), (stagepath, load(stagepath))]
    qp = "artifacts/reports/pilot-b-v7-audit-r8-20261009/input224-r3/input224-findings.json"
    op = "artifacts/reports/pilot-b-v7-audit-r8-20261009/input224-r3/ownership-findings.json"
    findings = {r["sample_id"]: r for r in load(qp)["findings"]}
    ownership = {r["sample_id"]: r for r in load(op)["findings"]}
    parent_ids = {r["sample_id"] for r in parent_ledger}
    new = sorted(
        [r for r in v7 if r["usage"] == "train" and r["sample_id"] not in parent_ids],
        key=lambda x: x["sample_id"],
    )
    assert len(new) == 375
    parent_groups = {
        r["group"]["leakage_group_id"]
        for r in ledger
        if r["sample_id"] in parent_ids and r["group"]
    }
    state = {"positive": "P", "negative": "N", "unknown": "U"}
    rows = []
    for r in new:
        sid, ch = r["sample_id"], r["crop"]["crop_sha256"]
        assert file_sha(ROOT / release["package"] / r["crop"]["crop_relpath"]) == ch, sid
        p = prov[sid]
        assert (
            p["crop"]["sha256"] == ch
            and p["original_source"]["sha256"] == r["source"]["image_sha256"]
        ), sid
        q, o = findings.get(sid), ownership.get(sid)
        qmatch = q and q["evidence_pins"]["crop_sha256"] == ch
        omatch = o and o["evidence_pins"]["crop_sha256"] == ch
        hints, tags, bucket, family, refs = {}, [], "unknown", "unknown", []
        for path, ds in drafts:
            for d in ds:
                if d["sample_id"] != sid or d.get("media", {}).get("crop", {}).get("sha256") != ch:
                    continue
                bucket = d.get("bucket", bucket)
                family = d.get("visual_family_hint", family)
                tags.extend(d.get("phenotypes", []))
                refs.append(path + "#" + sid)
        # Literal evidence search only; these are mentions, not presence/absence labels.
        reason = r["phone_use"]["reason"] + " | " + r["looking_around"]["reason"]
        for tag, pattern in {
            "desk": (
                r"phone.{0,22}(trên|nằm).{0,18}(bàn|sách|giấy)|"
                r"mobile.{0,22}(trên|nằm).{0,18}(bàn|sách|giấy)"
            ),
            "at_ear": r"áp tai|phone.{0,15}(tai|ear)",
            "partial": r"che một phần|partial|che tay|tay che|hand.occlusion",
            "small": r"phone nhỏ|mobile nhỏ|small.phone",
            "low_detail": r"low.detail|mất chi tiết|mờ|noise",
            "own_workarea": r"own.{0,2}(desk|page|workarea)|bài (riêng|của mình)",
            "crowded": r"crowded|người khác|nhiều người|bên cạnh|tiền cảnh|foreground",
            "read_write": r"đọc|viết|reading|writing",
            "rest_pose": r"chống đầu|nghỉ|chạm (tai|mặt)",
        }.items():
            matches = [m.group(0) for m in re.finditer(pattern, reason, re.IGNORECASE)]
            if matches:
                hints[tag] = sorted(set(matches))
        row = {
            "sample_id": sid,
            "phone": state[r["phone_use"]["state"]],
            "looking": state[r["looking_around"]["state"]],
            "crop_sha256": ch,
            "source_sha256": r["source"]["image_sha256"],
            "source_id": r["source"]["source_id"],
            "group_id": r["group"]["leakage_group_id"],
            "source_family_conservative": r["group"]["leakage_group_id"],
            "visual_family_hint_draft": family,
            "parent_linked_component": r["group"]["leakage_group_id"] in parent_groups,
            "domain": p.get("domain", "unknown"),
            "primary_exam_camera_verified": None,
            "bucket_hint_draft": bucket,
            "phenotypes_explicit_draft": sorted(set(tags)),
            "phenotype_taxonomy_accepted": None,
            "literal_reason_mentions_not_phenotype_labels": hints,
            "phone_ownership": "accepted_positive_anchor_link"
            if r["phone_use"]["state"] == "positive"
            else "accepted_negative_observation"
            if r["phone_use"]["state"] == "negative"
            else "unknown",
            "ownership_subtype_draft": o.get("ownership_evidence") if omatch else None,
            "input224_quality_draft": q["input224_evidence"] if qmatch else "unknown",
            "input224_quality_reason": q["final_reason"] if qmatch else None,
            "input224_review_crop_sha_matches": bool(qmatch),
            "historical_input224_sha_mismatch": bool(q and not qmatch),
            "phone_roi_input224": q.get("phone_roi_input224_xyxy") if qmatch else None,
            "new_independence_proven": False,
            "independence_status": "unknown_not_proven",
            "verified_context_ids": {
                k: r["group"][k] for k in ("video_id", "session_id", "room_id", "subject_id")
            },
            "phone_evidence_ref": r["phone_use"]["review"]["evidence_ref"],
            "looking_evidence_ref": r["looking_around"]["review"]["evidence_ref"],
            "phone_reason": r["phone_use"]["reason"],
            "looking_reason": r["looking_around"]["reason"],
            "draft_evidence_refs": refs,
            "input224_evidence_ref": qp + "#" + sid if qmatch else None,
            "exact_image_pairs": [],
            "historical_pairs_valid": [],
        }
        assert not any(row["verified_context_ids"].values()), sid
        rows.append(row)
    byid = {r["sample_id"]: r for r in rows}
    byimage = defaultdict(list)
    for row in rows:
        byimage[row["source_sha256"]].append(row)
    pairs = []
    for image, members in byimage.items():
        for target in ("phone", "looking"):
            for p in [r for r in members if r[target] == "P"]:
                for n in [r for r in members if r[target] == "N"]:
                    pair = {
                        "target": target,
                        "positive_id": p["sample_id"],
                        "negative_id": n["sample_id"],
                        "source_sha256": image,
                        "quality": "same_image_polarity_only",
                        "same_anchor_time_contrast": False,
                        "independent_session_proven": False,
                    }
                    pairs.append(pair)
                    for item in (p, n):
                        item["exact_image_pairs"].append(len(pairs) - 1)
    historical = load("data/interim/pilot-b/v7-targeted-review-20261008-r7/pairs.json")
    historical_targets = {
        p["pair_id"]: p for p in load("artifacts/reports/E004-v7-fit-audit-20261010/pair-join.json")
    }
    valid, invalid = [], []
    for pair in historical:
        p, n = byid.get(pair["positive_id"]), byid.get(pair["negative_id"])
        target = {"phone_use": "phone", "looking_around": "looking"}[
            historical_targets[pair["pair_id"]]["target"]
        ]
        if p and n and p[target] == "P" and n[target] == "N":
            valid.append({**pair, "target_audited": target})
            p["historical_pairs_valid"].append(pair["pair_id"])
            n["historical_pairs_valid"].append(pair["pair_id"])
        else:
            invalid.append(pair["pair_id"])
    comparator = load("artifacts/reports/E004-v7-fit-audit-20261010/comparator-proposal.json")
    old, current = {r["sample_id"]: r for r in v6}, {r["sample_id"]: r for r in v7}
    retained, mapping = [], defaultdict(set)
    for sid in comparator["same_pixel_source_target_mask_context_rights_ids"]:
        a, b = old[sid], current[sid]
        for key in (
            "source",
            "crop",
            "phone_use",
            "looking_around",
            "target_values",
            "target_mask",
            "work_context_review",
            "rights",
        ):
            assert a[key] == b[key], (sid, key)
        assert a["usage"] == b["usage"] == "val"
        retained.append(
            {
                "sample_id": sid,
                "phone": state[b["phone_use"]["state"]],
                "looking": state[b["looking_around"]["state"]],
                "group_id": b["group"]["leakage_group_id"],
            }
        )
    for sid in {r["sample_id"] for r in v6 if r["usage"] == "val"} & {
        r["sample_id"] for r in v7 if r["usage"] == "val"
    }:
        mapping[old[sid]["group"]["leakage_group_id"]].add(
            current[sid]["group"]["leakage_group_id"]
        )
    assert (
        len(mapping) == 14
        and all(len(v) == 1 for v in mapping.values())
        and len({next(iter(v)) for v in mapping.values()}) == 14
    )
    summary = {
        "cohort_definition": "V7 manifest train IDs absent from V6 full review ledger",
        "new_train_unique_source_images": len({r["source_sha256"] for r in rows}),
        "new_train_unique_crop_hashes": len({r["crop_sha256"] for r in rows}),
        "new_train": support(rows),
        "by_source": group_by(rows, "source_id"),
        "by_domain": group_by(rows, "domain"),
        "by_acquisition_bucket_draft": group_by(rows, "bucket_hint_draft"),
        "input224_quality_draft": dict(Counter(r["input224_quality_draft"] for r in rows)),
        "input224_historical_sha_mismatches": sum(
            r["historical_input224_sha_mismatch"] for r in rows
        ),
        "ownership_subtype_draft": dict(
            Counter(r["ownership_subtype_draft"] or "unknown" for r in rows)
        ),
        "parent_linked_crop_counts": dict(Counter(str(r["parent_linked_component"]) for r in rows)),
        "parent_linked_groups": len({r["group_id"] for r in rows if r["parent_linked_component"]}),
        "new_independent_groups_proven": 0,
        "primary_exam_camera_verified": 0,
        "accepted_complete_phenotype_taxonomy_rows": 0,
        "phone_roi_input224_measured": sum(r["phone_roi_input224"] is not None for r in rows),
        "explicit_draft_phenotype_tags": dict(
            Counter(tag for r in rows for tag in r["phenotypes_explicit_draft"])
        ),
        "literal_mentions_not_actual_slice_counts": {
            tag: support(
                [r for r in rows if tag in r["literal_reason_mentions_not_phenotype_labels"]]
            )
            for tag in sorted(
                {tag for r in rows for tag in r["literal_reason_mentions_not_phenotype_labels"]}
            )
        },
        "exact_image_pairs": {
            "raw_pairs": len(pairs),
            "images": len({p["source_sha256"] for p in pairs}),
            "by_target": dict(Counter(p["target"] for p in pairs)),
            "endpoints": len({p[k] for p in pairs for k in ("positive_id", "negative_id")}),
            "both_endpoints_broad_classroom_by_target": {
                target: sum(
                    p["target"] == target
                    and all(
                        byid[p[k]]["domain"] == "classroom_or_exam_context"
                        for k in ("positive_id", "negative_id")
                    )
                    for p in pairs
                )
                for target in ("phone", "looking")
            },
        },
        "r5_pairs": {
            "raw": len(historical),
            "valid": len(valid),
            "invalid": len(invalid),
            "strength": dict(Counter(p["match_strength"] for p in valid)),
        },
        "comparator48": support(retained),
        "val49_registered_groups": len(
            {r["group"]["leakage_group_id"] for r in v7 if r["usage"] == "val"}
        ),
    }
    assert summary["new_train"]["phone"] == {"P": 141, "N": 93, "U": 141}
    assert summary["new_train"]["looking"] == {"P": 97, "N": 163, "U": 115}
    assert summary["exact_image_pairs"]["raw_pairs"] == 22
    dump("coverage-summary.json", summary)
    dump(
        "pairs.json",
        {"exact_image": pairs, "historical_r5_valid": valid, "historical_r5_invalid_ids": invalid},
    )
    dump(
        "comparator48-verification.json",
        {
            "status": "verified_metadata_not_owner_frozen",
            "ids": [r["sample_id"] for r in retained],
            "old14_to_new14": {k: next(iter(v)) for k, v in mapping.items()},
            "comparator48_support": support(retained),
            "top_two_groups": Counter(r["group_id"] for r in retained).most_common(2),
            "full49_mapping_distinct_from_comparator13": True,
        },
    )
    v5 = load("data/processed/pilot-b/pilot-b-20261007-v5/manifest.jsonl")
    old13 = {r["sample_id"] for r in v5 if r["usage"] == "val"}
    added37 = [r for r in v6 if r["usage"] == "val" and r["sample_id"] not in old13]

    def cohort(rs):
        mapped = [
            {
                "sample_id": r["sample_id"],
                "phone": state[r["phone_use"]["state"]],
                "looking": state[r["looking_around"]["state"]],
                "group_id": r["group"]["leakage_group_id"],
            }
            for r in rs
        ]
        return {"ids": [r["sample_id"] for r in mapped], "support": support(mapped)}

    retained36 = [
        current[r["sample_id"]]
        for r in added37
        if r["sample_id"] in current and current[r["sample_id"]]["usage"] == "val"
    ]
    cids = {r["sample_id"] for r in retained}
    comparator35 = [r for r in retained36 if r["sample_id"] in cids]
    assert (len(added37), len(retained36), len(comparator35)) == (37, 36, 35)
    dump(
        "added-development-verification.json",
        {
            "historical_added37": cohort(added37),
            "current_retained36": cohort(retained36),
            "comparator_retained35": cohort(comparator35),
            "status": "measured_not_frozen",
            "removed_from_val": ["V6-CA-041"],
            "changed_label_excluded_from_comparator": ["EXP-SCB-002"],
        },
    )
    scores = load("outputs/E003/predictions-val.json")
    assert (
        PINS["outputs/E003/predictions-val.json"]["sha256"]
        == "19311c32a1943cef682767899c3fc78502fd925717d357e8f69b8010030f8e00"
    )
    score_byid = {r["sample_id"]: r for r in scores}
    baseline = {}
    for i, target in enumerate(("phone", "looking")):
        known = [r for r in retained if r[target] != "U"]
        tp = sum(r[target] == "P" and score_byid[r["sample_id"]]["scores"][i] >= 0.5 for r in known)
        fp = sum(r[target] == "N" and score_byid[r["sample_id"]]["scores"][i] >= 0.5 for r in known)
        p = sum(r[target] == "P" for r in known)
        n = len(known) - p
        baseline[target] = {
            "P": p,
            "N": n,
            "tp": tp,
            "fp": fp,
            "fn": p - tp,
            "tn": n - fp,
            "recall": tp / p,
            "precision": tp / (tp + fp),
            "fpr": fp / n,
        }
    dump(
        "cached-comparator48-baseline.json",
        {"status": "cached_scores_only_no_inference", "threshold": 0.5, "targets": baseline},
    )
    (OUT / "coverage-matrix.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows),
        encoding="utf-8",
    )
    cols = [
        "sample_id",
        "phone",
        "looking",
        "source_id",
        "domain",
        "group_id",
        "parent_linked_component",
        "visual_family_hint_draft",
        "bucket_hint_draft",
        "phenotypes_explicit_draft",
        "phone_ownership",
        "ownership_subtype_draft",
        "input224_quality_draft",
        "historical_input224_sha_mismatch",
        "new_independence_proven",
        "exact_image_pairs",
        "historical_pairs_valid",
        "crop_sha256",
    ]
    with (OUT / "coverage-matrix.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(
                {
                    k: json.dumps(r[k], ensure_ascii=False) if isinstance(r[k], list) else r[k]
                    for k in cols
                }
            )
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return ledger, prov


def run_sources(ledger, prov):
    fingerprints = load(
        "artifacts/reports/pilot-b-v7-targeted-20261008/parent-fingerprints-metadata.json"
    )
    for p in prov.values():
        d = p.get("original_provider_record", {})
        if isinstance(d.get("dhash"), int):
            fingerprints.append(
                {
                    "sha256": p["original_source"]["sha256"],
                    "dhash": d["dhash"],
                    "sample_ids": [p["sample_id"]],
                }
            )
    current_byid = {r["sample_id"]: r for r in ledger}
    current_sha = defaultdict(list)
    for r in ledger:
        current_sha[r["source"]["image_sha256"]].append(r)
    pool = []
    for fp in fingerprints:
        ids = [sid for sid in fp["sample_ids"] if sid in current_byid]
        if ids:
            pool.append(
                {
                    **fp,
                    "sample_ids": ids,
                    "current_usages": sorted({current_byid[s]["usage"] for s in ids}),
                }
            )
    audit = {}
    retained_index = []
    for source, filename in [
        ("StudentClassroomBehavior", "StudentClassroomBehavior.v1i.yolov8.zip"),
        ("behavie", "behavie.v2i.yolov8.zip"),
    ]:
        path = Path("C:/Users/OS/Downloads") / filename
        z = zipfile.ZipFile(path)
        infos = z.infolist()
        names = defaultdict(list)
        for info in infos:
            names[info.filename].append(info)
        duplicate_members = []
        for name, members in names.items():
            if len(members) > 1:
                duplicate_members.append(
                    {
                        "member": name,
                        "copies": len(members),
                        "identical_bytes": len({sha(z.read(m)) for m in members}) == 1,
                    }
                )
        assert all(
            d["member"] == "data.yaml" and d["identical_bytes"] for d in duplicate_members
        ), "Ambiguous ZIP inventory"
        config_infos = names["data.yaml"]
        configs = [yaml.safe_load(z.read(info)) for info in config_infos]
        assert all(c == configs[0] for c in configs)
        config = configs[0]
        classes = {i: n for i, n in enumerate(config["names"])}
        allowed = set(classes)
        images = [
            i
            for i in infos
            if Path(i.filename).suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        labels = {
            i.filename: i for i in infos if "/labels/" in i.filename and i.filename.endswith(".txt")
        }
        raw_groups, rgb_groups, lineages = defaultdict(list), defaultdict(list), defaultdict(list)
        splits, resolutions, counts = Counter(), Counter(), Counter()
        empty, invalid, missing, decode_errors, overlap, triage, records = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
        bbox_dims = defaultdict(list)
        metadata = {
            name: z.read(members[0]).decode("utf-8-sig")
            for name, members in names.items()
            if name in {"README.dataset.txt", "README.roboflow.txt"}
        }
        for idx, info in enumerate(images):
            member = info.filename
            split = member.split("/")[0]
            raw = z.read(info)
            h = sha(raw)
            technical_id = source.upper()[:3] + "-" + h[:16] + "-" + sha(member.encode())[:8]
            splits[split] += 1
            raw_groups[h].append({"id": technical_id, "split": split})
            stem = Path(member).stem
            lineage = re.sub(r"\.rf\.[0-9a-f]+$", "", stem)
            lineages[lineage].append({"id": technical_id, "split": split})
            labelname = member.replace("/images/", "/labels/").rsplit(".", 1)[0] + ".txt"
            boxes = []
            if labelname not in labels:
                missing.append(technical_id)
            else:
                lines = z.read(labels[labelname]).decode("utf-8-sig").splitlines()
                if not any(line.strip() for line in lines):
                    empty.append(technical_id)
                errors = []
                for lineno, line in enumerate(lines, 1):
                    if not line.strip():
                        continue
                    try:
                        b = YoloAnnotation.parse(line)
                        if b.class_id not in allowed:
                            raise DataContractError("Unknown class ID")
                        boxes.append(b)
                    except DataContractError as exc:
                        errors.append({"line": lineno, "error": str(exc)})
                if errors:
                    invalid.append(
                        {
                            "id": technical_id,
                            "label_member_sha256": sha(labelname.encode()),
                            "errors": errors,
                        }
                    )
                    boxes = []  # No partial file statistics.
            try:
                with Image.open(io.BytesIO(raw)) as image:
                    image.load()
                    rgb = image.convert("RGB")
                    width, height = rgb.size
                    resolutions[f"{width}x{height}"] += 1
                    # This method is intentionally raw orientation, matching active dHash.
                    dh = difference_hash(rgb)
                    rh = sha(f"{width}x{height}:".encode() + rgb.tobytes())
                    rgb_groups[rh].append({"id": technical_id, "split": split})
            except (OSError, ValueError) as exc:
                decode_errors.append({"id": technical_id, "error": str(exc)})
                continue
            for b in boxes:
                counts[classes[b.class_id]] += 1
                bbox_dims[classes[b.class_id]].append((b.width * width, b.height * height))
            exact = current_sha.get(h, [])
            if exact:
                overlap.append(
                    {
                        "id": technical_id,
                        "source_sha256": h,
                        "current_sample_ids": [r["sample_id"] for r in exact],
                        "current_usages": sorted({r["usage"] for r in exact}),
                    }
                )
            nearby = [fp for fp in pool if (dh ^ fp["dhash"]).bit_count() <= 4]
            if nearby:
                triage.append(
                    {
                        "id": technical_id,
                        "source_sha256": h,
                        "matched_ids": sorted({sid for fp in nearby for sid in fp["sample_ids"]}),
                        "current_usages": sorted(
                            {u for fp in nearby for u in fp["current_usages"]}
                        ),
                        "min_distance": min((dh ^ fp["dhash"]).bit_count() for fp in nearby),
                        "confirmed_duplicate": False,
                    }
                )
            records.append(
                {
                    "id": technical_id,
                    "member_sha256": sha(member.encode()),
                    "source_sha256": h,
                    "rgb_sha256": rh,
                    "split": split,
                    "width": width,
                    "height": height,
                    "dhash": dh,
                    "source_class_hints": dict(Counter(classes[b.class_id] for b in boxes)),
                    "exact_existing_overlap": bool(exact),
                    "near_existing_flag": bool(nearby),
                    "independence": "unknown_not_proven",
                    "canonical_targets": None,
                }
            )
            if idx and idx % 1500 == 0:
                print(f"{source}: decoded {idx}/{len(images)}", flush=True)

        def duplicate_stats(groups):
            return {
                "unique": len(groups),
                "duplicate_groups": sum(len(v) > 1 for v in groups.values()),
                "duplicate_file_copies": sum(len(v) - 1 for v in groups.values()),
                "cross_split_groups": sum(
                    len({x["split"] for x in v}) > 1 for v in groups.values()
                ),
            }

        def quantile(vals, q):
            s = sorted(vals)
            return s[round((len(s) - 1) * q)] if s else None

        shortlisted = []
        families_seen = set()
        for hint in [
            "phone",
            "Using_phone",
            "Look Around",
            "turn_head",
            "Normal",
            "writing",
            "reading",
            "Bend Over The Desk",
            "Hand Under Table",
        ]:
            candidates = [
                r
                for r in records
                if hint in r["source_class_hints"]
                and not r["exact_existing_overlap"]
                and not r["near_existing_flag"]
            ]
            for r in sorted(candidates, key=lambda x: x["source_sha256"]):
                if r["rgb_sha256"] in families_seen:
                    continue
                shortlisted.append(
                    {
                        **r,
                        "priority_hint": hint,
                        "selection_reason": (
                            "source_class_hint_hash_order_unique_rgb_"
                            "no_cached_overlap_flag_not_independence_proof"
                        ),
                    }
                )
                families_seen.add(r["rgb_sha256"])
                if sum(x["priority_hint"] == hint for x in shortlisted) >= 4:
                    break
        audit[source] = {
            "archive_filename": filename,
            "archive_sha256": file_sha(path),
            "archive_size": path.stat().st_size,
            "provider": config["roboflow"],
            "owner_use_authorization": (
                "2026-10-11 owner xác nhận quyền sử dụng cả hai, "
                "scope xử lý local; không hỏi lại quyền"
            ),
            "readme_metadata": metadata,
            "duplicate_zip_members": duplicate_members,
            "images": len(images),
            "splits": dict(splits),
            "label_files": len(labels),
            "missing_labels": missing,
            "orphan_labels": len(
                set(labels)
                - {
                    i.filename.replace("/images/", "/labels/").rsplit(".", 1)[0] + ".txt"
                    for i in images
                }
            ),
            "empty_label_files": len(empty),
            "invalid_label_files": len(invalid),
            "invalid_lines": sum(len(r["errors"]) for r in invalid),
            "invalid_label_details": invalid,
            "decode_failures": decode_errors,
            "strict_valid_annotation_counts": dict(counts),
            "resolutions": dict(resolutions),
            "source_bbox_pixel_stats_not_person_crop": {
                k: {
                    "count": len(v),
                    "min_width": min(x[0] for x in v),
                    "min_height": min(x[1] for x in v),
                    "median_width": quantile([x[0] for x in v], 0.5),
                    "median_height": quantile([x[1] for x in v], 0.5),
                }
                for k, v in bbox_dims.items()
            },
            "byte_duplicate_stats": duplicate_stats(raw_groups),
            "rgb_duplicate_stats": duplicate_stats(rgb_groups),
            "filename_lineage_flags_not_groups": duplicate_stats(lineages),
            "exact_v7_image_overlap": {
                "count": len(overlap),
                "by_usage": dict(Counter(u for r in overlap for u in r["current_usages"])),
                "details": overlap,
            },
            "dhash64_le4_existing_screening": {
                "flagged_images": len(triage),
                "by_usage": dict(Counter(u for r in triage for u in r["current_usages"])),
                "fingerprint_records": len(pool),
                "details": triage,
                "not_complete_overlap_exclusion": True,
            },
            "new_independent_groups_proven": 0,
            "camera_session_metadata_supplied": False,
            "draft_shortlist": shortlisted,
        }
        retained_index.extend({**r, "source": source} for r in records)
        print(
            source,
            json.dumps(
                {
                    k: audit[source][k]
                    for k in (
                        "images",
                        "splits",
                        "strict_valid_annotation_counts",
                        "invalid_label_files",
                        "invalid_lines",
                        "byte_duplicate_stats",
                        "rgb_duplicate_stats",
                    )
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
    # Compare the two new exports without asserting absence of semantic lineage.
    cross = {}
    for key in ("source_sha256", "rgb_sha256"):
        a = {r[key] for r in retained_index if r["source"] == "StudentClassroomBehavior"}
        b = {r[key] for r in retained_index if r["source"] == "behavie"}
        cross[key] = {"shared_unique_hashes": len(a & b)}
    dump(
        "source-zip-audit.json",
        {
            "sources": audit,
            "cross_new_sources": cross,
            "limits": (
                "Không chứng minh independence từ SHA/dHash/project/filename. "
                "Không audit toàn upstream đã dùng; không dùng upstream splits làm holdout. "
                "Không inference."
            ),
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-only", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.metadata_only and (OUT / "input-pins.json").is_file():
        PINS.update(json.loads((OUT / "input-pins.json").read_text(encoding="utf-8")))
    ledger, prov = run_metadata()
    if not args.metadata_only:
        run_sources(ledger, prov)
    pin_context()
    dump("input-pins.json", PINS)
