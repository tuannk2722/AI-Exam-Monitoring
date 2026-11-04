from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from dataclasses import asdict, fields, replace
from pathlib import Path

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import torch
    import yaml
    from fixtures.adaptation_fixture import fixture, pin
    from PIL import Image

    from ai_exam_monitoring.common.errors import ConfigurationError
    from ai_exam_monitoring.data.pilot_schema import PixelBox
    from ai_exam_monitoring.training.adaptation_config import (
        ADAPTATION_CONFIG_SCHEMA_V3,
        AdaptationAugmentationConfig,
        E005AdaptationConfig,
        config_from_dict,
        verify_adaptation_approval,
    )
    from ai_exam_monitoring.training.adaptation_data import prepare_cohorts
    from ai_exam_monitoring.training.adaptation_evaluate import load_bundle
    from ai_exam_monitoring.training.adaptation_metrics import (
        build_fp_fn_gallery,
        calibrate_optimal_thresholds,
        minibatch_loss,
    )
    from ai_exam_monitoring.training.adaptation_model import (
        AdaptationModel,
        create_e005_initial_head,
        head_input_dim,
        tensor_digest,
    )
    from ai_exam_monitoring.training.adaptation_train import infer
    from ai_exam_monitoring.training.artifacts import code_identity, digest_json, write_json
    from ai_exam_monitoring.training.data import (
        compute_relative_anchor_geometry,
        extract_anchor_subcrop,
    )
    from ai_exam_monitoring.training.evaluate import evaluate
    from ai_exam_monitoring.training.train import run


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class E005AnchorContextTests(unittest.TestCase):
    def setUp(self) -> None:
        torch.set_num_threads(1)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base_config, self.rows = fixture(self.root, epochs=3)

    def make_v3_config(
        self,
        *,
        model: str = "resnet18_anchor_context",
        trainable_scope: str = "head_and_layer4_block1",
        head_hidden_dim: int = 32,
        warmup_epochs: int = 1,
        aug_enabled: bool = True,
    ) -> E005AdaptationConfig:
        in_dim = 1542 if model == "resnet18_anchor_context" else 512
        head_path = self.root / f"head-{model}-{trainable_scope}-{head_hidden_dim}.pt"
        if not head_path.exists():
            create_e005_initial_head(
                head_path,
                self.base_config.seed,
                in_dim=in_dim,
                hidden_dim=head_hidden_dim,
                dropout=0.2 if head_hidden_dim > 0 else 0.0,
            )
        owner_auth_path = self.root / "owner-auth.json"
        write_json(
            owner_auth_path,
            {
                "status": "approved",
                "owner": self.base_config.owner,
                "final_test_inference_authorized": False,
            },
        )
        ready = json.loads((self.root / "readiness.json").read_text(encoding="utf-8"))
        ready["scope"] = "research"
        ready["gates"] = {"G0": True, "G1": True, "G2": True, "G3": True}
        write_json(self.root / "readiness.json", ready)
        aug = AdaptationAugmentationConfig(
            enabled=aug_enabled,
            horizontal_flip_prob=0.5,
            box_jitter_ratio=0.05 if model == "resnet18_anchor_context" else 0.0,
            brightness_jitter=0.15,
            contrast_jitter=0.15,
            saturation_jitter=0.10,
            random_erasing_prob=0.15,
        )
        base_dict = {f.name: getattr(self.base_config, f.name) for f in fields(self.base_config)}
        base_dict.update(
            schema_version=ADAPTATION_CONFIG_SCHEMA_V3,
            experiment_id="SYNTHETIC-E005",
            run_kind="research",
            model=model,
            readiness=pin(self.root, self.root / "readiness.json"),
            head_initialization=pin(self.root, head_path),
            transform=(
                "dual_roi_anchor_context_letterbox_v3"
                if model == "resnet18_anchor_context"
                else "rgb_letterbox_bilinear_v1"
            ),
            objective="balanced_smoothed_minibatch_bce_v3",
            checkpoint_policy="atomic_epoch_boundary_v3",
            trainable_scope=trainable_scope,
            head_hidden_dim=head_hidden_dim,
            head_dropout=0.2 if head_hidden_dim > 0 else 0.0,
            use_geometry_features=(model == "resnet18_anchor_context"),
            anchor_padding_ratio=0.05,
            warmup_epochs=warmup_epochs,
            lr_scheduler="cosine",
            min_lr_ratio=0.1,
            pos_weight=(1.13, 1.46),
            label_smoothing=0.05,
            selection_metric="val_macro_ap",
            calibrate_thresholds_on_val=True,
            augmentation=aug,
        )
        cfg = E005AdaptationConfig(**base_dict)
        write_json(
            self.root / cfg.approval_ref,
            {
                "status": "approved",
                "owner": cfg.owner,
                "scope": "local_classifier_research",
                "run_kind": cfg.run_kind,
                "code_sha256": code_identity()["sha256"],
                "final_test_inference_authorized": False,
                "owner_authorization": asdict(pin(self.root, owner_auth_path)),
                "config_signatures": {cfg.experiment_id: cfg.match_signature()},
                "configs": {cfg.experiment_id: digest_json(cfg.to_dict())},
            },
        )
        (self.root / "config-v3.yaml").write_text(
            yaml.safe_dump(cfg.to_dict()), encoding="utf-8"
        )
        return cfg

    def test_relative_geometry_and_anchor_subcrop(self) -> None:
        context_box = PixelBox(100, 50, 300, 250)
        person_box = PixelBox(150, 100, 250, 200)
        geom = compute_relative_anchor_geometry(person_box, context_box)
        self.assertEqual(geom, (0.25, 0.25, 0.75, 0.75, 0.5, 0.5))
        img = Image.new("RGB", (200, 200), (10, 20, 30))
        sub = extract_anchor_subcrop(img, person_box, context_box, padding_ratio=0.0)
        self.assertEqual(sub.size, (100, 100))
        sub_padded = extract_anchor_subcrop(img, person_box, context_box, padding_ratio=0.1)
        self.assertEqual(sub_padded.size, (120, 120))

    def test_v3_config_validation_and_roundtrip(self) -> None:
        cfg = self.make_v3_config()
        self.assertEqual(config_from_dict(cfg.to_dict()), cfg)
        verify_adaptation_approval(cfg, self.root)
        with self.assertRaises(ConfigurationError):
            replace(cfg, warmup_epochs=cfg.max_epochs)
        with self.assertRaises(ConfigurationError):
            replace(cfg, model="resnet18_single_crop_v3", use_geometry_features=True)

    def test_two_stage_unfreeze_and_layer4_block1_gradients(self) -> None:
        cfg = self.make_v3_config(
            model="resnet18_anchor_context",
            trainable_scope="head_and_layer4_block1",
            warmup_epochs=1,
        )
        self.assertEqual(head_input_dim(cfg), 1542)
        model = AdaptationModel(
            cfg,
            weights=cfg.weights.verify(self.root),
            initial_head=cfg.head_initialization.verify(self.root),
        )
        # Stage 1 (epoch 1 <= warmup_epochs): only head requires_grad
        stage1 = model.configure_trainable_stage(cfg, epoch=1)
        self.assertEqual(stage1, "warmup_head_only")
        self.assertFalse(any(p.requires_grad for p in model.network.layer4.parameters()))
        self.assertTrue(all(p.requires_grad for p in model.network.fc.parameters()))
        # Stage 2 (epoch 2 > warmup_epochs): head and layer4.1 require_grad, layer4.0 frozen
        stage2 = model.configure_trainable_stage(cfg, epoch=2)
        self.assertEqual(stage2, "finetune_layer4_block1")
        self.assertFalse(any(p.requires_grad for p in model.network.layer4[0].parameters()))
        self.assertTrue(all(p.requires_grad for p in model.network.layer4[1].parameters()))
        batch = {
            "anchor": torch.randn(3, 3, 32, 32),
            "context": torch.randn(3, 3, 32, 32),
            "geometry": torch.rand(3, 6),
        }
        logits = model(batch)
        loss = minibatch_loss(
            logits,
            torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]),
            torch.ones(3, 2, dtype=torch.bool),
            3,
            torch.tensor([3, 3]),
            pos_weight=cfg.pos_weight,
            label_smoothing=cfg.label_smoothing,
        )
        loss.backward()
        for name, param in model.named_parameters():
            if name.startswith("network.fc.") or name.startswith("network.layer4.1."):
                self.assertIsNotNone(param.grad, name)
            else:
                self.assertIsNone(param.grad, name)

    def test_threshold_calibration_and_fp_fn_gallery(self) -> None:
        values = torch.tensor([[1.0, 1.0]] * 35 + [[0.0, 0.0]] * 35)
        mask = torch.ones(70, 2, dtype=torch.bool)
        scores = torch.cat(
            [
                torch.full((35, 2), 0.72),
                torch.full((35, 2), 0.28),
            ],
            dim=0,
        )
        groups = [f"G-{i % 10}" for i in range(70)]
        cal = calibrate_optimal_thresholds(scores, values, mask, groups=groups)
        self.assertTrue(cal["evaluation"]["v11_all_targets_pass_gates"])
        gallery = build_fp_fn_gallery(
            self.rows[:4],
            [f"G-{i}" for i in range(4)],
            torch.tensor([[0.9, 0.1], [0.1, 0.9], [0.8, 0.2], [0.2, 0.8]]),
            (0.5, 0.5),
        )
        self.assertIn("phone_use", gallery)
        self.assertIn("looking_around", gallery)

    def test_end_to_end_v3_run_reload_and_resume_parity(self) -> None:
        cfg = self.make_v3_config()
        out_full = self.root / "outputs/v3-full"
        rec_full = run(self.root / "config-v3.yaml", out_full, self.root)
        self.assertEqual(rec_full.status, "FINISHED")
        self.assertEqual(rec_full.completed_epochs, 3)
        model, bundle = load_bundle(out_full, self.root)
        cohorts, _ = prepare_cohorts(cfg, self.root)
        scores = infer(model, cohorts[1], cfg).sigmoid().tolist()
        preds = json.loads((out_full / "predictions-development.json").read_text(encoding="utf-8"))
        self.assertEqual(scores, [r["scores"] for r in preds])
        metrics = evaluate(out_full, self.root / "outputs/v3-eval", self.root, "val")
        saved_metrics = json.loads((out_full / "metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(metrics["development"], saved_metrics["development"])
        self.assertIn("calibrated_evaluation", metrics["development"])
        self.assertIn("fp_fn_gallery_calibrated_threshold", metrics["development"])
        # Verify epoch-boundary interruption and resume parity
        out_res = self.root / "outputs/v3-resume"
        with self.assertRaises(KeyboardInterrupt):
            run(self.root / "config-v3.yaml", out_res, self.root, interrupt_after=1)
        rec_res = run(self.root / "config-v3.yaml", out_res, self.root, resume=True)
        self.assertEqual(rec_res.status, "FINISHED")
        a = torch.load(out_full / "best.pt", weights_only=True)
        b = torch.load(out_res / "best.pt", weights_only=True)
        self.assertEqual(tensor_digest(a["model"]), tensor_digest(b["model"]))


if __name__ == "__main__":
    unittest.main()
