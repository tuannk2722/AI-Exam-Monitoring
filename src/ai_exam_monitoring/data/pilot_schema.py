"""Versioned reviewed-crop ledger and masked-label contract for pilot B.

Validation checks recorded approvals; it never infers labels, rights or groups.
An unreviewed SCB candidate may have no crop and remains review-only.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields, is_dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Any, Literal, TypeVar

from ai_exam_monitoring.common.errors import DataContractError

SCHEMA_VERSION = "pilot-b-manifest-v1"
DERIVED_SCHEMA_VERSION = "pilot-b-manifest-v2"
TARGET_ENCODING_VERSION = "pilot-b-targets-v1"
TARGET_ORDER = ("phone_use", "looking_around")
MULTILABEL_SCHEMA_VERSION = "pilot-b-manifest-v3"
MULTILABEL_ENCODING_VERSION = "pilot-b-targets-v2"
MULTILABEL_TARGET_ORDER = (*TARGET_ORDER, "sleeping", "hand_raising", "standing_up")
MULTILABEL_SEMANTICS_VERSION = "LABEL-CONTRACT-20261109"

TargetState = Literal["positive", "negative", "unknown"]
ContextState = Literal["confirmed_working", "confirmed_other", "unknown"]
NormalState = Literal["confirmed_normal", "not_normal", "unknown"]
Usage = Literal["review_only", "excluded", "train", "val", "test"]
Split = Literal["train", "val", "test"]


def _text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise DataContractError(f"{name} must be a non-empty string")


def _optional_text(value: Any, name: str) -> None:
    if value is not None:
        _text(value, name)


def _sha(value: Any, name: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise DataContractError(f"{name} must be a lowercase SHA-256 hex digest")


def _relative_path(value: Any, name: str) -> None:
    _text(value, name)
    path = PurePosixPath(value)
    if path.is_absolute() or "\\" in value or ":" in value or ".." in path.parts:
        raise DataContractError(f"{name} must be a safe relative POSIX path")
    if path.as_posix() != value or value == ".":
        raise DataContractError(f"{name} must be a canonical relative POSIX path")


def _integer(value: Any, name: str, minimum: int = 0) -> None:
    if type(value) is not int or value < minimum:
        raise DataContractError(f"{name} must be an integer >= {minimum}")


def _texts(values: Any, name: str) -> None:
    if not isinstance(values, tuple):
        raise DataContractError(f"{name} must be a tuple")
    for value in values:
        _text(value, name)


@dataclass(frozen=True, slots=True)
class ReviewEvidence:
    reviewer: str
    reviewed_at: str
    evidence_ref: str
    crop_sha256: str | None = None

    def __post_init__(self) -> None:
        for name in ("reviewer", "reviewed_at", "evidence_ref"):
            _text(getattr(self, name), name)
        if self.crop_sha256 is not None:
            _sha(self.crop_sha256, "review.crop_sha256")


@dataclass(frozen=True, slots=True)
class TargetReview:
    state: TargetState
    reason: str
    review: ReviewEvidence | None = None

    def __post_init__(self) -> None:
        if self.state not in {"positive", "negative", "unknown"}:
            raise DataContractError(f"Invalid target state: {self.state!r}")
        _text(self.reason, "target.reason")
        if self.review is not None and not isinstance(self.review, ReviewEvidence):
            raise DataContractError("target.review must be ReviewEvidence")
        if self.state != "unknown" and (self.review is None or self.review.crop_sha256 is None):
            raise DataContractError("Known target requires review on a specific crop SHA")

    @property
    def value(self) -> int | None:
        return {"positive": 1, "negative": 0, "unknown": None}[self.state]

    @property
    def mask(self) -> int:
        return int(self.state != "unknown")


@dataclass(frozen=True, slots=True)
class ContextReview:
    state: ContextState
    reason: str
    review: ReviewEvidence | None = None

    def __post_init__(self) -> None:
        if self.state not in {"confirmed_working", "confirmed_other", "unknown"}:
            raise DataContractError(f"Invalid work context state: {self.state!r}")
        _text(self.reason, "work_context.reason")
        if self.review is not None and not isinstance(self.review, ReviewEvidence):
            raise DataContractError("work_context.review must be ReviewEvidence")
        if self.state != "unknown" and (self.review is None or self.review.crop_sha256 is None):
            raise DataContractError("Confirmed work context requires review on a crop SHA")


@dataclass(frozen=True, slots=True)
class PixelBox:
    """Integer source-image XYXY, with exclusive right and bottom edges."""

    xmin: int
    ymin: int
    xmax: int
    ymax: int

    def __post_init__(self) -> None:
        for name in ("xmin", "ymin", "xmax", "ymax"):
            _integer(getattr(self, name), name)
        if self.xmin >= self.xmax or self.ymin >= self.ymax:
            raise DataContractError("PixelBox must have positive width and height")

    @property
    def xyxy(self) -> tuple[int, int, int, int]:
        return (self.xmin, self.ymin, self.xmax, self.ymax)

    def contains(self, other: PixelBox) -> bool:
        return (
            self.xmin <= other.xmin < other.xmax <= self.xmax
            and self.ymin <= other.ymin < other.ymax <= self.ymax
        )


@dataclass(frozen=True, slots=True)
class SourceRef:
    source_id: str
    archive_sha256: str
    image_relpath: str
    image_sha256: str
    image_width: int
    image_height: int
    label_relpath: str | None = None
    label_sha256: str | None = None
    label_line_1based: int | None = None
    source_class_id: int | None = None
    original_split: str | None = None
    aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text(self.source_id, "source_id")
        _sha(self.archive_sha256, "archive_sha256")
        _sha(self.image_sha256, "image_sha256")
        _relative_path(self.image_relpath, "image_relpath")
        _integer(self.image_width, "image_width", 1)
        _integer(self.image_height, "image_height", 1)
        if (self.label_relpath is None) != (self.label_sha256 is None):
            raise DataContractError("Source label path and SHA must be recorded together")
        if self.label_relpath is not None:
            _relative_path(self.label_relpath, "label_relpath")
            _sha(self.label_sha256, "label_sha256")
        if self.label_line_1based is not None:
            _integer(self.label_line_1based, "label_line_1based", 1)
            if self.label_relpath is None:
                raise DataContractError("Source annotation line requires label provenance")
        if self.source_class_id is not None:
            _integer(self.source_class_id, "source_class_id")
            if self.label_line_1based is None:
                raise DataContractError("Source class requires source annotation line")
        _optional_text(self.original_split, "original_split")
        _texts(self.aliases, "source.aliases")


@dataclass(frozen=True, slots=True)
class CropDerivation:
    """Reviewed imported derivative; does not claim a reproducible resize recipe."""

    source_sha256: str
    native_roi_rgb_sha256: str
    output_width: int
    output_height: int
    output_format: str
    evidence_ref: str
    review: ReviewEvidence
    kind: str = "reviewed_import"

    def __post_init__(self) -> None:
        if self.kind != "reviewed_import":
            raise DataContractError("Unsupported crop derivation kind")
        _sha(self.source_sha256, "derivation.source_sha256")
        _sha(self.native_roi_rgb_sha256, "derivation.native_roi_rgb_sha256")
        _integer(self.output_width, "derivation.output_width", 1)
        _integer(self.output_height, "derivation.output_height", 1)
        if self.output_format not in {"JPEG", "PNG"}:
            raise DataContractError("Derived crop format must be JPEG or PNG")
        _text(self.evidence_ref, "derivation.evidence_ref")
        if not isinstance(self.review, ReviewEvidence) or self.review.crop_sha256 is None:
            raise DataContractError("Derived crop requires review bound to output SHA")


@dataclass(frozen=True, slots=True)
class CropRef:
    """A context crop with optional joint person/crop owner approval."""

    person_id: str
    person_box: PixelBox
    context_box: PixelBox
    crop_relpath: str
    crop_sha256: str
    review: ReviewEvidence | None = None
    derivation: CropDerivation | None = None

    def __post_init__(self) -> None:
        _text(self.person_id, "person_id")
        if not isinstance(self.person_box, PixelBox) or not isinstance(self.context_box, PixelBox):
            raise DataContractError("person_box and context_box must be PixelBox")
        if not self.context_box.contains(self.person_box):
            raise DataContractError("Context crop must contain the visible-person box")
        _relative_path(self.crop_relpath, "crop_relpath")
        _sha(self.crop_sha256, "crop_sha256")
        if self.derivation is not None and (
            not isinstance(self.derivation, CropDerivation)
            or self.derivation.review.crop_sha256 != self.crop_sha256
        ):
            raise DataContractError("Derivation review must bind to crop SHA")
        if self.review is not None and (
            not isinstance(self.review, ReviewEvidence)
            or self.review.crop_sha256 != self.crop_sha256
        ):
            raise DataContractError("Person/crop approval must bind to this crop SHA")


@dataclass(frozen=True, slots=True)
class RightsReview:
    license_id: str | None
    attribution_ref: str | None
    approved_use_scope: tuple[str, ...] = ()
    review: ReviewEvidence | None = None

    def __post_init__(self) -> None:
        _optional_text(self.license_id, "license_id")
        _optional_text(self.attribution_ref, "attribution_ref")
        _texts(self.approved_use_scope, "approved_use_scope")
        if self.review is not None and not isinstance(self.review, ReviewEvidence):
            raise DataContractError("rights.review must be ReviewEvidence")
        if self.approved_use_scope and self.review is None:
            raise DataContractError("Approved use scope requires owner review evidence")


@dataclass(frozen=True, slots=True)
class GroupReview:
    leakage_group_id: str | None = None
    evidence_refs: tuple[str, ...] = ()
    review: ReviewEvidence | None = None
    video_id: str | None = None
    session_id: str | None = None
    room_id: str | None = None
    subject_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("leakage_group_id", "video_id", "session_id", "room_id", "subject_id"):
            _optional_text(getattr(self, name), name)
        _texts(self.evidence_refs, "group.evidence_refs")
        if self.review is not None and not isinstance(self.review, ReviewEvidence):
            raise DataContractError("group.review must be ReviewEvidence")
        if self.leakage_group_id is not None and (not self.evidence_refs or self.review is None):
            raise DataContractError("Leakage group assignment requires evidence and owner review")


@dataclass(frozen=True, slots=True)
class PilotRecord:
    sample_id: str
    dataset_version: str
    selection_version: str
    crop_policy_version: str
    source: SourceRef
    phone_use: TargetReview
    looking_around: TargetReview
    work_context_review: ContextReview
    rights: RightsReview
    crop: CropRef | None = None
    group: GroupReview | None = None
    disposition: Literal["pending", "approved", "excluded"] = "pending"
    usage: Usage = "review_only"
    split: Split | None = None
    split_version: str | None = None
    ineligibility_reasons: tuple[str, ...] = ()
    exclusion_reason: str | None = None
    owner_decision_ref: str | None = None
    release_review: ReviewEvidence | None = None
    test_freeze_ref: str | None = None
    use_scope: str | None = None
    schema_version: str = SCHEMA_VERSION
    target_encoding_version: str = TARGET_ENCODING_VERSION
    targets: Mapping[str, TargetReview] | None = None
    semantics_version: str | None = None

    def __post_init__(self) -> None:
        multilabel = self.schema_version == MULTILABEL_SCHEMA_VERSION
        if self.schema_version not in {
            SCHEMA_VERSION, DERIVED_SCHEMA_VERSION, MULTILABEL_SCHEMA_VERSION,
        }:
            raise DataContractError(f"Unsupported schema_version: {self.schema_version!r}")
        expected_encoding = MULTILABEL_ENCODING_VERSION if multilabel else TARGET_ENCODING_VERSION
        if self.target_encoding_version != expected_encoding:
            raise DataContractError("Unsupported target encoding version")
        if multilabel:
            if (not isinstance(self.targets, Mapping)
                    or set(self.targets) != set(MULTILABEL_TARGET_ORDER)
                    or any(not isinstance(v, TargetReview) for v in self.targets.values())
                    or self.semantics_version != MULTILABEL_SEMANTICS_VERSION):
                raise DataContractError("V3 requires five named targets and approved semantics")
            if (self.phone_use != self.targets["phone_use"]
                    or self.looking_around != self.targets["looking_around"]):
                raise DataContractError("Legacy target accessors must match V3 targets")
            object.__setattr__(self, "targets", MappingProxyType(dict(self.targets)))
            if (self.targets["sleeping"].state == "positive"
                    and self.targets["looking_around"].state != "negative"):
                raise DataContractError("Ground truth sleeping P requires looking_around N")
        elif self.targets is not None or self.semantics_version is not None:
            raise DataContractError("V1/V2 cannot contain V3 target fields")
        for name in ("sample_id", "dataset_version", "selection_version", "crop_policy_version"):
            _text(getattr(self, name), name)
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", self.sample_id) is None:
            raise DataContractError("sample_id must be a technical filename-safe ID")
        typed_fields = (
            (self.source, SourceRef, "source"),
            (self.phone_use, TargetReview, "phone_use"),
            (self.looking_around, TargetReview, "looking_around"),
            (self.work_context_review, ContextReview, "work_context_review"),
            (self.rights, RightsReview, "rights"),
        )
        for value, expected, name in typed_fields:
            if not isinstance(value, expected):
                raise DataContractError(f"{name} must be {expected.__name__}")
        for optional_value, optional_expected, optional_name in (
            (self.crop, CropRef, "crop"),
            (self.group, GroupReview, "group"),
            (self.release_review, ReviewEvidence, "release_review"),
        ):
            if optional_value is not None and not isinstance(optional_value, optional_expected):
                raise DataContractError(
                    f"{optional_name} must be {optional_expected.__name__} or null"
                )
        for name in (
            "split_version",
            "exclusion_reason",
            "owner_decision_ref",
            "test_freeze_ref",
            "use_scope",
        ):
            _optional_text(getattr(self, name), name)
        _texts(self.ineligibility_reasons, "ineligibility_reasons")
        if self.disposition not in {"pending", "approved", "excluded"}:
            raise DataContractError("Invalid disposition")
        if self.usage not in {"review_only", "excluded", "train", "val", "test"}:
            raise DataContractError("Invalid usage")
        if self.split is not None and self.split not in {"train", "val", "test"}:
            raise DataContractError("Invalid split")
        if self.crop is not None:
            if self.crop.derivation is not None and (
                self.schema_version not in {DERIVED_SCHEMA_VERSION, MULTILABEL_SCHEMA_VERSION}
                or self.crop.derivation.source_sha256 != self.source.image_sha256
            ):
                raise DataContractError("Derived crop requires V2/V3 and matching source SHA")
            bounds = PixelBox(0, 0, self.source.image_width, self.source.image_height)
            if not bounds.contains(self.crop.context_box):
                raise DataContractError("Crop must be within source-image dimensions")
        reviews: tuple[TargetReview | ContextReview, ...] = (
            *self.target_reviews, self.work_context_review)
        for reviewed in reviews:
            if reviewed.state != "unknown" and (
                self.crop is None
                or reviewed.review is None
                or reviewed.review.crop_sha256 != self.crop.crop_sha256
            ):
                raise DataContractError("Known review evidence must match the record crop SHA")
        if self.disposition == "excluded":
            if self.usage != "excluded" or not self.exclusion_reason or not self.owner_decision_ref:
                raise DataContractError(
                    "Excluded record requires reason, decision and excluded usage"
                )
        elif self.usage == "excluded" or self.exclusion_reason is not None:
            raise DataContractError("Exclusion fields require excluded disposition")
        if self.disposition == "approved" and (
            self.crop is None or self.crop.review is None or self.owner_decision_ref is None
        ):
            raise DataContractError("Approved disposition requires person/crop review and decision")
        if self.usage in {"review_only", "excluded"}:
            if self.split is not None or self.split_version is not None:
                raise DataContractError("Review-only/excluded records must have null split/version")
            if self.usage == "review_only" and not self.ineligibility_reasons:
                raise DataContractError("Review-only record requires ineligibility reasons")
            return
        self._validate_usage_gates()

    def _validate_usage_gates(self) -> None:
        if self.disposition != "approved" or self.crop is None or self.crop.review is None:
            raise DataContractError("Training/evaluation usage requires approved person/crop")
        if not any(self.target_mask):
            raise DataContractError("All-unknown crop cannot supply loss or metric supervision")
        if (
            self.rights.review is None
            or not self.rights.approved_use_scope
            or self.rights.license_id is None
            or self.rights.attribution_ref is None
            or self.use_scope not in self.rights.approved_use_scope
        ):
            raise DataContractError("Training/evaluation usage requires approval for its use scope")
        if self.group is None or self.group.leakage_group_id is None:
            raise DataContractError("Training/evaluation usage requires reviewed leakage group")
        if self.release_review is None or self.owner_decision_ref is None:
            raise DataContractError("Training/evaluation usage requires owner release review")
        if self.split != self.usage or self.split_version is None:
            raise DataContractError("Usage must match an assigned versioned split")
        if self.ineligibility_reasons:
            raise DataContractError("Usable record cannot retain unresolved eligibility blockers")
        if self.usage == "test" and self.test_freeze_ref is None:
            raise DataContractError("Test usage requires owner test-freeze evidence")

    @property
    def target_order(self) -> tuple[str, ...]:
        return MULTILABEL_TARGET_ORDER if self.schema_version == MULTILABEL_SCHEMA_VERSION else (
            TARGET_ORDER)

    @property
    def target_reviews(self) -> tuple[TargetReview, ...]:
        if self.schema_version == MULTILABEL_SCHEMA_VERSION:
            assert self.targets is not None
            return tuple(self.targets[name] for name in self.target_order)
        return self.phone_use, self.looking_around

    def target_review(self, name: str) -> TargetReview:
        return self.target_reviews[self.target_order.index(name)]

    @property
    def target_values(self) -> tuple[int | None, ...]:
        return tuple(target.value for target in self.target_reviews)

    @property
    def target_mask(self) -> tuple[int, ...]:
        return tuple(target.mask for target in self.target_reviews)

    @property
    def normal_review(self) -> NormalState:
        states = tuple(target.state for target in self.target_reviews)
        if "positive" in states or self.work_context_review.state == "confirmed_other":
            return "not_normal"
        if all(state == "negative" for state in states) and (
            self.work_context_review.state == "confirmed_working"
        ):
            return "confirmed_normal"
        return "unknown"


def record_to_dict(record: PilotRecord) -> dict[str, Any]:
    # V1/V2 bytes stay unchanged; V3 serializes only named targets, not duplicate accessors.
    payload: dict[str, Any] = {}
    for field in fields(record):
        if field.name == "targets":
            continue
        value = getattr(record, field.name)
        payload[field.name] = (asdict(value) if is_dataclass(value)
                               and not isinstance(value, type) else value)
    if record.schema_version == MULTILABEL_SCHEMA_VERSION:
        payload.pop("phone_use")
        payload.pop("looking_around")
        payload["targets"] = dict(zip(record.target_order,
                                      (asdict(t) for t in record.target_reviews), strict=True))
    else:
        payload.pop("semantics_version")
    if record.schema_version == SCHEMA_VERSION and payload["crop"] is not None:
        # Frozen V1 serialization, including historical test hashes, is unchanged.
        payload["crop"].pop("derivation")
    payload["target_order"] = list(record.target_order)
    payload["target_values"] = list(record.target_values)
    payload["target_mask"] = list(record.target_mask)
    payload["normal_review"] = record.normal_review
    return payload


_Model = TypeVar("_Model")


def _object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        raise DataContractError(f"{name} must be a JSON object")
    return dict(value)


def _construct(model: type[_Model], payload: dict[str, Any]) -> _Model:
    allowed = {field.name for field in fields(model)}  # type: ignore[arg-type]
    unknown = set(payload) - allowed
    if unknown:
        raise DataContractError(f"Unknown {model.__name__} fields: {sorted(unknown)}")
    try:
        return model(**payload)
    except TypeError as error:
        raise DataContractError(f"Invalid {model.__name__} fields: {error}") from error


def _review(value: Any) -> ReviewEvidence | None:
    if value is None:
        return None
    return _construct(ReviewEvidence, _object(value, "review"))


def _tuple(payload: dict[str, Any], name: str) -> None:
    if name in payload:
        value = payload[name]
        if not isinstance(value, (list, tuple)):
            raise DataContractError(f"{name} must be an array")
        payload[name] = tuple(value)


def record_from_dict(value: Mapping[str, Any]) -> PilotRecord:
    payload = _object(value, "record")
    derived_names = ("target_order", "target_values", "target_mask", "normal_review")
    if any(name not in payload for name in derived_names):
        raise DataContractError("Record must include derived target encoding and normal state")
    derived = {name: payload.pop(name) for name in derived_names}
    for name in ("schema_version", "target_encoding_version"):
        if name not in payload:
            raise DataContractError(f"Record requires explicit {name}")
    source = _object(payload.get("source"), "source")
    _tuple(source, "aliases")
    payload["source"] = _construct(SourceRef, source)
    multilabel = payload["schema_version"] == MULTILABEL_SCHEMA_VERSION
    if multilabel:
        if any(name in payload for name in TARGET_ORDER):
            raise DataContractError("V3 stores labels in targets, not separate legacy fields")
        targets = _object(payload.get("targets"), "targets")
        if set(targets) != set(MULTILABEL_TARGET_ORDER):
            raise DataContractError("V3 requires exactly the five canonical target IDs")
    else:
        if "targets" in payload or "semantics_version" in payload:
            raise DataContractError("V1/V2 cannot contain V3 fields")
        targets = {name: payload.get(name) for name in TARGET_ORDER}
    for name in (MULTILABEL_TARGET_ORDER if multilabel else TARGET_ORDER):
        target = _object(targets[name], name)
        target["review"] = _review(target.get("review"))
        targets[name] = _construct(TargetReview, target)
    payload.update({name: targets[name] for name in TARGET_ORDER})
    if multilabel:
        payload["targets"] = targets
    context = _object(payload.get("work_context_review"), "work_context_review")
    context["review"] = _review(context.get("review"))
    payload["work_context_review"] = _construct(ContextReview, context)
    rights = _object(payload.get("rights"), "rights")
    _tuple(rights, "approved_use_scope")
    rights["review"] = _review(rights.get("review"))
    payload["rights"] = _construct(RightsReview, rights)
    if payload.get("crop") is not None:
        crop = _object(payload["crop"], "crop")
        if "derivation" in crop and payload["schema_version"] == SCHEMA_VERSION:
            raise DataContractError("V1 crop cannot contain derivation fields")
        if crop.get("derivation") is not None:
            derivation = _object(crop["derivation"], "derivation")
            derivation["review"] = _review(derivation.get("review"))
            crop["derivation"] = _construct(CropDerivation, derivation)
        for name in ("person_box", "context_box"):
            crop[name] = _construct(PixelBox, _object(crop.get(name), name))
        crop["review"] = _review(crop.get("review"))
        payload["crop"] = _construct(CropRef, crop)
    if payload.get("group") is not None:
        group = _object(payload["group"], "group")
        _tuple(group, "evidence_refs")
        group["review"] = _review(group.get("review"))
        payload["group"] = _construct(GroupReview, group)
    payload["release_review"] = _review(payload.get("release_review"))
    _tuple(payload, "ineligibility_reasons")
    record = _construct(PilotRecord, payload)
    expected = {
        "target_order": list(record.target_order),
        "target_values": list(record.target_values),
        "target_mask": list(record.target_mask),
        "normal_review": record.normal_review,
    }
    # JSON booleans compare equal to 0/1 in Python; reject them as label values.
    for name in ("target_values", "target_mask"):
        observed = derived[name]
        if not isinstance(observed, list) or any(
            item is not None and type(item) is not int for item in observed
        ):
            raise DataContractError(f"{name} must contain nullable integers, not booleans")
    if derived != expected:
        raise DataContractError("Derived encoding/normal state disagrees with reviewed states")
    return record


def validate_records(records: Sequence[PilotRecord]) -> None:
    sample_ids: set[str] = set()
    identities: set[tuple[str, str, str | int | None]] = set()
    split_keys: dict[tuple[str, str], set[str]] = {}
    package_versions: dict[str, set[str]] = {
        name: set() for name in ("dataset_version", "selection_version", "crop_policy_version",
                                "target_encoding_version")
    }
    split_versions: set[str] = set()
    for record in records:
        if not isinstance(record, PilotRecord):
            raise DataContractError("Ledger entries must be PilotRecord")
        for name, versions in package_versions.items():
            versions.add(getattr(record, name))
        if record.sample_id in sample_ids:
            raise DataContractError(f"Duplicate sample_id: {record.sample_id}")
        sample_ids.add(record.sample_id)
        person_or_anchor = record.crop.person_id if record.crop else record.source.label_line_1based
        identity = (
            record.source.archive_sha256,
            record.source.image_sha256,
            person_or_anchor,
        )
        if identity in identities:
            raise DataContractError(f"Duplicate source person/anchor identity: {record.sample_id}")
        identities.add(identity)
        if record.split is None:
            continue
        assert record.split_version is not None
        split_versions.add(record.split_version)
        assert record.crop is not None and record.group is not None
        assert record.group.leakage_group_id is not None
        for kind, key in (
            ("image", record.source.image_sha256),
            ("crop", record.crop.crop_sha256),
            ("group", record.group.leakage_group_id),
        ):
            split_keys.setdefault((kind, key), set()).add(record.split)
    leaked = {key: sorted(splits) for key, splits in split_keys.items() if len(splits) > 1}
    if leaked:
        raise DataContractError(f"Image/crop/group leakage across splits: {leaked}")
    mixed_versions = {
        name: sorted(values) for name, values in package_versions.items() if len(values) > 1
    }
    if mixed_versions or len(split_versions) > 1:
        raise DataContractError(
            f"Mixed package/split versions: {mixed_versions}, splits={sorted(split_versions)}"
        )


def read_records(path: str | Path) -> list[PilotRecord]:
    records: list[PilotRecord] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                raise DataContractError(f"Blank JSONL record at line {line_number}")
            try:
                payload = json.loads(line)
                if isinstance(payload, dict) and payload.get("schema_version") == (
                    MULTILABEL_SCHEMA_VERSION
                ):
                    payload = json.loads(line, object_pairs_hook=_unique_object)
                records.append(record_from_dict(payload))
            except (json.JSONDecodeError, DataContractError) as error:
                raise DataContractError(
                    f"Invalid pilot record at line {line_number}: {error}"
                ) from error
    validate_records(records)
    return records


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise DataContractError(f"Duplicate JSON field: {name}")
        result[name] = value
    return result


def write_records(path: str | Path, records: Sequence[PilotRecord]) -> None:
    validate_records(records)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for record in sorted(records, key=lambda item: item.sample_id):
            handle.write(
                json.dumps(record_to_dict(record), ensure_ascii=False, sort_keys=True) + "\n"
            )
