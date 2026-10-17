# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-10-18**. Chỉ giữ trạng thái hiện hành, thay nội dung khi tiến độ đổi; không append nhật ký/metrics/mọi task. Không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data engineering | V11 local accepted: 1.823 ledger records, 1.185 train / 266 val / 11 test; bổ sung đúng 270 crop đã duyệt | [V11 release/pointers](../artifacts/reports/dataset-release-20261017/README.md), [allocation và mức đạt](../artifacts/reports/train-val-plan-20261017/README.md) |
| Baseline | E001–E003 FINISHED, Continue research; chưa model Selected | Reports → runs/baseline |
| Model improvement | C345 FINISHED sau thêm 345 train; looking cải thiện nhưng phone false positives tăng, chưa đạt quality; Continue research, chưa Selected | [C345 results](../artifacts/reports/E004-train-enrollment-20261016/README.md), [RC1 baseline](../artifacts/reports/E004-RC1-execution-20261014/README.md) |
| Runtime | Generic detector/JSONL guards và dataclass có; chưa person → context crop → classifier B | [Reference](reference.md), [system](system.md) |
| Tracking/events/risk/web | Chưa end-to-end; tracker/rules/risk còn quyết định mở | [Decisions](decisions.md), system acceptance |
| Tooling/storage | Giữ V11, parent V10/development, model chính và nguồn; backup V11 local kiểm restore, cùng ổ D | [Release](../artifacts/reports/dataset-release-20261017/README.md), [chính sách](storage.md), [availability lịch sử](../artifacts/reports/storage-retention-20261016/README.md) |

## Phạm vi hiện hành

- [V11 đã materialize](../artifacts/reports/dataset-release-20261017/README.md) đúng phân bổ owner duyệt: 1.185 train / 266 val. [Mức đạt](../artifacts/reports/train-val-plan-20261017/owner-acceptance.json) từng target precision/recall ≥ 80%, FPR ≤ 20% và support theo receipt; cách train chưa chốt, chưa train/smoke mới.
- Dataset dùng tiếp: [V11 pointer và SHA](../artifacts/reports/dataset-release-20261017/package-pointers.json). Validation là development, có 178 mẫu từng ở train cũ; phải khai báo exposure khi diễn giải kết quả model. Test 11 giữ đóng, holdout để sau; parent V10/C345 giữ nguyên và không tự áp dụng protocol selection/diagnostic cũ cho V11.
- [C345 đã hoàn tất](../artifacts/reports/E004-train-enrollment-20261016/README.md): Continue research, chưa Selected; looking cải thiện nhưng phone false positives tăng, overfit còn. Không tự thêm epochs/đổi recipe, nhãn hoặc threshold. Nghiên cứu mới cần proposal và quyền đúng scope.
- [Waiver support](../artifacts/reports/E004-v9-consolidation-20261013/owner-direction.json) có hiệu lực đúng phạm vi; không chứng minh independence hoặc cấp test/promotion. M4 còn INCONCLUSIVE; chưa final-test freeze mới.
- [Coverage sau RC1](../artifacts/reports/E004-targeted-coverage-20261014/README.md) còn giới hạn và phần review Draft; không lấy số crops hoặc receipt cũ làm bằng chứng đủ coverage. Lịch sử nguồn/V8/V9/RC1 tra qua [reports index](../artifacts/reports/README.md) khi cần.
- [Availability](../artifacts/reports/storage-retention-20261016/availability.json) xác định payload còn sẵn. Crops active V4–V9/V9 development và một số checkpoint/archive đã nghỉ lưu; metadata/pins không đổi. Không mặc định tái lập được run cũ.
- Runtime/downstream theo [system gates](system.md#6-điều-kiện-chuyển-bước); phần độc lập được user yêu cầu vẫn tiếp tục. Chưa model demo Selected hoặc quality threshold/SLA toàn video Accepted.
