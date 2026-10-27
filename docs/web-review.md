# Web Review local

Ứng dụng gồm sảnh phiên, bàn duyệt và tổng kết; đọc kết quả AI thật. Chạy tại
máy owner, theo [scope được duyệt](../configs/web/README.md). Không có dịch vụ cloud.

## Chạy ứng dụng

Từ thư mục repository, dùng môi trường runtime hiện có:

```powershell
.venv/Scripts/python.exe -m pip install -e ".[web]"
.venv/Scripts/python.exe -m ai_exam_monitoring.web
```

Mở **http://127.0.0.1:8765**. Có thể dùng `--port 8767` hoặc `--workspace <repo>`.
Phần xử lý video cần dependencies/model runtime đã có của dự án; web extra
không tải model. Config UI ở [review.yaml](../configs/web/review.yaml).

## Duyệt phiên đã có

1. Chọn **Mở bàn duyệt** tại phiên events completed. App kiểm SHA các artifacts
   đọc và ghép chính xác frame/time/anchor/person box với tracking.
2. Lọc candidate theo hành vi/trạng thái, tìm ID/track/ghi chú, sắp xếp thời gian,
   span hoặc mean classifier. Tab riêng cho chuỗi ngắn và tracks.
3. Chọn event, bấm timeline/filmstrip hoặc bước qua mẫu để xem nguồn, context
   crop có person box và input RGB letterbox. 10 Hz chỉ có detector/tracker tại
   các frame trung gian; không nội suy điểm G0.
4. Chọn Xác nhận, Bác bỏ FP hoặc Chưa rõ; thêm lý do/ghi chú và đánh dấu ngoại lệ.
   Tự lưu SQLite; **Lưu & tiếp theo** chờ lưu thành công trước chuyển candidate.
5. Tổng kết hiển thị thống kê quyết định và accounting thật. Xuất JSON để bàn
   giao/khôi phục hoặc Markdown để đọc. JSON khác SHA phiên bị từ chối; nhập
   cùng SHA cần xác nhận thay bản review trong UI.

Phím tắt và semantics có trong nút **?**. Phím tắt tạm ngưng trong trường nhập
liệu/hộp thoại. Theme lưu trên trình duyệt; màu trạng thái thích ứng light/dark.
Hai nhãn có thể cùng dương, không phải bài toán softmax.

## Video mới

Nhập đường dẫn MP4 local và receipt JSON được duyệt. Nút preflight kiểm file,
model pins, source SHA, quyền media, deadline và FPS hợp lệ với C10. UI hiện
kích thước/thời lượng đo được; không tự đặt quota/SLA chưa được owner chốt.
Receipt dùng schema `runtime-media-approval-v1/v2` của runtime, phải có deadline
tuyệt đối còn hiệu lực và không gia hạn nguồn cũ. Không tự sinh consent.

**Xử lý & tạo phiên** xếp job vào hàng đợi local một worker. Trạng thái
queued/running/completed/failed và số mẫu thực đã ghi được polling từ server.
Lỗi không bị coi là completed; khởi động lại server đánh dấu job dở là
ServerInterrupted, không resume hoặc đổi config âm thầm. Không đóng server
khi còn xử lý nếu muốn hoàn tất job.

Pipeline tạo runtime, tracking và events mới dưới `outputs/web-review/job-*`.
Nguồn video kết nối trong bộ nhớ của server; sau khởi động lại dùng **Kết nối
video** nếu cần frame không có ảnh tĩnh. Chỉ nhận video khớp SHA nguồn.

## Review persistence và media

- `outputs/web-review/reviews.sqlite3` giữ bản review hiện hành, khóa theo
  `events_sha256`; revision chặn ghi đè từ tab dùng bản cũ. Khi xung đột, tải lại
  phiên trước sửa tiếp. Không dùng SQLite để sửa `events.jsonl` hoặc acceptance.
- JSON `event-human-review-v1`: `events_sha256`, `revision`, `decisions` keyed
  event ID, `summary`, `disposition`, `updated_at`. Mỗi decision gồm `status`,
  `note`, `reasons`, `flagged`. `uncertain` thuộc lớp review riêng, không đổi
  dataclass BehaviorEvent. Disposition cấp phiên không xác nhận từng event.
- Ảnh tĩnh đọc từ runtime/cadence theo checksum. Khi thiếu, giải mã đúng frame
  từ video nguồn đã kiểm SHA; crop/input dùng geometry và preprocessing đã pin.
  Không thay ảnh của frame khác. Không có nguồn thì báo thiếu evidence.
- Server kiểm deadline từng lần cấp ảnh; browser xóa ảnh khi hết hạn. Metadata
  và provenance vẫn đọc được. Khóa xem không tự xóa bytes: owner vẫn thực hiện
  retention/deletion media theo receipt. Không gia hạn media vì mở UI.
- Risk hiển thị chưa mở; mean classifier không là xác suất gian lận.

## Kiểm tra phần mềm

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_web_review.py' -v
.venv/Scripts/python.exe -m ruff check src/ai_exam_monitoring/web tests/test_web*.py
.venv/Scripts/python.exe -m mypy src/ai_exam_monitoring/web
node --check src/ai_exam_monitoring/web/assets/app.js
```

Browser integration tùy chọn dùng Chrome đã cài và package `playwright`, chạy
server fixture local riêng, không ghi quyết định vào phiên thật:

```powershell
.venv/Scripts/python.exe -m pip install playwright
$env:RUN_WEB_BROWSER_TESTS = '1'
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_web_browser.py' -v
```

Software checks không thay owner acceptance video mới, độ chính xác classifier,
fragmentation C10 hoặc benchmark phần cứng. Không chạy lại model chỉ để kiểm UI.
