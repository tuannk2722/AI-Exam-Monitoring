"""Run an approved local linear probe. Never evaluates the frozen test split."""

from __future__ import annotations

import argparse
import copy
import json
import random
import time
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from torch import nn

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file

from .artifacts import (
    RunRecord,
    checksum_artifacts,
    code_identity,
    digest_json,
    environment,
    now,
    save_checkpoint,
    write_json,
)
from .config import ExperimentConfig, load_config, verify_approval
from .data import select_records, verify_dataset
from .metrics import evaluate_scores, masked_loss
from .model import FrozenEncoder, SplitFeatures, extract_features


@dataclass(frozen=True)
class PredictionRow:
    sample_id: str
    source_id: str
    group_id: str
    split: str
    scores: list[float]
    targets: list[int | None]
    mask: list[int]
    decisions: list[bool]


def rng_state() -> dict[str, Any]:
    state = cast(tuple[Any, ...], np.random.get_state(legacy=True))
    return {"torch": torch.get_rng_state(), "python": random.getstate(),
            "numpy": [state[0], state[1].tolist(), int(state[2]), int(state[3]), float(state[4])]}


def restore_rng(state: dict[str, Any]) -> None:
    torch.set_rng_state(state["torch"])
    random.setstate(state["python"])
    name, keys, position, gaussian, cached = state["numpy"]
    np.random.set_state((name, np.array(keys, dtype=np.uint32), position, gaussian, cached))


def train_head(train: SplitFeatures, val: SplitFeatures, config: ExperimentConfig,
               output: Path, identity: str, *, resume: bool = False,
               interrupt_after: int | None = None) -> dict[str, Any]:
    torch.manual_seed(config.seed)
    head = nn.Linear(train.features.shape[1], 2)
    optimizer = torch.optim.AdamW(head.parameters(), lr=config.learning_rate,
                                 weight_decay=config.weight_decay)
    start, best_loss, early_reference, stale = 0, float("inf"), float("inf"), 0
    best_head, best_epoch, history = None, 0, []
    if resume:
        state = torch.load(output / "last.pt", map_location="cpu", weights_only=True)
        if state["identity"] != identity:
            raise DataContractError("Resume config/code/data/features differ")
        head.load_state_dict(state["head"])
        optimizer.load_state_dict(state["optimizer"])
        restore_rng(state["rng"])
        start, best_loss = state["epoch"], state["best_loss"]
        early_reference, stale = state["early_reference"], state["stale"]
        best_head, best_epoch, history = state["best_head"], state["best_epoch"], state["history"]
    for epoch in range(start + 1, config.max_epochs + 1):
        if stale >= config.patience:
            break
        head.train()
        optimizer.zero_grad(set_to_none=True)
        loss = masked_loss(head(train.features), train.values, train.mask)
        if not torch.isfinite(loss):
            raise DataContractError("Nonfinite training loss")
        torch.autograd.backward(loss)
        if any(p.grad is None or not torch.isfinite(p.grad).all() for p in head.parameters()):
            raise DataContractError("Nonfinite or missing head gradient")
        optimizer.step()
        head.eval()
        with torch.no_grad():
            train_loss = float(masked_loss(head(train.features), train.values, train.mask))
            val_loss = float(masked_loss(head(val.features), val.values, val.mask))
        if val_loss < best_loss:
            best_loss, best_epoch = val_loss, epoch
            best_head = copy.deepcopy(head.state_dict())
        if val_loss < early_reference - config.min_delta:
            early_reference, stale = val_loss, 0
        else:
            stale += 1
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss})
        state = {"identity": identity, "head": head.state_dict(),
                 "optimizer": optimizer.state_dict(), "rng": rng_state(), "epoch": epoch,
                 "best_head": best_head, "best_epoch": best_epoch, "best_loss": best_loss,
                 "early_reference": early_reference, "stale": stale, "history": history}
        save_checkpoint(output / "last.pt", state)
        write_json(output / "history.json", history)
        if interrupt_after is not None and epoch == interrupt_after:
            raise KeyboardInterrupt("Requested checkpoint interruption")
    if best_head is None:
        raise DataContractError("No completed optimizer update")
    save_checkpoint(output / "best.pt", {"head": best_head, "identity": identity,
                                         "epoch": best_epoch, "val_loss": best_loss,
                                         "config": config.to_dict()})
    head.load_state_dict(best_head)
    return {"head": head, "best_epoch": best_epoch, "epochs": len(history),
            "history": history, "early_stopped": stale >= config.patience}


