"""Read-only local compute inventory; never opens media, downloads or loads models."""

from __future__ import annotations

import json
import platform
import subprocess
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from typing import Any


def probe() -> dict[str, Any]:
    packages: dict[str, str | None] = {}
    for name in ("torch", "torchvision", "ultralytics", "opencv-python", "numpy", "Pillow"):
        try:
            packages[name] = version(name)
        except PackageNotFoundError:
            packages[name] = None
    result: dict[str, Any] = {
        "os": platform.system(), "os_release": platform.release(),
        "architecture": platform.machine(), "python": platform.python_version(),
        "processor": platform.processor(), "packages": packages,
        "cuda_available": False, "gpus": [], "errors": [],
    }
    try:
        driver = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,driver_version,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True, timeout=5,
        )
        result["nvidia_driver_inventory"] = driver.stdout.strip().splitlines()
    except (OSError, subprocess.SubprocessError) as exc:
        result["nvidia_driver_inventory"] = []
        result["errors"].append(f"NVIDIA driver inventory unavailable: {type(exc).__name__}")
    try:
        psutil = import_module("psutil")

        result.update(ram_bytes=psutil.virtual_memory().total,
                      cpu_physical_cores=psutil.cpu_count(logical=False),
                      cpu_logical_cores=psutil.cpu_count(logical=True))
    except ImportError:
        result["errors"].append("psutil unavailable; RAM/core inventory omitted")
    try:
        import torch

        result["torch_cuda_build"] = torch.version.cuda
        result["cuda_available"] = torch.cuda.is_available()
        if result["cuda_available"]:
            for index in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(index)
                result["gpus"].append({
                    "device": f"cuda:{index}", "name": props.name,
                    "vram_bytes": props.total_memory,
                    "compute_capability": [props.major, props.minor],
                })
    except (ImportError, RuntimeError, OSError) as exc:
        result["errors"].append(f"Torch inventory failed: {type(exc).__name__}")
    return result


def main() -> None:
    print(json.dumps(probe(), ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
