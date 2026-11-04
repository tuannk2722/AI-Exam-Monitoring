"""Pinned detector-only ablation; never loads a behavior classifier or selects a winner."""
from __future__ import annotations

import argparse
import html
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from PIL import Image, ImageDraw

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_config import FilePin, local_path
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    digest_json,
    environment,
    write_json,
)

from .person import PersonDetection, PersonDetector, crop_boxes
from .runtime_config import RuntimeConfig, load_runtime_config


def read_object(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise DataContractError("Expected JSON object")
    return raw


def draft_review(cohort: dict[str, Any], cohort_sha: str) -> dict[str, Any]:
    """Prefill candidate groups from existing review hypotheses, never accepted labels."""
    frames = []
    # Candidate pairs only; no new geometric matching threshold is introduced.
    pairs = cohort.get("pair_candidates", [])
    for frame in cohort["frames"]:
        groups = [{o["anchor_id"]} for o in frame["baseline_observations"]]
        cases = [c for c in pairs if c["frame_index"] == frame["frame_index"]]
        for case in cases:
            if case["draft_relation"] == "same_person_candidate":
                members = set(case["anchor_ids"])
                matching = [g for g in groups if g & members]
                if matching:
                    merged = set().union(*matching)
                    groups = [g for g in groups if not g & members] + [merged]
        groups.sort(key=lambda g: min(g))
        people = []
        assignment = {}
        observations = {o["anchor_id"]: o for o in frame["baseline_observations"]}
        for i, group in enumerate(groups):
            person_id = f"p{i + 1:03d}"
            boxes = [observations[a]["person_box"] for a in sorted(group)]
            people.append({"person_id": person_id,
                           "location_description": f"Vùng box baseline: {boxes}",
                           "draft_anchor_ids": sorted(group)})
            assignment.update({a: person_id for a in sorted(group)})
        frames.append({"frame_index": frame["frame_index"], "source_png": frame["source_png"],
                       "complete_visible_person_census": False, "people": people,
                       "baseline_assignment": assignment,
                       "unresolved_cases": ["Kiểm toàn frame: người bị bỏ sót, box giả, nhóm trùng"]
                       + [c["case_id"] for c in cases]})
    return {"schema_version": "detector-person-review-v1", "status": "draft",
            "cohort_sha256": cohort_sha, "reviewer": None, "decision_ref": None,
            "note": "Nhóm tự điền từ baseline và candidate có sẵn; không là ground truth. "
                    "Thêm người baseline bỏ sót; null assignment chỉ dành cho box giả đã review.",
            "frames": frames}


def validate_review(review: dict[str, Any], cohort: dict[str, Any], cohort_sha: str) -> None:
    """Require a complete owner-reviewed census, including baseline misses, before inference."""
    if (review.get("schema_version") != "detector-person-review-v1"
            or review.get("status") != "accepted"
            or review.get("cohort_sha256") != cohort_sha
            or not review.get("decision_ref")
            or review.get("reviewer") != "repository-owner"):
        raise DataContractError("Owner-reviewed person census is required before detector run")
    frames = review.get("frames", [])
    if [r.get("frame_index") for r in frames] != [f["frame_index"] for f in cohort["frames"]]:
        raise DataContractError("Review must cover the exact ordered cohort")
    for row, frame in zip(frames, cohort["frames"], strict=True):
        people = row.get("people", [])
        ids = [p.get("person_id") for p in people]
        mapping = row.get("baseline_assignment", {})
        anchors = {o["anchor_id"] for o in frame["baseline_observations"]}
        if (row.get("complete_visible_person_census") is not True
                or any(not isinstance(p, str) or not p or p == "unknown" for p in ids)
                or len(ids) != len(set(ids))
                or any(not p.get("location_description") for p in people)
                or set(mapping) != anchors
                or any(p is not None and p not in ids for p in mapping.values())
                or row.get("unresolved_cases") != []):
            raise DataContractError("Incomplete person census or unresolved baseline matching")


def preflight(config_path: Path, workspace: Path) -> tuple[
    dict[str, Any], RuntimeConfig, dict[str, Any], dict[str, Any]
]:
    raw = load_yaml(config_path)
    if (raw.get("schema_version") not in {"detector-ablation-config-v1",
                                          "detector-ablation-config-v2"}
            or raw.get("classifier_inference") is not False
            or raw.get("role_policy") != "unknown_diagnostic_only"):
        raise DataContractError("Unsupported detector-only scope")
    approval = read_object(local_path(workspace, raw["approval_ref"]))
    if (approval.get("status") != "approved"
            or approval.get("run_id") != raw["run_id"]
            or approval.get("config_sha256") != digest_json(raw)):
        raise DataContractError("Detector ablation approval/config mismatch")
    if raw["schema_version"] == "detector-ablation-config-v2":
        if (raw.get("review_policy") != "diagnostic_unknown_no_selection"
                or "detector_only_diagnostic_with_unknowns" not in approval.get("scope", [])
                or approval.get("cohort_labels_accepted") is not False
                or approval.get("quality_acceptance") is not False):
            raise DataContractError("Explicit diagnostic exception approval is required")
        FilePin(**raw["pins"]["draft_review"]).verify(workspace)
        FilePin(**raw["pins"]["diagnostic_decision"]).verify(workspace)
        if approval.get("decision_ref") != raw["pins"]["diagnostic_decision"]:
            raise DataContractError("Diagnostic decision pin mismatch")
    pins = raw["pins"]
    proposal = load_yaml(FilePin(**pins["proposal"]).verify(workspace))
    if raw["arms"] != proposal["arms"] or raw["frame_indices"] != proposal["frame_indices"]:
        raise DataContractError("Executable variables differ from approved proposal")
    baseline = load_runtime_config(FilePin(**pins["baseline_runtime"]).verify(workspace), workspace)
    cohort = FilePin(**pins["cohort"]).read_json(workspace)
    session = FilePin(**pins["session"]).read_json(workspace)
    rights_path = FilePin(**pins["media_approval"]).verify(workspace)
    rights = read_object(rights_path)
    checksums_path = FilePin(**cohort["session_checksums"]).verify(workspace)
    checksums = read_object(checksums_path)
    predictions_path = FilePin(**cohort["source_predictions"]).verify(workspace)
    cached_rows = [json.loads(s) for s in predictions_path.read_text(encoding="utf-8").splitlines()]
    cached = {r["frame_index"]: r for r in cached_rows if r.get("record_type") == "frame"}
    expected_rights = {"schema_version": "runtime-media-approval-v1", "status": "approved",
                       "runtime_id": baseline.raw["runtime_id"],
                       "use_scope": "local_prototype_qa", "source_sha256": cohort["source_sha256"],
                       "test_or_holdout": False, "rights_confirmed": True,
                       "third_party_processing": False, "access": "repository_owner",
                       "retention_days": 7}
    if (any(rights.get(k) != v for k, v in expected_rights.items())
            or not rights.get("decision_ref")
            or session["media_approval_sha256"] != sha256_file(rights_path)
            or session["status"] != "completed"
            or session["runtime_id"] != baseline.raw["runtime_id"]
            or session["config_sha256"] != baseline.sha256
            or session["source_sha256"] != cohort["source_sha256"]
            or session["media_delete_by"] != cohort["media_delete_by"]
            or datetime.now(UTC) >= datetime.fromisoformat(cohort["media_delete_by"])):
        raise DataContractError("Source session/rights/retention mismatch or expired media")
    if ([f["frame_index"] for f in cohort["frames"]] != raw["frame_indices"]
            or len(set(raw["frame_indices"])) != len(raw["frame_indices"])
            or [a["id"] for a in raw["arms"]] != ["D0", "D1", "D2"]):
        raise DataContractError("Unexpected ablation cohort or arms")
    for frame in cohort["frames"]:
        path = FilePin(**frame["source_png"]).verify(workspace)
        if (checksums.get(path.name) != frame["source_png"]["sha256"]
                or cached[frame["frame_index"]]["observations"] != frame["baseline_observations"]
                or cached[frame["frame_index"]]["video_time_ms"] != frame["video_time_ms"]):
            raise DataContractError("Cohort differs from cached source session")
    if checksums.get(predictions_path.name) != sha256_file(predictions_path):
        raise DataContractError("Cached prediction checksum mismatch")
    for arm in raw["arms"]:
        if (set(arm) != {"id", "conf", "iou"}
                or not 0 <= arm["conf"] <= 1 or not 0 <= arm["iou"] <= 1):
            raise DataContractError("Invalid ablation arm")
    if raw["arms"][0] != {"id": "D0", "conf": baseline.raw["detector"]["conf"],
                           "iou": baseline.raw["detector"]["iou"]}:
        raise DataContractError("D0 must reproduce baseline detector variables")
    return raw, baseline, cohort, approval


def serialize_boxes(detections: list[PersonDetection], size: tuple[int, int],
                    margins: dict[str, float]) -> list[dict[str, Any]]:
    result = []
    for index, detection in enumerate(detections):
        person, context = crop_boxes(detection, size, margins)
        result.append({"box_id": f"b{index:03d}", "xyxy_float": list(detection.xyxy),
                       "person_box": list(person), "context_box": list(context),
                       "detector_confidence": detection.confidence})
    return result


def assert_baseline_parity(actual: list[dict[str, Any]], cached: list[dict[str, Any]]) -> None:
    keys = ("person_box", "context_box", "detector_confidence")
    if [{k: b[k] for k in keys} for b in actual] != [{k: b[k] for k in keys} for b in cached]:
        raise DataContractError("D0 parity failed; stop before candidate arms and explain drift")


def validate_run_review(raw: dict[str, Any], review: dict[str, Any],
                        cohort: dict[str, Any], review_sha: str) -> None:
    if raw.get("schema_version") == "detector-ablation-config-v2":
        if (raw.get("review_policy") != "diagnostic_unknown_no_selection"
                or review_sha != raw["pins"]["draft_review"]["sha256"]
                or review.get("schema_version") != "detector-person-review-v1"
                or review.get("status") != "draft"
                or review.get("cohort_sha256") != raw["pins"]["cohort"]["sha256"]
                or [f["frame_index"] for f in review["frames"]]
                != [f["frame_index"] for f in cohort["frames"]]):
            raise DataContractError("Diagnostic input must retain the pinned draft and cohort")
    else:
        validate_review(review, cohort, raw["pins"]["cohort"]["sha256"])


def run_ablation(config_path: Path, workspace: Path, review_path: Path, output: Path) -> None:
    if output.exists():
        raise DataContractError("Ablation output must be new")
    if not output.resolve().is_relative_to((workspace / "outputs").resolve()):
        raise DataContractError("Ablation output must remain under workspace outputs")
    raw, baseline, cohort, approval = preflight(config_path, workspace)
    review = read_object(review_path)
    review_sha = sha256_file(review_path)
    validate_run_review(raw, review, cohort, review_sha)
    output.mkdir(parents=True, exist_ok=False)
    record: dict[str, Any] = {"run_id": raw["run_id"], "status": "running",
                              "started_at": datetime.now(UTC).isoformat(),
                              "config_sha256": digest_json(raw), "review_sha256": review_sha,
                              "media_delete_by": cohort["media_delete_by"],
                              "completed_forwards": 0, "quality_acceptance": "pending_review"}
    if raw.get("schema_version") == "detector-ablation-config-v2":
        record.update(review_policy=raw["review_policy"],
                      quality_acceptance="not_evaluated_diagnostic", winner=None)
    sections: list[str] = []
    matching: list[dict[str, Any]] = []
    write_json(output / "run.json", record)
    try:
        write_json(output / "config.json", raw)
        write_json(output / "approval.json", approval)
        write_json(output / "person-review.json", review)
        write_json(output / "code-provenance.json", code_identity())
        torch.set_num_threads(baseline.raw["classifier"]["threads"])
        write_json(output / "environment.json", environment())
        # A fresh detector call uses each arm's NMS; never re-suppress cached boxes.
        detector = PersonDetector(baseline)
        with (output / "detections.jsonl").open("x", encoding="utf-8") as handle:
            for arm in raw["arms"]:
                detector.variables = {**baseline.raw["detector"],
                                      "conf": arm["conf"], "iou": arm["iou"]}
                for frame in cohort["frames"]:
                    if datetime.now(UTC) >= datetime.fromisoformat(cohort["media_delete_by"]):
                        raise DataContractError("Media retention expired during run")
                    path = FilePin(**frame["source_png"]).verify(workspace)
                    with Image.open(path) as source:
                        image = source.convert("RGB")
                    boxes = serialize_boxes(detector.predict(image), image.size,
                                            baseline.raw["crop"])
                    record["completed_forwards"] += 1
                    row = {"arm": arm["id"], "frame_index": frame["frame_index"],
                           "video_time_ms": frame["video_time_ms"],
                           "source_png": frame["source_png"], "boxes": boxes}
                    handle.write(json.dumps(row, allow_nan=False) + "\n")
                    handle.flush()
                    if arm["id"] == "D0":
                        assert_baseline_parity(boxes, frame["baseline_observations"])
                    draw = ImageDraw.Draw(image)
                    for box in boxes:
                        draw.rectangle(box["person_box"], outline="red", width=2)
                        draw.text(tuple(box["person_box"][:2]), box["box_id"], fill="yellow")
                    name = f'{arm["id"]}-f{frame["frame_index"]:08d}.png'
                    image.save(output / name)
                    sections.append(f'<section><h2>{html.escape(name)}</h2>'
                                    f'<img src="{name}" style="max-width:100%"></section>')
                    matching.append({"arm": arm["id"], "frame_index": frame["frame_index"],
                                     "assignment": {b["box_id"]: "unknown" for b in boxes}})
        if sha256_file(review_path) != review_sha:
            raise DataContractError("Person review changed during run")
        record["status"] = "completed"
    except BaseException as exc:
        record.update(status="failed", error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        record["ended_at"] = datetime.now(UTC).isoformat()
        write_json(output / "run.json", record)
        write_json(output / "matching-draft.json", {"status": "draft", "frames": matching})
        (output / "index.html").write_text(
            '<!doctype html><html lang="vi"><meta charset="utf-8">'
            '<title>Đối chứng detector</title><h1>Đối chứng detector — chưa nghiệm thu</h1>'
            f'<p>Trạng thái: {record["status"]}. Không chọn winner từ số boxes.</p>'
            + "".join(sections) + "</html>", encoding="utf-8")
        checksum_artifacts(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--review", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--draft-review", type=Path,
                        help="Create a new draft census from cached candidates, without inference")
    args = parser.parse_args()
    if args.draft_review:
        if args.draft_review.exists():
            parser.error("Draft output must be new")
        raw, _, cohort, _ = preflight(args.config, args.workspace)
        draft = draft_review(cohort, raw["pins"]["cohort"]["sha256"])
        with args.draft_review.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(draft, ensure_ascii=False, indent=2) + "\n")
        print("Draft census prepared; owner review required. No inference.")
    elif args.preflight_only:
        raw, _, cohort, _ = preflight(args.config, args.workspace)
        if args.review:
            validate_run_review(raw, read_object(args.review), cohort, sha256_file(args.review))
        print("Input integrity PASS; no inference. Review policy: "
              + raw.get("review_policy", "accepted_census_required"))
    else:
        if args.review is None or args.output is None:
            parser.error("--review and --output are required for a run")
        run_ablation(args.config, args.workspace, args.review, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
