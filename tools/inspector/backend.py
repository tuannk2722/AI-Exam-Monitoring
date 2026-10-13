"""Backend inference engine for Model Inspector.
Loads PyTorch checkpoints, performs exact letterbox preprocessing, and runs evaluation.
Supports both full-model checkpoints (E004+) and head-only checkpoints (E001-E003).
"""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Any

import torch
import torchvision.transforms.functional as TF
from PIL import Image
from torch import nn
from torchvision.models import resnet18


class ModelCache:
    """Caches loaded PyTorch models in memory for fast interactive inference."""

    def __init__(self) -> None:
        self._models: dict[str, nn.Module] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._pretrained_path: Path | None = None

    def _find_pretrained_weights(self) -> Path:
        if self._pretrained_path and self._pretrained_path.exists():
            return self._pretrained_path
        candidates = [
            Path("outputs/pretrained/resnet18-f37072fd.pth"),
            Path.cwd() / "outputs" / "pretrained" / "resnet18-f37072fd.pth",
        ]
        for c in candidates:
            if c.exists():
                self._pretrained_path = c.resolve()
                return self._pretrained_path
        msg = "Pretrained weights not found in outputs/pretrained/resnet18-f37072fd.pth"
        raise FileNotFoundError(msg)

    def get_model(self, checkpoint_path: str | Path) -> tuple[nn.Module, dict[str, Any]]:
        path = Path(checkpoint_path).resolve()
        key = str(path)
        if key in self._models:
            return self._models[key], self._metadata[key]

        if not path.exists():
            raise FileNotFoundError(f"Checkpoint not found at: {path}")

        ckpt = torch.load(path, map_location="cpu", weights_only=False)
        model = resnet18(weights=None)
        model.fc = nn.Linear(512, 2)

        # Case 1: Full-model checkpoint (E004+)
        if isinstance(ckpt, dict) and "model" in ckpt:
            raw_state = ckpt["model"]
            meta = {
                "schema_version": ckpt.get("schema_version", "full-model-v1"),
                "identity": ckpt.get("identity", path.parent.name),
                "experiment": path.parent.name,
                "epoch": ckpt.get("epoch"),
                "val_loss": ckpt.get("val_loss"),
                "model_type": ckpt.get("config", {}).get("model", "resnet18"),
            }
            state_dict = {}
            for k, v in raw_state.items():
                clean_key = k
                if clean_key.startswith("network."):
                    clean_key = clean_key[len("network.") :]
                elif clean_key.startswith("module."):
                    clean_key = clean_key[len("module.") :]
                state_dict[clean_key] = v
            model.load_state_dict(state_dict, strict=True)

        # Case 2: Head-only checkpoint (E001-E003)
        elif isinstance(ckpt, dict) and "head" in ckpt:
            pretrained = self._find_pretrained_weights()
            model.load_state_dict(torch.load(pretrained, map_location="cpu", weights_only=True))
            model.fc = nn.Linear(512, 2)
            model.fc.load_state_dict(ckpt["head"])
            meta = {
                "schema_version": ckpt.get("schema_version", "head-only-v1"),
                "identity": ckpt.get("identity", path.parent.name),
                "experiment": path.parent.name,
                "epoch": ckpt.get("epoch"),
                "val_loss": ckpt.get("val_loss"),
                "model_type": "resnet18_frozen_linear_head",
            }

        # Case 3: Raw state_dict
        elif isinstance(ckpt, dict) and any(
            k.startswith("conv1") or k.startswith("network.") for k in ckpt.keys()
        ):
            state_dict = {
                k.replace("network.", "").replace("module.", ""): v
                for k, v in ckpt.items()
            }
            model.load_state_dict(state_dict, strict=True)
            meta = {"identity": path.stem, "model_type": "resnet18"}
        else:
            raise ValueError(f"Unsupported checkpoint payload in {path}")

        model.eval()

        meta["path"] = str(path)
        if path.is_relative_to(Path.cwd()):
            meta["relpath"] = str(path.relative_to(Path.cwd())).replace("\\", "/")
        else:
            meta["relpath"] = str(path)
        meta["size_mb"] = round(path.stat().st_size / (1024 * 1024), 2)

        self._models[key] = model
        self._metadata[key] = meta
        return model, meta


# Global cache instance
cache = ModelCache()


def scan_checkpoints(root: Path | None = None) -> list[dict[str, Any]]:
    """Discovers all valid .pt checkpoints in outputs/ and artifacts/ directories.
    Filters out feature caches (features-*.pt) and temporary files.
    """
    base = root or Path.cwd()
    search_dirs = [base / "outputs", base / "artifacts"]
    found: list[dict[str, Any]] = []

    for sdir in search_dirs:
        if not sdir.exists():
            continue
        for p in sdir.rglob("*.pt"):
            # Only include model checkpoints (best.pt or last.pt)
            if not (p.name == "best.pt" or p.name == "last.pt"):
                continue

            rel = str(p.relative_to(base)).replace("\\", "/")
            name_label = f"{p.parent.name} ({p.name})"
            found.append({
                "label": name_label,
                "path": str(p),
                "relpath": rel,
                "is_best": p.name == "best.pt",
                "experiment": p.parent.name,
                "filename": p.name,
                "size_mb": round(p.stat().st_size / (1024 * 1024), 2),
            })

    # Sort: best.pt first, newest experiment first
    found.sort(key=lambda x: (not x["is_best"], x["experiment"], x["filename"]))
    return found


def letterbox_image(
    image: Image.Image,
    target_size: int = 224,
    fill: tuple[int, int, int] = (124, 116, 104),
) -> tuple[Image.Image, torch.Tensor]:
    """Exact RGB letterbox matching project data contract."""
    image = image.convert("RGB")
    scale = target_size / max(image.size)
    width, height = (max(1, min(target_size, round(v * scale))) for v in image.size)
    resized = image.resize((width, height), Image.Resampling.BILINEAR)

    canvas = Image.new("RGB", (target_size, target_size), fill)
    offset = ((target_size - width) // 2, (target_size - height) // 2)
    canvas.paste(resized, offset)

    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    tensor = TF.normalize(TF.to_tensor(canvas), mean, std).unsqueeze(0)
    return canvas, tensor


def image_to_base64(img: Image.Image, fmt: str = "JPEG") -> str:
    buffered = io.BytesIO()
    img.save(buffered, format=fmt, quality=90)
    encoded = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/{fmt.lower()};base64,{encoded}"


def base64_to_image(b64_string: str) -> Image.Image:
    if "," in b64_string:
        b64_string = b64_string.split(",", 1)[1]
    img_data = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(img_data)).convert("RGB")


def analyze_crop(
    image: Image.Image,
    model_path: str | Path,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Runs single model inference and returns formatted results."""
    model, meta = cache.get_model(model_path)
    canvas, tensor = letterbox_image(image)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.sigmoid(logits).squeeze(0).tolist()

    phone_score = float(probs[0])
    looking_score = float(probs[1])

    return {
        "metadata": meta,
        "phone_use": {
            "score": phone_score,
            "percentage": round(phone_score * 100, 1),
            "decision": phone_score >= threshold,
            "label": "PHÁT HIỆN GIAN LẬN" if phone_score >= threshold else "BÌNH THƯỜNG",
        },
        "looking_around": {
            "score": looking_score,
            "percentage": round(looking_score * 100, 1),
            "decision": looking_score >= threshold,
            "label": "PHÁT HIỆN NHÌN QUANH" if looking_score >= threshold else "BÌNH THƯỜNG",
        },
        "threshold": threshold,
    }

