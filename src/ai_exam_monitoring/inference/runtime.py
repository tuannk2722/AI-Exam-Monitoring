"""Recorded video -> person -> context -> real classifier observations and QA."""
from __future__ import annotations

import argparse
import html
import json
import math
import time
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

import numpy as np
from PIL import Image, ImageDraw

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    digest_json,
    environment,
    write_json,
)
from ai_exam_monitoring.training.train import peak_rss

from .classifier import BundleClassifier
from .person import PersonDetection, PersonDetector, crop_boxes
from .runtime_config import (
    TARGETS,
    RuntimeConfig,
    load_runtime_config,
    media_deadline,
    verify_media,
)
from .video import RecordedVideo, VideoFrame, qa_indices, sample_indices, validate_time


class Detector(Protocol):
    def predict(self, image: Image.Image) -> list[PersonDetection]: ...


class Classifier(Protocol):
    thresholds: list[float]

    def predict(self, image: Image.Image) -> list[float]: ...
    def preview(self, image: Image.Image) -> Image.Image: ...


def write_gallery(output: Path, sections: list[str], error: str | None = None) -> None:
    title = "Kiểm tra crop runtime — chưa nghiệm thu chất lượng"
    document = ("<!doctype html><html lang='vi'><meta charset='utf-8'>"
                f"<title>{title}</title><style>body{{font:16px sans-serif;margin:24px}}"
                "img{max-width:640px;max-height:360px}section{border-top:1px solid #aaa;"
                "padding:16px 0}figure{display:inline-block;vertical-align:top;margin:8px}"
                "</style><h1>" + title + "</h1><p>Source → person/context → crop → input. "
                "Scores không phải nhãn thật; không kết luận gian lận.</p>"
                + (f"<p>FAILED: {html.escape(error)}</p>" if error else "")
                + "".join(sections) + "</html>")
    (output / "index.html").write_text(document, encoding="utf-8")


def process_frames(
    frames: Iterable[VideoFrame], detector: Detector, classifier: Classifier,
    config: RuntimeConfig, output: Path, metadata: dict[str, Any], selected: set[int],
    *, expected_times: list[float] | None = None,
    expected_indices: list[int] | None = None,
) -> dict[str, Any]:
    """Stream outputs; injected protocols exist for software fixtures, not CLI fallback."""
    previous: float | None = None
    frame_count = observation_count = 0
    times: list[float] = []
    sections: list[str] = []
    current: VideoFrame | None = None
    thresholds = classifier.thresholds
    if len(thresholds) != 2 or any(not math.isfinite(v) for v in thresholds):
        raise DataContractError("Invalid operating thresholds")
    with (output / "predictions.jsonl").open("x", encoding="utf-8") as handle:
        def emit(row: dict[str, Any]) -> None:
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            handle.flush()

        emit({"record_type": "metadata", "schema_version": "recorded-observations-v1",
              **metadata, "target_order": TARGETS, "thresholds": thresholds})
        try:
            for frame in frames:
                if "media_delete_by" in metadata:
                    media_deadline(metadata)
                current = frame
                started = time.perf_counter()
                expected_index = (expected_indices[frame_count]
                                  if expected_indices is not None
                                  and frame_count < len(expected_indices) else frame_count)
                if frame.index != expected_index:
                    raise DataContractError("Missing or duplicated video frame")
                validate_time(frame.time_ms, previous)
                previous = frame.time_ms
                if expected_times is not None and (
                    frame_count >= len(expected_times)
                    or frame.time_ms != expected_times[frame_count]
                ):
                    raise DataContractError("Decode timestamp changed after preflight")
                annotated = frame.image.copy()
                draw = ImageDraw.Draw(annotated)
                figures: list[str] = []
                observations: list[dict[str, Any]] = []
                for index, detection in enumerate(detector.predict(frame.image)):
                    person, context = crop_boxes(detection, frame.image.size, config.raw["crop"])
                    crop = frame.image.crop(context)
                    scores = classifier.predict(crop)
                    if len(scores) != 2 or any(not math.isfinite(v) or not 0 <= v <= 1
                                               for v in scores):
                        raise DataContractError("Invalid behavior scores")
                    anchor = f"f{frame.index:08d}-a{index:03d}"
                    observations.append({"anchor_id": anchor, "person_box": person,
                                         "context_box": context,
                                         "detector_confidence": detection.confidence,
                                         "scores": scores,
                                         "above_threshold": [s >= t for s, t in
                                                             zip(scores, thresholds, strict=True)]})
                    if frame.index in selected:
                        crop.save(output / f"{anchor}-crop.png")
                        classifier.preview(crop).save(output / f"{anchor}-input.png")
                        draw.rectangle(person, outline="lime", width=2)
                        draw.rectangle(context, outline="orange", width=2)
                        draw.text((person[0], person[1]), anchor, fill="lime")
                        figures.append(f"<figure><figcaption>{anchor}: {scores[0]:.4f}, "
                                       f"{scores[1]:.4f}</figcaption><img src='{anchor}-crop.png'>"
                                       f"<img src='{anchor}-input.png'></figure>")
                emit({"record_type": "frame", "frame_index": frame.index,
                      "video_time_ms": frame.time_ms, "width": frame.image.width,
                      "height": frame.image.height, "observations": observations})
                if frame.index in selected:
                    source_name = f"f{frame.index:08d}-source.png"
                    boxes_name = f"f{frame.index:08d}-boxes.png"
                    frame.image.save(output / source_name)
                    annotated.save(output / boxes_name)
                    sections.append(f"<section><h2>Frame {frame.index} — {frame.time_ms:.3f} ms"
                                    f"</h2><img src='{source_name}'><img src='{boxes_name}'>"
                                    + ("".join(figures) or "<p>Không detection.</p>")
                                    + "</section>")
                frame_count += 1
                observation_count += len(observations)
                times.append((time.perf_counter() - started) * 1000)
                # The iterator may fail before yielding another source frame.
                current = None
            if frame_count == 0 or (expected_times is not None
                                    and frame_count != len(expected_times)):
                raise DataContractError("Incomplete or empty decoded session")
        except BaseException as exc:
            # Avoid logging exception text that can contain private input paths.
            error = type(exc).__name__
            emit({"record_type": "outcome", "status": "failed", "error_type": error,
                  "completed_frames": frame_count,
                  "failed_frame_index": current.index if current is not None else None})
            if current is not None and len(sections) < config.raw.get("gallery_frames", 20):
                current.image.save(output / "failed-frame.png")
                sections.append(f"<section><h2>Lỗi tại frame {current.index}</h2>"
                                "<img src='failed-frame.png'></section>")
            write_gallery(output, sections, error)
            raise
        emit({"record_type": "frames_processed", "frames": frame_count})
    write_gallery(output, sections)
    return {"frames": frame_count, "observations": observation_count,
            "frame_processing_ms": times, "timing_scope": "detector_classifier_jsonl_qa_io",
            "mean_frame_ms": sum(times) / len(times), "peak_rss_bytes": peak_rss(),
            "p50_frame_ms": float(np.percentile(times, 50)),
            "p95_frame_ms": float(np.percentile(times, 95)),
            "quality_acceptance": "pending_owner_qa"}


