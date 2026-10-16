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
| Tooling/storage | CI/checker/type gates/restore có; backup cùng D, chưa toàn bộ off-device | [Development](development.md), [handoff](../artifacts/reports/repository-handoff-20261011/README.md) |

## Đầu vào và công việc đang xem xét

- [Audit mở rộng E004 ngày 13/10](../artifacts/reports/E004-source-expansion-20261013/README.md): đã xem 104 ảnh PX/US và rà lại 222 CF; đã nghiệm thu 199 crop mới (27 train, 47 development, 125 reserve holdout). Tổng 308 anchors accepted qua các batch. [V8 local Accepted](../artifacts/reports/E004-source-expansion-20261013/v8-release-pointer.json) giữ parent val/test; [cohort packages](../artifacts/reports/E004-source-expansion-20261013/cohort-package-pointers.json) chưa final freeze. Review mới có sửa nhãn/geometry, được xử lý bằng revision V9; các counts/receipts V8 là snapshot lịch sử.

- [V10](../artifacts/reports/E004-train-enrollment-20261016/package-pointers.json) là release local mới cho research C345; [V9 parent](../artifacts/reports/E004-v9-consolidation-20261013/v9-release-pointer.json) và các releases trước bất biến. Dataset acceptance không mặc định là training config approved; quyền C345 có receipt riêng.
- Hợp nhất V9 đã nhập đầy đủ review mới và 7 recrop được owner nghiệm thu. 308 anchors các batch xuất hiện đúng một lần, gồm 27 đã có trong V8. Development 71, reserve 199; 4 train candidates cũ và 7 U/U vẫn review-only. [Coverage/giới hạn](../artifacts/reports/E004-v9-consolidation-20261013/README.md). Support quota cũ đã được miễn; chưa final-test freeze mới.
- [E004 V9 execution freeze](../artifacts/reports/E004-v9-execution-20261013/README.md): owner đã duyệt exact membership/recipe/protocol và family boundaries; package experiment/revision v2/smoke đã PASS. Matched E004-V9-LP và E004-V9-L4 đã FINISHED; reload/benchmark PASS, layer4 không cải thiện selection, khuyến nghị Continue research; test vẫn đóng. Owner đã duyệt compute, miễn independence và nay [miễn thiếu hụt support cũ](../artifacts/reports/E004-v9-consolidation-20261013/owner-direction.json). Những yêu cầu bù đủ quota trong snapshot readiness trước đã bị thay thế ở phạm vi này. M4 còn INCONCLUSIVE; waiver không tự cấp quyền test inference hoặc model promotion.
- Runtime/downstream theo system gate; phần độc lập đúng user scope vẫn được làm. Unit PASS/housekeeping không là model acceptance.
- [RC1 results](../artifacts/reports/E004-RC1-execution-20261014/README.md) hoàn tất scope được duyệt: bốn arms và development reload PASS; quality/family gaps còn lớn. [Targeted coverage sau RC1](../artifacts/reports/E004-targeted-coverage-20261014/README.md) đã có matrix 716 train/71 selection, 44 train xem mới và 31 selection từ audit trước; gallery/factors Draft chờ owner review batch; anchor V7-OE-S061-A01 đã được owner xác định là người áo khoác xanh lá đậm. Train có các tình huống liên quan nhưng chưa đủ evidence chốt coverage đầy đủ; chưa duyệt nguồn/variables/run mới, test đóng, nhãn/splits giữ nguyên.

- [Enrollment C345](../artifacts/reports/E004-train-enrollment-20261016/README.md): V10/development có 1.061 train, giữ exact bytes của 345 crop và nội dung parent; deterministic rebuild/loader PASS. Smoke và research FINISHED; run được recovery sau orphan process tại epoch 8, hoàn tất epoch 11/best epoch 1; reload exact parity. Cùng recipe RC1-W-H và selection 71: looking tốt hơn nhưng phone false positives tăng mạnh, overfit chưa giải quyết. Coverage chỉ bù một phần; M4 INCONCLUSIVE, test/reserve không inference, chưa Selected; snapshots V9 bất biến.

Model demo: **chưa Selected**. Chưa có quality threshold/SLA toàn video Accepted. Thay ưu tiên không tự đổi scientific gates/decisions.
