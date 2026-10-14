# Tra cứu kết quả và bằng chứng

Index theo đối tượng; không là bảng metrics hoặc backlog. Hồ sơ đã pin là snapshot, kể cả chữ “next”, “pending” hoặc lệnh CLI cũ. [Status](../../docs/status.md) chỉ công việc hiện hành; [operations](../../docs/operations.md) xử lý historical paths/restore. Không sửa report/card/receipt đã seal để cập nhật tiến độ.

## Releases và nghiên cứu dữ liệu

E004 hiện hành: [V9 hợp nhất và review mới đã nghiệm thu](E004-v9-consolidation-20261013/README.md), [release pointer](E004-v9-consolidation-20261013/v9-release-pointer.json). V9 local Accepted, không tự cấp quyền run/test.

Snapshot trước: [mở rộng hai ZIP và rà lại nguồn cũ](E004-source-expansion-20261013/README.md), [batch 199 crop đã nghiệm thu](E004-source-expansion-20261013/REVIEW.md). Tổng 308 anchors đã nghiệm thu; [V8 local Accepted](E004-source-expansion-20261013/v8-release-pointer.json) thêm 27 train. [Package prepared trước](E004-consolidated-frames-20261013/package-pointers-r2.json) và các snapshot cũ giữ nguyên.

| Đối tượng | Hồ sơ | Nguồn / giới hạn |
|---|---|---|
| Nghiên cứu nguồn, releases v4–v7, coverage, holdout research | [Tổng hợp đến 2026-10-11](data-research-20261011/README.md) | Diễn giải chuyển từ spec, không audit mới; original qua Git/archive locators |
| v4 | [Report](pilot-b-release-acceptance-20261005/README.md), [approval](pilot-b-release-acceptance-20261005/owner-approval.json) | Local release; remote scope riêng |
| v5 | [Report](pilot-b-v5-release-20261007/README.md), [pointer](pilot-b-v5-release-20261007/release-pointer.json) | Parent v4 và metadata dependencies đúng pins |
| v6 | [Report](pilot-b-v6-release-20261007/README.md), [pointer](pilot-b-v6-release-20261007/release-pointer.json) | Validation development, không independent holdout |
| v7 | [Report](pilot-b-v7-release-20261010/README.md), [pointer](pilot-b-v7-release-20261010/release-pointer.json) | Pointer pin card/approval/manifest/verification; không tự train/upload |
| v8 và E004 source expansion | [Report](E004-source-expansion-20261013/README.md), [pointer V8](E004-source-expansion-20261013/v8-release-pointer.json), [cohorts](E004-source-expansion-20261013/cohort-package-pointers.json) | 199 crop accepted; 27 train bổ sung, development/reserve chưa final freeze |
| Audit v7 cho E004 | [Kết luận](E004-v7-fit-audit-20261010/README.md), [pins](E004-v7-fit-audit-20261010/input-pins.json) | Cached scores, không prediction mới hoặc approval E004 |
| Audit E004 sau V7, 2026-10-11 | [Matrix/gaps/nguồn/comparator/gates](E004-post-v7-audit-20261011/README.md) | Inventory đủ 375 new-train; taxonomy/independence unknown giữ nguyên; protocol/plan vẫn Draft |
| E004 source review và pilot, 2026-10-11–12 | [Nghiệm thu hiện hành/QA/gaps](E004-source-review-20261011/REVIEW-OWNER-20261012.md), [owner receipt](E004-source-review-20261011/owner-review-receipt-20261012.json), [snapshot đầu](E004-source-review-20261011/README.md) | 56 anchors đã nghiệm thu nhãn/geometry, 136 nguồn đã xem; ledger review-only, chưa independent group hoặc assignment mới |

Card/manifest/coverage ở package mà pointer chỉ tới; có thể không hiện diện trong clean Git checkout. Metadata report được Git giữ để hiểu scope và tìm restore. Không cần đọc mọi record để hiểu task.

## Experiments

[E004 V9 execution freeze](E004-v9-execution-20261013/README.md): matched control/layer4 FINISHED; development evaluation và benchmark hoàn tất, khuyến nghị Continue research, test đóng.

[Phân tích nguyên nhân sau E004](E004-root-cause-20261014/README.md): đối chiếu lịch sử, code và cached scores; phân biệt overfitting, giới hạn dữ liệu/cohort và giả thuyết khắc phục; chưa cấp quyền run/test mới.

[Audit thị giác E004](E004-visual-audit-20261014/README.md): 31 crop selection qua 10 family, evidence source/crop/input 224 và nhận xét Draft; dẫn tới proposal ablation E004-RC1, chưa train mới.

[E004-RC1 execution](E004-RC1-execution-20261014/README.md): bốn arms FINISHED, reload parity PASS; warm head/LR cao tốt nhất matrix nhưng chưa đạt quality, Continue research; test đóng.

| Đối tượng | Kết quả / evidence | Config và quyền |
|---|---|---|
| E001 | [Run](E001/run.json), [metrics](E001/metrics.json), [test metrics](E001/test-metrics.json) | [Config](../../configs/experiments/E001.yaml), [approval](../../docs/experiments/E001-approval.json), [final protocol](../../docs/experiments/E001-final-test-protocol.json) |
| E002 | [Summary](E002/summary.json), [metrics](E002/metrics.json), [comparison](E002/comparison.json) | [Config](../../configs/experiments/E002.yaml), [approval](../../docs/experiments/E002-approval.json) |
| E003 | [Summary](E003/summary.json), [metrics](E003/metrics.json), [errors](E003/error-analysis.json) | [Config](../../configs/experiments/E003.yaml), [approval](../../docs/experiments/E003-approval.json) |
| Baseline review | [Recipe/results/errors E001–E003](baseline-review-20261011/README.md) | Snapshot chuyển từ spec, không ghép cohort khác để kết luận gain |
| E004 software readiness | [Implementation/validation](E004-software-readiness-20261012/README.md) | Synthetic I1–I8 và regression; chưa release hoặc run thật |

Experiment đang thiết kế: [configs index](../../configs/experiments/README.md). Run mới có hồ sơ riêng; chỉ thêm locator ở đây, không nối vào baseline lịch sử. Checkpoints/predictions ở `outputs/<ID>` theo run pins; restore không cấp test access.

## Vận hành

[Handoff 2026-10-11](repository-handoff-20261011/README.md) giữ snapshot checks/backup và original locator. Các tổng hợp mới trên không thay receipt gốc hoặc là data/model acceptance mới.
