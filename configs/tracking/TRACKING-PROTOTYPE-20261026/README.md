# TRACKING-PROTOTYPE-20261026 — Benchmark tracking trên output V8S

Trạng thái: **Draft, cần chốt thiết kế trước implementation/run**. Owner đã yêu cầu làm riêng tracking sau V8S trong hội thoại ngày 26/10/2026. Đây là authorization về scope công việc, chưa phải chọn ByteTrack hoặc nghiệm thu các variables/metrics dưới đây. Không mở temporal events, risk hoặc web.

## 1. Inputs và phát hiện đã xác minh

- Parent: `outputs/runtime-v8s-session-20261026-r2`; stage Accepted / Complete theo [receipt](../../../artifacts/reports/runtime-clip-qa-20261025/stage-acceptance-20261026.json).
- [Preflight](preflight.json) pin session, predictions và runtime-config; ba SHA256 khớp checksums của session. 60 samples cách nhau đúng 1.000 ms, 1.162 observations, 19 source frames đã lưu để QA. Preflight chỉ đọc metadata, không chạy tracker/model.
- Confidence detector nhỏ nhất 0,2501247; không có box dưới 0,25; 395 observations dưới 0,5. Output đã qua detector threshold/NMS và person box đã được làm tròn pixel. Đây là replay trên output runtime, không tái lập raw detector tensors.
- Model/crop/ngưỡng hành vi giữ nguyên theo [runtime V8S](../../runtime/RUNTIME-V8S-20261026/README.md). Track dùng `person_box` và detector confidence, không dùng context box hoặc behavior scores để nối người.
- Môi trường có Ultralytics 8.3.221, NumPy 2.4.6, SciPy 1.17.1, Torch 2.8.0+cpu; chưa có `lap`. Module matching của Ultralytics có nhánh tự cài lap lúc import: adapter phải preflight dependency và tắt auto-install trước import. Đề xuất pin `lap==0.5.12` và ghi environment receipt khi triển khai; nếu cài không khả thi thì dừng arm này, không silent thay solver.

## 2. Thiết kế đề xuất

Replay cả 60 samples cho mỗi arm trong [proposal.yaml](proposal.yaml), trên CPU local, không gọi detector/classifier. Không sweep hoặc tự tune sau khi xem kết quả. Mỗi arm có tracker instance/ID space riêng; reset mỗi session, không dùng ID ngoài session và không suy role/danh tính.

| Arm | Mục đích | Variables đề xuất |
|---|---|---|
| N0 | No-tracking baseline theo FR-TRK-01 | Mỗi anchor có một ID riêng, không nối qua frame; chỉ là đối chứng benchmark |
| B0 | ByteTrack với ngưỡng mặc định trên input hiện có | high/new 0,25; low 0,10; match cost 0,80; fuse score true |
| B1 | Kiểm nhánh association điểm thấp trong phạm vi detections đã lưu | high/new 0,50; low 0,25; match cost 0,80; fuse score true |

Cả B0/B1 dùng Ultralytics BYTETracker 8.3.221, `frame_rate=1`, `track_buffer=60`, cho `max_time_lost=2` update theo công thức upstream. Đây là tham số benchmark được đề xuất, không là chất lượng Accepted. Adapter gọi một update cho mỗi sample, kể cả frame không detection. Giữ `frame_index` nguồn và `video_time_ms` riêng; không đưa frame nguồn 0/30/60 vào bộ đếm update. Cần test chính xác ranh giới lost/reactivation/removal theo implementation; không hứa cutoff cứng 2 giây vì thứ tự association/expiry upstream.

B0 không có detections trong dải low của ByteTrack; B1 có thể sử dụng 395 detections ở dải [0,25; 0,50). B1 không khôi phục box dưới 0,25 hoặc các frame chưa sample. Không gọi replay này là đánh giá đầy đủ ByteTrack ở 30 FPS. Nếu cả hai không phù hợp, trình kết quả để quyết định sampling/detector run mới riêng.

## 3. Output và adapter

Đề xuất output riêng `outputs/tracking-prototype-20261026/<arm-id>/`, không ghi vào parent. Mỗi arm có session outcome, config/environment/code/input pins, checksums, assignments JSONL và summary. Schema mới chỉ materialize sau duyệt; không đổi `recorded-observations-v1` hoặc dataclass cũ để chứa payload đặc thù.

Mỗi assignment giữ parent session SHA, frame index/time, anchor ID gốc, track ID hoặc null, và lý do chưa được tracker xuất. Mỗi input anchor phải có đúng một assignment; track ID không trùng giữa hai anchors trong cùng frame. Kiểm index mapping trả về của upstream, không tự nối output với input bằng thứ tự hoặc IoU. Giữ box gốc; box Kalman nếu xuất phải là field riêng. Không tạo behavior prediction cho lost/predicted-only track; không copy scores qua frame thiếu detection.

Không sửa/xóa duplicate input hoặc gộp behavior scores. ByteTrack có quản lý duplicate track nội bộ; observation không được trả về vẫn phải được giữ với assignment null, không biến mất khỏi sổ đối soát. N0 là baseline thực, không là fallback production khi ByteTrack lỗi.

