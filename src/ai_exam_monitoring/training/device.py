"""Explicit V4 execution device and resumable CUDA state; no silent fallback."""

from __future__ import annotations

import os
from typing import Any

import torch

from ai_exam_monitoring.common.errors import DataContractError

from .adaptation_config import AdaptationConfig, RepresentationConfig
from .artifacts import environment


def execution_device(config: AdaptationConfig) -> torch.device:
    if not isinstance(config, RepresentationConfig):
        return torch.device("cpu")
    if config.device == "cuda" and not torch.cuda.is_available():
        raise DataContractError("CUDA explicitly requested but unavailable; no CPU fallback")
    return torch.device(config.device)


def configure_device(config: AdaptationConfig) -> torch.device:
    device = execution_device(config)
    if isinstance(config, RepresentationConfig):
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        if os.environ["CUBLAS_WORKSPACE_CONFIG"] != ":4096:8":
            raise DataContractError("V4 requires CUBLAS_WORKSPACE_CONFIG=:4096:8")
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        if device.type == "cuda":
            torch.cuda.manual_seed_all(config.seed)
    return device


def execution_environment(config: AdaptationConfig) -> dict[str, Any]:
    env = environment()
    if isinstance(config, RepresentationConfig):
        device = execution_device(config)
        env["device"] = str(device)
        env["accelerator"] = {
            "torch_cuda": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),  # type: ignore[no-untyped-call]
            "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
            "capability": list(torch.cuda.get_device_capability(device))
            if device.type == "cuda" else None,
            "precision": config.precision,
            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "cudnn_deterministic": torch.backends.cudnn.deterministic,
            "matmul_tf32": torch.backends.cuda.matmul.allow_tf32,
            "cudnn_tf32": torch.backends.cudnn.allow_tf32,
        }
    return env


def move_batch(
    batch: torch.Tensor | dict[str, torch.Tensor], device: torch.device
) -> torch.Tensor | dict[str, torch.Tensor]:
    if isinstance(batch, torch.Tensor):
        return batch.to(device)
    return {key: tensor.to(device) for key, tensor in batch.items()}


def save_cuda_rng(config: AdaptationConfig) -> list[torch.Tensor] | None:
    if isinstance(config, RepresentationConfig) and config.device == "cuda":
        return torch.cuda.get_rng_state_all()
    return None


def restore_cuda_rng(config: AdaptationConfig, state: Any) -> None:
    if isinstance(config, RepresentationConfig) and config.device == "cuda":
        if not isinstance(state, list) or len(state) != torch.cuda.device_count():
            raise DataContractError("Missing/mismatched CUDA RNG state")
        torch.cuda.set_rng_state_all(state)

