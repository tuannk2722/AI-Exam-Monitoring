# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-10-13**. Chỉ giữ trạng thái hiện hành, thay nội dung khi tiến độ đổi; không append nhật ký/metrics/mọi task. Không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data engineering | Releases v4–v9 local accepted; V9 hợp nhất 1.208 records, 716 train/49 val/11 test; 71 development và 199 reserve giữ review-only | [V9 release và review mới](../artifacts/reports/E004-v9-consolidation-20261013/README.md), release pointer |
| Baseline | E001–E003 FINISHED, Continue research; chưa model Selected | Reports → runs/baseline |
| Model improvement | E004 V9 control/layer4 đã FINISHED và đánh giá development; layer4 kém control trên selection, khuyến nghị Continue research, chưa Selected | [Software evidence](../artifacts/reports/E004-software-readiness-20261012/README.md), [execution companion](../configs/experiments/E004-data-execution-20261011.md) |
| Runtime | Generic detector/JSONL guards và dataclass có; chưa person → context crop → classifier B | [Reference](reference.md), [system](system.md) |
| Tracking/events/risk/web | Chưa end-to-end; tracker/rules/risk còn quyết định mở | [Decisions](decisions.md), system acceptance |
| Tooling/storage | CI/checker/type gates/restore có; backup cùng D, chưa toàn bộ off-device | [Development](development.md), [handoff](../artifacts/reports/repository-handoff-20261011/README.md) |

## Đầu vào và công việc đang xem xét

- [Audit mở rộng E004 ngày 13/10](../artifacts/reports/E004-source-expansion-20261013/README.md): đã xem 104 ảnh PX/US và rà lại 222 CF; đã nghiệm thu 199 crop mới (27 train, 47 development, 125 reserve holdout). Tổng 308 anchors accepted qua các batch. [V8 local Accepted](../artifacts/reports/E004-source-expansion-20261013/v8-release-pointer.json) giữ parent val/test; [cohort packages](../artifacts/reports/E004-source-expansion-20261013/cohort-package-pointers.json) chưa final freeze. Review mới có sửa nhãn/geometry, được xử lý bằng revision V9; các counts/receipts V8 là snapshot lịch sử.

- [V9](../artifacts/reports/E004-v9-consolidation-20261013/v9-release-pointer.json) là release local hiện hành; V8 và các release trước bất biến. Dataset acceptance không mặc định là training config approved.
- Hợp nhất V9 đã nhập đầy đủ review mới và 7 recrop được owner nghiệm thu. 308 anchors các batch xuất hiện đúng một lần, gồm 27 đã có trong V8. Development 71, reserve 199; 4 train candidates cũ và 7 U/U vẫn review-only. [Coverage/giới hạn](../artifacts/reports/E004-v9-consolidation-20261013/README.md). Support quota cũ đã được miễn; chưa final-test freeze mới.
- [E004 V9 execution freeze](../artifacts/reports/E004-v9-execution-20261013/README.md): owner đã duyệt exact membership/recipe/protocol và family boundaries; package experiment/revision v2/smoke đã PASS. Matched E004-V9-LP và E004-V9-L4 đã FINISHED; reload/benchmark PASS, layer4 không cải thiện selection, khuyến nghị Continue research; test vẫn đóng. Owner đã duyệt compute, miễn independence và nay [miễn thiếu hụt support cũ](../artifacts/reports/E004-v9-consolidation-20261013/owner-direction.json). Những yêu cầu bù đủ quota trong snapshot readiness trước đã bị thay thế ở phạm vi này. M4 còn INCONCLUSIVE; waiver không tự cấp quyền test inference hoặc model promotion.
- Runtime/downstream theo system gate; phần độc lập đúng user scope vẫn được làm. Unit PASS/housekeeping không là model acceptance.

Model demo: **chưa Selected**. Chưa có quality threshold/SLA toàn video Accepted. Thay ưu tiên không tự đổi scientific gates/decisions.
