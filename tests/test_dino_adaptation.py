from __future__ import annotations

import importlib.util
import json
import unittest
from dataclasses import fields, replace
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import test_representation
    import torch
    import yaml
    from fixtures.adaptation_fixture import pin

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.training.adaptation_config import (
        DinoAdaptationConfig,
        SpatialConfig,
        config_from_dict,
    )
    from ai_exam_monitoring.training.adaptation_data import prepare_cohorts
    from ai_exam_monitoring.training.adaptation_evaluate import evaluate_adaptation
    from ai_exam_monitoring.training.adaptation_model import (
        AdaptationModel,
        create_e005_initial_head,
        head_input_dim,
        tensor_digest,
    )
    from ai_exam_monitoring.training.adaptation_train import train_images
    from ai_exam_monitoring.training.artifacts import code_identity, digest_json, write_json
    from ai_exam_monitoring.training.train import run

    class TinyDino(torch.nn.Module):
        def __init__(self, dim=384):
            super().__init__()
            self.blocks = torch.nn.ModuleList([torch.nn.Linear(dim, dim) for _ in range(12)])
            self.norm = torch.nn.LayerNorm(dim)
            self.dim = dim

        def prepare_tokens_with_masks(self, images):
            base = images.mean((1, 2, 3)).reshape(-1, 1, 1).expand(-1, 5, self.dim)
            return base + torch.arange(5, dtype=images.dtype).reshape(1, 5, 1) / 5


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class DinoAdaptationTests(unittest.TestCase):
    def setUp(self):
        self.helper = test_representation.RepresentationFixtureTests()
        self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.root = self.helper.root

    def config(self, *, base=False, last=2):
        template = self.helper.config()
        dim = 768 if base else 384
        weights = self.root / f"weights-{dim}.pt"
        torch.save(TinyDino(dim).state_dict(), weights)
        head = self.root / f"head-{dim}.pt"
        create_e005_initial_head(head, template.seed, in_dim=dim*2,
                                 hidden_dim=template.head_hidden_dim,
                                 dropout=template.head_dropout)
        raw = {f.name: getattr(template, f.name) for f in fields(template)}
        variant = "dinov2_vitb14" if base else "dinov2_vits14"
        raw.update(schema_version="dinov2-adaptation-v6", model=variant+"_v6",
                   encoder_variant=variant, train_last_blocks=last, train_final_norm=True,
                   pooling="global_mean", weights_id="DINOv2_VITB14" if base else "DINOv2_VITS14",
                   weights=pin(self.root, weights), encoder_source=pin(self.root, weights),
                   head_initialization=pin(self.root, head), image_size=28,
                   anchor_padding_ratio=0., trainable_scope="head_and_last_blocks",
                   augmentation=replace(template.augmentation, random_erasing_prob=0.))
        return DinoAdaptationConfig(**raw)

    def model(self, c):
        dim = 768 if c.encoder_variant == "dinov2_vitb14" else 384
        with patch("ai_exam_monitoring.training.encoders.load_dino_source",
                   side_effect=lambda *args, **kwargs: TinyDino(dim)):
            return AdaptationModel(c, weights=c.weights.verify(self.root),
                                   initial_head=c.head_initialization.verify(self.root),
                                   workspace=self.root)

    def test_schema_roundtrip_and_legacy_rejection(self):
        c = self.config()
        self.assertEqual(config_from_dict(c.to_dict()), c)
        for change in ({"train_last_blocks": 3}, {"train_last_blocks": True},
                       {"train_final_norm": False}, {"encoder_variant": "dinov2_vitl14"},
                       {"image_size": 30}, {"pooling": "person_2x2"},
                       {"precision": "bfloat16"}, {"model": "dinov2_vitb14_v6"}):
            with self.assertRaises(ConfigurationError):
                replace(c, **change)
        raw = c.to_dict()
        raw["schema_version"] = "spatial-representation-v5"
        with self.assertRaises(ConfigurationError):
            config_from_dict(raw)

    def test_base_four_blocks_optimizer_and_frozen_gradients(self):
        c = self.config(base=True, last=4)
        self.assertEqual(head_input_dim(c), 1536)
        model = self.model(c)
        model.configure_trainable_stage(c, epoch=1)
        self.assertFalse(any(p.requires_grad for p in model.network.backbone.parameters()))
        model.configure_trainable_stage(c, epoch=c.warmup_epochs+1)
        groups, names = model.parameter_groups(c)
        self.assertEqual(len(groups), 2)
        self.assertTrue(any("blocks.8." in n for n in names["layer4"]))
        self.assertFalse(any("blocks.7." in n for n in names["layer4"]))
        model(torch.randn(2, 3, 28, 28)).sum().backward()
        self.assertIsNone(model.network.backbone.blocks[7].weight.grad)
        for i in range(8, 12):
            self.assertIsNotNone(model.network.backbone.blocks[i].weight.grad)
        self.assertIsNotNone(model.network.backbone.norm.weight.grad)

    def test_C0_matches_V5_features_gradients_and_optimizer_update(self):
        c = self.config()
        raw = c.to_dict()
        for key in ("encoder_variant", "train_last_blocks", "train_final_norm"):
            raw.pop(key)
        raw.update(schema_version="spatial-representation-v5", model="dinov2_vits14_v4",
                   trainable_scope="head_and_last_two_blocks")
        old = config_from_dict(raw)
        self.assertIsInstance(old, SpatialConfig)
        model = self.model(c)
        with patch("ai_exam_monitoring.training.encoders.load_dino_source",
                   side_effect=lambda *args, **kwargs: TinyDino()):
            twin = AdaptationModel(old, full_state=model.state_dict(), workspace=self.root)
        inputs = torch.randn(2, 3, 28, 28)
        for net, config in ((model, c), (twin, old)):
            net.configure_trainable_stage(config, epoch=config.warmup_epochs+1)
            net.train()
            torch.manual_seed(1234)
            optimizer = torch.optim.AdamW(net.parameter_groups(config)[0])
            out = net(inputs)
            if net is model:
                expected = out.detach().clone()
            else:
                torch.testing.assert_close(out, expected, rtol=0, atol=0)
            out.square().mean().backward()
            optimizer.step()
        self.assertEqual(tensor_digest(model.state_dict()), tensor_digest(twin.state_dict()))

    def test_four_block_resume_and_full_bundle_dispatch(self):
        c = self.config(last=4)
        cohorts, _ = prepare_cohorts(c, self.root)
        states = []
        for interrupted in (False, True):
            torch.manual_seed(c.seed)
            model = self.model(c)
            folder = self.root / f"trial-{interrupted}"
            folder.mkdir()
            if interrupted:
                with self.assertRaises(KeyboardInterrupt):
                    train_images(model, *cohorts[:2], c, folder, "fixture",
                                 interrupt_after=c.warmup_epochs)
            state = train_images(model, *cohorts[:2], c, folder, "fixture", resume=interrupted)
            states.append((state["history"], tensor_digest(state["best_model"])))
        self.assertEqual(*states)
        approval = json.loads((self.root/c.approval_ref).read_text())
        approval.update(code_sha256=code_identity()["sha256"],
                        configs={c.experiment_id:digest_json(c.to_dict())},
                        config_signatures={c.experiment_id:c.match_signature()})
        write_json(self.root/c.approval_ref, approval)
        path = self.root/"v6.yaml"
        path.write_text(yaml.safe_dump(c.to_dict()), encoding="utf-8")
        output = self.root/"outputs/v6"
        with patch("ai_exam_monitoring.training.encoders.load_dino_source",
                   side_effect=lambda *args, **kwargs: TinyDino()):
            self.assertEqual(run(path, output, self.root).status, "FINISHED")
            result = evaluate_adaptation(output, self.root/"outputs/reload", self.root, "val")
        original = json.loads((output/"metrics.json").read_text())
        self.assertEqual(result["development"], original["development"])
        self.assertTrue((output/"telemetry.json").is_file())
        with self.assertRaises(DataContractError):
            evaluate_adaptation(output, self.root/"outputs/test", self.root, "test")
