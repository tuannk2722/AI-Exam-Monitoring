"""Bounded incremental candidates from timestamped, track-snapshot observations.

Internal metadata only: no evidence images, database, wire schema or confirmation.
The consumer must persist support/revisions before presenting reviewable events.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from ai_exam_monitoring.common.errors import DataContractError

from .frame_processor import Anchor
from .live_timing import LiveTimingPolicy, SelectedSlot, TrackingToken, validate_slot
from .streaming import FrameStamp

BEHAVIORS = ("phone_use", "looking_around")


@dataclass(frozen=True)
class TrackedScores:
    anchor: Anchor
    track_id: int | None
    scores: tuple[float | None, float | None]


@dataclass(frozen=True)
class Support:
    stamp: FrameStamp
    anchor: Anchor
    score: float


@dataclass(frozen=True)
class CandidateUpdate:
    event_id: str
    track_id: int
    behavior: str
    epoch: int
    generation: int
    lifecycle: str
    reason: str | None
    support_count: int
    first: Support
    latest: Support
    initial_support: tuple[Support, ...]
    mean_score: float


@dataclass
class _Segment:
    event_id: str
    track_id: int
    behavior: str
    first: Support
    latest: Support
    count: int = 0
    total: float = 0.
    initial: list[Support] = field(default_factory=list)
    candidate: bool = False


class LiveCandidates:
    """One source-ordered owner; memory bounded by current anchors/targets.

    Keep only the first minimum support samples and latest support per segment.
    These refs do not constitute a full persisted support history. Every eligible
    update is returned to the caller; there is no retained queue of old events.
    """

    def __init__(self, policy: LiveTimingPolicy, session_id: str,
                 thresholds: Sequence[float], *, epoch: int, generation: int):
        if (not session_id or len(thresholds) != 2
                or any(not math.isfinite(t) or not 0 <= t <= 1 for t in thresholds)
                or any(type(n) is not int or n < 0 for n in (epoch, generation))):
            raise DataContractError("Invalid live event identity/thresholds")
        self.policy, self.session_id = policy, session_id
        self.thresholds = tuple(thresholds)
        self.epoch, self.generation = epoch, generation
        self.active: dict[tuple[int, str], _Segment] = {}
        self.serial = self.stale_results = 0
        self.last_slot = -1
        self.last_stamp: FrameStamp | None = None
        self.last_selection: SelectedSlot | None = None

    def _snapshot(self, segment: _Segment, lifecycle: str,
                  reason: str | None = None) -> CandidateUpdate:
        return CandidateUpdate(segment.event_id, segment.track_id, segment.behavior,
                               self.epoch, self.generation, lifecycle, reason, segment.count,
                               segment.first, segment.latest, tuple(segment.initial),
                               segment.total / segment.count)

    def _finish(self, key: tuple[int, str], reason: str) -> CandidateUpdate | None:
        segment = self.active.pop(key)
        return self._snapshot(segment, "closed", reason) if segment.candidate else None

    def close(self, reason: str) -> list[CandidateUpdate]:
        result = []
        for key in list(self.active):
            update = self._finish(key, reason)
            if update is not None:
                result.append(update)
        return result

    def advance(self, *, epoch: int, generation: int, reason: str) -> list[CandidateUpdate]:
        if (any(type(n) is not int or n < 0 for n in (epoch, generation))
                or (epoch, generation) <= (self.epoch, self.generation)):
            raise DataContractError("Continuity must advance")
        result = self.close(reason)
        self.epoch, self.generation = epoch, generation
        self.last_slot, self.last_stamp = -1, None
        self.last_selection = None
        return result

    def mark_missing(self, slot_index: int) -> list[CandidateUpdate]:
        """Close on a declared missing G0 slot without fabricating a source frame."""
        if (type(slot_index) is not int or slot_index <= self.last_slot
                or slot_index % self.policy.classifier_stride):
            raise DataContractError("Missing classifier slot must advance on its grid")
        self.last_slot = slot_index
        return self.close("missing_classifier_slot")

    def consume(self, token: TrackingToken,
                observations: Sequence[TrackedScores]) -> list[CandidateUpdate]:
        slot, stamp = token.slot, token.slot.stamp
        validate_slot(slot, self.policy)
        if (stamp.session_id != self.session_id or type(token.generation) is not int
                or token.generation < 0 or not token.classifier_due
                or slot.index % self.policy.classifier_stride):
            raise DataContractError("Invalid classifier frame token")
        identity = (stamp.epoch, token.generation)
        if identity < (self.epoch, self.generation) or (
            identity == (self.epoch, self.generation) and slot.index <= self.last_slot
        ):
            self.stale_results += 1
            return []
        if identity == (self.epoch, self.generation) and self.last_stamp is not None and (
            stamp.sequence <= self.last_stamp.sequence
            or stamp.source_time_ms <= self.last_stamp.source_time_ms
            or stamp.captured_ns <= self.last_stamp.captured_ns
            or (stamp.width, stamp.height) != (self.last_stamp.width, self.last_stamp.height)
        ):
            raise DataContractError("Classifier source identity must advance")
        if (identity == (self.epoch, self.generation) and self.last_selection is not None
                and not math.isclose(
                    slot.due_ms - self.last_selection.due_ms,
                    (slot.index - self.last_selection.index) * self.policy.detector_interval_ms,
                    rel_tol=0, abs_tol=1e-6)):
            raise DataContractError("Classifier slots must share the source grid")
        if len(observations) > 100:
            raise DataContractError("Observations exceed parent detector max_det")
        anchors: set[str] = set()
        tracks: set[int] = set()
        positives: dict[tuple[int, str], Support] = {}
        for obs in observations:
            if not obs.anchor.anchor_id or obs.anchor.anchor_id in anchors:
                raise DataContractError("Duplicate or missing anchor")
            anchors.add(obs.anchor.anchor_id)
            for box in (obs.anchor.person_box, obs.anchor.context_box):
                if (len(box) != 4 or any(not math.isfinite(v) for v in box)
                        or not 0 <= box[0] < box[2] <= stamp.width
                        or not 0 <= box[1] < box[3] <= stamp.height):
                    raise DataContractError("Support geometry outside its source frame")
            if obs.track_id is not None:
                if (type(obs.track_id) is not int or obs.track_id <= 0 or obs.track_id in tracks):
                    raise DataContractError("Invalid or duplicated track in frame")
                tracks.add(obs.track_id)
            if len(obs.scores) != 2:
                raise DataContractError("Expected two target scores")
            for behavior, score, threshold in zip(
                BEHAVIORS, obs.scores, self.thresholds, strict=True
            ):
                if score is not None and (
                    type(score) not in (float, int)
                    or not math.isfinite(score) or not 0 <= score <= 1
                ):
                    raise DataContractError("Invalid behavior score")
                if obs.track_id is not None and score is not None and score >= threshold:
                    positives[(obs.track_id, behavior)] = Support(stamp, obs.anchor, score)
        updates = []
        if identity > (self.epoch, self.generation):
            updates.extend(self.advance(epoch=stamp.epoch, generation=token.generation,
                                        reason="continuity_reset"))
        if self.last_slot >= 0 and slot.index != self.last_slot + self.policy.classifier_stride:
            updates.extend(self.close("missing_classifier_slot"))
        for key in list(self.active):
            if key not in positives:
                update = self._finish(key, "negative_unknown_or_unassigned")
                if update is not None:
                    updates.append(update)
        for key, support in positives.items():
            if key not in self.active:
                self.serial += 1
                event_id = (f"{self.policy.policy_id}:{self.session_id}:{self.epoch}:"
                            f"{self.generation}:{key[0]}:{key[1]}:{self.serial}")
                self.active[key] = _Segment(event_id, *key, support, support)
            segment = self.active[key]
            segment.count += 1
            segment.total += support.score
            segment.latest = support
            if len(segment.initial) < self.policy.min_positive_observations:
                segment.initial.append(support)
            if (segment.count >= self.policy.min_positive_observations
                    and support.stamp.source_time_ms - segment.first.stamp.source_time_ms
                    >= self.policy.min_observed_span_ms):
                segment.candidate = True
                updates.append(self._snapshot(segment, "open"))
        self.last_slot, self.last_stamp = slot.index, stamp
        self.last_selection = slot
        return updates
