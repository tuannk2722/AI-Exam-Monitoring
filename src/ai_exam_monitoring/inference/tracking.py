"""Pinned, local replay of person observations; no detector or classifier calls."""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import time
from collections import defaultdict
from importlib import import_module
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    environment,
    now,
    write_json,
)

from .runtime_config import media_deadline


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DataContractError(message)


class Detections:
    """Minimal upstream result interface, preserving indices through high/low slicing."""

    def __init__(self, data: NDArray[np.float32], indices: NDArray[np.int64]):
        self.data, self.indices = data, indices

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, key: Any) -> Detections:
        return Detections(self.data[key], self.indices[key])

    @property
    def conf(self) -> NDArray[np.float32]:
        return self.data[:, 4]

    @property
    def cls(self) -> NDArray[np.float32]:
        return np.zeros(len(self), dtype=np.float32)

    @property
    def xywh(self) -> NDArray[np.float32]:
        boxes = self.data[:, :4].copy()
        boxes[:, 2:] -= boxes[:, :2]
        boxes[:, :2] += boxes[:, 2:] / 2
        return boxes


def tracker_factory(settings: dict[str, Any], arm: dict[str, Any], workspace: Path) -> Any:
    # Check BEFORE importing Ultralytics, whose matching module can auto-install lap.
    require(version("ultralytics") == settings["ultralytics_version"], "Tracker version changed")
    require(version("lap") == settings["proposed_lap_version"], "Solver version changed")
    settings_dir = workspace / "outputs/runtime-settings"
    settings_dir.mkdir(parents=True, exist_ok=True)
    os.environ.update(YOLO_AUTOINSTALL="false", YOLO_OFFLINE="true",
                      YOLO_CONFIG_DIR=str(settings_dir))
    utils: Any = import_module("ultralytics.utils")
    utils.AUTOINSTALL = False
    utils.SETTINGS.update({"sync": False})
    module = import_module("ultralytics.trackers.byte_tracker")
    args = SimpleNamespace(**{k: settings[k] for k in
                             ("track_buffer", "match_thresh", "fuse_score")},
                           **{k: arm[k] for k in
                              ("track_high_thresh", "track_low_thresh", "new_track_thresh")})
    tracker = module.BYTETracker(args, frame_rate=settings["frame_rate"])
    require(tracker.max_time_lost == settings["expected_max_time_lost_updates"],
            "Unexpected tracker clock")
    original_init = tracker.init_track

    def init_track(results: Detections, img: Any = None) -> Any:
        tracks = original_init(results, img)
        for track in tracks:
            # Upstream enumerates each filtered subset again: restore the original index.
            track.idx = int(results.indices[int(track.idx)])
        return tracks

    tracker.init_track = init_track
    return tracker


def validate_frames(frames: list[dict[str, Any]], hz: float) -> None:
    require(bool(frames) and hz > 0, "Empty frames or invalid sampling")
    previous_index = -1
    previous_time: float | None = None
    for frame in frames:
        index, stamp = frame["frame_index"], frame["video_time_ms"]
        require(type(index) is int and index > previous_index, "Invalid frame index")
        require(isinstance(stamp, (int, float)) and math.isfinite(stamp) and stamp >= 0,
                "Invalid timestamp")
        if previous_time is not None:
            require(abs(stamp - previous_time - 1000 / hz) < 1e-6, "Unexpected sample interval")
        previous_index, previous_time = index, stamp
        w, h = frame["width"], frame["height"]
        require(type(w) is int and type(h) is int and w > 0 and h > 0, "Invalid dimensions")
        anchors: set[str] = set()
        for obs in frame["observations"]:
            anchor = obs["anchor_id"]
            require(isinstance(anchor, str) and bool(anchor) and anchor not in anchors,
                    "Invalid or duplicate anchor")
            anchors.add(anchor)
            box, score = obs["person_box"], obs["detector_confidence"]
            require(len(box) == 4 and all(math.isfinite(v) for v in box), "Invalid box")
            require(0 <= box[0] < box[2] <= w and 0 <= box[1] < box[3] <= h,
                    "Box outside source")
            require(math.isfinite(score) and 0 <= score <= 1, "Invalid detector score")


