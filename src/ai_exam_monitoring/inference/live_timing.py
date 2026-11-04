"""Approved source-clock slot selection and continuity; no capture/model execution."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError

from .streaming import FrameStamp


@dataclass(frozen=True)
class LiveTimingPolicy:
    policy_id: str
    detector_interval_ms: int
    frame_tolerance_ms: int
    classifier_stride: int
    min_positive_observations: int
    min_observed_span_ms: int

    @classmethod
    def load(cls, path: Path) -> LiveTimingPolicy:
        raw = load_yaml(path)
        expected = dict(
            schema_version="live-timing-policy-v1", policy_id="LIVE-TIMING-20261028",
            status="approved_for_implementation_and_fixtures", detector_interval_ms=100,
            frame_tolerance_ms=50, classifier_stride=10, min_positive_observations=3,
            min_observed_span_ms=2000, reset_tracker_on_missing_slot=True,
            break_on_missing_classifier=True, bridge_negative_or_unknown=False,
            propagate_behavior_labels=False,
        )
        if (set(raw) != set(expected)
                or any(type(raw[k]) is not type(v) or raw[k] != v for k, v in expected.items())):
            raise DataContractError("Unsupported or unapproved live timing policy")
        return cls(**{name: raw[name] for name in cls.__dataclass_fields__})


@dataclass(frozen=True)
class SelectedSlot:
    stamp: FrameStamp
    index: int
    due_ms: float


@dataclass(frozen=True)
class TrackingToken:
    slot: SelectedSlot
    generation: int
    reset_required: bool
    missing_detector_slots: int
    classifier_due: bool


def validate_slot(slot: SelectedSlot, policy: LiveTimingPolicy) -> None:
    if (type(slot.index) is not int or slot.index < 0 or not math.isfinite(slot.due_ms)
            or slot.due_ms < 0
            or not 0 <= slot.stamp.source_time_ms - slot.due_ms <= policy.frame_tolerance_ms):
        raise DataContractError("Frame outside its source-clock slot")


class SlotSelector:
    """Consume every captured frame; retain only counters and the last identity.

    origin_ms is explicit: source zero initially, the selected source position
    after seek. A new instance belongs to each epoch. Never fabricate timestamps.
    Missing slots are counted arithmetically, even after a very large clock jump.
    """

    def __init__(self, policy: LiveTimingPolicy, session_id: str, epoch: int, *, origin_ms: float):
        if (not session_id or type(epoch) is not int or epoch < 0
                or not math.isfinite(origin_ms) or origin_ms < 0):
            raise DataContractError("Invalid source clock identity/origin")
        self.policy, self.session_id, self.epoch = policy, session_id, epoch
        self.origin_ms = origin_ms
        self.next_slot = self.selected = self.missing = 0
        self.last: FrameStamp | None = None

    def offer(self, stamp: FrameStamp) -> SelectedSlot | None:
        if (stamp.session_id != self.session_id or stamp.epoch != self.epoch
                or stamp.source_time_ms < self.origin_ms):
            raise DataContractError("Frame outside active source clock")
        if self.last is not None and (
            stamp.sequence <= self.last.sequence or stamp.captured_ns <= self.last.captured_ns
            or stamp.source_time_ms <= self.last.source_time_ms
            or (stamp.width, stamp.height) != (self.last.width, self.last.height)
        ):
            raise DataContractError("Frame identity must advance without changing geometry")
        self.last = stamp
        index = math.floor((stamp.source_time_ms - self.origin_ms)
                           / self.policy.detector_interval_ms)
        if index < self.next_slot:
            return None
        self.missing += index - self.next_slot
        due = self.origin_ms + index * self.policy.detector_interval_ms
        self.next_slot = index + 1
        if stamp.source_time_ms - due > self.policy.frame_tolerance_ms:
            self.missing += 1
            return None
        self.selected += 1
        return SelectedSlot(stamp, index, due)


class TrackingContinuity:
    """Consume slots actually processed, so latest-buffer drops also reset tracks.

    Caller must reset its tracker before updating a token with reset_required.
    Tokens snapshot generation for later classification; never reassign them.
    """

    def __init__(self, policy: LiveTimingPolicy, session_id: str, epoch: int):
        self.policy, self.session_id, self.epoch = policy, session_id, epoch
        self.generation = self.missing = 0
        self.last: SelectedSlot | None = None
        self._force_reset = True

    def reset(self) -> None:
        """Pause/resume in the same epoch; invalidate any in-flight G0 token now."""
        self.generation += 1
        self._force_reset = True

    def accept(self, slot: SelectedSlot) -> TrackingToken:
        validate_slot(slot, self.policy)
        if slot.stamp.session_id != self.session_id or slot.stamp.epoch != self.epoch:
            raise DataContractError("Slot belongs to another epoch/session")
        previous = self.last
        if previous is not None and (
            slot.index <= previous.index or slot.stamp.sequence <= previous.stamp.sequence
            or slot.stamp.source_time_ms <= previous.stamp.source_time_ms
            or slot.stamp.captured_ns <= previous.stamp.captured_ns
            or (slot.stamp.width, slot.stamp.height)
            != (previous.stamp.width, previous.stamp.height)
            or not math.isclose(slot.due_ms - previous.due_ms,
                                (slot.index - previous.index) * self.policy.detector_interval_ms,
                                rel_tol=0, abs_tol=1e-6)
        ):
            raise DataContractError("Tracking slots must advance on the same grid")
        missing = slot.index - (previous.index + 1 if previous else 0)
        if missing:
            self.generation += 1
            self.missing += missing
        reset = self._force_reset or missing > 0
        self._force_reset = False
        self.last = slot
        return TrackingToken(slot, self.generation, reset, missing,
                             slot.index % self.policy.classifier_stride == 0)
