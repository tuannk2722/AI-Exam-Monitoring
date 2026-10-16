"""Verified manifest selection and deterministic full-context transforms."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import asdict
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

import torch
from PIL import Image
from torchvision.transforms import functional as TF

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.integrity import verify_payload
from ai_exam_monitoring.data.pilot_schema import PilotRecord, read_records, record_to_dict


class DatasetVariables(Protocol):
    @property
    def dataset(self) -> str: ...
    @property
    def dataset_version(self) -> str: ...
    @property
    def split_version(self) -> str: ...
    @property
    def encoding_version(self) -> str: ...
    @property
    def payload_sha256(self) -> str: ...


class ImageVariables(Protocol):
    @property
    def image_size(self) -> int: ...
    @property
    def mean(self) -> list[float]: ...
    @property
    def std(self) -> list[float]: ...
    @property
    def fill(self) -> list[int]: ...


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DataContractError("Metadata phải là JSON object")
    return value


def _workspace_path(workspace: Path, relative: str) -> Path:
    if (not isinstance(relative, str) or not relative or "\\" in relative
            or ":" in relative or PurePosixPath(relative).is_absolute()
            or ".." in PurePosixPath(relative).parts):
        raise DataContractError("Evidence path phải tương đối và nằm trong workspace")
    path = (workspace / relative).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise DataContractError("Evidence path thoát workspace")
    return path


def _pinned_file(workspace: Path, pin: dict[str, Any]) -> Path:
    if (not isinstance(pin, dict) or set(pin) != {"path", "sha256"}
            or not isinstance(pin["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", pin["sha256"]) is None):
        raise DataContractError("Evidence pointer phải pin path/SHA-256")
    path = _workspace_path(workspace, pin["path"])
    if sha256_file(path) != pin["sha256"]:
        raise DataContractError("Evidence checksum thay đổi")
    return path


def _verify_inline_freeze(root: Path, release: dict[str, Any], records: list[PilotRecord]) -> None:
    # Giữ nguyên kiểm tra freeze v4; dùng lại để xác minh parent của pointer v5.
    freeze = release["test_freeze"]
    if release["status"] != "accepted" or freeze["status"] != "frozen":
        raise DataContractError("Dataset release/test freeze not accepted")
    for filename, key in (("manifest.jsonl", "manifest_sha256"),
                          ("split-assignment.jsonl", "split_assignment_sha256")):
        if sha256_file(root / filename) != freeze[key]:
            raise DataContractError("Frozen manifest/split hash changed")
    test = sorted((r for r in records if r.usage == "test"), key=lambda r: r.sample_id)
    encoded = "".join(json.dumps(record_to_dict(r), sort_keys=True, ensure_ascii=False,
                                 allow_nan=False) + "\n" for r in test).encode()
    if (hashlib.sha256(encoded).hexdigest() != freeze["test_manifest_sha256"]
            or [r.sample_id for r in test] != freeze["test_sample_ids"]):
        raise DataContractError("Frozen test identity changed")


def _verify_membership(root: Path, records: list[PilotRecord]) -> list[PilotRecord]:
    if any(r.group is None or r.group.leakage_group_id is None for r in records):
        raise DataContractError("Supervised records require reviewed leakage groups")
    ledger = read_records(root / "review-ledger.jsonl")
    expected = {r.sample_id: record_to_dict(r) for r in ledger
                if r.usage in {"train", "val", "test"}}
    if {r.sample_id: record_to_dict(r) for r in records} != expected:
        raise DataContractError("Manifest không khớp membership/nhãn của ledger")
    assignments = [json.loads(line) for line in
                   (root / "split-assignment.jsonl").read_text(encoding="utf-8").splitlines()]
    expected_split = {r.sample_id: {
        "sample_id": r.sample_id, "split": r.split, "split_version": r.split_version,
        "leakage_group_id": r.group.leakage_group_id if r.group else None,
        "test_freeze_ref": r.test_freeze_ref,
    } for r in records}
    if (len(assignments) != len(expected_split)
            or {r["sample_id"]: r for r in assignments} != expected_split):
        raise DataContractError("Split assignment không khớp manifest")
    return ledger


def _evaluation_identity(row: PilotRecord) -> dict[str, Any]:
    if row.crop is None or row.group is None:
        raise DataContractError("Evaluation identity requires crop and group")
    # Bỏ version packaging; giữ freeze ref/evidence/crop/target/group phục vụ đánh giá.
    return {"source": asdict(row.source), "crop": asdict(row.crop),
            "phone_use": asdict(row.phone_use), "looking_around": asdict(row.looking_around),
            "context": asdict(row.work_context_review), "rights": asdict(row.rights),
            "group": asdict(row.group), "values": row.target_values, "mask": row.target_mask,
            "usage": row.usage, "split": row.split, "encoding": row.target_encoding_version,
            "test_freeze_ref": row.test_freeze_ref}


def _verify_preservation(root: Path, config: DatasetVariables, release: dict[str, Any],
                         records: list[PilotRecord], ledger: list[PilotRecord]) -> None:
    relative = PurePosixPath(config.dataset)
    workspace = root.resolve()
    for _ in relative.parts:
        workspace = workspace.parent
    if _workspace_path(workspace, config.dataset) != root.resolve():
        raise DataContractError("Package/pointer không thuộc workspace của config")
    evidence_path = _pinned_file(workspace, release["test_freeze"])
    if release["test_freeze_ref"] != release["test_freeze"]["path"]:
        raise DataContractError("Release preservation reference không khớp pointer")
    evidence = _read_object(evidence_path)
    if (release["status"] != "accepted"
            or evidence["status"] != "owner_approved_preservation"
            or evidence["test_already_evaluated_in_e001"] is not True
            or evidence["new_test_inference_authorized"] is not False):
        raise DataContractError("Preservation chưa được nghiệm thu đúng phạm vi")
    if evidence["owner_approval"] != release["owner_approval"]:
        raise DataContractError("Preservation và release không cùng owner approval")
    approval = _read_object(_pinned_file(workspace, evidence["owner_approval"]))
    if (approval["decision"] != "approve_pilot_b_v5_release"
            or not approval["reviewer"] or not approval["reviewed_at"]
            or approval["approved_counts"] != dict(Counter(r.usage for r in ledger))):
        raise DataContractError("Owner approval không khớp release/membership")
    for key in ("membership", "groups", "proposal_config"):
        _pinned_file(workspace, approval[key])

    parent_ref = evidence["parent"]
    parent = _workspace_path(workspace, parent_ref["package"])
    if (_pinned_file(workspace, parent_ref["checksums"]) != parent / "checksums.sha256"
            or _pinned_file(workspace, parent_ref["ledger"]) != parent / "review-ledger.jsonl"
            or parent == root.resolve()):
        raise DataContractError("Preservation parent không khớp package/pins")
    verify_payload(parent)
    parent_records = read_records(parent / "manifest.jsonl")
    parent_release = _read_object(parent / "release.json")
    _verify_inline_freeze(parent, parent_release, parent_records)
    _verify_membership(parent, parent_records)
    parent_freeze = parent_release["test_freeze"]
    _pinned_file(workspace, {"path": parent_freeze["owner_decision_ref"],
                             "sha256": parent_freeze["owner_decision_sha256"]})
    before = {r.sample_id: r for r in parent_records if r.usage in {"val", "test"}}
    after = {r.sample_id: r for r in records if r.usage in {"val", "test"}}
    preserved = evidence["records"]
    if (set(before) != set(after) or len(preserved) != len(before)
            or {r["sample_id"] for r in preserved} != set(before)):
        raise DataContractError("Preservation thiếu/thay/nhân đôi ID validation hoặc test")
    for item in preserved:
        old, row = before[item["sample_id"]], after[item["sample_id"]]
        if row.crop is None or row.group is None:
            raise DataContractError("Preserved record requires crop and group")
        if (_evaluation_identity(old) != _evaluation_identity(row)
                or item["split"] != row.split
                or item["source_image_sha256"] != row.source.image_sha256
                or item["crop_sha256"] != row.crop.crop_sha256
                or item["phone_use"] != row.phone_use.state
                or item["looking_around"] != row.looking_around.state
                or item["target_mask"] != list(row.target_mask)
                or item["leakage_group_id"] != row.group.leakage_group_id
                or item["original_test_freeze_ref"] != old.test_freeze_ref):
            raise DataContractError("Nội dung validation/test khác parent đã freeze")


def verify_dataset(root: Path, config: DatasetVariables) -> list[PilotRecord]:
    try:
        if sha256_file(root / "checksums.sha256") != config.payload_sha256:
            raise DataContractError("Dataset payload pin changed")
        verify_payload(root)
        records = read_records(root / "manifest.jsonl")
        release = _read_object(root / "release.json")
        if release["status"] != "accepted":
            raise DataContractError("Dataset release not accepted")
        for row in records:
            if (row.dataset_version != config.dataset_version
                    or row.split_version != config.split_version
                    or row.target_encoding_version != config.encoding_version
                    or row.use_scope != "local_classifier_research"
                    or row.usage not in {"train", "val", "test"}):
                raise DataContractError("Manifest version/scope/usage differs from config")
        ledger = _verify_membership(root, records)
        freeze = release["test_freeze"]
        if isinstance(freeze, dict) and set(freeze) == {"path", "sha256"}:
            _verify_preservation(root, config, release, records, ledger)
        else:
            _verify_inline_freeze(root, release, records)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        raise DataContractError(
            f"Dataset/freeze metadata thiếu hoặc không hợp lệ: {error}") from error
    return records


def select_records(records: list[PilotRecord], split: str, *, final_test: bool = False
                   ) -> list[PilotRecord]:
    if split not in {"train", "val"} and not (split == "test" and final_test):
        raise DataContractError("Test is reserved for explicit final evaluation")
    selected = sorted((r for r in records if r.usage == split), key=lambda r: r.sample_id)
    if not selected:
        raise DataContractError(f"Empty {split} split")
    return selected


def letterbox(image: Image.Image, config: ImageVariables) -> Image.Image:
    image = image.convert("RGB")
    scale = config.image_size / max(image.size)
    width, height = (max(1, min(config.image_size, round(v * scale))) for v in image.size)
    size = (width, height)
    resized = image.resize(size, Image.Resampling.BILINEAR)
    result = Image.new("RGB", (config.image_size, config.image_size), tuple(config.fill))
    result.paste(resized, ((config.image_size - size[0]) // 2,
                          (config.image_size - size[1]) // 2))
    return result


def image_tensor(path: Path, config: ImageVariables) -> torch.Tensor:
    with Image.open(path) as image:
        prepared = letterbox(image, config)
    return TF.normalize(TF.to_tensor(prepared), config.mean, config.std)


def labels(records: list[PilotRecord]) -> tuple[torch.Tensor, torch.Tensor]:
    # Finite placeholder only in memory; mask retains unknown semantics.
    values = torch.tensor([[0 if v is None else v for v in r.target_values] for r in records],
                          dtype=torch.float32)
    mask = torch.tensor([r.target_mask for r in records], dtype=torch.bool)
    return values, mask


def crop_path(root: Path, row: PilotRecord) -> Path:
    if row.crop is None:
        raise DataContractError("Missing reviewed crop")
    path = (root / row.crop.crop_relpath).resolve()
    if not path.is_relative_to(root.resolve()) or sha256_file(path) != row.crop.crop_sha256:
        raise DataContractError("Crop escaped root or changed bytes")
    if row.crop.derivation is not None:
        derived = row.crop.derivation
        with Image.open(path) as image:
            if (image.size != (derived.output_width, derived.output_height)
                    or image.format != derived.output_format):
                raise DataContractError("Derived crop dimensions/format changed")
    return path
