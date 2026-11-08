"""Build a device-aware processor without changing historical runtime variables.

Internal construction only. Callers own source rights, approved execution profile,
warm-up, provenance and lifetime. Web GPU requires an explicit measured selection;
legacy callers retain their CPU runtime and package checks.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import digest_json

from .classifier import BundleClassifier
from .execution import ExecutionSettings, verify_execution_packages
from .frame_processor import FrameProcessor
from .person import PersonDetector
from .profiling import StageProfiler
from .runtime_config import RuntimeConfig


def load_execution_selection(path: Path, workspace: Path,
                             runtime: RuntimeConfig) -> tuple[dict[str, Any], ExecutionSettings]:
    """Validate the measured GPU selection without allocating a model/device."""
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if (raw.get("schema_version") != "video-web-execution-v1"
            or raw.get("status") != "approved" or raw.get("scope") != "local_video_web"
            or raw.get("runtime_sha256") != runtime.sha256
            or raw.get("precision") != "float32"
            or raw.get("device") != "cuda:0" or raw.get("batch_size") != 1
            or not isinstance(raw.get("packages"), dict)):
        raise DataContractError("Video web execution selection mismatch")
    FilePin(**raw["decision_ref"]).verify(workspace)
    parity = FilePin(**raw["parity"]).read_json(workspace)
    profile = FilePin(**raw["profile"]).read_json(workspace)
    code = FilePin(**raw["profile_code"]).read_json(workspace)
    if (parity.get("status") != "completed" or profile.get("status") != "completed"
            or parity.get("runtime_sha256") != runtime.sha256
            or profile.get("runtime_sha256") != runtime.sha256
            or parity.get("source_sha256") != profile.get("source_sha256")
            or profile.get("device") != raw["device"]
            or profile.get("batch_size") != raw["batch_size"]
            or profile.get("precision") != raw["precision"]
            or code.get("sha256") != digest_json(code.get("files"))):
        raise DataContractError("Video web selection lacks matching measured evidence")
    # Keep numerical producers identical to the successful laptop run. Transport
    # integration may change without rewriting that run's whole-package identity.
    package = Path(__file__).resolve().parents[1]
    for name in ("inference/classifier.py", "inference/frame_processor.py",
                 "inference/person.py", "inference/execution.py",
                 "training/adaptation_model.py", "training/encoders.py", "training/data.py"):
        digest = hashlib.sha256((package / name).read_text(encoding="utf-8").encode()).hexdigest()
        if code["files"].get(name) != digest:
            raise DataContractError(f"Measured numerical source changed: {name}")
    return raw, ExecutionSettings(raw["device"], raw["batch_size"])


def create_execution_processor(runtime: RuntimeConfig, settings: ExecutionSettings,
                               packages: Mapping[str, str], *,
                               profiler: StageProfiler | None = None) -> FrameProcessor:
    if runtime.raw.get("schema_version") not in {
        "recorded-runtime-config-v4", "recorded-runtime-config-v5",
    }:
        raise DataContractError("Execution adapter requires an approved V8S/E009 parent runtime")
    receipt = json.loads(runtime.pin("detector_receipt").read_text(encoding="utf-8"))
    # Fail before checkpoint allocation, model setup or third-party imports.
    verify_execution_packages(receipt["packages"], packages, settings)
    classifier = BundleClassifier(runtime, execution=settings)
    detector = PersonDetector(runtime, execution=settings, packages=packages)
    return FrameProcessor(detector, classifier, runtime.raw["crop"],
                          batch_size=settings.batch_size, profiler=profiler)
