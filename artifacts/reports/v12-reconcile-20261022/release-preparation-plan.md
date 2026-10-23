# Kế hoạch chuẩn bị release sau audit V12

Trạng thái: **đề xuất thực hiện sau chốt audit**, chưa là approval phát hành hoặc allocation. Parent là `pilot-b-20261020-v12`. Không tự lấy version/experiment lớn nhất làm scope. Snapshot đầu vào là [candidate-final-audit.json](candidate-final-audit.json), [checks](final-audit-checks.json) và [nhóm audit](leakage-groups-final-audit.json).

Mục tiêu: đưa quyết định owner đã chốt vào package mới sạch, bỏ payload crop loại, giữ exact pixels và đúng nhãn/unknown masks, ngăn ảnh cùng nguồn hoặc biến thể nằm khác split. Không train lại trong task release.

## 1. Chốt eligibility và provenance

Inventory audit có 1.305 crop: 1.156 cũ, 149 mới. Bảy exclude cuối và hai U/N đã áp. Tách 21 ảnh chưa rõ parent và V6-EX-003 U/U khỏi danh sách đề xuất supervision; không xóa quyết định audit, không ép nhãn. 1.283 crop còn lại vẫn phải kiểm quyền sử dụng theo từng record.

Với 21 ảnh/8 họ cảnh, xác minh nguồn bằng evidence có sẵn; nếu chưa xác minh được, giữ quarantine ngoài used package. Không đưa vào val/test chỉ dựa trên việc tách các ảnh mới cùng cảnh thành nhóm. Ảnh mới có liên hệ thị giác không đồng nghĩa recipe tạo ảnh hoặc quyền nguồn đã được xác minh. Đề xuất phạm vi local; không upload.

## 2. Chuẩn bị strict records và allocation để owner duyệt

Dùng codec `pilot_schema` và luồng `review_acceptance` được định tuyến trong docs/reference.md. Map geometry từ tọa độ crop vào source/derivation đúng schema, gắn evidence đúng SHA, giữ U là null/mask 0. Không chuyển audit JSON thành PilotRecord bằng parser permissive. Context/normal metadata chỉ kế thừa khi evidence còn phù hợp, không suy N/N thành confirmed_normal tự động.

Tạo bảng assignment tường minh theo 331 nhóm audit sau lọc eligibility, kèm thống kê nhãn và delta so với parent. Không random resplit, không đặt quota hoặc tỷ lệ train/val/test từ suy đoán. Mọi quan hệ nguồn và augmentation giữ cùng ranh giới. Nhóm lớn nhất cần rà evidence nối trước allocation để tránh coi liên kết bắc cầu quá rộng là cùng một session thực tế.

Tách quyết định development evaluation khỏi independent holdout: test cũ đã được mở audit; SCB-write-015 bị loại là thay đổi owner yêu cầu, không mutate test V12. Không mở prediction/test metrics để chọn split.

Owner duyệt bảng membership đủ eligibility, assignment/version, quyền dùng và protocol test cụ thể trước xuất release. Approval audit hiện tại không được thay thế các quyết định này.

## 3. Export vào đường dẫn version mới

Tái dùng `pilot_package.build_pilot_package(records, output_dir, source_roots, crop_inputs, selection_rows, metadata, expected_sample_ids)`. Output phải mới; giữ V12 bất biến. Không dùng script release lịch sử chỉ bằng cách đổi tên version.

Package gồm ledger/used manifest, source/derivation/provenance, selection, assignment, policy revision, coverage/delta, release metadata/approval, checksums và test freeze phù hợp. Payload crop chỉ chứa ID được duyệt dùng trong release; không mang ảnh bị loại hoặc các bản thay thế cũ vào used payload. Quarantine giữ ngoài package supervision.

## 4. Checks và nghiệm thu

Strict schema/usage/rights/evidence, exact ID inventory và bytes, decode/geometry, null/masks, cross-split group/source leakage, deterministic export/rebuild theo scope; đối chiếu V12 parent pin và test delta. Kiểm near-duplicate lại khi pixels/membership/group thay đổi có ảnh hưởng, không coi zero hash duplicate là đủ.

Chỉ cập nhật pointer/card sang release mới sau checks và owner acceptance đúng package/version. Không tự train/smoke/downstream sau release. Giữ inputs/evidence được report dẫn tới; dọn preview/cache dư theo storage policy sau khi đã bảo toàn kết quả.
