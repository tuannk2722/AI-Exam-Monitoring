from __future__ import annotations

import ast
import base64
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
import types
import unittest
import zlib
from pathlib import Path
from unittest.mock import Mock, patch

from ai_exam_monitoring.training.colab_launcher import launch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import torch

    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.training.artifacts import write_json

    SPEC = importlib.util.spec_from_file_location(
        "e009_recovery", Path(__file__).parents[1] / "src/e009_recovery.py"
    )
    assert SPEC is not None and SPEC.loader is not None
    recovery = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(recovery)


class RecoveryNotebookTests(unittest.TestCase):
    def test_worker_stdout_and_stderr_are_forwarded_before_exit_failure(self):
        notebook = json.loads(
            (Path(__file__).parents[1] / "notebooks/E009-V15-Colab.ipynb").read_text(
                encoding="utf-8"
            )
        )
        tree = ast.parse("".join(notebook["cells"][1]["source"]))
        forward = next(
            n
            for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name == "forward_worker_output"
        )
        with subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import sys; print('child-out'); print('child-error',file=sys.stderr); sys.exit(1)",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        ) as process:
            printer = Mock()
            scope = {"worker": process, "print": printer}
            exec(compile(ast.Module(body=[forward], type_ignores=[]), "<forward>", "exec"), scope)
            scope["forward_worker_output"]()
            self.assertEqual(process.wait(timeout=10), 1)
            output = "".join(call.args[0] for call in printer.call_args_list)
            self.assertIn("child-out", output)
            self.assertIn("child-error", output)

    @unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
    def test_notebook_adapter_runs_original_bootstrap_and_preserves_subprocess_constants(self):
        notebook = json.loads(
            (Path(__file__).parents[1] / "notebooks/E009-V15-Colab.ipynb").read_text(
                encoding="utf-8"
            )
        )
        tree = ast.parse("".join(notebook["cells"][1]["source"]))
        worker = next(
            ast.literal_eval(n.value)
            for n in ast.walk(tree)
            if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id == "worker_code"
        )
        nodes = [
            n
            for n in ast.parse(worker).body
            if (
                isinstance(n, (ast.FunctionDef, ast.ClassDef))
                and n.name in {"route_campaign", "ProcessAPI"}
            )
            or (
                isinstance(n, ast.Assign)
                and isinstance(n.targets[0], ast.Name)
                and n.targets[0].id == "process_api"
            )
        ]
        runner = Mock()
        process_stub = types.SimpleNamespace(
            run=runner, STDOUT=subprocess.STDOUT, check_output=Mock(return_value="numpy==2.2.6\n")
        )
        scope = {
            "subprocess": process_stub,
            "types": types,
            "original_run": runner,
            "extension_path": Path("/extension.py"),
            "auth_path": Path("/authorization.json"),
            "auth_sha": "pin",
        }
        exec(compile(ast.Module(body=nodes, type_ignores=[]), "<adapter>", "exec"), scope)
        adapter = scope["process_api"]
        # This reproduces the failure from Colab: launch needs STDOUT during setup.
        self.assertEqual(adapter.STDOUT, subprocess.STDOUT)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            storage = root / "drive"
            storage.mkdir()
            (storage / "E009-V15-COLAB-20261106").mkdir()
            first = time.time() - 300
            write_json(
                storage / "E009-launch.json",
                {
                    "bundle_sha256": "bundle",
                    "started_at": first,
                    "setup_elapsed_seconds": 1,
                    "setup_in_progress": False,
                },
            )
            clone = types.FunctionType(
                launch.__code__,
                {
                    **launch.__globals__,
                    "subprocess": adapter,
                    "extract_bundle": Mock(
                        return_value={"code_sha256": "original", "design": {"path": "design.json"}}
                    ),
                    "committed_state": Mock(return_value={"started_at": first}),
                    "shutil": types.SimpleNamespace(
                        disk_usage=Mock(return_value=types.SimpleNamespace(free=10**12))
                    ),
                },
                launch.__name__,
                launch.__defaults__,
                launch.__closure__,
            )
            clone.__kwdefaults__ = launch.__kwdefaults__
            clone(
                root / "bundle.zip",
                "bundle",
                storage,
                attempt_started_at=time.time(),
                resume=True,
                prior_process_stopped=True,
                workspace=root / "workspace",
                venv=root / "venv",
            )
            journal = json.loads((storage / "E009-launch.json").read_text())
            self.assertTrue(journal["environment_ready"])
            self.assertEqual(journal["started_at"], first)
            self.assertEqual(runner.call_args.args[0][1], str(Path("/extension.py")))

    @unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
    def test_research_preparer_binding_changes_cap_without_mutating_package_globals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            c = recovery.RecoveryCampaign.__new__(recovery.RecoveryCampaign)
            c.root, c.design_path, c.config_dir, c.profile = (
                root,
                root / "design",
                root / "configs",
                "full",
            )
            c.recovery_authorization = {"path": "recovery.json", "sha256": "pin"}
            c.state = {"recovery_extension": {"sha256": "extension"}}
            c.sync = Mock()
            folder = c.config_dir / "full/research"
            namespace = {"write_json": write_json, "folder": folder}
            exec(
                "def prepare(design, root, phase, *, profile=None):\n"
                "    budget=campaign_budget({}, {}, profile)\n"
                "    write_json(folder/'approval.json', {'status':'approved'})\n"
                "    return {'budget':budget}\n",
                namespace,
            )
            resolver = Mock(
                return_value={
                    "run_including_reload_minutes": 20,
                    "per_research_run_including_reload_and_sync_minutes": 20,
                    "total_minutes": 720,
                }
            )
            with (
                patch.object(recovery.preparer, "prepare", namespace["prepare"]),
                patch.object(recovery.preparer, "campaign_budget", resolver),
            ):
                result = c.plan("research")
                self.assertIs(recovery.preparer.campaign_budget, resolver)
                self.assertIs(recovery.preparer.prepare, namespace["prepare"])
            self.assertEqual(result["budget"]["run_including_reload_minutes"], 45)
            self.assertEqual(result["budget"]["total_minutes"], 720)
            self.assertEqual(
                json.loads((folder / "approval.json").read_text())["recovery_authorization"],
                c.recovery_authorization,
            )

    def test_notebook_payload_and_only_canonical_command_is_redirected(self):
        root = Path(__file__).parents[1]
        notebook = json.loads((root / "notebooks/E009-V15-Colab.ipynb").read_text(encoding="utf-8"))
        tree = ast.parse("".join(notebook["cells"][1]["source"]))
        names = {"RECOVERY_PAYLOAD", "RECOVERY_PAYLOAD_SHA256", "worker_code"}
        constants = {
            n.targets[0].id: ast.literal_eval(n.value)
            for n in ast.walk(tree)
            if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id in names
        }
        raw = zlib.decompress(base64.b64decode(constants["RECOVERY_PAYLOAD"]))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), constants["RECOVERY_PAYLOAD_SHA256"])
        payload = json.loads(raw)
        self.assertEqual(
            payload["extension.py"], (root / "src/e009_recovery.py").read_text(encoding="utf-8")
        )
        worker = ast.parse(constants["worker_code"])
        route = next(
            n for n in worker.body if isinstance(n, ast.FunctionDef) and n.name == "route_campaign"
        )
        runner = Mock()
        namespace = {
            "original_run": runner,
            "extension_path": Path("/extension.py"),
            "auth_path": Path("/authorization.json"),
            "auth_sha": "pin",
        }
        exec(
            compile(ast.Module(body=[route], type_ignores=[]), "<worker-routing>", "exec"),
            namespace,
        )
        namespace["route_campaign"](["python", "-m", "pip", "install", "numpy"], check=True)
        self.assertEqual(runner.call_args.args[0], ["python", "-m", "pip", "install", "numpy"])
        namespace["route_campaign"](
            [
                "python",
                "-m",
                "ai_exam_monitoring.training.representation_campaign",
                "--resume",
                "--prior-process-stopped",
            ],
            check=True,
        )
        self.assertEqual(runner.call_args.args[0][1], str(Path("/extension.py")))
        with self.assertRaises(RuntimeError):
            namespace["route_campaign"](
                ["python", "-m", "ai_exam_monitoring.training.representation_campaign"]
            )


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class RecoveryTests(unittest.TestCase):
    def test_cap_override_preserves_other_limits(self):
        old = {
            "total_minutes": 720,
            "research_pool_minutes": 500,
            "training_deadline_minutes_from_first_launch": 610,
            "run_including_reload_minutes": 20,
            "per_research_run_including_reload_and_sync_minutes": 20,
        }
        new = recovery.revised_budget(old)
        self.assertEqual(old["run_including_reload_minutes"], 20)
        self.assertEqual(new["run_including_reload_minutes"], 45)
        self.assertEqual(new["per_research_run_including_reload_and_sync_minutes"], 45)
        self.assertEqual(
            {k: v for k, v in new.items() if new[k] != old[k]},
            {
                "run_including_reload_minutes": 45,
                "per_research_run_including_reload_and_sync_minutes": 45,
            },
        )

    def fixture(self, root):
        storage = root / "drive"
        backup = storage / "E009-V15-COLAB-20261106"
        backup.mkdir(parents=True)
        names = [
            f"E009-V15-SMOKE-{a}-{m}" for a in ("C0", "S4", "B448") for m in ("FULL", "RESUME")
        ]
        state = {
            "design": {"path": "design.json", "sha256": "design"},
            "code_sha256": "original",
            "runtime_sha256": "runtime",
            "profile": "full",
            "started_at": 1000.0,
            "status": "STOPPED",
            "research_runs": [],
            "smoke_runs": names,
            "runs": {n: {"status": "FINISHED", "reload": "PASS"} for n in names},
            "error": "DataContractError: Smoke projection exceeds approved research run cap",
        }
        write_json(backup / "runs/campaign.json", state)
        digest = sha256_file(backup / "runs/campaign.json")
        write_json(
            backup / "mirror-manifest.json",
            {
                "schema_version": "incremental-campaign-mirror-v1",
                "files": {
                    "runs/campaign.json": {
                        "sha256": digest,
                        "bytes": (backup / "runs/campaign.json").stat().st_size,
                    }
                },
            },
        )
        write_json(storage / "E009-launch.json", {"bundle_sha256": "bundle", "started_at": 1000.0})
        auth = {
            "status": "approved",
            "id": "E009-RECOVERY-20261107",
            "research_run_minutes": 45,
            "total_minutes": 720,
            "research_pool_minutes": 500,
            "verify_completed_smoke_after_original_window": True,
            "final_test_inference_authorized": False,
            "extension_sha256": sha256_file(Path(recovery.__file__)),
            "bundle_sha256": "bundle",
            "started_at": 1000.0,
            "campaign_id": backup.name,
            "design": state["design"],
            "code_sha256": "original",
            "runtime_sha256": "runtime",
            "original_mirror_sha256": sha256_file(backup / "mirror-manifest.json"),
            "original_campaign_sha256": digest,
            "smoke_runs": names,
        }
        path = root / "authorization.json"
        write_json(path, auth)
        return storage, path, auth

    def test_authorization_accepts_only_exact_stopped_campaign(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(recovery.time, "time", return_value=2000),
        ):
            storage, path, auth = self.fixture(Path(tmp))
            self.assertEqual(recovery.authorize(path, sha256_file(path), storage), auth)
            with self.assertRaises(DataContractError):
                recovery.authorize(path, "changed", storage)
            write_json(
                storage / "E009-launch.json", {"bundle_sha256": "bundle", "started_at": 2000}
            )
            with self.assertRaises(DataContractError):
                recovery.authorize(path, sha256_file(path), storage)

    def test_original_total_deadline_is_not_extended(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage, path, _ = self.fixture(Path(tmp))
            with patch.object(recovery.time, "time", return_value=1000 + 720 * 60):
                with self.assertRaises(TimeoutError):
                    recovery.authorize(path, sha256_file(path), storage)

    def smoke_fixture(self, root, *, tamper=False, incomplete=False):
        c = recovery.RecoveryCampaign.__new__(recovery.RecoveryCampaign)
        c.root = root
        c.profile = "full"
        c.base = root / "runs"
        c.base.mkdir()
        c.receipt = root / "receipt.json"
        c.original_budget = {"setup_and_environment_minutes": 40, "actual_gpu_smoke_minutes": 70}
        c.budget = {"screening_arms": ["C0"], "smoke_arms": ["C0"]}
        c.proposal = {"arms": {"C0": {"encoder": "S", "image_size": 336, "train_last_blocks": 2}}}
        c.recovery_authorization = {"path": "authorization.json", "sha256": "pin"}
        c.authority = {"payload_sha256": "data"}
        c.design_path = root / "design.json"
        c.design_path.write_text("{}")
        names = ["C0-FULL", "C0-RESUME"]
        c.recovery_auth = {"smoke_runs": names}
        c.state = {
            "started_at": 1000.0,
            "smoke_started_at": 1100.0,
            "runtime_sha256": "runtime",
            "smoke_runs": names,
            "runs": {},
            "recovery_extension": {"sha256": "extension"},
        }
        write_json(
            c.base / "shape-checks.json",
            {
                "status": "PASS",
                "checks": [{"encoder_size_blocks": ["S", 336, 2], "finite_gradients": True}],
            },
        )
        fields = (
            "model",
            "best_model",
            "optimizer",
            "rng",
            "sampler_rng",
            "sampler_permutation",
            "sampler_cursor",
            "cuda_rng",
            "global_step",
            "best_epoch",
            "best_loss",
            "best_val_macro_ap",
            "early_reference",
            "stale",
            "parameter_groups",
            "selection_metric",
        )
        for name in names:
            folder = c.base / name
            folder.mkdir()
            state = dict.fromkeys(fields, 0)
            state.update(epoch=5, history=[{"stage": "warmup"}, {"stage": "adapt"}])
            if tamper and name.endswith("RESUME"):
                state["rng"] = 1
            torch.save(state, folder / "last.pt")
            write_json(folder / "run.json", {"elapsed_seconds": 200})
            write_json(
                folder / "telemetry.json", {"peak_vram_reserved_bytes": 10, "total_vram_bytes": 100}
            )
            c.state["runs"][name] = {
                "status": "FINISHED",
                "reload": "PASS",
                "first_started_at": 1200,
                "elapsed_including_reload_sync_seconds": 300,
                "reload_seconds": 10,
                "final_sync_seconds": 2,
            }
        if incomplete:
            c.state["runs"][names[0]]["status"] = "STARTED"
        c.plan = Mock(return_value={"items": [{"id": n, "arm": "C0"} for n in names]})
        c.config = Mock(return_value=None)
        c.verify_run = Mock()
        c.verify_reload = Mock()
        c.sync = Mock()
        c.command = Mock(side_effect=AssertionError("Smoke must never train again"))
        return c

    def test_completed_smoke_revalidated_after_old_window_without_training(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(recovery.time, "time", return_value=10000),
        ):
            c = self.smoke_fixture(Path(tmp))
            c.smoke()
            receipt = json.loads(c.receipt.read_text())
            self.assertTrue(receipt["completed_smoke_reused"])
            self.assertFalse(receipt["smoke_training_repeated"])
            self.assertEqual(c.verify_run.call_count, 2)
            c.command.assert_not_called()
            initial = hashlib.sha256(c.receipt.read_bytes()).hexdigest()
            c.smoke()
            self.assertEqual(hashlib.sha256(c.receipt.read_bytes()).hexdigest(), initial)

    def test_incomplete_smoke_or_parity_failure_cannot_publish_pass(self):
        for case in ({"tamper": True}, {"incomplete": True}):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                c = self.smoke_fixture(Path(tmp), **case)
                with self.assertRaises(DataContractError):
                    c.smoke()
                self.assertFalse(c.receipt.exists())
                c.command.assert_not_called()
