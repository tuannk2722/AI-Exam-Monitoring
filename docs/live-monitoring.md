# Demo giám sát trực tiếp — LIVE-DEMO-FOUNDATION-20261027

## Phạm vi và thẩm quyền

Owner yêu cầu ngày 27/10/2026: chuyển trọng tâm sang camera có detection trên hình
và log bên cạnh; video upload cũng phát và phân tích trong phiên; review chỉ cần
mở bằng chứng và quyết định nhanh. Giữ light/dark. Owner đã xác nhận dùng **iPhone**
và **có thể mượn máy GPU NVIDIA**; model máy/OS chưa chốt. Đợt này chỉ sửa spec
và bộ khung, phần cứng và adapter cụ thể vẫn là đề xuất.

Hướng sản phẩm này thay riêng yêu cầu recorded-only/review-first của ADR-001 và
WEB-REVIEW-20261027. Bản Web Review tại commit `996c52c` là baseline chạy được;
không xóa workflow đọc artifacts cũ. Approval model, tracking, events và quyền
media lịch sử giữ nguyên phạm vi, không tự trở thành acceptance live.

## Approval của owner — 28/10/2026

Owner đã review và xác nhận trong hội thoại: **“tôi đã review và approve thay đổi”**,
sau đó yêu cầu chốt approval, cleanup và commit. Thiết kế và bộ khung hiện tại
được **Accepted ở cấp thiết kế**: monitoring là màn hình chính; bbox đúng frame;
log đủ temporal support và review nhanh; buffer giới hạn/epoch reset; MJPEG + SSE
và POST cho bản local đầu; stable log ID/evidence revision trong SQLite riêng;
hướng iPhone/USB/Camo nếu máy Windows và GPU NVIDIA mượn chạy local.

Không hỏi lại các phương án đã duyệt ở trên. Các từ “đề xuất” bên dưới ghi lại
thiết kế được duyệt, không còn là yêu cầu chờ duyệt lại. Approval này chưa là
config chạy, wire schema hoặc migration SQLite đã materialize; numeric values
chưa được nêu vẫn cần thiết kế cụ thể. Model máy/GPU/OS, sampling jitter/tolerance,
gap/reset thresholds, SLA và receipt/retention camera còn mở. Chưa có nghiệm thu
hiệu năng/chất lượng live hoặc quyền thu nhận media mới từ approval thiết kế.

Primitives nội bộ không mở camera, gọi model hoặc thay artifacts đã pin. Không
cần triển khai auth phức tạp, risk score, nhiều camera hoặc hệ thống nghiệp vụ mới.

### Cụ thể hóa timing — 28/10/2026

Owner tiếp tục duyệt [LIVE-TIMING-20261028](../configs/tracking/LIVE-TIMING-20261028/README.md)
cho implementation và fixtures: slot detector 100 ms, frame đầu tại/sau mốc lệch
tối đa 50 ms, G0 mỗi 10 slot; slot detector thiếu reset continuity/tracker, slot G0
thiếu ngắt segment. Candidate cần ≥ 3 positives ở slot liên tiếp và span timestamp
thật ≥ 2.000 ms; pause/resume reset continuity. Approval này thay riêng trạng thái
numeric jitter/gap/reset còn mở trong phần thiết kế ban đầu bên dưới. Không tự
gán acceptance C10 cho stream mới. Camera receipt, wire/evidence persistence và
profile/SLA máy thật còn cần slice tích hợp; không hỏi lại policy đã duyệt.

Đối chiếu code và nguồn chính thức ngày 27–28/10/2026. Tài liệu ban đầu trong
Downloads là input thiết kế UI cũ; yêu cầu mới của owner có ưu tiên khi khác nhau.

## Những điểm code hiện tại cần thay đúng chỗ

