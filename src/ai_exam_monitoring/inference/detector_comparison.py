"""Approved detector comparison; owner census and post-run matching remain separate."""

from __future__ import annotations

import argparse
import html
import json
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
from .person import PersonDetection, crop_boxes
from .runtime_config import media_deadline


def validate_census(census: dict[str, Any], cohort: dict[str, Any]) -> None:
    if (
        census.get("status") != "accepted"
        or census.get("reviewer") != "repository-owner"
        or not census.get("decision_ref")
    ):
        raise DataContractError("Accepted owner census required")
    frames = census.get("frames", [])
    if [f["frame_index"] for f in frames] != [f["frame_index"] for f in cohort["frames"]]:
        raise DataContractError("Census cohort mismatch")
    for f in frames:
        people = f.get("people", [])
        ids = [p["person_id"] for p in people]
        anchors = [a for p in people for a in p["anchors"]]
        if (
            f.get("complete_visible_person_census") is not True
            or len(ids) != len(set(ids))
            or len(anchors) != len(set(anchors))
            or f.get("missing_people") != []
            or f.get("false_boxes") != []
        ):
            raise DataContractError("Incomplete or conflicting census")


def run(
    config: Path,
    authorization: Path,
    acquisition: Path,
    census_path: Path,
    output: Path,
    workspace: Path,
) -> None:
    workspace = workspace.resolve()
    if output.exists() or not output.resolve().is_relative_to(workspace / "outputs"):
        raise DataContractError("New output required")
    raw = load_yaml(config)
    auth = read_object(authorization)
    acq = read_object(acquisition)
    if (
        auth["status"] != "owner_approved"
        or FilePin(**auth["proposal"]).verify(workspace) != config.resolve()
        or FilePin(**acq["authorization"]).verify(workspace) != authorization.resolve()
    ):
        raise DataContractError("Authorization mismatch")
    FilePin(**auth["design"]).verify(workspace)
    paths = {k: FilePin(**v).verify(workspace) for k, v in raw["pins"].items()}
    for package, expected in raw["packages"].items():
        if version(package) != expected:
            raise DataContractError("Package mismatch")
    cohort = read_object(paths["cohort"])
    census = read_object(census_path)
    validate_census(census, cohort)
    decision = FilePin(**census["decision_ref"]).verify(workspace)
    receipt = read_object(decision)
    if receipt.get("complete_visible_person_census") is not True:
        raise DataContractError("Completeness decision missing")
    reviewed = FilePin(**receipt["reviewed_census"]).verify(workspace)
    original = read_object(reviewed)
    if [[p for p in f["people"]] for f in census["frames"]] != [
        f["people"] for f in original["frames"]
    ]:
        raise DataContractError("Census people differ from reviewed revision")
    execution = raw["execution"]
    media_deadline(execution)
    if execution["media_delete_by"] != cohort["media_delete_by"]:
        raise DataContractError("Deadline mismatch")
    frames = cohort["frames"]
    arms = raw["arms"][1:]
    if len(frames) * len(arms) != execution["new_frame_forwards"]:
        raise DataContractError("Forward budget mismatch")
    sources = {f["frame_index"]: FilePin(**f["source_png"]).verify(workspace) for f in frames}
    weights = {
        a["id"]: FilePin(**acq["assets"][a["id"]]["weights"]).verify(workspace) for a in arms
    }
    checks = read_object(paths["D2_checksums"])
    for k in ("D2_detections", "D2_run"):
        if checks[paths[k].name] != sha256_file(paths[k]):
            raise DataContractError("Baseline checksum mismatch")
    baseline = [
        r
        for r in map(json.loads, paths["D2_detections"].read_text().splitlines())
        if r["arm"] == "D2"
    ]
    if [f["frame_index"] for f in baseline] != list(sources):
        raise DataContractError("Baseline frames mismatch")
    margins = load_yaml(paths["D2_runtime"])["crop"]
    torch.set_num_threads(execution["threads"])
    torch.manual_seed(execution["seed"])
    np.random.seed(execution["seed"])
    random.seed(execution["seed"])
    output.mkdir(parents=True, exist_ok=False)
    state: dict[str, Any] = {
        "status": "running",
        "resolved_config": raw,
        "config_sha256": sha256_file(config),
        "authorization_sha256": sha256_file(authorization),
        "acquisition_sha256": sha256_file(acquisition),
        "census_sha256": sha256_file(census_path),
        "code": code_identity(),
        "environment": environment(),
        "attempted_forwards": 0,
        "completed_forwards": 0,
        "media_delete_by": execution["media_delete_by"],
        "winner": None,
        "quality_acceptance": "pending_owner_matching",
    }
    write_json(output / "run.json", state)
    write_json(output / "census.json", census)
    write_json(output / "baseline.json", {"frames": baseline})
    records = []
    started = time.perf_counter()
    try:
        os.environ["YOLO_OFFLINE"] = "true"
        os.environ["YOLO_CONFIG_DIR"] = str(workspace / "outputs/runtime-settings")
        ultra = import_module("ultralytics")
        ultra.settings.update({"sync": False})
        for arm in arms:
            model = ultra.YOLO(str(weights[arm["id"]]), task="detect")
            if model.names.get(0) != "person" or bool(
                getattr(model.model, "end2end", False)
            ) != bool(arm.get("require_end2end", False)):
                raise DataContractError("Model taxonomy/end2end mismatch")
            predict = dict(raw["common_predict"])
            if arm["iou"] is not None:
                predict["iou"] = arm["iou"]
            for f in frames:
                media_deadline(execution)
                fi = f["frame_index"]
                with Image.open(sources[fi]) as src:
                    img = src.convert("RGB")
                state["attempted_forwards"] += 1
                write_json(output / "run.json", state)
                before = time.perf_counter()
                results = model.predict(source=img, **predict)
                elapsed = time.perf_counter() - before
                media_deadline(execution)
                if len(results) != 1 or results[0].boxes is None:
                    raise DataContractError("Invalid detector result")
                detections = []
                overlay = img.copy()
                draw = ImageDraw.Draw(overlay)
                for i, b in enumerate(results[0].boxes):
                    if int(b.cls.item()) != 0:
                        raise DataContractError("Nonperson output")
                    xy = [float(v) for v in b.xyxy[0].tolist()]
                    if len(xy) != 4:
                        raise DataContractError("Expected four box coordinates")
                    detection = PersonDetection((xy[0], xy[1], xy[2], xy[3]), float(b.conf.item()))
                    person, context = crop_boxes(detection, img.size, margins)
                    ident = f"f{fi:08d}-{arm['id']}-b{i:03d}"
                    detections.append(
                        {
                            "anchor_id": ident,
                            "xyxy_float": xy,
                            "person_box": person,
                            "context_box": context,
                            "confidence": detection.confidence,
                            "person_assignment": "unknown",
                        }
                    )
                    draw.rectangle(person, outline="cyan", width=2)
                    draw.text(
                        (person[0] + 2, person[1] + 2),
                        f"b{i:03d}",
                        fill="cyan",
                        stroke_width=1,
                        stroke_fill="black",
                    )
                name = f"{arm['id']}-f{fi:08d}.png"
                overlay.save(output / name)
                record = {
                    "arm": arm["id"],
                    "frame_index": fi,
                    "source": f["source_png"],
                    "predict_seconds": elapsed,
                    "boxes": detections,
                }
                records.append(record)
                write_json(output / f"{arm['id']}-f{fi:08d}.json", record)
                state["completed_forwards"] += 1
                write_json(output / "run.json", state)
                print(f"{arm['id']}: {state['completed_forwards']}/38", flush=True)
            del model
        write_json(output / "detections.json", {"frames": records})
        sections = []
        for f in frames:
            fi = f["frame_index"]
            link = html.escape(Path(os.path.relpath(sources[fi], output)).as_posix())
            sections.append(
                f'<section><h2>{fi / 30:g}s / frame {fi}</h2><a href="{link}">Source</a>'
            )
            media_deadline(execution)
            with Image.open(sources[fi]) as source:
                overlay = source.convert("RGB")
            draw = ImageDraw.Draw(overlay)
            for box in next(row["boxes"] for row in baseline if row["frame_index"] == fi):
                draw.rectangle(box["person_box"], outline="orange", width=2)
                draw.text(tuple(box["person_box"][:2]), box["box_id"], fill="orange")
            baseline_image = f"D2-f{fi:08d}.png"
            overlay.save(output / baseline_image)
            sections.append(f'<h3>D2 cached</h3><img src="{baseline_image}">')
            for arm in arms:
                name = f"{arm['id']}-f{fi:08d}.png"
                sections.append(f'<h3>{arm["id"]}</h3><a href="{name}"><img src="{name}"></a>')
            sections.append("</section>")
        (output / "index.html").write_text(
            '<!doctype html><meta charset="utf-8"><title>Detector comparison</title>'
            "<style>body{font:17px system-ui;margin:24px}img{max-width:100%}</style>"
            "<h1>Đối chứng detector — chờ matching</h1>"
            "<p>Chưa chọn winner; tổng box không phải số người được tìm đúng.</p>"
            '<a href="census.json">Accepted census</a> | <a href="baseline.json">D2 baseline</a>'
            + "".join(sections),
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
    for k in ("config", "authorization", "acquisition", "census", "output"):
        parser.add_argument("--" + k, type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    a = parser.parse_args()
    run(a.config, a.authorization, a.acquisition, a.census, a.output, a.workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
