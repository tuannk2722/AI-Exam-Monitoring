"""Build a device-aware processor without changing historical runtime variables.

Internal construction only. Callers own source rights, approved execution profile,
warm-up, provenance and lifetime. The existing web/CLI factories remain CPU-only.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

from ai_exam_monitoring.common.errors import DataContractError

from .classifier import BundleClassifier
from .execution import ExecutionSettings, verify_execution_packages
from .frame_processor import FrameProcessor
from .person import PersonDetector
from .profiling import StageProfiler
from .runtime_config import RuntimeConfig


def create_execution_processor(runtime: RuntimeConfig, settings: ExecutionSettings,
                               packages: Mapping[str, str], *,
                               profiler: StageProfiler | None = None) -> FrameProcessor:
    if runtime.raw.get("schema_version") != "recorded-runtime-config-v4":
        raise DataContractError("Execution adapter requires the approved V8S parent runtime")
    receipt = json.loads(runtime.pin("detector_receipt").read_text(encoding="utf-8"))
    # Fail before checkpoint allocation, model setup or third-party imports.
    verify_execution_packages(receipt["packages"], packages, settings)
    classifier = BundleClassifier(runtime, execution=settings)
    detector = PersonDetector(runtime, execution=settings, packages=packages)
    return FrameProcessor(detector, classifier, runtime.raw["crop"],
                          batch_size=settings.batch_size, profiler=profiler)
