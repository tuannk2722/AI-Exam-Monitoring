# RUNTIME-CLIP-1HZ-20261025 — QA 1 Hz

Owner duyệt “approve, thực hiện tiếp đi!” ngày 25/10/2026 sau đề xuất QA 1 Hz trên toàn clip và review detector/crop. Accepted cho config sampling và một lượt local QA; chưa là acceptance nhãn/crop/video hoặc numerical quality gate.

Kế thừa [prototype](../RUNTIME-PROTOTYPE-20261025/runtime.yaml), chỉ đổi identity/approval/schema v2 và `sampling_hz: 1`. G0 seed 20261023, calibration, detector/context-v1 và CPU giữ nguyên. [Authorization](owner-authorization.json) pin digest [runtime.yaml](runtime.yaml). Quyền clip từ hội thoại trước giữ hiệu lực, receipt mới gắn runtime ID và exact source SHA ở outputs local. Không công khai đường dẫn riêng tư hoặc media.

Mục tiêu: 60 frame lấy mẫu theo timestamp gốc trên clip 60 giây, gallery 19 frame đều theo thời gian; dùng lại [protocol QA](../RUNTIME-QA-PREP-20261025/README.md) và [findings partial](../../../artifacts/reports/runtime-clip-qa-20261025/README.md). Tập trung duplicate boxes, attribution, crop nhạy score và che khuất ở phần sau clip. Review mọi contact sheet gallery, phóng lớn case cần thiết; nhãn nhận xét là draft để owner nghiệm thu batch.

Không sửa hoặc tái chạy session partial; không tự thay NMS/padding/thresholds, không training/test/tracking/events. Sampling có thể bỏ qua hành vi giữa các mốc, không chứng minh precision/recall toàn video hoặc realtime. Media chỉ local owner, không upload, retention tối đa 7 ngày. Output mới ở `outputs/runtime-clip-1hz-20261025/session`; companion kết quả ở hồ sơ runtime clip sau khi run kết thúc.
