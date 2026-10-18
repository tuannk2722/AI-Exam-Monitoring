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

from .adaptation_config import (
    AdaptationConfig,
    E005AdaptationConfig,
    FilePin,
    ResearchAdaptationConfig,
)
from .artifacts import save_checkpoint


def tensor_digest(state: Mapping[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        value = tensor.detach().cpu().contiguous()
        digest.update(f"{name}:{value.dtype}:{tuple(value.shape)}\n".encode())
        digest.update(value.numpy().tobytes())
    return digest.hexdigest()


def head_input_dim(config: AdaptationConfig) -> int:
    if isinstance(config, E005AdaptationConfig) and config.model == "resnet18_anchor_context":
        return 1542 if config.use_geometry_features else 1536
    return 512


def build_e005_head(in_dim: int, hidden_dim: int, dropout: float) -> nn.Module:
    if hidden_dim <= 0:
        return nn.Linear(in_dim, 2)
    return nn.Sequential(
        nn.LayerNorm(in_dim),
        nn.Dropout(p=dropout),
        nn.Linear(in_dim, hidden_dim),
        nn.GELU(),
        nn.Dropout(p=dropout),
        nn.Linear(hidden_dim, 2),
    )


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


def create_e005_initial_head(
    path: Path,
    seed: int,
    *,
    in_dim: int = 512,
    hidden_dim: int = 0,
    dropout: float = 0.0,
) -> str:
    if path.exists():
        raise DataContractError("Head initialization must have a new immutable path")
    if in_dim == 512 and hidden_dim == 0:
        return create_initial_head(path, seed)
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(seed)
        head = build_e005_head(in_dim, hidden_dim, dropout)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_checkpoint(
        path,
        {
            "schema_version": "e005-head-init-v3",
            "seed": seed,
            "in_dim": in_dim,
            "hidden_dim": hidden_dim,
            "dropout": dropout,
            "head": head.state_dict(),
            "tensor_sha256": tensor_digest(head.state_dict()),
        },
    )
    return sha256_file(path)


def validate_head(state: Any) -> None:
    if (not isinstance(state, dict) or set(state) != {"weight", "bias"}
            or any(not isinstance(v, torch.Tensor) for v in state.values())
            or state["weight"].shape != (2, 512) or state["bias"].shape != (2,)
            or any(v.dtype != torch.float32 or not torch.isfinite(v).all()
                   for v in state.values())):
        raise DataContractError("Head must contain finite float32 weight[2,512] and bias[2]")


def validate_e005_head_state(state: Any, expected_module: nn.Module) -> None:
    expected = expected_module.state_dict()
    if (
        not isinstance(state, dict)
        or set(state) != set(expected)
        or any(
            not isinstance(state[k], torch.Tensor)
            or state[k].shape != expected[k].shape
            or state[k].dtype != torch.float32
            or not torch.isfinite(state[k]).all()
            for k in expected
        )
    ):
        raise DataContractError("Invalid E005 head state dictionary")


def create_learned_head(
    path: Path, parent: FilePin, workspace: Path, parent_epoch: int
) -> str:
    """Extract only the approved parent FC, never optimizer or adapted backbone."""
    if path.exists():
        raise DataContractError("Learned head requires a new immutable path")
    payload = torch.load(parent.verify(workspace), map_location="cpu", weights_only=True)
    if (payload.get("schema_version") != "full-model-bundle-v1"
            or payload.get("epoch") != parent_epoch
            or payload.get("config", {}).get("model") != "resnet18_matched_control"
            or payload.get("config", {}).get("target_order") != ["phone_use", "looking_around"]
            or tensor_digest(payload["model"]) != payload.get("model_tensor_sha256")):
        raise DataContractError("Learned head parent bundle/epoch/targets mismatch")
    head = {name: payload["model"]["network.fc." + name].detach().clone()
            for name in ("weight", "bias")}
    validate_head(head)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_checkpoint(path, {
        "schema_version": "learned-head-init-v1",
        "parent_checkpoint": {"path": parent.path, "sha256": parent.sha256},
        "parent_epoch": parent_epoch,
        "head": head,
        "tensor_sha256": tensor_digest(head),
    })
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
        self._config = config
        self.policy = config.model
        self.network = resnet18(weights=None)
        is_v3 = isinstance(config, E005AdaptationConfig)
        in_dim = head_input_dim(config)
        hidden_dim = config.head_hidden_dim if isinstance(config, E005AdaptationConfig) else 0
        dropout = config.head_dropout if isinstance(config, E005AdaptationConfig) else 0.0
        if full_state is None:
            if (
                weights is None
                or initial_head is None
                or sha256_file(weights) != config.weights.sha256
                or sha256_file(initial_head) != config.head_initialization.sha256
            ):
                raise DataContractError("Missing or changed pretrained/head initialization")
            self.network.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True))
            self.network.fc = cast(Any, build_e005_head(in_dim, hidden_dim, dropout))
            payload = torch.load(initial_head, map_location="cpu", weights_only=True)
            if is_v3 and (in_dim != 512 or hidden_dim > 0):
                validate_e005_head_state(payload.get("head"), self.network.fc)
                if (
                    payload.get("schema_version") != "e005-head-init-v3"
                    or payload.get("seed") != config.seed
                    or payload.get("in_dim") != in_dim
                    or payload.get("hidden_dim") != hidden_dim
                ):
                    raise DataContractError("E005 head initialization identity mismatch")
            else:
                validate_head(payload.get("head"))
                if (isinstance(config, ResearchAdaptationConfig)
                        and config.head_provenance.kind == "parent_fc"):
                    parent = config.head_provenance.parent_checkpoint
                    if parent is None or (
                        payload.get("schema_version") != "learned-head-init-v1"
                        or payload.get("parent_checkpoint") != {
                            "path": parent.path, "sha256": parent.sha256
                        }
                        or payload.get("parent_epoch") != config.head_provenance.parent_epoch
                    ):
                        raise DataContractError("Learned head provenance mismatch")
                elif (payload.get("schema_version") != "linear-head-init-v1"
                      or payload.get("seed") != config.seed):
                    raise DataContractError("Random head initialization identity mismatch")
            if tensor_digest(payload["head"]) != payload.get("tensor_sha256"):
                raise DataContractError("Head initialization identity mismatch")
            self.network.fc.load_state_dict(payload["head"])
        else:
            if weights is not None or initial_head is not None:
                raise DataContractError("Standalone reload cannot also load external weights")
            self.network.fc = cast(Any, build_e005_head(in_dim, hidden_dim, dropout))
            self.load_state_dict(full_state, strict=True)
        self.configure_trainable_stage(config, epoch=config.max_epochs)
        self.train()

    def configure_trainable_stage(self, config: AdaptationConfig, *, epoch: int = 1) -> str:
        self.requires_grad_(False)
        self.network.fc.requires_grad_(True)
        if not isinstance(config, E005AdaptationConfig):
            if self.policy == "resnet18_layer4":
                self.network.layer4.requires_grad_(True)
            return "legacy"
        if config.trainable_scope == "head_only":
            return "head_only"
        if epoch <= config.warmup_epochs:
            return "warmup_head_only"
        if config.trainable_scope == "head_and_layer4_block1":
            self.network.layer4[1].requires_grad_(True)
            return "finetune_layer4_block1"
        if config.trainable_scope == "head_and_layer4":
            self.network.layer4.requires_grad_(True)
            return "finetune_layer4"
        raise DataContractError("Unsupported trainable_scope")

    def train(self, mode: bool = True) -> AdaptationModel:
        super().train(mode)
        for module in self.modules():
            if isinstance(module, nn.modules.batchnorm._BatchNorm):
                module.eval()
        return self

    def _extract_backbone_features(self, images: torch.Tensor) -> torch.Tensor:
        net = self.network
        if images.requires_grad:
            x = net.conv1(images)
            x = net.bn1(x)
            x = net.relu(x)
            x = net.maxpool(x)
            x = net.layer1(x)
            x = net.layer2(x)
            x = net.layer3(x)
        else:
            with torch.no_grad():
                x = net.conv1(images)
                x = net.bn1(x)
                x = net.relu(x)
                x = net.maxpool(x)
                x = net.layer1(x)
                x = net.layer2(x)
                x = net.layer3(x)
        b0_grad = any(p.requires_grad for p in net.layer4[0].parameters()) or x.requires_grad
        if b0_grad:
            x = net.layer4[0](x)
        else:
            with torch.no_grad():
                x = net.layer4[0](x)
        b1_grad = any(p.requires_grad for p in net.layer4[1].parameters()) or x.requires_grad
        if b1_grad:
            x = net.layer4[1](x)
        else:
            with torch.no_grad():
                x = net.layer4[1](x)
        x = net.avgpool(x)
        return torch.flatten(x, 1)

    def forward(
        self, inputs: torch.Tensor | Mapping[str, torch.Tensor]
    ) -> torch.Tensor:
        if not isinstance(self._config, E005AdaptationConfig):
            if not isinstance(inputs, torch.Tensor):
                raise DataContractError("Legacy model expects single image tensor")
            return cast(torch.Tensor, self.network(inputs))
        if self.policy == "resnet18_anchor_context":
            if isinstance(inputs, torch.Tensor):
                anchor = inputs
                context = inputs
                geom = torch.tensor(
                    [0.0, 0.0, 1.0, 1.0, 1.0, 1.0],
                    dtype=inputs.dtype,
                    device=inputs.device,
                ).unsqueeze(0).expand(len(inputs), 6)
            else:
                anchor = inputs["anchor"]
                context = inputs["context"]
                geom = inputs["geometry"]
            both = torch.cat([anchor, context], dim=0)
            feats = self._extract_backbone_features(both)
            fa, fc = feats.chunk(2, dim=0)
            parts = [fa, fc, fa - fc]
            if self._config.use_geometry_features:
                parts.append(geom.to(device=fa.device, dtype=fa.dtype))
            fused = torch.cat(parts, dim=1)
            return cast(torch.Tensor, self.network.fc(fused))
        if not isinstance(inputs, torch.Tensor):
            raise DataContractError("Single-crop model expects tensor input")
        feats = self._extract_backbone_features(inputs)
        return cast(torch.Tensor, self.network.fc(feats))

    def parameter_groups(
        self, config: AdaptationConfig
    ) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
        names: dict[str, list[str]] = {"head": [], "layer4": []}
        params: dict[str, list[nn.Parameter]] = {"head": [], "layer4": []}
        if isinstance(config, E005AdaptationConfig):
            for name, parameter in self.named_parameters():
                if name.startswith("network.fc."):
                    names["head"].append(name)
                    params["head"].append(parameter)
                elif (
                    config.trainable_scope == "head_and_layer4_block1"
                    and name.startswith("network.layer4.1.")
                ) or (
                    config.trainable_scope == "head_and_layer4"
                    and name.startswith("network.layer4.")
                ):
                    names["layer4"].append(name)
                    params["layer4"].append(parameter)
        else:
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

