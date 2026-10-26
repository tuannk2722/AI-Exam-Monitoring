# Đối chứng duplicate sau review — Draft, chưa chạy

Inputs: D2 và [owner review r2](../../../artifacts/reports/runtime-clip-qa-20261025/owner-review-20261026-r2.json). C01/C02 same-person đã xác nhận; không thay winner/config/pins cũ. Giữ mọi person diagnostic, role unknown.

## Câu hỏi phải giải quyết

1. Hai box có thật sự cùng người? Hai case đã xác nhận không đủ suy rằng mọi box overlap là duplicate.
2. Nếu cùng người, giữ crop nào đủ evidence thuộc anchor? C01 crop rộng chứa phone hàng xóm; score cao không là tiêu chí chọn crop.
3. Có làm mất người thật bị che nhau không? Cần nhóm đối chứng khác người, không chỉ hai cặp lỗi.

## Thiết kế đề xuất

Giữ D2 làm baseline. Chuẩn bị bảng overlap/containment trên float boxes của 19 frame đã có, chỉ để shortlist; không sửa detections hoặc coi threshold hình học là ground truth. Bổ sung review nhóm khác người bị che từ source và các candidate trước, owner xác nhận nhóm/bảo toàn evidence. Không cần gọi detector hoặc classifier để lập bảng này.

Chỉ sau khi có cohort quan hệ same/different/unknown, so sánh một candidate xử lý duplicate hữu hạn với D2. Candidate cần chốt riêng điều kiện đề xuất cặp, điều kiện từ chối suppression khi unknown, và cách chọn box/crop; không tự largest-box/highest-score, không dùng score hành vi làm evidence ownership. Numerical variables chưa chốt: không executable hoặc run approval trong tài liệu này.

Tiêu chí đề xuất: giải quyết duplicate đã xác nhận, không làm mất người khác đã review, giữ đầu/tay/bàn và evidence thuộc anchor; unknown không tính thành thành công. Nếu hình học không phân biệt được hai người bị che và hai box cùng người, ghi giới hạn và xét detector/refinement khác trong thiết kế riêng, không hạ threshold tiếp để vừa hai case.

Attribution và visibility là nhánh riêng: C03 phone U không là FN; looking N ở giây 56 là FP đã review; C05 giây 59 có đầu nhưng không đủ evidence nên U/U, không là detector false positive. Không dùng rule suppression để che lỗi classifier hoặc tự filter người sát camera ngoài policy được duyệt.

Sau đối chứng và crop QA mới xem xét session tích hợp D2/revision trên clip với receipt absolute deadline, rồi thiết kế tracker/events. Chưa chạy video mới, train, model A1 hoặc downstream từ proposal này.
