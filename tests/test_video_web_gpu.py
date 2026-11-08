"""GPU video-upload boundary checks using synthetic transport/models only."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from contextlib import ExitStack
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

AVAILABLE = all(importlib.util.find_spec(p) for p in ("fastapi", "httpx", "torch", "torchvision"))
if AVAILABLE:
    import yaml
    from fastapi.testclient import TestClient
    from PIL import Image
    from test_web_monitor import SyntheticClassifier, SyntheticDetector, monitor_models_fixture

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.execution_processor import load_execution_selection
    from ai_exam_monitoring.inference.frame_processor import FrameProcessor
    from ai_exam_monitoring.inference.video import VideoFrame
    from ai_exam_monitoring.training.artifacts import code_identity, write_json
    from ai_exam_monitoring.web.app import create_app


@unittest.skipUnless(AVAILABLE, "Install web/classifier dependencies")
class VideoWebGpuTests(unittest.TestCase):
    def setUp(self):
        self.temp = self.enterContext(tempfile.TemporaryDirectory())
        self.root = Path(self.temp)
        models, self.payload, self.rights, config_path = monitor_models_fixture(self.root)
        self.runtime = models["B0"]
        self.selection = self.root / "execution.json"
        def pin(path):
            return dict(path=path.relative_to(self.root).as_posix(), sha256=sha256_file(path))
        decision = self.root / "decision.md"
        decision.write_text("Synthetic test authorization")
        parity = self.root / "parity.json"
        write_json(parity, dict(status="completed", runtime_sha256=self.runtime.sha256,
                                source_sha256="synthetic"))
        profile = self.root / "profile.json"
        write_json(profile, dict(status="completed", runtime_sha256=self.runtime.sha256,
                                 source_sha256="synthetic", device="cuda:0", batch_size=1,
                                 precision="float32"))
        code = self.root / "code.json"
        write_json(code, code_identity())
        self.raw = dict(schema_version="video-web-execution-v1", status="approved",
                        scope="local_video_web", runtime_sha256=self.runtime.sha256,
                        device="cuda:0", batch_size=1, precision="float32", packages={},
                        decision_ref=pin(decision), parity=pin(parity), profile=pin(profile),
                        profile_code=pin(code))
        write_json(self.selection, self.raw)
        config = yaml.safe_load(config_path.read_text())
        config.update(schema_version="online-video-web-gpu-config-v1",
                      models={"B0": config["models"]["B0"]}, execution=pin(self.selection))
        config_path.write_text(yaml.safe_dump(config))
        stack = self.enterContext(ExitStack())
        for module in ("web.monitor", "inference.online_video"):
            stack.enter_context(patch(f"ai_exam_monitoring.{module}.load_runtime_config",
                                      return_value=self.runtime))
        self.opens = 0
        owner = self
        class Source:
            count, fps = 100, 30.
            def frames(self):
                owner.opens += 1
                for i in range(self.count):
                    yield VideoFrame(i, i * 1000 / self.fps, Image.new("RGB", (640, 360)))
        for module in ("web.monitor", "inference.online_video"):
            stack.enter_context(patch(f"ai_exam_monitoring.{module}.RecordedVideo",
                                      return_value=Source()))
        self.processor = stack.enter_context(patch(
            "ai_exam_monitoring.inference.execution_processor.create_execution_processor",
            return_value=FrameProcessor(SyntheticDetector(), SyntheticClassifier(),
                                        self.runtime.raw["crop"])))
        app = create_app(self.root)
        self.monitor = app.state.monitor
        self.client = self.enterContext(TestClient(app))

    def ready(self):
        response = self.client.post("/api/monitor/uploads", json=dict(
            receipt=self.rights, size=len(self.payload), model_id="B0"))
        self.assertEqual(response.status_code, 201, response.text)
        identity = response.json()["session"]["id"]
        response = self.client.put(f"/api/monitor/uploads/{identity}", content=self.payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["session"]["execution"]["device"], "cuda:0")
        return identity

    def wait(self, predicate):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if predicate():
                return
            threading.Event().wait(.005)
        self.fail("Synthetic GPU transport did not reach expected state")

    def command(self, identity, action, **extra):
        if action == "start":
            return self.client.post(f"/api/monitor/sessions/{identity}/start")
        state = self.monitor.state()["session"]
        return self.client.post(f"/api/monitor/sessions/{identity}/command", json=dict(
            action=action, command_id=state["command_id"]+1, epoch=state["epoch"], **extra))

    def test_upload_gpu_factory_and_playback_controls(self):
        identity = self.ready()
        self.assertEqual(self.command(identity, "start").status_code, 200)
        self.wait(lambda: self.monitor.state()["session"]["processed"] >= 1)
        settings = self.processor.call_args.args[1]
        self.assertEqual((settings.device, settings.batch_size), ("cuda:0", 1))
        self.assertEqual(self.command(identity, "pause").status_code, 200)
        self.assertEqual(self.command(identity, "seek", frame_index=2).status_code, 200)
        self.assertEqual(self.command(identity, "resume").status_code, 200)
        self.assertEqual(self.command(identity, "stop").status_code, 200)
        self.wait(lambda: self.monitor.state()["session"]["status"] == "stopped")
        self.assertEqual(self.processor.call_count, 1)
        self.assertIn("execution-profile.json", self.monitor.record["input_pins"])

    def test_gpu_failure_never_falls_back_to_cpu_or_opens_decoder(self):
        self.processor.side_effect = DataContractError("CUDA unavailable")
        identity = self.ready()
        self.command(identity, "start")
        self.wait(lambda: self.monitor.state()["session"]["status"] == "failed")
        self.assertEqual(self.monitor.state()["session"]["processed"], 0)
        self.assertEqual(self.opens, 0)
        self.assertEqual(self.processor.call_count, 1)

    def test_selection_change_between_upload_and_start_is_rejected(self):
        identity = self.ready()
        value = copy.deepcopy(self.raw)
        value["batch_size"] = 4
        write_json(self.selection, value)
        self.assertEqual(self.command(identity, "start").status_code, 400)
        self.processor.assert_not_called()

    def test_unmeasured_batch_and_mismatched_runtime_are_rejected(self):
        for key, value in (("batch_size", 2), ("runtime_sha256", "different")):
            with self.subTest(key=key):
                raw = dict(self.raw, **{key: value})
                write_json(self.selection, raw)
                with self.assertRaises(DataContractError):
                    load_execution_selection(self.selection, self.root, self.runtime)

    def test_changed_numerical_training_source_is_rejected(self):
        original = Path.read_text
        def changed(path, *args, **kwargs):
            value = original(path, *args, **kwargs)
            if path.as_posix().endswith("ai_exam_monitoring/training/data.py"):
                return value + "\n# Synthetic numerical source change\n"
            return value
        with patch.object(Path, "read_text", changed):
            with self.assertRaisesRegex(DataContractError, "training/data.py"):
                load_execution_selection(self.selection, self.root, self.runtime)

    def test_receipt_keeps_source_deadline_and_never_overwrites_an_approval(self):
        from ai_exam_monitoring.web.bundle import receipt
        source = self.root / "scene.mp4"
        source.write_bytes(self.payload)
        with patch("ai_exam_monitoring.web.bundle.selected", return_value=(self.runtime, {}, None)):
            path = receipt(self.root, source, self.rights["media_delete_by"], confirmed=True)
            original = path.read_bytes()
            self.assertEqual(receipt(self.root, source, self.rights["media_delete_by"],
                                     confirmed=True), path)
            with self.assertRaises(ConfigurationError):
                receipt(self.root, source, "2026-01-01T00:00:00+00:00", confirmed=True)
            changed_deadline = (datetime.fromisoformat(self.rights["media_delete_by"])
                                + timedelta(hours=1)).isoformat()
            with self.assertRaises(DataContractError):
                receipt(self.root, source, changed_deadline, confirmed=True)
            with self.assertRaises(DataContractError):
                receipt(self.root, source, self.rights["media_delete_by"], confirmed=False)
            self.assertEqual(path.read_bytes(), original)

    @unittest.skipUnless(shutil.which("powershell") or shutil.which("pwsh"),
                         "PowerShell integration on deployment platform")
    def test_launcher_restores_shell_and_limits_dependency_install(self):
        launcher_text = (Path(__file__).resolve().parents[1] / "RUN.ps1").read_text("utf-8")
        shell = shutil.which("powershell") or shutil.which("pwsh")
        def quote(path):
            return "'" + str(path).replace("'", "''") + "'"
        for fail in (False, True):
            with self.subTest(preflight_failure=fail):
                root = self.root / ("failed" if fail else "success")
                package = root / "src/ai_exam_monitoring/web"
                package.mkdir(parents=True)
                (package.parent / "__init__.py").write_text("")
                (package / "__init__.py").write_text("")
                (package / "bundle.py").write_text(
                    "import json,os,sys\nfrom pathlib import Path\n"
                    "with Path('bundle-calls.jsonl').open('a') as stream: "
                    "stream.write(json.dumps(sys.argv[1:])+'\\n')\n"
                    "if os.environ['SYNTHETIC_FAIL']=='1': sys.exit(9)\n"
                    "if sys.argv[1]=='deps': sys.exit(2)\n")
                (package / "__main__.py").write_text(
                    "from pathlib import Path\nPath('server-started').write_text('synthetic')\n")
                (root / "src/pip.py").write_text(
                    "import json,sys\nfrom pathlib import Path\n"
                    "Path('pip-args.json').write_text(json.dumps(sys.argv[1:]))\n")
                launcher = root / "RUN.ps1"
                launcher.write_text(launcher_text, encoding="utf-8")
                source = root / "scene.mp4"
                source.write_bytes(self.payload)
                artifacts = root / "input models.zip"
                artifacts.write_bytes(b"synthetic transfer")
                wrapper = root / "calling-shell.ps1"
                wrapper.write_text(
                    "$ErrorActionPreference='Stop'\n"
                    f"Set-Location -LiteralPath {quote(root)}\n"
                    "$env:PYTHONPATH='original-path'\n"
                    "$env:PYTHONDONTWRITEBYTECODE='0'\n"
                    f"$env:SYNTHETIC_FAIL='{int(fail)}'\n"
                    "$failed=$false\ntry {\n"
                    f"& {quote(launcher)} -Python {quote(sys.executable)} "
                    f"-Source {quote(source)} -Artifacts {quote(artifacts)} -DeleteBy 'synthetic' "
                    "-ConfirmSourceRights -NotTestOrHoldout\n"
                    "} catch { $failed=$true }\n"
                    "[PSCustomObject]@{failed=$failed; cwd=(Get-Location).Path; "
                    "pythonpath=$env:PYTHONPATH; bytecode=$env:PYTHONDONTWRITEBYTECODE} "
                    "| ConvertTo-Json -Compress\n", encoding="utf-8")
                result = subprocess.run([shell, "-NoProfile", "-NonInteractive", "-File",
                                         str(wrapper)], capture_output=True, text=True,
                                        timeout=30, check=True)
                state = json.loads(result.stdout.strip().splitlines()[-1])
                self.assertEqual(state, dict(failed=fail, cwd=str(root),
                                             pythonpath="original-path", bytecode="0"))
                self.assertEqual((root / "server-started").exists(), not fail)
                calls = [json.loads(line) for line in (root / "bundle-calls.jsonl")
                         .read_text().splitlines()]
                self.assertEqual(calls[0], ["restore", "--workspace", ".", "--archive",
                                           str(artifacts)])
                self.assertEqual([c[0] for c in calls], ["restore"] if fail else
                                 ["restore", "check", "deps", "check", "receipt"])
                if not fail:
                    args = json.loads((root / "pip-args.json").read_text())
                    self.assertIn("--no-deps", args)
                    self.assertEqual(args[-1], "requirements/video-web.txt")
                else:
                    self.assertFalse((root / "pip-args.json").exists())


@unittest.skipUnless(AVAILABLE, "Install web/classifier dependencies")
class DeploymentInputsTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.config = self.root / "configs/web/LAPTOP-VIDEO-20261108/inputs.json"
        self.config.parent.mkdir(parents=True)
        self.payloads = {"outputs/model/best.pt": b"synthetic weights",
                         "outputs/model/bundle.json": b'{"synthetic":true}'}
        self.manifest = dict(schema_version="video-web-inputs-v1", files={
            name: dict(sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
            for name, data in self.payloads.items()})
        self.config.write_text(json.dumps(self.manifest))
        self.archive = self.root / "transfer.zip"

    def archive_payloads(self, payloads=None):
        with zipfile.ZipFile(self.archive, "w") as archive:
            for name, data in (self.payloads if payloads is None else payloads).items():
                archive.writestr(name, data)
            archive.writestr("src/ai_exam_monitoring/__init__.py", b"must not overwrite source")
            archive.writestr("../escape.pt", b"must not extract")

    def test_restore_missing_inputs_is_idempotent_and_never_extracts_code(self):
        from ai_exam_monitoring.web.bundle import restore
        source = self.root / "src/ai_exam_monitoring/__init__.py"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"repository source")
        self.archive_payloads()
        restore(self.root, self.archive)
        restore(self.root)
        for name, data in self.payloads.items():
            self.assertEqual((self.root / name).read_bytes(), data)
        self.assertEqual(source.read_bytes(), b"repository source")
        self.assertFalse((self.root / "escape.pt").exists())

    def test_missing_archive_and_changed_existing_input_fail_without_overwrite(self):
        from ai_exam_monitoring.web.bundle import restore
        with self.assertRaisesRegex(DataContractError, "Missing model inputs"):
            restore(self.root)
        self.archive_payloads()
        target = self.root / "outputs/model/best.pt"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"different weights")
        with self.assertRaisesRegex(DataContractError, "refusing overwrite"):
            restore(self.root, self.archive)
        self.assertEqual(target.read_bytes(), b"different weights")
        self.assertFalse((self.root / "outputs/model/bundle.json").exists())

    def test_corrupt_or_missing_member_installs_nothing(self):
        from ai_exam_monitoring.web.bundle import restore
        for corrupt in (False, True):
            with self.subTest(corrupt=corrupt):
                payloads = dict(self.payloads)
                if corrupt:
                    payloads["outputs/model/bundle.json"] = b"x" * len(
                        payloads["outputs/model/bundle.json"])
                else:
                    del payloads["outputs/model/bundle.json"]
                self.archive_payloads(payloads)
                with self.assertRaises(DataContractError):
                    restore(self.root, self.archive)
                self.assertFalse((self.root / "outputs").exists())

    def test_duplicate_member_and_unsafe_manifest_paths_are_rejected(self):
        from ai_exam_monitoring.web.bundle import restore
        self.archive_payloads()
        with zipfile.ZipFile(self.archive, "a") as archive:
            with self.assertWarns(UserWarning):
                archive.writestr("outputs/model/best.pt", self.payloads["outputs/model/best.pt"])
        with self.assertRaisesRegex(DataContractError, "duplicate"):
            restore(self.root, self.archive)
        pin = self.manifest["files"]["outputs/model/best.pt"]
        for name in ("outputs/../src/model.pt", "../outside.pt", "outputs/dir/model.pt:extra",
                     "outputs\\model.pt", "/outputs/model.pt", "outputs/media.mp4"):
            with self.subTest(name=name):
                self.config.write_text(json.dumps(dict(
                    schema_version="video-web-inputs-v1", files={name: pin})))
                with self.assertRaises(DataContractError):
                    restore(self.root, self.archive)
        self.assertFalse((self.root / "outputs").exists())

    def test_web_cli_defaults_to_gpu_and_keeps_explicit_cpu_config(self):
        from ai_exam_monitoring.web.__main__ import main
        for override in (None, Path("configs/web/review.yaml")):
            argv = ["web", "--workspace", str(self.root)]
            if override is not None:
                argv += ["--config", str(override)]
            with (patch.object(sys, "argv", argv),
                  patch("ai_exam_monitoring.web.__main__.load_yaml", return_value={"port": 8765}),
                  patch("ai_exam_monitoring.web.__main__.create_app") as create,
                  patch("ai_exam_monitoring.web.__main__.uvicorn.run") as run):
                main()
            expected = override or self.root / "configs/web/LAPTOP-VIDEO-20261108/web.yaml"
            create.assert_called_once_with(self.root, expected)
            self.assertEqual(run.call_args.kwargs, dict(host="127.0.0.1", port=8765))
