from __future__ import annotations

import importlib.util
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import yaml

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.inference.frame_processor import Anchor
from ai_exam_monitoring.inference.live_events import LiveCandidates, TrackedScores
from ai_exam_monitoring.inference.live_timing import (
    LiveTimingPolicy,
    SelectedSlot,
    SlotSelector,
    TrackingContinuity,
    TrackingToken,
)
from ai_exam_monitoring.inference.streaming import FrameStamp

POLICY = Path("configs/tracking/LIVE-TIMING-20261028/policy.yaml")


def stamp(index, time_ms, epoch=0):
    return FrameStamp("fixture", epoch, index, time_ms, index + 1, 100, 100)


def token(slot, offset=0, generation=0, epoch=0):
    return TrackingToken(SelectedSlot(stamp(slot, slot * 100. + offset, epoch), slot, slot * 100.),
                         generation, False, 0, slot % 10 == 0)


def observation(index, identity=1, scores=(.8, .7)):
    return TrackedScores(Anchor(f"f{index}-a{identity}", (1, 1, 10, 10), (0, 0, 11, 11), .9),
                         identity, scores)


class TimingTests(unittest.TestCase):
    def setUp(self):
        self.policy = LiveTimingPolicy.load(POLICY)

    def selector(self):
        return SlotSelector(self.policy, "fixture", 0, origin_ms=0.)

    def test_first_at_or_after_boundary_tolerance_and_late_slot(self):
        selector = self.selector()
        self.assertEqual(selector.offer(stamp(0, 0.)).index, 0)
        self.assertIsNone(selector.offer(stamp(1, 33.)))
        self.assertEqual(selector.offer(stamp(2, 150.)).index, 1)
        self.assertIsNone(selector.offer(stamp(3, 250.001)))
        selected = selector.offer(stamp(4, 300.))
        self.assertEqual(selected.stamp.source_time_ms, 300.)
        self.assertEqual(selector.missing, 1)
        self.assertEqual(selector.selected, 3)

    def test_25_and_30_fps_keep_real_timestamps_and_no_duplicate_frame(self):
        for fps in (25, 30):
            selector = self.selector()
            selected = [s for i in range(fps * 3)
                        if (s := selector.offer(stamp(i, i * 1000. / fps))) is not None]
            self.assertEqual(len(selected), 30)
            self.assertEqual(selector.missing, 0)
            self.assertEqual(len({s.stamp.sequence for s in selected}), 30)
            for s in selected:
                self.assertEqual(s.stamp.source_time_ms, s.stamp.sequence * 1000. / fps)
                self.assertTrue(0 <= s.stamp.source_time_ms - s.due_ms <= 50)

    def test_large_jump_is_counted_without_queue_and_wrong_identity_rejected(self):
        selector = self.selector()
        first = stamp(0, 0.)
        selector.offer(first)
        with self.assertRaises(DataContractError):
            selector.offer(first)
        selector.offer(stamp(1, 10_000_000.))
        self.assertEqual(selector.missing, 99_999)
        for bad in (stamp(2, 10_000_100., epoch=1),
                    replace(stamp(2, 10_000_100.), width=101)):
            with self.assertRaises(DataContractError):
                selector.offer(bad)

    def test_processed_slot_gap_resets_even_when_capture_selected_every_slot(self):
        selector = self.selector()
        slots = [selector.offer(stamp(i, i * 100.)) for i in range(4)]
        continuity = TrackingContinuity(self.policy, "fixture", 0)
        first = continuity.accept(slots[0])
        self.assertTrue(first.reset_required)
        self.assertTrue(first.classifier_due)
        second = continuity.accept(slots[1])
        self.assertFalse(second.reset_required)
        after_drop = continuity.accept(slots[3])
        self.assertEqual(after_drop.missing_detector_slots, 1)
        self.assertTrue(after_drop.reset_required)
        self.assertGreater(after_drop.generation, first.generation)
        continuity.reset()
        self.assertGreater(continuity.generation, after_drop.generation)
        with self.assertRaises(DataContractError):
            continuity.accept(slots[3])

    def test_unapproved_numeric_or_status_change_rejected(self):
        raw = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "policy.yaml"
            for key, value in (("frame_tolerance_ms", 51), ("status", "draft"),
                               ("classifier_stride", True), ("propagate_behavior_labels", True)):
                path.write_text(yaml.safe_dump({**raw, key: value}))
                with self.assertRaises(DataContractError):
                    LiveTimingPolicy.load(path)


