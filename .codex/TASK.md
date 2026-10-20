# E006-CLEAN-COMMIT-20261021 — Tinh gọn và commit

- Owner duyệt dọn run lỗi, tài liệu/bản chuẩn bị dư và commit ngày 21/10/2026.
- Đã xóa 109 file (9.134.002 bytes): run LP lỗi, cấu hình/head chuẩn bị không dùng, log và báo cáo tự động trùng lặp. Danh sách ở `artifacts/reports/e006-v12-20261020/cleanup-receipt.json`.
- Giữ smoke và 9 research run/evaluation cùng dependency; đối chiếu SHA sau dọn: 2.508 file PASS. Giữ nguyên config/receipt/artifact đã pin còn cần; không đổi variables, train lại hoặc mở test.
- Tinh gọn report và cấu hình README; sửa encoding status; thêm Git attributes giữ exact bytes config E006.
- Checks: Ruff PASS; mypy 45 source files PASS; 178 unittest PASS. Bước bàn giao: kiểm Git index/staged diff, commit và kiểm clean checkout; dọn scratch/cache sau kiểm.
