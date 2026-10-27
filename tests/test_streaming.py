"""Synthetic frame flow checks, with no camera access or model inference."""

import unittest
from dataclasses import replace
from threading import Event, Thread

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.inference.streaming import (
    FrameStamp,
    LatestFrameBuffer,
    StreamFrame,
    can_overlay,
)


def frame(sequence: int, *, epoch: int = 0) -> StreamFrame[str]:
    return StreamFrame(
        FrameStamp("session", epoch, sequence, sequence * 100.0, sequence + 1, 640, 480),
        f"pixels-{sequence}",
    )


class StreamingTests(unittest.TestCase):
    def test_overload_keeps_newest_and_preserves_inflight_frame(self):
        buffer = LatestFrameBuffer[str]("session")
        buffer.publish(frame(0))
        inflight = buffer.take()
        for i in range(1, 1001):
            buffer.publish(frame(i))
        self.assertEqual(inflight, frame(0))
        self.assertEqual(buffer.take(), frame(1000))
        self.assertIsNone(buffer.take())
        stats = buffer.stats()
        self.assertEqual((stats.accepted, stats.taken, stats.dropped), (1001, 2, 999))
        self.assertFalse(stats.pending)

    def test_reset_discards_pending_and_rejects_late_old_epoch(self):
        buffer = LatestFrameBuffer[str]("session")
        buffer.publish(frame(10))
        buffer.reset(epoch=1)
        self.assertIsNone(buffer.take())
        with self.assertRaises(DataContractError):
            buffer.publish(frame(11))
        with self.assertRaises(DataContractError):
            buffer.reset(epoch=1)
        buffer.publish(frame(0, epoch=1))
        self.assertEqual(buffer.take(), frame(0, epoch=1))
        self.assertEqual(buffer.stats().dropped, 1)

    def test_out_of_order_and_geometry_checks_survive_take(self):
        buffer = LatestFrameBuffer[str]("session")
        buffer.publish(frame(2))
        buffer.take()
        invalid = [
            frame(1).stamp,
            replace(frame(3).stamp, source_time_ms=200.0),
            replace(frame(3).stamp, captured_ns=3),
            replace(frame(3).stamp, width=1280),
            replace(frame(3).stamp, session_id="other"),
        ]
        for stamp in invalid:
            with self.subTest(stamp=stamp), self.assertRaises(DataContractError):
                buffer.publish(StreamFrame(stamp, "invalid"))
        self.assertEqual(buffer.stats().accepted, 1)
        buffer.publish(frame(3))
        self.assertEqual(buffer.take(), frame(3))

    def test_stamp_rejects_invalid_clocks_and_dimensions(self):
        for changes in (
            {"source_time_ms": float("nan")}, {"source_time_ms": float("inf")},
            {"source_time_ms": -1}, {"captured_ns": -1}, {"epoch": -1},
            {"sequence": True}, {"width": 0}, {"height": -1}, {"session_id": " "},
        ):
            with self.subTest(changes=changes), self.assertRaises(DataContractError):
                replace(frame(0).stamp, **changes)

    def test_overlay_never_matches_only_track_or_sequence(self):
        result = frame(5).stamp
        for changes in (
            {"epoch": 1}, {"session_id": "other"}, {"sequence": 6},
            {"width": 1280}, {"source_time_ms": 501.0}, {"captured_ns": 7},
        ):
            with self.subTest(changes=changes):
                self.assertFalse(can_overlay(
                    replace(result, **changes), result, now_ns=10, max_age_ns=10
                ))
        self.assertTrue(can_overlay(result, result, now_ns=10, max_age_ns=4))
        self.assertFalse(can_overlay(result, result, now_ns=11, max_age_ns=4))
        self.assertFalse(can_overlay(result, result, now_ns=5, max_age_ns=4))
        with self.assertRaises(DataContractError):
            can_overlay(result, result, now_ns=10, max_age_ns=-1)

    def test_producer_can_finish_while_consumer_is_busy(self):
        buffer = LatestFrameBuffer[str]("session")
        buffer.publish(frame(0))
        inflight = buffer.take()
        finished = Event()

        def produce():
            for i in range(1, 101):
                buffer.publish(frame(i))
            finished.set()

        producer = Thread(target=produce, daemon=True)
        producer.start()
        self.assertTrue(finished.wait(timeout=5), "Capture blocked on a busy consumer")
        producer.join(timeout=5)
        self.assertEqual(inflight, frame(0))
        self.assertEqual(buffer.take(), frame(100))
        self.assertEqual(buffer.stats().dropped, 99)


if __name__ == "__main__":
    unittest.main()
