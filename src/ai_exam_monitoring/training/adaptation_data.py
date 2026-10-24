"""Exact cohort and whole-family enrollment for approved adaptation experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from torch.nn import functional as F
from torchvision.transforms import functional as TF

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import PilotRecord, record_to_dict

from .adaptation_config import (
    AdaptationConfig,
    E005AdaptationConfig,
    FilePin,
    RepresentationConfig,
    local_path,
)
from .artifacts import digest_json
from .data import (
    compute_relative_anchor_geometry,
    crop_path,
    extract_anchor_subcrop,
    image_tensor,
    labels,
    letterbox,
    verify_dataset,
)


def _uint8_letterbox(image: Image.Image, config: AdaptationConfig) -> torch.Tensor:
    return TF.pil_to_tensor(letterbox(image, config))



def _normalize_float_chw(
    tensor_chw: torch.Tensor, mean: list[float], std: list[float]
) -> torch.Tensor:
    m = torch.tensor(mean, dtype=torch.float32).view(3, 1, 1)
    s = torch.tensor(std, dtype=torch.float32).view(3, 1, 1)
    return (tensor_chw - m) / s


def _apply_photometric_jitter(
    img_float: torch.Tensor, b_factor: float, c_factor: float, s_factor: float
) -> torch.Tensor:
    out = (img_float * b_factor).clamp(0.0, 1.0)
    mean_spatial = out.mean(dim=(1, 2), keepdim=True)
    out = ((out - mean_spatial) * c_factor + mean_spatial).clamp(0.0, 1.0)
    gray = (0.2989 * out[0:1] + 0.5870 * out[1:2] + 0.1140 * out[2:3])
    out = ((out - gray) * s_factor + gray).clamp(0.0, 1.0)
    return out


@dataclass
class ImageCohort:
    name: str
    role: str
    records: list[PilotRecord]
    paths: list[Path]
    values: torch.Tensor
    mask: torch.Tensor
    groups: list[str]
    _context_cache: dict[int, torch.Tensor] = field(default_factory=dict, init=False, repr=False)
    _anchor_cache: dict[int, torch.Tensor] = field(default_factory=dict, init=False, repr=False)
    _geometry_cache: dict[int, torch.Tensor] = field(default_factory=dict, init=False, repr=False)
    _v4_cache_key: str | None = field(default=None, init=False, repr=False)

    @property
    def ids(self) -> list[str]:
        return [r.sample_id for r in self.records]

    def batch(self, indices: list[int], config: AdaptationConfig) -> torch.Tensor:
        return torch.stack([image_tensor(self.paths[i], config) for i in indices])

    def _ensure_cached(self, idx: int, config: E005AdaptationConfig) -> None:
        if isinstance(config, RepresentationConfig):
            key = digest_json({"size": config.image_size, "fill": config.fill,
                               "transform": config.transform, "model": config.model})
            if key != self._v4_cache_key:
                self._context_cache.clear()
                self._anchor_cache.clear()
                self._geometry_cache.clear()
                self._v4_cache_key = key
        if idx in self._context_cache:
            return
        record = self.records[idx]
        if record.crop is None:
            raise DataContractError("Missing crop metadata in cohort record")
        with Image.open(self.paths[idx]) as raw_image:
            rgb_image = raw_image.convert("RGB")
            self._context_cache[idx] = _uint8_letterbox(rgb_image, config)
            if config.model == "resnet18_anchor_context":
                geom = compute_relative_anchor_geometry(
                    record.crop.person_box, record.crop.context_box
                )
                self._geometry_cache[idx] = torch.tensor(geom, dtype=torch.float32)
                anchor_pil = extract_anchor_subcrop(
                    rgb_image,
                    record.crop.person_box,
                    record.crop.context_box,
                    padding_ratio=config.anchor_padding_ratio,
                )
                self._anchor_cache[idx] = _uint8_letterbox(anchor_pil, config)

    def model_batch(
        self,
        indices: list[int],
        config: AdaptationConfig,
        *,
        epoch: int | None = None,
        train_mode: bool = False,
    ) -> torch.Tensor | dict[str, torch.Tensor]:
        if not isinstance(config, E005AdaptationConfig):
            return self.batch(indices, config)
        is_dual = config.model == "resnet18_anchor_context"
        aug = config.augmentation
        do_aug = bool(train_mode and aug.enabled)
        ctx_list: list[torch.Tensor] = []
        anc_list: list[torch.Tensor] = []
        geo_list: list[torch.Tensor] = []
        size = config.image_size
        for i in indices:
            self._ensure_cached(i, config)
            ctx_f = self._context_cache[i].to(dtype=torch.float32) / 255.0
            anc_f = (
                self._anchor_cache[i].to(dtype=torch.float32) / 255.0
                if is_dual
                else ctx_f
            )
            geo = (
                self._geometry_cache[i].clone()
                if is_dual
                else torch.zeros(6, dtype=torch.float32)
            )
            if do_aug:
                gen = torch.Generator()
                sample_seed = (
                    int(config.seed)
                    + int(epoch if epoch is not None else 1) * 100003
                    + int(i) * 97
                ) % (2**31 - 1)
                gen.manual_seed(sample_seed)
                # 1. Horizontal flip (synchronous across anchor, context, and geometry)
                if (
                    aug.horizontal_flip_prob > 0.0
                    and float(torch.rand(1, generator=gen)) < aug.horizontal_flip_prob
                ):
                    ctx_f = torch.flip(ctx_f, dims=[2])
                    if is_dual:
                        anc_f = torch.flip(anc_f, dims=[2])
                        old_rx1, old_rx2 = float(geo[0]), float(geo[2])
                        geo[0] = 1.0 - old_rx2
                        geo[2] = 1.0 - old_rx1
                # 2. Anchor box jitter (zoom/shift on anchor tensor + geometry perturbation)
                if is_dual and aug.box_jitter_ratio > 0.0:
                    j = aug.box_jitter_ratio
                    deltas = (torch.rand(4, generator=gen) * 2.0 - 1.0) * j
                    max_crop = int(round(size * j))
                    if max_crop >= 1:
                        top = int(torch.randint(0, max_crop + 1, (1,), generator=gen))
                        left = int(torch.randint(0, max_crop + 1, (1,), generator=gen))
                        bottom = size - int(torch.randint(0, max_crop + 1, (1,), generator=gen))
                        right = size - int(torch.randint(0, max_crop + 1, (1,), generator=gen))
                        if bottom - top >= size // 2 and right - left >= size // 2:
                            cropped = anc_f[:, top:bottom, left:right].unsqueeze(0)
                            anc_f = F.interpolate(
                                cropped, size=(size, size), mode="bilinear", align_corners=False
                            ).squeeze(0)
                    gw, gh = float(geo[4]), float(geo[5])
                    rx1 = max(0.0, min(1.0, float(geo[0]) + float(deltas[0]) * gw))
                    ry1 = max(0.0, min(1.0, float(geo[1]) + float(deltas[1]) * gh))
                    rx2 = max(rx1 + 1e-4, min(1.0, float(geo[2]) + float(deltas[2]) * gw))
                    ry2 = max(ry1 + 1e-4, min(1.0, float(geo[3]) + float(deltas[3]) * gh))
                    geo = torch.tensor(
                        [rx1, ry1, rx2, ry2, rx2 - rx1, ry2 - ry1], dtype=torch.float32
                    )
                # 3. Synchronous Photometric Jitter
                b_jit = (torch.rand(1, generator=gen) * 2.0 - 1.0) * aug.brightness_jitter
                c_jit = (torch.rand(1, generator=gen) * 2.0 - 1.0) * aug.contrast_jitter
                s_jit = (torch.rand(1, generator=gen) * 2.0 - 1.0) * aug.saturation_jitter
                b_fac = 1.0 + float(b_jit)
                c_fac = 1.0 + float(c_jit)
                s_fac = 1.0 + float(s_jit)
                ctx_f = _apply_photometric_jitter(ctx_f, b_fac, c_fac, s_fac)
                if is_dual:
                    anc_f = _apply_photometric_jitter(anc_f, b_fac, c_fac, s_fac)
                # 4. Random Erasing on context
                if (
                    aug.random_erasing_prob > 0.0
                    and float(torch.rand(1, generator=gen)) < aug.random_erasing_prob
                ):
                    min_e, max_e = max(1, size // 12), max(2, size // 4)
                    eh = int(torch.randint(min_e, max_e, (1,), generator=gen))
                    ew = int(torch.randint(min_e, max_e, (1,), generator=gen))
                    ey = int(torch.randint(0, max(1, size - eh), (1,), generator=gen))
                    ex = int(torch.randint(0, max(1, size - ew), (1,), generator=gen))
                    fill_val = torch.tensor(config.mean, dtype=torch.float32).view(3, 1, 1)
                    ctx_f = ctx_f.clone()
                    ctx_f[:, ey : ey + eh, ex : ex + ew] = fill_val

            ctx_list.append(_normalize_float_chw(ctx_f, config.mean, config.std))
            if is_dual:
                anc_list.append(_normalize_float_chw(anc_f, config.mean, config.std))
                geo_list.append(geo)
        ctx_batch = torch.stack(ctx_list)
        if not is_dual:
            return ctx_batch
        return {
            "anchor": torch.stack(anc_list),
            "context": ctx_batch,
            "geometry": torch.stack(geo_list),
        }



def _waiver(config: AdaptationConfig, workspace: Path, ready: dict[str, Any]) -> None:
    """V2 is an explicit owner-authorized research revision, never fake independence."""
    protocol = config.protocol.read_json(workspace)
    if protocol.get("schema_version") != "matched-protocol-v2":
        raise DataContractError("Waiver readiness requires protocol v2")
    value = ready.get("waiver_approval")
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise DataContractError("Require exact waiver approval pin")
    approval = FilePin(**value).read_json(workspace)
    if (
        protocol.get("waiver_approval") != value
        or approval.get("status") != "approved"
        or approval.get("owner") != config.owner
        or approval.get("waive_independence") is not True
        or approval.get("waive_support_shortfalls") is not True
        or approval.get("final_test_inference_authorized") is not False
        or protocol.get("independence_claim") is not False
        or protocol.get("final_test_inference_authorized") is not False
        or protocol.get("M4_status") != "INCONCLUSIVE"
    ):
        raise DataContractError("Waiver scope/owner/policy mismatch")


def validate_readiness(config: AdaptationConfig, workspace: Path) -> dict[str, Any]:
    ready = config.readiness.read_json(workspace)
    if isinstance(config, RepresentationConfig):
        if (ready.get("schema_version") != "representation-readiness-v4"
                or ready.get("status") != "approved" or ready.get("owner") != config.owner
                or ready.get("scope") != config.run_kind
                or ready.get("protocol_sha256") != config.protocol.sha256
                or ready.get("cohorts_sha256") != digest_json(config.to_dict()["cohorts"])
                or ready.get("execution_authorization")
                != config.to_dict()["execution_authorization"]
                or ready.get("independence_claim") is not False):
            raise DataContractError("V4 readiness identity/scope mismatch")
        evidence = ready.get("evidence_pins")
        if not isinstance(evidence, list) or not evidence:
            raise DataContractError("V4 readiness evidence missing")
        for item in evidence:
            FilePin(**item).verify(workspace)
        if config.run_kind == "research":
            from .artifacts import code_identity

            receipt = FilePin(**ready["smoke_receipt"]).read_json(workspace)
            if (receipt.get("status") != "PASS" or receipt.get("device") != config.device
                    or receipt.get("code_sha256") != code_identity()["sha256"]
                    or receipt.get("payload_sha256")
                    != next(c.data.payload_sha256 for c in config.cohorts if c.role == "train")
                    or receipt.get("checks") != {
                        "resume": "PASS", "reload": "PASS", "stage_transition": "PASS"
                    }):
                raise DataContractError("Actual V4 smoke PASS required")
        return ready
    if (
        ready.get("schema_version") not in {"adaptation-readiness-v1", "adaptation-readiness-v2"}
        or ready.get("status") != "approved"
        or ready.get("owner") != config.owner
        or ready.get("scope") != config.run_kind
        or ready.get("protocol_sha256") != config.protocol.sha256
        or ready.get("cohorts_sha256") != digest_json(config.to_dict()["cohorts"])
        or not ready.get("decision_ref")
    ):
        raise DataContractError("Readiness does not bind exact data/protocol/action")
    revised = ready["schema_version"] in {"adaptation-readiness-v2", "representation-readiness-v4"}
    if revised:
        _waiver(config, workspace, ready)
    gates = ready.get("gates", {})
    required: tuple[str, ...] = (
        ("G0", "G1", "G2", "G3") if config.run_kind in {"promotion", "research"} else ("G0",)
    )
    if revised and config.run_kind in {"promotion", "research"}:
        required = ("G0", "G1")
        if any(gates.get(gate) != "owner_waived" for gate in ("G2", "G3")):
            raise DataContractError("Waived gates must not claim verified PASS")
    if any(gates.get(gate) is not True for gate in required):
        raise DataContractError("Required readiness gate is not approved")
    evidence = ready.get("evidence_pins")
    if not isinstance(evidence, list) or not evidence:
        raise DataContractError("Readiness requires source/acceptance evidence pins")
    for pin in evidence:
        FilePin(**pin).verify(workspace)
    if config.run_kind == "promotion" and not revised:
        support = ready.get("holdout_support", {})
        requirements = {"independent_groups": 10, "verified_contexts": 2}
        for target in config.target_order:
            for key, minimum in (
                ("positive", 100),
                ("negative", 100),
                ("positive_groups", 5),
                ("negative_groups", 5),
            ):
                value = support.get(target, {}).get(key)
                if type(value) is not int or value < minimum:
                    raise DataContractError("G3 target/group support insufficient")
        for key, minimum in requirements.items():
            if type(support.get(key)) is not int or support[key] < minimum:
                raise DataContractError("G3 independent groups/contexts insufficient")
    return ready


def prepare_cohorts(
    config: AdaptationConfig, workspace: Path
) -> tuple[list[ImageCohort], dict[str, Any]]:
    ready = validate_readiness(config, workspace)
    revised = ready["schema_version"] in {"adaptation-readiness-v2", "representation-readiness-v4"}
    protocol = config.protocol.read_json(workspace)
    if (
        protocol.get("schema_version")
        != ("representation-protocol-v4" if isinstance(config, RepresentationConfig)
            else "matched-protocol-v2" if revised else "matched-protocol-v1")
        or protocol.get("status") != "frozen"
        or protocol.get("owner") != config.owner
        or protocol.get("target_order") != config.target_order
        or not protocol.get("decision_ref")
        or set(protocol.get("cohorts", {})) != {c.name for c in config.cohorts}
    ):
        raise DataContractError("Unfrozen or mismatched cohort protocol")
    cache: dict[str, list[PilotRecord]] = {}
    cohorts = []
    families = protocol.get("family_assignments", {})
    reserved = protocol.get("reserved_holdout", {})
    if not isinstance(reserved.get("source_sha256"), list) or not isinstance(
        reserved.get("family_ids"), list
    ):
        raise DataContractError("Protocol must explicitly reserve holdout identities")
    for spec in config.cohorts:
        root = local_path(workspace, spec.data.dataset)
        key = digest_json(spec.data.__dict__)
        if key not in cache:
            cache[key] = verify_dataset(root, spec.data)
        if isinstance(config, RepresentationConfig) and any(
            row.usage == "test" for row in cache[key]
        ):
            raise DataContractError("V4 protocol requires an explicitly zero-test release")
        all_rows = {r.sample_id: r for r in cache[key]}
        if not set(spec.sample_ids) <= set(all_rows):
            raise DataContractError("Cohort member missing from accepted manifest")
        rows = [all_rows[s] for s in spec.sample_ids]
        expected_usage = "train" if spec.role == "train" else "val"
        if any(r.usage != expected_usage or not any(r.target_mask) for r in rows):
            raise DataContractError("Wrong split/review-only/test/all-unknown cohort member")
        receipt = protocol["cohorts"][spec.name]
        if receipt.get("role") != spec.role or receipt.get("records_sha256") != digest_json(
            [record_to_dict(r) for r in rows]
        ):
            raise DataContractError("Cohort record/label/geometry/order pin changed")
        groups = []
        for row in rows:
            group = families.get(row.sample_id, {})
            if (
                not isinstance(group.get("family_id"), str)
                or not group["family_id"]
                or not group.get("evidence_refs")
                or group.get("owner_accepted") is not True
            ):
                raise DataContractError("Whole-family membership lacks owner evidence")
            if (spec.role == "selection" and not revised
                    and group.get("independence_verified") is not True):
                raise DataContractError("New-development independence not verified")
            if (
                row.source.image_sha256 in reserved["source_sha256"]
                or group["family_id"] in reserved["family_ids"]
            ):
                raise DataContractError("Holdout identity enrolled in training/development")
            groups.append(group["family_id"])
        values, mask = labels(rows)
        cohorts.append(
            ImageCohort(
                spec.name, spec.role, rows, [crop_path(root, r) for r in rows], values, mask, groups
            )
        )
    train = next(c for c in cohorts if c.role == "train")
    for other in cohorts:
        if other is train:
            continue
        for a, b in (
            (set(train.ids), set(other.ids)),
            (set(train.groups), set(other.groups)),
            (
                {r.source.image_sha256 for r in train.records},
                {r.source.image_sha256 for r in other.records},
            ),
            (
                {r.crop.crop_sha256 for r in train.records if r.crop},
                {r.crop.crop_sha256 for r in other.records if r.crop},
            ),
        ):
            if a & b:
                raise DataContractError("Train/development ID/source/crop/family leakage")
    return cohorts, protocol
