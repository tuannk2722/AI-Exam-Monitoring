"""Opt-in browser checks against a temporary synthetic-only monitoring server."""

from __future__ import annotations

import json
import os
import socket
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from test_web_monitor import AVAILABLE, monitor_fixture, synthetic_runner


@unittest.skipUnless(AVAILABLE and os.environ.get("RUN_WEB_BROWSER_TESTS") == "1",
                     "Opt-in browser check with web/classifier/Playwright/Chrome")
class MonitorBrowserTests(unittest.TestCase):
    def test_upload_live_controls_refresh_themes_and_legacy(self):
        import uvicorn
        from playwright.sync_api import expect, sync_playwright

        from ai_exam_monitoring.web.app import create_app

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            runtime, payload, receipt, _ = monitor_fixture(root)
            source, rights = root / "synthetic.mp4", root / "synthetic-rights.json"
            source.write_bytes(payload)
            rights.write_text(json.dumps(receipt), encoding="utf-8")
            with (patch("ai_exam_monitoring.web.monitor.load_runtime_config", return_value=runtime),
                  patch("ai_exam_monitoring.web.monitor.RecordedVideo",
                        return_value=SimpleNamespace(count=120, fps=10.)),
                  patch("ai_exam_monitoring.web.monitor.create_online_video",
                        side_effect=synthetic_runner(runtime, count=120, interval=100.)
                        ) as factory):
                app = create_app(root)
                sock = socket.socket()
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
                server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
                thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]})
                thread.start()
                try:
                    deadline = time.monotonic() + 10
                    while not server.started and time.monotonic() < deadline:
                        time.sleep(.02)
                    self.assertTrue(server.started)
                    with sync_playwright() as playwright:
                        browser = playwright.chromium.launch(channel="chrome", headless=True)
                        page = browser.new_page(viewport={"width": 1440, "height": 1050})
                        errors = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        page.goto(f"http://127.0.0.1:{port}")
                        expect(page.get_by_role("region", name="Video giám sát")).to_be_visible()
                        page.locator("#video-file").set_input_files(source)
                        page.locator("#receipt-file").set_input_files(rights)
                        page.locator("#upload").click()
                        expect(page.locator("#session-state")).to_have_text("Video sẵn sàng",
                                                                           timeout=15000)
                        page.locator("#start").click()
                        expect(page.locator("#preview")).to_be_visible(timeout=10000)
                        page.reload()
                        expect(page.locator("#session-state")).to_have_text("Đang phát & phân tích")
                        expect(page.locator("#preview")).to_be_visible()
                        factory.assert_called_once()
                        page.locator("#pause").click()
                        expect(page.locator("#session-state")).to_have_text("Đã tạm dừng")
                        expect(page.locator("#observations")).to_contain_text("Dùng điện thoại")
                        page.wait_for_function("""async () => {
                            const state = await fetch('/api/monitor/state').then(r => r.json());
                            const image = document.getElementById('preview');
                            if (!image.naturalWidth || !state.observations) return false;
                            const canvas = document.createElement('canvas');
                            canvas.width = 640; canvas.height = 360;
                            const context = canvas.getContext('2d');
                            context.drawImage(image, 0, 0, 640, 360);
                            const actual = context.getImageData(5, 5, 1, 1).data[0];
                            const expected = 20 + state.observations.frame_index % 8 * 25;
                            return Math.abs(actual - expected) < 6;
                        }""", timeout=5000)
                        for theme in ("dark", "light"):
                            if page.locator("html").get_attribute("data-theme") != theme:
                                page.locator("#theme").click()
                            expect(page.locator("html")).to_have_attribute("data-theme", theme)
                            preview_dir = os.environ.get("WEB_MONITOR_PREVIEW_DIR")
                            if preview_dir:
                                directory = Path(preview_dir)
                                directory.mkdir(parents=True, exist_ok=True)
                                page.screenshot(path=directory / f"synthetic-{theme}.png",
                                                full_page=True)
                        page.locator("#seek").evaluate("""element => {
                            element.value = '25';
                            element.dispatchEvent(new Event('input', {bubbles:true}));
                            element.dispatchEvent(new Event('change', {bubbles:true}));
                        }""")
                        expect(page.locator("#preview")).to_be_hidden()
                        expect(page.locator("#pause")).to_be_enabled()
                        page.locator("#pause").click()
                        expect(page.locator("#preview")).to_be_visible()
                        page.locator("#stop").click()
                        expect(page.locator("#session-state")).to_have_text("Phiên đã dừng")
                        expect(page.locator("#preview")).to_be_hidden()
                        # Terminal SSE is closed; the browser must still enforce its deadline.
                        identity = app.state.monitor.record["id"]
                        app.state.monitor.record["media_delete_by"] = "2000-01-01T00:00:00+00:00"
                        page.evaluate("snapshot.session.media_delete_by = '2000-01-01T00:00:00Z'")
                        expect(page.locator("#session-state")).to_have_text("Không hoàn tất phiên")
                        expect(page.locator("#notice")).to_contain_text("đã hết hạn")
                        self.assertFalse((app.state.monitor.path(identity) / "source.mp4").exists())
                        page.locator("#delete").click()
                        expect(page.locator("#session-state")).to_have_text("Chưa có nguồn")
                        page.goto(f"http://127.0.0.1:{port}/review")
                        expect(page.locator("#hub")).to_be_visible()
                        self.assertEqual(errors, [])
                        browser.close()
                finally:
                    server.should_exit = True
                    thread.join(10)
                    sock.close()
                    self.assertFalse(thread.is_alive(), "Synthetic server did not stop")
