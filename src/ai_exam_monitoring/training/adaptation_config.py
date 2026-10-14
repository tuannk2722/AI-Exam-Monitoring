"""Resolved, owner-bound variables for matched image mini-batch experiments."""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass, fields
from pathlib import Path, PurePosixPath
from typing import Any

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import ConfigurationError
from ai_exam_monitoring.common.provenance import sha256_file

from .artifacts import digest_json


def strict_fields(payload: Any, model: type[Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != {f.name for f in fields(model)}:
        raise ConfigurationError(f"Invalid {model.__name__} fields")
    return payload


def text(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip() or value.upper().startswith("TBD"):
        raise ConfigurationError(f"Unresolved {name}")


def sha(value: Any) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ConfigurationError("Expected SHA-256")


def local_path(workspace: Path, relative: str) -> Path:
    text(relative, "path")
    if (
        "\\" in relative
        or ":" in relative
        or PurePosixPath(relative).is_absolute()
        or ".." in PurePosixPath(relative).parts
    ):
        raise ConfigurationError("Expected workspace-relative POSIX path")
    path = (workspace / relative).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise ConfigurationError("Path escaped workspace")
    return path


@dataclass(frozen=True)
class FilePin:
    path: str
    sha256: str

    def __post_init__(self) -> None:
        text(self.path, "pin path")
        sha(self.sha256)

    def verify(self, workspace: Path) -> Path:
        path = local_path(workspace, self.path)
        if sha256_file(path) != self.sha256:
            raise ConfigurationError(f"Pinned input changed: {self.path}")
        return path

    def read_json(self, workspace: Path) -> dict[str, Any]:
        payload = json.loads(self.verify(workspace).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ConfigurationError("Expected pinned JSON object")
        return payload


@dataclass(frozen=True)
class DatasetSpec:
    dataset: str
    dataset_version: str
    split_version: str
    encoding_version: str
    payload_sha256: str

    def __post_init__(self) -> None:
        for f in fields(self):
            text(getattr(self, f.name), f.name)
        sha(self.payload_sha256)
        if self.encoding_version != "pilot-b-targets-v1":
            raise ConfigurationError("Unsupported target encoding")


@dataclass(frozen=True)
class CohortSpec:
    name: str
    role: str
    data: DatasetSpec
    sample_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or re.fullmatch(r"[A-Za-z0-9_-]+", self.name) is None:
            raise ConfigurationError("Unsafe cohort name")
        if self.role not in {"train", "selection", "diagnostic"}:
            raise ConfigurationError("Training config cannot enroll holdout")
        if not isinstance(self.data, DatasetSpec):
            raise ConfigurationError("Expected DatasetSpec")
        if (
            not isinstance(self.sample_ids, tuple)
            or not self.sample_ids
            or any(not isinstance(s, str) or not s for s in self.sample_ids)
            or len(set(self.sample_ids)) != len(self.sample_ids)
        ):
            raise ConfigurationError("Require explicit unique cohort IDs in frozen order")


@dataclass(frozen=True)
class AdaptationConfig:
    schema_version: str
    experiment_id: str
    owner: str
    hypothesis: str
    approval_ref: str
    run_kind: str
    model: str
    cohorts: tuple[CohortSpec, ...]
    protocol: FilePin
    readiness: FilePin
    weights: FilePin
    weights_license: FilePin
    head_initialization: FilePin
    weights_id: str
    device: str
    seed: int
    image_size: int
    mean: list[float]
    std: list[float]
    fill: list[int]
    transform: str
    target_order: list[str]
    batch_size: int
    threads: int
    workers: int
    optimizer: str
    head_learning_rate: float
    layer4_learning_rate: float
    weight_decay: float
    max_epochs: int
    patience: int
    min_delta: float
    threshold: float
    wall_time_seconds: float
    objective: str
    bn_policy: str
    sampling: str
    checkpoint_policy: str

    def __post_init__(self) -> None:
        for key in ("experiment_id", "owner", "hypothesis", "approval_ref"):
            text(getattr(self, key), key)
        if re.fullmatch(r"[A-Za-z0-9_-]+", self.experiment_id) is None:
            raise ConfigurationError("Unsafe experiment ID")
        fixed = {
            "schema_version": (
                "matched-adaptation-v2" if isinstance(self, ResearchAdaptationConfig)
                else "matched-adaptation-v1"
            ),
            "weights_id": "IMAGENET1K_V1",
            "device": "cpu",
            "optimizer": "AdamW",
            "transform": "rgb_letterbox_bilinear_v1",
            "target_order": ["phone_use", "looking_around"],
            "objective": "global_known_normalized_minibatch_bce_v1",
            "bn_policy": "all_eval_affine_follows_model_policy",
            "sampling": "uniform_permutation_no_drop_v1",
            "checkpoint_policy": "atomic_epoch_boundary_v1",
        }
        for key, value in fixed.items():
            if getattr(self, key) != value:
                raise ConfigurationError(f"Unsupported {key}")
        if self.model not in {"resnet18_matched_control", "resnet18_layer4"}:
            raise ConfigurationError("Unsupported adaptation model")
        scopes = {"smoke", "research"} if isinstance(self, ResearchAdaptationConfig) else {
            "smoke", "promotion"
        }
        if self.run_kind not in scopes:
            raise ConfigurationError("Unsupported run scope")
        for key in ("batch_size", "threads", "image_size", "max_epochs", "patience"):
            if type(getattr(self, key)) is not int or getattr(self, key) <= 0:
                raise ConfigurationError(f"Expected positive integer {key}")
        if type(self.workers) is not int or self.workers != 0:
            raise ConfigurationError("Only deterministic workers=0 implemented")
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ConfigurationError("Invalid seed")
        for key in (
            "head_learning_rate",
            "layer4_learning_rate",
            "weight_decay",
            "min_delta",
            "threshold",
            "wall_time_seconds",
        ):
            numeric_value: Any = getattr(self, key)
            if (type(numeric_value) not in (float, int) or not math.isfinite(numeric_value)
                    or numeric_value < 0):
                raise ConfigurationError(f"Invalid {key}")
        if (
            min(self.head_learning_rate, self.layer4_learning_rate, self.wall_time_seconds) <= 0
            or not 0 < self.threshold < 1
        ):
            raise ConfigurationError("Invalid learning rate, budget or threshold")
        for key in ("mean", "std", "fill"):
            rgb_value: Any = getattr(self, key)
            if (
                not isinstance(rgb_value, list)
                or len(rgb_value) != 3
                or any(type(v) not in (float, int) or not math.isfinite(v) for v in rgb_value)
            ):
                raise ConfigurationError(f"Invalid RGB {key}")
        if any(v <= 0 for v in self.std) or any(
            type(v) is not int or not 0 <= v <= 255 for v in self.fill
        ):
            raise ConfigurationError("Invalid std/fill")
        for key in ("protocol", "readiness", "weights", "weights_license", "head_initialization"):
            if not isinstance(getattr(self, key), FilePin):
                raise ConfigurationError(f"Expected FilePin for {key}")
        if (
            not isinstance(self.cohorts, tuple)
            or not self.cohorts
            or any(not isinstance(c, CohortSpec) for c in self.cohorts)
        ):
            raise ConfigurationError("Expected explicit cohorts")
        if (
            len({c.name for c in self.cohorts}) != len(self.cohorts)
            or sum(c.role == "train" for c in self.cohorts) != 1
            or sum(c.role == "selection" for c in self.cohorts) != 1
        ):
            raise ConfigurationError("Require one train and one selection cohort")

    def to_dict(self) -> dict[str, Any]:
        # JSON-normalize tuples so YAML, JSON checkpoint and approval hashes agree.
        return dict(json.loads(json.dumps(asdict(self))))

    def match_signature(self) -> str:
        value = self.to_dict()
        for key in ("experiment_id", "model", "approval_ref", "hypothesis"):
            value.pop(key)
        return digest_json(value)


@dataclass(frozen=True)
class HeadProvenance:
    kind: str
    seed: int | None
    parent_checkpoint: FilePin | None
    parent_epoch: int | None

    def __post_init__(self) -> None:
        if self.kind == "random_seed":
            if (type(self.seed) is not int or not 0 <= self.seed < 2**32
                    or self.parent_checkpoint is not None or self.parent_epoch is not None):
                raise ConfigurationError("Invalid random head provenance")
        elif self.kind == "parent_fc":
            if (self.seed is not None or not isinstance(self.parent_checkpoint, FilePin)
                    or type(self.parent_epoch) is not int or self.parent_epoch <= 0):
                raise ConfigurationError("Invalid learned head provenance")
        else:
            raise ConfigurationError("Unsupported head provenance")


@dataclass(frozen=True)
class ResearchAdaptationConfig(AdaptationConfig):
    head_provenance: HeadProvenance
    diagnostic_steps: tuple[int, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        if not isinstance(self.head_provenance, HeadProvenance):
            raise ConfigurationError("Require explicit head provenance")
        if (self.head_provenance.kind == "random_seed"
                and self.head_provenance.seed != self.seed):
            raise ConfigurationError("Random head seed must match run seed")
        if (not isinstance(self.diagnostic_steps, tuple)
                or any(type(s) is not int or s <= 0 for s in self.diagnostic_steps)
                or tuple(sorted(set(self.diagnostic_steps))) != self.diagnostic_steps):
            raise ConfigurationError("Require sorted unique positive diagnostic steps")
        train = next(c for c in self.cohorts if c.role == "train")
        if self.diagnostic_steps and self.diagnostic_steps[-1] >= math.ceil(
            len(train.sample_ids) / self.batch_size
        ):
            raise ConfigurationError("Diagnostics must precede first epoch boundary")


def config_from_dict(raw: Any) -> AdaptationConfig:
    model = (ResearchAdaptationConfig if isinstance(raw, dict)
             and raw.get("schema_version") == "matched-adaptation-v2" else AdaptationConfig)
    value = dict(strict_fields(raw, model))
    for key in ("protocol", "readiness", "weights", "weights_license", "head_initialization"):
        value[key] = FilePin(**strict_fields(value[key], FilePin))
    if not isinstance(value["cohorts"], list):
        raise ConfigurationError("Cohorts must be an array")
    cohorts = []
    for raw_cohort in value["cohorts"]:
        cohort = dict(strict_fields(raw_cohort, CohortSpec))
        cohort["data"] = DatasetSpec(**strict_fields(cohort["data"], DatasetSpec))
        if not isinstance(cohort["sample_ids"], list):
            raise ConfigurationError("Sample IDs must be an array")
        cohort["sample_ids"] = tuple(cohort["sample_ids"])
        cohorts.append(CohortSpec(**cohort))
    value["cohorts"] = tuple(cohorts)
    if model is ResearchAdaptationConfig:
        head = dict(strict_fields(value["head_provenance"], HeadProvenance))
        if head["parent_checkpoint"] is not None:
            head["parent_checkpoint"] = FilePin(
                **strict_fields(head["parent_checkpoint"], FilePin)
            )
        value["head_provenance"] = HeadProvenance(**head)
        if not isinstance(value["diagnostic_steps"], list):
            raise ConfigurationError("Diagnostic steps must be an array")
        value["diagnostic_steps"] = tuple(value["diagnostic_steps"])
    return model(**value)


def load_adaptation_config(path: Path) -> AdaptationConfig:
    return config_from_dict(load_yaml(path))


def verify_adaptation_approval(config: AdaptationConfig, workspace: Path) -> None:
    approval = json.loads(local_path(workspace, config.approval_ref).read_text(encoding="utf-8"))
    if (
        approval.get("status") != "approved"
        or approval.get("owner") != config.owner
        or approval.get("scope") != "local_classifier_research"
        or approval.get("run_kind") != config.run_kind
        or approval.get("configs", {}).get(config.experiment_id) != digest_json(config.to_dict())
        or (
            approval.get("config_signatures", {}).get(config.experiment_id)
            if isinstance(config, ResearchAdaptationConfig)
            else approval.get("matched_signature")
        ) != config.match_signature()
    ):
        raise ConfigurationError("Exact matched run/config approval missing")
    if isinstance(config, ResearchAdaptationConfig):
        from .artifacts import code_identity

        if (approval.get("code_sha256") != code_identity()["sha256"]
                or approval.get("final_test_inference_authorized") is not False):
            raise ConfigurationError("Research approval must bind code and closed test scope")
        authorization = FilePin(
            **strict_fields(approval.get("owner_authorization"), FilePin)
        ).read_json(workspace)
        if (authorization.get("status") != "approved"
                or authorization.get("owner") != config.owner
                or authorization.get("final_test_inference_authorized") is not False):
            raise ConfigurationError("Research owner authorization missing or wrong scope")


def verify_matched_configs(control: AdaptationConfig, candidate: AdaptationConfig) -> None:
    if (
        control.model != "resnet18_matched_control"
        or candidate.model != "resnet18_layer4"
        or control.experiment_id == candidate.experiment_id
        or control.match_signature() != candidate.match_signature()
    ):
        raise ConfigurationError("Control/candidate variables or initialization are not matched")
