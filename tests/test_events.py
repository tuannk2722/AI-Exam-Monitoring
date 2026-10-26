from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

AVAILABLE = importlib.util.find_spec("torch") is not None
if AVAILABLE:
    from ai_exam_monitoring.common.config import load_yaml
    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.inference.events import aggregate, load_event_inputs, run


@unittest.skipUnless(AVAILABLE, "Install classifier dependencies")
class EventTests(unittest.TestCase):
    def setUp(self):
        self.rule = load_yaml(Path("configs/events/EVENTS-PROTOTYPE-20261027/approved-rule.yaml"))
        self.meta = {"target_order": ["phone_use", "looking_around"], "thresholds": [0.5, 0.4]}

    def fixture(self, scores, ids=None, times=None):
        ids = ids or [1] * len(scores)
        times = times or [i * 1000 for i in range(len(scores))]
        frames, rows = [], []
        for i, (score, identity, stamp) in enumerate(zip(scores, ids, times, strict=True)):
            obs = dict(
                anchor_id=f"f{i:08d}-a000",
                person_box=[0, 0, 10, 10],
                scores=[score, 0.8],
                above_threshold=[None if score is None else score >= 0.5, True],
            )
            frames.append(dict(frame_index=i * 30, video_time_ms=stamp, observations=[obs]))
            rows.append(
                dict(
                    arm_id="C10",
                    frame_index=i * 30,
                    video_time_ms=stamp,
                    assignments=[
                        dict(
                            anchor_id=obs["anchor_id"],
                            person_box=obs["person_box"],
                            track_id=identity,
                        )
                    ],
                )
            )
        return frames, rows

    def compute(self, scores, **kwargs):
        frames, rows = self.fixture(scores, **kwargs)
        return aggregate(frames, rows, self.meta, self.rule, "session", "model")

    def test_boundary_eof_two_labels_and_mean(self):
        events, counts = self.compute([0.5, 0.7])
        self.assertEqual(events, [])
        self.assertEqual(counts["behaviors"]["phone_use"]["short_support"], 2)
        events, counts = self.compute([0.5, 0.7, 0.9])
        self.assertEqual(len(events), 2)
        event = events[0]
        self.assertEqual(event["observed_span_ms"], 2000)
        self.assertAlmostEqual(event["event"]["aggregated_confidence"], 0.7)
        self.assertEqual(event["event"]["status"], "candidate")
        self.assertEqual(event["event"]["source_prediction_ids"][0], "session:f00000000-a000")

    def test_negative_breaks_only_its_label(self):
        events, counts = self.compute([0.8, 0.8, 0.1, 0.8, 0.8, 0.8])
        phone = [e for e in events if e["event"]["behavior"] == "phone_use"]
        self.assertEqual(len(phone), 1)
        self.assertEqual(phone[0]["event"]["start_time_ms"], 3000)
        self.assertEqual(counts["behaviors"]["phone_use"]["short_support"], 2)
        self.assertEqual(counts["behaviors"]["looking_around"]["event_support"], 6)

    def test_unknown_null_missing_and_id_change_break(self):
        for options in [
            dict(scores=[0.8, 0.8, None, 0.8, 0.8]),
            dict(scores=[0.8] * 5, ids=[1, 1, None, 1, 1]),
            dict(scores=[0.8] * 4, times=[0, 1000, 3000, 4000]),
            dict(scores=[0.8] * 4, ids=[1, 1, 2, 2]),
        ]:
            with self.subTest(options=options):
                events, _ = self.compute(**options)
                self.assertFalse(any(e["event"]["behavior"] == "phone_use" for e in events))

    def test_absent_track_in_present_frame_breaks(self):
        frames, rows = self.fixture([0.8] * 5)
        frames[2]["observations"] = []
        rows[2]["assignments"] = []
        events, _ = aggregate(frames, rows, self.meta, self.rule, "s", "m")
        self.assertEqual(events, [])

    def test_rejects_invalid_join_and_samples(self):
        for mutation in ["box", "time", "duplicate", "score", "flag", "track"]:
            with self.subTest(mutation=mutation):
                frames, rows = self.fixture([0.8] * 3)
                if mutation == "box":
                    rows[0]["assignments"][0]["person_box"] = [1, 1, 9, 9]
                elif mutation == "time":
                    frames[1]["video_time_ms"] = rows[1]["video_time_ms"] = 1100
                elif mutation == "duplicate":
                    frames[1]["frame_index"] = 0
                elif mutation == "score":
                    frames[0]["observations"][0]["scores"][0] = float("nan")
                elif mutation == "flag":
                    frames[0]["observations"][0]["above_threshold"][0] = False
                else:
                    rows[0]["assignments"][0]["track_id"] = True
                with self.assertRaises(DataContractError):
                    aggregate(frames, rows, self.meta, self.rule, "s", "m")

    def test_duplicate_track_and_anchor_rejected(self):
        for same_anchor in (False, True):
            frames, rows = self.fixture([0.8] * 3)
            obs = copy.deepcopy(frames[0]["observations"][0])
            assignment = copy.deepcopy(rows[0]["assignments"][0])
            if not same_anchor:
                obs["anchor_id"] = assignment["anchor_id"] = "different"
            frames[0]["observations"].append(obs)
            rows[0]["assignments"].append(assignment)
            with self.assertRaises(DataContractError):
                aggregate(frames, rows, self.meta, self.rule, "s", "m")

    def test_accounting_and_inputs_unchanged(self):
        frames, rows = self.fixture([0.8, 0.1, None, 0.8, 0.8, 0.8], ids=[None, 1, 1, 1, 1, 1])
        original = copy.deepcopy((frames, rows))
        _, counts = aggregate(frames, rows, self.meta, self.rule, "s", "m")
        self.assertEqual((frames, rows), original)
        c = counts["behaviors"]["phone_use"]
        self.assertEqual(
            sum(
                c[k]
                for k in [
                    "positive_assigned",
                    "negative_assigned",
                    "unknown_assigned",
                    "null_track",
                ]
            ),
            6,
        )

    def test_scope_and_expiry_precede_input_loading(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "auth.json"
            p.write_text(
                json.dumps(
                    dict(
                        schema_version="events-authorization-v1",
                        status="approved",
                        allowed_actions=["implementation", "synthetic_tests", "cached_replay"],
                        access="repository_owner",
                        upload=False,
                        risk=False,
                        web=False,
                        new_model_forwards=0,
                        cached_replay_runs=1,
                        media_delete_by="2000-01-01T00:00:00+00:00",
                    )
                )
            )
            with self.assertRaises(ConfigurationError):
                load_event_inputs(p, Path(temp))

    def test_success_and_input_mutation_after_aggregation(self):
        for mutate in (False, True):
            with self.subTest(mutate=mutate), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                authpath = root / "auth.json"
                authpath.write_text("{}")
                auth = dict(
                    output="outputs/replay",
                    event_run_id="synthetic",
                    media_delete_by="2099-01-01T00:00:00+00:00",
                    pins={"rule": {"sha256": "rule"}},
                )
                frames, rows = self.fixture([0.8] * 3)
                inputs = dict(
                    metadata={
                        **self.meta,
                        "source_sha256": "source",
                        "pins": {"checkpoint": {"sha256": "model"}},
                    },
                    parent_pins={"session.json": {"sha256": "parent"}},
                )
                values = (auth, self.rule, frames, rows, inputs)
                prefix = "ai_exam_monitoring.inference.events."
                with (
                    patch(
                        prefix + "load_event_inputs",
                        side_effect=[values, ConfigurationError("mutation") if mutate else values],
                    ),
                    patch(prefix + "environment", return_value={}),
                    patch(prefix + "code_identity", return_value={}),
                ):
                    output = root / "outputs/replay"
                    if mutate:
                        with self.assertRaises(ConfigurationError):
                            run(authpath, root, output)
                    else:
                        result = run(authpath, root, output)
                        self.assertEqual(result["event_count"], 2)
                    state = json.loads((output / "session.json").read_text())
                    self.assertEqual(state["status"], "failed" if mutate else "completed")

    def test_failed_outcome_and_replay_path_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            authpath = root / "auth.json"
            authpath.write_text("{}")
            auth = dict(
                output="outputs/replay",
                event_run_id="synthetic",
                media_delete_by="2099-01-01T00:00:00+00:00",
            )
            prefix = "ai_exam_monitoring.inference.events."
            with patch(prefix + "load_event_inputs", return_value=(auth, self.rule, [], [], {})):
                out = root / "outputs/replay"
                with self.assertRaises(KeyError):
                    run(authpath, root, out)
                self.assertEqual(json.loads((out / "session.json").read_text())["status"], "failed")
                self.assertTrue((out / "checksums.json").exists())
                with self.assertRaises(DataContractError):
                    run(authpath, root, out)


if __name__ == "__main__":
    unittest.main()
