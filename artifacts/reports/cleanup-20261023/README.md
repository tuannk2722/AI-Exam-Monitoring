# Cleanup workspace — 23/10/2026

Owner yêu cầu dọn codebase và dung lượng sau V13, rồi commit. Đã xóa **4.690 file / 1.118.246.110 bytes** (1,118 GB; 1,041 GiB): cache công cụ, crop candidate trùng V13 và bản làm việc media E004 cũ đã có blob archive khớp SHA. Không xóa nguồn/evidence độc nhất.

Dung lượng trống ổ D tăng 1.127.870.464 bytes trong khoảng apply/check; đây là số đo toàn ổ, có thể chịu ảnh hưởng tiến trình khác. Tất cả file đã xóa có một hardlink tại thời điểm kiểm. Tổng kích thước hiển thị của workspace có thể đếm lặp archive và DVC cache qua hardlink; không coi tổng này là dung lượng đĩa thực.

## Evidence và availability

- [Exact manifest](cleanup-manifest.json): path, bytes, SHA và archive/member khôi phục cho media E004. Blob trong ZIP đã được đọc và kiểm SHA trước xóa bản làm việc.
- [Kết quả apply](cleanup-result.json), [protected snapshot](protected-before.json): 12.461 file trong `data/processed`, `data/raw`, `outputs`, `archive` và source-inputs V13 khớp SHA trước/sau; không thiếu file.
- Candidate `data/interim/v13-release-preparation-20261023/package/crops` đã nghỉ lưu; metadata/checksums giữ nguyên. Khôi phục file cùng tên từ `data/processed/pilot-b/pilot-b-20261023-v13/crops`, kiểm SHA theo manifest trước sử dụng candidate. Không coi candidate hiện tại là package đầy đủ.
- Media E004 có trong manifest không còn tại working path. Khi cần mở gallery/recrop lịch sử, đọc đúng `restore_member` trong `restore_archive`, kiểm SHA và đặt lại đúng `path`. Không chạy gallery lịch sử với giả định payload còn đủ. Không đổi pin hoặc tái tạo ảnh thay thế.
- Cache `.mypy_cache`, `.ruff_cache`, `.pytest_cache` tái tạo qua công cụ tương ứng. Không có giá trị nguồn độc nhất.

Giữ accepted V13 và các dataset/model hiện có, môi trường ML, archive, nguồn rebuild V13, ảnh/input/board của audit mới nhất. Phần dung lượng này không được coi là rác chỉ vì lớn. Archive cùng ổ không phải off-device backup. Availability ở đây cập nhật riêng exact paths trong manifest; [receipt 16/10](../storage-retention-20261016/availability.json) vẫn áp dụng cho phần khác.

## Code và validation

Đưa vào commit công cụ diagnostics/review/reconcile, tests, policy owner đã chốt, hồ sơ audit và release V13 cùng protocol loader zero-test. Cleanup không đổi nhãn/split hoặc bytes release accepted. TASK thay bằng task cleanup; status bỏ checkpoint đã superseded, dẫn release hiện hành và availability mới.

Ruff PASS; 200 unit tests PASS; mypy PASS trên 48 source files. Không train, inference hoặc upload trong cleanup. Kết quả Git index và bàn giao cuối ở [handoff](handoff.json).
