"""Read-only, multi-run diagnostics from pinned train/val predictions."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageOps

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import TARGET_ORDER, PilotRecord, read_records
from ai_exam_monitoring.training.error_audit import prediction_errors


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def local(root: Path, value: str) -> Path:
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise DataContractError("Path outside workspace")
    return path


def outcome(row: dict[str, Any], target: int, threshold: float) -> str:
    if not row["mask"][target]:
        return "U"
    positive = row["targets"][target] == 1
    predicted = row["scores"][target] >= threshold
    return ("TP" if predicted else "FN") if positive else ("FP" if predicted else "TN")


def coverage(records: list[PilotRecord]) -> dict[str, Any]:
    result: dict[str, Any] = {"records": len(records), "targets": {}}
    for t, name in enumerate(TARGET_ORDER):
        states = {}
        for state, value in (("P", 1), ("N", 0), ("U", None)):
            selected = [r for r in records if r.target_values[t] == value]
            states[state] = {
                "records": len(selected),
                "groups": len({r.group.leakage_group_id for r in selected if r.group}),
            }
        result["targets"][name] = states
    result["joint_states"] = dict(Counter(
        "/".join("U" if v is None else "P" if v else "N" for v in r.target_values)
        for r in records
    ))
    return result


def operating_envelope(rows: list[dict[str, Any]], target: int) -> dict[str, Any]:
    """Describe attainable gates from cached scores; never install a new threshold."""
    known = [r for r in rows if r["mask"][target]]
    p = sum(r["targets"][target] == 1 for r in known)
    n = len(known) - p
    if not p or not n:
        return {"positive": p, "negative": n, "feasible_80_80_20": None,
                "max_precision_at_recall_ge80": None,
                "max_recall_at_precision_ge80": None}
    points = []
    for cut in sorted({0., .5, math.nextafter(1., 2.),
                       *(r["scores"][target] for r in known)}):
        counts = Counter(outcome(r, target, cut) for r in known)
        tp, fp = counts["TP"], counts["FP"]
        precision = tp / (tp + fp) if tp + fp else None
        points.append((precision, tp / p, fp / n))
    return {
        "positive": p, "negative": n,
        "feasible_80_80_20": any(pr is not None and pr >= .8 and re >= .8 and fpr <= .2
                                      for pr, re, fpr in points),
        "max_precision_at_recall_ge80": max(
            (pr for pr, re, _ in points if pr is not None and re >= .8), default=None),
        "max_recall_at_precision_ge80": max(
            (re for pr, re, _ in points if pr is not None and pr >= .8), default=None),
    }


def consensus(
    predictions: dict[str, dict[str, dict[str, Any]]],
    thresholds: dict[str, list[float]],
    runs: list[str],
) -> list[dict[str, Any]]:
    if not runs or len(set(runs)) != len(runs):
        raise DataContractError("Empty or duplicate run list")
    ids = set(predictions[runs[0]])
    if any(set(predictions[run]) != ids for run in runs):
        raise DataContractError("Unmatched cohort")
    result = []
    for sid in sorted(ids):
        first = predictions[runs[0]][sid]
        if first["split"] not in {"train", "val"}:
            raise DataContractError("Diagnostics excludes test")
        for run in runs:
            row = predictions[run][sid]
            if any(row[key] != first[key] for key in
                   ("targets", "mask", "source_id", "group_id", "split")):
                raise DataContractError("Unmatched labels/masks/source/group/split")
        for target, name in enumerate(TARGET_ORDER):
            outcomes = {run: outcome(predictions[run][sid], target, thresholds[run][target])
                        for run in runs}
            scores = {run: predictions[run][sid]["scores"][target] for run in runs}
            result.append({
                "sample_id": sid, "target": name, "split": first["split"],
                "source_id": first["source_id"], "group_id": first["group_id"],
                "state": "U" if not first["mask"][target] else
                "P" if first["targets"][target] else "N",
                "outcomes": outcomes, "scores": scores,
                "error_count": sum(o in {"FP", "FN"} for o in outcomes.values()),
                "stable_outcome": next(iter(outcomes.values()))
                if len(set(outcomes.values())) == 1 else "mixed",
                "mean_margin": sum(abs(scores[r] - thresholds[r][target]) for r in runs)
                / len(runs),
            })
    return result


def shortlist(rows: list[dict[str, Any]], per_bucket: int) -> list[dict[str, Any]]:
    """Diverse source/group first; margin prioritizes errors, never changes labels."""
    chosen: dict[str, dict[str, Any]] = {}
    for target in TARGET_ORDER:
        for category in ("FP", "FN", "TP", "TN", "U"):
            candidates = [r for r in rows if r["target"] == target
                          and r["stable_outcome"] == category]
            candidates.sort(key=lambda r: (-r["mean_margin"], r["sample_id"]))
            count = per_bucket if category in {"FP", "FN"} else 2
            groups: set[str] = set()
            sources: set[str] = set()
            picked: set[str] = set()
            for diverse in (True, False):
                for row in candidates:
                    if len(picked) >= count:
                        break
                    sid = row["sample_id"]
                    if sid in picked or row["group_id"] in groups:
                        continue
                    if diverse and row["source_id"] in sources:
                        continue
                    picked.add(sid)
                    groups.add(row["group_id"])
                    sources.add(row["source_id"])
                    item = chosen.setdefault(sid, {"sample_id": sid, "reasons": []})
                    item["reasons"].append(f"{target}:{category}")
    return list(chosen.values())


def build(workspace: Path, config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    package = local(workspace, config["package"])
    output = local(workspace, config["report_output"])
    media = local(workspace, config["media_output"])
    if (output.exists() or media.exists()
            or not output.is_relative_to(workspace / "artifacts/reports")
            or not media.is_relative_to(workspace / "data/interim")):
        raise DataContractError("Fresh report and interim output paths required")
    pins = {}

    def pin(path: Path, expected: str | None = None) -> None:
        digest = sha256_file(path)
        if expected is not None and digest != expected:
            raise DataContractError(f"SHA mismatch: {path.name}")
        pins[path.relative_to(workspace).as_posix()] = digest

    pin(config_path)
    for name in ("diagnostics.py", "adaptation_data.py", "adaptation_config.py", "data.py"):
        pin(workspace / "src/ai_exam_monitoring/training" / name)
    pin(package / "checksums.sha256", config["payload_sha256"])
    inventory = dict(line.split("  ", 1)[::-1] for line in
                     (package / "checksums.sha256").read_text().splitlines() if line)
    pin(package / "manifest.jsonl", inventory["manifest.jsonl"])
    # Read metadata only; never decode, score, select or display test media.
    records = [r for r in read_records(package / "manifest.jsonl")
               if r.usage in {"train", "val"}]
    by_id = {r.sample_id: r for r in records}
    if len(by_id) != len(records):
        raise DataContractError("Duplicate manifest IDs")
    predictions: dict[str, dict[str, dict[str, Any]]] = {}
    thresholds = {}
    run_configs = {}
    parity = []
    run_root = local(workspace, config.get("run_root", "outputs"))
    for run_name in config["runs"]:
        run = local(run_root, run_name)
        pin(run / "checksums.json", config["run_checksum_pins"][run_name])
        hashes = read_json(run / "checksums.json")
        for name in ("run.json", "resolved-config.json", "metrics.json",
                     "predictions-train.json", "predictions-selection.json"):
            pin(run / name, hashes[name])
        if read_json(run / "run.json")["status"] != "FINISHED":
            raise DataContractError("Run unfinished")
        rc = read_json(run / "resolved-config.json")
        run_configs[run_name] = rc
        if rc["experiment_id"] != run_name:
            raise DataContractError("Run identity mismatch")
        metrics = read_json(run / "metrics.json")
        merged = {}
        for split, suffix, metric_key in (("train", "train", "train"),
                                          ("val", "selection", "selection")):
            rows = read_json(run / f"predictions-{suffix}.json")
            prediction_errors(rows, split, rc["threshold"])
            expected_ids = {r.sample_id for r in records if r.usage == split}
            cohort = next(c for c in rc["cohorts"] if c["role"] == suffix)
            if (set(cohort["sample_ids"]) != expected_ids
                    or cohort["data"]["dataset"] != config["package"]
                    or cohort["data"]["payload_sha256"] != config["payload_sha256"]
                    or {r["sample_id"] for r in rows} != expected_ids):
                raise DataContractError("Dataset/cohort membership mismatch")
            mr = metrics[metric_key]
            ts = [mr["calibrated_thresholds"][target] for target in TARGET_ORDER]
            is_v4 = rc["schema_version"] == "representation-adaptation-v4"
            if any(type(t) not in {int, float} or not math.isfinite(t)
                   or not (0 <= t <= math.nextafter(1., 2.) if is_v4 else 0 < t < 1)
                   for t in ts):
                raise DataContractError("Invalid calibrated threshold")
            if is_v4 and mr["calibrated_thresholds"] != metrics["selection"][
                    "calibrated_thresholds"]:
                raise DataContractError("V4 thresholds must be reused from selection")
            for row in rows:
                rec = by_id[row["sample_id"]]
                if (row["targets"] != list(rec.target_values)
                        or row["mask"] != list(rec.target_mask) or rec.group is None
                        or row["source_id"] != rec.source.source_id
                        or row["group_id"] != rec.group.leakage_group_id
                        or row["target_order"] != list(TARGET_ORDER)
                        or row["calibrated_thresholds"] != ts
                        or row["calibrated_decisions"] !=
                        [row["scores"][i] >= ts[i] for i in range(2)]):
                    raise DataContractError("Prediction manifest/calibration mismatch")
                merged[row["sample_id"]] = row
            for i, target in enumerate(TARGET_ORDER):
                for mode, cut in (("fixed", rc["threshold"]), ("calibrated", ts[i])):
                    counts = Counter(outcome(row, i, cut) for row in rows)
                    saved = (mr if mode == "fixed" else mr["calibrated_evaluation"])
                    for key in ("TP", "FP", "FN", "TN"):
                        if counts[key] != saved["targets"][target][key.lower()]:
                            raise DataContractError("Confusion parity failure")
                    parity.append({"run": run_name, "split": split, "target": target,
                                   "mode": mode, "counts": dict(counts)})
            if split == "val":
                thresholds[run_name] = ts
        predictions[run_name] = merged
    analyses = {}
    for recipe, runs in config["recipes"].items():
        for mode, cuts in (("calibrated", thresholds),
                           ("fixed", {r: [run_configs[r]["threshold"]] * 2 for r in runs})):
            analyses[f"{recipe}_{mode}"] = consensus(predictions, cuts, runs)
    cov = {}
    for split in ("train", "val"):
        subset = [r for r in records if r.usage == split]
        cov[split] = {
            "overall": coverage(subset),
            "by_source": {s: coverage([r for r in subset if r.source.source_id == s])
                          for s in sorted({r.source.source_id for r in subset})},
        }
    reference = config["reference_recipe"]
    rows = analyses[f"{reference}_calibrated"]
    selected = shortlist([r for r in rows if r["split"] == "val"], config["errors_per_bucket"])
    # Train controls provide looking U (absent from val) and actual training augmentation.
    train_controls = shortlist([r for r in rows if r["split"] == "train"
                                and r["stable_outcome"] in {"TP", "TN", "U"}], 0)
    selected.extend(train_controls)
    # Explicit audit cases supplement the diverse shortlist without losing same-group errors.
    selected_ids = {r["sample_id"] for r in selected}
    for sid in config.get("review_sample_ids", []):
        if sid not in by_id:
            raise DataContractError("Review ID outside train/val cohort")
        if sid not in selected_ids:
            selected.append({"sample_id": sid, "reasons": ["explicit_audit_case"]})
            selected_ids.add(sid)
    output.mkdir(parents=True)
    media.mkdir(parents=True)
    write_json(output / "coverage.json", cov)
    write_json(media / "consensus.json", analyses)
    write_json(output / "recurrent-errors.json", {
        k: [r for r in values if r["split"] == "val" and r["error_count"] >= 2]
        for k, values in analyses.items()
    })
    write_json(output / "confusion-parity.json", parity)
    write_json(output / "operating-envelopes.json", {
        run: {split: {target: operating_envelope(
            [r for r in members.values() if r["split"] == split], i)
                      for i, target in enumerate(TARGET_ORDER)} for split in ("train", "val")}
        for run, members in predictions.items()
    })
    make_gallery(workspace, package, media, selected, by_id, run_configs,
                 config, pin)
    write_json(output / "review-selection.json", selected)
    summary = {}
    for key, values in analyses.items():
        summary[key] = {split: {target: dict(Counter(
            r["stable_outcome"] for r in values if r["split"] == split
            and r["target"] == target)) for target in TARGET_ORDER} for split in ("train", "val")}
    write_json(output / "summary.json", summary)
    write_json(output / "input-pins.json", pins)
    write_json(output / "local-artifacts.json", {
        p.relative_to(workspace).as_posix(): sha256_file(p)
        for p in sorted(media.iterdir()) if p.is_file()
    })
    return summary


def make_gallery(
    workspace: Path, package: Path, media: Path, selected: list[dict[str, Any]],
    records: dict[str, PilotRecord], run_configs: dict[str, Any], config: dict[str, Any],
    pin: Any,
) -> None:
    import torch

    from .adaptation_config import E005AdaptationConfig, config_from_dict
    from .adaptation_data import ImageCohort
    from .data import letterbox

    ref = config["recipes"][config["reference_recipe"]][0]
    rc = config_from_dict(run_configs[ref])
    if not isinstance(rc, E005AdaptationConfig):
        raise DataContractError("Gallery requires v3 config")
    roots_path = local(workspace, config["source_roots"])
    pin(roots_path, config["source_roots_sha256"])
    roots = read_json(roots_path)
    train_spec = next(c for c in rc.cohorts if c.role == "train")
    train = [records[sid] for sid in train_spec.sample_ids]
    cohort = ImageCohort("train", "train", train,
                         [package / r.crop.crop_relpath for r in train if r.crop],
                         torch.tensor([[v or 0 for v in r.target_values] for r in train]),
                         torch.tensor([r.target_mask for r in train], dtype=torch.bool),
                         [str(r.group.leakage_group_id) for r in train if r.group])
    train_ids = [r.sample_id for r in train]
    cards = []
    size = rc.image_size
    panel_width = max(340, size)
    card_height = max(245, size) + 65
    page = ["<!doctype html><meta charset='utf-8'><title>Review Draft</title>",
            "<style>body{font:16px sans-serif;margin:24px}img{max-width:100%}</style>",
            f"<h1>Review Draft — source / crop / input {size} / augmentation train</h1>",
            "<p>Không hiển thị scores hoặc nhãn để review độc lập với dự đoán. "
            f"Ảnh nguồn có box anchor xanh và context đỏ. Input hiển thị đúng {size} px. "
            "Augmentation chỉ train, epoch đã ghi; val không augmentation.</p>"]
    for index, item in enumerate(selected):
        rec = records[item["sample_id"]]
        if rec.usage not in {"train", "val"} or rec.crop is None:
            raise DataContractError("Gallery refuses test or missing crop")
        crop_path = local(package, rec.crop.crop_relpath)
        source_path = local(workspace, str(Path(roots[rec.source.source_id])
                                            / rec.source.image_relpath))
        pin(crop_path, rec.crop.crop_sha256)
        pin(source_path, rec.source.image_sha256)
        with Image.open(source_path) as raw:
            source = raw.convert("RGB")
        with Image.open(crop_path) as raw:
            crop = raw.convert("RGB")
            crop_format = raw.format
        if source.size != (rec.source.image_width, rec.source.image_height):
            raise DataContractError("Source dimensions mismatch")
        native_box = rec.crop.context_box
        native = source.crop((native_box.xmin, native_box.ymin,
                              native_box.xmax, native_box.ymax))
        native_equal = native.size == crop.size and native.tobytes() == crop.tobytes()
        if not native_equal and rec.crop.derivation is None:
            raise DataContractError("Native ROI mismatch without derivation")
        derived = rec.crop.derivation
        if derived is not None and (
            hashlib.sha256(native.tobytes()).hexdigest() != derived.native_roi_rgb_sha256
            or source.size != (rec.source.image_width, rec.source.image_height)
            or derived.source_sha256 != rec.source.image_sha256
            or crop.size != (derived.output_width, derived.output_height)
            or crop_format != derived.output_format
        ):
            raise DataContractError("Derived ROI provenance mismatch")
        item.update(split=rec.usage, crop_sha256=rec.crop.crop_sha256,
                    source_sha256=rec.source.image_sha256, source_id=rec.source.source_id,
                    crop_size=list(crop.size), native_roi_equal=native_equal,
                    has_derivation=rec.crop.derivation is not None,
                    current_states=list(rec.target_values),
                    reasons_current=[rec.phone_use.reason, rec.looking_around.reason])
        draw = ImageDraw.Draw(source)
        for box, color in ((rec.crop.context_box, "red"), (rec.crop.person_box, "lime")):
            draw.rectangle((box.xmin, box.ymin, box.xmax - 1, box.ymax - 1),
                           outline=color, width=max(2, source.width // 300))
        card = Image.new("RGB", (4 * (panel_width + 12), card_height), "white")
        d = ImageDraw.Draw(card)
        d.text((8, 8), f"{index + 1:02d} {rec.sample_id} | {rec.usage}", fill="black")
        panels = [ImageOps.contain(source, (340, 245)),
                  ImageOps.contain(crop, (340, 245)), letterbox(crop, rc)]
        positions = [8 + i * (panel_width + 12) for i in range(4)]
        titles = ["Source + anchor/context", f"Crop {crop.width}x{crop.height}", f"Input {size}"]
        if rec.usage == "train":
            idx = train_ids.index(rec.sample_id)
            epoch = config["augmentation_epoch"]
            batch = cohort.model_batch([idx], rc, epoch=epoch, train_mode=True)
            if not isinstance(batch, torch.Tensor):
                raise DataContractError("Expected single crop")
            restored = batch[0] * torch.tensor(rc.std).view(3, 1, 1)
            restored += torch.tensor(rc.mean).view(3, 1, 1)
            panels.append(Image.fromarray(
                (restored.clamp(0, 1).permute(1, 2, 0).numpy() * 255).astype("uint8")
            ))
            titles.append(f"Train aug epoch {epoch}")
            item["augmentation"] = {"run": ref, "epoch": epoch, "cohort_index": idx}
            epochs = config["augmentation_epochs"]
            aug_sheet = Image.new("RGB", (6 * size, math.ceil(len(epochs) / 6) * (size + 22)),
                                  "white")
            aug_draw = ImageDraw.Draw(aug_sheet)
            for ep_index, ep in enumerate(epochs):
                aug_batch = cohort.model_batch([idx], rc, epoch=ep, train_mode=True)
                if not isinstance(aug_batch, torch.Tensor):
                    raise DataContractError("Expected single crop")
                pixels = aug_batch[0] * torch.tensor(rc.std).view(3, 1, 1)
                pixels += torch.tensor(rc.mean).view(3, 1, 1)
                aug_image = Image.fromarray(
                    (pixels.clamp(0, 1).permute(1, 2, 0).numpy() * 255).astype("uint8")
                )
                x, y = (ep_index % 6) * size, (ep_index // 6) * (size + 22)
                aug_draw.text((x, y), f"{rec.sample_id} epoch {ep}", fill="black")
                aug_sheet.paste(aug_image, (x, y + 22))
            aug_name = f"augmentation-{index + 1:03d}.png"
            aug_sheet.save(media / aug_name)
            item["augmentation"]["epochs"] = epochs
            item["augmentation"]["sheet"] = (media / aug_name).relative_to(workspace).as_posix()
        for x, panel, title in zip(positions, panels, titles, strict=False):
            d.text((x, 33), title, fill="black")
            card.paste(panel, (x, 55))
        filename = f"card-{index + 1:03d}.png"
        card.save(media / filename)
        item["card"] = (media / filename).relative_to(workspace).as_posix()
        item["card_sha256"] = sha256_file(media / filename)
        page.append(f"<h2>{index + 1:02d} {html.escape(rec.sample_id)}</h2>"
                    f"<img src='{filename}' loading='lazy'>")
        cards.append(card)
    for offset in range(0, len(cards), 4):
        sheet = Image.new("RGB", (cards[offset].width,
                                 card_height * len(cards[offset:offset + 4])), "white")
        for i, card in enumerate(cards[offset:offset + 4]):
            sheet.paste(card, (0, card_height * i))
        sheet.save(media / f"sheet-{offset // 4 + 1:02d}.png")
    (media / "index.html").write_text("\n".join(page), encoding="utf8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    build(args.workspace.resolve(), args.config.resolve())


if __name__ == "__main__":
    main()
