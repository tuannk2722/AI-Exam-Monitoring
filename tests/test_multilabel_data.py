from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import test_pilot_package
import test_source_review
from PIL import Image
from test_pilot_schema import pending_record, reviewed_record

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.audit import audit_dataset
from ai_exam_monitoring.data.pilot_package import build_pilot_package, coverage_report
from ai_exam_monitoring.data.pilot_schema import (
    MULTILABEL_ENCODING_VERSION,
    MULTILABEL_SCHEMA_VERSION,
    MULTILABEL_SEMANTICS_VERSION,
    MULTILABEL_TARGET_ORDER,
    ContextReview,
    PilotRecord,
    TargetReview,
    read_records,
    record_from_dict,
    record_to_dict,
    validate_records,
    write_records,
)
from ai_exam_monitoring.data.review_acceptance import accept_reviews
from ai_exam_monitoring.data.review_reconcile import apply_review_only_policy, merge_review
from ai_exam_monitoring.data.review_workspace import build
from ai_exam_monitoring.data.source_review import (
    PinnedYoloZip,
    fingerprint,
    member_key,
    write_pending_crop,
)


def five(record: PilotRecord, *, pending: bool = False) -> PilotRecord:
    targets = {name: TargetReview("unknown", "Pending visual audit")
               for name in MULTILABEL_TARGET_ORDER}
    if not pending:
        targets.update(phone_use=record.phone_use, looking_around=record.looking_around)
    return replace(record, schema_version=MULTILABEL_SCHEMA_VERSION,
                   target_encoding_version=MULTILABEL_ENCODING_VERSION,
                   semantics_version=MULTILABEL_SEMANTICS_VERSION, targets=targets,
                   phone_use=targets["phone_use"], looking_around=targets["looking_around"])


class MultilabelDataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def workspace(self, multilabel=True):
        old, source_root, crop = test_pilot_package.PilotPackageTests().make_record(
            self.root, "A001", 1)
        old = replace(old, source=replace(old.source, image_relpath=(
            Path("source") / old.source.image_relpath).as_posix()),
            crop=replace(old.crop, crop_relpath=crop.relative_to(self.root).as_posix()))
        if multilabel:
            item = five(replace(old, disposition="pending", owner_decision_ref=None,
                                crop=replace(old.crop, review=None)), pending=True)
        else:
            item = old
        # Internal audit ledger, before review or release, as in the existing workflow.
        write_records(self.root / "review-ledger.jsonl", [item])
        recipe = self.root / "recipe.json"
        recipe.write_text(json.dumps({"image_size": 336 if multilabel else 224,
                                      "fill": [124, 116, 104]}), encoding="utf-8")
        config = {
            "package": ".", "ledger_sha256": sha256_file(self.root / "review-ledger.jsonl"),
            "allow_test_visual_review": False, "recipe": "recipe.json",
            "recipe_sha256": sha256_file(recipe), "output": "review", "report": "report",
            "groups": 1,
        }
        if multilabel:
            config.update(include_pending=True, expected_review=1)
        else:
            config["expected_accepted"] = 1
        config_path = self.root / "review-config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        summary = build(config_path, self.root)
        inventory = json.loads((self.root / "review/inventory.json").read_text(encoding="utf-8"))
        return item, config, summary, inventory, source_root

    def test_v3_pending_can_start_before_crop_labels_rights_or_groups_are_reviewed(self):
        item = five(pending_record(), pending=True)
        self.assertIsNone(item.crop)
        self.assertIsNone(item.rights.review)
        self.assertIsNone(item.group)
        self.assertEqual(item.target_values, (None,) * 5)
        self.assertEqual(record_from_dict(record_to_dict(item)), item)

    def test_schema_named_targets_masks_versions_and_legacy_bytes(self):
        item = five(reviewed_record())
        raw = record_to_dict(item)
        self.assertNotIn("phone_use", raw)
        self.assertEqual(set(raw["targets"]), set(MULTILABEL_TARGET_ORDER))
        self.assertEqual(item.target_mask, (1, 0, 0, 0, 0))
        self.assertEqual(record_from_dict(json.loads(json.dumps(raw))), item)
        for old_version, digest in (
            ("pilot-b-manifest-v1",
             "6104195eeba68dc9b77745f7acbab8fb8611a13a02c0cef1df9e56564b091d7f"),
            ("pilot-b-manifest-v2",
             "4106fa5848e3890c2cb6765314931a4222df5fbb66b61e303fff173e33db11e8"),
        ):
            old = replace(reviewed_record(), schema_version=old_version)
            payload = (json.dumps(record_to_dict(old), sort_keys=True, ensure_ascii=False)
                       + "\n").encode()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), digest)
            self.assertEqual(record_from_dict(record_to_dict(old)), old)

    def test_normal_uses_all_targets_and_new_target_reviews_bind_exact_crop(self):
        base = reviewed_record()
        evidence = base.crop.review
        targets = {name: TargetReview("negative", "Reviewed absence", evidence)
                   for name in MULTILABEL_TARGET_ORDER}
        item = replace(five(base), targets=targets, phone_use=targets["phone_use"],
                       looking_around=targets["looking_around"], work_context_review=ContextReview(
                           "confirmed_working", "Reviewed work context", evidence))
        self.assertEqual(item.normal_review, "confirmed_normal")
        targets["standing_up"] = TargetReview("unknown", "Not reviewed")
        self.assertEqual(item.normal_review, "confirmed_normal")
        self.assertEqual(replace(item, targets=targets).normal_review, "unknown")
        targets["hand_raising"] = TargetReview("positive", "Wrong crop", replace(
            evidence, crop_sha256="0" * 64))
        with self.assertRaises(DataContractError):
            replace(item, targets=targets)

    def test_strict_targets_derived_values_and_no_mixed_encoding(self):
        item = five(reviewed_record())
        raw = record_to_dict(item)
        for change in ("missing", "alias", "order", "mask", "bool", "old_field", "version"):
            altered = copy.deepcopy(raw)
            if change == "missing":
                altered["targets"].pop("sleeping")
            elif change == "alias":
                altered["targets"]["standing"] = altered["targets"].pop("standing_up")
            elif change == "order":
                altered["target_order"].reverse()
            elif change == "mask":
                altered["target_mask"][2] = 1
            elif change == "bool":
                altered["target_values"][0] = True
            elif change == "old_field":
                altered["phone_use"] = raw["targets"]["phone_use"]
            else:
                altered["target_encoding_version"] = "pilot-b-targets-v1"
            with self.subTest(change=change), self.assertRaises(DataContractError):
                record_from_dict(altered)
        with self.assertRaises(DataContractError):
            validate_records([item, replace(reviewed_record("Other"), source=replace(
                item.source, image_sha256="d" * 64))])
        path = self.root / "duplicate.jsonl"
        text = json.dumps(raw).replace('"targets": {', '"targets": {}, "targets": {')
        path.write_text(text, encoding="utf-8")
        with self.assertRaises(DataContractError):
            read_records(path)

    def test_source_hint_and_draft_geometry_do_not_become_five_ground_truths(self):
        path, raw = test_source_review.SourceReviewTests().make_zip(self.root)
        reader = PinnedYoloZip(path, sha256_file(path), {0: "sleep-source-hint"})
        try:
            source = reader.read(member_key("train/images/image.png"),
                                 hashlib.sha256(raw).hexdigest())
            from ai_exam_monitoring.data.pilot_schema import PixelBox

            row = write_pending_crop(
                source, PixelBox(8, 3, 28, 18), PixelBox(3, 0, 35, 20), "D001",
                self.root / "drafts", states=("N", "N", "P", "U", "U"), reason="Source hint only",
                input_size=336, fill=(124, 116, 104), target_order=MULTILABEL_TARGET_ORDER)
            self.assertEqual(row["canonical_targets"], [None] * 5)
            self.assertEqual(row["canonical_mask"], [0] * 5)
            self.assertFalse(row["owner_approved"])
            hints = fingerprint(source, target_order=MULTILABEL_TARGET_ORDER)
            self.assertEqual(hints["canonical_mask"], [0] * 5)
            with Image.open(self.root / "drafts/D001/input.png") as image:
                self.assertEqual(image.size, (336, 336))
        finally:
            reader.close()

    def test_existing_source_batch_builder_renders_five_hint_states_without_acceptance(self):
        from scripts.build_source_review_batch import build as build_batch

        archive, raw = test_source_review.SourceReviewTests().make_zip(self.root)
        config = {
            "status": "authorized_draft_preparation", "input_size": 336,
            "fill": [124, 116, 104], "sources": [{"id": "source-01", "archive": str(archive),
                "archive_sha256": sha256_file(archive), "names": {0: "source-hint"}}],
        }
        # JSON is valid YAML; source class keys must stay integers in the source config.
        import yaml

        config_path = self.root / "source-config.yaml"
        config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
        geometry = {
            "target_order": list(MULTILABEL_TARGET_ORDER), "input_size": 336,
            "fill": [124, 116, 104], "candidates": [{
                "owner_approved": False, "source_id": "source-01",
                "member_sha256": member_key("train/images/image.png"),
                "source_sha256": hashlib.sha256(raw).hexdigest(),
                "draft_states": ["N", "N", "P", "U", "U"],
                "person_xyxy": [8, 3, 28, 18], "context_xyxy": [3, 0, 35, 20],
                "candidate_id": "D001", "reason": "Draft hints only", "review_id": "R001",
                "draft_scene_boundary": "unverified", "role_proposal": "unassigned",
                "phenotype": "source-review-software-fixture",
            }],
        }
        geometry_path = self.root / "geometry.json"
        geometry_path.write_text(json.dumps(geometry), encoding="utf-8")
        module_path = Path("src/ai_exam_monitoring/data/source_review.py")
        copied_module = self.root / module_path
        copied_module.parent.mkdir(parents=True)
        copied_module.write_bytes((Path(__file__).resolve().parents[1] / module_path).read_bytes())
        output = self.root / "data/interim/source-review"
        build_batch(config_path, geometry_path, sha256_file(geometry_path), output, self.root)
        proposal = json.loads((output / "D001/proposal.json").read_text(encoding="utf-8"))
        self.assertEqual(proposal["canonical_mask"], [0] * 5)
        self.assertEqual(proposal["input336_qa"], "pending_visual_review")
        self.assertFalse(proposal["owner_approved"])
        document = (output / "review.html").read_text(encoding="utf-8")
        self.assertIn("standing_up", document)
        self.assertIn("input 336", document)
        with self.assertRaises(DataContractError):
            build_batch(config_path, geometry_path, sha256_file(geometry_path), output, self.root)

    def test_existing_audit_handles_unlabelled_images_before_canonical_review(self):
        _, _, _, _, source = self.workspace()
        (source / "train/labels").mkdir()
        audit = audit_dataset(source, images_dir="train/images", labels_dir="train/labels",
                              source_names={0: "source-hint"})
        self.assertEqual(audit["image_count"], 1)
        self.assertEqual(len(audit["missing_labels"]), 1)
        self.assertIn("label_semantics", audit["checks"]["not_checked"])

    def test_existing_audit_review_and_package_workflow_uses_five_named_targets(self):
        item, config, summary, inventory, source_root = self.workspace()
        self.assertEqual(summary["total_accepted"], 0)
        self.assertEqual(summary["pending_review_ids"], [item.sample_id])
        self.assertEqual(summary["excluded"], [])
        self.assertEqual(inventory["target_order"], list(MULTILABEL_TARGET_ORDER))
        self.assertEqual(inventory["records"][0]["old_labels"], [None] * 5)
        with Image.open(self.root / "review/images/0000-336.png") as image:
            self.assertEqual(image.size, (336, 336))
        receipt = self.receipt(item, config)
        original = copy.deepcopy(receipt)
        result = accept_reviews([item], receipt, ledger_sha256=config["ledger_sha256"],
                                evidence_ref="owner-review.json", workspace=self.root)[0]
        self.assertEqual(receipt, original)
        self.assertEqual(result.target_values, (0, 0, 1, 0, 0))
        self.assertEqual(result.usage, "review_only")
        self.assertIsNone(result.group)
        self.assertIsNone(result.rights.review)
        self.assertIsNone(result.split)
        coverage = coverage_report([result])["all"]
        self.assertEqual(coverage["targets"]["sleeping"]["positive"], 1)
        self.assertEqual(coverage["fully_labeled"], 1)
        self.assertIsNone(coverage["cooccurrence"])
        with self.assertRaises(DataContractError):
            replace(result, usage="train", split="train")
        packaged = replace(
            result, source=replace(result.source, image_relpath="train/images/A001.png"),
            crop=replace(result.crop, crop_relpath="crops/A001.png"))
        build_pilot_package(
            [packaged], self.root / "package", {"rf": source_root},
            {"A001": self.root / item.crop.crop_relpath}, [],
            {"status": "prepared_pending_gates", "dataset_version": item.dataset_version,
             "git_commit": "synthetic-software-fixture"}, [item.sample_id])
        encoded = json.loads((self.root / "package/target-encoding.json").read_text())
        self.assertEqual(encoded["target_order"], list(MULTILABEL_TARGET_ORDER))
        self.assertEqual(read_records(self.root / "package/review-ledger.jsonl")[0].target_mask,
                         (1,) * 5)

    def test_package_release_gates_require_reviewed_support_for_new_targets_too(self):
        helper = test_pilot_package.PilotPackageTests()
        inputs = helper.accepted_fixture(self.root)
        rows = [five(row) for row in inputs["records"]]
        with self.assertRaises(DataContractError):
            build_pilot_package(output_dir=self.root / "missing-support", **{**inputs,
                                "records": rows})
        reviewed = []
        for index, row in enumerate(rows):
            states = (("positive", "positive", "negative", "positive", "positive") if index == 0
                      else ("negative", "negative", "positive", "negative", "negative"))
            targets = {name: TargetReview(state, "Synthetic owner decision", row.crop.review)
                       for name, state in zip(MULTILABEL_TARGET_ORDER, states, strict=True)}
            reviewed.append(replace(row, targets=targets, phone_use=targets["phone_use"],
                                   looking_around=targets["looking_around"]))
        build_pilot_package(output_dir=self.root / "software-fixture-package", **{**inputs,
                            "records": reviewed})
        coverage = coverage_report(reviewed)["all"]
        self.assertEqual(coverage["fully_labeled"], 2)
        self.assertEqual(coverage["targets"]["standing_up"]["positive"], 1)

    def receipt(self, item, config):
        return {
            "schema_version": "crop-review-acceptance-v2", "scope": "labels_and_geometry_only",
            "target_order": list(MULTILABEL_TARGET_ORDER),
            "ledger_sha256": config["ledger_sha256"], "reviewer": "owner",
            "reviewed_at": "2026-11-09", "decisions": [{
                "sample_id": item.sample_id,
                "targets": dict(zip(MULTILABEL_TARGET_ORDER, ("N", "N", "P", "N", "N"),
                                    strict=True)),
                "reason": "Owner reviewed source/crop/input", "geometry_accepted": True,
                "source_sha256": item.source.image_sha256, "crop_sha256": item.crop.crop_sha256,
                "input_relpath": "review/images/0000-336.png",
                "input_sha256": sha256_file(self.root / "review/images/0000-336.png"),
            }],
        }

    def test_review_conflict_stale_media_and_incomplete_map_are_rejected(self):
        item, config, _, _, _ = self.workspace()
        for change in ("conflict", "missing", "stale", "order"):
            receipt = self.receipt(item, config)
            decision = receipt["decisions"][0]
            if change == "conflict":
                decision["targets"]["looking_around"] = "P"
            elif change == "missing":
                decision["targets"].pop("hand_raising")
            elif change == "stale":
                decision["crop_sha256"] = "0" * 64
            else:
                receipt["target_order"].reverse()
            with self.subTest(change=change), self.assertRaises(DataContractError):
                accept_reviews([item], receipt, ledger_sha256=config["ledger_sha256"],
                               evidence_ref="owner-review.json", workspace=self.root)
        self.assertEqual(item.target_mask, (0,) * 5)

    def test_reconcile_retains_unreviewed_pending_and_never_fills_other_negatives(self):
        item, _, _, inventory, _ = self.workspace()
        review = {"schema": "crop-review-draft-v2", "cohort": inventory["cohort"],
                  "target_order": list(MULTILABEL_TARGET_ORDER), "decisions": {}}
        merged = merge_review([item], inventory, review)
        self.assertEqual(merged[0]["effective_pnu"], ["U"] * 5)
        self.assertEqual(apply_review_only_policy(merged)[0]["effective_action"], "keep")
        review["decisions"][item.sample_id] = {
            "sha256": item.crop.crop_sha256, "targets": {"phone_use": "N"}}
        self.assertEqual(merge_review([item], inventory, review)[0]["effective_pnu"],
                         ["N", "U", "U", "U", "U"])

    def test_reconcile_respects_approved_only_review_scope_in_a_mixed_ledger(self):
        item, config, _, _, _ = self.workspace()
        evidence = replace(reviewed_record().crop.review, crop_sha256=item.crop.crop_sha256)
        reviewed = replace(item, sample_id="A002", crop=replace(item.crop, person_id="person-02",
                           review=evidence), disposition="approved",
                           owner_decision_ref="owner-geometry-review")
        write_records(self.root / "review-ledger.jsonl", [item, reviewed])
        config.pop("include_pending")
        config.pop("expected_review")
        config.update(expected_accepted=1, output="approved-review", report="approved-report",
                      ledger_sha256=sha256_file(self.root / "review-ledger.jsonl"))
        config_path = self.root / "approved-config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        build(config_path, self.root)
        inventory = json.loads((self.root / "approved-review/inventory.json").read_text(
            encoding="utf-8"))
        review = {"schema": "crop-review-draft-v2", "cohort": inventory["cohort"],
                  "target_order": list(MULTILABEL_TARGET_ORDER), "decisions": {}}
        merged = merge_review([item, reviewed], inventory, review)
        self.assertEqual([row["id"] for row in merged], ["A002"])

    @unittest.skipUnless(importlib.util.find_spec("playwright") and
                         os.environ.get("RUN_DATA_REVIEW_BROWSER_TESTS") == "1",
                         "Opt-in: RUN_DATA_REVIEW_BROWSER_TESTS=1 and Chrome")
    def test_browser_five_targets_preview_export_and_legacy_two_targets(self):
        from playwright.sync_api import expect, sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="chrome", headless=True)
            page = browser.new_page(viewport={"width": 1600, "height": 1000})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("dialog", lambda dialog: dialog.accept() if dialog.type == "confirm"
                    else dialog.dismiss())
            for multi in (True, False):
                with tempfile.TemporaryDirectory() as folder:
                    original_root, self.root = self.root, Path(folder)
                    try:
                        self.workspace(multi)
                        page.goto((self.root / "review/index.html").as_uri())
                        expect(page.locator("#target-fields select")).to_have_count(
                            5 if multi else 2)
                        expect(page.locator("#input-caption")).to_contain_text(
                            "336" if multi else "224")
                        ids = MULTILABEL_TARGET_ORDER if multi else ("phone", "looking")
                        for name in ids:
                            expect(page.locator("#" + name)).to_have_value("")
                            page.select_option("#" + name, "N")
                        page.select_option("#action", "keep")
                        if multi:
                            page.select_option("#sleeping", "P")
                            page.select_option("#looking_around", "P")
                            page.click("#done")
                            expect(page.locator("#done")).not_to_be_checked()
                            expect(page.locator("#looking_around")).to_have_value("P")
                            page.select_option("#looking_around", "N")
                        page.check("#done")
                        expect(page.locator("#done")).to_be_checked()
                        with page.expect_download() as download:
                            page.click("#export")
                        path = self.root / "owner-draft.json"
                        download.value.save_as(path)
                        exported = json.loads(path.read_text(encoding="utf-8"))
                        self.assertEqual(exported["schema"], "crop-review-draft-v2" if multi
                                         else "crop-review-draft-v1")
                        if multi:
                            self.assertEqual(set(exported["decisions"]["A001"]["targets"]),
                                             set(MULTILABEL_TARGET_ORDER))
                        else:
                            self.assertIn("phone", exported["decisions"]["A001"])
                        page.evaluate("localStorage.clear()")
                        page.reload()
                        expect(page.locator("#done")).not_to_be_checked()
                        page.set_input_files("#import", path)
                        expect(page.locator("#done")).to_be_checked()
                        expect(page.locator("#" + ids[0])).to_have_value("N")
                    finally:
                        self.root = original_root
            browser.close()
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
