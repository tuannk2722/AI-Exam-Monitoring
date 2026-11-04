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
    from ai_exam_monitoring.data.pilot_schema import PixelBox
    from ai_exam_monitoring.training.adaptation_config import SpatialConfig, config_from_dict
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
    from ai_exam_monitoring.training.spatial_pooling import (
        letterbox_regions,
        mirror_regions,
        spatial_features,
    )
    from ai_exam_monitoring.training.train import run

    class TinyDino(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.blocks = torch.nn.ModuleList([torch.nn.Linear(384, 384) for _ in range(12)])
            self.norm = torch.nn.LayerNorm(384)

        def prepare_tokens_with_masks(self, images):
            base = images.mean((1, 2, 3)).reshape(-1, 1, 1).expand(-1, 5, 384)
            return base + torch.arange(5, dtype=images.dtype).reshape(1, 5, 1) / 5


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class SpatialTests(unittest.TestCase):
    def test_rounded_letterbox_offset_import_and_mirror(self):
        # Native 200 x 100 imported as 101 x 51 -> rounded 28 x 14 at top=7.
        boxes = letterbox_regions(PixelBox(125, 60, 225, 110),
                                  PixelBox(100, 50, 300, 150), (101, 51), 28)
        torch.testing.assert_close(boxes[0], torch.tensor([0., 7., 28., 21.]))
        torch.testing.assert_close(boxes[1], torch.tensor([3.5, 8.4, 17.5, 15.4]))
        mirrored = mirror_regions(boxes, 28)
        torch.testing.assert_close(mirrored[1], torch.tensor([10.5, 8.4, 24.5, 15.4]))
        torch.testing.assert_close(mirror_regions(mirrored, 28), boxes)

    def test_area_means_against_independent_scalar_reference_and_gradient(self):
        tokens = torch.arange(5., requires_grad=True).reshape(1, 5, 1)
        box = torch.tensor([[3., 5., 24., 26.]])
        result = spatial_features(tokens, box, image_size=28)
        expected = [0.]
        for ya, yb in ((5., 15.5), (15.5, 26.)):
            for xa, xb in ((3., 13.5), (13.5, 24.)):
                numer = denom = 0.
                for j, value in enumerate((1., 2., 3., 4.)):
                    px, py = (j % 2)*14., (j//2)*14.
                    area = max(0., min(xb, px+14)-max(xa, px)) * max(
                        0., min(yb, py+14)-max(ya, py))
                    numer += value*area
                    denom += area
                expected.append(numer/denom)
        torch.testing.assert_close(result[0], torch.tensor(expected))
        grad = torch.autograd.grad(result.sum(), tokens)[0]
        self.assertTrue(torch.isfinite(grad).all())
        self.assertTrue((grad > 0).all())

    def test_no_silent_empty_nonfinite_outside_or_wrong_grid(self):
        tokens = torch.zeros(1, 5, 2)
        for box in ([0,0,0,1], [-1,0,28,28], [0,0,29,28], [0,0,float('nan'),28]):
            with self.assertRaises(DataContractError):
                spatial_features(tokens, torch.tensor([box]), image_size=28)
        with self.assertRaises(DataContractError):
            spatial_features(tokens[:, :4], torch.tensor([[0,0,28,28]]), image_size=28)


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class SpatialPipelineTests(unittest.TestCase):
    def setUp(self):
        self.helper = test_representation.RepresentationFixtureTests()
        self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.root = self.helper.root

    def config(self):
        base = self.helper.config()
        weights = self.root / 'tiny-dino.pt'
        torch.save(TinyDino().state_dict(), weights)
        head = self.root / 'spatial-head.pt'
        create_e005_initial_head(head, base.seed, in_dim=1920,
                                 hidden_dim=base.head_hidden_dim, dropout=base.head_dropout)
        raw = {f.name: getattr(base, f.name) for f in fields(base)}
        raw.update(schema_version='spatial-representation-v5', pooling='person_2x2',
                   model='dinov2_vits14_v4', weights_id='DINOv2_VITS14', image_size=28,
                   weights=pin(self.root, weights), encoder_source=pin(self.root, weights),
                   head_initialization=pin(self.root, head), anchor_padding_ratio=0.,
                   trainable_scope='head_and_last_two_blocks',
                   augmentation=replace(base.augmentation, random_erasing_prob=0.))
        return SpatialConfig(**raw)

    def test_schema_head_pair_and_geometry_synchronized_with_augmentation(self):
        config = self.config()
        self.assertEqual(config_from_dict(config.to_dict()), config)
        self.assertEqual(head_input_dim(config), 1920)
        self.assertEqual(config.head_initialization,
                         replace(config, pooling='context_2x2').head_initialization)
        for change in ({'pooling':'bogus'}, {'schema_version':'representation-adaptation-v4'},
                       {'augmentation':replace(config.augmentation, random_erasing_prob=.1)}):
            with self.assertRaises(ConfigurationError):
                replace(config, **change)
        cohorts, _ = prepare_cohorts(config, self.root)
        cohort = cohorts[0]
        for epoch in range(1, 6):
            a = cohort.model_batch([0], config, epoch=epoch, train_mode=True)
            g0 = cohort.model_batch([0], replace(config, pooling='global_mean'),
                                     epoch=epoch, train_mode=True)
            torch.testing.assert_close(a['context'], g0, rtol=0, atol=0)
            gen = torch.Generator().manual_seed((config.seed+epoch*100003) % (2**31-1))
            expected = cohort._geometry_cache[0].clone()
            if float(torch.rand(1, generator=gen)) < config.augmentation.horizontal_flip_prob:
                expected = mirror_regions(expected, config.image_size)
            torch.testing.assert_close(a['pooling_box'][0], expected[1])

    def test_equal_region_features_logits_and_frozen_prefix_gradients(self):
        config = self.config()
        with patch('ai_exam_monitoring.training.encoders.load_dino_source',
                   side_effect=lambda *_: TinyDino()):
            model = AdaptationModel(config, weights=config.weights.verify(self.root),
                                    initial_head=config.head_initialization.verify(self.root),
                                    workspace=self.root)
            twin = AdaptationModel(replace(config, pooling='context_2x2'),
                                   full_state=model.state_dict(), workspace=self.root)
        inputs = {'context':torch.randn(2,3,28,28),
                  'pooling_box':torch.tensor([[0.,0.,28.,28.]]*2)}
        model.eval()
        twin.eval()
        torch.testing.assert_close(model(inputs), twin(inputs), rtol=0, atol=0)
        model.configure_trainable_stage(config, epoch=1)
        self.assertFalse(any(p.requires_grad for p in model.network.backbone.parameters()))
        model.configure_trainable_stage(config, epoch=config.warmup_epochs+1)
        model.train()
        model(inputs).sum().backward()
        self.assertIsNone(model.network.backbone.blocks[9].weight.grad)
        self.assertIsNotNone(model.network.backbone.blocks[10].weight.grad)
        self.assertIsNotNone(model.network.backbone.norm.weight.grad)
        with self.assertRaises(DataContractError):
            model(inputs['context'])

    def test_spatial_resume_transition_and_standalone_reload(self):
        config = self.config()
        cohorts, _ = prepare_cohorts(config, self.root)
        with patch('ai_exam_monitoring.training.encoders.load_dino_source',
                   side_effect=lambda *_: TinyDino()):
            states = []
            for interrupted in (False, True):
                torch.manual_seed(config.seed)
                model = AdaptationModel(config, weights=config.weights.verify(self.root),
                                        initial_head=config.head_initialization.verify(self.root),
                                        workspace=self.root)
                folder = self.root/f'resume-{interrupted}'
                folder.mkdir()
                if interrupted:
                    with self.assertRaises(KeyboardInterrupt):
                        train_images(model, *cohorts[:2], config, folder, 'fixture',
                                     interrupt_after=config.warmup_epochs)
                state = train_images(model, *cohorts[:2], config, folder, 'fixture',
                                     resume=interrupted)
                states.append((state['history'], tensor_digest(state['best_model'])))
            self.assertEqual(states[0], states[1])
            approval = json.loads((self.root/config.approval_ref).read_text())
            approval.update(code_sha256=code_identity()['sha256'],
                            configs={config.experiment_id:digest_json(config.to_dict())},
                            config_signatures={config.experiment_id:config.match_signature()})
            write_json(self.root/config.approval_ref, approval)
            path = self.root/'v5.yaml'
            path.write_text(yaml.safe_dump(config.to_dict()), encoding='utf-8')
            output = self.root/'outputs/spatial'
            self.assertEqual(run(path, output, self.root).status, 'FINISHED')
            original = json.loads((output/'metrics.json').read_text())
            result = evaluate_adaptation(output, self.root/'outputs/reload', self.root, 'val')
            self.assertEqual(result['development'], original['development'])


if __name__ == '__main__':
    unittest.main()
