# Runtime V8S + G0 — 26/10/2026

Owner chấp nhận V8S có lỗi và duyệt tích hợp/crop QA. [Decision](decision.json), [selection](selection.json), [runtime](runtime.yaml), [authorization](runtime-authorization.json). Revision v4 chỉ cho V8S với policy đã chạy: 640/conf0,25/IoU0,30/CPU FP32/rect=true/batch1/no augment. Không sửa D2 history, không suppression hoặc đổi role unknown.

Checkpoint receipt tái dùng acquisition chính thức V8S, xác minh taxonomy thực tế trước ghi receipt. Guard v4 kiểm exact policy/weights/winner và pins decision/evidence. G0 seed20261023/checkpoint/calibration/context-v1 giữ nguyên. Đây là lựa chọn prototype có lỗi accepted, không thắng thống kê V10S hoặc nghiệm thu mọi video.

## Crop/G0 QA

[crop-review.yaml](crop-review.yaml) và [approval](crop-review-authorization.json) pin 19 source frame, comparison completed và 364 V8S detections. Không có exact cached match geometry/confidence; 364 G0 forwards, không detector rerun. Reusable selected_crop_review v2 nhận comparison JSON và runtime config, v1/D2 giữ behavior; kiểm deadline trước model/output và sau kết thúc. Output phân biệt cached/new, crop/input SHA, scores/flags, source identity/environment. [Gallery kết quả](../../../outputs/runtime-v8s-crop-review-20261026/index.html).

Owner review hành vi/attribution là bước riêng. Không truyền labels D2 sang V8S chỉ từ IoU; cùng frame có thể khác target/context. Duplicate giữ nguyên theo acceptance, không lấy max scores hoặc tự loại một crop. Source/crop/input mới phải kiểm đúng người trước session QA.

## Session tích hợp — hoàn tất

Session tích hợp local đã chạy trên clip đã được phép, sampling 1Hz như runtime.yaml (60 source samples theo session trước), V8S → context-v1 → G0. Đây là regression/integration QA trên clip quen thuộc, **không test độc lập hoặc confirmation tổng quát**. Không tăng lên mọi frame 30FPS, không mở clip mới hoặc tracking. Receipt mới đã pin source và parent_session, absolute deadline giữ 01/11/2026 15:55 Việt Nam. Đã thực hiện sau owner nghiệm thu batch G0; acceptance không tự mở rộng sang mọi video.

Nếu cần confirmation tổng quát về sau, phải chọn clip/đoạn khác phù hợp và protocol trước khi xem đầu ra; không gọi 19 frame hoặc clip đã dùng chọn model là holdout mới. Chưa train/tune thresholds hoặc đổi model từ batch này.

## Kết quả thực hiện

Lượt crop/G0 completed: 364 forwards mới, 0 cached, 19 frame; 735 checksum PASS. [Report](../../../artifacts/reports/runtime-clip-qa-20261025/v8s-g0-20261026.md), [batch 10 case / 17 crop](../../../outputs/runtime-v8s-behavior-review-20261026/index.html). Owner đã nghiệm thu batch không có case cần chỉnh sửa; [receipt](../../../artifacts/reports/runtime-clip-qa-20261025/v8s-behavior-acceptance-20261026.json). Session 1 Hz đã hoàn tất, [media receipt kế thừa](session-media-approval.json); không đổi deadline.

[Session r2 / audit / bàn giao](../../../artifacts/reports/runtime-clip-qa-20261025/v8s-session-20261026.md): 60/60 samples, 1.162 observations; 772 hashes PASS, 19 frame tham chiếu không đổi flags. Lượt đầu interrupted do global thread override, r2 thay thế sau sửa classifier thread guard.

## Chốt stage

Owner đã review và yêu cầu đóng stage: [quyết định nghiệm thu cuối](../../../artifacts/reports/runtime-clip-qa-20261025/stage-acceptance-20261026.json). Trạng thái Accepted / Complete trong scope clip hiện tại. Phần chờ nghiệm thu trong snapshot run/report cũ được quyết định này thay thế về trạng thái stage; không sửa bytes artifact đã pin hoặc suy nhãn từng crop. Không còn bước chạy/review bắt buộc của stage này.
