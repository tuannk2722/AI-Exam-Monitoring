"""Explicit FP32 execution primitives; not a runtime approval or device auto-selector.

Legacy callers keep their CPU receipt. A future execution profile must pin its
own exact package versions before using these internal adapters on another build.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.metadata import version

import torch

from ai_exam_monitoring.common.errors import DataContractError


@dataclass(frozen=True)
class ExecutionSettings:
    device: str
    batch_size: int

    def __post_init__(self) -> None:
        if (not isinstance(self.device, str)
                or re.fullmatch(r"cpu|cuda:(0|[1-9][0-9]*)", self.device) is None):
            raise DataContractError("Require cpu or explicit cuda:N; no automatic device")
        if type(self.batch_size) is not int or not 1 <= self.batch_size <= 100:
            raise DataContractError("Batch size must be 1..100 (runtime max_det bound)")

    def resolve(self) -> torch.device:
        device = torch.device(self.device)
        if device.type == "cuda" and (
            not torch.cuda.is_available() or device.index is None
            or device.index >= torch.cuda.device_count()
        ):
            raise DataContractError("Requested CUDA device unavailable; no CPU fallback")
        return device

    def synchronize(self) -> None:
        if self.device.startswith("cuda:"):
            torch.cuda.synchronize(self.resolve())

    @contextmanager
    def precision(self) -> Iterator[None]:
        """One model owner only; restore process-global flags even on OOM/error.

        Disable autocast/TF32 for the new execution path. This does not promise
        bitwise equivalence between GPU and CPU kernels; parity still needs data.
        """
        device = self.resolve()
        if device.type == "cpu":
            with torch.autocast(device_type="cpu", enabled=False):
                yield
            return
        matmul = torch.backends.cuda.matmul.allow_tf32
        cudnn = torch.backends.cudnn.allow_tf32
        benchmark = torch.backends.cudnn.benchmark
        try:
            torch.backends.cuda.matmul.allow_tf32 = False
            torch.backends.cudnn.allow_tf32 = False
            torch.backends.cudnn.benchmark = False
            with torch.autocast(device_type="cuda", enabled=False):
                yield
        finally:
            torch.backends.cuda.matmul.allow_tf32 = matmul
            torch.backends.cudnn.allow_tf32 = cudnn
            torch.backends.cudnn.benchmark = benchmark


def verify_execution_packages(parent: Mapping[str, str], expected: Mapping[str, str],
                              settings: ExecutionSettings) -> None:
    """Only Torch wheel variants may differ from the CPU acquisition receipt.

    No wildcard, ignored package or implicit CPU/CUDA substitution. Expected
    versions are supplied by the new execution profile, never written to parent.
    """
    if set(expected) != set(parent) or not {"torch", "torchvision"} <= set(expected):
        raise DataContractError("Execution package manifest must cover the parent receipt")
    for name, original in parent.items():
        target = expected[name]
        if not isinstance(target, str) or not target:
            raise DataContractError("Require exact execution package versions")
        if name in {"torch", "torchvision"}:
            if target.split("+", 1)[0] != original.split("+", 1)[0]:
                raise DataContractError("Execution adapter cannot upgrade Torch/torchvision")
        elif target != original:
            raise DataContractError(f"Execution adapter cannot change package: {name}")
        if version(name) != target:
            raise DataContractError(f"Execution package changed: {name}")
    settings.resolve()
