"""CPU prototype use of an approved full bundle; never invokes historical evaluation."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torchvision.transforms import functional as TF

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.training.adaptation_config import SpatialConfig, config_from_dict
from ai_exam_monitoring.training.adaptation_model import AdaptationModel, tensor_digest
from ai_exam_monitoring.training.artifacts import digest_json
from ai_exam_monitoring.training.data import letterbox

from .runtime_config import TARGETS, RuntimeConfig


def read_object(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise DataContractError("Expected JSON object")
    return result


class BundleClassifier:
    def __init__(self, runtime: RuntimeConfig):
        resolved = read_object(runtime.pin("resolved_config"))
        self.config = config_from_dict(resolved)
        bundle = read_object(runtime.pin("bundle"))
        record = read_object(runtime.pin("run"))
        calibration = read_object(runtime.pin("calibration"))
        checkpoint = runtime.pin("checkpoint")
        checkpoint_sha = runtime.raw["pins"]["checkpoint"]["sha256"]
        if (not isinstance(self.config, SpatialConfig)
                or self.config.model != "dinov2_vits14_v4"
                or self.config.pooling != "global_mean"
                or self.config.target_order != TARGETS
                or self.config.experiment_id != "E008-V14-G0-S20261023"
                or record["status"] != "FINISHED"
                or bundle["schema_version"] != "full-model-bundle-v1"
                or bundle["checkpoint_sha256"] != checkpoint_sha
                or bundle["config_sha256"] != digest_json(resolved)
                or record["config_sha256"] != bundle["config_sha256"]
                or record["code_sha256"] != bundle["code_sha256"]
                or bundle["target_order"] != TARGETS
                or calibration["schema_version"] != "selection-calibration-v4"
                or calibration["checkpoint_sha256"] != checkpoint_sha):
            raise DataContractError("Prototype checkpoint/config/calibration identity mismatch")
        self.thresholds = [float(v) for v in calibration["thresholds"]]
        if len(self.thresholds) != 2 or any(not math.isfinite(v) for v in self.thresholds):
            raise DataContractError("Invalid classifier thresholds")
        self.config.weights_license.verify(runtime.workspace)
        payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
        if (payload["schema_version"] != bundle["schema_version"]
                or payload["identity"] != bundle["identity"]
                or payload["config"] != resolved
                or tensor_digest(payload["model"]) != payload["model_tensor_sha256"]
                or any(not torch.isfinite(v).all() for v in payload["model"].values())):
            raise DataContractError("Checkpoint tensor/config identity mismatch")
        self.threads = runtime.raw["classifier"]["threads"]
        torch.set_num_threads(self.threads)
        self.model = AdaptationModel(self.config, full_state=payload["model"],
                                     workspace=runtime.workspace).cpu().float().eval()
        self.model.requires_grad_(False)

    def preview(self, image: Image.Image) -> Image.Image:
        return letterbox(image, self.config)

    def predict(self, image: Image.Image) -> list[float]:
        # Other adapters (including Ultralytics CPU setup) can change this global.
        if torch.get_num_threads() != self.threads:
            torch.set_num_threads(self.threads)
        tensor = TF.normalize(TF.to_tensor(self.preview(image)), self.config.mean, self.config.std)
        with torch.inference_mode():
            logits = self.model(tensor.unsqueeze(0))
            if logits.shape != (1, 2) or not torch.isfinite(logits).all():
                raise DataContractError("Invalid classifier output")
            return [float(v) for v in torch.sigmoid(logits)[0].tolist()]
