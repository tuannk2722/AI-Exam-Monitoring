# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-10-18**. Chỉ giữ trạng thái hiện hành, thay nội dung khi tiến độ đổi; không append nhật ký/metrics/mọi task. Không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data engineering | V11 local accepted: 1.823 ledger records, 1.185 train / 266 val / 11 test; bổ sung đúng 270 crop đã duyệt | [V11 release/pointers](../artifacts/reports/dataset-release-20261017/README.md), [allocation và mức đạt](../artifacts/reports/train-val-plan-20261017/README.md) |
| Baseline | E001–E003 FINISHED, Continue research; chưa model Selected | Reports → runs/baseline |
| Model improvement | E005 V11 (1 smoke + 4 runs) FINISHED, reload parity PASS; `E005-V11-S1-AUG` tốt nhất (`Val Macro AP = 0.7378`, `Val BCE = 0.5260`, `phone AP = 0.8161`, `looking AP = 0.6595`), tăng `+0.0365` Macro AP so với LP nhưng chưa đồng thời đạt cổng 80/80/20 cả hai target; Continue research, chưa Selected | [E005 V11 results](../artifacts/reports/e005-v11-adaptation-20261018/README.md), [C345 lịch sử](../artifacts/reports/E004-train-enrollment-20261016/README.md) |
| Runtime | Generic detector/JSONL guards và dataclass có; chưa person → context crop → classifier B | [Reference](reference.md), [system](system.md) |
| Tracking/events/risk/web | Chưa end-to-end; tracker/rules/risk còn quyết định mở | [Decisions](decisions.md), system acceptance |
| Tooling/storage | Giữ V11, parent V10/development, model chính và nguồn; backup V11 local kiểm restore, cùng ổ D | [Release](../artifacts/reports/dataset-release-20261017/README.md), [chính sách](storage.md), [availability lịch sử](../artifacts/reports/storage-retention-20261016/README.md) |

## Phạm vi hiện hành

- [Thực nghiệm E005 trên V11 đã hoàn tất](../artifacts/reports/e005-v11-adaptation-20261018/README.md) theo đúng [phê duyệt E005](../artifacts/reports/e005-v11-adaptation-20261018/owner-e005-approval.json) và [mức đạt V11](../artifacts/reports/train-val-plan-20261017/owner-acceptance.json): 1 smoke (`E005-V11-AC-L4B1-SMOKE`) và 4 run đối chứng (`E005-V11-LP`, `E005-V11-S1-AUG`, `E005-V11-AC-L4B1`, `E005-V11-AC-L4`) đều `FINISHED` và `PASS` standalone reload parity. Cấu hình Single-Crop + Regularized MLP + 2-Stage `layer4.1` + Augmentation + Balanced Smoothed BCE (`E005-V11-S1-AUG`) đạt cao nhất (`Val Macro AP = 0.7378`, `Val BCE = 0.5260`, `phone_use Precision = 80.0% / FPR = 12.5%` ở ngưỡng `0.50` và `Recall = 79.2% / F1 = 0.7651` ở ngưỡng hiệu chỉnh `0.41`), nhưng chưa đồng thời vượt cổng `80 / 80 / 20` trên cả hai target. Quyết định hiện hành: `continue_research_only`, chưa có model `Selected`.
- Dataset dùng tiếp: [V11 pointer và SHA](../artifacts/reports/dataset-release-20261017/package-pointers.json) (1.185 train / 266 val / 11 test). Toàn bộ các run E005 khởi tạo sạch từ `IMAGENET1K_V1` + head mới (`seed = 20261018`), không warm-start từ V9/V10. Phân tích lát cắt chỉ ra sự chênh lệch tỷ lệ lớp dương tính của `phone_use` giữa `legacy_val_192` (`62 P / 51 N`, `E005-V11-S1-AUG AP = 0.8606`) và lô mới `new270_val_74` (`10 P / 45 N`, `AP = 0.5020`, nhiều ca âm tính khó ở `owner-frames-part01/02`), cùng giả thuyết mờ do nội suy lại khi cắt tiếp `x_anchor` từ crop kích thước nhỏ; chưa có đối chứng tách riêng để kết luận nguyên nhân. Tập `test` 11 mẫu giữ đóng tuyệt đối.
- [C345 lịch sử](../artifacts/reports/E004-train-enrollment-20261016/README.md) và [Waiver support](../artifacts/reports/E004-v9-consolidation-20261013/owner-direction.json) giữ nguyên phạm vi; M4 còn INCONCLUSIVE; chưa final-test freeze mới.
- [Coverage sau RC1](../artifacts/reports/E004-targeted-coverage-20261014/README.md) còn giới hạn và phần review Draft; không lấy số crops hoặc receipt cũ làm bằng chứng đủ coverage. Lịch sử nguồn/V8/V9/RC1 tra qua [reports index](../artifacts/reports/README.md) khi cần.
- [Availability](../artifacts/reports/storage-retention-20261016/availability.json) xác định payload còn sẵn. Crops active V4–V9/V9 development và một số checkpoint/archive đã nghỉ lưu; metadata/pins không đổi. Không mặc định tái lập được run cũ.
- Runtime/downstream theo [system gates](system.md#6-điều-kiện-chuyển-bước); phần độc lập được user yêu cầu vẫn tiếp tục. Chưa model demo Selected hoặc quality threshold/SLA toàn video Accepted.
