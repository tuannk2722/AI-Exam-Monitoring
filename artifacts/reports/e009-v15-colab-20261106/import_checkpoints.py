"""Import the three requested E009 run ZIPs and audit tensors without inference."""

from __future__ import annotations

import gc
import hashlib
import json
import math
import os
import platform
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

import torch

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_schema import read_records
from ai_exam_monitoring.training.adaptation_config import config_from_dict
from ai_exam_monitoring.training.adaptation_model import AdaptationModel, tensor_digest
from ai_exam_monitoring.training.adaptation_train import runtime_signature
from ai_exam_monitoring.training.artifacts import code_identity, digest_json

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
OUTPUT = ROOT / "outputs/E009-V15-Colab-20261106"
SOURCES = {
    "E009-V15-B0-S20261106": "E009-V15-B0-S20261106-20261107T030642Z-1-001.zip",
    "E009-V15-B448-S20261110": "E009-V15-B448-S20261110-20261107T030621Z-1-001.zip",
    "E009-V15-C0-S20261107": "E009-V15-C0-S20261107-20261107T030609Z-1-001.zip",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def finite_tree(value):
    if isinstance(value, torch.Tensor):
        assert value.device.type == "cpu" and torch.isfinite(value).all()
    elif isinstance(value, dict):
        for child in value.values():
            finite_tree(child)
    elif isinstance(value, (tuple, list)):
        for child in value:
            finite_tree(child)
    elif isinstance(value, float):
        assert math.isfinite(value)


def verify_tensor_payload(folder, records, original_code):
    run, config, bundle, initialization, calibration, history = [
        load_json(folder / (n + ".json"))
        for n in ("run", "resolved-config", "bundle", "initialization", "calibration", "history")
    ]
    assert run["code_sha256"] == original_code["sha256"]
    assert load_json(folder / "code-provenance.json") == original_code
    identity = digest_json(
        {
            "config": config,
            "code": run["code_sha256"],
            "runtime": runtime_signature(run["environment"]),
        }
    )
    assert bundle["identity"] == identity
    best = torch.load(folder / "best.pt", map_location="cpu", weights_only=True, mmap=True)
    last = torch.load(folder / "last.pt", map_location="cpu", weights_only=True, mmap=True)
    assert best["schema_version"] == "full-model-bundle-v1"
    assert last["schema_version"] == "full-model-epoch-v1"
    assert best["identity"] == last["identity"] == identity
    assert best["config"] == last["config"] == config
    assert digest_json(config) == run["config_sha256"]
    assert best["epoch"] == last["best_epoch"] == run["best_epoch"]
    assert last["epoch"] == run["completed_epochs"] == len(history)
    assert last["history"] == history
    selected = min(history, key=lambda h: (-h["val_macro_ap"], h["val_loss"], h["epoch"]))
    assert selected["epoch"] == best["epoch"]
    assert best["val_loss"] == last["best_loss"] == selected["val_loss"]
    assert best["best_val_macro_ap"] == last["best_val_macro_ap"] == selected["val_macro_ap"]
    assert best["selection_metric"] == last["selection_metric"] == "val_macro_ap"
    finite_tree(best)
    finite_tree(last)
    assert tensor_digest(best["model"]) == best["model_tensor_sha256"]
    assert tensor_digest(last["best_model"]) == best["model_tensor_sha256"]
    assert all(torch.equal(v, last["best_model"][k]) for k, v in best["model"].items())
    assert best["model"].keys() == last["model"].keys() == last["best_model"].keys()
    assert all(v.dtype == torch.float32 for v in best["model"].values())
    train = sorted((r for r in records if r.usage == "train"), key=lambda r: r.sample_id)
    ids = [r.sample_id for r in train]
    assert len(ids) == 1377
    values = torch.tensor([[v or 0 for v in r.target_values] for r in train], dtype=torch.float32)
    mask = torch.tensor([r.target_mask for r in train], dtype=torch.bool)
    assert torch.equal(best["train_prevalence"], (values * mask).sum(0) / mask.sum(0))
    permutation = last["sampler_permutation"]
    assert sorted(permutation) == list(range(len(ids)))
    assert last["sampler_cursor"] == len(ids)
    assert digest_json([ids[i] for i in permutation]) == history[-1]["permutation_sha256"]
    batches = math.ceil(len(ids) / config["batch_size"])
    assert last["global_step"] == last["epoch"] * batches
    assert last["resume_semantics"] == "restart_uncommitted_epoch_from_last_atomic_epoch_boundary"
    for name in ("sampler_rng",):
        assert last[name].dtype == torch.uint8 and last[name].ndim == 1
        torch.Generator().set_state(last[name])
    assert last["rng"]["torch"].dtype == torch.uint8
    assert isinstance(last["rng"]["python"], tuple) and len(last["rng"]["numpy"]) == 5
    assert len(last["cuda_rng"]) == 1 and last["cuda_rng"][0].dtype == torch.uint8

    loaded_config = config_from_dict(config)
    # Strict architecture/state loading only. No forward, sample, dataset batch or metric.
    model = AdaptationModel(loaded_config, full_state=best["model"], workspace=ROOT)
    model.load_state_dict(last["model"], strict=True)
    groups, names = model.parameter_groups(loaded_config)
    assert names == last["parameter_groups"] == initialization["parameter_groups"]
    opt_groups = last["optimizer"]["param_groups"]
    assert [g["name"] for g in opt_groups] == [g["name"] for g in groups]
    for group in opt_groups:
        assert group["weight_decay"] == config["weight_decay"]
        assert len(group["params"]) == len(names[group["name"]])
        expected_steps = (
            last["epoch"] if group["name"] == "head" else last["epoch"] - config["warmup_epochs"]
        ) * batches
        for pid, name in zip(group["params"], names[group["name"]], strict=True):
            opt_state = last["optimizer"]["state"][pid]
            assert float(opt_state["step"]) == expected_steps
            for key in ("exp_avg", "exp_avg_sq"):
                assert opt_state[key].shape == last["model"][name].shape
                assert opt_state[key].dtype == last["model"][name].dtype
            assert (opt_state["exp_avg_sq"] >= 0).all()
    model.load_state_dict(best["model"], strict=True)
    strict_parameters = sum(p.numel() for p in model.parameters())
    del model

    pretrained_path = ROOT / config["weights"]["path"]
    assert sha256_file(pretrained_path) == config["weights"]["sha256"]
    pretrained = torch.load(pretrained_path, map_location="cpu", weights_only=True)
    allowed = set(names["layer4"])
    frozen, changed_best, changed_last = [], [], []
    for key, initial in pretrained.items():
        target = "network.backbone." + key
        assert target in best["model"]
        changed = not torch.equal(initial, best["model"][target])
        changed_final = not torch.equal(initial, last["model"][target])
        if target not in allowed:
            assert not changed and not changed_final, target
            frozen.append(target)
        else:
            if changed:
                changed_best.append(target)
            if changed_final:
                changed_last.append(target)
    assert changed_best and changed_last
    row = {
        "status": "PASS",
        "run_id": run["experiment_id"],
        "config_sha256": run["config_sha256"],
        "identity": identity,
        "best_epoch": best["epoch"],
        "completed_epochs": last["epoch"],
        "selection_metric": best["selection_metric"],
        "best_model_tensor_sha256": best["model_tensor_sha256"],
        "last_model_tensor_sha256": tensor_digest(last["model"]),
        "parameters": strict_parameters,
        "model_state_keys": len(best["model"]),
        "frozen_backbone_tensors_unchanged_from_pretrained": len(frozen),
        "trainable_backbone_tensors_changed_best": len(changed_best),
        "trainable_backbone_tensors_changed_last": len(changed_last),
        "optimizer_parameter_states": len(last["optimizer"]["state"]),
        "global_step": last["global_step"],
        "sampler_cursor": last["sampler_cursor"],
        "strict_architecture_load": "PASS",
        "finite_model_and_optimizer": "PASS",
        "best_matches_last_best_model": True,
        "thresholds": calibration["thresholds"],
        "local_model_forward_performed": False,
    }
    del pretrained, best, last
    gc.collect()
    return row


def main():
    torch.set_num_threads(4)
    audit_path = REPORT / "results-audit-20261107.json"
    audit = load_json(audit_path)
    metadata_path = ROOT / audit["source_zip"]["path"]
    assert sha256_file(metadata_path) == audit["source_zip"]["sha256"]
    with zipfile.ZipFile(metadata_path) as metadata:
        manifest = json.loads(metadata.read("mirror-manifest.json"))
        code = code_identity()
        assert code["sha256"] == audit["code_sha256"]
        records = read_records(ROOT / "data/processed/pilot-b/pilot-b-20261106-v15/manifest.jsonl")
        results, total = [], 0
        for ident, filename in SOURCES.items():
            source = Path("C:/Users/OS/Downloads") / filename
            archive_sha = sha256_file(source)
            print("Importing", ident, flush=True)
            folder = OUTPUT / "runs" / ident
            expected = {
                name.removeprefix("runs/"): row
                for name, row in manifest["files"].items()
                if name.startswith("runs/" + ident + "/")
            }
            imported = []
            with zipfile.ZipFile(source) as archive:
                entries = archive.infolist()
                assert len(entries) == len({i.filename for i in entries}) == len(expected) == 16
                assert {i.filename for i in entries} == set(expected)
                for item in entries:
                    relative = PurePosixPath(item.filename)
                    assert not relative.is_absolute() and ".." not in relative.parts
                    assert "\\" not in item.filename and ":" not in item.filename
                    assert not stat.S_ISLNK(item.external_attr >> 16) and not item.is_dir()
                    assert item.file_size == expected[item.filename]["bytes"]
                    target = (OUTPUT / "runs" / item.filename).resolve()
                    assert target.is_relative_to(folder.resolve())
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists():
                        assert sha256_file(target) == expected[item.filename]["sha256"]
                    else:
                        temporary = target.with_name(target.name + ".import-partial")
                        if temporary.exists():
                            raise RuntimeError(
                                "Unreviewed partial import already exists: " + str(temporary)
                            )
                        digest, copied = hashlib.sha256(), 0
                        with archive.open(item) as stream, temporary.open("xb") as output:
                            while block := stream.read(8 * 1024 * 1024):
                                digest.update(block)
                                copied += len(block)
                                output.write(block)
                        assert copied == item.file_size
                        assert digest.hexdigest() == expected[item.filename]["sha256"]
                        os.replace(temporary, target)
                    assert target.stat().st_size == item.file_size
                    assert sha256_file(target) == expected[item.filename]["sha256"]
                    if target.suffix != ".pt":
                        assert target.read_bytes() == metadata.read("runs/" + item.filename)
                    imported.append(
                        {"path": target.relative_to(ROOT).as_posix(), **expected[item.filename]}
                    )
                    total += target.stat().st_size
            assert {p.name for p in folder.iterdir()} == {PurePosixPath(n).name for n in expected}
            checks = load_json(folder / "checksums.json")
            for name, digest in checks.items():
                assert sha256_file(folder / name) == digest
            tensor = verify_tensor_payload(folder, records, code)
            results.append(
                {
                    "source_zip": {
                        "filename": filename,
                        "bytes": source.stat().st_size,
                        "sha256": archive_sha,
                    },
                    "run_id": ident,
                    "files": imported,
                    "tensor_audit": tensor,
                }
            )
            print(
                "PASS",
                ident,
                "best/last",
                tensor["best_epoch"],
                tensor["completed_epochs"],
                "frozen tensors",
                tensor["frozen_backbone_tensors_unchanged_from_pretrained"],
                flush=True,
            )
    receipt = {
        "status": "PASS_CHECKPOINT_IMPORT_AND_STRUCTURE",
        "audit_environment": {
            "python": sys.version,
            "torch": str(torch.__version__),
            "platform": platform.platform(),
            "device": "cpu",
            "threads": torch.get_num_threads(),
            "checkpoint_load": "weights_only=True, map_location=cpu, mmap=True",
        },
        "scope": list(SOURCES),
        "source_metadata": audit["source_zip"],
        "source_metadata_audit": {
            "path": audit_path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(audit_path),
        },
        "files": sum(len(r["files"]) for r in results),
        "bytes": total,
        "best_last_checkpoints_verified": 6,
        "code_sha256": code["sha256"],
        "local_inference_performed": False,
        "training_performed": False,
        "test_opened": False,
        "model_promoted": False,
        "whole_campaign_checkpoint_backup_verified": False,
        "metadata_audit_findings_remain": True,
        "runs": results,
    }
    (REPORT / "checkpoint-import-20261107.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("PASS: imported", receipt["files"], "files;", total, "bytes; six checkpoints", flush=True)


if __name__ == "__main__":
    main()
