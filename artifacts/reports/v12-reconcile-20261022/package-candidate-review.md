# Candidate package sau allocation A

Membership và allocation đã được owner duyệt: **1.304 crop, 1.119 train / 185 val / 0 test**. Dùng đủ 21 ảnh generated theo xác nhận owner; V6-EX-003 excluded. Không yêu cầu duyệt lại nhãn, membership hoặc allocation.

Package chuẩn bị: `data/interim/v13-release-preparation-20261023/package`, identity `pilot-b-20261023-v13-candidate`. [Checks export](prepared-package-checks.json), [allocation đã duyệt](allocation-approved.json), [nguồn upstream và lineage](candidate-source-provenance.json).

Package hiện là `prepared_pending_gates`: strict ledger có 1.304 crop được owner review, chưa có used manifest. `review_only` trong ledger staging là trạng thái kỹ thuật chờ nghiệm thu package, **không phải loại 21 ảnh hoặc rút approval dùng ảnh**. Allocation A được lưu riêng; sau nghiệm thu package mới áp vào manifest train/val.

Source boundary là bundle crop đã review, SHA `74ac2a4e40e86f2d14e40750aeb837609ee4b5593764636f67ef190834879ece`. Mỗi source/crop byte giữ nguyên. Sidecar giữ nguồn/crop V12 gốc và lineage; không mô tả bundle là ảnh camera nguyên thủy hoặc recipe AI đã xác minh. Không có media crop bị loại trong package.

Checksums package chuẩn bị: `dcc70a73a57ff045df25356fef6f221eb742ab8140e038321da6d476995e0aab`. Schema, source/crop pixel parity và integrity PASS. [Rebuild và allocation](prepared-package-checks-r2.json) đã PASS: đảo thứ tự records vẫn cùng checksums; exact ID set khớp allocation, không nhóm đã xác định nào trộn split, V12 nguyên pin. Bản rebuild dư đã dọn sau bảo toàn evidence.

## Phạm vi nghiệm thu release đề xuất

Đóng release local **pilot-b-20261023-v13** từ đúng candidate đã kiểm và allocation A; quyền `local_classifier_research`, không upload, không train/inference. Export bằng codec/exporter chuẩn vào đường dẫn version mới, kiểm checksum/schema/loader/delta trước cập nhật pointer. Giữ V12 bất biến.

Validation là development: 5 test lịch sử đã mở audit chuyển sang val; 21 ảnh chưa có exact parent nên không khẳng định độc lập nguồn giữa train/val. Holdout riêng cần protocol và nguồn độc lập sau này. Work context/normal trong candidate để unknown vì không có quyết định riêng cho toàn bộ ảnh; nhãn Phone/Looking giữ nguyên.

Đây là bước nghiệm thu package/version cụ thể theo docs/data.md §4 bước 7–9 và docs/reference.md đường export. Approval nhãn và allocation đã có; chỉ còn xác nhận đóng release local theo nội dung package này, không lặp lại các câu hỏi audit.
