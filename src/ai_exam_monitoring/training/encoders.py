"""Pinned local DINOv2 source loading and explicit frozen-prefix extraction."""

from __future__ import annotations

import importlib
import os
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

import torch
from torch import nn

from ai_exam_monitoring.common.errors import DataContractError

from .adaptation_config import FilePin


def load_dino_source(pin: FilePin, workspace: Path) -> Any:
    archive = pin.verify(workspace)
    cache = workspace / "outputs" / "encoder-source" / pin.sha256
    with zipfile.ZipFile(archive) as zipped:
        roots = {PurePosixPath(i.filename).parts[0] for i in zipped.infolist()}
        if len(roots) != 1:
            raise DataContractError("Encoder source must have one archive root")
        for member in zipped.infolist():
            path = PurePosixPath(member.filename)
            target = (cache / member.filename).resolve()
            if (path.is_absolute() or ".." in path.parts or "\\" in member.filename
                    or ":" in member.filename or not target.is_relative_to(cache.resolve())
                    or (member.external_attr >> 16) & 0o170000 == 0o120000):
                raise DataContractError("Unsafe encoder source archive")
            if member.is_dir():
                continue
            content = zipped.read(member)
            if target.exists():
                if target.read_bytes() != content:
                    raise DataContractError("Cached encoder source changed")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
    source = (cache / next(iter(roots))).resolve()
    loaded = sys.modules.get("dinov2")
    if loaded is not None and not Path(str(loaded.__file__)).resolve().is_relative_to(source):
        raise DataContractError("Different DINO source already imported; use a fresh process")
    # Do not let installed xformers silently change kernels across environments.
    os.environ["XFORMERS_DISABLED"] = "1"
    sys.path.insert(0, str(source))
    try:
        module = importlib.import_module("dinov2.hub.backbones")
        return module.dinov2_vits14(pretrained=False, drop_path_rate=0.0)
    finally:
        sys.path.remove(str(source))


class DinoNetwork(nn.Module):
    def __init__(self, backbone: Any, head: nn.Module):
        super().__init__()
        self.backbone = backbone
        self.fc = head

    def features(self, images: torch.Tensor) -> torch.Tensor:
        net = self.backbone
        # Blocks 0..9 and tokenization are always frozen in the approved policy.
        with torch.no_grad():
            x = net.prepare_tokens_with_masks(images)
            for block in net.blocks[:10]:
                x = block(x)
        if any(p.requires_grad for p in net.blocks[10:].parameters()):
            for block in net.blocks[10:]:
                x = block(x)
            x = net.norm(x)
        else:
            with torch.no_grad():
                for block in net.blocks[10:]:
                    x = block(x)
                x = net.norm(x)
        return torch.cat((x[:, 0], x[:, 1:].mean(dim=1)), dim=1)

