# LIVE-VIDEO-WEB-20261028 — Adapter video online local

Trạng thái: **Accepted cho implementation**. Owner trả lời “Duyệt phương án này”
trong hội thoại ngày 28/10/2026, đúng phương án ở tài liệu này; không thay approval
thiết kế live ngày 28/10/2026. Runtime nền: commit `6f4cbe3`; CPU V8S/G0 và pins,
context-v1, thresholds giữ nguyên. Không camera/GPU hoặc temporal event rule mới.

Ngày 28/10/2026, owner review giao diện và xác nhận: “có thể chốt thiết kế và logic
như hiện tại”, sau đó yêu cầu cleanup và commit baseline. Acceptance này áp dụng
cho slice web/video đã triển khai; chưa là nghiệm thu model thật, hiệu năng GPU,
camera hoặc temporal log.

## Phương án triển khai

- `/` là màn hình giám sát video, `/review` giữ bàn review offline và API cũ.
- Một phiên upload/runner tại một thời điểm. Bắt đầu lại cần ID mới; refresh chỉ
  nối phiên hiện có. Không chạy offline job và online inference đồng thời.
- Chọn MP4 và receipt JSON đã duyệt. Receipt/hash/deadline được kiểm; không tự
  tạo consent từ checkbox. POST tạo upload, PUT truyền bytes có giới hạn, POST
  start khi checksum/decode metadata hợp lệ. Không multipart dependency mới.
- Đề xuất giới hạn upload **512 MiB**, receipt **64 KiB**; ghi từng chunk ra file,
  không giữ toàn video trong RAM. Tên local opaque, không lưu filename gốc.
  File lỗi/partial được xóa; file hoàn tất giữ đến khi xóa phiên hoặc deadline
  receipt, không gia hạn. Startup dọn partial/expired thuộc đúng root phiên mới.
- MJPEG giữ một ảnh annotated mới nhất; SSE gửi snapshot trạng thái đầy đủ khi
  nối/reconnect, không replay observations thành event. Cả hai gắn session/epoch;
  seek/stop vô hiệu ảnh cũ. Consumer chậm bỏ preview, không tăng queue vô hạn.
- POST điều khiển pause/resume/seek/stop; seek dùng source frame index và epoch
  như runner. Ảnh chỉ có bbox của chính frame; hiển thị source time, tuổi kết quả,
  samples xử lý và dropped. JPEG quality 85; cập nhật trạng thái mỗi 250 ms là
  tham số transport, không là cadence AI hoặc SLA.
- Quan sát tức thời hiển thị bên cạnh video. Khu vực log ghi rõ chưa bật temporal
  rule, không có nút xác nhận cho observations đơn lẻ. Không ghi observations
  vào bảng review legacy hoặc tự tạo candidate/confirmed.

## Contract local được duyệt

Config mới `online-video-web-config-v1` trong thư mục này chứa runtime path,
output root, upload/receipt limits, JPEG quality và nhịp transport; không sửa
`configs/web/review.yaml` hoặc runtime YAML đã pin.

API nằm dưới `/api/monitor`: `GET state`, `POST uploads`, `PUT uploads/{id}`,
`POST sessions/{id}/start`, `POST sessions/{id}/command`,
`GET sessions/{id}/preview`, `GET sessions/{id}/events`, `DELETE sessions/{id}`.
Client dùng ID opaque; server không nhận path output tùy ý. Lệnh gắn expected
epoch và command ID nguyên tăng dần để retry không tua hai lần. Retry lệnh cuối
cùng payload trả snapshot hiện hành; ID cũ hơn hoặc sai epoch trả conflict,
không replay lại side effect. SSE gửi snapshot đầy đủ, không dùng Last-Event-ID
để suy rằng đã replay một lịch sử log chưa tồn tại.

`online-video-web-session-v1` lưu metadata phiên riêng: ID, source/runtime/config/
receipt/code/environment pins, source frame count/FPS, deadline, status, thời điểm
bắt đầu/kết thúc, counts và lỗi theo loại (không private path). Trạng thái gồm
uploading/ready/starting/running/paused/stopping/stopped/completed/failed. Server
restart đánh dấu phiên đang chạy là failed/interrupted, không tự chạy model lại.
Không ghi ảnh/crop evidence hoặc toàn bộ predictions trong slice này; metadata
không phải output event, không đủ để review một hành vi sau phiên.
Metadata vận hành còn có thể đổi khi expiry/recovery, chưa là artifact AI đã
seal. `input_pins` giữ SHA các snapshot receipt/config/code/environment đã ghi;
receipt JSON được lưu thành snapshot nội dung, không tuyên bố byte-for-byte
giống cách định dạng file JSON gốc phía trình duyệt. Source SHA kiểm bytes MP4.

Config thực thi: [monitor.yaml](monitor.yaml). Khởi chạy bằng CLI web hiện có;
không phải chạy một server thứ hai. `state`/media guard ngừng phục vụ khi receipt
hết hạn; payload phiên hiện hành được dọn sau khi worker giải phóng, các payload
quá hạn khác được dọn lúc startup. Nếu server đã tắt, owner vẫn chịu trách nhiệm
dọn bytes local đúng deadline. Stop/EOF giữ bản upload để có thể kiểm metadata;
DELETE chỉ xóa các file thuộc adapter, không xóa thư mục có file ngoài scope.

## Điều kiện kiểm và giới hạn

Fixtures kiểm chunked upload/hash/expiry/limits, một phiên, reconnect, late result,
seek/stop/idempotency, partial cleanup và restart; browser synthetic light/dark.
Không chạy media người thật hoặc model thật để nghiệm thu từ tests phần mềm.
Tracker/events online, SQLite stable log revisions, camera receipt/device và GPU
parity/profile là phần riêng; numeric policy chưa được chốt không được tự điền.