def run_video(config_path: Path, workspace: Path, source: Path,
              media_approval: Path, output: Path) -> dict[str, Any]:
    workspace, source, output = workspace.resolve(), source.resolve(), output.resolve()
    if output.exists() or not output.is_relative_to(workspace / "outputs"):
        raise DataContractError("Require new output directory under workspace outputs")
    if not source.is_file() or source.suffix.lower() != ".mp4":
        raise DataContractError("Require an existing local MP4")
    config = load_runtime_config(config_path, workspace)
    rights = verify_media(source, media_approval, config)
    deadline = media_deadline(rights).isoformat()
    source_sha = rights["source_sha256"]
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    record: dict[str, Any] = {"schema_version": "recorded-session-v1", "status": "running",
                              "runtime_id": config.raw["runtime_id"],
                              "source_sha256": source_sha, "config_sha256": config.sha256,
                              "media_approval_sha256": sha256_file(media_approval),
                              "started_at": datetime.now(UTC).isoformat(),
                              "media_delete_by": deadline}
    write_json(output / "session.json", record)
    try:
        # Decode pass one validates the entire clip and samples uniformly in video time.
        video = RecordedVideo(source)
        timestamps = []
        for frame in video.frames():
            media_deadline(rights)
            timestamps.append(frame.time_ms)
        indices = (sample_indices(timestamps, config.raw["sampling_hz"])
                   if "sampling_hz" in config.raw else list(range(len(timestamps))))
        sampled_times = [timestamps[i] for i in indices]
        included = set(indices)
        # Reserve one QA slot for a technical failure frame.
        selected = {indices[i] for i in qa_indices(
            sampled_times, max(1, config.raw["gallery_frames"] - 1))}
        classifier = BundleClassifier(config)
        detector = PersonDetector(config)
        record["startup_seconds"] = time.perf_counter() - started
        env = environment()
        env["command"] = ["ai_exam_monitoring.inference.runtime",
                          "config_sha256=" + config.sha256, "source_sha256=" + source_sha]
        write_json(output / "environment.json", env)
        write_json(output / "code-provenance.json", code_identity())
        write_json(output / "runtime-config.json", config.raw)
        metadata = {"source_sha256": source_sha, "runtime_id": config.raw["runtime_id"],
                    "config_sha256": config.sha256, "code_sha256": code_identity()["sha256"],
                    "environment_sha256": digest_json(env), "pins": config.raw["pins"],
                    "crop_policy": config.raw["crop"], "fps": video.fps,
                    "qa_frame_indices": sorted(selected), "media_delete_by": deadline}
        metadata.update(sampling_hz=config.raw.get("sampling_hz"),
                        source_frame_count=len(timestamps), sampled_frame_indices=indices)
        record.update(source_frame_count=len(timestamps),
                      sampling_hz=config.raw.get("sampling_hz"), sampled_frame_indices=indices)
        record.update(process_frames((f for f in video.frames() if f.index in included),
                                     detector, classifier, config, output,
                                     metadata, selected, expected_times=sampled_times,
                                     expected_indices=indices))
        if sha256_file(source) != source_sha:
            raise DataContractError("Video changed during processing")
        media_deadline(rights)
        record["status"] = "completed"
    except BaseException as exc:
        record.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        record["elapsed_seconds"] = time.perf_counter() - started
        record["ended_at"] = datetime.now(UTC).isoformat()
        write_json(output / "session.json", record)
        with (output / "predictions.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"record_type": "outcome", "status": record["status"],
                                     "error_type": record.get("error_type")}) + "\n")
        checksum_artifacts(output)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Recorded-video prototype with approved pins")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--media-approval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        run_video(args.config, args.workspace, args.source, args.media_approval, args.output)
    except Exception as exc:
        parser.exit(1, f"Runtime failed ({type(exc).__name__}); inspect session.json if created.\n")
    print("Runtime completed; owner crop/video QA remains required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
