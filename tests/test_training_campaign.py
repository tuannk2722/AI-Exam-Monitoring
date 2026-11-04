from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    from ai_exam_monitoring.training.adaptation_config import E005AdaptationConfig
    from ai_exam_monitoring.training.adaptation_train import _compute_epoch_lrs
    from ai_exam_monitoring.training.campaign import execute, rank_key, report, verify_parity
    from ai_exam_monitoring.training.campaign_prepare import pin
    from ai_exam_monitoring.training.evaluate import evaluate


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class CampaignTests(unittest.TestCase):
    def test_pin_resolves_relative_path(self) -> None:
        path = Path(__file__).resolve()
        root = Path.cwd().resolve()
        relative = path.relative_to(root)
        self.assertEqual(pin(root, path), pin(root, relative))

    def test_pin_preserves_actual_windows_receipt_bytes(self) -> None:
        import hashlib

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "smoke.json"
            payload = b'{\r\n  "status": "PASS"\r\n}\r\n'
            path.write_bytes(payload)
            self.assertEqual(pin(root, path)["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertNotEqual(
                pin(root, path)["sha256"],
                hashlib.sha256(payload.replace(b"\r\n", b"\n")).hexdigest(),
            )

    def test_cli_dispatches_v3_to_adaptation_evaluator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "resolved-config.json").write_text(
                '{"schema_version": "matched-adaptation-v3"}')
            with patch(
                "ai_exam_monitoring.training.adaptation_evaluate.evaluate_adaptation",
                return_value={"verified": True},
            ) as delegated:
                self.assertEqual(evaluate(root, root / "out", root, "val"), {"verified": True})
                delegated.assert_called_once()

    def test_frozen_schedule_matches_finetuning_head(self) -> None:
        args: dict[str, Any] = dict(
            warmup_epochs=3, lr_scheduler="cosine", max_epochs=12,
            min_lr_ratio=0.1, head_learning_rate=0.0003, layer4_learning_rate=0.00003,
        )
        frozen = cast(E005AdaptationConfig, SimpleNamespace(trainable_scope="head_only", **args))
        tuned = cast(E005AdaptationConfig, SimpleNamespace(
            trainable_scope="head_and_layer4_block1", **args))
        for epoch in range(1, 13):
            self.assertEqual(_compute_epoch_lrs(frozen, epoch)[0],
                             _compute_epoch_lrs(tuned, epoch)[0])
            self.assertEqual(_compute_epoch_lrs(frozen, epoch)[1], 0)

    def test_gate_rank_and_parity_failure(self) -> None:
        def metrics(passed: bool, ap: float) -> dict[str, Any]:
            return {"calibrated_evaluation": {"v11_all_targets_pass_gates": passed},
                    "macro_ap": ap, "macro_masked_bce": 0.4}
        self.assertGreater(rank_key(metrics(True, 0.7)), rank_key(metrics(False, 0.9)))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("run", "eval"):
                (root / name).mkdir()
                (root / name / "metrics.json").write_text('{"selection": {}}')
                (root / name / "predictions-selection.json").write_text("[]")
            verify_parity(root / "run", root / "eval")
            (root / "eval" / "predictions-selection.json").write_text("[1]")
            with self.assertRaisesRegex(ValueError, "predictions"):
                verify_parity(root / "run", root / "eval")

    def test_failed_smoke_stops_queue_and_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = {"code_sha256": "abc", "evidence_pins": [], "report_dir": "report",
                    "smoke": {}, "smoke_result": "result.json", "screening": [{}]}
            path = root / "plan.json"
            path.write_text(json.dumps(plan))
            with patch("ai_exam_monitoring.training.campaign.code_identity",
                       return_value={"sha256": "abc"}), patch(
                           "ai_exam_monitoring.training.campaign.run_one",
                           side_effect=ValueError("integrity failed")) as run:
                with self.assertRaisesRegex(ValueError, "integrity"):
                    execute(path, root)
                run.assert_called_once()
            state = json.loads((root / "report/campaign-state.json").read_text())
            self.assertEqual(state["status"], "FAILED")
            self.assertFalse((root / "result.json").exists())
            self.assertIn(
                "integrity failed", (root / "report/machine-summary.md").read_text("utf-8"))
            self.assertFalse((root / "report/README.md").exists())

    def test_complete_report_aggregates_seeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metrics = {"macro_ap": 0.7, "macro_masked_bce": 0.4, "targets": {},
                       "calibrated_evaluation": {"v11_all_targets_pass_gates": False,
                                                 "targets": {}}}
            rows = [{"id": f"run-{s}", "recipe": "S1", "seed": s, "best_epoch": 4,
                     "metrics": metrics} for s in (1, 2, 3)]
            report(root, {"report_dir": "report"}, {"status": "FINISHED", "completed": rows})
            summary = json.loads((root / "report/summary.json").read_text())
            self.assertEqual(summary["recommended_recipe"], "S1")
            self.assertEqual(summary["recipes"][0]["std_macro_ap"], 0)

    def test_automatic_selection_runs_only_two_confirmations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def item(recipe: str, seed: int = 1) -> dict[str, Any]:
                return {"id": f"{recipe}-{seed}", "recipe": recipe, "seed": seed}
            plan = {
                "code_sha256": "abc", "evidence_pins": [], "report_dir": "report",
                "smoke": item("SMOKE"), "smoke_result": "result.json",
                "screening": [item(r) for r in ("LP", "A", "B", "C", "D")],
                "repeat_recipes": ["A", "B", "C", "D"],
                "confirmation": [item(r, s) for r in ("A", "B", "C", "D") for s in (2, 3)],
            }
            path = root / "plan.json"
            path.write_text(json.dumps(plan))
            smoke = root / "outputs/SMOKE-1"
            smoke.mkdir(parents=True)
            (smoke / "history.json").write_text(json.dumps([
                {"stage": "warmup_head_only"}, {"stage": "finetune_layer4_block1"}]))
            def fake_run(
                workspace: Path, entry: dict[str, Any], logs: Path, interrupt: bool = False,
            ) -> dict[str, Any]:
                return {**entry, "best_epoch": 1, "metrics": {
                    "macro_ap": {"A": 0.9, "B": 0.8}.get(entry["recipe"], 0.5),
                    "macro_masked_bce": 0.5, "targets": {},
                    "calibrated_evaluation": {"v11_all_targets_pass_gates": False, "targets": {}},
                }}
            with patch("ai_exam_monitoring.training.campaign.code_identity",
                       return_value={"sha256": "abc"}), patch(
                           "ai_exam_monitoring.training.campaign.run_one",
                           side_effect=fake_run) as run:
                execute(path, root)
                self.assertEqual(run.call_count, 10)
            state = json.loads((root / "report/campaign-state.json").read_text())
            self.assertEqual(state["status"], "FINISHED")
            self.assertEqual([r["id"] for r in state["completed"]][-4:],
                             ["A-2", "A-3", "B-2", "B-3"])


if __name__ == "__main__":
    unittest.main()
