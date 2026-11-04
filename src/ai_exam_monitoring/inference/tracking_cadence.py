"""Finite detector cadence experiment with immutable 1 Hz classifier observations."""
from __future__ import annotations

import argparse
import copy
import json
import os
import platform
import time
from collections.abc import Iterable
from importlib.metadata import version
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    environment,
    now,
    write_json,
)

from .person import PersonDetector, crop_boxes
from .runtime_config import RuntimeConfig, load_runtime_config, media_deadline, verify_media
from .tracking import load_inputs, require, run_arm, technical_summary, validate_frames
from .video import RecordedVideo, VideoFrame


def grid_stride(fps: int, hz: int) -> int:
    require(type(fps) is int and type(hz) is int and 0 < hz <= fps and fps % hz == 0,
            "Cadence must divide source FPS exactly")
    return fps // hz


def load_experiment(path: Path, workspace: Path, source: Path) -> tuple[
    dict[str, Any], dict[str, Any], RuntimeConfig, list[dict[str, Any]], dict[str, Any]
]:
    auth = json.loads(path.read_text(encoding="utf-8"))
    require(auth.get("schema_version") == "tracking-cadence-authorization-v1"
            and auth.get("status") == "approved_under_owner_delegation",
            "Cadence authorization required")
    require({"implementation", "synthetic_tests", "detector_cadence_cache", "C5_C10_replay",
             "local_visual_audit", "technical_selection"} <= set(auth.get("allowed_actions", [])),
            "Incomplete cadence authorization")
    require(auth.get("access") == "repository_owner" and auth.get("upload") is False
            and all(auth.get(k) is False for k in ("events", "risk", "web")), "Wrong scope")
    media_deadline(auth)
    for key in ("config", "design", "parent_authorization", "baseline_selection", "runtime"):
        FilePin(**auth[key]).verify(workspace)
    cfg = load_yaml(workspace / auth["config"]["path"])
    require(cfg.get("schema_version") == "tracking-cadence-config-v1"
            and cfg["experiment_id"] == auth["experiment_id"], "Wrong cadence config")
    require(cfg["classifier_new_forwards"] == 0
            and cfg["expected_new_forwards"] == 540 and cfg["cache_hz"] == 10
            and [(a["arm_id"], a["hz"]) for a in cfg["arms"]] == [("C5", 5), ("C10", 10)],
            "Unsupported experiment scope")
    parent_auth, _, parents, pins = load_inputs(
        workspace / auth["parent_authorization"]["path"], workspace)
    selection = FilePin(**auth["baseline_selection"]).read_json(workspace)
    require(selection["selected_arm"] == "B0", "Expected B0 baseline")
    for key in ("selected_output", "selected_assignments", "research", "visual_audit"):
        FilePin(**selection[key]).verify(workspace)
    runtime = load_runtime_config(workspace / auth["runtime"]["path"], workspace)
    rights = verify_media(source, workspace / parent_auth["parent_media"]["path"], runtime)
    require(auth["source_sha256"] == rights["source_sha256"] == parent_auth["source_sha256"]
            and auth["media_delete_by"] == cfg["media_delete_by"]
            == rights["media_delete_by"] == parent_auth["media_delete_by"],
            "Source/retention mismatch")
    for key in ("track_buffer", "match_thresh", "fuse_score"):
        require(cfg["tracker_policy"][key] == selection["policy"][key], "Tracker policy drift")
    for key in ("track_high_thresh", "track_low_thresh", "new_track_thresh"):
        require(cfg["arm_policy"][key] == selection["policy"][key], "Association policy drift")
    require(runtime.raw["runtime_id"] == "RUNTIME-V8S-20261026", "Wrong detector runtime")
    require(len(parents) == cfg["expected_parent_samples"], "Parent sample count changed")
    return auth, cfg, runtime, parents, pins


