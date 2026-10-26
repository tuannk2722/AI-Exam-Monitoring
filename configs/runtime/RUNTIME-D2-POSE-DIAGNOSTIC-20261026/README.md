# D2 pose diagnostic — proposal cần quyết định

## Quyết định đề xuất

Duyệt một candidate YOLOv8n-pose pretrained COCO để diagnostic local đúng 19 source PNG đã pin, giữ D2/G0. Scope gồm tải weights chính thức, ghi SHA trước load, implementation riêng và synthetic tests, rồi một lượt tối đa 19 frame forwards trên CPU. Không train, đổi classifier, tự suppression hoặc tự mở video/tracking. Owner đã chấp nhận hướng license Ultralytics cho prototype trước đây; không hỏi lại lựa chọn license chung, nhưng checkpoint và variables pose mới chưa được duyệt.

[proposal.yaml](proposal.yaml) là snapshot đầy đủ để duyệt; status draft không phải config executable. Không lấy approval thiết kế trước làm approval cho model/variables mới.

## Vì sao chọn candidate này

Môi trường local đã có Ultralytics 8.3.221/Torch 2.8.0+cpu/OpenCV 4.11.0.86; [YOLOv8 docs](https://docs.ultralytics.com/models/yolov8/) liệt kê yolov8n-pose. [Pose docs](https://docs.ultralytics.com/tasks/pose/) mô tả keypoints và confidence. Đây là candidate tương thích họ công cụ đang dùng, không kết luận tốt nhất hoặc đã phân biệt đúng người bị che. Không upgrade dependencies hoặc chọn model theo benchmark không cùng camera.

[Release chính thức](https://github.com/ultralytics/assets/releases/tag/v8.3.0) có asset ID 195719300, size 6.832.633 bytes; GitHub API không cung cấp digest cho asset này. Chưa tải hoặc load weights. Khi được duyệt, tải exact URL, ghi SHA-256/source/final URL/size/package/license receipt trước inference; pin acquired bytes cho run và không silent đổi asset. License tham chiếu [Ultralytics](https://www.ultralytics.com/license), không thay license repo hoặc tự công khai dữ liệu/source.

## Thiết kế diagnostic hữu hạn

- Đầu vào: source PNG gốc của cohort 19 frame, không upscale crop rồi coi là source. Một forward/frame, RGB/PIL theo adapter; 960 px, square letterbox (rect=false), conf 0,25, pose NMS IoU 0,70, max_det 100, CPU float32, 4 threads, seed 20261026. Lý do 960: giả thuyết giữ thêm chi tiết người nhỏ; chưa chứng minh lợi ích. IoU pose 0,70 độc lập D2 0,30 nhằm quan sát pose instances, không thay detector D2.
- Lưu raw pose box và 17 keypoints/confidence trong tọa độ source, thiếu/nonfinite => unknown hoặc failed integrity; không tự điền điểm.
- Candidate support: điểm confidence >= 0,50; cần ít nhất 3/5 điểm đầu và cả hai vai. Tất cả điểm đầu đủ confidence cùng hai vai phải nằm trong float D2 box không padding. Box có đúng một pose support mới có assignment; 0 hoặc nhiều support => unknown. Rule này chỉ là giả thuyết diagnostic, không nhãn accepted.
- Với 259 cặp giao nhau: cùng unique pose => same_proposed; khác unique pose => different_proposed; còn lại unknown. Không gộp bắc cầu. Ghi toàn bộ support và ambiguity để review, không dùng nhãn accepted hoặc keeper làm input cho matcher.
- So riêng 8 cặp accepted, giữ 4 keeper làm reference. Không chọn crop tự động: pose không xác minh phone ownership hoặc mức đủ evidence hành vi. Trên người bị che/quay lưng, thiếu đầu/vai có thể dẫn tới nhiều unknown; đó là kết quả feasibility, không lý do tự hạ threshold.

## Acceptance và điểm dừng

Software: pin/deadline guard; tọa độ/keypoint-index tests, missing/multiple support => unknown, không dùng labels để matching, giữ originals. Real diagnostic: báo same/different/unknown từng cặp, số usable poses/support và thời gian thực đo. Tách wrong_same (nguy cơ mất người) với wrong_different/unresolved (duplicate còn lại). Không gọi unknown là thành công hoặc báo accuracy toàn video.

Mục tiêu feasibility trên reference: 4 same được đề xuất đúng, 4 different không bị same; unknown vẫn là chưa giải quyết. Dù đạt, chưa promotion: phải kiểm người ngoài shortlist và thiết kế keeper tự động trước suppression. Nếu thiếu đầu/vai hoặc mapping sai, báo không đủ evidence; không đổi model/imgsz/threshold để chạy lại trong scope này. Không mở test/train, không dùng scores G0 để sửa kết quả.

Quyền media local và deadline nguồn giữ nguyên, không upload ảnh. Kiểm còn hạn trước run; không gia hạn ngầm. Outputs có ID mới, pins/source identity/environment/status/checksums và gallery; không ghi đè audit/gallery cũ. Không có extra real smoke: kiểm load/schema trước, frame đầu là phần của 19-frame run; failure ghi failed, không silent rerun.

## Câu hỏi owner

Có duyệt đúng candidate và variables trong proposal.yaml, bao gồm acquisition, implementation/synthetic checks và một diagnostic 19 frame không? Nếu duyệt, agent làm trọn scope này và bàn giao kết quả; chỉ hỏi lại khi input/pins/license mâu thuẫn hoặc cần đổi variables/scope. Chưa xin nghiệm thu chất lượng hoặc quyền suppression.
