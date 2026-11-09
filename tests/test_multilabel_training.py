"""Synthetic checks for explicit five-target execution, without real model/data."""
from __future__ import annotations

import importlib.util
import json
import time
import unittest
from dataclasses import asdict, replace
from types import SimpleNamespace
from unittest.mock import patch

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import test_representation
    import torch
    import yaml
    from fixtures.adaptation_fixture import pin

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.data.pilot_schema import (
        MULTILABEL_ENCODING_VERSION,
        MULTILABEL_SCHEMA_VERSION,
        MULTILABEL_SEMANTICS_VERSION,
        MULTILABEL_TARGET_ORDER,
        TARGET_ORDER,
        TargetReview,
        read_records,
        record_to_dict,
        write_records,
    )
    from ai_exam_monitoring.training.adaptation_config import config_from_dict
    from ai_exam_monitoring.training.adaptation_data import prepare_cohorts
    from ai_exam_monitoring.training.adaptation_evaluate import evaluate_adaptation
    from ai_exam_monitoring.training.adaptation_metrics import (
        build_fp_fn_gallery,
        minibatch_loss,
        report_scores,
    )
    from ai_exam_monitoring.training.adaptation_model import (
        AdaptationModel,
        create_e005_initial_head,
    )
    from ai_exam_monitoring.training.adaptation_train import train_images
    from ai_exam_monitoring.training.artifacts import code_identity, digest_json, write_json
    from ai_exam_monitoring.training.calibration import calibrate_exact, evaluate_pair
    from ai_exam_monitoring.training.data import _evaluation_identity
    from ai_exam_monitoring.training.metrics import evaluate_scores, masked_loss
    from ai_exam_monitoring.training.representation_campaign import champion_key, run_campaign
    from ai_exam_monitoring.training.train import run


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class MultilabelMetricTests(unittest.TestCase):
    def test_minibatch_gradient_matches_full_objective_with_empty_targets_and_tail(self):
        torch.manual_seed(73)
        values = torch.randint(2, (7, 5)).float()
        mask = torch.eye(5, dtype=torch.bool)[torch.tensor([0, 1, 2, 3, 4, 0, 1])]
        values[~mask] = float("nan")
        full = torch.randn(7, 5, requires_grad=True)
        batches = full.detach().clone().requires_grad_()
        expected = masked_loss(full, values, mask, target_order=MULTILABEL_TARGET_ORDER)
        expected.backward()
        actual = sum(minibatch_loss(
            batches[start:start+3], values[start:start+3], mask[start:start+3], 7, mask.sum(0),
            pos_weight=(1.,) * 5, target_order=MULTILABEL_TARGET_ORDER
        ) * len(values[start:start+3]) / 7 for start in (0, 3, 6))
        actual.backward()
        self.assertTrue(torch.allclose(full.grad, batches.grad))
        self.assertTrue(torch.equal(batches.grad[~mask], torch.zeros_like(batches.grad[~mask])))

    def test_calibration_requires_explicit_goals_and_preserves_five_thresholds(self):
        values = torch.tensor([[1., 0., 1., 0., 1.], [0., 1., 0., 1., 0.]])
        scores = values * .7 + .1
        mask = torch.ones_like(values, dtype=torch.bool)
        with self.assertRaises(DataContractError):
            calibrate_exact(scores, values, mask, target_order=MULTILABEL_TARGET_ORDER)
        goals = {name: {"precision_min": .7, "recall_min": .9, "fpr_max": .1}
                 for name in MULTILABEL_TARGET_ORDER}
        thresholds = calibrate_exact(scores, values, mask, target_order=MULTILABEL_TARGET_ORDER,
                                     objectives=goals)
        report = evaluate_pair(scores, values, mask, thresholds,
                               target_order=MULTILABEL_TARGET_ORDER)
        self.assertEqual(len(thresholds), 5)
        self.assertTrue(all(r["f1"] == 1. for r in report["targets"].values()))
        self.assertNotIn("v11_all_targets_pass_gates", report)
        mask[:, 4] = False
        with self.assertRaises(DataContractError):
            calibrate_exact(scores, values, mask, target_order=MULTILABEL_TARGET_ORDER,
                            objectives=goals)

    def test_gallery_uses_all_targets_and_masks(self):
        record = SimpleNamespace(sample_id="s1", source=SimpleNamespace(source_id="source"),
                                 crop=None, target_mask=(1, 1, 1, 1, 0),
                                 target_values=(0, 0, 0, 0, None))
        gallery = build_fp_fn_gallery([record], ["g1"], torch.full((1, 5), .9), (.5,) * 5,
                                      target_order=MULTILABEL_TARGET_ORDER)
        self.assertEqual(tuple(gallery), MULTILABEL_TARGET_ORDER)
        self.assertEqual(gallery["hand_raising"][0]["error_type"], "FP")
        self.assertEqual(gallery["standing_up"], [])
        with self.assertRaises(DataContractError):
            build_fp_fn_gallery([record], ["g1"], torch.full((1, 5), .9), (.5,) * 2,
                                target_order=MULTILABEL_TARGET_ORDER)

    def test_full_objective_report_and_train_constant_have_five_targets(self):
        values = torch.tensor([[1., 0., 1., 0., 1.], [0., 1., 0., 1., 0.]])
        mask = torch.ones_like(values, dtype=torch.bool)
        mask[0, 4] = False
        values[0, 4] = float("nan")
        logits = torch.zeros_like(values, requires_grad=True)
        loss = masked_loss(logits, values, mask, target_order=MULTILABEL_TARGET_ORDER)
        loss.backward()
        self.assertAlmostEqual(float(loss.detach()), .69314718, places=6)
        self.assertEqual(float(logits.grad[0, 4]), 0.)
        report = report_scores(logits.detach(), values, mask, .5, torch.full((5,), .5),
                               target_order=MULTILABEL_TARGET_ORDER)
        self.assertAlmostEqual(report["macro_masked_bce"], .69314718, places=6)
        constant = report["constant_train_prevalence"]
        self.assertEqual(tuple(constant["targets"]), MULTILABEL_TARGET_ORDER)
        self.assertIsNone(report["macro_ap"])
        self.assertNotIn("v11_all_targets_pass_gates", report)
        mask[:, 4] = False
        with self.assertRaises(DataContractError):
            masked_loss(logits, values, mask, target_order=MULTILABEL_TARGET_ORDER)
        report = report_scores(logits.detach(), values, mask, .5, torch.full((5,), .5),
                               target_order=MULTILABEL_TARGET_ORDER)
        self.assertIsNone(report["macro_masked_bce"])

    def test_explicit_contract_and_unknown_support(self):
        values = torch.tensor([[1., 0., 1., 0., 1.], [0., 1., 0., 1., 0.]])
        mask = torch.ones_like(values, dtype=torch.bool)
        scores = values * .8 + .1
        result = evaluate_scores(scores, values, mask, .5, target_order=MULTILABEL_TARGET_ORDER)
        self.assertEqual(tuple(result["targets"]), MULTILABEL_TARGET_ORDER)
        self.assertEqual(result["macro_ap"], 1.)
        self.assertEqual(result["cooccurrence"]["reason"],
                         "not_defined_for_five_target_contract")
        self.assertNotIn("v11_all_targets_pass_gates", result)
        mask[:, 4] = False
        values[:, 4] = float("nan")
        result = evaluate_scores(scores, values, mask, .5, target_order=MULTILABEL_TARGET_ORDER)
        self.assertIsNone(result["macro_ap"])
        self.assertEqual(result["targets"]["standing_up"]["unknown"], 2)
        self.assertIsNone(result["targets"]["standing_up"]["ap"])

    def test_no_implicit_expansion_reordering_or_score_postprocessing(self):
        values = torch.tensor([[1., 1., 1., 0., 1.], [0., 0., 0., 1., 0.]])
        mask = torch.ones_like(values, dtype=torch.bool)
        with self.assertRaises(DataContractError):
            evaluate_scores(values, values, mask, .5)
        with self.assertRaises(DataContractError):
            evaluate_scores(values, values, mask, .5,
                            target_order=tuple(reversed(MULTILABEL_TARGET_ORDER)))
        result = evaluate_scores(values, values, mask, .5, target_order=MULTILABEL_TARGET_ORDER)
        # Scores are evaluated independently: the annotation rule must not alter predictions.
        self.assertEqual(result["targets"]["sleeping"]["tp"], 1)
        self.assertEqual(result["targets"]["looking_around"]["tp"], 1)
        legacy = evaluate_scores(values[:, :2], values[:, :2], mask[:, :2], .5)
        self.assertEqual(tuple(legacy["targets"]), TARGET_ORDER)
        self.assertEqual(legacy["cooccurrence"]["positive"], 1)


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class MultilabelTrainingFixtureTests(unittest.TestCase):
    def setUp(self):
        self.helper = test_representation.RepresentationFixtureTests()
        self.helper.setUp()
        self.addCleanup(self.helper.doCleanups)
        self.root = self.helper.root

    def config(self):
        config = self.helper.config()
        package = self.root / config.cohorts[0].data.dataset
        rows = []
        for i, row in enumerate(read_records(package / "manifest.jsonl")):
            states = [i % 2, int(i % 3 != 0 and i % 2 == 1), int(i % 3 == 0),
                      int(i % 2 == 0), i % 2]
            targets = {name: TargetReview("positive" if v else "negative", "synthetic",
                                           row.phone_use.review)
                       for name, v in zip(MULTILABEL_TARGET_ORDER, states, strict=True)}
            rows.append(replace(row, schema_version=MULTILABEL_SCHEMA_VERSION,
                                target_encoding_version=MULTILABEL_ENCODING_VERSION,
                                semantics_version=MULTILABEL_SEMANTICS_VERSION, targets=targets,
                                phone_use=targets["phone_use"],
                                looking_around=targets["looking_around"]))
        for name in ("manifest.jsonl", "review-ledger.jsonl"):
            write_records(package / name, rows)
        release = json.loads((package / "release.json").read_text())
        release["test_freeze"]["manifest_sha256"] = sha256_file(package / "manifest.jsonl")
        write_json(package / "release.json", release)
        checksum = package / "checksums.sha256"
        checksum.write_text("".join(sha256_file(p) + "  " + p.relative_to(package).as_posix() + "\n"
                                     for p in sorted(package.rglob("*"))
                                     if p.is_file() and p != checksum), encoding="utf-8")
        data = replace(config.cohorts[0].data, encoding_version=MULTILABEL_ENCODING_VERSION,
                        payload_sha256=sha256_file(checksum))
        cohorts = tuple(replace(c, data=data) for c in config.cohorts)
        authority = json.loads((self.root / "execution.json").read_text())
        authority["payload_sha256"] = data.payload_sha256
        write_json(self.root / "execution.json", authority)
        protocol = json.loads((self.root / "protocol.json").read_text())
        protocol.update(target_order=list(MULTILABEL_TARGET_ORDER), calibration_objectives={
            name: {"precision_min": .6, "recall_min": .7, "fpr_max": .3}
            for name in MULTILABEL_TARGET_ORDER})
        for cohort in cohorts:
            protocol["cohorts"][cohort.name]["records_sha256"] = digest_json(
                [record_to_dict(r) for r in rows if r.sample_id in cohort.sample_ids])
        write_json(self.root / "protocol.json", protocol)
        head = self.root / "five-head.pt"
        create_e005_initial_head(head, config.seed, hidden_dim=config.head_hidden_dim,
                                 dropout=config.head_dropout, target_order=MULTILABEL_TARGET_ORDER)
        config = replace(config, cohorts=cohorts, target_order=list(MULTILABEL_TARGET_ORDER),
                          pos_weight=(1.,) * 5, head_initialization=pin(self.root, head),
                          protocol=pin(self.root, self.root / "protocol.json"),
                          execution_authorization=pin(self.root, self.root / "execution.json"))
        ready = json.loads((self.root / "readiness.json").read_text())
        ready.update(protocol_sha256=config.protocol.sha256,
                     cohorts_sha256=digest_json(config.to_dict()["cohorts"]),
                     execution_authorization=asdict(config.execution_authorization),
                     evidence_pins=[asdict(config.execution_authorization)])
        write_json(self.root / "readiness.json", ready)
        config = replace(config, readiness=pin(self.root, self.root / "readiness.json"))
        approval = json.loads((self.root / config.approval_ref).read_text())
        approval.update(code_sha256=code_identity()["sha256"],
                        configs={config.experiment_id: digest_json(config.to_dict())},
                        config_signatures={config.experiment_id: config.match_signature()})
        write_json(self.root / config.approval_ref, approval)
        (self.root / "five.yaml").write_text(yaml.safe_dump(config.to_dict()), encoding="utf-8")
        return config

    def test_loader_head_training_reload_and_reporting(self):
        config = self.config()
        self.assertEqual(config_from_dict(config.to_dict()), config)
        cohorts, _ = prepare_cohorts(config, self.root)
        self.assertEqual(cohorts[0].values.shape[1], 5)
        with self.assertRaises(ConfigurationError):
            replace(config, pos_weight=(1., 1.))
        model = AdaptationModel(config, weights=config.weights.verify(self.root),
                                initial_head=config.head_initialization.verify(self.root))
        self.assertEqual(model(torch.zeros(1, 3, config.image_size, config.image_size)).shape,
                         (1, 5))
        output = self.root / "outputs/five"
        self.assertEqual(run(self.root / "five.yaml", output, self.root).status, "FINISHED")
        metrics = json.loads((output / "metrics.json").read_text())
        self.assertEqual(tuple(metrics["development"]["targets"]), MULTILABEL_TARGET_ORDER)
        self.assertNotIn("v11_all_targets_pass_gates", metrics["development"])
        predictions = json.loads((output / "predictions-development.json").read_text())
        self.assertEqual(len(predictions[0]["calibrated_decisions"]), 5)
        evaluate_adaptation(output, self.root / "outputs/reload-five", self.root, "val")
        reload = json.loads((self.root / "outputs/reload-five/metrics.json").read_text())
        self.assertEqual(reload["development"], metrics["development"])
        interrupted = self.root / "outputs/resumed-five"
        with self.assertRaises(KeyboardInterrupt):
            run(self.root / "five.yaml", interrupted, self.root, interrupt_after=1)
        self.assertEqual(run(self.root / "five.yaml", interrupted, self.root,
                             resume=True).status, "FINISHED")
        self.assertEqual(json.loads((interrupted / "predictions-development.json").read_text()),
                         predictions)

    def test_loss_selection_retains_unavailable_ap_in_history(self):
        config = self.config()
        cohorts, _ = prepare_cohorts(config, self.root)
        config = replace(config, selection_metric="val_loss", calibrate_thresholds_on_val=False)
        model = AdaptationModel(config, weights=config.weights.verify(self.root),
                                initial_head=config.head_initialization.verify(self.root))
        output = self.root / "history-five"
        output.mkdir()
        with patch("ai_exam_monitoring.training.adaptation_train.evaluate_scores",
                   return_value={"macro_ap": None}):
            result = train_images(model, cohorts[0], cohorts[1], config, output, "synthetic")
        self.assertTrue(all(row["val_macro_ap"] is None for row in result["history"]))
        self.assertTrue(all(row["train_macro_ap"] is None for row in result["history"]))

    def test_preservation_identity_includes_new_target_review_evidence(self):
        config = self.config()
        row = read_records(self.root / config.cohorts[0].data.dataset / "manifest.jsonl")[0]
        targets = dict(row.targets)
        targets["hand_raising"] = replace(targets["hand_raising"], reason="changed audit evidence")
        changed = replace(row, targets=targets)
        self.assertEqual(row.target_values, changed.target_values)
        self.assertNotEqual(_evaluation_identity(row), _evaluation_identity(changed))

    def test_legacy_campaign_rejects_five_targets_before_device_or_run_setup(self):
        proposal = self.root / "five-proposal.yaml"
        proposal.write_text(yaml.safe_dump({"targets": list(MULTILABEL_TARGET_ORDER)}))
        authority = self.root / "campaign-authority.json"
        write_json(authority, {"status": "approved", "scope": "synthetic software fixture only"})
        design_path = self.root / "campaign-design.json"
        for schema in ("representation-adaptation-v4", "dinov2-adaptation-v6"):
            write_json(design_path, {"config_schema": schema,
                                     "proposal": asdict(pin(self.root, proposal)),
                                     "authorization": asdict(pin(self.root, authority))})
            with (patch("torch.cuda.is_available", side_effect=AssertionError("GPU probed")),
                  self.assertRaisesRegex(DataContractError, "two-target campaign")):
                run_campaign(design_path, self.root, self.root / "unused-storage", time.time())
        self.assertFalse((self.root / "unused-storage").exists())
        with self.assertRaises(DataContractError):
            champion_key("synthetic", {"calibrated_evaluation": {"targets": {
                name: {} for name in MULTILABEL_TARGET_ORDER}}})

    def test_missing_protocol_targets_and_two_output_initialization_are_rejected(self):
        config = self.config()
        with self.assertRaises(ConfigurationError):
            replace(config, target_order=list(TARGET_ORDER), pos_weight=(1., 1.))
        two_head = self.root / "wrong-head.pt"
        create_e005_initial_head(two_head, config.seed, hidden_dim=config.head_hidden_dim)
        bad = replace(config, head_initialization=pin(self.root, two_head))
        with self.assertRaises(DataContractError):
            AdaptationModel(bad, weights=bad.weights.verify(self.root), initial_head=two_head)
        protocol = json.loads((self.root / "protocol.json").read_text())
        protocol.pop("calibration_objectives")
        write_json(self.root / "protocol.json", protocol)
        ready = json.loads((self.root / "readiness.json").read_text())
        ready["protocol_sha256"] = sha256_file(self.root / "protocol.json")
        write_json(self.root / "readiness.json", ready)
        bad = replace(config, protocol=pin(self.root, self.root / "protocol.json"),
                       readiness=pin(self.root, self.root / "readiness.json"))
        with self.assertRaisesRegex(DataContractError, "Calibration objectives"):
            prepare_cohorts(bad, self.root)
