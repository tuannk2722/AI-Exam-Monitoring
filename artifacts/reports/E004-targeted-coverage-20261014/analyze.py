"""Analysis artifact for the frozen RC1 follow-up question; no model execution.

Uses existing codec, score validation and preprocess. This is a study worksheet,
not a new production CLI or a release/annotation pipeline.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import yaml
from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records
from ai_exam_monitoring.data.source_review import preview_input
from ai_exam_monitoring.training.data import letterbox
from ai_exam_monitoring.training.error_audit import prediction_errors, support

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "configs/datasets/E004-targeted-coverage-20261014.yaml"
cfg = yaml.safe_load(CONFIG.read_text(encoding="utf8"))
out, report = (ROOT / cfg[k] for k in ("output", "report"))
if out.exists():
    raise RuntimeError("Output exists; preserve the audit snapshot")
pins = {}


def pin(path):
    pins[path.relative_to(ROOT).as_posix()] = sha256_file(path)
    return path


def read(path):
    return json.loads(pin(path).read_text(encoding="utf8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


pin(CONFIG)
models = {}
for name, key in [("WH", "run"), ("LP", "reference")]:
    run = ROOT / cfg[key]
    checks = read(run / "checksums.json")
    config = read(run / "resolved-config.json")
    assert sha256_file(run / "resolved-config.json") == checks["resolved-config.json"]
    assert read(run / "run.json")["status"] == "FINISHED"
    models[name] = {}
    for cohort, split in [("train", "train"), ("selection", "val")]:
        path = run / f"predictions-{cohort}.json"
        assert sha256_file(path) == checks[path.name]
        rows = read(path)
        prediction_errors(rows, split, config["threshold"])
        assert all(r["target_order"] == ["phone_use", "looking_around"] for r in rows)
        spec = next(c for c in config["cohorts"] if c["name"] == cohort)
        assert {r["sample_id"] for r in rows} == set(spec["sample_ids"])
        models[name][cohort] = {r["sample_id"]: r for r in rows}
    if name == "WH":
        current = config

train_spec = next(c for c in current["cohorts"] if c["name"] == "train")
package = ROOT / train_spec["data"]["dataset"]
assert sha256_file(pin(package / "checksums.sha256")) == train_spec["data"]["payload_sha256"]
checks = dict(
    line.split("  ", 1)[::-1] for line in (package / "checksums.sha256").read_text().splitlines()
)
assert sha256_file(pin(package / "manifest.jsonl")) == checks["manifest.jsonl"]
records = {r.sample_id: r for r in read_records(package / "manifest.jsonl")}
prior = read(ROOT / cfg["prior_audit"] / "observations.json")
prior_inputs = read(ROOT / cfg["prior_audit"] / "review-inputs.json")
prior_map = {r["sample_id"]: r for r in prior["observations"]}
assert set(prior_map) <= models["WH"]["selection"].keys()
for item in prior_inputs["findings"]:
    assert item["crop_sha256"] == records[item["sample_id"]].crop.crop_sha256

matrix = []
for cohort in ("train", "selection"):
    assert models["WH"][cohort].keys() == models["LP"][cohort].keys()
    for sid, _score in sorted(models["WH"][cohort].items()):
        record = records[sid]
        assert record.split == ("train" if cohort == "train" else "val")
        assert record.usage == record.split and record.disposition == "approved"
        assert record.use_scope == "local_classifier_research"
        assert record.use_scope in record.rights.approved_use_scope
        assert record.crop is not None and record.group is not None
        for model in models:
            row = models[model][cohort][sid]
            assert row["targets"] == list(record.target_values)
            assert row["mask"] == list(record.target_mask)
            assert row["source_id"] == record.source.source_id
            assert row["group_id"] == record.group.leakage_group_id
        reasons = [record.phone_use.reason, record.looking_around.reason]
        hints = {}
        for factor, rule in cfg["factors"].items():
            target = rule["target"]
            text = " ".join(reasons).casefold()
            matches = [term for term in rule["terms"] if term.casefold() in text]
            if matches and (target is None or record.target_values[target] == rule["state"]):
                hints[factor] = matches
        box = record.crop.context_box
        size = [box.xmax - box.xmin, box.ymax - box.ymin]
        outcomes = {}
        for model in models:
            row = models[model][cohort][sid]
            outcomes[model] = [
                "U" if y is None else ("TP" if d else "FN") if y else ("FP" if d else "TN")
                for y, d in zip(row["targets"], row["decisions"], strict=True)
            ]
        matrix.append(
            dict(
                sample_id=sid,
                cohort=cohort,
                source=record.source.source_id,
                family=record.group.leakage_group_id,
                source_sha256=record.source.image_sha256,
                crop_path=(package / record.crop.crop_relpath).relative_to(ROOT).as_posix(),
                crop_sha256=record.crop.crop_sha256,
                native_size=size,
                scale_224=224 / max(size),
                labels=list(record.target_values),
                reasons=reasons,
                work_context=record.work_context_review.state,
                metadata_hints=hints,
                no_hint_means="unassessed_not_absent",
                outcomes=outcomes,
                scores={m: models[m][cohort][sid]["scores"] for m in models},
                prior_draft_observation=prior_map.get(sid),
                review_reasons=[],
            )
        )

train = [r for r in matrix if r["cohort"] == "train"]
assert len(train) == 716 and len(matrix) == 787
assert not (models["WH"]["train"].keys() & models["WH"]["selection"].keys())


def choose(pool, count, reason):
    # Deterministic coverage first; scores only prioritize within available families.
    ordered = sorted(
        pool, key=lambda r: (-sum(v in ("FN", "FP") for v in r["outcomes"]["WH"]), r["sample_id"])
    )
    selected, families = [], set()
    for diverse in (True, False):
        for r in ordered:
            if r in selected or (diverse and r["family"] in families):
                continue
            selected.append(r)
            families.add(r["family"])
            if len(selected) >= count:
                break
        if len(selected) >= count:
            break
    for r in selected:
        r["review_reasons"].append(reason)


for source in sorted({r["source"] for r in train}):
    choose(
        [r for r in train if r["source"] == source],
        cfg["shortlist"]["per_source"],
        f"source:{source}",
    )
for factor in cfg["factors"]:
    pool = [r for r in train if factor in r["metadata_hints"]]
    choose(
        pool,
        len(pool) if factor == "calculator_negative" else cfg["shortlist"]["per_factor"],
        f"hint:{factor}",
    )
for target in range(2):
    for state in (0, 1, None):
        choose(
            [r for r in train if r["labels"][target] == state],
            cfg["shortlist"]["per_target_state"],
            f"target:{target}:state:{state}",
        )
shortlist = [r for r in train if r["review_reasons"]]
for r in matrix:
    if r["cohort"] == "selection" and r["sample_id"] in prior_map:
        r["review_reasons"].append("prior_visual_audit_31")

summary = {
    "status": "draft_pending_owner_review",
    "cohorts": {},
    "hint_matrix": {},
    "review_train_count": len(shortlist),
    "prior_selection_review_count": len(prior_map),
}
for cohort in ("train", "selection"):
    rows = [r for r in matrix if r["cohort"] == cohort]
    summary["cohorts"][cohort] = dict(
        count=len(rows),
        sources=dict(Counter(r["source"] for r in rows)),
        families=len({r["family"] for r in rows}),
        family_counts=dict(Counter(r["family"] for r in rows)),
        work_context=dict(Counter(r["work_context"] for r in rows)),
        native_long_edge_le_224=sum(max(r["native_size"]) <= 224 for r in rows),
        no_factor_hints=sum(not r["metadata_hints"] for r in rows),
        support={m: support(list(models[m][cohort].values()), 0.5) for m in models},
    )
    summary["hint_matrix"][cohort] = {}
    for factor in cfg["factors"]:
        subset = [r for r in rows if factor in r["metadata_hints"]]
        summary["hint_matrix"][cohort][factor] = dict(
            n=len(subset),
            families=len({r["family"] for r in subset}),
            sources=dict(Counter(r["source"] for r in subset)),
            sample_ids=[r["sample_id"] for r in subset],
        )

out.mkdir(parents=True)
(out / "inputs224").mkdir()
(out / "boards").mkdir()
font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
panels = []
media_hashes = {}
for r in shortlist:
    path = ROOT / r["crop_path"]
    assert sha256_file(path) == r["crop_sha256"] == checks[path.relative_to(package).as_posix()]
    with Image.open(path) as image:
        image = image.convert("RGB")
        assert list(image.size) == r["native_size"]
        prepared = preview_input(image, 224, tuple(current["fill"]))
        exact = letterbox(image, SimpleNamespace(image_size=224, fill=tuple(current["fill"])))
        assert prepared.tobytes() == exact.tobytes()
        destination = out / "inputs224" / f"{r['sample_id']}.png"
        prepared.save(destination)
        media_hashes[destination.relative_to(out).as_posix()] = sha256_file(destination)
        panel = Image.new("RGB", (600, 330), "white")
        draw = ImageDraw.Draw(panel)
        draw.text((8, 4), r["sample_id"] + " | " + str(r["labels"]), fill="black", font=font)
        draw.text((8, 25), r["source"] + " | " + str(image.size), fill="black", font=font)
        draw.text((8, 46), "Native fit <=340x264  |  Exact 224 (right)", fill="black", font=font)
        thumb = image.copy()
        thumb.thumbnail((340, 264))
        panel.paste(thumb, (8, 66))
        panel.paste(prepared, (368, 75))
        panels.append(panel)
for index in range(0, len(panels), 6):
    board = Image.new("RGB", (1200, 990), "#ddd")
    for j, panel in enumerate(panels[index : index + 6]):
        board.paste(panel, ((j % 2) * 600, (j // 2) * 330))
    path = out / "boards" / f"{index // 6 + 1:02}.jpg"
    board.save(path, quality=94)
    media_hashes[path.relative_to(out).as_posix()] = sha256_file(path)

write(report / "matrix.json", {"status": "metadata_hints_not_visual_ground_truth", "rows": matrix})
write(report / "summary.json", summary)
write(
    report / "shortlist.json",
    {
        "status": "draft_pending_owner_review",
        "train_ids": [r["sample_id"] for r in shortlist],
        "selection_ids": sorted(prior_map),
        "note": "Purposive shortlist; no prevalence/generalization claim.",
    },
)
write(report / "input-pins.json", pins)
write(out / "media-checksums.json", media_hashes)
write(
    report / "verification.json",
    dict(
        status="PASS",
        checked_prediction_files=4,
        membership=[716, 71],
        checked_manifest_and_payload_pins=True,
        checked_labels_masks_groups_sources=True,
        cropped_media_decoded=len(shortlist),
        exact_input_pixel_parity=len(shortlist),
        test_reserve_media_accessed=False,
        new_inference=False,
        label_changes=False,
        scope_note=("Manifest includes other splits; only exact train/selection membership used."),
    ),
)
print(json.dumps(summary, ensure_ascii=False, indent=2))
