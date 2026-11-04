"""Bounded stage timings for one inference owner; no SLA/acceptance inference."""

from __future__ import annotations

import math
import time
from collections import deque
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

from ai_exam_monitoring.common.errors import DataContractError

STAGES = ("detect", "crop", "classify", "frame", "decode", "encode")


class StageProfiler:
    """Cumulative count/mean/max plus explicitly labelled rolling percentiles.

    Synchronize the execution device before and after timed sections. GPU wall
    time includes transfers and completed work, not only kernel enqueue time.
    A failed operation contributes to failures, never to successful latency.
    Snapshot from the owner thread; this is not a concurrent metrics registry.
    """

    def __init__(self, capacity: int, *, synchronize: Callable[[], None],
                 clock: Callable[[], int] = time.perf_counter_ns):
        if type(capacity) is not int or capacity < 1:
            raise DataContractError("Timing window capacity must be positive")
        self.capacity = capacity
        self.synchronize = synchronize
        self.clock = clock
        self._values: dict[str, deque[float]] = {s: deque(maxlen=capacity) for s in STAGES}
        self._count = dict.fromkeys(STAGES, 0)
        self._failed = dict.fromkeys(STAGES, 0)
        self._total = dict.fromkeys(STAGES, 0.0)
        self._max = dict.fromkeys(STAGES, 0.0)

    @contextmanager
    def measure(self, stage: str) -> Iterator[None]:
        if stage not in self._values:
            raise DataContractError("Unknown profiling stage")
        try:
            self.synchronize()
            started = self.clock()
            yield
            self.synchronize()
            duration = (self.clock() - started) / 1e6
            if not math.isfinite(duration) or duration < 0:
                raise DataContractError("Invalid monotonic timing")
        except BaseException:
            self._failed[stage] += 1
            raise
        self._values[stage].append(duration)
        self._count[stage] += 1
        self._total[stage] += duration
        self._max[stage] = max(self._max[stage], duration)

    def snapshot(self) -> dict[str, Any]:
        rows = {}
        for stage, values in self._values.items():
            ordered = sorted(values)
            count = self._count[stage]
            rows[stage] = {
                "completed": count, "failed": self._failed[stage],
                "mean_ms": self._total[stage] / count if count else None,
                "max_ms": self._max[stage] if count else None,
                "window_count": len(values),
                "window_p50_ms": ordered[math.ceil(.50 * len(values)) - 1] if values else None,
                "window_p95_ms": ordered[math.ceil(.95 * len(values)) - 1] if values else None,
            }
        return {"window_capacity": self.capacity, "percentile_method": "nearest_rank",
                "stages": rows}