| Thành phần | Hiện tại và hệ quả | Hướng tái sử dụng |
|---|---|---|
| `inference/video.py` | `RecordedVideo` cần FPS/frame count hữu hạn; kiểm timestamp file | Giữ nguyên cho offline; adapter camera riêng, không giả video vô hạn là file |
| `inference/runtime.py` | Decode toàn file lấy timestamps rồi decode lượt hai để predict; session seal ở cuối | Tách xử lý một frame dùng chung; live không gọi nguyên `run_video` |
| `inference/detector.py`, `person.py` | V8S và context crop có geometry/config guards | Tái dùng geometry và model pins; không đổi detector hoặc crop policy |
| `inference/classifier.py` | G0 CPU, một crop mỗi lần, `.cpu().float()` | Adapter device/batch có identity mới và kiểm parity trước dùng GPU; sửa YAML không đủ |
| `inference/tracking.py`, `tracking_cadence.py` | C10 chạy chuỗi 10 Hz; ByteTrack đếm update | Online tracker cần clock/gap policy riêng; bỏ frame tùy ý không còn tương đương C10 |
| `inference/events.py` | Aggregate arrays đã hoàn tất; 3 positives tại 1 Hz, span 2 giây, missing phá chuỗi | Incremental accumulator phải đối chiếu offline trên cùng observations, không nới rule |
| `web/pipeline.py` | Worker hoàn tất runtime rồi decode tracking, aggregate ở cuối | Session runner từng bước, một nguồn đang chạy, stop/cancel và lỗi rõ |
| `web/catalog.py`, `store.py` | Catalog phiên sealed; review gắn SHA events cuối | Adapter đọc phiên cũ; log live cần ID ổn định và revision bằng chứng riêng |
| `web/assets/*`, `app.py` | Ba màn hình hub/workbench/summary; local paths, chưa upload bytes/live API | Một màn hình giám sát chính; routes cũ giữ cho artifacts lịch sử |

Evidence hiệu năng: `outputs/runtime-v8s-session-20261026-r2/session.json` ghi mean
8 117 ms và p95 9 667 ms **mỗi sampled frame**, tức khoảng 8,1 và 9,7 giây; 60
samples, tổng khoảng 525 giây. Đây là runtime CPU offline bao gồm xử lý nhiều
người và ghi QA/artifacts, không phải benchmark riêng kernel/model hay GPU.
Không dùng số này để suy GPU đạt bao nhiêu FPS, nhưng đường hiện tại không đáp
ứng 1 mẫu/giây khi chạy tuần tự theo thời gian thực.

## Camera điện thoại và phần cứng đề xuất