class LiveEventTests(unittest.TestCase):
    def setUp(self):
        self.policy = LiveTimingPolicy.load(POLICY)
        self.events = LiveCandidates(self.policy, "fixture", [.5, .4], epoch=0, generation=0)

    def consume(self, index, **kwargs):
        return self.events.consume(token(index, **kwargs), [observation(index)])

    def test_three_positive_span_and_stable_id_then_close(self):
        self.assertEqual(self.consume(0), [])
        self.assertEqual(self.consume(10), [])
        opened = self.consume(20)
        self.assertEqual(len(opened), 2)
        updated = self.consume(30)
        self.assertEqual([u.event_id for u in updated], [u.event_id for u in opened])
        self.assertTrue(all(u.support_count == 4 for u in updated))
        closed = self.events.close("eof")
        self.assertEqual([u.event_id for u in closed], [u.event_id for u in opened])
        self.assertTrue(all(u.lifecycle == "closed" for u in closed))

    def test_jitter_does_not_fake_two_second_span(self):
        self.consume(0, offset=50)
        self.consume(10)
        self.assertEqual(self.consume(20), [])
        updates = self.consume(30)
        self.assertEqual(updates[0].first.stamp.source_time_ms, 50.)
        self.assertEqual(updates[0].support_count, 4)

    def test_missing_unknown_negative_null_and_id_change_break_support(self):
        for middle in ([], [observation(20, scores=(None, None))],
                       [observation(20, scores=(.1, .1))], [observation(20, identity=None)],
                       [observation(20, identity=2)]):
            self.setUp()
            self.consume(0)
            self.consume(10)
            self.assertEqual(self.events.consume(token(20), middle), [])
            self.assertEqual(self.consume(30), [])
            self.assertEqual(self.consume(40), [])
        self.setUp()
        self.consume(0)
        self.consume(10)
        self.assertEqual(self.consume(30), [])
        self.assertEqual(self.consume(40), [])

    def test_generation_epoch_and_declared_missing_reject_late_results(self):
        self.consume(0)
        self.consume(10)
        self.consume(20)
        closed = self.events.advance(epoch=0, generation=1, reason="pause")
        self.assertEqual(len(closed), 2)
        self.assertEqual(self.consume(30), [])
        self.assertEqual(self.events.stale_results, 1)
        self.assertEqual(self.consume(30, generation=1), [])
        self.events.mark_missing(40)
        self.assertEqual(self.consume(40, generation=1), [])
        self.assertEqual(self.consume(50, generation=1), [])
        self.events.advance(epoch=1, generation=0, reason="seek")
        self.assertEqual(self.consume(0, epoch=1), [])
        self.assertEqual(self.consume(60, generation=1), [])

    def test_duplicate_mapping_bad_geometry_and_scores_do_not_mutate_state(self):
        for rows in ([observation(0), observation(0)],
                     [replace(observation(0), scores=(float("nan"), .4))],
                     [replace(observation(0), anchor=Anchor("bad", (0, 0, 200, 200),
                                                             (0, 0, 200, 200), .9))]):
            with self.assertRaises(DataContractError):
                self.events.consume(token(0), rows)
            self.assertEqual(self.events.last_slot, -1)
            self.assertEqual(self.events.active, {})

    def test_14_people_ten_minutes_has_bounded_support_and_no_event_queue(self):
        for second in range(600):
            rows = [observation(second, identity=person) for person in range(1, 15)]
            updates = self.events.consume(token(second * 10), rows)
            self.assertLessEqual(len(updates), 28)
            self.assertLessEqual(len(self.events.active), 28)
        self.assertTrue(all(len(s.initial) == 3 and s.count == 600
                            for s in self.events.active.values()))

    @unittest.skipUnless(importlib.util.find_spec("torch"), "Offline event module needs Torch")
    def test_exact_grid_parity_with_offline_events(self):
        from ai_exam_monitoring.inference.events import aggregate

        rule = yaml.safe_load(Path("configs/events/EVENTS-PROTOTYPE-20261027/approved-rule.yaml")
                              .read_text(encoding="utf-8"))
        frames, projected, final = [], [], []
        for index, score in enumerate([.7, .8, .9, .1, .6, .7, .8, .9]):
            slot = index * 10
            obs = observation(slot, scores=(score, .8))
            final.extend(u for u in self.events.consume(token(slot), [obs])
                         if u.lifecycle == "closed")
            row = dict(anchor_id=obs.anchor.anchor_id, person_box=list(obs.anchor.person_box),
                       scores=[score, .8], above_threshold=[score >= .5, True])
            frames.append(dict(frame_index=slot, video_time_ms=index * 1000, observations=[row]))
            projected.append(dict(arm_id="C10", frame_index=slot, video_time_ms=index * 1000,
                                  assignments=[dict(anchor_id=row["anchor_id"],
                                                    person_box=row["person_box"], track_id=1)]))
        final.extend(self.events.close("eof"))
        meta = dict(target_order=["phone_use", "looking_around"], thresholds=[.5, .4])
        offline, _ = aggregate(frames, projected, meta, rule, "fixture", "model")
        def normalize(rows):
            return sorted(rows, key=lambda r: (r[0], r[1]))
        self.assertEqual(normalize([(u.behavior, u.first.stamp.source_time_ms,
                                     u.latest.stamp.source_time_ms, u.support_count,
                                     round(u.mean_score, 8)) for u in final]),
                         normalize([(r["event"]["behavior"], r["event"]["start_time_ms"],
                                     r["event"]["end_time_ms"], r["support_count"],
                                     round(r["event"]["aggregated_confidence"], 8))
                                    for r in offline]))
