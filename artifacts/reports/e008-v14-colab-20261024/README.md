# E008 V14 Colab — Bàn giao launcher ngày 24/10/2026

**Cập nhật 25/10: owner đã chạy xong Colab; [kết quả và audit metadata](results-20261025.md).** Campaign gồm 4 smoke + 5 research FINISHED, G0 thắng screening; looking chưa đạt, chưa Selected. Nội dung bên dưới giữ bối cảnh bàn giao ngày 24/10; trạng thái chưa chạy chỉ thuộc đợt chuẩn bị đó.

## Files dùng ngay

- [Notebook E008-V14-Colab.ipynb](../../../notebooks/E008-V14-Colab.ipynb).
- [Bundle e008-colab-bundle.zip](../../../outputs/E008-V14-Colab-20261024/e008-colab-bundle.zip): 489.023.246 bytes. Upload vào **My Drive/E008/** trước khi kết nối GPU.
- [Handoff/checksum](handoff.json), [hướng dẫn chạy và khôi phục](../../../configs/experiments/E008-V14-LOOKING-20261024/README.md).

Bundle SHA256: `8d1b7f25d5fcc11dfe963ab8deea5948e5d5b0d5a3f6a3a086d606a8e116aab7`. Notebook đã pin SHA này; giữ nguyên bundle. Kết quả sẽ ở **My Drive/E008/E008-V14-COLAB-20261024/**; metadata tổng hợp ở **My Drive/E008/E008-V14-results-metadata.zip**. Không có external/public upload trong task này.

## Phạm vi và kiểm tra

[Proposal/authorization/design](../../../configs/experiments/E008-V14-LOOKING-20261024/README.md) triển khai ba arm G0/G1/A1 trên V14. Owner giao tăng thời lượng trong ngân sách cũ; cap 24 epoch, early stopping patience 6, warmup 3, cùng horizon cosine cho mọi arm. Giữ trần 4 giờ, tối đa 7 research run; không tăng batch/resolution, đổi loss, thêm pretrained, hạ thresholds hoặc mua credits.

Core thêm schema V5 và area-weighted spatial pooling; pipeline V4 tiếp tục dùng CLS + global patch mean. Preprocessing mang rectangle content/person qua kích thước resize đã làm tròn và hflip. G1/A1 dùng chung head initialization theo seed. Preparer/runner/bundler hiện có nhận arm/control/pooling/input mới; không nhân bản exporter/trainer theo version.

[Software checks](software-checks.json): 6 spatial tests, 10 representation/V4 tests, 5 anchor-context/V3 tests và 16 adaptation tests — **37 PASS**. Kiểm weighted means bằng scalar reference độc lập, invalid/empty bins, mirrored geometry, image augmentation parity, equal-region logits, frozen-prefix gradients, synthetic resume và standalone reload. Ruff PASS; mypy PASS trên 56 source files. Đây là fixture synthetic, không phải model metrics hoặc GPU acceptance.

[Bundle validation](bundle-validation.json) kiểm inventory/SHA và materialize smoke configs từ thư mục sạch bằng chính source trong bundle; code digest khớp. Local enrollment kiểm đủ 1.199 train / 156 selection, exact approval/pins. Research preparer từ chối khi thiếu receipt GPU thực. Notebook code parse được và SHA pin khớp bundle. Original V13/E008 proposal pins được bảo toàn; E007/E008-V13 không được reseal hoặc chạy lại.

## Giới hạn khi đánh giá

[Input audit](input-audit.json): 334/1.199 train và 69/156 val có person box bằng context. A1 không cô lập background do tokens vẫn self-attention toàn context. G0→G1 đồng thời đổi pooling, bỏ padding và kích thước head; G1→A1 là contrast vùng pooling cùng số chiều.

Val V14 chỉ 29 looking-positive, không đạt support tối thiểu 30 dù precision/recall/FPR có thể tốt. Giữ gate, không kết luận Selected hoặc đạt toàn bộ chất lượng. Dataset/split/horizon đã đổi so E007; chỉ so paired G0/G1/A1 trong campaign V14, không dùng raw E007/V13 metrics làm đối chứng trực tiếp. Giới hạn lineage generated và development validation vẫn giữ nguyên.

Actual GPU/runtime, CU thực tế, timing, resume/reload parity và metrics chỉ được ghi sau khi owner chạy notebook. Sau đó audit `campaign.json`, smoke receipt, từng run/config/environment/checksum/predictions và kết quả qua ba seed trước khi đề xuất bước tiếp.

Dọn scratch đã bị execution policy từ chối với thông báo `blocked by policy`, kể cả khi giới hạn lệnh vào exact path đã kiểm. Hai thư mục tạm `outputs/_scratch/e008-prepare` và `outputs/_scratch/e008-portable-check` cùng cache còn lưu; không ảnh hưởng bundle/inputs. [Receipt cleanup](cleanup.json) ghi phần còn lại, không giả định đã dọn xong.

Đợt rà soát trước commit ngày 25/10: 220 software tests, Ruff, mypy, compile và checker Git PASS; bổ sung bảo toàn exact bytes E008/V14 qua `.gitattributes`. [Dry-run cleanup](codebase-cleanup-plan-20261025.json) và [receipt](codebase-cleanup-20261025.json) ghi 1.456 files tạm / 533.806.757 bytes còn giữ vì execution policy tiếp tục chặn lệnh xóa. Source/model/data đã pin được kiểm bảo toàn; scratch/cache không đưa vào commit.
