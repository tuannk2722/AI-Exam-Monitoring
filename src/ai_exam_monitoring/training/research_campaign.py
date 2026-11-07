"""Hardware-selected, paired-seed research with bounded, verified continuation."""

from __future__ import annotations

import gc
import json
import math
import os
import signal
import subprocess
import sys
import time
import uuid
from dataclasses import replace
from pathlib import Path
from typing import Any

import torch
import yaml

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .adaptation_config import DinoAdaptationConfig, FilePin, load_adaptation_config, local_path
from .adaptation_model import AdaptationModel
from .adaptation_train import runtime_signature
from .artifacts import code_identity, digest_json, write_json
from .campaign_runtime import IncrementalMirror, admit_run, phase_deadline, safe_child
from .device import configure_device, execution_environment
from .recovery import restore_epoch
from .representation_prepare import campaign_budget, pin, prepare, read_pin, smoke_receipt_path
from .research_analysis import (
    paired_group_bootstrap,
    recipe_key,
    representative_seed,
    resolve_arm,
    summarize_seeds,
)


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def select_profile(vram_bytes: int, proposal: dict[str, Any]) -> str:
    gib = vram_bytes / 1024**3
    if gib >= proposal["profiles"]["full"]["minimum_reported_vram_gib"]:
        return "full"
    if gib >= proposal["profiles"]["core"]["minimum_reported_vram_gib"]:
        return "core"
    raise DataContractError("Insufficient GPU VRAM; no CPU or variable fallback")


def tree_equal(a: Any, b: Any) -> bool:
    if isinstance(a, torch.Tensor):
        return isinstance(b, torch.Tensor) and torch.equal(a, b)
    if isinstance(a, dict):
        return isinstance(b, dict) and a.keys() == b.keys() and all(
            tree_equal(a[k], b[k]) for k in a)
    if isinstance(a, (tuple, list)):
        return type(a) is type(b) and len(a) == len(b) and all(
            tree_equal(x, y) for x, y in zip(a, b, strict=True))
    return bool(a == b)


def verify_artifacts(folder: Path) -> None:
    checks = read(folder / "checksums.json")
    if not isinstance(checks, dict) or not checks:
        raise DataContractError("Missing artifact inventory")
    for name, digest in checks.items():
        if sha256_file(safe_child(folder, name)) != digest:
            raise DataContractError(f"Campaign artifact changed: {folder.name}/{name}")


