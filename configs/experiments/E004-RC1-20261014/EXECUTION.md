# E004-RC1 — Thực thi phương án đã duyệt

Owner đã duyệt ngày 14/10/2026: [receipt](../../../artifacts/reports/E004-RC1-execution-20261014/owner-approval.json). [README](README.md) và [plan](plan.yaml) giữ snapshot proposal ban đầu; chữ Draft trong snapshot không phủ nhận approval này.

Đã hoàn tất scope: smoke/recovery PASS trong budget, bốn main runs FINISHED và development reload parity PASS. Kết quả/contrasts/limitations ở [execution report](../../../artifacts/reports/E004-RC1-execution-20261014/README.md); Continue research, chưa Selected. Không còn run được duyệt trong study cần chạy.

Phạm vi: schema provenance/diagnostics mới và fixtures → freeze exact configs → smoke/recovery trong 30 phút tổng → bốn runs tuần tự CPU, tối đa 2 giờ/run → development reload/analysis. Giữ recipe/data theo plan. Test/reserve/promotion/upload/commit chưa được cấp quyền.

Schema matched-adaptation-v2 chỉ hỗ trợ smoke/research trong đợt này, giữ v1 và final-test guards. Warm snapshot có parent checkpoint/epoch/tensor digest; chỉ lấy FC, backbone ImageNet và optimizer reset. Epoch0/steps15/30 là diagnostic, không tham gia best/early stopping; records có attempt/step/committed epoch cho recovery.

[Software checks](../../../artifacts/reports/E004-RC1-execution-20261014/software-validation.json) PASS 46 training tests, Ruff và strict mypy. [Smoke preflight](../../../artifacts/reports/E004-RC1-execution-20261014/smoke-preflight.json) pin configs/input/code. Trạng thái và kết quả ở [execution report](../../../artifacts/reports/E004-RC1-execution-20261014/README.md).

Configs smoke/main giữ exact pins/approval đúng action. Budget hết giữ status thật, không tự thay variables/budget hoặc chạy thêm seed. Sau gain development mới cân nhắc confirmation; FINISHED không Selected.
