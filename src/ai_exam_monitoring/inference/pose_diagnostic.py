"""Bounded pose feasibility diagnostic; never mutates D2 or suppresses boxes."""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import os
import random
import time
from importlib import import_module
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image, ImageDraw

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    environment,
    write_json,
)

from .detector_review import read_object
from .runtime_config import media_deadline


def support(box: list[float], poses: list[dict[str, Any]], rules: dict[str, Any]) -> list[int]:
    """Return all qualifying pose indices; missing or ambiguous evidence stays explicit."""
    if len(box) != 4 or not all(math.isfinite(v) for v in box):
        raise DataContractError("Invalid D2 box")
    if box[0] >= box[2] or box[1] >= box[3]:
        raise DataContractError("Degenerate D2 box")
    found = []
    for idx, pose in enumerate(poses):
        points = pose["keypoints"]
        if len(points) != 17 or any(
            len(p) != 3 or not all(math.isfinite(v) for v in p) for p in points
        ):
            continue
        head = [
            points[i]
            for i in rules["head_indices"]
            if points[i][2] >= rules["keypoint_confidence_min"]
        ]
        shoulders = [
            points[i]
            for i in rules["shoulder_indices"]
            if points[i][2] >= rules["keypoint_confidence_min"]
        ]
        if (
            len(head) < rules["minimum_head_points"]
            or len(shoulders) < rules["minimum_shoulder_points"]
        ):
            continue
        if all(box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3] for p in head + shoulders):
            found.append(idx)
    return found


def relation(a: list[int], b: list[int]) -> str:
    if len(a) != 1 or len(b) != 1:
        return "unknown"
    return "same_proposed" if a[0] == b[0] else "different_proposed"


