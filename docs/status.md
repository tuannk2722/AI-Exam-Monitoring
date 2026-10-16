# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-10-16**. Chỉ giữ trạng thái hiện hành, thay nội dung khi tiến độ đổi; không append nhật ký/metrics/mọi task. Không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data engineering | V10 local accepted cho research: 1.553 ledger records, 1.061 train/49 val/11 test; development package giữ selection 71 cũ, không thêm holdout từ 345 crop mới | [V10 enrollment/pointers](../artifacts/reports/E004-train-enrollment-20261016/README.md), [parent V9](../artifacts/reports/E004-v9-consolidation-20261013/README.md) |
| Baseline | E001–E003 FINISHED, Continue research; chưa model Selected | Reports → runs/baseline |
| Model improvement | C345 FINISHED sau thêm 345 train; looking cải thiện nhưng phone false positives tăng, chưa đạt quality; Continue research, chưa Selected | [C345 results](../artifacts/reports/E004-train-enrollment-20261016/README.md), [RC1 baseline](../artifacts/reports/E004-RC1-execution-20261014/README.md) |
| Runtime | Generic detector/JSONL guards và dataclass có; chưa person → context crop → classifier B | [Reference](reference.md), [system](system.md) |
| Tracking/events/risk/web | Chưa end-to-end; tracker/rules/risk còn quyết định mở | [Decisions](decisions.md), system acceptance |
| Tooling/storage | Retention theo tài sản hiện hành: V10/development/model chính giữ; payload lịch sử được retire có inventory. Backup hiện hành đã restore kiểm, cùng D, chưa off-device | [Chính sách](storage.md), [availability/receipt](../artifacts/reports/storage-retention-20261016/README.md) |

## Phạm vi hiện hành

- Dataset dùng tiếp: [V10 canonical và C345 development](../artifacts/reports/E004-train-enrollment-20261016/package-pointers.json). Giữ selection 71 và diagnostic 49, test/reserve đóng; acceptance dataset không cấp quyền run mới.
- [C345 đã hoàn tất](../artifacts/reports/E004-train-enrollment-20261016/README.md): Continue research, chưa Selected; looking cải thiện nhưng phone false positives tăng, overfit còn. Không tự thêm epochs/đổi recipe, nhãn hoặc threshold. Nghiên cứu mới cần proposal và quyền đúng scope.
- [Waiver support](../artifacts/reports/E004-v9-consolidation-20261013/owner-direction.json) có hiệu lực đúng phạm vi; không chứng minh independence hoặc cấp test/promotion. M4 còn INCONCLUSIVE; chưa final-test freeze mới.
- [Coverage sau RC1](../artifacts/reports/E004-targeted-coverage-20261014/README.md) còn giới hạn và phần review Draft; không lấy số crops hoặc receipt cũ làm bằng chứng đủ coverage. Lịch sử nguồn/V8/V9/RC1 tra qua [reports index](../artifacts/reports/README.md) khi cần.
- [Availability](../artifacts/reports/storage-retention-20261016/availability.json) xác định payload còn sẵn. Crops active V4–V9/V9 development và một số checkpoint/archive đã nghỉ lưu; metadata/pins không đổi. Không mặc định tái lập được run cũ.
- Runtime/downstream theo [system gates](system.md#6-điều-kiện-chuyển-bước); phần độc lập được user yêu cầu vẫn tiếp tục. Chưa model demo Selected hoặc quality threshold/SLA toàn video Accepted.
