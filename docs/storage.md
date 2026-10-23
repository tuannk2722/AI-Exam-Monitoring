# Chính sách lưu trữ và vòng đời tài sản

Owner duyệt 16/10/2026: ưu tiên dataset/model hiện hành và khả năng cải thiện; không giữ khả năng tái lập mọi thử nghiệm. Chính sách này thay đề xuất ở commit `999c0cc`, chuyển thành tài liệu hệ thống chính thức; không thay consent/retention media runtime trong [system spec](system.md#5-yêu-cầu-vận-hành-và-luồng-người-dùng).

## Nguồn sự thật

- Chính sách: tài liệu này (`docs/storage.md`). Trạng thái payload: [availability](../artifacts/reports/storage-retention-20261016/availability.json); chỉ đọc inventory chi tiết khi task cần.
- `archive/index.json` và DVC pointers giữ identity/checksum; không chứng minh binary còn tồn tại hoặc đã remote backup.
- [Cleanup 23/10](../artifacts/reports/cleanup-20261023/README.md) cập nhật availability riêng cho exact paths đã nghỉ lưu trong manifest; dùng locator này cùng availability 16/10 khi restore bản làm việc E004 hoặc candidate V13.
- Report/approval/pins lịch sử giữ nguyên, mô tả thời điểm thực hiện. [Receipt cleanup](../artifacts/reports/storage-retention-20261016/README.md) giữ kết quả, không là backlog.

## Giữ và nghỉ lưu

| Loại | Quy tắc |
|---|---|
| Dataset/model hiện hành | Giữ đủ bytes và dependencies để dùng, đánh giá, cải thiện; nhãn/split/group/provenance/rights/config/preprocessing/metrics/approval đi cùng |
| Nguồn và review | Giữ nguồn cần recrop/QA và evidence độc nhất; tên interim/preview không tự cho phép xóa |
| Run đang chạy/gián đoạn | Giữ checkpoint resume; FINISHED không đồng nghĩa model Selected |
| Lịch sử đã đóng | Có thể nghỉ lưu theo scope/manifest được duyệt sau kiểm dependencies; giữ metadata và ghi availability. Không xóa nếu consumer hiện hành còn cần |
| Backup | Theo mốc tài sản có giá trị, kiểm restore; không ZIP toàn workspace sau mỗi task. Cùng ổ không chống hỏng ổ; off-device/upload cần scope riêng |

Bất biến = không sửa bytes rồi giữ nguyên identity/checksum; không có nghĩa giữ payload vĩnh viễn. Nghỉ lưu không sửa/reseal pins hoặc nới evaluator. Package chỉ còn metadata không được dùng như package đầy đủ.

## Thiếu input

1. Kiểm đúng version/path và [availability](../artifacts/reports/storage-retention-20261016/availability.json); không chọn bản có ID lớn nhất.
2. Còn được giữ: tra active → Git cho text/code → inventory archive/backup; restore đúng pins khi task cần theo [runbook operations](operations.md).
3. Đã nghỉ lưu hoặc không có bản xác minh: báo giới hạn, dừng phần phụ thuộc; tiếp tục coding độc lập. Không tự thay bằng dataset mới, dựng lại crop hoặc tải version khác để qua guard.

## Thao tác

Cleanup cần dry-run exact paths/hashes, kiểm dependencies/backup phù hợp và protected bytes trước/sau. Chỉ một apply hoạt động; mất kết nối tool không chứng minh process đã dừng. Giữ logs/config/kết quả smoke; bỏ weights chỉ khi không còn consumer cần.

Đợt 16/10 giữ V10/development, model chính, last.pt C345/E001–E003, nguồn và gallery; chi tiết ở availability. Script trong report là migration một lần, không là công cụ cleanup định kỳ. Kho ảnh chung theo hash chưa triển khai; không đổi loader hoặc paths package hiện hành để dedup.

