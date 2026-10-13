"""Verify pinned inputs, review-only proposals and deterministic pixel reconstruction."""

import argparse
import hashlib
import io
import json
from collections import Counter
from importlib.metadata import version
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import preview_input

REPORT = Path("artifacts/reports/E004-source-review-20261011")
ROOT = Path("data/interim/E004-source-review-20261011")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def validate(output):
    direction = json.loads((REPORT / "owner-direction.json").read_text(encoding="utf-8"))
    assert all(sha256_file(Path(p)) == digest for p,digest in direction["input_sha256"].items())
    config_path = Path("configs/datasets/e004_source_review_20261011.yaml")
    config = load_yaml(config_path)
    assert sha256_file(Path(config["parent_manifest"])) == config["parent_manifest_sha256"]
    assert sha256_file(Path(config["source_audit"])) == config["source_audit_sha256"]
    audit = json.loads(Path(config["source_audit"]).read_text(encoding="utf-8"))
    source_counts = {}
    for source in config["sources"]:
        assert sha256_file(Path(source["archive"])) == source["archive_sha256"]
        inventory = json.loads((ROOT / (source["id"] + "-inventory.json")).read_text(encoding="utf-8"))
        selected = json.loads((ROOT / (source["id"] + "-inspection.json")).read_text(encoding="utf-8"))
        originals = audit["sources"][source["audit_key"]]["draft_shortlist"]
        assert len(selected) == 60 and len({r["source_sha256"] for r in selected}) == 60
        assert [(r["review_id"],r["source_sha256"],r["member_sha256"]) for r in selected[:20]] == [(r["id"],r["source_sha256"],r["member_sha256"]) for r in originals]
        assert all(not r["cached_overlap_flag"] for r in selected[20:])
        assert all(r["canonical_targets"] == [None,None] and r["canonical_mask"] == [0,0] and r["usage"] == "review_only" for r in inventory)
        invalid = json.loads((ROOT / (source["id"] + "-invalid.json")).read_text(encoding="utf-8"))
        source_counts[source["id"]] = {"valid_file_inventory":len(inventory), "invalid_label_files_quarantined":len(invalid), "selected":len(selected)}
    parent = [json.loads(x) for x in Path(config["parent_manifest"]).read_text(encoding="utf-8").splitlines()]
    test_sources = {r["source"]["image_sha256"] for r in parent if r["usage"] == "test"}
    fingerprints = json.loads((ROOT / "non-test-parent-scene-fingerprints.json").read_text(encoding="utf-8"))
    assert len(fingerprints) == 629 and test_sources.isdisjoint(r["source_sha256"] for r in fingerprints)
    qa = json.loads((REPORT / "pilot-input224-review.json").read_text(encoding="utf-8"))
    assert len(qa) == 58 and len({r["candidate_id"] for r in qa}) == 58
    pins = {}
    for row in qa:
        directory = Path(row["media_directory"])
        assert row["canonical_targets"] == [None,None] and row["canonical_mask"] == [0,0]
        assert row["usage"] == "review_only" and row["split"] is None and row["owner_approved"] is False
        assert row["independence_proven"] is False
        assert sha256_file(directory / "source.bin") == row["source_sha256"]
        with Image.open(directory / "source.bin") as source:
            crop = source.convert("RGB").crop(row["context_xyxy"])
        stream = io.BytesIO(); crop.save(stream,format="PNG")
        assert hashlib.sha256(stream.getvalue()).hexdigest() == row["crop_sha256"]
        prepared = preview_input(crop, row["input_size"], tuple(row["fill"]))
        stream = io.BytesIO(); prepared.save(stream,format="PNG")
        assert hashlib.sha256(stream.getvalue()).hexdigest() == row["input_sha256"]
        assert hashlib.sha256(prepared.tobytes()).hexdigest() == row["input_pixel_sha256"]
        assert sha256_file(directory / "crop.png") == row["crop_sha256"]
        assert sha256_file(directory / "input.png") == row["input_sha256"]
        pins[row["candidate_id"]] = {"source_sha256":row["source_sha256"],"crop_sha256":row["crop_sha256"],"input_sha256":row["input_sha256"]}
    matrix = [json.loads(x) for x in (REPORT.parent / "E004-post-v7-audit-20261011/coverage-matrix.jsonl").read_text(encoding="utf-8").splitlines()]
    cells = [(row,target) for row in matrix for target in ("phone","looking") if row[target] == "U"]
    assert len(matrix) == 375 and len(cells) == 256
    queue = []
    for target in ("phone","looking"):
        eligible = [r for r in matrix if r[target] == "U"]
        eligible.sort(key=lambda r:(not r["historical_input224_sha_mismatch"], r["input224_quality_draft"] != "ambiguous", r["input224_quality_draft"] != "unknown", r["source_id"],r["sample_id"]))
        seen = set()
        for r in eligible:
            if r["source_family_conservative"] in seen: continue
            seen.add(r["source_family_conservative"])
            queue.append({"sample_id":r["sample_id"],"target_to_review":target,"current_state":"U", "crop_sha256":r["crop_sha256"],
                          "source_id":r["source_id"], "conservative_group":r["source_family_conservative"], "independence_proven":False,
                          "existing_reason_verbatim":r[target+"_reason"],"existing_evidence_ref":r[target+"_evidence_ref"],
                          "input224_quality_existing_draft":r["input224_quality_draft"], "old_review_crop_sha_mismatch":r["historical_input224_sha_mismatch"],
                          "unknown_cause_taxonomy":None,"new_state_proposal":None,"trigger":"only_if_accepted_train_supplement_still_has_specific_gap",
                          "action":"source_crop_input224_review_only_no_relabel_or_recrop_in_place"})
            if sum(q["target_to_review"] == target for q in queue) == 16: break
    write(output / "unknown-review-queue.json", {"status":"conditional_not_activated", "total_unknown_cells":256,
          "unknown_cells_by_target":dict(Counter(t for _,t in cells)), "queue_cells":queue, "no_current_labels_changed":True})
    checks_path = REPORT / "software-checks.json"
    checks = json.loads(checks_path.read_text(encoding="utf-8")) if checks_path.exists() else {"status":"pending"}
    result = {"status":"PASS" if checks.get("scope_checks_passed") else "DATA_PASS_SOFTWARE_PENDING", "source_inventory":source_counts,
              "owner_approved_input_hashes_preserved":direction["input_sha256"], "parent_manifest_sha256":config["parent_manifest_sha256"],
              "non_test_source_comparisons":len(fingerprints), "test_media_hashes_excluded":True, "original_shortlist_order_and_pins_preserved":True,
              "source_to_crop_to_input_pixel_reconstruction_count":len(qa),"new_independent_groups_proven":0,
              "no_canonical_supervised_assignments_created":True, "unknown_256_cells_preserved":True,
              "environment":{"Pillow":version("Pillow"),"numpy":version("numpy"),"PyYAML":version("PyYAML")},
              "software_checks":checks, "report_file_sha256":{str(p).replace("\\","/"):sha256_file(p) for p in sorted(REPORT.iterdir()) if p.is_file() and p.name not in {"validation.json"}},
              "config_sha256":sha256_file(config_path), "interim_evidence_pins":{str(p).replace("\\","/"):sha256_file(p) for p in sorted(ROOT.glob("*.json"))},
              "crop_input_pins":pins,
              "historical_seal_mismatch":"Known prior E004-v7-fit README seal mismatch preserved; not repaired or resealed"}
    write(output / "validation.json", result)


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=REPORT)
    validate(parser.parse_args().output)
