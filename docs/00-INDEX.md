# Đọc tài liệu theo task

Bắt đầu từ AGENTS, TASK và [status](status.md), rồi đọc contract/code/hồ sơ đúng task. Spec quy định hệ thống; status chỉ tiến độ; reports giữ evidence; configs giữ thiết kế/variables theo identity. “Next work” trong report lịch sử không phải backlog hiện hành.

| Task | Contract / hướng dẫn | Context cần chọn |
|---|---|---|
| Phạm vi, kiến trúc, runtime/integration/UI | [System](system.md) | [Reference](reference.md), [decisions](decisions.md), capability ở status |
| Semantics/schema, annotation/group/split/release | [Data](data.md) | [Reports index](../artifacts/reports/README.md) → nguồn/release/coverage đúng version; reference → công cụ data |
| Loss/metrics, training/evaluation/promotion | [Training](training.md) | [Configs index](../configs/experiments/README.md) → proposal/config/approval; reports → kết quả run |
| Coding/setup/checks/bàn giao | [Development](development.md) | [TASK template](templates/task-template.md), source/tests/CI liên quan |
| Tái lập/restore/backup | [Operations](operations.md) | Exact pins/commit/package/run; restore không tự cấp test access |

Không đọc toàn bộ mỗi task. Sửa parser: data contract → implementation/tests. Thiết kế E004: training contract → proposal → audit được link. Release mới: data contract → parent pointer/research → công cụ. Restore E003: run pins → operations.

Khi xong, ghi outputs vào hồ sơ đúng đối tượng theo development. **Không cập nhật spec nếu requirement/contract không đổi.** Status chỉ đổi khi capability/input/blocker/ưu tiên đổi; index chỉ thêm locator. Hồ sơ đã pin giữ bytes, path original đã chuyển dùng Git/archive locator, không sửa approval/config để sửa docs.
