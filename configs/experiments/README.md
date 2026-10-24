# Experiment configs và proposal

[Training contract](../../docs/training.md) quy định loss/evaluation; [reference](../../docs/reference.md#training-code) mô tả trainer/CLI; [reports](../../artifacts/reports/README.md) giữ kết quả. Không lấy ID lớn nhất làm model được duyệt.

[E007 V13 — execution Colab](E007-V13-20261024/README.md): smoke và 9 research FINISHED trên L4, artifacts đã kiểm; D1 thắng, chưa Selected. [Proposal 23/10](E007-V13-20261023/README.md) giữ snapshot Draft đã pin; authorization và exact materialized configs nằm ở execution companion.

[E008 V14 — Colab Pro](E008-V14-LOOKING-20261024/README.md): owner đã chạy 4 smoke + 5 research; G0 thắng screening, audit metadata PASS. Looking thiếu support và chưa đạt precision/recall; Continue research, chưa Selected.

[E008 V13 — proposal gốc](E008-V13-LOOKING-20261024/README.md): snapshot giữ nguyên sau review; ba arm global/context spatial/anchor spatial, tối đa 7 research run và trần 4 giờ GPU mới. [Variables gốc](E008-V13-LOOKING-20261024/proposal.yaml); approval và input hiện hành ở companion V14.

[Follow-up E006 ngày 21/10](E006-followup-20261021/README.md): Draft đối chứng SQRT có/không random erasing sau review nhãn và freeze dataset; chưa executable config hoặc approval run.

| Hồ sơ | Vai trò | Approval / cách dùng |
|---|---|---|
| [E001](E001.yaml), [smoke](E001-smoke.yaml) | Frozen CPU probe v4 lịch sử | [Approval](../../docs/experiments/E001-approval.json); final test có protocol riêng qua reports index |
| [E002](E002.yaml), [smoke](E002-smoke.yaml) | Frozen CPU probe v5 lịch sử | [Approval](../../docs/experiments/E002-approval.json), không test mới/promotion |
| [E003](E003.yaml), [smoke](E003-smoke.yaml) | Frozen CPU probe v6 lịch sử | [Approval](../../docs/experiments/E003-approval.json), không holdout/promotion |
| [E004 proposal](E004-proposal.md) | Snapshot thiết kế/gates đã được audit pin | Trạng thái hiện hành/owner approval ở companion execution; không runnable config |
| [E004 freeze proposal 2026-10-11](E004-freeze-proposal-20261011.md) | Snapshot cohorts/objective/BN/checkpoint/test/reproducibility plan | Owner đã approve tài liệu/thiết kế; giữ chữ Draft và bytes của snapshot, chưa quyền exact run/test |
| [E004 data execution 2026-10-11](E004-data-execution-20261011.md) | Lifecycle sau approval và các bước data/software freeze | [Receipt crop 12/10](../../artifacts/reports/E004-source-review-20261011/owner-review-receipt-20261012.json); nhãn/geometry đã đóng, group/roles/cohorts và G1–G3 còn thiếu |
| [E004-plan YAML](E004-plan.yaml) | Snapshot proposal đã được audit pin | Giữ bytes; original paths giải thích trong companion proposal |
| [E004 execution readiness 12/10](E004-execution-readiness-20261012.md) | Evidence dữ liệu còn thiếu và compute đề xuất sau implementation | Chưa runnable config/approval; software evidence qua reports |

Config mới cần identity/hypothesis/inputs/protocol/owner và approval đúng config trước run. Config được report pin giữ nguyên dù còn Draft; revision mới có identity riêng. Proposal ghi lifecycle/decision và link results; metrics ở hồ sơ run. JSON approvals dưới `docs/experiments` giữ original path do code/config phụ thuộc.

[E006 V12](E006-V12-20261020/README.md): owner duyệt local CPU, tối đa 9 research run
và smoke; ba lựa chọn weighting, đối chứng frozen và xác nhận hai recipe qua ba seed.
Runner tự động, test đóng; trạng thái/kết quả ở
[report E006](../../artifacts/reports/e006-v12-20261020/README.md).

[E005-V11 — Dual-ROI Anchor-Context & 4-Run Ablation trên V11](E005-V11-20261018/README.md): owner đã duyệt thiết kế `matched-adaptation-v3`, ma trận 4 run đối chứng (`E005-V11-LP`, `E005-V11-S1-AUG`, `E005-V11-AC-L4B1`, `E005-V11-AC-L4`) và thực thi local CPU trên dataset V11 (1.185 train / 266 val). Smoke và cả 4 run đã FINISHED, reload parity PASS; kết quả chi tiết tại [báo cáo E005 V11](../../artifacts/reports/e005-v11-adaptation-20261018/README.md).

[E004-C345 — bổ sung 345 train](E004-C345-20261016/README.md): geometry/group/thiết kế đã được owner duyệt; cùng recipe RC1-W-H và selection 71, research với independence chưa chứng minh. [Kết quả và package](../../artifacts/reports/E004-train-enrollment-20261016/README.md).

[E004-RC1 — initialization × LR](E004-RC1-20261014/README.md): proposal snapshot sau audit thị giác 14/10; owner đã duyệt implementation/execution, trạng thái và exact configs ở [execution companion](E004-RC1-20261014/EXECUTION.md). Không thay freeze E004 V9 hoặc cấp test access.

Trạng thái E004 sau ngày 13/10: [V9 và waiver support mới](../../artifacts/reports/E004-v9-consolidation-20261013/README.md). Các yêu cầu bù quota trong snapshot trước đã được owner miễn; protocol/cohort và exact run configs đã được duyệt và thực thi trong revision V9.

Bước lịch sử: [E004 V9 execution freeze](../../artifacts/reports/E004-v9-execution-20261013/README.md), [recipe](E004-v9-execution-20261013/recipe-proposal.yaml), [protocol](E004-v9-execution-20261013/protocol-proposal.json). Exact configs E004-V9-LP.yaml và E004-V9-L4.yaml đã thực thi FINISHED; xem report kết quả. Recipe/protocol proposal giữ snapshot gốc.
