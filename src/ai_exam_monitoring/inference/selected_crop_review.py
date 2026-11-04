"""Review a selected detector arm, reusing only verified identical cached classifier inputs."""
from __future__ import annotations

import argparse
import html
import math
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image

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

from .classifier import BundleClassifier
from .detector_review import preflight, read_object
from .runtime_config import load_runtime_config, media_deadline


def normalize_comparison(rows: list[dict[str, Any]], cohort: dict[str, Any],
                         arm: str) -> list[dict[str, Any]]:
    frames = {f["frame_index"]: f for f in cohort["frames"]}
    result = []
    for row in rows:
        if row["arm"] != arm:
            continue
        frame = frames.get(row["frame_index"])
        if frame is None or row["source"] != frame["source_png"]:
            raise DataContractError("Comparison source mismatch")
        boxes = []
        for b in row["boxes"]:
            box_id = b["anchor_id"].split("-")[-1]
            if b["anchor_id"] != f'f{row["frame_index"]:08d}-{arm}-{box_id}':
                raise DataContractError("Comparison anchor mismatch")
            boxes.append({"box_id": box_id, "xyxy_float": b["xyxy_float"],
                          "person_box": b["person_box"], "context_box": b["context_box"],
                          "detector_confidence": b["confidence"]})
        result.append({"frame_index": row["frame_index"], "arm": arm, "boxes": boxes,
                       "source_png": row["source"], "video_time_ms": frame["video_time_ms"]})
    return result


def exact_cached_match(
    box: dict[str, Any], observations: list[dict[str, Any]],
) -> dict[str, Any] | None:
    keys = ("person_box", "context_box", "detector_confidence")
    matches = [o for o in observations if all(o[k] == box[k] for k in keys)]
    if len(matches) > 1:
        raise DataContractError("Ambiguous cached anchor; cannot reuse prediction")
    return matches[0] if matches else None


def verify_image(path: Path, expected: Image.Image, expected_sha: str) -> None:
    if sha256_file(path) != expected_sha:
        raise DataContractError("Cached image checksum mismatch")
    with Image.open(path) as image:
        if (image.mode != expected.mode or image.size != expected.size
                or image.tobytes() != expected.tobytes()):
            raise DataContractError("Cached image pixels differ from selected input")


