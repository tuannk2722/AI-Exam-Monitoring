"""Pinned E009 recovery extension; the checkpoint-producing package stays immutable.

Only the approved per-run time cap changes. Original trainer/config validators,
runtime identity, completed-run hashes and the research queue remain authoritative.
The notebook transports this file separately from the original private bundle.
"""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path
from types import FunctionType
from typing import Any

import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training import representation_prepare as preparer
from ai_exam_monitoring.training.artifacts import code_identity, write_json
from ai_exam_monitoring.training.campaign_runtime import IncrementalMirror, phase_deadline
from ai_exam_monitoring.training.representation_prepare import pin
from ai_exam_monitoring.training.research_analysis import resolve_arm
from ai_exam_monitoring.training.research_campaign import ResearchCampaign, read, tree_equal


def revised_budget(budget: dict[str, Any]) -> dict[str, Any]:
    """The two aliases must agree; every other approved limit is unchanged."""
    return {
        **budget,
        "per_research_run_including_reload_and_sync_minutes": 45,
        "run_including_reload_minutes": 45,
    }


def authorize(path: Path, expected_sha: str, storage: Path) -> dict[str, Any]:
    if sha256_file(path) != expected_sha:
        raise DataContractError("Recovery authorization SHA mismatch")
    auth = read(path)
    if (
        auth.get("status") != "approved"
        or auth.get("id") != "E009-RECOVERY-20261107"
        or auth.get("research_run_minutes") != 45
        or auth.get("total_minutes") != 720
        or auth.get("research_pool_minutes") != 500
        or auth.get("verify_completed_smoke_after_original_window") is not True
        or auth.get("final_test_inference_authorized") is not False
        or auth.get("extension_sha256") != sha256_file(Path(__file__))
    ):
        raise DataContractError("Recovery scope/extension differs from owner approval")
    journal = read(storage / "E009-launch.json")
    if (
        journal["bundle_sha256"] != auth["bundle_sha256"]
        or journal["started_at"] != auth["started_at"]
    ):
        raise DataContractError("Recovery cannot change original bundle/clock")
    if not math.isfinite(auth["started_at"]) or time.time() >= auth["started_at"] + 720 * 60:
        raise TimeoutError("Original 12-hour budget exhausted")
    mirror = IncrementalMirror(storage / auth["campaign_id"])
    state = read(mirror.verified_file("runs/campaign.json"))
    if (
        state["design"] != auth["design"]
        or state["code_sha256"] != auth["code_sha256"]
        or state["runtime_sha256"] != auth["runtime_sha256"]
        or state["profile"] != "full"
        or state["started_at"] != auth["started_at"]
    ):
        raise DataContractError("Recovery campaign/design/runtime identity mismatch")
    prior = state.get("recovery_extension")
    if prior is None:
        if (
            sha256_file(mirror.manifest_path) != auth["original_mirror_sha256"]
            or mirror.files["runs/campaign.json"]["sha256"] != auth["original_campaign_sha256"]
            or state["status"] != "STOPPED"
            or state["research_runs"]
            or state["error"]
            != "DataContractError: Smoke projection exceeds approved research run cap"
        ):
            raise DataContractError("Initial recovery must match the audited stopped campaign")
    elif prior != {"sha256": auth["extension_sha256"], "authorization_sha256": expected_sha}:
        raise DataContractError("A different recovery extension already owns this campaign")
    if set(state["smoke_runs"]) != set(auth["smoke_runs"]) or any(
        state["runs"][name]["status"] != "FINISHED" or state["runs"][name].get("reload") != "PASS"
        for name in auth["smoke_runs"]
    ):
        raise DataContractError("All original smoke runs must already be finished")
    return dict(auth)