def assignments(frame: dict[str, Any], tracker: Any,
                next_id: int) -> tuple[list[dict[str, Any]], int]:
    observations = frame["observations"]
    mapping: dict[int, tuple[int, list[float]]] = {}
    if tracker is None:
        for index in range(len(observations)):
            next_id += 1
            mapping[index] = (next_id, [])
    else:
        values = np.asarray([o["person_box"] + [o["detector_confidence"]]
                             for o in observations], dtype=np.float32).reshape(-1, 5)
        results = tracker.update(Detections(values, np.arange(len(values), dtype=np.int64)))
        used: set[int] = set()
        for row in results:
            require(len(row) == 8 and bool(np.isfinite(row).all()), "Invalid tracker result")
            index, identity = int(row[7]), int(row[4])
            require(row[7] == index and 0 <= index < len(observations) and index not in mapping,
                    "Invalid tracker anchor mapping")
            require(row[4] == identity and identity > 0 and identity not in used,
                    "Duplicate/invalid track ID in frame")
            require(row[6] == 0 and row[5] == values[index, 4],
                    "Tracker score/class mapping changed")
            used.add(identity)
            mapping[index] = identity, [float(v) for v in row[:4]]
    rows = []
    for index, obs in enumerate(observations):
        value = mapping.get(index)
        rows.append({"anchor_id": obs["anchor_id"], "person_box": obs["person_box"],
                     "track_id": value[0] if value else None,
                     "tracker_box": value[1] if value and value[1] else None,
                     "reason": "assigned" if value else "not_emitted_by_tracker"})
    return rows, next_id


def technical_summary(frames: list[dict[str, Any]], times: list[float]) -> dict[str, Any]:
    tracks: dict[int, list[int]] = defaultdict(list)
    total = assigned = 0
    for sample, frame in enumerate(frames):
        for row in frame["assignments"]:
            total += 1
            if row["track_id"] is not None:
                assigned += 1
                tracks[row["track_id"]].append(sample)
    return {"samples": len(frames), "observations": total, "assigned": assigned,
            "unassigned": total - assigned, "assignment_coverage": assigned / total if total else 0,
            "track_count": len(tracks),
            "tracks": [{"track_id": key, "start_sample": samples[0], "end_sample": samples[-1],
                        "assigned_samples": len(samples),
                        "gap_count": sum(b > a + 1 for a, b in
                                         zip(samples, samples[1:], strict=False))}
                       for key, samples in sorted(tracks.items())],
            "timing_scope": "association_and_assignment_only",
            "mean_update_ms": float(np.mean(times)),
            "p50_update_ms": float(np.percentile(times, 50)),
            "p95_update_ms": float(np.percentile(times, 95)),
            "quality_metrics": None, "quality_acceptance": "pending_owner_review"}


def load_inputs(authorization: Path, workspace: Path) -> tuple[
    dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]
]:
    auth = json.loads(authorization.read_text(encoding="utf-8"))
    require(auth.get("schema_version") == "tracking-authorization-v1"
            and auth.get("status") == "approved", "Tracking approval required")
    require({"implementation", "synthetic_checks", "replay_N0_B0_B1", "local_review_gallery"}
            <= set(auth.get("allowed_actions", [])), "Tracking scope not approved")
    require(auth.get("access") == "repository_owner" and auth.get("upload") is False
            and all(auth.get(k) is False for k in ("events", "risk", "web")), "Invalid use scope")
    media_deadline(auth)
    for name in ("design", "proposal", "preflight", "parent_media"):
        FilePin(**auth[name]).verify(workspace)
    config = load_yaml(workspace / auth["proposal"]["path"])
    require(config["proposal_id"] == auth["proposal_id"], "Proposal identity mismatch")
    require([a["arm_id"] for a in config["arms"]] == ["N0", "B0", "B1"], "Invalid approved arms")
    preflight = FilePin(**auth["preflight"]).read_json(workspace)
    pins = preflight["input_pins"]
    for pin in pins.values():
        FilePin(**pin).verify(workspace)
    session = FilePin(**pins["session.json"]).read_json(workspace)
    parent = FilePin(**auth["parent_media"]).read_json(workspace)
    require(session["status"] == "completed"
            and session["runtime_id"] == config["parent_runtime_id"],
            "Parent session not completed or wrong runtime")
    require(parent.get("status") == "approved" and parent.get("rights_confirmed") is True
            and parent.get("test_or_holdout") is False
            and parent.get("third_party_processing") is False
            and parent.get("access") == "repository_owner", "Invalid parent media rights")
    require(parent["source_sha256"] == session["source_sha256"] == auth["source_sha256"],
            "Source mismatch")
    require(parent["media_delete_by"] == session["media_delete_by"] == auth["media_delete_by"]
            == config["media"]["media_delete_by"], "Retention changed")
    require(session["media_approval_sha256"] == auth["parent_media"]["sha256"],
            "Rights pin mismatch")
    prediction_path = workspace / pins["predictions.jsonl"]["path"]
    rows = [json.loads(line) for line in prediction_path.read_text(encoding="utf-8").splitlines()]
    require(rows[0].get("schema_version") == "recorded-observations-v1"
            and rows[-1].get("record_type") == "outcome" and rows[-1].get("status") == "completed",
            "Incomplete predictions")
    require(rows[0]["source_sha256"] == auth["source_sha256"], "Prediction source mismatch")
    frames = [r for r in rows if r["record_type"] == "frame"]
    validate_frames(frames, config["sampling_hz"])
    require(len(frames) == config["expected_samples"] == session["frames"]
            and sum(len(f["observations"]) for f in frames) == config["expected_observations"]
            == session["observations"], "Input counts changed")
    require([f["frame_index"] for f in frames] == session["sampled_frame_indices"],
            "Sample indices changed")
    return auth, config, frames, pins