def split_report(data: SplitFeatures, head: nn.Module, config: ExperimentConfig,
                 prevalence: torch.Tensor) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with torch.no_grad():
        logits = head(data.features)
        scores = logits.sigmoid()
    metrics = evaluate_scores(scores, data.values, data.mask, config.threshold)
    metrics["macro_masked_bce"] = float(masked_loss(logits, data.values, data.mask))
    metrics["constant_train_prevalence"] = evaluate_scores(
        prevalence.expand_as(scores), data.values, data.mask, config.threshold)
    rows = []
    for row, score in zip(data.records, scores.tolist(), strict=True):
        if row.group is None or row.group.leakage_group_id is None:
            raise DataContractError("Prediction record requires reviewed leakage group")
        rows.append(asdict(PredictionRow(
            row.sample_id, row.source.source_id, row.group.leakage_group_id, row.usage,
            score, list(row.target_values), list(row.target_mask),
            [s >= config.threshold for s in score])))
    metrics["by_source"] = {}
    for source in sorted({r.source.source_id for r in data.records}):
        indices = [i for i, r in enumerate(data.records) if r.source.source_id == source]
        metrics["by_source"][source] = evaluate_scores(
            scores[indices], data.values[indices], data.mask[indices], config.threshold)
    return metrics, rows


def write_curve(output: Path, history: list[dict[str, Any]]) -> None:
    # Standalone SVG, no chart dependency or media upload.
    maximum = max(r[k] for r in history for k in ("train_loss", "val_loss")) * 1.05
    curves = []
    for key, color in (("train_loss", "#2166ac"), ("val_loss", "#b2182b")):
        points = " ".join(f"{50 + i * 680 / max(1, len(history)-1):.2f},"
                          f"{340 - r[key] * 280 / maximum:.2f}"
                          for i, r in enumerate(history))
        curves.append(f'<polyline fill="none" stroke="{color}" points="{points}"/>')
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400">'
           '<rect width="800" height="400" fill="white"/>'
           '<g font-family="sans-serif" font-size="14">'
           '<text x="50" y="25">Macro masked BCE by epoch</text>'
           '<text x="50" y="380">Epoch 1</text>'
           f'<text x="650" y="380">Epoch {len(history)}</text>'
           f'<text x="5" y="65">{maximum:.2f}</text><text x="20" y="340">0</text>'
           '<text x="400" y="25" fill="#2166ac">Train</text>'
           '<text x="510" y="25" fill="#b2182b">Validation</text></g>'
           '<path d="M50 55V340H740" fill="none" stroke="black"/>'
           + ''.join(curves) + '</svg>')
    (output / "learning-curve.svg").write_text(svg, encoding="utf-8")


def peak_rss() -> int | None:
    try:
        psutil = import_module("psutil")

        memory = psutil.Process().memory_info()
        return int(getattr(memory, "peak_wset", memory.rss))
    except ImportError:
        return None


