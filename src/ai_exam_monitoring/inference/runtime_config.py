"""Approved runtime variables and immutable input pins, separate from training."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import (
    MULTILABEL_SEMANTICS_VERSION,
    MULTILABEL_TARGET_ORDER,
)
from ai_exam_monitoring.training.adaptation_config import FilePin, local_path
from ai_exam_monitoring.training.artifacts import digest_json

TARGETS = ["phone_use", "looking_around"]


def media_deadline(receipt: dict[str, Any]) -> datetime:
    """New execution needs an absolute deadline; never renew retention on rerun."""
    try:
        deadline = datetime.fromisoformat(receipt["media_delete_by"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigurationError("Explicit media_delete_by is required for execution") from exc
    now = datetime.now(UTC)
    if deadline.tzinfo is None or deadline <= now or deadline > now + timedelta(days=7):
        raise ConfigurationError("Media deadline must be aware, unexpired and within seven days")
    return deadline


@dataclass(frozen=True)
class RuntimeConfig:
    raw: dict[str, Any]
    workspace: Path

    @property
    def sha256(self) -> str:
        return digest_json(self.raw)

    def pin(self, name: str) -> Path:
        return FilePin(**self.raw["pins"][name]).verify(self.workspace)


def load_runtime_config(path: Path, workspace: Path) -> RuntimeConfig:
    raw = load_yaml(path)
    expected = {"schema_version", "runtime_id", "approval_ref", "pins", "detector",
                "crop", "classifier", "gallery_frames"}
    selected_d2 = raw.get("schema_version") == "recorded-runtime-config-v3"
    e009 = raw.get("schema_version") == "recorded-runtime-config-v5"
    selected_v8s = raw.get("schema_version") == "recorded-runtime-config-v4" or e009
    selected = selected_d2 or selected_v8s
    if raw.get("schema_version") == "recorded-runtime-config-v2" or selected:
        expected.add("sampling_hz")
        if type(raw.get("sampling_hz")) is not int or raw.get("sampling_hz") not in {1, 2}:
            raise ConfigurationError("Only approved 1 Hz or 2 Hz QA sampling is supported")
    if (set(raw) != expected or raw["schema_version"] not in
            {"recorded-runtime-config-v1", "recorded-runtime-config-v2",
             "recorded-runtime-config-v3", "recorded-runtime-config-v4",
             "recorded-runtime-config-v5"}):
        raise ConfigurationError("Invalid runtime config schema")
    config = RuntimeConfig(raw, workspace.resolve())
    approval = json.loads(local_path(workspace, raw["approval_ref"]).read_text(encoding="utf-8"))
    if (approval.get("status") != "approved"
            or approval.get("runtime_id") != raw["runtime_id"]
            or approval.get("config_sha256") != config.sha256):
        raise ConfigurationError("Runtime design approval/config mismatch")
    if e009:
        decision = FilePin(**approval["decision_ref"]).read_json(config.workspace)
        if (decision.get("status") != "approved"
                or decision.get("runtime_id") != raw["runtime_id"]
                or decision.get("models", {}).get(raw["classifier"].get("model_id"))
                != raw["classifier"].get("experiment_id")):
            raise ConfigurationError("Model choice differs from owner decision")
    expected_pins = {"checkpoint", "resolved_config", "calibration", "bundle",
                     "run", "detector_weights", "detector_receipt"}
    if selected:
        expected_pins.add("detector_selection")
    if set(raw["pins"]) != expected_pins:
        raise ConfigurationError("Incomplete runtime pins")
    for name in expected_pins:
        config.pin(name)
    policy = {"imgsz": 640, "conf": 0.25, "iou": 0.3 if selected else 0.7,
              "max_det": 100, "device": "cpu", "half": False}
    if selected_v8s:
        policy.update(rect=True, augment=False, batch=1)
    if raw["detector"] != policy:
        raise ConfigurationError("Unsupported detector policy")
    if selected:
        selection = json.loads(config.pin("detector_selection").read_text(encoding="utf-8"))
        if (selection.get("status") != "accepted"
                or selection.get("winner") != ("V8S" if selected_v8s else "D2")
                or selection.get("detector") != raw["detector"]
                or selection.get("detector_weights") != raw["pins"]["detector_weights"]
                or not selection.get("decision_ref")):
            raise ConfigurationError("Detector selection/weights/policy mismatch")
        if selected_v8s:
            FilePin(**selection["decision_ref"]).verify(config.workspace)
            for pin in selection["evidence"].values():
                FilePin(**pin).verify(config.workspace)
    if raw["crop"] != {"version": "context-v1", "left": 0.2, "right": 0.2,
                       "top": 0.1, "bottom": 0.2}:
        raise ConfigurationError("Unsupported crop policy")
    classifier = {"device": "cpu", "batch_size": 1, "threads": 4,
                  "precision": "float32", "target_order": TARGETS}
    if e009:
        binding = raw["classifier"]
        multilabel = binding.get("target_order") == list(MULTILABEL_TARGET_ORDER)
        if multilabel:
            if (not isinstance(binding.get("model_id"), str)
                    or re.fullmatch(r"[A-Za-z0-9_-]+", binding["model_id"]) is None
                    or type(binding.get("image_size")) is not int or binding["image_size"] <= 0
                    or binding["image_size"] % 14
                    or binding.get("model") not in {"dinov2_vits14_v6", "dinov2_vitb14_v6"}
                    or binding.get("semantics_version") != MULTILABEL_SEMANTICS_VERSION):
                raise ConfigurationError("Invalid five-target model/semantics binding")
            classifier.update(target_order=list(MULTILABEL_TARGET_ORDER),
                              semantics_version=MULTILABEL_SEMANTICS_VERSION)
        if ((not multilabel and binding.get("model_id") not in {"B0", "B448"})
                or not isinstance(binding.get("experiment_id"), str)
                or (not multilabel and (binding.get("image_size") not in {336, 448}
                                       or binding.get("model") != "dinov2_vitb14_v6"))):
            raise ConfigurationError("Unsupported E009 model binding")
        classifier.update({key: binding[key] for key in
                           ("model_id", "experiment_id", "image_size", "model")})
    if (raw["classifier"] != classifier
            or type(raw["gallery_frames"]) is not int or not 1 <= raw["gallery_frames"] <= 20):
        raise ConfigurationError("Unsupported classifier/QA policy")
    return config


def verify_media(path: Path, receipt_path: Path, config: RuntimeConfig) -> dict[str, Any]:
    """A per-source receipt is required; design approval alone is not media consent."""
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    return verify_media_receipt(receipt, config, source_sha256=sha256_file(path))


def verify_media_receipt(receipt: Any, config: RuntimeConfig,
                         *, source_sha256: str) -> dict[str, Any]:
    """Validate declared rights before upload; verify bytes against the SHA afterwards."""
    if not isinstance(receipt, dict):
        raise ConfigurationError("Expected media approval object")
    schema = receipt.get("schema_version")
    if schema not in {"runtime-media-approval-v1", "runtime-media-approval-v2"}:
        raise ConfigurationError("Unsupported media receipt schema")
    expected = {"schema_version": schema, "status": "approved",
                "runtime_id": config.raw["runtime_id"], "use_scope": "local_prototype_qa",
                "source_sha256": source_sha256, "test_or_holdout": False,
                "rights_confirmed": True, "third_party_processing": False,
                "access": "repository_owner", "retention_days": 7}
    if any(receipt.get(k) != v for k, v in expected.items()) or not receipt.get("decision_ref"):
        raise ConfigurationError("Missing/mismatched source rights and media policy approval")
    if schema == "runtime-media-approval-v2":
        deadline = media_deadline(receipt)
        if "parent_session" in receipt:
            parent = FilePin(**receipt["parent_session"]).read_json(config.workspace)
            if (parent.get("source_sha256") != receipt["source_sha256"]
                    or parent.get("media_delete_by") is None
                    or deadline > datetime.fromisoformat(parent["media_delete_by"])):
                raise ConfigurationError("Media receipt cannot extend parent source retention")
    return receipt
