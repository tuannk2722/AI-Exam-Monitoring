# Runtime D2 — 26/10/2026

Owner đã review toàn bộ 19 frame, xác nhận D2 không mất người/không crop trùng và chọn D2 winner. [Decision](../RUNTIME-DETECTOR-REVIEW-20261025/d2-winner-decision-20261026.md) và [receipt selection](winner.json) giữ phạm vi visual cohort và pins bằng chứng; không tự tạo metrics hoặc sửa matching draft lịch sử.

[Runtime mới](runtime.yaml) dùng schema `recorded-runtime-config-v3`, NMS IoU **0,30**, confidence **0,25**; còn lại giữ detector weights/package, context-v1, G0/preprocessing/calibration và sampling 1 Hz. [Authorization](runtime-authorization.json) gắn digest exact config. V1/V2 vẫn chỉ nhận detector cũ; V3 bắt buộc pin receipt selection D2 khớp weights/policy. Không sửa runtime D0 đã pin.

[Config crop review](crop-review.yaml) và [authorization](crop-review-authorization.json) thực hiện bước tiếp theo sau detector: dùng 342 anchors D2, tái dùng 340 prediction baseline chỉ sau exact geometry/confidence và crop/input SHA + pixel checks; hai crop đổi geometry ở frame 1080/1170 chạy G0. Đây là kết quả kết hợp cached/new có provenance, không gọi là 342 forward mới hoặc full-video rerun. Không chạy lại detector, không đổi threshold/model hoặc mở tracking/events.

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.inference.selected_crop_review --config configs/runtime/RUNTIME-D2-20261026/crop-review.yaml --output outputs/runtime-d2-crop-review-20261026
```

Command trên thuộc một run đã cấp identity; không chạy lại nếu output đã tồn tại. Xem [hồ sơ kết quả](../../../artifacts/reports/runtime-clip-qa-20261025/detector-stage-a-20261026.md). Gallery giữ deadline nguồn 01/11/2026 lúc 15:55 giờ Việt Nam. Runtime config mới sẵn dùng qua CLI hiện có với media receipt đúng runtime ID; không tự cấp quyền clip khác hoặc kéo dài retention của clip này.

Detector winner không thay nghiệm thu hành vi/attribution của classifier hoặc chất lượng mọi video. Role vẫn unknown, không tự xác định thí sinh/giám thị từ hình ảnh.
