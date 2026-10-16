# DOCS-RESTRUCTURE-STORAGE-20261016 — Cấu trúc lại tài liệu hệ thống và chính sách lưu trữ

- Trạng thái: hoàn tất; đã chuẩn hóa vị trí và tên file chính sách lưu trữ từ STORAGE_OPTIMIZATION.md thành tài liệu hệ thống chính thức docs/storage.md và cập nhật toàn bộ liên kết trong repository.

## Yêu cầu và hiện trạng
- User goal: chuyển STORAGE_OPTIMIZATION.md (vốn sinh ra là bản kế hoạch thực hiện) thành tài liệu hệ thống chính thức docs/storage.md, chuẩn hóa vị trí, tên file và cập nhật toàn bộ incoming links trong repository; đồng thời phân tích sâu nguyên nhân cốt lõi khiến chất lượng model chưa bứt phá sau nhiều vòng lặp dữ liệu/huấn luyện.
- Đối chiếu Git/files/code: baseline 999c0cc; STORAGE_OPTIMIZATION.md ở root đã được chuyển thành docs/storage.md; toàn bộ links từ AGENTS.md, README.md, docs/00-INDEX.md, docs/decisions.md, docs/development.md, docs/operations.md, docs/reference.md, docs/status.md, docs/system.md, docs/training.md, artifacts/reports/storage-retention-20261016/README.md đã được cập nhật đồng bộ.
- Nguyên tắc: Giữ nguyên các cam kết kỹ thuật và quyết định owner 16/10/2026; không sửa source code, tests, hay pins lịch sử.

## Quyết định và inputs
- Quyết định: STORAGE-RETENTION-20261016 (Accepted); chính sách lưu trữ trở thành contract hệ thống docs/storage.md.
- Inputs: docs/storage.md, docs/00-INDEX.md, AGENTS.md, README.md, docs/decisions.md, docs/development.md, docs/operations.md, docs/reference.md, docs/status.md, docs/system.md, docs/training.md, artifacts/reports/storage-retention-20261016/README.md, cùng toàn bộ báo cáo thực nghiệm E001–E004 (V9, RC1, C345) và mã nguồn training.

## Outputs và vòng đời
- Di chuyển và chuẩn hóa: xóa STORAGE_OPTIMIZATION.md ở root → tạo docs/storage.md.
- Cập nhật references: 11 files tài liệu hệ thống và báo cáo lưu trữ trỏ chính xác về docs/storage.md.
- Hồ sơ: không tạo report mới; giữ nguyên trạng thái chưa stage/commit theo quy tắc bàn giao.

## Contract impact và checks
- Contract impact: Chuẩn hóa bộ tài liệu docs/, docs/storage.md trở thành tài liệu lưu trữ chính thức. Không thay đổi scientific gates, data schema hay model contracts.
- Checks: scripts/check_repo.py PASS (failures=0); tests/test_check_repo.py PASS (13 tests OK); git grep xác nhận không còn reference cũ tới STORAGE_OPTIMIZATION.md ngoài TASK.md.

## Checkpoint và bàn giao
- Đã hoàn tất cấu trúc lại docs/storage.md và đồng bộ toàn bộ hệ thống tài liệu.
- Đã hoàn tất phân tích nguyên nhân gốc rễ về giới hạn chất lượng model qua các vòng E001–E004 và đề xuất lộ trình giải quyết dứt điểm.
