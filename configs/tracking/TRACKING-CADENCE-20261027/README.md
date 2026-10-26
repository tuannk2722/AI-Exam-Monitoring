# TRACKING-CADENCE-20261027 — Kiểm chứng nhịp detector/tracker

Owner yêu cầu thực hiện tiếp [research §6](../../../artifacts/reports/tracking-prototype-20261026/research-20261027/README.md), giữ ủy quyền agent quyết định kỹ thuật. Agent chọn thiết kế này trước inference, theo hướng cadence được ưu tiên; không ghi thành owner tự đặt các con số 5/10 Hz. [Authorization](owner-authorization.json) ghi đúng cơ sở và pin thiết kế/config.

## Giả thuyết và ma trận

Giả thuyết: 1 Hz bỏ qua chuyển động đi ngang giữa người ngồi và người đi qua, làm association bằng motion/IoU nối nhầm. Thêm detections trung gian có thể giữ trajectory đúng mà không đổi G0 hoặc thêm model appearance. Không bảo đảm cadence tự khắc phục occlusion/duplicate.

| Arm | Detections | Tracker | Classifier |
|---|---|---|---|
| B0 đối chứng | 60 parent samples đã pin | Output B0 cũ, không replay | Scores G0 cũ |
| C5 | 300 samples, 5 Hz | B0 policy, frame_rate 5, buffer 60 → lost 10 updates | Chỉ tham chiếu scores của 60 parent samples |
| C10 | 600 samples, 10 Hz | B0 policy, frame_rate 10, buffer 60 → lost 20 updates | Như C5 |

Một cache 10 Hz dùng lại 60 parent observations và chạy V8S đúng policy cho 540 samples còn lại. C5 lấy các samples cách 200 ms từ cùng cache. Không chạy classifier mới, không hạ detector threshold, không đổi NMS, weights, rect, precision, crop hoặc role unknown. Lưới là video time, không wall-clock throughput; nhịp 10 Hz không có nghĩa xử lý real-time.

`track_buffer=60` với `frame_rate` mới giữ khoảng thời gian lost tương đương parent. Giữ nguyên thứ tự association/expiry upstream; không suy cutoff thời gian cứng. Không thêm threshold gate/heuristic sửa ID. Cache ở frame parent giữ original observation nguyên trạng và provenance parent; intermediate observations chỉ person box/confidence/anchor, không scores/flags giả.

## Inputs, guards và outputs

Config pin runtime V8S, parent authorization và selection B0. Kiểm source SHA, media rights/deadline, model/package pins, parent outcome và prediction hashes trước và sau. Runtime config 1 Hz cũ không sửa; sampling mới thuộc cadence config. Dừng nếu source FPS/frames/timestamps hoặc 60 parent timestamps không khớp lưới, không silently resample.

Reusable CLI mới tạo output riêng, cache có completed/failed outcome, config/code/environment/input pins. Arms tái dùng tracker/assignment mapping đã kiểm. `person-cadence-v1` phân biệt cached parent và new detector; intermediate frame không có classifier evidence. `track-assignments-v1` giữ anchors và source index/time; projection xuống 60 samples phải exact anchor order/person box và trỏ parent predictions. Không thêm behavior prediction trong khoảng trống. Không sửa B0 output đã pin.

Mọi run có ID/status/checksums. Có lỗi thì giữ partial failed, không sửa config rồi resume vào output cũ. Ngân sách tối đa 540 detector forwards và hai tracker replays; chỉ synthetic smoke trước run, không extra model smoke. Không train, không tải weights, không cloud, không upload.

## Protocol trước khi xem kết quả

1. Software checks: cached/new routing, sampling 5/10 Hz, parent projection, high/low index mapping reuse, lost-clock conversion, invalid/missing frames, failed outcome, source/pin mutation và retention.
2. Kiểm đủ 600/300 frames và 540 new/60 cached, every-frame assignment accounting; so projection với parent 1.162 anchors. Coverage chỉ so trên 60 samples chung; không so trực tiếp track counts 600 với 60 như quality metric.
3. Known case: inspect toàn đoạn 7–11 giây, đặc biệt parent anchors `f00000240-a004` và `f00000270-a000`. Khác ID ở hai endpoint là check cần, chưa đủ: xem intermediate frames để bảo đảm không lẫn người rồi đổi ID, không che lỗi bằng null. Không yêu cầu ID số 10 giữ nguyên giữa arms.
4. Audit thêm đoạn 35–40 giây và các chuyển động tâm box lớn, cùng các chuỗi người confidence thấp/duplicate đã thấy ở nghiên cứu trước. Snapshot visual từ source đúng SHA; không đổi role hoặc suppress người di chuyển.
5. Chỉ chọn cadence làm baseline mới nếu known case được xử lý qua visual trace và không thấy regression rõ trong scope audit. Nếu C5/C10 tương đương, ưu tiên C5 để giảm detector compute. Nếu không đủ evidence hoặc còn mixed-person ID, giữ quality gate mở và đề xuất appearance riêng. Không tạo numerical quality threshold mới hoặc gọi diagnostic là holdout độc lập.

Agent thực hiện audit/decision theo ủy quyền hiện hành; không đẩy việc chọn thuật toán về owner. Chưa cấp acceptance tổng quát, events/risk/web. Các vùng chưa audit vẫn phải được báo rõ.

## Retention

Đúng clip local hiện có, source/rights từ parent. Giữ absolute deadline **01/11/2026 15:55:06 Việt Nam**, không gia hạn khi decode hoặc chạy lại. Source/models không vào Git; config/report metadata nhỏ giữ trong Git khi owner yêu cầu commit. Cache/review giữ trong outputs để truy vết; không dọn evidence trước deadline hoặc sửa pins cũ.
