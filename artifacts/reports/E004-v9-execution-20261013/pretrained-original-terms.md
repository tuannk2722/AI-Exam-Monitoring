# E001 — Approved local frozen-feature classifier

Owner/reviewer: repository owner. Approval: [ADR-014](../decisions/ADR-014-e001-local-linear-probe.md), 2026-10-06. The [proposal](../reviews/training-readiness-20261006.md) is the parameter source. Dataset v4 remains immutable. This implementation uses local CPU and no uploads.

## Model provenance and terms

Architecture: torchvision ResNet18; weights enum IMAGENET1K_V1. Official URL: https://download.pytorch.org/models/resnet18-f37072fd.pth . Record the complete downloaded SHA-256 in config and receipt; validate the official filename hash prefix before pinning. No implicit download occurs during training.

[TorchVision v0.23.0 LICENSE](https://raw.githubusercontent.com/pytorch/vision/v0.23.0/LICENSE) is BSD-3-Clause for software. Its [README pretrained model notice](https://raw.githubusercontent.com/pytorch/vision/v0.23.0/README.md) states weights can have additional terms inherited from pretraining data. [ImageNet access terms](https://www.image-net.org/download.php) specify non-commercial research/education for the dataset. The owner-approved use is academic local classifier research; retain attribution to TorchVision/ResNet/ImageNet. This is not a blanket weights redistribution or commercial license determination. No weights or people media are committed/uploaded.

ResNet paper: He et al., Deep Residual Learning for Image Recognition, CVPR 2016. [Original paper](https://arxiv.org/abs/1512.03385). Transfer-learning protocol follows the approved project proposal, not the original ImageNet training recipe.

## Environment

Python 3.11. CPU-only torch 2.8.0 / torchvision 0.23.0 are an explicitly supported pair in [official installation instructions](https://pytorch.org/get-started/previous-versions/). Pinning a known supported pair avoids tracking a rolling latest release. Install project base/dev, then requirements/classifier-cpu.txt. The measured run records exact transitive versions in pip-freeze/environment. Production classifiers do not import ultralytics or W&B.

For an exact reconstruction of the measured Windows CPU environment, install requirements/classifier-cpu-lock.txt. Set PYTHONPATH to the checkout's src when using a standalone venv without an editable project install. The local E001 code is pinned to a clean isolated Git checkout; --workspace can point to the original local workspace containing the immutable dataset/weights. No Git push or cloud execution is required for this approved local experiment.

## Commands

Run from the repository root with the project's Python environment. Actual config/weights must exist first:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements/classifier-cpu.txt
.venv/Scripts/python.exe -m ai_exam_monitoring.training.train --config configs/experiments/E001-smoke.yaml --output outputs/E001-smoke
.venv/Scripts/python.exe -m ai_exam_monitoring.training.train --config configs/experiments/E001.yaml --output outputs/E001
.venv/Scripts/python.exe -m ai_exam_monitoring.training.evaluate --run outputs/E001 --split val --output outputs/E001-val-evaluation
```

Outputs must be new directories. Resume an interrupted run using the same config/output plus --resume; code, config, data, features and environment must match. --interrupt-after is an explicit recovery drill and records INTERRUPTED, not FINISHED. OOM/config changes require a new run ID/config; no silent fallback. A crash with no last checkpoint must start a new run rather than overwrite partial artifacts.

Test is never read for model predictions by train. Final evaluation requires a separate protocol pinning the sole candidate's checkpoint SHA, code/config/payload SHA, threshold=0.5 and approval reference. Do not run final test repeatedly to compare variants. The evaluator rejects an absent/mismatched protocol before extracting test features.

## Artifacts and limits

Each run saves resolved config, code hashes, environment, run status, best/last checkpoints, hashed train/val feature caches, loss history/curve, per-target metrics/constant baseline/source slices and per-record predictions. Unknown labels remain null/masked; normal is metadata. Finite placeholder zeros in tensors never become negative annotations. Checkpoint includes optimizer/RNG/early-stop state. Full-batch loss averages known-target means equally. Early stopping uses min_delta/patience; best checkpoint uses the strict raw validation minimum, ties keep earlier epoch.

Dataset is tiny and phone labels confound source with behavior; scores do not establish generalization or production readiness. Test has no positive co-occurrence support. No numeric promotion gate is introduced. Weight/state binaries remain local, with DVC pointer/cache for preservation if available; external transfer is a separate storage-scope decision.