def run_review(config_path: Path, workspace: Path, output: Path) -> None:
    import json

    workspace = workspace.resolve()
    output = output.resolve()
    if output.exists() or not output.is_relative_to(workspace / "outputs"):
        raise DataContractError("Review output must be new under workspace outputs")
    raw = load_yaml(config_path)
    approval = read_object(local_path(workspace, raw["approval_ref"]))
    comparison = raw.get("schema_version") == "selected-crop-review-v2"
    if (raw.get("schema_version") not in {"selected-crop-review-v1", "selected-crop-review-v2"}
            or approval.get("status") != "approved"
            or approval.get("run_id") != raw["run_id"]
            or approval.get("config_sha256") != digest_json(raw)
            or "selected_arm_crop_g0_review" not in approval.get("scope", [])):
        raise DataContractError("Selected crop review approval mismatch")
    paths = {k: FilePin(**v).verify(workspace) for k, v in raw["pins"].items()}
    winner = read_object(paths["winner"])
    if winner.get("status") != "accepted" or winner.get("winner") != raw["selected_arm"]:
        raise DataContractError("Selected detector winner mismatch")
    for pin in winner["evidence"].values():
        FilePin(**pin).verify(workspace)
    if comparison:
        baseline = load_runtime_config(paths["runtime_config"], workspace)
        cohort = read_object(paths["cohort"])
        diagnostic_config = load_yaml(paths["diagnostic_config"])
        media_deadline(cohort)
    else:
        diagnostic_config, baseline, cohort, _ = preflight(paths["diagnostic_config"], workspace)
    checks = read_object(paths["diagnostic_checksums"])
    for key in ("detections", "diagnostic_run"):
        if checks.get(paths[key].name) != sha256_file(paths[key]):
            raise DataContractError("Diagnostic output mismatch")
    diagnostic = read_object(paths["diagnostic_run"])
    config_sha = (sha256_file(paths["diagnostic_config"]) if comparison
                  else digest_json(diagnostic_config))
    if (diagnostic["status"] != "completed" or diagnostic["config_sha256"] != config_sha):
        raise DataContractError("Diagnostic did not complete")
    rows = (normalize_comparison(read_object(paths["detections"])["frames"], cohort,
                                 raw["selected_arm"]) if comparison else
            [json.loads(s) for s in paths["detections"].read_text().splitlines()])
    selected = [r for r in rows if r["arm"] == raw["selected_arm"]]
    if [r["frame_index"] for r in selected] != [f["frame_index"] for f in cohort["frames"]]:
        raise DataContractError("Selected frames differ from cohort")
    frames = {f["frame_index"]: f for f in cohort["frames"]}
    for row in selected:
        if (row["source_png"] != frames[row["frame_index"]]["source_png"]
                or row["video_time_ms"] != frames[row["frame_index"]]["video_time_ms"]):
            raise DataContractError("Selected source frame/time mismatch")
    plan = [(r, b, exact_cached_match(b, frames[r["frame_index"]]["baseline_observations"]))
            for r in selected for b in r["boxes"]]
    new_count = sum(old is None for _, _, old in plan)
    if new_count != raw["new_crop_forwards"] or len(plan) - new_count != raw["cached_crops"]:
        raise DataContractError("Selected crop scope changed")
    source_checks_path = FilePin(**cohort["session_checksums"]).verify(workspace)
    source_checks = read_object(source_checks_path)
    session_dir = source_checks_path.parent
    media_deadline(cohort)
    output.mkdir(parents=True, exist_ok=False)
    record: dict[str, Any] = {"run_id": raw["run_id"], "status": "running",
                              "started_at": datetime.now(UTC).isoformat(),
                              "media_delete_by": cohort["media_delete_by"],
                              "new_forwards": 0, "cached_predictions": 0,
                              "quality_acceptance": "pending_crop_attribution_review"}
    results: list[dict[str, Any]] = []
    sections: list[str] = []
    thresholds: list[float] | None = None
    try:
        write_json(output / "config.json", raw)
        write_json(output / "approval.json", approval)
        write_json(output / "code-provenance.json", code_identity())
        classifier = BundleClassifier(baseline)
        thresholds = classifier.thresholds
        write_json(output / "environment.json", environment())
        for row, box, cached in plan:
            if datetime.now(UTC) >= datetime.fromisoformat(cohort["media_delete_by"]):
                raise DataContractError("Media retention expired")
            frame = frames[row["frame_index"]]
            with Image.open(FilePin(**frame["source_png"]).verify(workspace)) as source:
                crop = source.convert("RGB").crop(box["context_box"])
            preview = classifier.preview(crop)
            anchor = f'f{row["frame_index"]:08d}-{raw["selected_arm"]}-{box["box_id"]}'
            if cached is not None:
                crop_path = session_dir / f'{cached["anchor_id"]}-crop.png'
                input_path = session_dir / f'{cached["anchor_id"]}-input.png'
                verify_image(crop_path, crop, source_checks[crop_path.name])
                verify_image(input_path, preview, source_checks[input_path.name])
                scores = cached["scores"]
                record["cached_predictions"] += 1
                origin = {"kind": "verified_cached_prediction",
                          "baseline_anchor": cached["anchor_id"],
                          "predictions": cohort["source_predictions"]}
            else:
                scores = classifier.predict(crop)
                record["new_forwards"] += 1
                crop_path = output / f"{anchor}-crop.png"
                input_path = output / f"{anchor}-input.png"
                crop.save(crop_path)
                preview.save(input_path)
                origin = {"kind": "new_g0_forward", "baseline_anchor": None}
            if len(scores) != 2 or any(not math.isfinite(s) or not 0 <= s <= 1 for s in scores):
                raise DataContractError("Invalid classifier scores")
            result = {"anchor_id": anchor, "frame_index": row["frame_index"],
                      "video_time_ms": row["video_time_ms"], **box, "scores": scores,
                      "above_threshold": [s >= t for s, t in
                                          zip(scores, classifier.thresholds, strict=True)],
                      "origin": origin,
                      "crop": {"path": crop_path.relative_to(workspace).as_posix(),
                               "sha256": sha256_file(crop_path)},
                      "input": {"path": input_path.relative_to(workspace).as_posix(),
                                "sha256": sha256_file(input_path)}}
            results.append(result)
            sections.append(f'<figure><figcaption>{html.escape(anchor)} — '
                            f'{html.escape(origin["kind"])}<br>phone={scores[0]:.4f}; '
                            f'looking={scores[1]:.4f}</figcaption>'
                            f'<img src="{Path(os.path.relpath(crop_path, output)).as_posix()}">'
                            f'<img src="{Path(os.path.relpath(input_path, output)).as_posix()}">'
                            '</figure>')
        media_deadline(cohort)
        record["status"] = "completed"
    except BaseException as exc:
        record.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        record["ended_at"] = datetime.now(UTC).isoformat()
        write_json(output / "run.json", record)
        write_json(output / "predictions.json", {"records": results,
                   "provenance": raw["pins"], "thresholds": thresholds})
        (output / "index.html").write_text(
            '<!doctype html><html lang="vi"><meta charset="utf-8"><title>Crop/G0 QA</title>'
            '<style>body{font:16px system-ui;margin:24px}figure{display:inline-block;'
            'vertical-align:top;width:420px;border:1px solid #ccc;padding:12px;margin:8px}'
            'img{max-width:200px;max-height:250px}figcaption{overflow-wrap:anywhere}</style>'
            f'<h1>{html.escape(raw["selected_arm"])} — kiểm crop và G0</h1>'
            '<p>Detector đã được owner chọn trên cohort. '
            'Scores không là nhãn thật; attribution/classifier chưa được nghiệm thu.</p>'
            f'<p>Trạng thái: {record["status"]}; new={record["new_forwards"]}; '
            f'cached={record["cached_predictions"]}.</p>' + "".join(sections) + '</html>',
            encoding="utf-8")
        checksum_artifacts(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    args = parser.parse_args()
    run_review(args.config, args.workspace, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
