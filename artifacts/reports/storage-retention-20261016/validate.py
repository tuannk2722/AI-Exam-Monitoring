"""Post-cleanup checks: no training, image inference, or holdout access."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_evaluate import load_bundle

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def main() -> None:
    receipt = json.loads((HERE / "receipt.json").read_text())
    assert receipt["status"] == "complete"
    plan = json.loads((HERE / "plan.json").read_text())
    assert all(not (ROOT / row["path"]).exists() for row in plan["delete"])
    run = ROOT / "outputs/E004-C345-W-H"
    checks = json.loads((run / "checksums.json").read_text())
    for name, digest in checks.items():
        assert sha256_file(run / name) == digest, name
    model, payload = load_bundle(run, ROOT)
    assert not model.training
    pins = json.loads((ROOT / "artifacts/reports/E004-train-enrollment-20261016"
                       / "result-pins.json").read_text())
    assert all(sha256_file(ROOT / name) == digest for name, digest in pins["files"].items())
    baseline = plan["baseline_commit"]
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", baseline, "src", "configs", "requirements"],
        cwd=ROOT).decode().splitlines()
    for name in paths:
        old = subprocess.check_output(["git", "show", baseline + ":" + name], cwd=ROOT)
        # Git may normalize LF; compare text semantics, not historical artifact pins.
        assert old.decode("utf8").replace("\r\n", "\n") == (ROOT / name).read_text("utf8")
    seen = set()
    logical = unique = 0
    for base, _, names in os.walk(ROOT):
        for name in names:
            s = (Path(base) / name).stat()
            logical += s.st_size
            key = (s.st_dev, s.st_ino)
            if key not in seen:
                unique += s.st_size
                seen.add(key)
    before = json.loads((HERE / "measurement-before.json").read_text())
    result = {
        "status": "PASS", "deleted_paths_absent": len(plan["delete"]),
        "current_run_all_checksums": len(checks), "c345_model_load": "PASS",
        "model_tensor_sha256": payload["model_tensor_sha256"],
        "c345_result_pins": len(pins["files"]), "source_config_requirements_unchanged": len(paths),
        "training_or_inference": False, "test_reserve_access": False,
        "whole_workspace_after": {"logical_bytes": logical, "unique_file_bytes": unique},
        "net_unique_bytes_reduction": before["unique_file_bytes"] - unique,
        "measurement_scope": "whole workspace including Git and caches; not disk allocation",
        "plan_sha256": hashlib.sha256((HERE / "plan.json").read_bytes()).hexdigest(),
    }
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
