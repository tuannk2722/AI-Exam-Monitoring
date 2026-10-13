"""Quick launcher for Model Inspector Web Application.
Usage:
    python inspect_model.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.inspector.server import run_server  # noqa: E402

if __name__ == "__main__":
    run_server()
