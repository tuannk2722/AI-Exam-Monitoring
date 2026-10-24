"""Budgeted Colab campaign: actual GPU smoke, exact reload, then approved research queue."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .adaptation_config import FilePin, RepresentationConfig, load_adaptation_config, local_path
from .adaptation_model import tensor_digest
from .adaptation_train import runtime_signature
from .artifacts import code_identity, write_json
from .device import configure_device, execution_environment
from .representation_prepare import pin, prepare, read_pin


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def champion_key(arm: str, metrics: dict[str, Any]) -> tuple[Any, ...]:
    calibrated = metrics["calibrated_evaluation"]
    rows = list(calibrated["targets"].values())
    passed = sum(row.get("v11_quality_gate_pass") is True for row in rows)
    gap = sum(max(0., .8 - (r["precision"] or 0.))
              + max(0., .8 - (r["recall"] or 0.))
              + max(0., (r["fpr"] if r["fpr"] is not None else 1.) - .2) for r in rows)
    return (-int(passed == 2), -passed, gap, -(metrics["macro_ap"] or 0.),
            metrics["macro_masked_bce"], arm)


def run_campaign(design_path: Path, root: Path, storage: Path, started_at: float) -> None:
    root, design_path, storage = root.resolve(), design_path.resolve(), storage.resolve()
    design = read(design_path)
    authority = read_pin(root, design["authorization"])
    if not torch.cuda.is_available():
        raise DataContractError("Actual CUDA GPU required before campaign; no CPU fallback")
    if not storage.is_dir() or storage.is_relative_to(root):
        raise DataContractError("Mounted private persistent storage outside workspace required")
    if started_at > time.time() or time.time() - started_at >= authority["max_gpu_seconds"]:
        raise DataContractError("Invalid/exhausted GPU allocation start timestamp")
    deadline = started_at + authority["max_gpu_seconds"]
    base = local_path(root, design["run_dir"])
    if base.exists():
        raise DataContractError("Campaign already exists; preserve evidence and recover explicitly")
    base.mkdir(parents=True)
    backup = storage / design["id"]
    if backup.exists():
        raise DataContractError("Persistent campaign already exists; do not duplicate runs")
    backup.mkdir()
    os.environ["E007_RECOVERY_DIR"] = str(backup / "recovery")
    state: dict[str, Any] = {
        "status": "RUNNING", "design": pin(root, design_path), "started_at": started_at,
        "deadline": deadline, "research_runs": [], "smoke_runs": [],
        "code_sha256": code_identity()["sha256"], "final_test_inference_authorized": False,
    }

    def sync() -> None:
        write_json(base / "campaign.json", state)
        # Never copy unrelated outputs, raw sources, credentials or browser state.
        for source, relative in ((base, "runs"),
                                 (local_path(root, design["config_dir"]), "configs")):
            shutil.copytree(source, backup / relative, dirs_exist_ok=True)
        receipt = local_path(root, design["smoke_receipt"])
        if receipt.exists():
            shutil.copy2(receipt, backup / "smoke-receipt.json")

    def command(args: list[str], until: float, log: Path, *, interrupt: bool = False) -> None:
        remaining = min(until, deadline) - time.time()
        if remaining <= 0:
            raise TimeoutError("Approved campaign/phase budget exhausted")
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.Popen([sys.executable, "-m", *args], cwd=root,
                                       stdout=stream, stderr=subprocess.STDOUT)
            try:
                result = process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                # Request an orderly epoch rollback; never silently alter run variables.
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise TimeoutError("Approved budget exhausted; see checkpoint recovery") from None
        if result != 0 and not interrupt:
            raise DataContractError(f"Subprocess failed; inspect {log}")
        if result == 0 and interrupt:
            raise DataContractError("Requested recovery drill did not interrupt")

    runtime: str | None = None

    def execute(item: dict[str, Any], until: float, *, drill: bool = False) -> Path:
        nonlocal runtime
        config_path = FilePin(**item["config"]).verify(root)
        config = load_adaptation_config(config_path)
        if not isinstance(config, RepresentationConfig):
            raise DataContractError("Campaign requires V4 config")
        configure_device(config)
        torch.set_num_threads(config.threads)
        current = execution_environment(config)
        signature = runtime_signature(current)
        if runtime is None:
            runtime = signature
            write_json(base / "runtime.json", current)
        elif signature != runtime:
            raise DataContractError("GPU/environment changed within campaign")
        output: Path = base / item["id"]
        args = ["ai_exam_monitoring.training.train", "--workspace", str(root),
                "--config", str(config_path), "--output", str(output)]
        if drill:
            command([*args, "--interrupt-after", str(config.warmup_epochs)], until,
                    base / f"{item['id']}-interrupt.log", interrupt=True)
            interrupted = read(output / "run.json")
            if (interrupted["status"] != "INTERRUPTED"
                    or interrupted["completed_epochs"] != config.warmup_epochs
                    or "Requested epoch-boundary recovery drill" not in interrupted["error"]):
                raise DataContractError("Unexpected interruption; smoke cannot continue")
            args.append("--resume")
        command(args, until, base / f"{item['id']}-train.log")
        if read(output / "run.json")["status"] != "FINISHED":
            raise DataContractError("Run did not finish")
        evaluation = base / f"{item['id']}-reload"
        command(["ai_exam_monitoring.training.evaluate", "--workspace", str(root),
                 "--run", str(output), "--output", str(evaluation), "--split", "val"],
                until, base / f"{item['id']}-reload.log")
        original, reloaded = read(output / "metrics.json"), read(evaluation / "metrics.json")
        for name, metrics in reloaded.items():
            if metrics != original[name] or read(output / f"predictions-{name}.json") != read(
                evaluation / f"predictions-{name}.json"
            ):
                raise DataContractError("Standalone reload parity failed")
        state["smoke_runs" if config.run_kind == "smoke" else "research_runs"].append({
            **item, "run": pin(root, output / "run.json"), "reload": "PASS",
            "metrics": pin(root, output / "metrics.json"),
        })
        sync()
        return output

    try:
        smoke_started = time.time()
        smoke = prepare(design_path, root, "smoke")
        smoke_deadline = min(deadline, smoke_started + smoke["budget"]["smoke_minutes"] * 60)
        sync()
        for arm in ("R0", "D1"):
            items = [item for item in smoke["items"] if item["arm"] == arm]
            if len(items) != 2:
                raise DataContractError("Smoke requires full/resumed pair for each encoder")
            full = execute(items[0], smoke_deadline)
            resumed = execute(items[1], smoke_deadline, drill=True)
            a = torch.load(full / "last.pt", map_location="cpu", weights_only=True)
            b = torch.load(resumed / "last.pt", map_location="cpu", weights_only=True)
            if (a["history"] != b["history"]
                    or tensor_digest(a["model"]) != tensor_digest(b["model"])
                    or tensor_digest(a["best_model"]) != tensor_digest(b["best_model"])
                    or len({row["stage"] for row in a["history"]}) != 2):
                raise DataContractError("GPU resume/stage-transition parity failed")
            # Conservative full-run estimate, including reporting and reload.
            seconds = read(full / "run.json")["elapsed_seconds"]
            run_cap = smoke["budget"]["run_including_reload_minutes"] * 60
            if seconds * 12 / a["epoch"] * 1.25 > run_cap:
                raise DataContractError("Smoke predicts full run exceeds approved cap")
        write_json(local_path(root, design["smoke_receipt"]), {
            "status": "PASS", "device": "cuda", "code_sha256": code_identity()["sha256"],
            "payload_sha256": authority["payload_sha256"],
            "design_sha256": sha256_file(design_path), "runtime_sha256": runtime,
            "checks": {"resume": "PASS", "reload": "PASS", "stage_transition": "PASS"},
            "runs": state["smoke_runs"], "elapsed_seconds": time.time() - smoke_started,
        })
        research = prepare(design_path, root, "research")
        sync()
        seed = design["screening_seed"]
        screening = [item for item in research["items"] if item["seed"] == seed]
        ranking = []

        def research_run(item: dict[str, Any]) -> Path:
            cap = research["budget"]["run_including_reload_minutes"] * 60
            if (len(state["research_runs"]) >= authority["max_research_runs"]
                    or time.time() + cap > deadline):
                raise TimeoutError("No approved budget remaining for another complete run")
            return execute(item, min(deadline, time.time() + cap))

        for item in screening:
            output = research_run(item)
            ranking.append((champion_key(item["arm"], read(output / "metrics.json")["selection"]),
                            item["arm"]))
        champion = min(ranking)[1]
        state["screening_champion"] = champion
        sync()
        for item in research["items"]:
            if item["seed"] != seed and item["arm"] in {champion, "R0"}:
                research_run(item)
        state["status"] = "FINISHED"
        state["decision"] = "continue_research_only_owner_review_required"
    except BaseException as error:
        state["status"] = "STOPPED"
        state["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        state["elapsed_seconds"] = time.time() - started_at
        sync()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--gpu-started-at", type=float, required=True)
    args = parser.parse_args()
    run_campaign(args.design, args.workspace, args.storage, args.gpu_started_at)


if __name__ == "__main__":
    main()
