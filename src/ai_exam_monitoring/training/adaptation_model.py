"""Full ResNet18 models with explicit trainable parameters and immutable BN buffers."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import torch
from torch import nn
from torchvision.models import resnet18

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .adaptation_config import AdaptationConfig
from .artifacts import save_checkpoint


def tensor_digest(state: Mapping[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        value = tensor.detach().cpu().contiguous()
        digest.update(f"{name}:{value.dtype}:{tuple(value.shape)}\n".encode())
        digest.update(value.numpy().tobytes())
    return digest.hexdigest()


def create_initial_head(path: Path, seed: int) -> str:
    if path.exists():
        raise DataContractError("Head initialization must have a new immutable path")
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(seed)
        head = nn.Linear(512, 2)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_checkpoint(
        path,
        {
            "schema_version": "linear-head-init-v1",
            "seed": seed,
            "head": head.state_dict(),
            "tensor_sha256": tensor_digest(head.state_dict()),
        },
    )
    return sha256_file(path)


class AdaptationModel(nn.Module):
    def __init__(
        self,
        config: AdaptationConfig,
        *,
        weights: Path | None = None,
        initial_head: Path | None = None,
        full_state: Mapping[str, torch.Tensor] | None = None,
    ):
        super().__init__()
        self.policy = config.model
        self.network = resnet18(weights=None)
        if full_state is None:
            if (
                weights is None
                or initial_head is None
                or sha256_file(weights) != config.weights.sha256
                or sha256_file(initial_head) != config.head_initialization.sha256
            ):
                raise DataContractError("Missing or changed pretrained/head initialization")
            self.network.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
            self.network.fc = nn.Linear(512, 2)
            payload = torch.load(initial_head, map_location="cpu", weights_only=True)
            if (
                payload["schema_version"] != "linear-head-init-v1"
                or payload["seed"] != config.seed
                or tensor_digest(payload["head"]) != payload["tensor_sha256"]
            ):
                raise DataContractError("Head initialization identity mismatch")
            self.network.fc.load_state_dict(payload["head"])
        else:
            if weights is not None or initial_head is not None:
                raise DataContractError("Standalone reload cannot also load external weights")
            self.network.fc = nn.Linear(512, 2)
            self.load_state_dict(full_state, strict=True)
        self.requires_grad_(False)
        self.network.fc.requires_grad_(True)
        if self.policy == "resnet18_layer4":
            self.network.layer4.requires_grad_(True)
        self.train()

    def train(self, mode: bool = True) -> AdaptationModel:
        super().train(mode)
        for module in self.modules():
            if isinstance(module, nn.modules.batchnorm._BatchNorm):
                module.eval()
        return self

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return cast(torch.Tensor, self.network(images))

    def parameter_groups(
        self, config: AdaptationConfig
    ) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
        names: dict[str, list[str]] = {"head": [], "layer4": []}
        params: dict[str, list[nn.Parameter]] = {"head": [], "layer4": []}
        for name, parameter in self.named_parameters():
            if not parameter.requires_grad:
                continue
            group = "head" if name.startswith("network.fc.") else "layer4"
            if group == "layer4" and not name.startswith("network.layer4."):
                raise DataContractError("Unexpected trainable parameter")
            names[group].append(name)
            params[group].append(parameter)
        flattened = [p for group in params.values() for p in group]
        if len({id(p) for p in flattened}) != len(flattened):
            raise DataContractError("Overlapping optimizer groups")
        result = [
            {
                "params": params["head"],
                "lr": config.head_learning_rate,
                "weight_decay": config.weight_decay,
                "name": "head",
            }
        ]
        if params["layer4"]:
            result.append(
                {
                    "params": params["layer4"],
                    "lr": config.layer4_learning_rate,
                    "weight_decay": config.weight_decay,
                    "name": "layer4",
                }
            )
        return result, names