def run(config_path: Path, output: Path, workspace: Path, *, resume: bool = False,
        interrupt_after: int | None = None) -> RunRecord:
    from ai_exam_monitoring.common.config import load_yaml

    if load_yaml(config_path).get("schema_version") in {
        "matched-adaptation-v1",
        "matched-adaptation-v2",
        "matched-adaptation-v3",
        "representation-adaptation-v4",
    }:
        from .adaptation_train import run_adaptation

        return run_adaptation(config_path, output, workspace, resume=resume,
                              interrupt_after=interrupt_after)

    config = load_config(config_path)
    output, workspace = output.resolve(), workspace.resolve()
    verify_approval(config, workspace)
    if not (output.is_relative_to(workspace / "outputs")
            or output.is_relative_to(workspace / "artifacts" / "models")):
        raise DataContractError("Run output must be under workspace outputs/ or artifacts/models/")
    if not resume:
        output.mkdir(parents=True, exist_ok=False)
    elif not (output / "last.pt").is_file():
        raise DataContractError("Resume requires a complete last checkpoint")
    torch.set_num_threads(config.threads)
    torch.use_deterministic_algorithms(True)
    random.seed(config.seed)
    np.random.seed(config.seed)
    torch.manual_seed(config.seed)
    code, env = code_identity(), environment()
    config_hash = digest_json(config.to_dict())
    if resume:
        record = RunRecord(**json.loads((output / "run.json").read_text(encoding="utf-8")))
        if (record.status not in {"INTERRUPTED", "FAILED", "OOM"}
                or record.config_sha256 != config_hash or record.code_sha256 != code["sha256"]
                or record.environment["packages"] != env["packages"]):
            raise DataContractError("Resume status/config/code/environment differs")
        checksums = json.loads((output / "checksums.json").read_text(encoding="utf-8"))
        for name in ("last.pt", "resolved-config.json", "code-provenance.json"):
            if sha256_file(output / name) != checksums.get(name):
                raise DataContractError("Resume artifact checksum changed")
        record.status, record.error = "RUNNING", None
        record.ended_at = None
        record.resumed_at.append(now())
    else:
        record = RunRecord(config.experiment_id, config.owner, config.hypothesis, config_hash,
                           code["sha256"], env, config.dataset_version, config.split_version,
                           config.encoding_version, config.payload_sha256, config.weights_sha256)
        write_json(output / "resolved-config.json", config.to_dict())
        write_json(output / "code-provenance.json", code)
    record.write(output)
    started = time.perf_counter()
    try:
        root = workspace / config.dataset
        records = verify_dataset(root, config)
        encoder = FrozenEncoder(workspace / config.weights, config.weights_sha256)
        train = extract_features(encoder, root, select_records(records, "train"), config,
                                 output / "features-train.pt")
        val = extract_features(encoder, root, select_records(records, "val"), config,
                               output / "features-val.pt")
        identity = digest_json({"config": config_hash, "code": code["sha256"],
                                "train": train.fingerprint, "val": val.fingerprint})
        result = train_head(train, val, config, output, identity, resume=resume,
                            interrupt_after=interrupt_after)
        prevalence = (train.values * train.mask).sum(0) / train.mask.sum(0)
        metrics = {}
        for split, features in (("train", train), ("val", val)):
            metrics[split], predictions = split_report(features, result["head"], config, prevalence)
            write_json(output / f"predictions-{split}.json", predictions)
        write_json(output / "metrics.json", metrics)
        write_curve(output, result["history"])
        record.best_epoch, record.completed_epochs = result["best_epoch"], result["epochs"]
        record.status, record.decision = "FINISHED", "continue_research_only"
        record.observation = (
            "Frozen-feature pilot completed; source-confounded, tiny validation support. "
            "No generalization/promotion claim. Test not evaluated. "
            f"Early stopping: {result['early_stopped']}.")
    except BaseException as error:
        record.status = "INTERRUPTED" if isinstance(error, KeyboardInterrupt) else "FAILED"
        if isinstance(error, MemoryError) or "out of memory" in str(error).lower():
            record.status = "OOM"
        record.error = f"{type(error).__name__}: {error}"
        record.observation = "Incomplete run; no automatic config/batch change."
        if (output / "last.pt").is_file():
            state = torch.load(output / "last.pt", map_location="cpu", weights_only=True)
            record.completed_epochs, record.best_epoch = state["epoch"], state["best_epoch"]
        raise
    finally:
        record.ended_at = now()
        record.elapsed_seconds += time.perf_counter() - started
        record.peak_rss_bytes = peak_rss()
        record.write(output)
        checksum_artifacts(output)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--interrupt-after", type=int, help="Checkpoint recovery drill; stops run")
    args = parser.parse_args()
    result = run(args.config, args.output, args.workspace, resume=args.resume,
                 interrupt_after=args.interrupt_after)
    print(f"{result.experiment_id}: {result.status}; best epoch {result.best_epoch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
