"""Approved runtime variables and immutable input pins, separate from training."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.common.provenance import sha256_file
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
    selected_v8s = raw.get("schema_version") == "recorded-runtime-config-v4"
    selected = selected_d2 or selected_v8s
    if raw.get("schema_version") == "recorded-runtime-config-v2" or selected:
        expected.add("sampling_hz")
        if type(raw.get("sampling_hz")) is not int or raw.get("sampling_hz") not in {1, 2}:
            raise ConfigurationError("Only approved 1 Hz or 2 Hz QA sampling is supported")
    if (set(raw) != expected or raw["schema_version"] not in
            {"recorded-runtime-config-v1", "recorded-runtime-config-v2",
             "recorded-runtime-config-v3", "recorded-runtime-config-v4"}):
        raise ConfigurationError("Invalid runtime config schema")
    config = RuntimeConfig(raw, workspace.resolve())
    approval = json.loads(local_path(workspace, raw["approval_ref"]).read_text(encoding="utf-8"))
    if (approval.get("status") != "approved"
            or approval.get("runtime_id") != raw["runtime_id"]
            or approval.get("config_sha256") != config.sha256):
        raise ConfigurationError("Runtime design approval/config mismatch")
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
    if (raw["classifier"] != {"device": "cpu", "batch_size": 1, "threads": 4,
                              "precision": "float32", "target_order": TARGETS}
            or type(raw["gallery_frames"]) is not int or not 1 <= raw["gallery_frames"] <= 20):
        raise ConfigurationError("Unsupported classifier/QA policy")
    return config


def verify_media(path: Path, receipt_path: Path, config: RuntimeConfig) -> dict[str, Any]:
    """A per-source receipt is required; design approval alone is not media consent."""
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(receipt, dict):
        raise ConfigurationError("Expected media approval object")
    schema = receipt.get("schema_version")
    if schema not in {"runtime-media-approval-v1", "runtime-media-approval-v2"}:
        raise ConfigurationError("Unsupported media receipt schema")
    expected = {"schema_version": schema, "status": "approved",
                "runtime_id": config.raw["runtime_id"], "use_scope": "local_prototype_qa",
                "source_sha256": sha256_file(path), "test_or_holdout": False,
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
