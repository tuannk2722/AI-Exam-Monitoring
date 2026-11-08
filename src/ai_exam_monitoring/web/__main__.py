"""Launch the local laptop GPU monitor; --config selects another profile explicitly."""

import argparse
from pathlib import Path

import uvicorn

from ai_exam_monitoring.common.config import load_yaml

from .app import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path,
                        help="Override the laptop GPU profile (CPU: configs/web/review.yaml)")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    config_path = args.config or args.workspace / "configs/web/LAPTOP-VIDEO-20261108/web.yaml"
    config = load_yaml(config_path)
    uvicorn.run(
        create_app(args.workspace, config_path), host="127.0.0.1", port=args.port or config["port"]
    )


if __name__ == "__main__":
    main()
