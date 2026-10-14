# E004-RC1-EXECUTION-20261014 — Hoàn tất ablation đã duyệt

- Trạng thái: hoàn thành phạm vi được duyệt; owner repository-owner; không delegation.

## Yêu cầu và quyền
User đã duyệt phương án RC1 ngày 14/10/2026, sau đó yêu cầu resume. Receipt owner-approval.json pin plan gốc. Implementation/fixtures, freeze, smoke/recovery và 4 main runs/evaluations đã hoàn tất trong budget; không còn run được duyệt cần chạy. Không test/reserve/promotion/labels/splits/upload/commit.

## Inputs và contract
E004-V9-L4 parent, random shared head, warm LP best epoch 10 FC, ImageNet original, package V9 và cohort/scope đúng pins. Schema matched-adaptation-v2 bổ sung learned-head provenance và early diagnostics; giữ v1 semantics/final-test guards. Spec không đổi; reference cập nhật API và lifecycle. Source cũ/mới đã archive và restore byte-exact; RC1 identity 5268fa4a6f0d45aed5e1e96d89cd1e5e085b2f6073ddb60babb8c9302e7dbd32 giữ nguyên sau freeze.

## Outputs và evidence
Outputs/E004-RC1-R-H, W-H, R-L, W-L và các development-evaluation folders là canonical runs. Configs/experiments/E004-RC1-20261014 có configs/approval/readiness/protocol, EXECUTION dẫn tới approval và kết quả; proposal plan/README giữ bytes snapshot ban đầu. Artifacts/reports/E004-RC1-execution-20261014 có results/contrasts, integrity, reload, backup/restore/cleanup và report. Canonical study-tools và gallery curves ở outputs/E004-RC1-execution-20261014; metadata giữ Git, binaries local/DVC. Giữ các task evidence trước, không reseal E004/V9.

## Checks và lifecycle
46 training regression tests PASS, Ruff src/tests/scripts PASS, strict mypy 42 source files PASS, compileall PASS. Smoke/recovery PASS 1.482,825 giây dưới trần 1.800; revision B2 kết hợp recovery đúng budget, không đổi scientific variables. 4 main runs FINISHED 11 epochs/best 1; 45 updates/epoch/shared sampler/pins/checksums/tensors PASS. Comparator R-H history/metrics/predictions 5 cohorts và best tensors khớp E004 gốc. Reload 4 cohorts/run delta 0, metrics/masks/decisions parity PASS. Independent cached metric audit PASS; tổng recorded training 5.928,095 giây dưới trần 30.600.
Backup 1.588 paths/restore 1.588 files byte-exact; restored loader/checksums PASS, DVC local đăng ký, cùng ổ D chưa off-device. Đã dọn duy nhất outputs/_scratch/e004-rc1-execution-20261014 sau bảo toàn scripts/source snapshots/canonical outputs. Links/JSON/YAML/SVG/config pins/diff/checker PASS; untracked source/config/report/DVC pointers chưa stage, không coi checker là Git delivery.

## Kết luận và bước tiếp
Continue research; chưa Selected. W-H giảm selection BCE/AP so L4 cũ, nhưng looking recall thấp hơn frozen LP và phone gain tập trung CF-Q072. LR thấp không cải thiện đồng thời BCE/AP, overfitting còn; mọi arm không đạt M1 tại bất kỳ threshold từ selection scores. Hướng nghiên cứu tiếp là targeted coverage train theo desk/held/partial phone, hard negatives và looking/own-workarea; chưa duyệt nguồn/variables/run mới, không tự chạy confirmation seeds hoặc mở test. Báo cáo giữ limitations một seed/development đã dùng/family dependence; không tuyên bố causal mechanism hoặc promotion.
