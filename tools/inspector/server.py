"""HTTP Server for Model Inspector Web Application.
Zero external dependencies; uses Python standard library threading HTTP server.
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Add project root to sys.path so it works from anywhere
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.inspector.backend import (  # noqa: E402
    analyze_crop,
    base64_to_image,
    image_to_base64,
    letterbox_image,
    scan_checkpoints,
)

WEB_DIR = Path(__file__).resolve().parent / "web"


class InspectorHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        # Keep console output clean
        pass

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            index_path = WEB_DIR / "index.html"
            if not index_path.exists():
                self.send_error(404, "index.html not found")
                return
            content = index_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        if self.path == "/api/models":
            models = scan_checkpoints(ROOT_DIR)
            payload = json.dumps(models).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Fallback 404
        self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        if self.path == "/api/predict":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode("utf-8"))
                img_b64 = data.get("image_base64")
                model_a_path = data.get("model_a")
                model_b_path = data.get("model_b")
                threshold = float(data.get("threshold", 0.5))

                if not img_b64 or not model_a_path:
                    self.send_error(400, "Missing image_base64 or model_a")
                    return

                pil_img = base64_to_image(img_b64)
                letterbox_canvas, _ = letterbox_image(pil_img)
                letterbox_b64 = image_to_base64(letterbox_canvas)

                res_a = analyze_crop(pil_img, model_a_path, threshold)
                res_b = (
                    analyze_crop(pil_img, model_b_path, threshold)
                    if model_b_path
                    else None
                )

                response_dict = {
                    "letterbox_base64": letterbox_b64,
                    "model_a": res_a,
                    "model_b": res_b,
                }
                out = json.dumps(response_dict).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)
            except Exception as e:
                err_bytes = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err_bytes)))
                self.end_headers()
                self.wfile.write(err_bytes)
            return

        self.send_error(404, "Not Found")


def run_server(host: str = "127.0.0.1", port: int = 8501, open_browser: bool = True) -> None:
    # Try preferred port, or fall back to open port if busy
    server = None
    for p in range(port, port + 20):
        try:
            server = ThreadingHTTPServer((host, p), InspectorHandler)
            port = p
            break
        except OSError:
            continue

    if server is None:
        msg = f"Could not bind server to {host} in port range {port}-{port+20}"
        raise RuntimeError(msg)

    url = f"http://{host}:{port}"
    print("=" * 60)
    print("  👁️  MODEL INSPECTOR & COMPARISON STUDIO")
    print("=" * 60)
    print(f"  URL: {url}")
    print("  Nhấn Ctrl+C trong terminal để dừng server.")
    print("=" * 60)

    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐang dừng server Model Inspector...")
    finally:
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Model Inspector Web UI")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8501, help="Port (default: 8501)")
    parser.add_argument(
        "--no-browser", action="store_true", help="Do not automatically open browser"
    )
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, open_browser=not args.no_browser)

