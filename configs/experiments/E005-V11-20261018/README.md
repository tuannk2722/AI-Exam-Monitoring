# E005-V11 — Dual-ROI Anchor-Context & 4-Run Ablation trên Dataset V11

Owner đã duyệt thiết kế kiến trúc Dual-ROI Anchor-Context (`resnet18_anchor_context`), ma trận 4 run đối chứng (`E005-V11-LP`, `E005-V11-S1-AUG`, `E005-V11-AC-L4B1`, `E005-V11-AC-L4`), tiêu chí chọn checkpoint theo `val_macro_ap`, hiệu chỉnh ngưỡng dự đoán trên `val`, hàm mục tiêu Balanced Smoothed BCE (`pos_weight = [1.13, 1.46]`, `label_smoothing = 0.05`) và thực thi local CPU (`threads = 4`, `run_wall_time_seconds = 7200`). Xem [receipt phê duyệt E005](../../../artifacts/reports/e005-v11-adaptation-20261018/owner-e005-approval.json), [receipt nghiệm thu phân bổ và mức đạt V11](../../../artifacts/reports/train-val-plan-20261017/owner-acceptance.json) và [dataset release V11](../../../artifacts/reports/dataset-release-20261017/README.md).

## Cấu hình trong thư mục

- [`protocol.json`](protocol.json): Protocol `matched-protocol-v2` đóng băng 1.185 mẫu `train` (274 nhóm) và 266 mẫu `selection` (`val`, 155 nhóm) từ `pilot-b-20261017-v11`, khóa 11 mẫu `test` trong `reserved_holdout` và đăng ký các lát cắt phân tích (`unexposed_val_88`, `former_train_178`, `new270_val_74`, `legacy_val_192`, `multi_person_context_58`, `single_person_crop_208`).
- [`smoke-readiness.json`](smoke-readiness.json), [`smoke-approval.json`](smoke-approval.json), [`E005-V11-AC-L4B1-SMOKE.yaml`](E005-V11-AC-L4B1-SMOKE.yaml): Kiểm tra kỹ thuật 1 epoch và standalone reload parity cho kiến trúc `resnet18_anchor_context` trước khi materialize 4 cấu hình research.
- [`research-readiness.json`](research-readiness.json), [`research-approval.json`](research-approval.json): Readiness và approval pin kết quả smoke, code SHA-256, dataset V11 và 4 cấu hình đối chứng:
  1. [`E005-V11-LP.yaml`](E005-V11-LP.yaml): Baseline Linear Probe (`resnet18_single_crop_v3`, `head_only`, single-crop `x_context`, không augmentation).
  2. [`E005-V11-S1-AUG.yaml`](E005-V11-S1-AUG.yaml): Single-Crop + Regularized MLP Head (`128D`, `dropout = 0.3`) + 2-Stage `layer4.1` + Augmentation + Balanced Smoothed BCE.
  3. [`E005-V11-AC-L4B1.yaml`](E005-V11-AC-L4B1.yaml): **Primary Candidate** — Dual-ROI Anchor-Context (`resnet18_anchor_context`, `x_anchor` + `x_context` + `6D g_rel` -> `1542D`) + Regularized MLP Head + 2-Stage `layer4.1` + Synchronous Dual-ROI Augmentation + Balanced Smoothed BCE.
  4. [`E005-V11-AC-L4.yaml`](E005-V11-AC-L4.yaml): Dual-ROI Anchor-Context mở toàn bộ `layer4` ở Stage 2 để đối chứng dung lượng tham số với `layer4.1`.

Toàn bộ các run khởi tạo sạch từ `IMAGENET1K_V1` (`outputs/pretrained/resnet18-f37072fd.pth`) và head khởi tạo mới (`seed = 20261018`) tại `data/interim/E005-V11-20261018/`, không warm-start từ bất kỳ checkpoint V9/V10 nào để tránh rò rỉ trên 178 mẫu `val` từng thuộc `train` cũ. Tập `test` (11 mẫu) giữ đóng hoàn toàn. Kết quả chi tiết và bảng đối chiếu tại [báo cáo E005 V11](../../../artifacts/reports/e005-v11-adaptation-20261018/README.md).