def cache_frames(frames: Iterable[VideoFrame], detector: Any, runtime: RuntimeConfig,
                 cfg: dict[str, Any], auth: dict[str, Any], parents: list[dict[str, Any]],
                 output: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Synthetic fixtures inject a detector; the production runner always uses V8S."""
    stride = grid_stride(cfg["source_fps"], cfg["cache_hz"])
    parent_by_index = {p["frame_index"]: p for p in parents}
    require(len(parent_by_index) == len(parents), "Duplicate parent index")
    rows: list[dict[str, Any]] = []
    cached = forwards = decoded_count = 0
    inference_seconds = 0.0
    (output / "frames").mkdir()
    with (output / "detections.jsonl").open("x", encoding="utf-8") as handle:
        for decoded in frames:
            media_deadline(auth)
            require(decoded.index == decoded_count, "Missing/duplicated source frame")
            require(abs(decoded.time_ms - decoded.index * 1000 / cfg["source_fps"]) < 1e-4,
                    "Source timestamp off configured grid")
            decoded_count += 1
            if decoded.index % stride:
                continue
            require(len(rows) < cfg["expected_cache_samples"], "Extra cadence sample")
            parent = parent_by_index.get(decoded.index)
            if parent is not None:
                require(abs(parent["video_time_ms"] - decoded.time_ms) < 1e-4
                        and decoded.image.size == (parent["width"], parent["height"]),
                        "Parent/source geometry or timestamp changed")
                observations = copy.deepcopy(parent["observations"])
                cached += 1
            else:
                require(forwards < cfg["expected_new_forwards"], "Detector budget exceeded")
                tick = time.perf_counter()
                detections = detector.predict(decoded.image)
                inference_seconds += time.perf_counter() - tick
                forwards += 1
                observations = []
                for i, detection in enumerate(detections):
                    person, _ = crop_boxes(detection, decoded.image.size, runtime.raw["crop"])
                    observations.append({"anchor_id": f"f{decoded.index:08d}-a{i:03d}",
                                         "person_box": list(person),
                                         "detector_confidence": detection.confidence})
            row = {"schema_version": "person-cadence-v1", "frame_index": decoded.index,
                   "video_time_ms": decoded.time_ms, "width": decoded.image.width,
                   "height": decoded.image.height, "observations": observations,
                   "origin": "cached_parent" if parent is not None else "new_detector",
                   "classifier_evaluated_in_this_run": False,
                   "parent_classifier_evidence": parent is not None}
            handle.write(json.dumps(row, allow_nan=False) + "\n")
            handle.flush()
            rows.append(row)
            if parent is not None or any(lo <= decoded.time_ms / 1000 <= hi
                                         for lo, hi in cfg["review_windows_seconds"]):
                decoded.image.save(output / "frames" / f"f{decoded.index:08d}.png")
            if len(rows) % 100 == 0:
                print(f"Cadence cache {len(rows)} samples; {forwards} detector forwards",
                      flush=True)
    require(decoded_count == cfg["source_frames"] and len(rows) == cfg["expected_cache_samples"]
            and cached == cfg["expected_parent_samples"]
            and forwards == cfg["expected_new_forwards"],
            "Incomplete cadence cache or budget mismatch")
    validate_frames(rows, cfg["cache_hz"])
    return rows, {"decoded_frames": decoded_count, "samples": len(rows), "cached_parent": cached,
                  "new_detector_forwards": forwards, "new_classifier_forwards": 0,
                  "detector_seconds": inference_seconds,
                  "observations": sum(len(row["observations"]) for row in rows)}


def project_parent(assignments: list[dict[str, Any]], parents: list[dict[str, Any]]) -> list[
    dict[str, Any]
]:
    by_index = {row["frame_index"]: row for row in assignments}
    require(len(by_index) == len(assignments), "Duplicate assignment frame")
    result = []
    for parent in parents:
        row = by_index.get(parent["frame_index"])
        require(row is not None, "Missing parent sample in projection")
        assert row is not None
        require(abs(row["video_time_ms"] - parent["video_time_ms"]) < 1e-4,
                "Projected time changed")
        require([(r["anchor_id"], r["person_box"]) for r in row["assignments"]]
                == [(r["anchor_id"], r["person_box"]) for r in parent["observations"]],
                "Projected anchor mapping changed")
        result.append(row)
    return result


def endpoint_check(frames: list[dict[str, Any]], case: dict[str, Any]) -> dict[str, Any]:
    identities = []
    for index, anchor in zip(case["frame_indices"], case["anchors"], strict=True):
        matches = [r["track_id"] for f in frames if f["frame_index"] == index
                   for r in f["assignments"] if r["anchor_id"] == anchor]
        require(len(matches) == 1, "Known-case anchor missing/duplicated")
        identities.append(matches[0])
    return {"anchors": case["anchors"], "track_ids": identities,
            "both_assigned": all(x is not None for x in identities),
            "distinct_assigned_ids": all(x is not None for x in identities)
            and identities[0] != identities[1], "visual_trace_required": True}


def review_document(output: Path, baseline: Path, parents: list[dict[str, Any]],
                    arm_rows: dict[str, list[dict[str, Any]]], result: dict[str, Any]) -> None:
    base_rows = [json.loads(line) for line in baseline.read_text(encoding="utf-8").splitlines()]
    all_arms = {"B0": base_rows, **arm_rows}
    maps = {arm: {r["frame_index"]: r for r in rows} for arm, rows in all_arms.items()}
    selected = []
    for p in sorted((output / "detections/frames").glob("*.png")):
        index = int(p.stem[1:])
        selected.append({"frame_index": index, "video_time_ms": index * 1000 / 30,
                         "image": p.relative_to(output).as_posix(),
                         "arms": {a: rows.get(index) for a, rows in maps.items()}})
    payload = {"frames": selected, "parent_indices": [p["frame_index"] for p in parents],
               "summary": result, "media_delete_by": result["media_delete_by"]}
    write_json(output / "review.json", payload)
    template = Path(__file__).parent / "tracking_review_assets/cadence.html"
    embedded = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
    (output / "index.html").write_text(
        template.read_text(encoding="utf-8").replace("__PAYLOAD__", embedded), encoding="utf-8")
    write_json(output / "review-template.json", {"sha256": sha256_file(template)})


def run(authorization: Path, workspace: Path, source: Path, output: Path) -> dict[str, Any]:
    workspace, output = workspace.resolve(), output.resolve()
    auth, cfg, runtime, parents, parent_pins = load_experiment(authorization, workspace, source)
    require(not output.exists() and output.is_relative_to(workspace / "outputs"),
            "Require new cadence output directory")
    video = RecordedVideo(source)
    require(video.fps == cfg["source_fps"] and video.count == cfg["source_frames"],
            "Source FPS/frame count mismatch")
    authorization_sha = sha256_file(authorization)
    output.mkdir(parents=True, exist_ok=False)
    result: dict[str, Any] = {"schema_version": "tracking-cadence-session-v1", "status": "running",
                              "experiment_id": cfg["experiment_id"], "started_at": now(),
                              "authorization_sha256": authorization_sha,
                              "media_delete_by": auth["media_delete_by"],
                              "source_sha256": auth["source_sha256"], "arms": {}}
    write_json(output / "session.json", result)
    started = time.perf_counter()
    cache_out = output / "detections"
    cache_out.mkdir()
    cache_state: dict[str, Any] = {"status": "running", "media_delete_by": auth["media_delete_by"],
                                   "source_sha256": auth["source_sha256"]}
    write_json(cache_out / "session.json", cache_state)
    try:
        env = environment()
        env["command"] = ["ai_exam_monitoring.inference.tracking_cadence",
                          "authorization_sha256=" + authorization_sha]
        env.update(processor=platform.processor(), logical_cpu_count=os.cpu_count())
        env.setdefault("packages", {}).update(
            {name: version(name) for name in ("ultralytics", "lap", "opencv-python", "scipy")})
        code = code_identity()
        write_json(output / "environment.json", env)
        write_json(output / "code-provenance.json", code)
        write_json(output / "resolved-config.json", cfg)
        detector = PersonDetector(runtime)
        rows, cache_summary = cache_frames(video.frames(), detector, runtime, cfg, auth,
                                           parents, cache_out)
        require(sha256_file(source) == auth["source_sha256"], "Source changed during detection")
        load_experiment(authorization, workspace, source)
        cache_state.update(status="completed", **cache_summary)
        write_json(cache_out / "session.json", cache_state)
        checksum_artifacts(cache_out)
        result["cache"] = cache_summary
        pins = {**parent_pins, "cadence_cache": {
            "path": (cache_out / "detections.jsonl").relative_to(workspace).as_posix(),
            "sha256": sha256_file(cache_out / "detections.jsonl")}, "cadence_session": {
            "path": (cache_out / "session.json").relative_to(workspace).as_posix(),
            "sha256": sha256_file(cache_out / "session.json")}}
        arm_rows = {}
        for arm in cfg["arms"]:
            stride = grid_stride(cfg["source_fps"], arm["hz"])
            subset = [r for r in rows if r["frame_index"] % stride == 0]
            require(len(subset) == arm["samples"], "Incomplete arm subset")
            validate_frames(subset, arm["hz"])
            tracker_settings = {**cfg["tracker_policy"], "frame_rate": arm["hz"],
                                "expected_max_time_lost_updates": int(
                                    arm["hz"] / 30 * cfg["tracker_policy"]["track_buffer"])}
            effective = {**cfg, "tracker": tracker_settings}
            full = run_arm({**cfg["arm_policy"], "arm_id": arm["arm_id"]}, effective, subset,
                           auth, pins, workspace, output / arm["arm_id"], env, code)
            assignment_path = output / arm["arm_id"] / "assignments.jsonl"
            assigned = [json.loads(line) for line in
                        assignment_path.read_text(encoding="utf-8").splitlines()]
            arm_rows[arm["arm_id"]] = assigned
            projected = project_parent(assigned, parents)
            common = technical_summary(projected, [0.0] * len(projected))
            for key in ("mean_update_ms", "p50_update_ms", "p95_update_ms", "timing_scope"):
                common.pop(key)
            entry = {"full_cadence": full, "common_1hz": common,
                     "known_case": endpoint_check(projected, cfg["known_case"])}
            result["arms"][arm["arm_id"]] = entry
            write_json(output / f"{arm['arm_id']}-parent-projection.json", projected)
        selection = FilePin(**auth["baseline_selection"]).read_json(workspace)
        baseline = FilePin(**selection["selected_assignments"]).verify(workspace)
        require(sha256_file(authorization) == authorization_sha, "Cadence approval changed")
        load_experiment(authorization, workspace, source)
        media_deadline(auth)
        result["status"] = "completed"
        result["quality_acceptance"] = "pending_visual_audit"
        review_document(output, baseline, parents, arm_rows, result)
    except BaseException as exc:
        if cache_state["status"] != "completed":
            cache_state.update(status="failed", error_type=type(exc).__name__)
            write_json(cache_out / "session.json", cache_state)
            checksum_artifacts(cache_out)
        result.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        result.update(ended_at=now(), elapsed_seconds=time.perf_counter() - started)
        write_json(output / "session.json", result)
        checksum_artifacts(output)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("authorization", "source", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        run(args.authorization, args.workspace, args.source, args.output)
    except Exception as exc:
        parser.exit(1, f"Cadence failed ({type(exc).__name__}); inspect session output.\n")
    print("Cadence experiment completed; visual association audit remains required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
