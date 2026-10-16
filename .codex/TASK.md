# FIX-CI-DERIVED-CROP-TORCH-GUARD-20261016 — Thêm guard ML_AVAILABLE cho test crop_path trong test_derived_crop.py

- Trạng thái: hoàn tất; phạm vi tests/test_derived_crop.py.

## Yêu cầu và hiện trạng
- User goal: khắc phục lỗi GitHub Actions fail tại bước `python -m unittest discover -s tests -q` trong job `quality` do `ModuleNotFoundError: No module named 'torch'`.
- Behavior trước: `tests/test_derived_crop.py` gọi trực tiếp `from ai_exam_monitoring.training.data import crop_path` trong `test_import_integrity_and_native_guard`, kéo theo `import torch` ở môi trường base/dev (nơi cố tình không cài PyTorch theo docs/development.md).
- Behavior sau: Tách kiểm tra consumer `crop_path` sang test method riêng có guard `@unittest.skipUnless(ML_AVAILABLE, ...)`, giúp job `quality` chạy đầy đủ suite mà không bị crash vì thiếu torch.

## Quyết định và inputs
- Quyết định: Tuân thủ quy định tại docs/development.md dòng 58-59 ("CI quality dùng base/dev, classifier job dùng Torch CPU/training + preservation fixtures. Base skip đúng tests cần Torch").
- Inputs: tests/test_derived_crop.py, tests/test_source_review.py, .github/workflows/ci.yml.

## Outputs và vòng đời
- Source/tests: tests/test_derived_crop.py được cập nhật.
- Không sửa spec hay contracts hệ thống; không tạo scratch dư thừa.

## Contract impact và checks
- Contract impact: Không thay đổi contract — không sửa spec. Giữ nguyên behavior của training/data.py và data contracts.
- Checks:
  - unittest discover trong môi trường có torch (local .venv): tất cả 165 tests PASS.
  - simulation không có torch: test_derived_crop_path_consumer skipped, test_import_integrity_and_native_guard PASS.
  - ruff check src tests scripts: PASS.
  - compileall src tests scripts: PASS.
  - scripts/check_repo.py --require-git: PASS.

## Checkpoint và bàn giao
- Cập nhật tests/test_derived_crop.py và .codex/TASK.md.
- Đã hoàn tất các bước kiểm tra, tiến hành commit và push theo yêu cầu của user.
