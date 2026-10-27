"""Launch the owner-only local review server."""

import argparse
from pathlib import Path

import uvicorn

from ai_exam_monitoring.common.config import load_yaml

from .app import create_app

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--workspace", type=Path, default=Path("."))
parser.add_argument("--config", type=Path)
parser.add_argument("--port", type=int)
args = parser.parse_args()
config_path = args.config or args.workspace / "configs/web/review.yaml"
config = load_yaml(config_path)
uvicorn.run(
    create_app(args.workspace, config_path), host="127.0.0.1", port=args.port or config["port"]
)
