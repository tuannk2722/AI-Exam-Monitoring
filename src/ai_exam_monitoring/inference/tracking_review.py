"""Build an offline, source-linked tracking review batch without running models."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import checksum_artifacts, now, write_json

from .runtime_config import media_deadline
from .tracking import load_inputs, require
from .video import RecordedVideo


def draft_cases(arms: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Algorithmic groups are review proposals, never person ground truth."""
    cases: list[dict[str, Any]] = []
    for arm, frames in arms.items():
        if arm == "N0":
            continue
        groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for sample, frame in enumerate(frames):
            missing = []
            for row in frame["assignments"]:
                if row["track_id"] is None:
                    missing.append(row["anchor_id"])
                else:
                    groups[row["track_id"]].append({"sample": sample,
                                                    "anchor_id": row["anchor_id"]})
            if missing:
                cases.append({"case_id": f"{arm}-unassigned-{sample:03d}", "arm": arm,
                              "kind": "unassigned", "samples": [sample], "anchors": missing,
                              "status": "pending"})
        for identity, members in groups.items():
            samples = [m["sample"] for m in members]
            gaps = [[a, b] for a, b in zip(samples, samples[1:], strict=False) if b > a + 1]
            cases.append({"case_id": f"{arm}-track-{identity:04d}", "arm": arm,
                          "kind": "draft_track_group", "track_id": identity, "samples": samples,
                          "members": members, "gaps": gaps, "status": "pending",
                          "identity_truth": "unreviewed"})
    # Exceptions first, then long groups. All groups and frames remain accessible.
    return sorted(cases, key=lambda c: (c["kind"] != "unassigned", not bool(c.get("gaps")),
                                        -len(c["samples"]), c["case_id"]))


def build_review(authorization: Path, workspace: Path, benchmark: Path, source: Path,
                 output: Path) -> dict[str, Any]:
    workspace, benchmark, output = workspace.resolve(), benchmark.resolve(), output.resolve()
    auth, _, frames, _ = load_inputs(authorization, workspace)
    auth_sha = sha256_file(authorization)
    benchmark_sha = sha256_file(benchmark / "benchmark.json")
    record = json.loads((benchmark / "benchmark.json").read_text(encoding="utf-8"))
    require(record["status"] == "completed" and record["authorization_sha256"] == auth_sha,
            "Require completed benchmark with same authorization")
    manifest_sha = sha256_file(benchmark / "checksums.json")
    checks = json.loads((benchmark / "checksums.json").read_text(encoding="utf-8"))
    for name, expected in checks.items():
        path = (benchmark / name).resolve()
        require(path.is_relative_to(benchmark) and sha256_file(path) == expected,
                "Benchmark checksum mismatch")
    require(source.is_file() and sha256_file(source) == auth["source_sha256"], "Wrong source")
    require(not output.exists() and output.is_relative_to(workspace / "outputs"),
            "Require new review output under workspace outputs")
    arms = {arm: [json.loads(line) for line in
                  (benchmark / arm / "assignments.jsonl").read_text(encoding="utf-8").splitlines()]
            for arm in ("N0", "B0", "B1")}
    for rows in arms.values():
        require(len(rows) == len(frames), "Incomplete arm")
        for original, row in zip(frames, rows, strict=True):
            require(original["frame_index"] == row["frame_index"]
                    and original["video_time_ms"] == row["video_time_ms"]
                    and [a["anchor_id"] for a in original["observations"]]
                    == [a["anchor_id"] for a in row["assignments"]], "Review mapping mismatch")
    output.mkdir(parents=True, exist_ok=False)
    state: dict[str, Any] = {"schema_version": "tracking-review-batch-v1", "status": "running",
                             "started_at": now(), "benchmark_sha256": benchmark_sha,
                             "authorization_sha256": auth_sha,
                             "media_delete_by": auth["media_delete_by"],
                             "source_sha256": auth["source_sha256"]}
    write_json(output / "review-session.json", state)
    try:
        wanted = {f["frame_index"]: f for f in frames}
        images = []
        for decoded in RecordedVideo(source).frames():
            media_deadline(auth)
            if decoded.index not in wanted:
                continue
            original = wanted[decoded.index]
            require(decoded.time_ms == original["video_time_ms"] and decoded.image.size ==
                    (original["width"], original["height"]), "Source frame changed")
            name = f"f{decoded.index:08d}.png"
            decoded.image.save(output / name)
            images.append({"frame_index": decoded.index, "video_time_ms": decoded.time_ms,
                           "image": name, "image_sha256": sha256_file(output / name)})
        require(len(images) == len(frames), "Incomplete review frames")
        require(sha256_file(source) == auth["source_sha256"], "Source changed during decode")
        require(sha256_file(benchmark / "checksums.json") == manifest_sha
                and sha256_file(benchmark / "benchmark.json") == benchmark_sha,
                "Benchmark changed during review")
        for name, expected in checks.items():
            require(sha256_file(benchmark / name) == expected, "Benchmark payload changed")
        require(sha256_file(authorization) == auth_sha, "Approval changed during review")
        load_inputs(authorization, workspace)
        cases = draft_cases(arms)
        payload = {**state, "frames": images, "arms": arms, "cases": cases,
                   "summaries": record["arms"], "status": "pending_owner_review"}
        write_json(output / "batch.json", payload)
        embedded = json.dumps(payload, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
        template = Path(__file__).parent / "tracking_review_assets/index.html"
        state["template_sha256"] = sha256_file(template)
        document = template.read_text(encoding="utf-8").replace("__PAYLOAD__", embedded)
        (output / "index.html").write_text(document, encoding="utf-8")
        state.update(status="completed", samples=len(images), cases=len(cases),
                     quality_acceptance="pending_owner_review")
    except BaseException as exc:
        state.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        state["ended_at"] = now()
        write_json(output / "review-session.json", state)
        checksum_artifacts(output)
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("authorization", "benchmark", "source", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        build_review(args.authorization, args.workspace, args.benchmark, args.source, args.output)
    except Exception as exc:
        parser.exit(1, f"Review failed ({type(exc).__name__}); inspect review-session.json.\n")
    print("Tracking review batch ready; no quality acceptance inferred.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