def run_arm(arm: dict[str, Any], config: dict[str, Any], frames: list[dict[str, Any]],
            auth: dict[str, Any], pins: dict[str, Any], workspace: Path, output: Path,
            env: dict[str, Any], code: dict[str, Any]) -> dict[str, Any]:
    output.mkdir(exist_ok=False)
    started = time.perf_counter()
    record: dict[str, Any] = {"schema_version": "tracking-session-v1", "status": "running",
                              "arm_id": arm["arm_id"], "started_at": now(),
                              "media_delete_by": auth["media_delete_by"],
                              "source_sha256": auth["source_sha256"], "input_pins": pins}
    write_json(output / "session.json", record)
    result: dict[str, Any] = {}
    try:
        write_json(output / "config.json", {"proposal": config, "arm": arm, "authorization": auth})
        write_json(output / "environment.json", env)
        write_json(output / "code-provenance.json", code)
        tracker = (None if arm["type"] == "no_tracking" else
                   tracker_factory(config["tracker"], arm, workspace))
        record["startup_seconds"] = time.perf_counter() - started
        processed, times, next_id = [], [], 0
        with (output / "assignments.jsonl").open("x", encoding="utf-8") as handle:
            for frame in frames:
                media_deadline(auth)
                tick = time.perf_counter()
                rows, next_id = assignments(frame, tracker, next_id)
                times.append((time.perf_counter() - tick) * 1000)
                item = {"schema_version": "track-assignments-v1", "arm_id": arm["arm_id"],
                        "parent_session_sha256": pins["session.json"]["sha256"],
                        "frame_index": frame["frame_index"],
                        "video_time_ms": frame["video_time_ms"],
                        "assignments": rows}
                processed.append(item)
                handle.write(json.dumps(item, allow_nan=False) + "\n")
                handle.flush()
        for pin in pins.values():
            FilePin(**pin).verify(workspace)
        media_deadline(auth)
        result = technical_summary(processed, times)
        write_json(output / "summary.json", result)
        record["status"] = "completed"
    except BaseException as exc:
        record.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        record.update(ended_at=now(), elapsed_seconds=time.perf_counter() - started)
        write_json(output / "session.json", record)
        checksum_artifacts(output)
    return result


def run(authorization: Path, workspace: Path, output: Path) -> dict[str, Any]:
    workspace, output = workspace.resolve(), output.resolve()
    auth, config, frames, pins = load_inputs(authorization, workspace)
    require(not output.exists() and output.is_relative_to(workspace / "outputs"),
            "Require new output directory under workspace outputs")
    # Version check before any arm runs; no silent baseline-only fallback.
    require(version("ultralytics") == config["tracker"]["ultralytics_version"]
            and version("lap") == config["tracker"]["proposed_lap_version"], "Dependency mismatch")
    output.mkdir(parents=True, exist_ok=False)
    state: dict[str, Any] = {"schema_version": "tracking-benchmark-v1", "status": "running",
                             "started_at": now(), "media_delete_by": auth["media_delete_by"],
                             "authorization_sha256": sha256_file(authorization), "arms": {}}
    write_json(output / "benchmark.json", state)
    try:
        env = environment()
        env["command"] = ["ai_exam_monitoring.inference.tracking",
                          "authorization_sha256=" + state["authorization_sha256"]]
        env.update(processor=platform.processor(), logical_cpu_count=os.cpu_count())
        for name in ("ultralytics", "lap", "scipy"):
            env["packages"][name] = version(name)
        code = code_identity()
        for arm in config["arms"]:
            state["arms"][arm["arm_id"]] = run_arm(
                arm, config, frames, auth, pins, workspace, output / arm["arm_id"], env, code)
        # Check authorization and design again, including deadline, before claiming success.
        require(sha256_file(authorization) == state["authorization_sha256"], "Approval changed")
        load_inputs(authorization, workspace)
        state["status"] = "completed"
    except BaseException as exc:
        state.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        state["ended_at"] = now()
        write_json(output / "benchmark.json", state)
        checksum_artifacts(output)
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization", required=True, type=Path)
    parser.add_argument("--workspace", default=Path("."), type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        run(args.authorization, args.workspace, args.output)
    except Exception as exc:
        parser.exit(1, f"Tracking failed ({type(exc).__name__}); inspect session output.\n")
    print("Tracking replay completed; quality requires owner review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
