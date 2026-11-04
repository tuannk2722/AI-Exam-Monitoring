# QA 1 Hz toàn clip — 25/10/2026

**Hoàn tất kỹ thuật; chưa nghiệm thu chất lượng detector/crop/video.** Owner duyệt tiếp đề xuất 1 Hz sau báo cáo partial. Một lượt chạy theo [config mới](../../../configs/runtime/RUNTIME-CLIP-1HZ-20261025/README.md), giữ G0, calibration, detector và context-v1. Không train, tune hoặc chạy lại full-frame.

## Kết quả và bằng chứng

| Nội dung | Kết quả |
|---|---|
| Session | completed, CLI exit 0 |
| Sampling | 60 frame tại 0–59 giây; index nguồn 0, 30, …, 1.770; preflight toàn 1.800 frame |
| Observations | 1.280; 18–26 detections/frame, không là số người duy nhất |
| Gallery | 19 frame phân bố toàn clip, 400 crops |
| Thời gian CLI | 399,39 giây ≈ 6 phút 39 giây |
| Runtime elapsed / startup | 387,72 / 18,07 giây |
| Frame processing mean / p50 / p95 | 5,775 / 5,474 / 8,177 giây |
| Peak RSS process | 514.650.112 bytes ≈ 490,8 MiB |
| Integrity | 844 session files khớp checksum; frame indices/time/geometry/scores/flags PASS |
| Đối chiếu partial | 15 frame chung giống hệt toàn bộ frame record, gồm boxes/scores/flags |

Máy local Intel Core i7-1255U, RAM vật lý khoảng 7,73 GiB; Python/OS/packages và code identity ghi trong session. CPU FP32, classifier 4 threads/batch 1. Một lượt, không warm-up riêng. Frame processing gồm detector/classifier/JSONL/gallery I/O, không gồm decode từ iterator; elapsed không bao trọn khởi động CLI/checksum cuối. Sampling giảm số inference, không làm mỗi inference nhanh hơn và chưa đạt xử lý clip theo thời gian thực.

Cờ phone 329, looking 357, đồng thời 71 trên 1.280 observations. Đây là cờ model, không là ground truth, người duy nhất hoặc event. Không tính precision/recall từ counts này; 1 Hz có thể bỏ sót hành vi giữa các mốc.

- [Gallery runtime source → boxes → crop → input](../../../outputs/runtime-clip-1hz-20261025/session/index.html).
- [Tổng quan 19 frame](../../../outputs/runtime-clip-1hz-20261025/review/source-overview.jpg), [audit](../../../outputs/runtime-clip-1hz-20261025/review/audit.json), [script audit](../../../outputs/runtime-clip-1hz-20261025/audit.py).
- [Phân tích box trùng trên cached partial](../../../outputs/runtime-clip-1hz-20261025/duplicate-case-analysis.json), [execution](../../../outputs/runtime-clip-1hz-20261025/execution.json).
- [Receipt media](../../../outputs/runtime-clip-1hz-20261025/media-approval.json) kế thừa quyền clip owner đã cấp, gắn runtime ID mới; không upload hoặc sửa raw. Giữ local đến deadline 01/11/2026 lúc 15:55 giờ Việt Nam hoặc xóa sớm theo yêu cầu; không tự xóa nguồn ngoài workspace.

## Review detector/crop và classifier

Đã xem 19 contact sheets chứa toàn bộ 400 crops và overview source/boxes, gồm đoạn 30–40 giây chưa có trong partial. Đây là triage, chưa phải 400 nhãn accepted; các case dưới đây để owner review batch và ngoại lệ.

| Case | Quan sát và ý nghĩa |
|---|---|
| Frame 690, a016/a017 | Hai crop cùng người bên phải; phone score khoảng 0,174 và 0,927. Crop rộng chứa tay/thiết bị của người đội mũ phía trước. Cần review attribution; không được mặc định phone trong crop thuộc anchor |
| Frame 480, a009/a010 | Cùng người phía sau mặc áo trắng, phone khoảng 0,161/0,640; hai crop nhìn thấy thiết bị cầm tay nhưng khác context/scale. Lỗi nhạy crop tiếp tục xuất hiện ngoài đoạn partial |
| Frame 1380, a004/a015 | Box/crop trùng cùng người cầm điện thoại phía trước; phone đều cao, looking khoảng 0,364/0,400 lại nằm hai phía ngưỡng. Không nên tạo hai event cho một người |
| Frame 1170 a001; frame 1770 a000 | Người đi gần camera chỉ còn phần đầu lớn trong crop; thiếu ngữ cảnh bài làm. Classifier vẫn phát score nhưng score không chứng minh đủ quan sát |
| Frame 1080 a000 | Người đi qua phòng có looking score khoảng 0,816. Detector person không phân biệt vai trò; chưa có policy xác định người nào thuộc phạm vi giám sát. Không tự gán đây là học sinh hoặc giám thị |
| Frame 1680 a002; frame 1770 a005 | Có vật dạng điện thoại trong tay người đội mũ nhưng phone khoảng 0,012/0,010; draft nghi bỏ sót cần owner xác nhận |

Một số phone rõ ở phía trước được gắn cờ ổn định; điều đó không giải quyết lỗi attribution/box trùng hoặc looking thiếu context. Không có tracking nên anchor IDs chỉ dùng trong frame; chưa đo missed persons hoặc xác nhận mọi người đều được phát hiện.

## Giải thích box trùng và hướng tiếp theo

Cached partial cho thấy nhiều box nhỏ gần như nằm trọn trong box lớn: intersection/diện tích box nhỏ khoảng 0,96–1,00 nhưng IoU chỉ 0,385–0,652 ở nhiều cặp. Với NMS IoU hiện tại 0,7, tồn tại đồng thời các box này là điều có thể giải thích; chưa phải chứng cứ adapter bỏ qua NMS. Một số cặp tính từ tọa độ integer xấp xỉ 0,70; không kết luận từ rounding rằng NMS sai. Không áp threshold mới hoặc tự xóa box overlap vì người khác bị che cũng có thể overlap mạnh.

**Ưu tiên tiếp theo là đối chứng detector/duplicate handling và chốt crop attribution, chưa mở tracking/events.** Chuẩn bị thiết kế đối chứng trên cohort đã review với hai loại case: box trùng cùng người và hai người thật bị che nhau. Giữ model/ngưỡng/crop khi thử detector để tách nguyên nhân; owner chốt biến NMS/conf hoặc quy tắc suppression và tiêu chí bảo toàn người bị che trước run mới. Cần chốt thêm phạm vi đối tượng khi có người di chuyển; không tự thêm bộ phân loại vai trò.

Không đề nghị train lại classifier hoặc giảm ngưỡng từ lượt QA này. Kết quả 1 Hz đủ mở rộng evidence theo thời gian, chưa chứng minh chất lượng toàn video/recall hành vi ngắn. Lượt partial và config/protocol cũ giữ nguyên bytes; báo cáo này là companion riêng.
