# Scope owner duyệt ngày 16/10/2026

Owner approve báo cáo E004-accepted-coverage-20261016 và các bước tiếp, yêu cầu thực hiện tới hoàn thành. Giữ 345 crop accepted, ưu tiên train, giữ selection 71 và các tập evaluation cũ; chuẩn hóa geometry/lineage, đóng package mới và chuẩn bị experiment chỉ thay dữ liệu.

Sau phát hiện 168 crop không phải native ROI, owner chọn: **“Giữ bytes accepted; duyệt mở rộng contract crop dẫn xuất (đề xuất)”**. Cho phép mở rộng schema/exporter/loader để ghi rõ crop dẫn xuất đã duyệt, pin frame/ROI/crop và kiểm integrity; không nới kiểm native.

Implementation dùng `pilot-b-manifest-v2` với `CropDerivation` tùy chọn; V1 đọc/ghi giữ nguyên payload. Derivative đã import không được tuyên bố biết chính xác recipe nén/resize upstream. Phải có SHA source, RGB SHA của ROI native, kích thước/format output, review gắn SHA crop và evidence ref. Export yêu cầu exact bytes input, không dựng lại derivative từ recipe phỏng đoán. Loader kiểm SHA và kích thước/format.

Approval này không xác nhận các person boxes chưa được đề xuất, không biến parent video ID thành room/person độc lập, không mở test/reserve cho visual review hoặc inference. Run recipe/config chưa có identity cụ thể vẫn cần hoàn thiện trước bước duyệt/chạy theo báo cáo đã approve.
