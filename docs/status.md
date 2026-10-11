# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-10-11**. Chỉ giữ trạng thái hiện hành, thay nội dung khi tiến độ đổi; không append nhật ký/metrics/mọi task. Không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data engineering | Releases v4–v7 local accepted; targeted coverage/provenance hạn chế, chưa independent holdout | Reports → release pointers/research |
| Baseline | E001–E003 FINISHED, Continue research; chưa model Selected | Reports → runs/baseline |
| Model improvement | E004 Draft, chưa fine-tune implementation/run | [E004 proposal](../configs/experiments/E004-proposal.md) |
| Runtime | Generic detector/JSONL guards và dataclass có; chưa person → context crop → classifier B | [Reference](reference.md), [system](system.md) |
| Tracking/events/risk/web | Chưa end-to-end; tracker/rules/risk còn quyết định mở | [Decisions](decisions.md), system acceptance |
| Tooling/storage | CI/checker/type gates/restore có; backup cùng D, chưa toàn bộ off-device | [Development](development.md), [handoff](../artifacts/reports/repository-handoff-20261011/README.md) |

## Đầu vào và công việc đang xem xét

- V7 là release local để chuẩn bị nghiên cứu; không mặc định là training config approved. Task phải chỉ parent/version/scope cụ thể; xem pointer qua reports.
- Ưu tiên data: đo targeted matrix phần train mới, đề xuất new-development/holdout có rights/provenance/independence. [Research đã có](../artifacts/reports/data-research-20261011/README.md) tránh audit lại cùng snapshot.
- E004: chốt comparator, recipe/compute, numerical gates và holdout/use scope; checklist chỉ ở proposal. Không tự chạy từ release acceptance.
- Runtime/downstream theo system gate; phần độc lập đúng user scope vẫn được làm. Unit PASS/housekeeping không là model acceptance.

Model demo: **chưa Selected**. Chưa có quality threshold/SLA toàn video Accepted. Thay ưu tiên không tự đổi scientific gates/decisions.
