"""Deterministic local packages for reviewed multi-label crops and pending QA.

This exporter consumes reviewed records. It never selects candidates, creates
labels, infers leakage groups, assigns splits, or signs a dataset release.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from PIL import Image

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .pilot_schema import PilotRecord, validate_records, write_records

SPLITS = ("train", "val", "test")
STATES = ("positive", "negative", "unknown")
TARGETS = ("phone_use", "looking_around")


def _json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _jsonl(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"
            for row in rows
        ),
        encoding="utf-8",
        newline="\n",
    )


def _source_file(root: Path, relative: str) -> Path:
    file = (root / relative).resolve()
    if Path(relative).is_absolute() or not file.is_relative_to(root):
        raise DataContractError(f"Source path escapes its root: {relative}")
    if not file.is_file():
        raise DataContractError(f"Missing source file: {relative}")
    return file


def _preflight(
    records: Sequence[PilotRecord],
    source_roots: Mapping[str, str | Path],
    crop_inputs: Mapping[str, str | Path],
) -> dict[str, Path]:
    """Check all source/crop bytes before writing any package output."""
    roots = {key: Path(value).resolve() for key, value in source_roots.items()}
    sources: dict[str, Path] = {}
    seen: dict[Path, tuple[str, tuple[int, int]]] = {}
    ids = {record.sample_id for record in records}
    if set(crop_inputs) - ids:
        raise DataContractError("Crop inputs contain IDs outside the decision ledger")
    for record in records:
        source = record.source
        if source.source_id not in roots:
            raise DataContractError(f"Missing source root: {source.source_id}")
        file = _source_file(roots[source.source_id], source.image_relpath)
        if file not in seen:
            with Image.open(file) as image:
                image.load()
                seen[file] = (sha256_file(file), image.size)
        image_hash, size = seen[file]
        if image_hash != source.image_sha256:
            raise DataContractError(f"Source image checksum changed: {record.sample_id}")
        if size != (source.image_width, source.image_height):
            raise DataContractError(f"Source image dimensions changed: {record.sample_id}")
        if source.label_relpath is not None:
            label = _source_file(roots[source.source_id], source.label_relpath)
            if sha256_file(label) != source.label_sha256:
                raise DataContractError(f"Source label checksum changed: {record.sample_id}")
        sources[record.sample_id] = file
        if record.crop is None:
            if record.sample_id in crop_inputs:
                raise DataContractError("Cannot supply crop bytes without crop geometry/review")
            continue
        crop = record.crop
        if record.sample_id in crop_inputs:
            input_crop = Path(crop_inputs[record.sample_id]).resolve()
            if not input_crop.is_file() or sha256_file(input_crop) != crop.crop_sha256:
                raise DataContractError(f"Approved crop checksum changed: {record.sample_id}")
            with Image.open(input_crop) as image, Image.open(file) as original:
                expected = original.convert("RGB").crop(crop.context_box.xyxy)
                actual = image.convert("RGB")
                if actual.size != expected.size or actual.tobytes() != expected.tobytes():
                    raise DataContractError(
                        f"Crop pixels do not match source coordinates: {record.sample_id}"
                    )
        elif crop.review is not None:
            # A new reviewed crop is reproduced from its rectangle; its checksum
            # must have been recorded by the reviewer/producer, never filled here.
            with Image.open(file) as image:
                cropped = image.convert("RGB").crop(crop.context_box.xyxy)
                buffer = io.BytesIO()
                cropped.save(buffer, format="PNG")
            if hashlib.sha256(buffer.getvalue()).hexdigest() != crop.crop_sha256:
                raise DataContractError(f"Rebuilt crop checksum differs: {record.sample_id}")
    return sources


def coverage_report(records: Sequence[PilotRecord]) -> dict[str, Any]:
    """Counts only reviewed states; metric support is reported without metrics."""
    slices: dict[tuple[str, str, str], list[PilotRecord]] = defaultdict(list)
    for record in records:
        slices[
            (
                record.source.source_id,
                record.split or "unassigned",
                record.group.leakage_group_id
                if record.group and record.group.leakage_group_id
                else "unresolved",
            )
        ].append(record)

    def counts(rows: Sequence[PilotRecord]) -> dict[str, Any]:
        states = {
            target: {
                state: sum(getattr(row, target).state == state for row in rows) for state in STATES
            }
            for target in TARGETS
        }
        support = {
            target: {
                "known": sum(states[target][state] for state in ("positive", "negative")),
                "unknown_ignored": states[target]["unknown"],
                "binary_metric_support": (
                    "available"
                    if states[target]["positive"] and states[target]["negative"]
                    else "unavailable_missing_positive_or_negative"
                ),
            }
            for target in TARGETS
        }
        return {
            "records": len(rows),
            "targets": states,
            "support": support,
            "cooccurrence": sum(
                all(getattr(row, t).state == "positive" for t in TARGETS) for row in rows
            ),
            "confirmed_normal": sum(row.normal_review == "confirmed_normal" for row in rows),
            "fully_labeled": sum(sum(row.target_mask) == 2 for row in rows),
            "partially_labeled": sum(sum(row.target_mask) == 1 for row in rows),
            "fully_unknown": sum(sum(row.target_mask) == 0 for row in rows),
        }

    return {
        "all": counts(records),
        "usage": dict(sorted(Counter(row.usage for row in records).items())),
        "disposition": dict(sorted(Counter(row.disposition for row in records).items())),
        "slices": [
            {"source_id": source, "split": split, "leakage_group_id": group, **counts(rows)}
            for (source, split, group), rows in sorted(slices.items())
        ],
        "split_support": {
            split: counts([row for row in records if row.split == split]) for split in SPLITS
        },
        "domain_limitations": [
            "Counts do not establish independent situations or real-exam generalization.",
            "Source labels and source quotas are not canonical target labels.",
            "Unknown targets are excluded from supervision and per-target metrics.",
        ],
    }


def leakage_report(records: Sequence[PilotRecord]) -> dict[str, Any]:
    image_members: dict[str, list[PilotRecord]] = defaultdict(list)
    for record in records:
        image_members[record.source.image_sha256].append(record)
    return {
        "exact_image_clusters": [
            {"image_sha256": digest, "sample_ids": sorted(row.sample_id for row in rows)}
            for digest, rows in sorted(image_members.items())
            if len(rows) > 1
        ],
        "unresolved_group_ids": sorted(
            row.sample_id
            for row in records
            if row.disposition != "excluded"
            and (row.group is None or not row.group.leakage_group_id or row.group.review is None)
        ),
        "independence_inferred_from_unique_hash": False,
        "near_duplicates_and_cross_source_relations": "owner_review_required",
    }


def _release_gates(records: Sequence[PilotRecord], metadata: Mapping[str, Any]) -> None:
    state = metadata.get("status")
    if state not in {"prepared_pending_gates", "accepted"}:
        raise DataContractError("Package status must be prepared_pending_gates or accepted")
    if state == "prepared_pending_gates":
        if any(
            row.usage not in {"review_only", "excluded"} or row.split is not None for row in records
        ):
            raise DataContractError("Pending package cannot contain train/val/test assignments")
        return
    for field in (
        "owner_decision_ref",
        "schema_config_review_ref",
        "split_config_review_ref",
        "test_freeze_ref",
        "leakage_review_ref",
    ):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            raise DataContractError(f"Accepted export requires {field}")
    used = [row for row in records if row.usage in SPLITS]
    if any(row.disposition == "pending" for row in records):
        raise DataContractError("Accepted export requires a decision for every candidate")
    if (
        not isinstance(metadata.get("config_sha256"), str)
        or re.fullmatch(r"[0-9a-f]{64}", metadata["config_sha256"]) is None
    ):
        raise DataContractError("Accepted export requires pinned config_sha256")
    scope = metadata.get("approved_use_scope")
    if (
        not isinstance(scope, (list, tuple))
        or not scope
        or any(not isinstance(item, str) or not item.strip() for item in scope)
    ):
        raise DataContractError("Accepted export requires explicit approved_use_scope")
    if any(tuple(scope) != row.rights.approved_use_scope for row in used):
        raise DataContractError("Release use scope differs from reviewed record rights")
    use_scope = metadata.get("use_scope")
    if (
        not isinstance(use_scope, str)
        or use_scope not in scope
        or any(row.use_scope != use_scope for row in used)
    ):
        raise DataContractError("Accepted export action use_scope differs from row authorization")
    if len({row.split_version for row in used}) != 1:
        raise DataContractError("Accepted export requires one reviewed split version")
    train = [row for row in used if row.usage == "train"]
    if not train:
        raise DataContractError("Accepted export requires reviewed training records")
    for target in TARGETS:
        states = {getattr(row, target).state for row in train}
        if not {"positive", "negative"}.issubset(states):
            raise DataContractError(f"Training coverage lacks reviewed P/N for {target}")
    identities: dict[str, set[str]] = defaultdict(set)
    groups: dict[str, set[str]] = defaultdict(set)
    for row in used:
        if row.group is None or row.group.leakage_group_id is None:
            raise DataContractError("Accepted records require reviewed leakage groups")
        groups[row.source.image_sha256].add(row.group.leakage_group_id)
        identities[row.source.image_sha256].add(str(row.split))
        if row.crop is not None:
            identities[row.crop.crop_sha256].add(str(row.split))
    if any(len(values) > 1 for values in identities.values()):
        raise DataContractError("Image/crop checksum leakage across splits")
    if any(len(values) > 1 for values in groups.values()):
        raise DataContractError("Same source image was assigned different leakage groups")


def build_pilot_package(
    records: Sequence[PilotRecord],
    output_dir: str | Path,
    source_roots: Mapping[str, str | Path],
    crop_inputs: Mapping[str, str | Path],
    selection_rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    expected_sample_ids: Sequence[str],
) -> dict[str, Any]:
    """Build a new version without promoting pending records or modifying inputs.

    ``metadata`` contains the pinned Git/config/input evidence and release status.
    The caller supplies the exact ledger ID set; selection rows carry source-anchor
    provenance only. Local roots/crop input paths are operational arguments and do
    not enter the portable deterministic payload.
    """
    rows = sorted(records, key=lambda row: row.sample_id)
    validate_records(rows)
    expected = list(expected_sample_ids)
    if len(expected) != len(set(expected)) or {row.sample_id for row in rows} != set(expected):
        raise DataContractError("Decision ledger must match the exact expected sample ID set")
    if not rows:
        raise DataContractError("Cannot export an empty pilot decision ledger")
    for field in (
        "dataset_version",
        "selection_version",
        "crop_policy_version",
        "target_encoding_version",
        "schema_version",
    ):
        if len({getattr(row, field) for row in rows}) != 1:
            raise DataContractError(f"Mixed {field} in one dataset package")
    if metadata.get("dataset_version") != rows[0].dataset_version:
        raise DataContractError("Package metadata dataset version differs from records")
    if not isinstance(metadata.get("git_commit"), str) or not metadata["git_commit"].strip():
        raise DataContractError("Pinned Git commit is required for package provenance")
    expected_counts = metadata.get("expected_source_counts")
    if expected_counts is not None and dict(Counter(row.source.source_id for row in rows)) != (
        dict(expected_counts)
    ):
        raise DataContractError("Ledger source counts differ from the pinned scope")
    selection = sorted(selection_rows, key=lambda row: str(row["sample_id"]))
    selected_ids = [str(row["sample_id"]) for row in selection]
    if len(selected_ids) != len(set(selected_ids)) or not set(selected_ids).issubset(set(expected)):
        raise DataContractError("Selection contains duplicate or unknown ledger IDs")
    if metadata.get("expected_selection_count", len(selection)) != len(selection):
        raise DataContractError("Selection count differs from the pinned scope")
    by_id = {row.sample_id: row for row in rows}
    for selected in selection:
        source = by_id[str(selected["sample_id"])].source
        fields = {
            "source_id": source.source_id,
            "archive_sha256": source.archive_sha256,
            "source_image_relpath": source.image_relpath,
            "source_image_sha256": source.image_sha256,
            "source_label_relpath": source.label_relpath,
            "source_label_sha256": source.label_sha256,
            "source_label_line_1based": source.label_line_1based,
            "source_class_id": source.source_class_id,
        }
        if any(selected.get(field) != value for field, value in fields.items()):
            raise DataContractError("Selection provenance differs from the decision ledger")
    for row in rows:
        if row.crop and row.crop.crop_relpath != f"crops/{row.sample_id}.png":
            raise DataContractError("Package crop path must be crops/<sample_id>.png")
    _release_gates(rows, metadata)
    output = Path(output_dir).resolve()
    raw = Path(__file__).resolve().parents[3] / "data" / "raw"
    if output.is_relative_to(raw.resolve()) or any(
        output.is_relative_to(Path(root).resolve()) for root in source_roots.values()
    ):
        raise DataContractError("Package output must be outside immutable source directories")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise DataContractError(
            "Package output must be new or empty; existing versions are preserved"
        )
    sources = _preflight(rows, source_roots, crop_inputs)
    # Serialization errors are found before starting output writes as well.
    json.dumps(dict(metadata), allow_nan=False)
    for selection_row in selection:
        json.dumps(dict(selection_row), allow_nan=False)

    output.mkdir(parents=True, exist_ok=True)
    copied_crops = []
    for row in rows:
        if row.crop is None or row.crop.review is None or row.disposition == "excluded":
            continue
        target = output / row.crop.crop_relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        if row.sample_id in crop_inputs:
            shutil.copyfile(crop_inputs[row.sample_id], target)
        else:
            with Image.open(sources[row.sample_id]) as image:
                image.convert("RGB").crop(row.crop.context_box.xyxy).save(target, format="PNG")
        if sha256_file(target) != row.crop.crop_sha256:
            raise DataContractError(f"Exported crop checksum differs: {row.sample_id}")
        copied_crops.append(row.sample_id)
    write_records(output / "review-ledger.jsonl", rows)
    _jsonl(output / "selection.jsonl", selection)
    if metadata["status"] == "accepted":
        used = [row for row in rows if row.usage in SPLITS]
        write_records(output / "manifest.jsonl", used)
        _jsonl(
            output / "split-assignment.jsonl",
            [
                {
                    "sample_id": row.sample_id,
                    "split": row.split,
                    "leakage_group_id": row.group.leakage_group_id if row.group else None,
                    "split_version": row.split_version,
                    "test_freeze_ref": row.test_freeze_ref,
                }
                for row in used
            ],
        )
    coverage = coverage_report(rows)
    leakage = leakage_report(rows)
    if metadata["status"] == "accepted":
        leakage["near_duplicates_and_cross_source_relations"] = "owner_reviewed_for_used_records"
        leakage["owner_review_ref"] = metadata["leakage_review_ref"]
    qa = {
        "records": len(rows),
        "source_hash_dimension_checks": "pass",
        "reviewed_crop_pixel_hash_checks": "pass",
        "schema_validation": "pass",
        "exported_reviewed_crop_ids": copied_crops,
        "pending_crop_ids": [
            row.sample_id for row in rows if row.crop is None or row.crop.review is None
        ],
        "training_release_accepted": metadata["status"] == "accepted",
        "runtime_crop_gate": "pending_separate_owner_decision",
    }
    release = {
        **dict(metadata),
        "schema_version": rows[0].schema_version,
        "selection_version": rows[0].selection_version,
        "target_encoding_version": rows[0].target_encoding_version,
        "crop_policy_version": rows[0].crop_policy_version,
        "ledger_records": len(rows),
        "reviewed_crops": len(copied_crops),
        "split_versions": sorted({row.split_version for row in rows if row.split_version}),
        "expected_sample_ids": sorted(expected),
        "media_uploaded": False,
        "runtime_crop_ready": False,
    }
    _json(output / "release.json", release)
    _json(
        output / "target-encoding.json",
        {
            "version": rows[0].target_encoding_version,
            "target_order": list(TARGETS),
            "states": {
                "positive": {"value": 1, "mask": 1},
                "negative": {"value": 0, "mask": 1},
                "unknown": {"value": None, "mask": 0},
            },
            "normal": "metadata: both targets negative and confirmed_working",
        },
    )
    _json(
        output / "crop-policy.json",
        {
            "version": rows[0].crop_policy_version,
            "coordinates": "source pixels; integer XYXY; top-left; half-open",
            "policy": "Separate visible-person and reviewed context; no automatic padding.",
            "runtime_policy": None,
            **({"batch_review_notes": metadata["crop_policy_review_notes"]}
               if "crop_policy_review_notes" in metadata else {}),
        },
    )
    _json(output / "reports" / "qa.json", qa)
    _json(output / "reports" / "coverage.json", coverage)
    _json(output / "reports" / "leakage.json", leakage)
    limitations = metadata.get("limitations", [])
    release_details = ""
    if metadata["status"] == "accepted":
        used_count = sum(row.usage in SPLITS for row in rows)
        release_details = (
            f"Usage manifest: `manifest.jsonl` ({used_count} crops). "
            "Read this manifest for training/evaluation; the full ledger/crop folder also "
            "retains review-only evidence. Assignment: `split-assignment.jsonl`. "
            "Test freeze hashes and access protocol: `release.json#test_freeze`.\n\n"
            f"Approved use scope: `{metadata['use_scope']}`. "
            "Source attribution: " + ", ".join(metadata.get("source_attribution_refs", []))
            + ". Keep attribution and derivative notes.\n\n"
        )
    card = (
        f"# Pilot B — {rows[0].dataset_version}\n\n"
        f"Status: `{metadata['status']}`. Ledger: {len(rows)} records. "
        f"Reviewed crop files: {len(copied_crops)}.\n\n"
        + release_details
        +
        "Person-context crops with targets `[phone_use, looking_around]`. "
        "Unknown remains null/mask=0; only reviewed known targets can supply supervision.\n\n"
        "Sources: " + ", ".join(sorted({row.source.source_id for row in rows})) + ".\n\n"
        "Coverage and support: `reports/coverage.json`. Provenance/review decisions: "
        "`review-ledger.jsonl`. Exact duplicates and unresolved groups: "
        "`reports/leakage.json`. Independent leakage groups are not inferred from names "
        "or distinct hashes.\n\n"
        "Pending packages contain no training manifest or split assignment. "
        "Local review media is evidence for preparation. Runtime automatic context crops "
        "require a separate owner decision before an end-to-end baseline. "
        "No training, model metrics, DVC upload, or external media sharing is performed.\n\n"
        "Limitations:\n\n- Pilot counts do not demonstrate real-exam generalization.\n"
        "- Check coverage by source and family before claiming domain diversity.\n"
        "- Static images do not establish behavior duration, intent, or violations.\n"
        + "".join(f"- {str(item)}\n" for item in limitations)
    )
    (output / "dataset-card.md").write_text(card, encoding="utf-8", newline="\n")
    checksums = {
        file.relative_to(output).as_posix(): sha256_file(file)
        for file in sorted(output.rglob("*"))
        if file.is_file()
    }
    (output / "checksums.sha256").write_text(
        "".join(f"{digest}  {relative}\n" for relative, digest in sorted(checksums.items())),
        encoding="utf-8",
        newline="\n",
    )
    return {
        "status": metadata["status"],
        "records": len(rows),
        "reviewed_crops": len(copied_crops),
        "payload_checksums": checksums,
        "checksums_sha256": sha256_file(output / "checksums.sha256"),
    }
