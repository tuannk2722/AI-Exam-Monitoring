# E004-C345-W-H

Owner đã duyệt [thiết kế](../../../artifacts/reports/E004-train-enrollment-20261016/experiment-proposal.md) và [geometry/group/compute](../../../artifacts/reports/E004-train-enrollment-20261016/owner-enrollment-approval.json). Chữ Draft trong proposal là snapshot trước approval, không phải trạng thái quyền hiện hành.

Thêm 345 crop accepted vào train, tổng 1.061. Giữ nguyên selection 71, recipe/head/seed RC1-W-H; CPU 4 threads, run tối đa 7.200 giây. Số updates mỗi epoch tăng 45 → 67. Smoke một epoch chỉ kiểm kỹ thuật, không chọn recipe; research config chỉ được materialize sau smoke FINISHED.

Config YAML, protocol, readiness và approval trong thư mục này pin chính xác membership, payload, code và owner authorization. Không sửa các artifacts đã chạy. [Hồ sơ kết quả](../../../artifacts/reports/E004-train-enrollment-20261016/README.md) giữ tiến độ và evidence.

Independence với protected pool chưa được chứng minh; M4 INCONCLUSIVE. Không final test/reserve inference, không model promotion từ approval này.

Execution đã FINISHED: smoke một epoch, research 11 epochs/best epoch 1, standalone reload exact parity. Orphan process sau epoch 8 được phục hồi cùng identity; downtime tính bảo thủ vào budget. Kết luận Continue research, chưa Selected; chi tiết trong hồ sơ kết quả.
