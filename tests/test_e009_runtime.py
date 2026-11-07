"""E009 runtime binding and calibrated inference on synthetic inputs only."""
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from dataclasses import replace
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import test_dino_adaptation
    import torch
    from PIL import Image

    from ai_exam_monitoring.common.errors import DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.classifier import BundleClassifier
    from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
    from ai_exam_monitoring.training.adaptation_model import AdaptationModel, tensor_digest
    from ai_exam_monitoring.training.artifacts import digest_json


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class E009RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.helper = test_dino_adaptation.DinoAdaptationTests()
        self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.root = self.helper.root
        self.config = replace(self.helper.config(base=True), image_size=336,
                              experiment_id="E009-V15-B0-S20261106")
        patcher = patch("ai_exam_monitoring.training.encoders.load_dino_source",
                        side_effect=lambda *a, **k: test_dino_adaptation.TinyDino(768))
        patcher.start()
        self.addCleanup(patcher.stop)

    def runtime(self, config):
        raw = config.to_dict()
        model = AdaptationModel(config, weights=config.weights.verify(self.root),
                                initial_head=config.head_initialization.verify(self.root),
                                workspace=self.root)
        checkpoint = self.root / "best.pt"
        state = model.state_dict()
        payload = dict(schema_version="full-model-bundle-v1", identity="fixture",
                       config=raw, model=state, model_tensor_sha256=tensor_digest(state))
        torch.save(payload, checkpoint)
        sha = sha256_file(checkpoint)
        pins = {"checkpoint": {"path": "best.pt", "sha256": sha}}
        objects = {
            "resolved_config": raw,
            "bundle": dict(schema_version="full-model-bundle-v1", identity="fixture",
                           config_sha256=digest_json(raw), code_sha256="historical-source",
                           checkpoint_sha256=sha, target_order=config.target_order),
            "run": dict(status="FINISHED", experiment_id=config.experiment_id,
                        config_sha256=digest_json(raw), code_sha256="historical-source"),
            "calibration": dict(schema_version="selection-calibration-v4",
                                checkpoint_sha256=sha, thresholds=[.207, .451]),
        }
        for name, value in objects.items():
            path = self.root / f"{name}.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            pins[name] = {"path": path.name, "sha256": sha256_file(path)}
        return RuntimeConfig(dict(schema_version="recorded-runtime-config-v5", pins=pins,
                                  classifier=dict(model_id="B0", model=config.model,
                                                  experiment_id=config.experiment_id,
                                                  image_size=config.image_size, threads=4)),
                             self.root)

    def test_both_sizes_load_exact_state_and_keep_calibrated_target_order(self):
        for size in (336, 448):
            with self.subTest(size=size):
                config = replace(self.config, image_size=size)
                runtime = self.runtime(config)
                classifier = BundleClassifier(runtime)
                image = Image.new("RGB", (31, 70), (30, 100, 200))
                self.assertEqual(classifier.preview(image).size, (size, size))
                self.assertEqual(classifier.thresholds, [.207, .451])
                scores = classifier.predict(image)
                self.assertEqual(len(scores), 2)
                self.assertTrue(all(0 <= value <= 1 for value in scores))
                self.assertEqual(scores, classifier.predict_batch([image])[0])
                self.assertFalse(any(p.requires_grad for p in classifier.model.parameters()))

    def test_crossed_model_binding_or_calibration_is_rejected(self):
        runtime = self.runtime(self.config)
        for key, value in (("experiment_id", "different-run"), ("image_size", 448)):
            raw = copy.deepcopy(runtime.raw)
            raw["classifier"][key] = value
            with self.subTest(key=key), self.assertRaises(DataContractError):
                BundleClassifier(RuntimeConfig(raw, self.root))
        path = runtime.pin("calibration")
        calibration = json.loads(path.read_text())
        calibration["checkpoint_sha256"] = "different-checkpoint"
        path.write_text(json.dumps(calibration))
        raw = copy.deepcopy(runtime.raw)
        raw["pins"]["calibration"]["sha256"] = sha256_file(path)
        with self.assertRaises(DataContractError):
            BundleClassifier(RuntimeConfig(raw, self.root))