def run(
    config: Path, authorization: Path, acquisition: Path, output: Path, workspace: Path
) -> None:
    workspace = workspace.resolve()
    if output.exists() or not output.resolve().is_relative_to(workspace / "outputs"):
        raise DataContractError("Require new output under workspace outputs")
    raw = load_yaml(config)
    auth, acquired = read_object(authorization), read_object(acquisition)
    if (
        auth["status"] != "owner_approved"
        or FilePin(**auth["proposal"]).verify(workspace) != config.resolve()
        or FilePin(**acquired["authorization"]).verify(workspace) != authorization.resolve()
    ):
        raise DataContractError("Approval mismatch")
    FilePin(**auth["design"]).verify(workspace)
    weights = FilePin(**acquired["weights"]).verify(workspace)
    paths = {k: FilePin(**v).verify(workspace) for k, v in raw["pins"].items()}
    for package, expected in raw["packages"].items():
        if version(package) != expected:
            raise DataContractError(f"Package mismatch: {package}")
    execution = raw["execution"]
    media_deadline(execution)
    cohort = read_object(paths["cohort"])
    if cohort["media_delete_by"] != execution["media_delete_by"]:
        raise DataContractError("Deadline mismatch")
    frames = cohort["frames"]
    if len(frames) != execution["max_model_frame_forwards"]:
        raise DataContractError("Frame budget mismatch")
    sources = {f["frame_index"]: FilePin(**f["source_png"]).verify(workspace) for f in frames}
    detections = [json.loads(line) for line in paths["detections"].read_text().splitlines()]
    d2 = {r["frame_index"]: r["boxes"] for r in detections if r["arm"] == "D2"}
    if set(d2) != set(sources):
        raise DataContractError("Cohort mismatch")
    torch.set_num_threads(execution["threads"])
    random.seed(execution["seed"])
    np.random.seed(execution["seed"])
    torch.manual_seed(execution["seed"])
    output.mkdir(parents=True, exist_ok=False)
    state: dict[str, Any] = {
        "status": "running",
        "config_sha256": sha256_file(config),
        "authorization_sha256": sha256_file(authorization),
        "acquisition_sha256": sha256_file(acquisition),
        "resolved_config": raw,
        "code": code_identity(),
        "environment": environment(),
        "frames_completed": 0,
        "model_frame_forwards_attempted": 0,
        "suppression_applied": False,
        "media_delete_by": execution["media_delete_by"],
    }
    write_json(output / "run.json", state)
    started = time.perf_counter()
    mappings: dict[str, list[int]] = {}
    sections = []
    try:
        os.environ["YOLO_OFFLINE"] = "true"
        os.environ["YOLO_CONFIG_DIR"] = str(workspace / "outputs/runtime-settings")
        ultra = import_module("ultralytics")
        ultra.settings.update({"sync": False})
        model = ultra.YOLO(str(weights), task="pose")
        if model.task != "pose" or list(model.model.model[-1].kpt_shape) != [17, 3]:
            raise DataContractError("Unexpected pose checkpoint schema")
        for frame in frames:
            media_deadline(execution)
            fi = frame["frame_index"]
            with Image.open(sources[fi]) as source:
                img = source.convert("RGB")
            before = time.perf_counter()
            state["model_frame_forwards_attempted"] += 1
            write_json(output / "run.json", state)
            results = model.predict(source=img, **raw["predict"])
            elapsed = time.perf_counter() - before
            media_deadline(execution)
            if len(results) != 1:
                raise DataContractError("Expected one frame result")
            result = results[0]
            poses = []
            if result.boxes is None or result.keypoints is None:
                raise DataContractError("Missing pose output schema")
            boxes = result.boxes.xyxy.cpu().tolist()
            scores = result.boxes.conf.cpu().tolist()
            points = result.keypoints.data.cpu().tolist()
            if len(boxes) != len(points) or len(scores) != len(points):
                raise DataContractError("Pose lengths differ")
            for box, score, kpts in zip(boxes, scores, points, strict=True):
                if (
                    len(kpts) != 17
                    or any(len(p) != 3 for p in kpts)
                    or not all(
                        math.isfinite(v) for v in box + [score] + [v for p in kpts for v in p]
                    )
                ):
                    raise DataContractError("Nonfinite or malformed pose output")
                poses.append({"box": box, "confidence": score, "keypoints": kpts})
            current = {}
            overlay = img.copy()
            draw = ImageDraw.Draw(overlay)
            for box in d2[fi]:
                anchor = f"f{fi:08d}-D2-{box['box_id']}"
                current[anchor] = support(box["xyxy_float"], poses, raw["matching_proposal"])
                draw.rectangle(box["xyxy_float"], outline="cyan", width=2)
                draw.text(tuple(box["xyxy_float"][:2]), box["box_id"], fill="cyan")
            for idx, pose in enumerate(poses):
                draw.rectangle(pose["box"], outline="orange", width=2)
                draw.text(tuple(pose["box"][:2]), f"pose-{idx}", fill="orange")
                for ki, (x, y, confidence) in enumerate(pose["keypoints"]):
                    if confidence >= raw["matching_proposal"]["keypoint_confidence_min"]:
                        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="red")
                        draw.text((x + 3, y), str(ki), fill="red")
            mappings.update(current)
            name = f"f{fi:08d}.png"
            overlay.save(output / name)
            write_json(
                output / f"f{fi:08d}.json",
                {
                    "frame_index": fi,
                    "source": frame["source_png"],
                    "poses": poses,
                    "support": current,
                    "predict_seconds": elapsed,
                },
            )
            source_link = Path(os.path.relpath(sources[fi], output)).as_posix()
            sections.append(
                f'<h2>Frame {fi}</h2><a href="{html.escape(source_link)}">Source</a>'
                f'<a href="{name}"><img src="{name}" width="1000"></a>'
                f'<p><a href="f{fi:08d}.json">Raw pose / support</a></p>'
            )
            state["frames_completed"] += 1
            write_json(output / "run.json", state)
            print(f"Completed {state['frames_completed']}/{len(frames)}", flush=True)
        # Labels are read only after matching, solely for comparison.
        accepted = {}
        for key in ("exception_review", "pair_review"):
            for r in read_object(paths[key])["relations"]:
                if r["status"] == "owner_confirmed":
                    accepted[frozenset(r["anchors"])] = r
        with paths["pair_table"].open(encoding="utf-8", newline="") as handle:
            pairs = [r for r in csv.DictReader(handle) if float(r["iou"]) > 0]
        comparisons = []
        for pair in pairs:
            a, b = pair["anchor_a"], pair["anchor_b"]
            pair["proposed"] = relation(mappings[a], mappings[b])
            reviewed = accepted.get(frozenset((a, b)))
            if reviewed:
                comparisons.append(
                    {
                        **reviewed,
                        "proposed": pair["proposed"],
                        "support_a": mappings[a],
                        "support_b": mappings[b],
                    }
                )
        if len(comparisons) != len(accepted):
            raise DataContractError("Missing reviewed comparison")
        write_json(
            output / "pairs.json",
            {
                "pairs": pairs,
                "comparisons": comparisons,
                "keeper_reference": read_object(paths["keeper_review"]),
                "automatic_keeper": None,
            },
        )
        (output / "index.html").write_text(
            '<!doctype html><html lang="vi"><meta charset="utf-8"><title>Pose diagnostic</title>'
            "<h1>Pose diagnostic — không suppression</h1><p>D2: cyan; pose: orange; "
            "keypoints confidence >= 0.5: red. Pose IDs chỉ trong frame.</p>"
            '<a href="pairs.json">Pair proposals và owner comparisons</a>'
            + "".join(sections)
            + "</html>",
            encoding="utf-8",
        )
        media_deadline(execution)
        state["status"] = "completed"
    except Exception as exc:
        state.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        state["elapsed_seconds"] = time.perf_counter() - started
        write_json(output / "run.json", state)
        checksum_artifacts(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("config", "authorization", "acquisition", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    args = parser.parse_args()
    run(args.config, args.authorization, args.acquisition, args.output, args.workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
