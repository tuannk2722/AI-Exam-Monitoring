# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-10-23**. Chỉ giữ trạng thái hiện hành, thay nội dung khi tiến độ đổi; không append nhật ký/metrics/mọi task. Không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data engineering | V13 local accepted: 1.304 crop, 1.119 train / 185 val development / 0 test; audit và allocation đã chốt | [V13 release/pointers](../artifacts/reports/dataset-release-20261023-v13/README.md) |
| Baseline | E001–E003 FINISHED, Continue research; chưa model Selected | Reports → runs/baseline |
| Model improvement | E006 V12: smoke + 9 research FINISHED, reload parity PASS; chưa run nào đạt đồng thời 80/80/20 trên cả hai target; chưa Selected | [E006 đã review](../artifacts/reports/e006-v12-20261020/README.md) |
| Runtime | Generic detector/JSONL guards và dataclass có; chưa person → context crop → classifier B | [Reference](reference.md), [system](system.md) |
| Tracking/events/risk/web | Chưa end-to-end; tracker/rules/risk còn quyết định mở | [Decisions](decisions.md), system acceptance |
| Tooling/storage | Giữ V13 và các dataset/model/nguồn hiện có; đã dọn 1,118 GB bản sao và cache, có locator khôi phục | [Cleanup/availability](../artifacts/reports/cleanup-20261023/README.md), [chính sách](storage.md) |

## Phạm vi hiện hành

Dataset dùng tiếp là [V13 accepted](../artifacts/reports/dataset-release-20261023-v13/README.md): 1.304 crop, 1.119 train / 185 val development / 0 test. Audit, nhãn, geometry và allocation đã chốt. Dùng đủ 21 ảnh generated; V6-EX-003 excluded. Validation không là holdout độc lập; holdout mới cần nguồn và protocol riêng. V12 và experiment pins lịch sử giữ nguyên; chưa train trên V13.

- [E006 V12](../artifacts/reports/e006-v12-20261020/README.md) hoàn tất; SQRT là recipe tham chiếu development, chưa đạt đồng thời cổng chất lượng cho cả hai target. Chưa model Selected. Các test cũ đã được mở visual audit trong scope V13; không phát sinh quyền inference/final-test mới.
- [Diagnostics V12](../artifacts/reports/e006-v12-diagnostics-20261021/README.md) và [audit](../artifacts/reports/v12-reconcile-20261022/README.md) giữ evidence. Các checkpoint candidate/quarantine cũ đã được thay bằng V13 accepted; không lấy chúng làm backlog.
- [Đối chứng erasing](../configs/experiments/E006-followup-20261021/README.md) chưa run approval. Không tự chuyển configs E005/E006 sang V13 hoặc train lại.
- [Cleanup ngày 23/10](../artifacts/reports/cleanup-20261023/README.md) ghi availability mới cho cache, candidate crops và bản làm việc E004 trùng archive. Giữ metadata/pins, archive, datasets/models và nguồn rebuild V13; [availability 16/10](../artifacts/reports/storage-retention-20261016/availability.json) áp dụng cho phần không được đợt mới cập nhật.
- Runtime/downstream theo [system gates](system.md#6-điều-kiện-chuyển-bước); chưa model demo Selected hoặc quality threshold/SLA toàn video Accepted. Phần độc lập được user yêu cầu vẫn tiếp tục.
