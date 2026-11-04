from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from dataclasses import asdict, fields, replace
from pathlib import Path
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import test_e005_anchor_context
    import torch
    import yaml
    from fixtures.adaptation_fixture import pin

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.training.adaptation_config import (
        RepresentationConfig,
        config_from_dict,
    )
    from ai_exam_monitoring.training.adaptation_data import prepare_cohorts
    from ai_exam_monitoring.training.adaptation_evaluate import evaluate_adaptation
    from ai_exam_monitoring.training.adaptation_model import (
        AdaptationModel,
        create_e005_initial_head,
        tensor_digest,
    )
    from ai_exam_monitoring.training.adaptation_train import train_images
    from ai_exam_monitoring.training.artifacts import code_identity, digest_json, write_json
    from ai_exam_monitoring.training.calibration import calibrate_exact, evaluate_pair
    from ai_exam_monitoring.training.device import configure_device
    from ai_exam_monitoring.training.recovery import mirror_epoch, restore_epoch
    from ai_exam_monitoring.training.representation_campaign import champion_key
    from ai_exam_monitoring.training.train import run


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class ExactCalibrationTests(unittest.TestCase):
    def test_low_scores_ties_and_endpoints(self):
        scores = torch.tensor([[.04, 1.], [.03, 1.], [.02, 0.], [.01, 0.]])
        values = torch.tensor([[1., 1.], [1., 1.], [0., 0.], [0., 0.]])
        mask = torch.ones_like(values, dtype=torch.bool)
        thresholds = calibrate_exact(scores, values, mask)
        result = evaluate_pair(scores, values, mask, thresholds)
        for target in result["targets"].values():
            self.assertEqual((target["tp"], target["fp"]), (2, 0))
        self.assertLess(thresholds[0], .05)

    def test_unknowns_and_undefined_precision(self):
        scores = torch.tensor([[.9, .8], [.1, .2], [1., 1.]])
        values = torch.tensor([[1., 1.], [0., 0.], [0., 0.]])
        mask = torch.tensor([[True, True], [True, True], [False, False]])
        pair = calibrate_exact(scores, values, mask)
        result = evaluate_pair(scores, values, mask, pair)
        self.assertEqual(result["targets"]["phone_use"]["fp"], 0)
        none = evaluate_pair(scores[:2], values[:2], mask[:2], (1., 1.))
        self.assertIsNone(none["targets"]["phone_use"]["precision"])

    def test_saturated_all_negative_boundary_is_representable(self):
        import math

        scores = torch.ones(4, 2)
        values = torch.tensor([[1., 1.], [0., 0.], [0., 0.], [0., 0.]])
        mask = torch.ones_like(values, dtype=torch.bool)
        result = evaluate_pair(scores, values, mask, (math.nextafter(1., 2.),)*2)
        self.assertEqual(result["targets"]["phone_use"]["fp"], 0)
        self.assertIsNone(result["targets"]["phone_use"]["precision"])

    def test_champion_uses_support_gate_before_ap(self):
        def metrics(passed, ap):
            return {"macro_ap": ap, "macro_masked_bce": .3, "calibrated_evaluation": {
                "targets": {key: {"v11_quality_gate_pass": passed, "precision": .9,
                                  "recall": .9, "fpr": .1} for key in ("a", "b")}}}
        self.assertLess(champion_key("R0", metrics(True, .7)),
                        champion_key("D1", metrics(None, .99)))

    def test_recovery_restores_checked_atomic_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "run"
            source.mkdir()
            for name in ("last.pt", "initialization.json", "resolved-config.json",
                         "code-provenance.json", "environment.json"):
                (source / name).write_bytes(name.encode())
            mirror_epoch(source, root / "storage", {"status": "INTERRUPTED"})
            restore_epoch(root / "storage/run.tar", root / "restored")
            self.assertEqual((root / "restored/last.pt").read_bytes(), b"last.pt")
            with self.assertRaises(DataContractError):
                restore_epoch(root / "storage/run.tar", root / "restored")


