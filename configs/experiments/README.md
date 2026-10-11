# Experiment configs và proposal

[Training contract](../../docs/training.md) quy định loss/evaluation; [reference](../../docs/reference.md#training-code) mô tả trainer/CLI; [reports](../../artifacts/reports/README.md) giữ kết quả. Không lấy ID lớn nhất làm model được duyệt.

| Hồ sơ | Vai trò | Approval / cách dùng |
|---|---|---|
| [E001](E001.yaml), [smoke](E001-smoke.yaml) | Frozen CPU probe v4 lịch sử | [Approval](../../docs/experiments/E001-approval.json); final test có protocol riêng qua reports index |
| [E002](E002.yaml), [smoke](E002-smoke.yaml) | Frozen CPU probe v5 lịch sử | [Approval](../../docs/experiments/E002-approval.json), không test mới/promotion |
| [E003](E003.yaml), [smoke](E003-smoke.yaml) | Frozen CPU probe v6 lịch sử | [Approval](../../docs/experiments/E003-approval.json), không holdout/promotion |
| [E004 proposal](E004-proposal.md) | Design/comparator/compute/promotion gates Draft | Không config chạy được hoặc approval |
| [E004-plan YAML](E004-plan.yaml) | Snapshot proposal đã được audit pin | Giữ bytes; original paths giải thích trong companion proposal |

Config mới cần identity/hypothesis/inputs/protocol/owner và approval đúng config trước run. Config được report pin giữ nguyên dù còn Draft; revision mới có identity riêng. Proposal ghi lifecycle/decision và link results; metrics ở hồ sơ run. JSON approvals dưới `docs/experiments` giữ original path do code/config phụ thuộc.