## 4. Benchmark và review đề xuất

### Software gate trước replay

Fixtures cho mapping/permutation, empty frames, một người ổn định, xuất hiện muộn, gap/expiry, reset session, invalid timestamps/geometry, input mutation, failed outcome, retention deadline và dependency không tự cài. Kiểm toàn vẹn parent và output coverage. Smoke synthetic trước real-output replay; không gọi synthetic PASS là nghiệm thu chất lượng.

### Evidence review

Tạo gallery/timeline local cho đủ 60 samples, ba arms cạnh nhau, kèm shortlist track bắt đầu/kết thúc, gap, đổi association và overlap cần kiểm. 19 source frames có sẵn không đủ chứng minh continuity toàn 60 samples: lấy thêm đúng source frames cần từ clip gốc bằng decoder hiện có, kiểm source SHA và deadline trước/sau; không inference mới. Nếu không tìm được source hợp lệ thì dừng phần media review, báo phần thiếu, không giả ảnh hoặc suy quality.

Agent tự draft nhóm người tạm thời và shortlist, owner review batch/ngoại lệ, không yêu cầu owner annotate từng ảnh hoặc người thứ hai. Track output chỉ là đề xuất association, không tự thành ground truth. Người review có thể đánh dấu uncertain; không ép identity qua occlusion không rõ. Giữ review evidence riêng với frame/anchor refs và scope coverage; nếu chỉ review một phần thì báo metrics đúng phần đó.

### Định nghĩa phép đo cần owner duyệt

- Technical coverage: số input observations có assignment / 1.162; số null, track starts/ends, gaps và track lengths. Không gọi các số này là ID switch hoặc accuracy.
- ID switch: trên chuỗi anchors của cùng người tạm thời đã được review, ID được gán khác ID được gán trước đó trong cùng đoạn identity rõ; một interval uncertain ngắt đoạn đánh giá. Báo numerator và số transition có thể đánh giá.
- Fragmentation: số lần chuyển từ assigned sang ít nhất một sample không assigned rồi trở lại assigned trong cùng đoạn người vẫn nhìn thấy, đã review. Bắt đầu/kết thúc clip hoặc uncertain không tự tính fragmentation.
- Detection loss: người được review là nhìn thấy nhưng không có anchor tương ứng; association loss: có anchor đã review nhưng assignment null. Báo riêng số person-samples và mẫu số đã review, không nhập hai loại lỗi.
- Occlusion recovery: từng episode được review có cùng người rõ trước/sau occlusion; báo same ID / changed ID / no assignment; episode uncertain loại khỏi denominator và đếm riêng.
- Duplicate tracks và mixed-person tracks: ghi case cụ thể từ review; không đồng nhất track count với số người. Báo nguyên lỗi detector và lỗi association.
- Timing: replay-only elapsed/mean/p50/p95 update latency, startup riêng, hardware/environment, số samples; không dùng làm end-to-end FPS/SLA.

Đây là diagnostic development trên clip quen thuộc, không độc lập/holdout. Không tự đặt numerical PASS hoặc chọn winner chỉ vì ít tracks hơn. Sau bảng so sánh và batch review, owner chọn arm, yêu cầu sửa hoặc chưa chấp nhận; quyết định phải nêu giới hạn còn lại. Stage chỉ đóng sau receipt owner, không tự mở events.

## 5. Quyền, retention và thứ tự thực hiện

Theo scope tracking owner vừa yêu cầu, đề xuất dùng lại đúng clip/source đã được phép, local owner-only, không upload, deadline giữ 01/11/2026 15:55:06 Việt Nam. Receipt tracking mới phải dẫn parent rights/source SHA và không gia hạn; không mutate receipt V8S. Source/checkpoint/media không vào Git. Không train hoặc final test.

1. Owner chốt thiết kế replay N0/B0/B1, variables, metrics/review và dependency nêu trên.
2. Materialize config/authorization theo đúng quyết định; triển khai CLI tái dùng trong src, synthetic tests và preflight.
3. Replay đúng ba arms, tạo gallery/review batch và đối soát input/output, giữ parent bất biến.
4. Owner nghiệm thu batch/ngoại lệ; tính metrics trong coverage đã review; quyết định tracker và đóng stage hoặc ghi giới hạn cần xử lý.

## 6. Cơ sở kỹ thuật

- [ADR-008 original](../../../docs/decisions.md): Git `ab34b32:docs/decisions/ADR-008-tracking-strategy.md`, Proposed; benchmark với phương án khác hoặc no-tracking baseline.
- [BYTETracker upstream 8.3.221](https://github.com/ultralytics/ultralytics/blob/v8.3.221/ultralytics/trackers/byte_tracker.py): đối chiếu source đang cài cho update clock, buffer, association và output mapping.
- [ByteTrack paper](https://arxiv.org/abs/2110.06864): association với detections điểm thấp là phần cốt lõi; input replay đã lọc là giới hạn cần báo rõ.

Không sửa system spec khi draft này chưa làm thay đổi contract Accepted.
