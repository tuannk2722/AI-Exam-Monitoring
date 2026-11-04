"""Guarded sequential compute profiling; not an online throughput or quality test.

Requires a new approved execution config and per-source receipt. No default GPU,
batch search, threshold change, image persistence or automatic model fallback.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from importlib import import_module
from pathlib import Path
from typing import Any

import torch

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_config import FilePin, local_path
from ai_exam_monitoring.training.artifacts import (
    checksum_artifacts,
    code_identity,
    digest_json,
    now,
    write_json,
)

from .execution import ExecutionSettings, verify_execution_packages
from .execution_processor import create_execution_processor
from .hardware_probe import probe
from .profiling import StageProfiler
from .runtime_config import RuntimeConfig, load_runtime_config, media_deadline, verify_media
from .video import FrameSampler, RecordedVideo


def load_profile(path: Path, workspace: Path) -> tuple[dict[str, Any], RuntimeConfig,
                                                     ExecutionSettings]:
    raw = load_yaml(path)
    keys = {"schema_version", "profile_id", "runtime", "device", "batch_size", "packages",
            "warmup_samples", "measured_samples", "timing_window", "approval_ref"}
    if (set(raw) != keys or raw.get("schema_version") != "runtime-execution-profile-v1"
            or not isinstance(raw.get("profile_id"), str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]+", raw["profile_id"])):
        raise ConfigurationError("Invalid execution profile")
    for key in ("warmup_samples", "measured_samples", "timing_window"):
        if type(raw[key]) is not int or raw[key] < 1:
            raise ConfigurationError("Explicit positive sample counts/window required")
    settings = ExecutionSettings(raw["device"], raw["batch_size"])
    if (not isinstance(raw["packages"], dict)
            or any(not isinstance(k, str) or not isinstance(v, str)
                   for k, v in raw["packages"].items())):
        raise ConfigurationError("Exact package manifest required")
    approval = json.loads(local_path(workspace, raw["approval_ref"]).read_text(encoding="utf-8"))
    if (approval.get("status") != "approved" or approval.get("profile_id") != raw["profile_id"]
            or approval.get("config_sha256") != digest_json(raw)
            or approval.get("scope") != "local_runtime_compute_profile"
            or not approval.get("decision_ref")):
        raise ConfigurationError("Execution profile approval/config mismatch")
    runtime = load_runtime_config(FilePin(**raw["runtime"]).verify(workspace), workspace)
    if runtime.raw.get("schema_version") != "recorded-runtime-config-v4":
        raise ConfigurationError("Profiling requires the selected V8S runtime parent")
    return raw, runtime, settings


def profile_runtime(config_path: Path, workspace: Path, source: Path,
                    receipt_path: Path, output: Path) -> dict[str, Any]:
    workspace, source, output = workspace.resolve(), source.resolve(), output.resolve()
    if not output.is_relative_to(workspace / "outputs") or output == workspace / "outputs":
        raise DataContractError("Profile output must be a new directory below outputs")
    if not source.is_file() or source.suffix.lower() != ".mp4":
        raise DataContractError("Profile source must be an existing MP4")
    raw, runtime, settings = load_profile(config_path, workspace)
    rights = verify_media(source, receipt_path, runtime)
    media_deadline(rights)
    receipt = json.loads(runtime.pin("detector_receipt").read_text(encoding="utf-8"))
    verify_execution_packages(receipt["packages"], raw["packages"], settings)
    source_video = RecordedVideo(source)
    output.mkdir(parents=True, exist_ok=False)
    profiler = StageProfiler(raw["timing_window"], synchronize=settings.synchronize)
    record: dict[str, Any] = {
        "schema_version": "runtime-compute-profile-result-v1", "profile_id": raw["profile_id"],
        "status": "starting", "started_at": now(), "config_sha256": digest_json(raw),
        "runtime_sha256": runtime.sha256, "source_sha256": rights["source_sha256"],
        "media_delete_by": rights["media_delete_by"], "device": settings.device,
        "batch_size": settings.batch_size, "precision": "float32", "completed_samples": 0,
        "warmup_completed": 0, "observations": 0, "model_quality_accepted": False,
        "online_sla_accepted": False, "startup_ms": None, "warmup_ms": 0.,
        "measured_wall_ms": None, "observed_peak_rss_bytes": 0,
        "cuda_peak_allocated_bytes": None, "cuda_peak_reserved_bytes": None,
    }
    frames = None
    started = time.perf_counter_ns()
    measured_start: int | None = None
    process = import_module("psutil").Process()
    try:
        write_json(output / "config.json", raw)
        write_json(output / "runtime.json", runtime.raw)
        write_json(output / "receipt.json", rights)
        write_json(output / "hardware.json", probe())
        write_json(output / "code.json", code_identity())
        record["input_pins"] = {p.name: sha256_file(p) for p in output.iterdir()}
        media_deadline(rights)
        if settings.device.startswith("cuda:"):
            torch.cuda.reset_peak_memory_stats(settings.resolve())
        load_start = time.perf_counter_ns()
        processor = create_execution_processor(runtime, settings, raw["packages"])
        settings.synchronize()
        record["startup_ms"] = (time.perf_counter_ns() - load_start) / 1e6
        record["status"] = "running"
        sampler = FrameSampler(runtime.raw["sampling_hz"])
        frames = source_video.frames()
        with (output / "samples.jsonl").open("x", encoding="utf-8") as samples:
            while record["completed_samples"] < raw["measured_samples"]:
                media_deadline(rights)
                # Decode timings include all decoded frames, not just sampled ones.
                try:
                    if record["warmup_completed"] < raw["warmup_samples"]:
                        frame = next(frames)
                    else:
                        with profiler.measure("decode"):
                            frame = next(frames)
                except StopIteration as exc:
                    raise DataContractError("Source too short for the configured profile") from exc
                if not sampler.include(frame.time_ms):
                    continue
                if record["warmup_completed"] < raw["warmup_samples"]:
                    warmup_start = time.perf_counter_ns()
                    processor.process(frame)
                    settings.synchronize()
                    media_deadline(rights)
                    record["warmup_ms"] += (time.perf_counter_ns() - warmup_start) / 1e6
                    record["warmup_completed"] += 1
                    if record["warmup_completed"] == raw["warmup_samples"]:
                        processor.profiler = profiler
                        measured_start = time.perf_counter_ns()
                else:
                    row = processor.process(frame)
                    media_deadline(rights)
                    record["completed_samples"] += 1
                    record["observations"] += len(row["observations"])
                    samples.write(json.dumps({
                        "frame_index": frame.index, "source_time_ms": frame.time_ms,
                        "observations": len(row["observations"]),
                    }, allow_nan=False) + "\n")
                    samples.flush()
                record["observed_peak_rss_bytes"] = max(
                    record["observed_peak_rss_bytes"], process.memory_info().rss)
            if measured_start is not None:
                record["measured_wall_ms"] = (time.perf_counter_ns() - measured_start) / 1e6
        if sha256_file(source) != rights["source_sha256"]:
            raise DataContractError("Source changed during profiling")
        current, _, _ = load_profile(config_path, workspace)
        if current != raw or verify_media(source, receipt_path, runtime) != rights:
            raise DataContractError("Profile or receipt changed during execution")
        media_deadline(rights)
        record["status"] = "completed"
    except BaseException as exc:
        record.update(status="failed", error_type=type(exc).__name__)
        raise
    finally:
        if frames is not None:
            close = getattr(frames, "close", None)
            if close is not None:
                close()
        record.update(ended_at=now(), elapsed_ms=(time.perf_counter_ns() - started) / 1e6,
                      timing=profiler.snapshot())
        if settings.device.startswith("cuda:"):
            try:
                device = settings.resolve()
                record["cuda_peak_allocated_bytes"] = torch.cuda.max_memory_allocated(device)
                record["cuda_peak_reserved_bytes"] = torch.cuda.max_memory_reserved(device)
            except (RuntimeError, DataContractError):
                record["cuda_memory_unavailable"] = True
        write_json(output / "profile.json", record)
        checksum_artifacts(output)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = profile_runtime(args.config, args.workspace, args.source, args.receipt, args.output)
    print(json.dumps({"status": result["status"],
                      "completed_samples": result["completed_samples"]}))


if __name__ == "__main__":
    main()
