# Đọc tài liệu theo task

Đọc AGENTS → index này → [status](status.md) và TASK, rồi chỉ chọn contract/code/hồ sơ đúng task. TASK hoàn tất không phải lệnh chạy tiếp; không đọc cả reports/archive/plan inventory. Spec quy định hệ thống; status chỉ tiến độ; reports giữ evidence; configs giữ thiết kế/variables theo identity. “Next work” trong report lịch sử không phải backlog hiện hành.

| Task | Contract / hướng dẫn | Context cần chọn |
|---|---|---|
| Phạm vi, kiến trúc, runtime/integration/UI | [System](system.md) | [Reference](reference.md), [decisions](decisions.md), capability ở status |
| Semantics/schema, annotation/group/split/release | [Data](data.md) | [Reports index](../artifacts/reports/README.md) → nguồn/release/coverage đúng version; reference → công cụ data |
| Loss/metrics, training/evaluation/promotion | [Training](training.md) | [Configs index](../configs/experiments/README.md) → proposal/config/approval; reports → kết quả run |
| Coding/setup/checks/bàn giao | [Development](development.md) | [TASK template](templates/task-template.md), source/tests/CI liên quan |
| Lưu trữ, retention và dung lượng | [Storage](storage.md) | [Availability](../artifacts/reports/storage-retention-20261016/availability.json); chỉ đọc receipt/plan chi tiết khi task cần |
| Tái lập/restore/backup | [Operations](operations.md) | Exact pins/commit/package/run; restore không tự cấp test access |

Không đọc toàn bộ mỗi task. Sửa parser: data contract → implementation/tests. Thiết kế E004: training contract → proposal → audit được link. Release mới: data contract → parent pointer/research → công cụ. Restore E003: run pins → operations.

Khi xong, ghi outputs vào hồ sơ đúng đối tượng theo development. **Không cập nhật spec nếu requirement/contract không đổi.** Status chỉ đổi khi capability/input/blocker/ưu tiên đổi; index chỉ thêm locator. Hồ sơ đã pin giữ bytes, path original đã chuyển dùng Git/archive locator, không sửa approval/config để sửa docs.