if ML_AVAILABLE:
    class RepresentationFixtureTests(unittest.TestCase):
        def setUp(self):
            # Reuse fixture construction, not the inherited legacy test cases.
            self.helper = test_e005_anchor_context.E005AnchorContextTests()
            self.helper.setUp()
            self.addCleanup(self.helper.doCleanups)
            self.root = self.helper.root

        def config(self):
            base = self.helper.make_v3_config(model="resnet18_single_crop_v3", aug_enabled=True)
            authority = {
                "status": "approved", "owner": base.owner,
                "dataset_version": base.cohorts[0].data.dataset_version,
                "payload_sha256": base.cohorts[0].data.payload_sha256,
                "final_test_inference_authorized": False,
                "implementation_authorized": True, "smoke_authorized": True,
                "research_authorized_after_smoke": True,
            }
            write_json(self.root / "execution.json", authority)
            protocol = json.loads((self.root / "protocol.json").read_text())
            protocol["schema_version"] = "representation-protocol-v4"
            write_json(self.root / "protocol.json", protocol)
            raw = {f.name: getattr(base, f.name) for f in fields(base)}
            raw.update(schema_version="representation-adaptation-v4", run_kind="smoke",
                       encoder_source=None, precision="float32",
                       execution_authorization=pin(self.root, self.root / "execution.json"),
                       protocol=pin(self.root, self.root / "protocol.json"))
            config = RepresentationConfig(**raw)
            write_json(self.root / "readiness.json", {
                "schema_version": "representation-readiness-v4", "status": "approved",
                "owner": config.owner, "scope": "smoke", "independence_claim": False,
                "protocol_sha256": config.protocol.sha256,
                "cohorts_sha256": digest_json(config.to_dict()["cohorts"]),
                "execution_authorization": asdict(config.execution_authorization),
                "evidence_pins": [asdict(config.execution_authorization)],
            })
            config = replace(config, readiness=pin(self.root, self.root / "readiness.json"))
            write_json(self.root / config.approval_ref, {
                "status": "approved", "owner": config.owner, "scope": "local_classifier_research",
                "run_kind": "smoke", "code_sha256": code_identity()["sha256"],
                "final_test_inference_authorized": False,
                "owner_authorization": asdict(pin(self.root, self.root / "owner-auth.json")),
                "configs": {config.experiment_id: digest_json(config.to_dict())},
                "config_signatures": {config.experiment_id: config.match_signature()},
            })
            (self.root / "v4.yaml").write_text(yaml.safe_dump(config.to_dict()), encoding="utf-8")
            return config

        def test_schema_device_and_no_silent_fallback(self):
            config = self.config()
            self.assertEqual(config_from_dict(config.to_dict()), config)
            with self.assertRaises(ConfigurationError):
                replace(config, device="auto")
            with patch("torch.cuda.is_available", return_value=False):
                with self.assertRaises(DataContractError):
                    configure_device(replace(config, device="cuda"))

        def test_cache_changes_with_resolution(self):
            config = self.config()
            cohorts, _ = prepare_cohorts(config, self.root)
            first = cohorts[0].model_batch([0], config)
            larger = replace(config, image_size=config.image_size * 2)
            second = cohorts[0].model_batch([0], larger)
            self.assertEqual(second.shape[-1], first.shape[-1] * 2)

        def test_dino_freeze_transition_and_feature_dimension(self):
            class TinyDino(torch.nn.Module):
                def __init__(self):
                    super().__init__()
                    self.blocks = torch.nn.ModuleList([
                        torch.nn.Linear(384, 384) for _ in range(12)])
                    self.norm = torch.nn.LayerNorm(384)

                def prepare_tokens_with_masks(self, images):
                    return images.mean((1, 2, 3)).reshape(-1, 1, 1).expand(-1, 5, 384)

            config = self.config()
            backbone = TinyDino()
            weights = self.root / "dino.pt"
            torch.save(backbone.state_dict(), weights)
            head = self.root / "dino-head.pt"
            create_e005_initial_head(head, config.seed, in_dim=768,
                                     hidden_dim=config.head_hidden_dim,
                                     dropout=config.head_dropout)
            config = replace(config, model="dinov2_vits14_v4", weights_id="DINOv2_VITS14",
                             weights=pin(self.root, weights), image_size=28,
                             encoder_source=pin(self.root, weights),
                             head_initialization=pin(self.root, head),
                             trainable_scope="head_and_last_two_blocks")
            with patch("ai_exam_monitoring.training.encoders.load_dino_source",
                       return_value=backbone):
                model = AdaptationModel(config, weights=weights, initial_head=head,
                                        workspace=self.root)
            model.configure_trainable_stage(config, epoch=1)
            self.assertFalse(any(p.requires_grad for p in backbone.parameters()))
            model.configure_trainable_stage(config, epoch=config.warmup_epochs + 1)
            model(torch.randn(2, 3, 28, 28)).sum().backward()
            self.assertIsNone(backbone.blocks[9].weight.grad)
            self.assertIsNotNone(backbone.blocks[10].weight.grad)
            self.assertIsNotNone(backbone.norm.weight.grad)

        def test_full_run_reuses_val_calibration_and_reload(self):
            config = self.config()
            output = self.root / "outputs/run"
            record = run(self.root / "v4.yaml", output, self.root)
            self.assertEqual(record.status, "FINISHED")
            result = json.loads((output / "metrics.json").read_text())
            expected = result["development"]["calibrated_thresholds"]
            self.assertEqual(result["train"]["calibrated_thresholds"], expected)
            actual = evaluate_adaptation(output, self.root / "outputs/eval", self.root, "val")
            self.assertEqual(actual["development"], result["development"])
            self.assertEqual(config.device, "cpu")

        def test_resume_transition_matches_uninterrupted(self):
            config = self.config()
            cohorts, _ = prepare_cohorts(config, self.root)
            train, val = cohorts[:2]
            results = []
            for interrupted in (False, True):
                torch.manual_seed(config.seed)
                model = AdaptationModel(config, weights=config.weights.verify(self.root),
                                        initial_head=config.head_initialization.verify(self.root))
                folder = self.root / f"recovery-{interrupted}"
                folder.mkdir()
                if interrupted:
                    with self.assertRaises(KeyboardInterrupt):
                        train_images(model, train, val, config, folder, "fixture",
                                     interrupt_after=1)
                    torch.manual_seed(999)
                state = train_images(model, train, val, config, folder, "fixture",
                                     resume=interrupted)
                results.append((state["history"], tensor_digest(state["best_model"])))
            self.assertEqual(results[0], results[1])


if __name__ == "__main__":
    unittest.main()
