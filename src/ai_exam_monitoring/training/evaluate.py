"""Explicit evaluation of one frozen artifact; test requires a hash-bound protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from torch import nn

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .artifacts import checksum_artifacts, code_identity, digest_json, now, write_json
from .config import ExperimentConfig, verify_approval
from .data import labels, select_records, verify_dataset
from .model import FrozenEncoder, extract_features
from .train import split_report


def validate_protocol(protocol: dict[str, Any], config: ExperimentConfig, checkpoint: Path,
                      config_hash: str, code_hash: str) -> None:
    expected = {"status": "approved", "experiment_id": config.experiment_id,
                "checkpoint_sha256": sha256_file(checkpoint), "config_sha256": config_hash,
                "code_sha256": code_hash, "payload_sha256": config.payload_sha256,
                "threshold": config.threshold, "split": "test", "candidate_count": 1}
    if any(protocol.get(k) != v for k, v in expected.items()):
        raise DataContractError("Final test protocol does not pin this candidate/config/data")
    if not protocol.get("owner") or not protocol.get("decision_ref"):
        raise DataContractError("Final evaluation requires owner/protocol decision reference")


def evaluate(run_dir: Path, output: Path, workspace: Path, split: str,
             protocol_path: Path | None = None, *, benchmark: bool = False) -> dict[str, Any]:
    raw_config = json.loads((run_dir / "resolved-config.json").read_text(encoding="utf-8"))
    if raw_config.get("schema_version") in {
        "matched-adaptation-v1", "matched-adaptation-v2", "matched-adaptation-v3",
        "representation-adaptation-v4",
        "spatial-representation-v5",
    }:
        from .adaptation_evaluate import evaluate_adaptation

        return evaluate_adaptation(run_dir, output, workspace, split, protocol_path,
                                   run_benchmark=benchmark)
    if benchmark:
        raise DataContractError("Benchmark flag requires matched adaptation schema")
    config = ExperimentConfig(**json.loads((run_dir / "resolved-config.json").read_text()))
    verify_approval(config, workspace)
    record = json.loads((run_dir / "run.json").read_text())
    code_hash, config_hash = code_identity()["sha256"], digest_json(config.to_dict())
    if (record["status"] != "FINISHED" or code_hash != record["code_sha256"]
            or config_hash != record["config_sha256"]):
        raise DataContractError("Evaluation requires finished run with identical code/config")
    checksums = json.loads((run_dir / "checksums.json").read_text())
    for name, checksum in checksums.items():
        path = (run_dir / name).resolve()
        if not path.is_relative_to(run_dir.resolve()) or sha256_file(path) != checksum:
            raise DataContractError("Training artifacts changed")
    checkpoint = run_dir / "best.pt"
    protocol = None
    if split == "test":
        if protocol_path is None:
            raise DataContractError("Test requires a separately frozen final protocol")
        protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
        validate_protocol(protocol, config, checkpoint, config_hash, code_hash)
    elif split != "val":
        raise DataContractError("Evaluator supports val or explicitly authorized test")
    output = output.resolve()
    if not output.is_relative_to(workspace.resolve() / "outputs"):
        raise DataContractError("Evaluation output must be under workspace outputs/")
    output.mkdir(parents=True, exist_ok=False)
    torch.set_num_threads(config.threads)
    torch.use_deterministic_algorithms(True)
    root = workspace / config.dataset
    records = verify_dataset(root, config)
    selected = select_records(records, split, final_test=split == "test")
    encoder = FrozenEncoder(workspace / config.weights, config.weights_sha256)
    features = extract_features(encoder, root, selected, config, output / f"features-{split}.pt")
    head = nn.Linear(512, 2)
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if state["config"] != config.to_dict():
        raise DataContractError("Checkpoint config mismatch")
    head.load_state_dict(state["head"])
    head.eval()
    values, mask = labels(select_records(records, "train"))
    prevalence = (values * mask).sum(0) / mask.sum(0)
    metrics, predictions = split_report(features, head, config, prevalence)
    write_json(output / "metrics.json", metrics)
    write_json(output / "predictions.json", predictions)
    write_json(output / "evaluation.json", {"evaluated_at": now(), "split": split,
               "checkpoint_sha256": sha256_file(checkpoint), "best_epoch": state["epoch"],
               "protocol": protocol, "config_sha256": config_hash, "code_sha256": code_hash,
               "payload_sha256": config.payload_sha256, "status": "FINISHED"})
    checksum_artifacts(output)
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--split", choices=["val", "test"], default="val")
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.run, args.output, args.workspace, args.split, args.protocol,
                              benchmark=args.benchmark),
                     indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
