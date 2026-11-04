# Membership đã duyệt và phương án allocation

Owner đã yêu cầu loại **V6-EX-003** và sử dụng đủ 21 ảnh generated, xác nhận chúng được tạo từ crop trong cohort hơn 1.600 ảnh đã audit. Quyết định này thay yêu cầu quarantine 21 ảnh ở tổng kết/kế hoạch trước; không yêu cầu owner cung cấp lại lịch sử tạo ảnh.

## Trạng thái hiện hành

[Candidate r2](candidate-final-audit-r2.json) có **1.304 crop: 1.155 cũ + 149 mới**, không còn U/U. [Cohort cũ r2](reconciled-review-final-r2.json), [331 nhóm](leakage-groups-final-audit-r2.json), [checks](owner-use-update-checks.json). Toàn bộ 21 ảnh đã bỏ blocker quarantine và được ghi nguồn theo xác nhận owner ở cấp cohort; không bịa ID parent cụ thể hoặc recipe. Các snapshot đã pin trước đó giữ nguyên, không dùng số đếm cũ để đóng release.

## Phân bổ cụ thể để chốt

[Allocation proposal từng ID](allocation-proposal.json) kế thừa role của nhóm V12; nhóm mới hoặc review_only đã được cho dùng đề xuất train. Không random resplit. Không có nhóm đã xác định nào chứa đồng thời train/val/test của V12. Toàn bộ 21 ảnh được đề xuất train.

| Phương án | Train | Validation/development | Test | Ý nghĩa |
|---|---:|---:|---:|---|
| A — đề xuất | 1.119 | 185 | 0 | Chuyển 5 test đã mở audit sang development; cần holdout mới và protocol riêng nếu muốn final test độc lập. |
| B — giữ role cũ | 1.119 | 180 | 5 | Giữ 5 mẫu với role test lịch sử; phải ghi đã mở audit, không gọi là holdout độc lập, chưa chạy test metrics. |

File JSON hiện biểu diễn B để đối chiếu trực tiếp parent; chưa là assignment được áp. Nếu owner chọn A, chuyển cả nhóm chứa 5 mẫu sang val, giữ bản so sánh parent trong report.

21 ảnh được dùng theo xác nhận và approval của owner; vì chưa có exact parent ID, chưa chứng minh chúng không bắt nguồn từ ảnh thuộc val hoặc test cũ. Không lấy việc các nhóm đang tách nhau làm bằng chứng độc lập thống kê. Kết quả trên tập hiện tại phải được diễn giải là development, không là ước lượng trên holdout độc lập. Không tự gộp toàn cohort thành một nhóm hoặc tự loại 21 ảnh trở lại.

## Bước đóng package sau chọn phương án

Map strict records theo `pilot_schema`, giữ exact crop SHA, source/derivation, geometry, nhãn/masks và evidence đã duyệt. Quyền local dùng 21 ảnh dẫn đúng quyết định owner; không suy quyền upload/phát hành công khai. Chốt dataset/version identity và allocation cụ thể, export bằng `pilot_package` vào path mới; kiểm inventory/bytes/schema/group leakage/delta/rebuild rồi mới nghiệm thu release. V12 giữ nguyên, không training hoặc inference trong bước chuẩn bị này.

Kế hoạch cũ ở release-preparation-plan.md còn dùng cho các bước codec/export/checks, nhưng membership/quarantine và số đếm được thay bằng tài liệu này.
