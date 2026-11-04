"""Pinned offline temporal candidates from real classifier observations and track IDs."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.contracts import BehaviorEvent
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    environment,
    now,
    write_json,
)

from .runtime_config import media_deadline
from .tracking import load_inputs, require


def validate_rule(rule: dict[str, Any]) -> None:
    expected = dict(
        schema_version="temporal-event-rule-v1",
        status="approved",
        tracking_arm="C10",
        classifier_sampling_hz=1,
        behaviors=["phone_use", "looking_around"],
        threshold_source="pinned_parent_runtime",
        min_positive_observations=3,
        expected_spacing_ms=1000,
        min_observed_span_ms=2000,
        bridge_missing_samples=False,
        merge_track_ids=False,
        break_on_negative=True,
        break_on_unknown=True,
        break_on_null_track=True,
        confidence_aggregation="arithmetic_mean_supporting_scores",
        event_status="candidate",
        duration_semantics="last_minus_first_observation",
        duplicate_suppression="none",
        new_model_forwards=0,
        cached_replay_runs=1,
        risk=False,
        web=False,
    )
    require(all(rule.get(k) == v for k, v in expected.items()), "Unsupported event rule")


def aggregate(
    frames: list[dict[str, Any]],
    projected: list[dict[str, Any]],
    metadata: dict[str, Any],
    rule: dict[str, Any],
    session_id: str,
    model_version: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    validate_rule(rule)
    labels = rule["behaviors"]
    thresholds = metadata["thresholds"]
    require(
        metadata["target_order"] == labels
        and len(thresholds) == len(labels)
        and all(math.isfinite(t) and 0 <= t <= 1 for t in thresholds),
        "Invalid targets",
    )
    require(len(frames) == len(projected) and bool(frames), "Incomplete join")
    active: dict[tuple[int, str], list[dict[str, Any]]] = {}
    events: list[dict[str, Any]] = []
    short: list[dict[str, Any]] = []
    counts = {
        label: dict(
            positive_assigned=0,
            negative_assigned=0,
            unknown_assigned=0,
            null_track=0,
            event_support=0,
            short_support=0,
        )
        for label in labels
    }
    previous_index = previous_time = -1
    seen_refs: set[str] = set()

    def finish(key: tuple[int, str]) -> None:
        support = active.pop(key)
        first, last = support[0], support[-1]
        span = last["video_time_ms"] - first["video_time_ms"]
        scores = [x["score"] for x in support]
        if len(support) < rule["min_positive_observations"] or span < rule["min_observed_span_ms"]:
            short.append(
                {
                    "track_id": key[0],
                    "behavior": key[1],
                    "support": support,
                    "reason": "insufficient_consecutive_support",
                }
            )
            counts[key[1]]["short_support"] += len(support)
            return
        event = BehaviorEvent(
            event_id=f"{rule['rule_id']}-e{len(events):05d}",
            session_id=session_id,
            track_id=key[0],
            behavior=key[1],
            start_frame=first["frame_index"],
            end_frame=last["frame_index"],
            start_time_ms=first["video_time_ms"],
            end_time_ms=last["video_time_ms"],
            aggregated_confidence=sum(scores) / len(scores),
            model_version=model_version,
            rule_version=rule["rule_id"],
            source_prediction_ids=tuple(x["prediction_ref"] for x in support),
        )
        events.append(
            {
                "schema_version": "temporal-event-candidates-v1",
                "event": asdict(event),
                "tracking_arm": "C10",
                "observed_span_ms": span,
                "support_count": len(support),
                "score_min": min(scores),
                "score_max": max(scores),
                "support": support,
            }
        )
        counts[key[1]]["event_support"] += len(support)

    for frame, row in zip(frames, projected, strict=True):
        index, stamp = frame["frame_index"], frame["video_time_ms"]
        require(
            type(index) is int
            and index > previous_index
            and isinstance(stamp, (int, float))
            and math.isfinite(stamp)
            and stamp >= 0
            and stamp == int(stamp)
            and stamp > previous_time
            and stamp % rule["expected_spacing_ms"] == 0,
            "Invalid/duplicate/off-grid sample",
        )
        require(
            row["frame_index"] == index
            and row["video_time_ms"] == stamp
            and row["arm_id"] == "C10",
            "Assignment frame mismatch",
        )
        require(
            [(x["anchor_id"], x["person_box"]) for x in frame["observations"]]
            == [(x["anchor_id"], x["person_box"]) for x in row["assignments"]],
            "Anchor/geometry mismatch",
        )
        if previous_time >= 0 and stamp - previous_time != rule["expected_spacing_ms"]:
            for key in list(active):
                finish(key)
        positives: dict[tuple[int, str], dict[str, Any]] = {}
        used: set[int] = set()
        for obs, assignment in zip(frame["observations"], row["assignments"], strict=True):
            ref = f"{session_id}:{obs['anchor_id']}"
            require(ref not in seen_refs, "Duplicate anchor reference")
            seen_refs.add(ref)
            identity = assignment["track_id"]
            require(
                identity is None or type(identity) is int and identity > 0 and identity not in used,
                "Invalid/duplicate track ID",
            )
            if identity is not None:
                used.add(identity)
            scores, flags = obs.get("scores"), obs.get("above_threshold")
            require(
                isinstance(scores, list)
                and isinstance(flags, list)
                and len(scores) == len(flags) == len(labels),
                "Invalid classifier payload",
            )
            for label, score, flag, threshold in zip(
                labels, scores, flags, thresholds, strict=True
            ):
                require(
                    score is None
                    or isinstance(score, (int, float))
                    and not isinstance(score, bool)
                    and math.isfinite(score)
                    and 0 <= score <= 1,
                    "Invalid score",
                )
                require(flag is None or type(flag) is bool, "Invalid threshold flag")
                if score is not None and flag is not None:
                    require(flag == (score >= threshold), "Threshold flag mismatch")
                kind = (
                    "null_track"
                    if identity is None
                    else "unknown_assigned"
                    if score is None or flag is None
                    else "positive_assigned"
                    if flag
                    else "negative_assigned"
                )
                counts[label][kind] += 1
                if kind == "positive_assigned":
                    positives[(identity, label)] = dict(
                        prediction_ref=ref,
                        anchor_id=obs["anchor_id"],
                        frame_index=index,
                        video_time_ms=int(stamp),
                        person_box=obs["person_box"],
                        score=score,
                        threshold=threshold,
                    )
        for key in list(active):
            if key not in positives:
                finish(key)
        for key, support in positives.items():
            active.setdefault(key, []).append(support)
        previous_index, previous_time = index, int(stamp)
    for key in list(active):
        finish(key)
    for values in counts.values():
        require(
            values["positive_assigned"] == values["event_support"] + values["short_support"],
            "Support accounting mismatch",
        )
    return events, {
        "frames": len(frames),
        "observations": len(seen_refs),
        "behaviors": counts,
        "short_sequences": short,
        "event_count": len(events),
    }


def load_event_inputs(
    path: Path, workspace: Path
) -> tuple[
    dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]
]:
    auth = json.loads(path.read_text(encoding="utf-8"))
    require(
        auth.get("schema_version") == "events-authorization-v1"
        and auth.get("status") == "approved"
        and {"implementation", "synthetic_tests", "cached_replay"}
        <= set(auth.get("allowed_actions", [])),
        "Event approval required",
    )
    require(
        auth.get("access") == "repository_owner"
        and auth.get("upload") is False
        and auth.get("risk") is False
        and auth.get("web") is False
        and auth.get("new_model_forwards") == 0
        and auth.get("cached_replay_runs") == 1,
        "Invalid event scope",
    )
    media_deadline(auth)
    pins = auth["pins"]
    for pin in pins.values():
        FilePin(**pin).verify(workspace)
    rule = load_yaml(workspace / pins["rule"]["path"])
    validate_rule(rule)
    parent_auth, _, frames, parent_pins = load_inputs(
        workspace / pins["tracking_authorization"]["path"], workspace
    )
    require(
        rule["rule_id"] == auth["event_run_id"]
        and rule["media_delete_by"] == auth["media_delete_by"] == parent_auth["media_delete_by"],
        "Rule/retention mismatch",
    )
    acceptance = FilePin(**pins["tracking_acceptance"]).read_json(workspace)
    require(
        acceptance["status"] == "accepted_for_current_clip_prototype"
        and acceptance["selected_arm"] == "C10"
        and acceptance["assignments"] == pins["assignments"],
        "C10 acceptance mismatch",
    )
    tracker = FilePin(**pins["tracker_session"]).read_json(workspace)
    require(
        tracker["status"] == "completed"
        and tracker["arm_id"] == "C10"
        and tracker["source_sha256"] == parent_auth["source_sha256"]
        and tracker["media_delete_by"] == auth["media_delete_by"]
        and tracker["input_pins"]["predictions.jsonl"] == parent_pins["predictions.jsonl"],
        "Tracker parent mismatch",
    )
    rows = [
        json.loads(line)
        for line in (workspace / pins["assignments"]["path"])
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    projected = json.loads((workspace / pins["projection"]["path"]).read_text(encoding="utf-8"))
    parent_indices = {f["frame_index"] for f in frames}
    require(
        [r for r in rows if r["frame_index"] in parent_indices] == projected,
        "Projection differs from C10 assignments",
    )
    require(
        all(r["parent_session_sha256"] == parent_pins["session.json"]["sha256"] for r in projected),
        "Assignment parent session mismatch",
    )
    meta = json.loads(
        (workspace / parent_pins["predictions.jsonl"]["path"])
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    return auth, rule, frames, projected, {"metadata": meta, "parent_pins": parent_pins}


def run(authorization: Path, workspace: Path, output: Path) -> dict[str, Any]:
    workspace, output = workspace.resolve(), output.resolve()
    auth, rule, frames, projection, inputs = load_event_inputs(authorization, workspace)
    require(
        output == (workspace / auth["output"]).resolve()
        and output.is_relative_to(workspace / "outputs")
        and not output.exists(),
        "One replay requires the approved, unused output path",
    )
    auth_sha = sha256_file(authorization)
    output.mkdir(parents=True, exist_ok=False)
    session: dict[str, Any] = dict(
        schema_version="temporal-event-session-v1",
        status="running",
        started_at=now(),
        event_run_id=auth["event_run_id"],
        media_delete_by=auth["media_delete_by"],
        new_model_forwards=0,
        quality_acceptance="pending_owner_review",
    )
    write_json(output / "session.json", session)
    try:
        meta = inputs["metadata"]
        provenance = dict(
            authorization_sha256=auth_sha,
            pins=auth["pins"],
            parent_pins=inputs["parent_pins"],
            source_sha256=meta["source_sha256"],
            model_pins=meta["pins"],
            rule_sha256=auth["pins"]["rule"]["sha256"],
        )
        write_json(output / "provenance.json", provenance)
        write_json(output / "resolved-rule.json", rule)
        write_json(output / "environment.json", environment())
        write_json(output / "code-provenance.json", code_identity())
        namespace = inputs["parent_pins"]["session.json"]["sha256"]
        events, accounting = aggregate(
            frames, projection, meta, rule, namespace, meta["pins"]["checkpoint"]["sha256"]
        )
        for event in events:
            event["provenance"] = provenance
            event["media_delete_by"] = auth["media_delete_by"]
        with (output / "events.jsonl").open("x", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event, allow_nan=False) + "\n")
        write_json(output / "accounting.json", accounting)
        require(sha256_file(authorization) == auth_sha, "Authorization changed during replay")
        load_event_inputs(authorization, workspace)
        session.update(
            status="completed",
            event_count=len(events),
            counts_by_behavior={
                b: sum(e["event"]["behavior"] == b for e in events) for b in rule["behaviors"]
            },
        )
    except BaseException as exc:
        session.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        session["ended_at"] = now()
        write_json(output / "session.json", session)
        checksum_artifacts(output)
    return session


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("authorization", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    args = parser.parse_args()
    run(args.authorization, args.workspace, args.output)
    print("Event replay completed; candidates require human review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