class RecoveryCampaign(ResearchCampaign):
    """Reuse completed original smoke; prepare future research with the approved cap."""

    recovery_authorization: dict[str, str]
    recovery_auth: dict[str, Any]
    original_budget: dict[str, Any]

    def plan(self, phase: str) -> dict[str, Any]:
        if phase == "smoke":
            effective = self.budget
            try:
                self.budget = self.original_budget
                return super().plan(phase)
            finally:
                self.budget = effective
        folder = self.config_dir / self.profile / phase
        if (folder / "plan.json").exists():
            result = super().plan(phase)
            if result.get("recovery_authorization") != self.recovery_authorization:
                raise DataContractError("Research plan lacks the exact recovery authorization")
            return result

        # Explicit dependency binding of the ORIGINAL preparer bytecode. No source,
        # pins or global functions are overwritten in the shipped package.
        def budget_for_recovery(design: Any, proposal: Any, profile: Any) -> dict[str, Any]:
            return revised_budget(preparer.campaign_budget(design, proposal, profile))

        prepare = FunctionType(
            preparer.prepare.__code__,
            {**preparer.prepare.__globals__, "campaign_budget": budget_for_recovery},
            "prepare",
            preparer.prepare.__defaults__,
            preparer.prepare.__closure__,
        )
        prepare.__kwdefaults__ = preparer.prepare.__kwdefaults__
        result = prepare(self.design_path, self.root, phase, profile=self.profile)
        result["recovery_authorization"] = self.recovery_authorization
        result["recovery_extension"] = self.state["recovery_extension"]
        write_json(folder / "plan.json", result)
        approval = read(folder / "approval.json")
        approval["recovery_authorization"] = self.recovery_authorization
        approval["recovery_extension"] = self.state["recovery_extension"]
        write_json(folder / "approval.json", approval)
        self.sync()
        return dict(result)

    def smoke(self) -> None:
        plan = self.plan("smoke")
        if set(item["id"] for item in plan["items"]) != set(self.recovery_auth["smoke_runs"]):
            raise DataContractError("Original smoke plan membership changed")
        original_until = phase_deadline(
            self.state["started_at"], self.original_budget, "smoke", self.state["smoke_started_at"]
        )
        shape = read(self.base / "shape-checks.json")
        expected = {
            tuple(
                resolve_arm(self.proposal["arms"], arm)[key]
                for key in ("encoder", "image_size", "train_last_blocks")
            )
            for arm in self.budget["screening_arms"]
        }
        if (
            shape["status"] != "PASS"
            or expected != {tuple(row["encoder_size_blocks"]) for row in shape["checks"]}
            or any(row["finite_gradients"] is not True for row in shape["checks"])
        ):
            raise DataContractError("Original shape/gradient evidence is incomplete")
        for item in plan["items"]:
            entry = self.state["runs"][item["id"]]
            if (
                entry["status"] != "FINISHED"
                or entry.get("reload") != "PASS"
                or entry["first_started_at"] + entry["elapsed_including_reload_sync_seconds"]
                > original_until
            ):
                raise DataContractError(
                    "Only smoke finished within its original window can be reused"
                )
            config = self.config(item)  # Actual runtime equality, not a copied GPU label.
            output = self.base / item["id"]
            self.verify_run(output, config)
            self.verify_reload(output, config)
        projections = {}
        for arm in self.budget["smoke_arms"]:
            items = [item for item in plan["items"] if item["arm"] == arm]
            full, resumed = [self.base / item["id"] for item in items]
            a = torch.load(full / "last.pt", map_location="cpu", weights_only=True)
            b = torch.load(resumed / "last.pt", map_location="cpu", weights_only=True)
            fields = (
                "model",
                "best_model",
                "optimizer",
                "history",
                "rng",
                "sampler_rng",
                "sampler_permutation",
                "sampler_cursor",
                "cuda_rng",
                "global_step",
                "epoch",
                "best_epoch",
                "best_loss",
                "best_val_macro_ap",
                "early_reference",
                "stale",
                "parameter_groups",
                "selection_metric",
            )
            if (
                not all(tree_equal(a[key], b[key]) for key in fields)
                or len({row["stage"] for row in a["history"]}) != 2
            ):
                raise DataContractError("Actual GPU full/resume state parity failed")
            telemetry = read(full / "telemetry.json")
            if telemetry["peak_vram_reserved_bytes"] > telemetry["total_vram_bytes"] * 0.85:
                raise DataContractError("Original smoke VRAM headroom failed")
            entry = self.state["runs"][items[0]["id"]]
            seconds = (
                read(full / "run.json")["elapsed_seconds"] * 24 / a["epoch"] * 1.25
                + entry["reload_seconds"]
                + entry["final_sync_seconds"]
            )
            if not math.isfinite(seconds) or seconds > 45 * 60:
                raise DataContractError("Smoke projection exceeds the approved 45-minute cap")
            projections[arm] = seconds
            del a, b
        if self.receipt.exists():
            receipt = read(self.receipt)
            if (
                receipt.get("recovery_authorization") != self.recovery_authorization
                or receipt.get("runtime_sha256") != self.state["runtime_sha256"]
                or receipt.get("projection_seconds") != projections
            ):
                raise DataContractError("Published recovery smoke receipt changed")
        else:
            write_json(
                self.receipt,
                {
                    "status": "PASS",
                    "device": "cuda",
                    "profile": self.profile,
                    "code_sha256": code_identity()["sha256"],
                    "payload_sha256": self.authority["payload_sha256"],
                    "design_sha256": sha256_file(self.design_path),
                    "runtime_sha256": self.state["runtime_sha256"],
                    "checks": {"resume": "PASS", "reload": "PASS", "stage_transition": "PASS"},
                    "shape_checks": pin(self.root, self.base / "shape-checks.json"),
                    "runs": self.state["smoke_runs"],
                    "projection_seconds": projections,
                    "elapsed_seconds": time.time() - self.state["smoke_started_at"],
                    "recovery_authorization": self.recovery_authorization,
                    "recovery_extension": self.state["recovery_extension"],
                    "completed_smoke_reused": True,
                    "smoke_training_repeated": False,
                },
            )
        self.sync()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--storage", type=Path, required=True)
    parser.add_argument("--gpu-started-at", type=float, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--prior-process-stopped", action="store_true")
    parser.add_argument("--recovery-authorization", type=Path, required=True)
    parser.add_argument("--recovery-authorization-sha256", required=True)
    args = parser.parse_args()
    if not args.resume or not args.prior_process_stopped:
        raise DataContractError("This extension only continues a stopped original campaign")
    auth = authorize(args.recovery_authorization, args.recovery_authorization_sha256, args.storage)
    if (
        code_identity()["sha256"] != auth["code_sha256"]
        or pin(args.workspace, args.design) != auth["design"]
        or args.gpu_started_at != auth["started_at"]
    ):
        raise DataContractError("Original trainer/design/clock must remain unchanged")
    # Archive and authorization are already SHA checked by the thin notebook worker.
    destination = (
        args.workspace / "configs/experiments/E009-V15-20261106/recovery-authorization.json"
    )
    payload = args.recovery_authorization.read_bytes()
    if destination.exists() and destination.read_bytes() != payload:
        raise DataContractError("Recovery authorization cannot be overwritten")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    campaign = RecoveryCampaign(
        args.design,
        args.workspace,
        args.storage,
        args.gpu_started_at,
        resume=True,
        prior_process_stopped=True,
    )
    campaign.recovery_auth = auth
    campaign.recovery_authorization = pin(args.workspace, destination)
    campaign.original_budget = dict(campaign.budget)
    campaign.budget = revised_budget(campaign.budget)
    campaign.state["recovery_extension"] = {
        "sha256": auth["extension_sha256"],
        "authorization_sha256": args.recovery_authorization_sha256,
    }
    campaign.state["effective_budget"] = campaign.budget
    campaign.state.pop("error", None)
    print(
        "E009 approved recovery: reuse six smoke runs; 45 min/run; original clock preserved.",
        flush=True,
    )
    campaign.run()


if __name__ == "__main__":
    main()
