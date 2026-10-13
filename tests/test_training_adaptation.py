from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import torch
    from fixtures.adaptation_fixture import approve, fixture, pin

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.training import holdout_access
    from ai_exam_monitoring.training.adaptation_config import (
        config_from_dict,
        verify_adaptation_approval,
        verify_matched_configs,
    )
    from ai_exam_monitoring.training.adaptation_data import prepare_cohorts
    from ai_exam_monitoring.training.adaptation_evaluate import (
        benchmark,
        evaluate_adaptation,
        load_bundle,
    )
    from ai_exam_monitoring.training.adaptation_metrics import (
        group_bootstrap,
        minibatch_loss,
        report_scores,
        slice_reports,
    )
    from ai_exam_monitoring.training.adaptation_model import AdaptationModel, tensor_digest
    from ai_exam_monitoring.training.adaptation_train import infer, train_images
    from ai_exam_monitoring.training.artifacts import code_identity, digest_json, write_json
    from ai_exam_monitoring.training.config import load_config
    from ai_exam_monitoring.training.metrics import masked_loss
    from ai_exam_monitoring.training.model import FrozenEncoder
    from ai_exam_monitoring.training.train import run


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class AdaptationMetricTests(unittest.TestCase):
    def test_minibatch_loss_and_gradient_equal_full_objective_with_missing_targets_and_tail(self):
        values = torch.tensor(
            [
                [1.0, float("nan")],
                [0.0, float("nan")],
                [1.0, 0.0],
                [float("nan"), 1.0],
                [float("nan"), 0.0],
            ]
        )
        mask = torch.isfinite(values)
        full = torch.randn(5, 2, requires_grad=True)
        batched = full.detach().clone().requires_grad_()
        expected = masked_loss(full, values, mask)
        expected.backward()
        losses = []
        for start in (0, 2, 4):
            section = slice(start, start + 2)
            losses.append(
                minibatch_loss(batched[section], values[section], mask[section], 5, mask.sum(0))
                * len(values[section])
                / 5
            )
        actual = sum(losses)
        actual.backward()
        self.assertAlmostEqual(float(actual.detach()), float(expected.detach()), places=6)
        self.assertTrue(torch.allclose(full.grad, batched.grad))
        self.assertTrue(torch.equal(batched.grad[~mask], torch.zeros_like(batched.grad[~mask])))

    def test_invalid_support_uu_and_nonfinite_fail(self):
        for mask, counts in (
            (torch.ones(2, 2, dtype=torch.bool), torch.tensor([0, 2])),
            (torch.tensor([[False, False], [True, True]]), torch.tensor([1, 1])),
        ):
            with self.assertRaises(DataContractError):
                minibatch_loss(torch.zeros(2, 2), torch.zeros(2, 2), mask, 2, counts)
        with self.assertRaises(DataContractError):
            minibatch_loss(
                torch.full((2, 2), float("nan")),
                torch.zeros(2, 2),
                torch.ones(2, 2, dtype=torch.bool),
                2,
                torch.tensor([2, 2]),
            )

    def test_fpr_constant_and_slice_support_are_explicit(self):
        values = torch.tensor([[1.0, 0.0], [0.0, 1.0], [0.0, 0.0], [1.0, 1.0]])
        mask = torch.ones(4, 2, dtype=torch.bool)
        logits = torch.tensor([[2.0, -2.0], [2.0, 2.0], [-2.0, 2.0], [-2.0, 2.0]])
        metrics = report_scores(logits, values, mask, 0.5, torch.tensor([0.5, 0.5]))
        self.assertEqual(metrics["targets"]["phone_use"]["fpr"], 0.5)
        self.assertAlmostEqual(metrics["constant_train_prevalence"]["macro_masked_bce"], 0.69314718)
        slices = slice_reports(
            logits,
            values,
            mask,
            ["a", "b", "c", "d"],
            ["g1", "g1", "g2", "g2"],
            {"positive-only": ["a", "d"]},
            0.5,
            torch.tensor([0.5, 0.5]),
        )
        self.assertEqual(
            slices["positive-only"]["targets"]["phone_use"]["support_status"], "INCONCLUSIVE"
        )
        self.assertIsNone(slices["positive-only"]["targets"]["phone_use"]["fpr"])

    def test_bootstrap_reproducible_whole_groups_and_invalid_denominators(self):
        values = torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
        mask = torch.ones(4, 2, dtype=torch.bool)
        scores = values.clone()
        groups = ["A", "A", "B", "B"]
        a = group_bootstrap(scores, values, mask, groups, 0.5)
        b = group_bootstrap(scores, values, mask, groups, 0.5)
        self.assertEqual(a, b)
        self.assertEqual(a["groups"], 2)
        self.assertEqual(a["targets"]["phone_use"]["recall"]["interval"], [1.0, 1.0])
        z = group_bootstrap(torch.zeros_like(scores), values, mask, groups, 0.5)
        self.assertIsNone(z["targets"]["phone_use"]["precision"]["interval"])
        self.assertEqual(z["targets"]["phone_use"]["precision"]["valid_resamples"], 0)


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class AdaptationTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config, self.rows = fixture(self.root)

    def model(self, config=None):
        c = config or self.config
        return AdaptationModel(
            c,
            weights=c.weights.verify(self.root),
            initial_head=c.head_initialization.verify(self.root),
        )

    def rewrite_protocol(self, protocol):
        write_json(self.root / "protocol.json", protocol)
        ready = json.loads((self.root / "readiness.json").read_text())
        ready["protocol_sha256"] = pin(self.root, self.root / "protocol.json").sha256
        write_json(self.root / "readiness.json", ready)
        return replace(
            self.config,
            protocol=pin(self.root, self.root / "protocol.json"),
            readiness=pin(self.root, self.root / "readiness.json"),
        )

    def test_strict_config_approval_matching_and_legacy(self):
        raw = self.config.to_dict()
        self.assertEqual(config_from_dict(raw), self.config)
        for changes in (
            {"extra": 0},
            {"batch_size": True},
            {"wall_time_seconds": None},
            {"head_learning_rate": float("nan")},
            {"model": "other"},
            {"target_order": ["looking_around", "phone_use"]},
            {"workers": 1},
        ):
            with self.subTest(changes=changes), self.assertRaises(ConfigurationError):
                config_from_dict({**raw, **changes})
        verify_adaptation_approval(self.config, self.root)
        with self.assertRaises(ConfigurationError):
            verify_adaptation_approval(replace(self.config, batch_size=2), self.root)
        control = replace(self.config, model="resnet18_matched_control", experiment_id="control")
        verify_matched_configs(control, self.config)
        with self.assertRaises(ConfigurationError):
            verify_matched_configs(replace(control, seed=1), self.config)
        for name in ("E001", "E002", "E003"):
            self.assertEqual(
                load_config(Path("configs/experiments") / (name + ".yaml")).model,
                "resnet18_frozen_linear",
            )

    def test_whole_family_reserve_and_record_pins_fail_closed(self):
        cohorts, original = prepare_cohorts(self.config, self.root)
        self.assertEqual([len(c.ids) for c in cohorts], [6, 4, 2])
        for kind in ("family_leak", "holdout", "not_independent", "record_pin"):
            protocol = copy.deepcopy(original)
            if kind == "family_leak":
                protocol["family_assignments"]["SYNTHETIC-06"]["family_id"] = "synthetic-group-0"
            elif kind == "holdout":
                protocol["reserved_holdout"]["family_ids"] = ["synthetic-group-0"]
            elif kind == "not_independent":
                protocol["family_assignments"]["SYNTHETIC-06"]["independence_verified"] = False
            else:
                protocol["cohorts"]["development"]["records_sha256"] = "0" * 64
            with self.subTest(kind=kind), self.assertRaises(DataContractError):
                prepare_cohorts(self.rewrite_protocol(protocol), self.root)

    def test_v2_explicit_waiver_preserves_leakage_and_owner_guards(self):
        _, protocol = prepare_cohorts(self.config, self.root)
        approval = {"status": "approved", "owner": self.config.owner,
                    "waive_independence": True, "waive_support_shortfalls": True,
                    "final_test_inference_authorized": False}
        write_json(self.root / "waiver.json", approval)
        waiver = {"path": "waiver.json", "sha256": pin(self.root, self.root / "waiver.json").sha256}
        protocol.update(schema_version="matched-protocol-v2", waiver_approval=waiver,
                        independence_claim=False, final_test_inference_authorized=False,
                        M4_status="INCONCLUSIVE")
        for value in protocol["family_assignments"].values():
            value["independence_verified"] = False
        config = self.rewrite_protocol(protocol)
        ready = json.loads((self.root / "readiness.json").read_text())
        ready.update(schema_version="adaptation-readiness-v2", waiver_approval=waiver,
                     scope="promotion", gates={"G0": True, "G1": True,
                                               "G2": "owner_waived", "G3": "owner_waived"})
        write_json(self.root / "readiness.json", ready)
        config = replace(config, run_kind="promotion",
                         readiness=pin(self.root, self.root / "readiness.json"))
        cohorts, _ = prepare_cohorts(config, self.root)
        self.assertEqual(len(cohorts[1].ids), 4)
        for field, value in (("owner", "another-owner"), ("waive_independence", False),
                             ("final_test_inference_authorized", True)):
            write_json(self.root / "waiver.json", {**approval, field: value})
            with self.assertRaises((DataContractError, ConfigurationError)):
                prepare_cohorts(config, self.root)
        write_json(self.root / "waiver.json", approval)
        ready["gates"]["G2"] = True
        write_json(self.root / "readiness.json", ready)
        with self.assertRaises(DataContractError):
            prepare_cohorts(
                replace(config, readiness=pin(self.root, self.root / "readiness.json")),
                self.root,
            )

    def test_actual_step_only_updates_head_layer4_and_preserves_all_bn_buffers(self):
        for policy in ("resnet18_layer4", "resnet18_matched_control"):
            c = replace(self.config, model=policy)
            model = self.model(c)
            before = {k: v.clone() for k, v in model.state_dict().items()}
            groups, names = model.parameter_groups(c)
            optimizer = torch.optim.AdamW(groups)
            model.train()
            logits = model(torch.randn(3, 3, 32, 32))
            loss = masked_loss(
                logits,
                torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]),
                torch.ones(3, 2, dtype=torch.bool),
            )
            loss.backward()
            for name, param in model.named_parameters():
                if param.requires_grad:
                    self.assertIsNotNone(param.grad, name)
                    self.assertTrue(torch.isfinite(param.grad).all(), name)
                else:
                    self.assertIsNone(param.grad, name)
            optimizer.step()
            changed = []
            for name, value in model.state_dict().items():
                if not torch.equal(before[name], value):
                    changed.append(name)
            self.assertTrue(any(n.startswith("network.fc.") for n in changed))
            self.assertTrue(
                all(
                    n.startswith("network.fc.")
                    or (
                        policy == "resnet18_layer4"
                        and n.startswith("network.layer4.")
                        and not any(
                            s in n for s in ("running_mean", "running_var", "num_batches_tracked")
                        )
                    )
                    for n in changed
                )
            )
            self.assertEqual(bool(names["layer4"]), policy == "resnet18_layer4")
            if policy == "resnet18_layer4":
                self.assertTrue(any(n.startswith("network.layer4.") for n in changed))

    def test_control_logits_equal_frozen_features_with_same_head(self):
        control = self.model(replace(self.config, model="resnet18_matched_control"))
        encoder = FrozenEncoder(self.config.weights.verify(self.root), self.config.weights.sha256)
        inputs = torch.randn(3, 3, 32, 32)
        with torch.no_grad():
            self.assertTrue(torch.equal(control(inputs), control.network.fc(encoder(inputs))))
        self.assertEqual(
            tensor_digest(control.network.fc.state_dict()),
            tensor_digest(self.model().network.fc.state_dict()),
        )

    def test_epoch_resume_matches_weights_optimizer_rng_order_and_best(self):
        cohorts, _ = prepare_cohorts(self.config, self.root)
        train, selection = cohorts[:2]
        full = self.root / "full"
        other = self.root / "interrupted"
        full.mkdir()
        other.mkdir()
        torch.manual_seed(42)
        expected = train_images(self.model(), train, selection, self.config, full, "identity")
        torch.manual_seed(42)
        with self.assertRaises(KeyboardInterrupt):
            train_images(
                self.model(), train, selection, self.config, other, "identity", interrupt_after=1
            )
        with self.assertRaises(DataContractError):
            train_images(self.model(), train, selection, self.config, other, "changed", resume=True)
        actual = train_images(
            self.model(), train, selection, self.config, other, "identity", resume=True
        )
        self.assertEqual(expected["history"], actual["history"])
        self.assertEqual(expected["best_epoch"], actual["best_epoch"])
        a = torch.load(full / "last.pt", weights_only=True)
        b = torch.load(other / "last.pt", weights_only=True)
        self.assertEqual(tensor_digest(a["model"]), tensor_digest(b["model"]))
        self.assertTrue(torch.equal(a["sampler_rng"], b["sampler_rng"]))
        self.assertEqual(a["sampler_permutation"], b["sampler_permutation"])
        self.assertEqual(a["rng"]["python"], b["rng"]["python"])
        self.assertEqual(a["rng"]["numpy"], b["rng"]["numpy"])
        self.assertTrue(torch.equal(a["rng"]["torch"], b["rng"]["torch"]))
        for key, state in a["optimizer"]["state"].items():
            for field, value in state.items():
                self.assertTrue(torch.equal(value, b["optimizer"]["state"][key][field]))

    def test_canonical_run_standalone_fresh_process_reload_and_evaluator_parity(self):
        output = self.root / "outputs/run"
        record = run(self.root / "config.yaml", output, self.root)
        self.assertEqual(record.status, "FINISHED")
        (self.root / "synthetic-weights.pt").unlink()
        (self.root / "head.pt").unlink()
        model, bundle = load_bundle(output, self.root)
        cohorts, _ = prepare_cohorts(self.config, self.root)
        scores = infer(model, cohorts[1], self.config).sigmoid().tolist()
        expected = json.loads((output / "predictions-development.json").read_text())
        self.assertEqual(scores, [r["scores"] for r in expected])
        metrics = evaluate_adaptation(output, self.root / "outputs/eval", self.root, "val")
        self.assertEqual(
            metrics["development"], json.loads((output / "metrics.json").read_text())["development"]
        )
        code = (
            "from pathlib import Path; "
            "from ai_exam_monitoring.training.adaptation_evaluate import load_bundle; "
            "from ai_exam_monitoring.training.adaptation_model import tensor_digest; "
            "import sys; m,b=load_bundle(Path(sys.argv[1]),Path(sys.argv[2])); "
            "print(tensor_digest(m.state_dict()))"
        )
        result = subprocess.run(
            [sys.executable, "-c", code, str(output), str(self.root)],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), bundle["model_tensor_sha256"])

    def test_budget_interrupts_without_changing_config_and_missing_approval_before_output(self):
        cohorts, _ = prepare_cohorts(self.config, self.root)
        output = self.root / "budget"
        output.mkdir()
        with self.assertRaises(TimeoutError):
            train_images(
                self.model(), *cohorts[:2], self.config, output, "identity", remaining_seconds=0
            )
        state = torch.load(output / "last.pt", weights_only=True)
        self.assertEqual(state["epoch"], 0)
        self.assertEqual(state["config"], self.config.to_dict())
        write_json(self.root / "approval.json", {})
        with self.assertRaises(ConfigurationError):
            run(self.root / "config.yaml", self.root / "outputs/denied", self.root)
        self.assertFalse((self.root / "outputs/denied").exists())

    def test_canonical_resume_and_checkpoint_tampering_guard(self):
        output = self.root / "outputs/recovery"
        with self.assertRaises(KeyboardInterrupt):
            run(self.root / "config.yaml", output, self.root, interrupt_after=1)
        receipt = json.loads((output / "run.json").read_text())
        self.assertEqual(receipt["status"], "INTERRUPTED")
        self.assertEqual(receipt["completed_epochs"], 1)
        record = run(self.root / "config.yaml", output, self.root, resume=True)
        self.assertEqual(record.status, "FINISHED")
        self.assertEqual(record.completed_epochs, 2)
        with self.assertRaises(DataContractError):
            run(self.root / "config.yaml", output, self.root, resume=True)
        with (output / "best.pt").open("ab") as handle:
            handle.write(b"tampered")
        with self.assertRaises(DataContractError):
            load_bundle(output, self.root)

    def test_benchmark_timing_encloses_decode_transform_forward_and_excludes_hash(self):
        config = replace(self.config, threads=4)
        cohorts, _ = prepare_cohorts(self.config, self.root)
        paths = cohorts[1].paths
        events = []

        def tick():
            events.append("timer")
            return len(events) / 1000

        def decode(path, cfg):
            self.assertIn(path, paths)
            self.assertEqual(cfg, config)
            events.append("decode_transform")
            return torch.zeros(3, 32, 32)

        class SyntheticModel:
            def eval(inner):
                events.append("eval")

            def __call__(inner, batch):
                self.assertEqual(tuple(batch.shape), (1, 3, 32, 32))
                events.append("forward")
                return torch.zeros(1, 2)

        module = "ai_exam_monitoring.training.adaptation_evaluate."
        with (
            patch(module + "time.perf_counter", side_effect=tick),
            patch(module + "image_tensor", side_effect=decode),
            patch(module + "sha256_file", side_effect=lambda p: events.append("hash") or "0" * 64),
        ):
            report = benchmark(SyntheticModel(), paths, config)
        self.assertEqual(events[: len(paths)], ["hash"] * len(paths))
        self.assertEqual(
            events[len(paths) + 1 :], ["timer", "decode_transform", "forward", "timer"] * 510
        )
        self.assertEqual(len(report["samples_ms"]), 500)
        self.assertEqual(report["threads"], 4)
        self.assertEqual(report["batch_size"], 1)
        with self.assertRaises(DataContractError):
            benchmark(SyntheticModel(), paths, self.config)

    def test_test_access_denied_before_model_or_media_for_missing_protocol(self):
        output = self.root / "outputs/run"
        output.mkdir(parents=True)
        write_json(output / "resolved-config.json", self.config.to_dict())
        module = "ai_exam_monitoring.training.adaptation_evaluate."
        with patch(module + "load_bundle") as model, patch(module + "crop_path") as crop:
            with self.assertRaises(DataContractError):
                evaluate_adaptation(output, self.root / "outputs/test", self.root, "test")
            model.assert_not_called()
            crop.assert_not_called()
        self.assertFalse((self.root / "outputs/test").exists())

    def test_final_reserves_before_model_and_failure_blocks_new_output(self):
        config = replace(self.config, run_kind="promotion")
        approve(self.root, config)
        output = self.root / "outputs/run"
        output.mkdir(parents=True)
        write_json(output / "resolved-config.json", config.to_dict())
        write_json(output / "bundle.json", {"checkpoint_sha256": "a" * 64})
        data = config.to_dict()["cohorts"][0]["data"]
        protocol = self.root / "final.json"
        write_json(
            protocol,
            {
                "schema_version": "final-adaptation-protocol-v1",
                "status": "approved",
                "owner": config.owner,
                "experiment_id": config.experiment_id,
                "config_sha256": digest_json(config.to_dict()),
                "code_sha256": code_identity()["sha256"],
                "checkpoint_sha256": "a" * 64,
                "threshold": config.threshold,
                "target_order": config.target_order,
                "candidate_count": 1,
                "decision_ref": "synthetic-test-only",
                "data": data,
            },
        )

        def fail_model(*args):
            self.assertEqual(
                holdout_access.history(self.root, data["payload_sha256"])[0]["status"], "reserved"
            )
            raise RuntimeError("synthetic failure before inference")

        module = "ai_exam_monitoring.training.adaptation_evaluate."
        with (
            patch(module + "load_bundle", side_effect=fail_model),
            patch(module + "crop_path") as crop,
        ):
            with self.assertRaises(RuntimeError):
                evaluate_adaptation(output, self.root / "outputs/test", self.root, "test", protocol)
            crop.assert_not_called()
        self.assertEqual(
            holdout_access.history(self.root, data["payload_sha256"])[-1]["status"], "failed"
        )
        with patch(module + "load_bundle") as model:
            with self.assertRaises(DataContractError):
                evaluate_adaptation(
                    output, self.root / "outputs/other", self.root, "test", protocol
                )
            model.assert_not_called()


if __name__ == "__main__":
    unittest.main()