class ResearchCampaign:
    def __init__(
        self, design_path: Path, root: Path, storage: Path, started_at: float,
        *, resume: bool = False, prior_process_stopped: bool = False,
    ):
        self.root, self.design_path = root.resolve(), design_path.resolve()
        self.storage = storage.resolve()
        self.design = read(self.design_path)
        self.authority = read_pin(self.root, self.design["authorization"])
        proposal_path = FilePin(**self.design["proposal"]).verify(self.root)
        self.proposal = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))
        if (self.authority.get("status") != "approved"
                or self.authority.get("proposal") != self.design["proposal"]
                or self.authority.get("cloud_upload_authorized") is not True
                or self.authority.get("research_authorized_after_smoke") is not True
                or self.authority.get("final_test_inference_authorized") is not False):
            raise DataContractError("Exact approved research/cloud scope missing")
        if not torch.cuda.is_available():
            raise DataContractError("Actual CUDA GPU required; no CPU fallback")
        if not self.storage.is_dir() or self.storage.is_relative_to(self.root):
            raise DataContractError("Mounted private storage outside workspace required")
        if (not math.isfinite(started_at) or started_at > time.time()
                or self.authority["max_gpu_seconds"]
                != self.proposal["budget"]["total_minutes"]*60):
            raise DataContractError("Invalid campaign start or authorization budget")
        vram = torch.cuda.get_device_properties(0).total_memory
        self.profile = select_profile(vram, self.proposal)
        self.budget = campaign_budget(self.design, self.proposal, self.profile)
        self.base = local_path(self.root, self.design["run_dir"])
        self.backup = safe_child(self.storage, self.design["id"])
        self.config_dir = local_path(self.root, self.design["config_dir"])
        self.initialization = local_path(self.root, self.design["initialization_dir"])
        self.receipt = smoke_receipt_path(self.design, self.root, self.profile)
        self.resuming = resume
        self.lease_token = uuid.uuid4().hex
        self.lease = self.backup / "active-lease.json"
        if resume:
            if not prior_process_stopped or not self.backup.is_dir():
                raise DataContractError("Recovery requires confirmation the old process stopped")
            self.mirror = IncrementalMirror(self.backup)
            self.mirror.verify()
            persisted = read(self.mirror.verified_file("runs/campaign.json"))
            if (persisted["design"] != pin(self.root, self.design_path)
                    or persisted["code_sha256"] != code_identity()["sha256"]
                    or persisted["profile"] != self.profile
                    or persisted["started_at"] != started_at
                    or persisted["status"] == "FINISHED"):
                raise DataContractError("Continuation identity/profile/clock mismatch")
            self.mirror.restore(self.root, {"runs": self.base, "configs": self.config_dir,
                                            "initialization": self.initialization,
                                            "receipts": self.receipt.parent.parent})
            self.state = persisted
            if self.lease.exists():
                self.lease.rename(self.backup / f"prior-lease-{self.lease_token}.json")
        else:
            if self.base.exists() or self.backup.exists():
                raise DataContractError("Campaign exists; use verified continuation, not Run all")
            if time.time()-started_at > self.budget["setup_and_environment_minutes"]*60:
                raise TimeoutError("Setup budget exhausted before smoke")
            self.base.mkdir(parents=True)
            self.backup.mkdir()
            self.mirror = IncrementalMirror(self.backup)
            self.state = {"status": "RUNNING", "design": pin(self.root, self.design_path),
                          "code_sha256": code_identity()["sha256"], "profile": self.profile,
                          "started_at": started_at, "runtime_sha256": None,
                          "runs": {}, "research_runs": [], "smoke_runs": [],
                          "final_test_inference_authorized": False}
        self.deadline = started_at + self.budget["total_minutes"]*60
        if time.time() >= self.deadline:
            raise TimeoutError("Original campaign budget exhausted; counter cannot reset")
        with self.lease.open("x", encoding="utf-8") as stream:
            json.dump({"token": self.lease_token, "started_at": time.time(),
                       "pid": os.getpid()}, stream)
        os.environ["E007_RECOVERY_DIR"] = str(self.backup / "recovery")
        self.state["status"] = "RUNNING"

    def sync(self, until: float | None = None) -> dict[str, Any]:
        write_json(self.base / "campaign.json", self.state)
        return self.mirror.sync([
            (self.base, "runs"), (self.config_dir, "configs"),
            (self.initialization, "initialization"), (self.receipt.parent.parent, "receipts"),
        ], deadline=min(until or self.deadline, self.deadline))

    def plan(self, phase: str) -> dict[str, Any]:
        path = self.config_dir / self.profile / phase / "plan.json"
        if not path.exists():
            result = prepare(self.design_path, self.root, phase, profile=self.profile)
            self.sync()
            return result
        result = dict(read(path))
        if (result["design"] != pin(self.root, self.design_path)
                or result["profile"] != self.profile or result["phase"] != phase
                or result["code_sha256"] != code_identity()["sha256"]
                or result["budget"] != self.budget):
            raise DataContractError("Immutable phase/config plan changed")
        for item in result["items"]:
            FilePin(**item["config"]).verify(self.root)
        return result

    def config(self, item: dict[str, Any]) -> DinoAdaptationConfig:
        config = load_adaptation_config(FilePin(**item["config"]).verify(self.root))
        if not isinstance(config, DinoAdaptationConfig) or config.experiment_id != item["id"]:
            raise DataContractError("Multi-seed campaign requires exact V6 config")
        configure_device(config)
        torch.set_num_threads(config.threads)
        env = execution_environment(config)
        signature = runtime_signature(env)
        if self.state["runtime_sha256"] is None:
            self.state["runtime_sha256"] = signature
            write_json(self.base / "runtime.json", env)
            self.sync()
        elif self.state["runtime_sha256"] != signature:
            raise DataContractError("GPU/environment differs from original campaign")
        return config

    def command(self, args: list[str], until: float, log: Path, *, interrupt: bool = False) -> None:
        remaining = min(until, self.deadline)-time.time()
        if remaining <= 0:
            raise TimeoutError("Original run/phase deadline exhausted")
        with log.open("a", encoding="utf-8") as stream:
            process = subprocess.Popen([sys.executable, "-m", *args], cwd=self.root,
                                       stdout=stream, stderr=subprocess.STDOUT)
            try:
                code = process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise TimeoutError("Run stopped at its original deadline") from None
        if (code == 0) == interrupt:
            raise DataContractError(f"Unexpected subprocess status; inspect {log.name}")

    def quarantine(self, path: Path) -> None:
        if path.parent.resolve() != self.base or path == self.base:
            raise DataContractError("Unsafe incomplete-output path")
        folder = self.base / "_incomplete"
        folder.mkdir(exist_ok=True)
        path.rename(folder / f"{path.name}-{uuid.uuid4().hex}")

    def verify_run(self, output: Path, config: DinoAdaptationConfig) -> None:
        verify_artifacts(output)
        run = read(output / "run.json")
        if (run["status"] != "FINISHED" or run["code_sha256"] != code_identity()["sha256"]
                or run["config_sha256"] != digest_json(config.to_dict())):
            raise DataContractError("Completed run identity changed")

    def execute(self, item: dict[str, Any], until: float, *, drill: bool = False) -> Path:
        config = self.config(item)
        output: Path = self.base / str(item["id"])
        entry = self.state["runs"].get(item["id"])
        cap = (self.budget["smoke_minutes"] if config.run_kind == "smoke"
               else self.budget["run_including_reload_minutes"])*60
        if entry is None:
            if config.run_kind == "research":
                admit_run(time.time(), until, cap, len(self.state["research_runs"]),
                          self.budget["max_research_runs"])
            entry = {"item": item, "first_started_at": time.time(), "status": "STARTED"}
            self.state["runs"][item["id"]] = entry
            self.sync(until)
        elif entry["item"] != item:
            raise DataContractError("Resumed run configuration changed")
        run_deadline = min(until, entry["first_started_at"]+cap)
        if entry["status"] == "FINISHED":
            self.verify_run(output, config)
            self.verify_reload(output, config)
            return output
        if time.time() >= run_deadline:
            raise TimeoutError("Unfinished run's original cap exhausted; cannot reset")
        print(f"Starting/continuing {item['id']} ({self.profile})", flush=True)
        args = ["ai_exam_monitoring.training.train", "--workspace", str(self.root),
                "--config", str(FilePin(**item["config"]).verify(self.root)),
                "--output", str(output)]
        if not output.exists() and entry.get("training_started"):
            snapshot = self.backup / "recovery" / f"{item['id']}.tar"
            if not snapshot.is_file():
                raise DataContractError("No verified committed epoch for unfinished run")
            restore_epoch(snapshot, output)
        if output.exists() and read(output / "run.json")["status"] == "RUNNING":
            if not self.resuming:
                raise DataContractError("Possibly active run; do not start a second process")
            self.quarantine(output)
            restore_epoch(self.backup / "recovery" / f"{item['id']}.tar", output)
        already_finished = output.exists() and read(output / "run.json")["status"] == "FINISHED"
        if not already_finished:
            if output.exists():
                args.append("--resume")
            elif drill:
                entry["training_started"] = True
                self.sync(run_deadline)
                self.command([*args, "--interrupt-after", str(config.warmup_epochs)], run_deadline,
                             self.base / f"{item['id']}-interrupt.log", interrupt=True)
                stopped = read(output / "run.json")
                if (stopped["status"] != "INTERRUPTED"
                        or stopped["completed_epochs"] != config.warmup_epochs
                        or "Requested epoch-boundary recovery drill" not in stopped["error"]):
                    raise DataContractError("Unexpected interruption in recovery smoke")
                args.append("--resume")
            entry["training_started"] = True
            self.sync(run_deadline)
            self.command(args, run_deadline, self.base / f"{item['id']}-train.log")
        self.verify_run(output, config)
        evaluation = self.base / f"{item['id']}-reload"
        reload_started = time.time()
        if evaluation.exists() and read(evaluation / "evaluation.json").get("status") != "FINISHED":
            self.quarantine(evaluation)
        if not evaluation.exists():
            self.command(["ai_exam_monitoring.training.evaluate", "--workspace", str(self.root),
                          "--run", str(output), "--output", str(evaluation), "--split", "val"],
                         run_deadline, self.base / f"{item['id']}-reload.log")
        self.verify_reload(output, config)
        entry.update(status="FINISHED", reload="PASS", reload_seconds=time.time()-reload_started)
        collection = self.state["smoke_runs" if config.run_kind == "smoke" else "research_runs"]
        if item["id"] not in collection:
            collection.append(item["id"])
        sync = self.sync(run_deadline)
        entry["final_sync_seconds"] = sync["elapsed_seconds"]
        entry["elapsed_including_reload_sync_seconds"] = time.time()-entry["first_started_at"]
        self.sync(run_deadline)
        return output

    def verify_reload(self, output: Path, config: DinoAdaptationConfig) -> None:
        evaluation = self.base / f"{output.name}-reload"
        verify_artifacts(evaluation)
        receipt = read(evaluation / "evaluation.json")
        if (receipt["status"] != "FINISHED" or receipt["code_sha256"] != code_identity()["sha256"]
                or receipt["config_sha256"] != digest_json(config.to_dict())
                or receipt["checkpoint_sha256"] != sha256_file(output / "best.pt")):
            raise DataContractError("Reload receipt identity mismatch")
        original = read(output / "metrics.json")
        for name, metrics in read(evaluation / "metrics.json").items():
            if (metrics != original[name] or read(output / f"predictions-{name}.json")
                    != read(evaluation / f"predictions-{name}.json")):
                raise DataContractError("Standalone reload metrics/predictions mismatch")

    def shape_checks(self, plan: dict[str, Any], until: float) -> None:
        physical: dict[tuple[str, int, int], DinoAdaptationConfig] = {}
        by_encoder = {}
        for item in plan["items"]:
            config = self.config(item)
            by_encoder[config.encoder_variant] = config
        for name in self.budget["screening_arms"]:
            arm = resolve_arm(self.proposal["arms"], name)
            config = replace(by_encoder[arm["encoder"]], image_size=arm["image_size"],
                             train_last_blocks=arm["train_last_blocks"])
            physical[(config.encoder_variant, config.image_size, config.train_last_blocks)] = config
        checks = []
        for key, config in physical.items():
            if time.time() >= until:
                raise TimeoutError("Smoke shape checks exhausted the original phase budget")
            torch.cuda.reset_peak_memory_stats()
            model = AdaptationModel(config, weights=config.weights.verify(self.root),
                                    initial_head=config.head_initialization.verify(self.root),
                                    workspace=self.root).cuda()
            model.configure_trainable_stage(config, epoch=config.warmup_epochs+1)
            images = torch.zeros(config.batch_size, 3, config.image_size, config.image_size,
                                 device="cuda")
            logits = model(images)
            logits.square().mean().backward()
            if (not torch.isfinite(logits).all() or any(p.grad is None
                    or not torch.isfinite(p.grad).all()
                    for p in model.parameters() if p.requires_grad)):
                raise DataContractError("Active GPU shape/gradient check failed")
            checks.append({"encoder_size_blocks": list(key), "finite_gradients": True,
                           "peak_vram_reserved_bytes": torch.cuda.max_memory_reserved()})
            del logits, images, model
            gc.collect()
            torch.cuda.empty_cache()
        write_json(self.base / "shape-checks.json", {"status": "PASS", "checks": checks})
        self.sync(until)

    def smoke(self) -> None:
        self.state.setdefault("smoke_started_at", time.time())
        until = phase_deadline(self.state["started_at"], self.budget, "smoke",
                               self.state["smoke_started_at"])
        plan = self.plan("smoke")
        if self.receipt.exists():
            receipt = read(self.receipt)
            if (receipt["status"] != "PASS" or receipt["runtime_sha256"]
                    != self.state["runtime_sha256"]):
                raise DataContractError("Smoke receipt/runtime changed")
            for item in plan["items"]:
                self.execute(item, until)
            return
        if time.time() >= until:
            raise TimeoutError("Original smoke pool exhausted")
        self.shape_checks(plan, until)
        for arm in self.budget["smoke_arms"]:
            items = [r for r in plan["items"] if r["arm"] == arm]
            full = self.execute(items[0], until)
            resumed = self.execute(items[1], until, drill=True)
            a = torch.load(full / "last.pt", map_location="cpu", weights_only=True)
            b = torch.load(resumed / "last.pt", map_location="cpu", weights_only=True)
            fields = ("model", "best_model", "optimizer", "history", "rng", "sampler_rng",
                      "sampler_permutation", "sampler_cursor", "cuda_rng", "global_step",
                      "epoch", "best_epoch", "best_loss", "best_val_macro_ap", "early_reference",
                      "stale", "parameter_groups", "selection_metric")
            if (not all(tree_equal(a[k], b[k]) for k in fields)
                    or len({r["stage"] for r in a["history"]}) != 2):
                raise DataContractError("Actual GPU full/resume state parity failed")
            telemetry = read(full / "telemetry.json")
            allowed_peak = telemetry["total_vram_bytes"] * self.proposal["smoke"][
                "maximum_peak_vram_fraction"]
            if telemetry["peak_vram_reserved_bytes"] > allowed_peak:
                raise DataContractError("Actual smoke VRAM headroom below approved requirement")
            entry = self.state["runs"][items[0]["id"]]
            epochs = self.proposal["common"]["max_epochs"]
            projection = (read(full / "run.json")["elapsed_seconds"] * epochs/a["epoch"] * 1.25
                          + entry["reload_seconds"] + entry["final_sync_seconds"])
            if projection > self.budget["run_including_reload_minutes"]*60:
                raise DataContractError("Smoke projection exceeds approved research run cap")
            del a, b
        write_json(self.receipt, {"status": "PASS", "device": "cuda", "profile": self.profile,
                                  "code_sha256": code_identity()["sha256"],
                                  "payload_sha256": self.authority["payload_sha256"],
                                  "design_sha256": sha256_file(self.design_path),
                                  "runtime_sha256": self.state["runtime_sha256"],
                                  "checks": {"resume": "PASS", "reload": "PASS",
                                             "stage_transition": "PASS"},
                                  "shape_checks": pin(self.root, self.base / "shape-checks.json"),
                                  "runs": self.state["smoke_runs"],
                                  "elapsed_seconds": time.time()-self.state["smoke_started_at"]})
        self.sync(until)

    def metrics(self, items: list[dict[str, Any]], arm: str, seeds: list[int]) -> dict[int, Any]:
        result = {}
        for item in items:
            if item["arm"] == arm and item["seed"] in seeds:
                if self.state["runs"].get(item["id"], {}).get("status") != "FINISHED":
                    raise DataContractError("Incomplete paired seed set")
                result[item["seed"]] = read(self.base / item["id"] / "metrics.json")["selection"]
        if set(result) != set(seeds):
            raise DataContractError("Missing paired seed")
        return result

    def research(self) -> None:
        plan = self.plan("research")
        self.state.setdefault("research_started_at", time.time())
        until = phase_deadline(self.state["started_at"], self.budget, "research",
                               self.state["research_started_at"])
        seeds = self.budget["screening_seeds"]
        for item in plan["items"]:
            if item["seed"] in seeds:
                self.execute(item, until)
        ranking = sorted(self.budget["screening_arms"], key=lambda arm: recipe_key(
            arm, list(self.metrics(plan["items"], arm, seeds).values()), self.proposal["arms"]))
        finalists = list(dict.fromkeys([*ranking[:2], "C0"]))
        self.state.update(screening_rank=ranking, confirmation_arms=finalists)
        self.sync(until)
        for item in plan["items"]:
            if item["seed"] in self.budget["confirmation_seeds"] and item["arm"] in finalists:
                self.execute(item, until)
        self.report(plan["items"], finalists, [*seeds, *self.budget["confirmation_seeds"]])

    def report(self, items: list[dict[str, Any]], finalists: list[str], seeds: list[int]) -> None:
        summary: dict[str, Any] = {}
        predictions: dict[str, dict[int, list[dict[str, Any]]]] = {}
        for arm in finalists:
            metrics = self.metrics(items, arm, seeds)
            summary[arm] = {"per_seed": metrics, "mean_sample_sd": summarize_seeds(metrics),
                            "ranking_key": list(recipe_key(
                                arm, list(metrics.values()), self.proposal["arms"])),
                            "representative_seed": representative_seed(metrics)}
            predictions[arm] = {item["seed"]: read(
                self.base / item["id"] / "predictions-selection.json")
                for item in items if item["arm"] == arm and item["seed"] in seeds}
        ranking = sorted(finalists, key=lambda arm: summary[arm]["ranking_key"])
        winner = ranking[0]
        stable = -summary[winner]["ranking_key"][0] >= self.proposal["selection"][
            "five_seed_stability_target"]["both_targets_pass_seeds_min"]
        chosen_seed = summary[winner]["representative_seed"]
        handoff = None
        if chosen_seed is not None:
            chosen = next(item for item in items
                          if item["arm"] == winner and item["seed"] == chosen_seed)
            output = self.base / chosen["id"]
            handoff = {"run_id": chosen["id"], "seed": chosen_seed,
                       "scope": "research_candidate" if stable else "research_checkpoint_only",
                       "checkpoint": pin(self.root, output / "best.pt"),
                       "bundle": pin(self.root, output / "bundle.json"),
                       "calibration": pin(self.root, output / "calibration.json"),
                       "config": chosen["config"], "owner_promotion_required": True}
        write_json(self.base / "research-summary.json", {
            "status": "FINISHED", "profile": self.profile, "recipes": summary,
            "final_recipe_rank": ranking, "winner": winner,
            "checkpoint_handoff": handoff,
            "four_of_five_both_targets": stable,
            "decision": "research_candidate_owner_review" if stable else "continue_research",
            "independent_holdout": False, "test_opened": False, "runtime_replaced": False})
        bootstrap = {}
        for arm in finalists:
            if arm != "C0":
                protocol = self.proposal["analysis"]["paired_whole_group_bootstrap"]
                if len({r["group_id"] for r in predictions[arm][seeds[0]]}) != protocol["groups"]:
                    raise DataContractError("Bootstrap group support differs from protocol")
                bootstrap[arm] = paired_group_bootstrap(predictions["C0"], predictions[arm],
                                                       replicates=protocol["replicates"],
                                                       seed=protocol["seed"])
        write_json(self.base / "paired-bootstrap.json", bootstrap)

    def run(self) -> None:
        try:
            self.sync()
            self.smoke()
            self.research()
            self.state.update(status="FINISHED", decision="owner_review_required")
            self.sync()
            self.mirror.verify()
        except BaseException as error:
            self.state.update(status="STOPPED", error=f"{type(error).__name__}: {error}")
            try:
                self.sync()
            except BaseException as sync_error:
                write_json(self.backup / "persistence-failure.json", {
                    "status": "STOPPED", "error": repr(sync_error),
                    "original_error": repr(error), "clock_not_reset": True})
            raise
        finally:
            if self.lease.exists() and read(self.lease).get("token") == self.lease_token:
                self.lease.unlink()


def run_multiseed_campaign(
    design_path: Path, root: Path, storage: Path, started_at: float,
    *, resume: bool = False, prior_process_stopped: bool = False,
) -> None:
    ResearchCampaign(design_path, root, storage, started_at, resume=resume,
                     prior_process_stopped=prior_process_stopped).run()
