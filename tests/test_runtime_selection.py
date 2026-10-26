import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ML_AVAILABLE = all(importlib.util.find_spec(n) for n in ("torch", "torchvision"))
if ML_AVAILABLE:
    import yaml

    from ai_exam_monitoring.common.errors import ConfigurationError, DataContractError
    from ai_exam_monitoring.common.provenance import sha256_file
    from ai_exam_monitoring.inference.runtime_config import load_runtime_config
    from ai_exam_monitoring.inference.selected_crop_review import normalize_comparison
    from ai_exam_monitoring.training.artifacts import digest_json


@unittest.skipUnless(ML_AVAILABLE, "Install classifier dependencies")
class RuntimeSelectionTests(unittest.TestCase):
    def test_v4_pins_winner_and_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def write(name, obj):
                p = root / name
                p.write_text(json.dumps(obj), encoding="utf-8")
                return {"path": name, "sha256": sha256_file(p)}

            dummy = write("dummy.json", {})
            policy = dict(
                imgsz=640,
                conf=0.25,
                iou=0.3,
                max_det=100,
                device="cpu",
                half=False,
                rect=True,
                augment=False,
                batch=1,
            )
            selection = dict(
                status="accepted",
                winner="V8S",
                detector=policy,
                detector_weights=dummy,
                decision_ref=dummy,
                evidence={"review": dummy},
            )
            raw = dict(
                schema_version="recorded-runtime-config-v4",
                runtime_id="test",
                approval_ref="approval.json",
                pins={
                    k: dummy
                    for k in [
                        "checkpoint",
                        "resolved_config",
                        "calibration",
                        "bundle",
                        "run",
                        "detector_weights",
                        "detector_receipt",
                    ]
                },
                detector=policy,
                crop=dict(version="context-v1", left=0.2, right=0.2, top=0.1, bottom=0.2),
                classifier=dict(
                    device="cpu",
                    batch_size=1,
                    threads=4,
                    precision="float32",
                    target_order=["phone_use", "looking_around"],
                ),
                gallery_frames=20,
                sampling_hz=1,
            )

            def config():
                raw["pins"]["detector_selection"] = write("selection.json", selection)
                (root / "runtime.yaml").write_text(yaml.safe_dump(raw), encoding="utf-8")
                write(
                    "approval.json",
                    dict(status="approved", runtime_id="test", config_sha256=digest_json(raw)),
                )

            config()
            self.assertEqual(
                load_runtime_config(root / "runtime.yaml", root).raw["runtime_id"], "test"
            )
            selection["winner"] = "D2"
            config()
            with self.assertRaises(ConfigurationError):
                load_runtime_config(root / "runtime.yaml", root)
            selection["winner"] = "V8S"
            raw["detector"] = {**policy, "iou": 0.7}
            config()
            with self.assertRaises(ConfigurationError):
                load_runtime_config(root / "runtime.yaml", root)

    def test_comparison_source_anchor_and_time_normalization(self):
        source = {"path": "source.png", "sha256": "abc"}
        cohort = {"frames": [{"frame_index": 3, "source_png": source, "video_time_ms": 100.0}]}
        box = dict(
            anchor_id="f00000003-V8S-b000",
            xyxy_float=[1.0, 2.0, 3.0, 4.0],
            person_box=[1, 2, 3, 4],
            context_box=[0, 1, 4, 5],
            confidence=0.8,
        )
        rows = [dict(arm="V8S", frame_index=3, source=source, boxes=[box])]
        normalized = normalize_comparison(rows, cohort, "V8S")
        self.assertEqual(normalized[0]["video_time_ms"], 100.0)
        self.assertEqual(normalized[0]["boxes"][0]["detector_confidence"], 0.8)
        rows[0]["source"] = {"path": "other"}
        with self.assertRaises(DataContractError):
            normalize_comparison(rows, cohort, "V8S")
        rows[0]["source"] = source
        box["anchor_id"] = "f00000003-D2-b000"
        with self.assertRaises(DataContractError):
            normalize_comparison(rows, cohort, "V8S")
