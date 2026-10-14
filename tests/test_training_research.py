from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import torch
    from fixtures.adaptation_fixture import fixture, pin

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.training.adaptation_config import (
        ResearchAdaptationConfig,
        config_from_dict,
        verify_adaptation_approval,
    )
    from ai_exam_monitoring.training.adaptation_data import prepare_cohorts
    from ai_exam_monitoring.training.adaptation_evaluate import evaluate_adaptation, load_bundle
    from ai_exam_monitoring.training.adaptation_model import (
        AdaptationModel,
        create_learned_head,
        tensor_digest,
    )
    from ai_exam_monitoring.training.adaptation_train import early_diagnostic, train_images
    from ai_exam_monitoring.training.artifacts import code_identity, digest_json, save_checkpoint
    from ai_exam_monitoring.training.train import restore_rng, rng_state, run


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class ResearchTrainingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base, _ = fixture(self.root)
        torch.set_num_threads(1)
        self.cohorts, _ = prepare_cohorts(self.base, self.root)

    def model(self, config=None):
        c = config or self.base
        return AdaptationModel(c, weights=c.weights.verify(self.root),
                               initial_head=c.head_initialization.verify(self.root))

    def research(self, *, steps=(1,), warm=False):
        raw = self.base.to_dict()
        raw.update(schema_version="matched-adaptation-v2", diagnostic_steps=list(steps),
                   head_provenance={"kind": "random_seed", "seed": 42,
                                    "parent_checkpoint": None, "parent_epoch": None})
        if warm:
            parent_model = self.model()
            with torch.no_grad():
                parent_model.network.fc.weight.add_(0.3)
                parent_model.network.layer4[0].conv1.weight.add_(5)
            parent_config = self.base.to_dict()
            parent_config["model"] = "resnet18_matched_control"
            state = parent_model.state_dict()
            save_checkpoint(self.root / "parent.pt", {
                "schema_version": "full-model-bundle-v1", "epoch": 10,
                "config": parent_config, "model": state,
                "model_tensor_sha256": tensor_digest(state),
            })
            source = pin(self.root, self.root / "parent.pt")
            create_learned_head(self.root / "learned.pt", source, self.root, 10)
            raw["head_initialization"] = {"path": "learned.pt",
                                          "sha256": pin(self.root, self.root / "learned.pt").sha256}
            raw["head_provenance"] = {"kind": "parent_fc", "seed": None,
                                      "parent_checkpoint": {"path": source.path,
                                                            "sha256": source.sha256},
                                      "parent_epoch": 10}
        result = config_from_dict(raw)
        self.assertIsInstance(result, ResearchAdaptationConfig)
        return result

    def approve(self, c):
        import yaml

        authorization = self.root / "owner.json"
        authorization.write_text(json.dumps({"status": "approved", "owner": c.owner,
                                             "final_test_inference_authorized": False}))
        approval = {"status": "approved", "owner": c.owner,
                    "scope": "local_classifier_research", "run_kind": c.run_kind,
                    "configs": {c.experiment_id: digest_json(c.to_dict())},
                    "config_signatures": {c.experiment_id: c.match_signature()},
                    "code_sha256": code_identity()["sha256"],
                    "final_test_inference_authorized": False,
                    "owner_authorization": {"path": "owner.json",
                                            "sha256": pin(self.root, authorization).sha256}}
        (self.root / c.approval_ref).write_text(json.dumps(approval))
        (self.root / "config.yaml").write_text(yaml.safe_dump(c.to_dict()))
        return approval

    def test_warm_head_exact_extraction_backbone_reset_and_provenance_rejection(self):
        c = self.research(warm=True)
        model = self.model(c)
        parent = torch.load(self.root / "parent.pt", weights_only=True)["model"]
        original = self.model().state_dict()
        for name, value in model.state_dict().items():
            self.assertTrue(torch.equal(value, parent[name] if name.startswith("network.fc.")
                                        else original[name]), name)
        groups, _ = model.parameter_groups(c)
        self.assertEqual(len(torch.optim.AdamW(groups).state), 0)
        with self.assertRaises(DataContractError):
            create_learned_head(self.root / "wrong.pt", pin(self.root, self.root / "parent.pt"),
                                self.root, 9)
        raw = c.to_dict()
        raw["head_provenance"]["parent_epoch"] = 9
        with self.assertRaises(DataContractError):
            self.model(config_from_dict(raw))
        payload = torch.load(self.root / "learned.pt", weights_only=True)
        payload["head"]["weight"][0, 0] = float("nan")
        save_checkpoint(self.root / "bad.pt", payload)
        raw = c.to_dict()
        raw["head_initialization"] = {"path": "bad.pt",
                                      "sha256": pin(self.root, self.root / "bad.pt").sha256}
        with self.assertRaises(DataContractError):
            self.model(config_from_dict(raw))

    def test_strict_version_scope_and_exact_research_approval(self):
        self.assertEqual(config_from_dict(self.base.to_dict()).to_dict(), self.base.to_dict())
        c = self.research()
        for field, value in (("run_kind", "promotion"), ("diagnostic_steps", [2]),
                             ("diagnostic_steps", [1, 1])):
            raw = c.to_dict()
            raw[field] = value
            with self.assertRaises(ConfigurationError):
                config_from_dict(raw)
        approval = self.approve(c)
        verify_adaptation_approval(c, self.root)
        approval["code_sha256"] = "0" * 64
        (self.root / c.approval_ref).write_text(json.dumps(approval))
        with self.assertRaises(ConfigurationError):
            verify_adaptation_approval(c, self.root)

    def test_diagnostics_preserve_all_modes_rng_tensors_and_optimizer(self):
        model = self.model()
        model.train()
        state = tensor_digest(model.state_dict())
        modes = [m.training for m in model.modules()]
        saved = rng_state()
        optimizer = torch.optim.AdamW(model.parameter_groups(self.base)[0])
        before = copy.deepcopy(optimizer.state_dict())
        metrics = early_diagnostic(model, self.cohorts[:2], self.base)
        self.assertEqual(set(metrics), {c.name for c in self.cohorts[:2]})
        self.assertEqual(state, tensor_digest(model.state_dict()))
        self.assertEqual(modes, [m.training for m in model.modules()])
        actual = rng_state()
        self.assertEqual(saved["python"], actual["python"])
        self.assertEqual(saved["numpy"], actual["numpy"])
        self.assertTrue(torch.equal(saved["torch"], actual["torch"]))
        self.assertEqual(before, optimizer.state_dict())
        with patch("ai_exam_monitoring.training.adaptation_train.infer",
                   side_effect=DataContractError("fixture failure")):
            with self.assertRaises(DataContractError):
                early_diagnostic(model, self.cohorts[:2], self.base)
        self.assertEqual(modes, [m.training for m in model.modules()])

    def test_instrumentation_training_and_resume_parity(self):
        c = self.research()
        train, selection = self.cohorts[:2]
        outputs = [self.root / n for n in ("legacy", "research", "resumed")]
        for p in outputs:
            p.mkdir()
        saved = rng_state()
        expected = train_images(self.model(), train, selection, self.base, outputs[0], "identity")
        restore_rng(saved)
        actual = train_images(self.model(c), train, selection, c, outputs[1], "identity")
        self.assertEqual(expected["history"], actual["history"])
        self.assertEqual(expected["best_epoch"], actual["best_epoch"])
        restore_rng(saved)
        with self.assertRaises(KeyboardInterrupt):
            train_images(
                self.model(c), train, selection, c, outputs[2], "identity", interrupt_after=1
            )
        resumed = train_images(
            self.model(c), train, selection, c, outputs[2], "identity", resume=True
        )
        self.assertEqual(actual["history"], resumed["history"])
        for p in outputs[1:]:
            a = torch.load(outputs[0] / "last.pt", weights_only=True)
            b = torch.load(p / "last.pt", weights_only=True)
            self.assertEqual(tensor_digest(a["model"]), tensor_digest(b["model"]))
            self.assertTrue(torch.equal(a["sampler_rng"], b["sampler_rng"]))
            for key, state in a["optimizer"]["state"].items():
                for field, value in state.items():
                    self.assertTrue(torch.equal(value, b["optimizer"]["state"][key][field]))
        rows = json.loads((outputs[1] / "early-diagnostics.json").read_text())
        self.assertEqual([(r["epoch"], r["step"]) for r in rows], [(0, 0), (1, 1)])
        self.assertTrue(all(r["diagnostic_only"] for r in rows))

    def test_warm_canonical_reload_evaluation_and_closed_test(self):
        c = self.research(warm=True)
        self.approve(c)
        output = self.root / "outputs/warm"
        record = run(self.root / "config.yaml", output, self.root)
        self.assertEqual(record.status, "FINISHED")
        initial = json.loads((output / "initialization.json").read_text())
        self.assertEqual(initial["head_provenance"], c.to_dict()["head_provenance"])
        (self.root / "learned.pt").unlink()
        (self.root / "parent.pt").unlink()
        (self.root / "synthetic-weights.pt").unlink()
        load_bundle(output, self.root)
        metrics = evaluate_adaptation(output, self.root / "outputs/eval", self.root, "val")
        trained = json.loads((output / "metrics.json").read_text())
        self.assertEqual(
            metrics, {c.name: trained[c.name] for c in self.cohorts if c.role != "train"}
        )
        with self.assertRaises(DataContractError):
            evaluate_adaptation(output, self.root / "outputs/test", self.root, "test")

    def test_uncommitted_diagnostic_attempts_are_distinct_after_restart(self):
        c = self.research()
        output = self.root / "restart"
        output.mkdir()
        train, selection = self.cohorts[:2]
        actual_diagnostic = early_diagnostic
        calls = 0

        def interrupt(model, cohorts, config):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt("synthetic uncommitted epoch")
            return actual_diagnostic(model, cohorts, config)

        with patch("ai_exam_monitoring.training.adaptation_train.early_diagnostic", interrupt):
            with self.assertRaises(KeyboardInterrupt):
                train_images(self.model(c), train, selection, c, output, "identity")
        self.assertEqual(torch.load(output / "last.pt", weights_only=True)["epoch"], 0)
        train_images(self.model(c), train, selection, c, output, "identity", resume=True)
        rows = json.loads((output / "early-diagnostics.json").read_text())
        self.assertEqual([(r["attempt"], r["epoch"], r["step"]) for r in rows],
                         [(1, 0, 0), (2, 0, 0), (2, 1, 1)])


if __name__ == "__main__":
    unittest.main()