1. Với máy mượn chạy Windows, ưu tiên thử **iPhone → USB → Camo Studio → camera
   thiết bị local → backend AI**. Tài liệu nhà cung cấp hỗ trợ iPhone qua USB
   trên Windows/macOS và có bản miễn phí. Cần kiểm giới hạn bản miễn phí, output
   resolution/FPS thực và khả năng OpenCV mở virtual camera trên đúng máy;
   chưa cài phần mềm hoặc coi tương thích là đã PASS.
   [Camo getting started](https://camo.com/support/camo/camo-getting-started).
2. Continuity Camera chính thức của Apple là đường **iPhone → Mac**; không lấy
   đó làm giải pháp cho máy Windows/NVIDIA. Nếu máy mượn là Mac phải đề xuất
   compute adapter khác, không gọi đó là CUDA. Các phương án Pixel USB/Windows
   Connected Camera Android đã nghiên cứu không áp dụng cho iPhone của owner.
   [Apple Continuity Camera](https://support.apple.com/en-au/102546).
3. IP camera/RTSP từ iPhone là adapter sau, cần biết ứng dụng/URL/quyền dùng.
   Không mặc định cài app hay đưa credentials vào log. Trình duyệt trên điện thoại
   phát camera sang PC bằng WebRTC là phương án khác, cần signaling và kết nối;
   `getUserMedia` cần secure context. `http://IP-LAN-của-PC` không hưởng ngoại lệ
   localhost của điện thoại. Chưa mở LAN/HTTPS/WebRTC trong đợt bộ khung này.
   [MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).

Đề xuất compute: ưu tiên **máy mượn có GPU NVIDIA chạy local**, chạy
cùng máy với backend và UI, giữ V8S/G0. Chưa đề xuất mua model GPU cụ thể hoặc
cam kết VRAM/FPS khi chưa đo số người/resolution. CPU là đường kiểm chức năng và
fallback có thông báo xử lý chậm; không gọi CPU hiện tại là demo real-time đã đạt.
Colab vẫn phục vụ nghiên cứu theo scope cũ; không chọn relay camera qua Colab
cho demo local. Không thêm cloud dependency hoặc tự upload media.

Trước chốt máy: profile decode, detector, crop, classifier theo số người, tracking,
encode và UI; báo startup, p50/p95 capture-to-result, samples/giây thực đạt,
dropped frames, RAM/VRAM. Đo trên clip có quyền và cấu hình mới, giữ checkpoint,
preprocessing, thresholds; thử batching cùng frame trước đổi model. Numeric SLA,
device, batch size và sampling profile phải chốt từ evidence; không tự đặt đạt.

## Màn hình đích

```text
Nguồn: Camera / Video tải lên     Bắt đầu / Dừng     Trạng thái     Light/Dark
┌──────────────────────────────────────────┬─────────────────────────────┐
│                                          │ Log phiên — mới nhất trước │
│  Video + bbox + tên hành vi trên người   │ 10:42 · #7 · Dùng điện thoại│
│                                          │ 10:40 · #3 · Nhìn quanh     │
│  AI đang chạy / xử lý chậm / mất nguồn   │ Bộ lọc: tất cả / chưa duyệt │
└──────────────────────────────────────────┴─────────────────────────────┘
Click log → bằng chứng đúng người/thời điểm → Xác nhận / Bỏ qua / Chưa rõ
```

Video là phần lớn diện tích; trạng thái nguồn và AI luôn thấy. Drawer bằng chứng
không dừng camera, không bắt reviewer chọn hàng chục tùy chọn. Thời điểm, hành vi,
track tạm và trạng thái review đủ cho mỗi dòng. Ghi chú tùy chọn. Thông tin model,
pins, confidence, metrics và export ở phần chi tiết mở khi cần. Không thêm risk
để xếp người; dùng thời gian và trạng thái chưa duyệt. Bbox mang nhãn hành vi,
không ghi người gian lận; xác nhận là quyết định người review về bằng chứng.
Màu bbox, chữ, drawer, trạng thái và focus keyboard phải đọc rõ ở cả light/dark;
không dựa chỉ vào màu để phân biệt.

## Luồng xử lý và đồng bộ

```text
Camera device / file được phép
  → source adapter → frame stamp → bounded latest-frame buffer
  → detector + tracker → context crops → G0 → incremental events
  → exact-frame annotated image                  → log + evidence snapshots
  → preview transport                           → metadata stream + SQLite
```

Đề xuất bản local đầu: backend capture một nguồn, frame có bbox được render cùng
ảnh ở server rồi stream MJPEG; SSE chuyển trạng thái/log, POST gửi start/stop/review.
FastAPI `StreamingResponse` là primitive gửi iterator, không tự xử lý camera,
inference hay đồng bộ. SSE là một chiều và phù hợp log; event ID/reconnect cần
server replay hoặc snapshot khi cursor hết hạn. WebSocket không tự giải quyết
backpressure. Đây là lựa chọn đơn giản cho một viewer, chưa thêm WebRTC.
[FastAPI](https://fastapi.tiangolo.com/advanced/custom-response/),
[MDN SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events),
[MDN WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket).

- Mỗi frame có session, source epoch, sequence, source time, capture monotonic
  time và geometry. File dùng media time; camera chưa có PTS đáng tin thì dùng
  elapsed monotonic từ capture, không gọi đó là thời điểm sensor phơi sáng.
  UTC chỉ dùng hiển thị/audit. Không trừ clock máy điện thoại với clock PC.
- Overlay chỉ ghép kết quả với **đúng frame/geometry/epoch**, không lấy bbox cũ
  vẽ lên ảnh mới vì cùng track ID. Khung đã phân tích có thể hiển thị trễ, phải
  ghi tuổi kết quả. Preview sạch có thể chạy nhanh hơn nhưng không có bbox cũ.
  Bản đầu chưa lan truyền nhãn qua các frame chưa phân loại; nếu cần phải có
  policy TTL/tracker riêng được review. FPS ảnh và tần suất phân tích báo riêng.
- Live ưu tiên frame mới: một pending frame, frame mới thay pending cũ khi AI
  bận, đếm dropped. Frame đang inference không bị thay. Không xếp video vô hạn
  trong RAM; subscriber chậm cũng phải có buffer giới hạn. Artifact log được
  lưu bền trước phát; không drop quyết định reviewer theo cơ chế drop preview.
- Tracker C10 cần cadence thật 10 Hz; classifier 1 Hz là nhánh khác, không buộc
  mọi detector frame đi qua G0. Nếu throughput thiếu, hiển thị degraded và gaps;
  không lặp cùng prediction cho đủ 3 positives. Không gọi cấu hình drop/irregular
  cadence là C10 Accepted. Chốt gap/reset policy bằng thiết kế online riêng.
- Disconnect/seek/đổi nguồn tạo epoch mới, reset tracker và chuỗi temporal;
  kết quả inference muộn thuộc epoch cũ bị loại khỏi hình/log đang chạy. Review
  lịch sử vẫn truy được bằng chứng cũ. UI refresh chỉ reconnect, không mở camera
  thứ hai; Stop giải phóng capture, ngừng nhận frame, chốt pending events và
  trạng thái phiên theo lý do stop/error, không tự restart vô hạn.
- Lifecycle đề xuất: idle → starting → running → stopping → stopped/completed;
  failed có lỗi cụ thể. File có paused, seek và EOF; pause không tạo positives.
  Pending command cần idempotent theo session; chưa mở job queue phân tán.

Runner đề xuất tách capture, detector/tracker và classifier thành các bước có
buffer giới hạn riêng; không để G0 chậm chặn mọi update detector/tracker. Detector
gắn track vào snapshot frame trước khi gửi crop sang G0; kết quả giữ nguyên
snapshot đó. Không tra lại track ID ở thời điểm G0 trả về để thay anchor. GPU
execution có thể vẫn phải serialize/batch tùy profiling, không mặc định nhiều
thread làm inference nhanh hơn. Preview annotated của bản đầu chạy theo kết quả
đã phân tích; muốn hình có bbox mượt hơn cần đo trước hoặc thiết kế propagation
riêng, không tự reuse label cũ.

Ultralytics phân biệt `stream=True` trả generator với `stream_buffer=False` bỏ
frame cũ để tránh tăng trễ; không có cờ nào bảo đảm pipeline đạt real-time.
OpenCV hỗ trợ thiết bị/file/IP stream nhưng backend và buffering phải kiểm trên
máy demo. Tài liệu latest dùng để nghiên cứu cơ chế, **không nâng dependency
Ultralytics 8.3.221 đã pin** chỉ để khớp ví dụ mới.
[Ultralytics predict](https://docs.ultralytics.com/modes/predict/),
[OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html).

## Video upload

Upload hoàn tất/kiểm input trước bắt đầu session; không đợi AI xử lý cả video.
Adapter đọc một lượt và phát theo media clock, dùng pipeline online giống camera.
Khi AI chậm có hai hành vi cần tách rõ: chế độ demo theo thời gian thực bỏ frame
và báo gaps; chế độ phân tích đầy đủ chạy chậm theo AI, không quảng bá real-time.
Đề xuất demo là mặc định, offline hiện hữu giữ vai trò phân tích đầy đủ.
Pause/seek điều khiển nguồn server, không để `<video>` chạy clock độc lập khỏi
backend rồi ghép bbox theo thời gian nhận HTTP. Seek mở epoch mới, không nối event
qua điểm tua. Log phân biệt đoạn đã xem/phân tích với đoạn bị bỏ qua.
File giữ checksum nguồn và quyền/deadline như hiện tại; camera không có SHA cả
file từ đầu nên cần receipt cấp phiên và hash cho từng bằng chứng được lưu.

## Log và review đơn giản

Đề xuất hai mức có tên rõ: nhãn **quan sát tức thời** từ prediction vượt threshold
đã pin; **ca cần xem lại** khi đủ temporal rule. Quan sát đầu tiên có thể hiện trên
bbox ngay khi có kết quả; không tự là temporal event hoặc confirmed. Log mặc định
hiển thị ca đủ rule, cập nhật cùng một dòng khi chuỗi kéo dài, không spam mỗi frame.
Một-frame observation vẫn xem được qua diagnostic tùy chọn. Owner đã duyệt
semantics hai mức này ở cấp thiết kế; không đổi rule đã Accepted.

Incremental rule giữ 3 positives liên tiếp tại 1 Hz/span ≥ 2 giây, không bridge
negative/unknown/missing/null; phát candidate ngay khi đủ hỗ trợ thay vì chờ EOF,
sau đó update/close. Track+behavior+epoch+segment xác định một ca; tách theo target,
không gộp khác người/epoch hoặc dùng mean score thành risk. Lifecycle open/closed
tách review candidate/confirmed/dismissed/uncertain. Kết quả muộn xử lý theo thứ tự
source, không arrival time; khi mất mẫu phải kết thúc segment rõ ràng.

Rule offline hiện kiểm spacing đúng 1 000 ms. Camera có jitter nên lấy “frame mới
nhất mỗi giây” chưa bảo đảm thỏa rule. Cần policy online có version cho sampling
slots, timestamp gốc, tolerance và missing trước thực thi. Chưa chốt tolerance
mới hoặc làm tròn timestamp để vượt validator; parity offline chỉ có nghĩa khi
input/cadence thật sự giống nhau. Đây là quyết định kỹ thuật còn mở cùng gap/reset,
không phải yêu cầu owner tự thiết kế lại temporal logic.

SQLite riêng tiếp tục là lựa chọn owner đã duyệt. Đề xuất log live dùng stable ID
và evidence revision, không lấy SHA file events đang đổi làm primary identity.
Review gắn snapshot bằng chứng mà người duyệt thực sự xem; evidence mới không
âm thầm kế thừa confirmed cho phần chưa xem. Drawer giữ snapshot trong lúc đọc,
báo có bằng chứng mới; log có thể yêu cầu xem lại revision mới. Export/seal cuối
phiên có manifest/hash riêng. Adapter legacy tiếp tục đọc `event-human-review-v1`;
chưa migrate hoặc sửa SQLite hiện hữu trong đợt này.

Bằng chứng tối thiểu đề xuất là frames hỗ trợ + crop đúng người + source time/
geometry/model/rule refs; không mặc định ghi toàn bộ camera hoặc audio. Clip ngắn
là tùy chọn sau khi chốt ring buffer, dung lượng và retention. Cần receipt camera
riêng trước capture/lưu người thật; không tái sử dụng quyền clip cũ. UI demo chỉ
cần bước xác nhận quyền/deadline gọn, không xây hệ thống tài khoản phức tạp.

## Bộ khung đã thêm và bước triển khai

`inference/streaming.py` cung cấp nội bộ `FrameStamp`, `StreamFrame`,
`LatestFrameBuffer` và `can_overlay`: identity/clock/geometry, một pending frame,
drop counters, explicit epoch reset và guard đúng frame/độ cũ. Không có web import,
I/O camera, dependency mới hoặc schema persistence. Chưa nối vào worker cũ;
chưa tuyên bố có live detection. Buffer không thay source scheduler, subscriber
hub hay incremental tracker/event logic. File adapter đầy đủ dùng queue/backpressure
riêng, không dùng latest buffer nếu cần giữ mọi mẫu.

| Bước | Đầu ra có thể review | Điều kiện hoàn tất |
|---|---|---|
| 1 — hiện tại | Spec đích, nghiên cứu, primitives và tests synthetic | Diff/checks đúng scope; không ảnh hưởng offline |
| 2 | Chốt adapter điện thoại, compute, policy gaps/log và media live; config mới | Owner review phương án, biết thiết bị; giữ original pins |
| 3 | Frame processor dùng chung, device/batch adapter, capture/file runner | Parity CPU/GPU trên input được phép; profile toàn pipeline, không train |
| 4 | Incremental tracker/events, stable log/evidence revisions, transport | Fixture parity offline/online; drop/seek/reconnect/late results và reconnect log |
| 5 | Màn hình monitor + log/drawer, upload, light/dark | E2E camera thật và file, stop/review/reload/EOF; báo latency thực và giới hạn |

Inputs còn thiếu trước bước chạy thật: model iPhone/iOS và model máy/GPU/OS.
Đường webcam local, bbox đúng frame + log đủ temporal rule và revision review
đã được duyệt ở cấp thiết kế; chỉ chọn nguồn IP thay thế nếu adapter thực tế cần.
Policy online phải cụ thể hóa jitter/gap/reset và retention/receipt camera trước
thực thi liên quan. GPU local chưa là quyền mua phần cứng hoặc run mới. Không
yêu cầu owner tự thiết kế logic; triển khai theo thiết kế đã duyệt, chỉ hỏi phần
chưa xác định có ảnh hưởng contract/scope.
