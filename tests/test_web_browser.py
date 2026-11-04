"""Opt-in browser integration with a temporary synthetic-only local server."""

from __future__ import annotations

import os
import tempfile
import threading
import time
import unittest
from pathlib import Path

from test_web_review import AVAILABLE, fixture


@unittest.skipUnless(
    AVAILABLE and os.environ.get("RUN_WEB_BROWSER_TESTS") == "1",
    "Opt-in: RUN_WEB_BROWSER_TESTS=1 and playwright/Chrome",
)
class WebBrowserTests(unittest.TestCase):
    def test_workbench_themes_review_export_and_reload(self):
        import uvicorn
        from playwright.sync_api import expect, sync_playwright

        from ai_exam_monitoring.web.app import create_app

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture(root)
            app = create_app(root)
            server = uvicorn.Server(
                uvicorn.Config(app, host="127.0.0.1", port=8766, log_level="error")
            )
            thread = threading.Thread(target=server.run, daemon=True)
            thread.start()
            deadline = time.monotonic() + 20
            while not server.started and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue(server.started)
            try:
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(channel="chrome", headless=True)
                    page = browser.new_page(viewport={"width": 1920, "height": 1080})
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto("http://127.0.0.1:8766")
                    page.locator("[data-open]").click()
                    expect(page.locator("#event-title")).to_contain_text("T1")
                    expect(page.locator("#input-state")).to_have_text("")
                    expect(page.locator("#media-state")).to_be_hidden()
                    page.locator("#next").click()
                    expect(page.locator("#frame-info")).to_contain_text("00000030")
                    page.locator("#first").click()
                    expect(page.locator("#frame-info")).to_contain_text("00000000")
                    page.keyboard.press("3")
                    expect(page.locator("#decision-status")).to_have_text("Chưa rõ")
                    page.locator("#note").fill("Synthetic browser check")
                    page.locator("#flag").check()
                    expect(page.locator("#save-status")).to_contain_text("Đã lưu")
                    with page.expect_download() as pending:
                        page.locator("#export").click()
                    exported = pending.value
                    self.assertEqual(exported.suggested_filename, "event-review.json")
                    exported.save_as(root / "review.json")
                    page.locator("#reset").click()
                    expect(page.locator("#save-status")).to_contain_text("Đã lưu")
                    page.locator("#import-file").set_input_files(root / "review.json")
                    page.locator("#confirm-import").click()
                    expect(page.locator("#decision-status")).to_have_text("Chưa rõ")
                    for theme in ("dark", "light"):
                        if page.locator("html").get_attribute("data-theme") != theme:
                            page.locator("#theme").click()
                        expect(page.locator("html")).to_have_attribute("data-theme", theme)
                        self.assertLessEqual(
                            page.evaluate("document.documentElement.scrollWidth"), 1920
                        )
                        self.assertLessEqual(
                            page.evaluate("document.documentElement.scrollHeight"), 1080
                        )
                        screenshot_dir = os.environ.get("WEB_SCREENSHOTS")
                        if screenshot_dir:
                            page.locator(".inspector").evaluate("el => el.scrollTop = 0")
                            destination = Path(screenshot_dir)
                            destination.mkdir(parents=True, exist_ok=True)
                            page.screenshot(path=str(destination / f"synthetic-{theme}.png"))
                    page.locator('[data-view="summary"]').click()
                    expect(page.locator("#accounting-pass")).to_contain_text("khớp")
                    expect(page.locator("#flagged-list")).to_contain_text("Synthetic browser check")
                    page.reload()
                    page.locator("[data-open]").click()
                    expect(page.locator("#note")).to_have_value("Synthetic browser check")
                    page.locator('[data-tab="short"]').click()
                    expect(page.locator("#queue-list")).to_contain_text("Không có")
                    page.locator('[data-tab="events"]').click()
                    page.locator("#search").fill("does-not-exist")
                    expect(page.locator("#queue-list")).to_contain_text("Không có")
                    page.set_viewport_size({"width": 390, "height": 844})
                    self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
                    self.assertEqual(errors, [])
                    browser.close()
            finally:
                server.should_exit = True
                thread.join(timeout=10)
                app.state.jobs.executor.shutdown(wait=True)
