# Tra cứu kết quả và bằng chứng

Index theo đối tượng; không là bảng metrics hoặc backlog. Hồ sơ đã pin là snapshot, kể cả chữ “next”, “pending” hoặc lệnh CLI cũ. [Status](../../docs/status.md) chỉ công việc hiện hành; [operations](../../docs/operations.md) xử lý historical paths/restore. Không sửa report/card/receipt đã seal để cập nhật tiến độ.

## Releases và nghiên cứu dữ liệu

| Đối tượng | Hồ sơ | Nguồn / giới hạn |
|---|---|---|
| Nghiên cứu nguồn, releases v4–v7, coverage, holdout research | [Tổng hợp đến 2026-10-11](data-research-20261011/README.md) | Diễn giải chuyển từ spec, không audit mới; original qua Git/archive locators |
| v4 | [Report](pilot-b-release-acceptance-20261005/README.md), [approval](pilot-b-release-acceptance-20261005/owner-approval.json) | Local release; remote scope riêng |
| v5 | [Report](pilot-b-v5-release-20261007/README.md), [pointer](pilot-b-v5-release-20261007/release-pointer.json) | Parent v4 và metadata dependencies đúng pins |
| v6 | [Report](pilot-b-v6-release-20261007/README.md), [pointer](pilot-b-v6-release-20261007/release-pointer.json) | Validation development, không independent holdout |
| v7 | [Report](pilot-b-v7-release-20261010/README.md), [pointer](pilot-b-v7-release-20261010/release-pointer.json) | Pointer pin card/approval/manifest/verification; không tự train/upload |
| Audit v7 cho E004 | [Kết luận](E004-v7-fit-audit-20261010/README.md), [pins](E004-v7-fit-audit-20261010/input-pins.json) | Cached scores, không prediction mới hoặc approval E004 |

Card/manifest/coverage ở package mà pointer chỉ tới; có thể không hiện diện trong clean Git checkout. Metadata report được Git giữ để hiểu scope và tìm restore. Không cần đọc mọi record để hiểu task.

## Experiments

| Đối tượng | Kết quả / evidence | Config và quyền |
|---|---|---|
| E001 | [Run](E001/run.json), [metrics](E001/metrics.json), [test metrics](E001/test-metrics.json) | [Config](../../configs/experiments/E001.yaml), [approval](../../docs/experiments/E001-approval.json), [final protocol](../../docs/experiments/E001-final-test-protocol.json) |
| E002 | [Summary](E002/summary.json), [metrics](E002/metrics.json), [comparison](E002/comparison.json) | [Config](../../configs/experiments/E002.yaml), [approval](../../docs/experiments/E002-approval.json) |
| E003 | [Summary](E003/summary.json), [metrics](E003/metrics.json), [errors](E003/error-analysis.json) | [Config](../../configs/experiments/E003.yaml), [approval](../../docs/experiments/E003-approval.json) |
| Baseline review | [Recipe/results/errors E001–E003](baseline-review-20261011/README.md) | Snapshot chuyển từ spec, không ghép cohort khác để kết luận gain |

Experiment đang thiết kế: [configs index](../../configs/experiments/README.md). Run mới có hồ sơ riêng; chỉ thêm locator ở đây, không nối vào baseline lịch sử. Checkpoints/predictions ở `outputs/<ID>` theo run pins; restore không cấp test access.

## Vận hành

[Handoff 2026-10-11](repository-handoff-20261011/README.md) giữ snapshot checks/backup và original locator. Các tổng hợp mới trên không thay receipt gốc hoặc là data/model acceptance mới.
