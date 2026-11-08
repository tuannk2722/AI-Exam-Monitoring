# LAPTOP-VIDEO-20261108 — Upload video và phân tích AI trên laptop

Phạm vi đã chốt theo yêu cầu owner ngày 08/11/2026: chạy web local trên laptop
mượn, upload MP4, phát video có bbox và hai hành vi E009, pause/resume/seek/stop.
Giữ model/ngưỡng/preprocessing hiện hành. Không camera, tracking/events online,
SQLite evidence/review live, training hoặc thay đổi hành vi.

## Setup và cấu hình

- Dell G15 5511, i5-11400H, RAM 16 GB, RTX 3050 Laptop GPU 4 GB, Windows 11.
- Python 3.11.9; Torch 2.8.0+cu128, Torchvision 0.23.0+cu128; dùng môi trường CUDA
  đã chạy thành công lượt B0. Ultralytics 8.3.221, OpenCV 4.11.0.86, NumPy 2.4.6,
  Pillow 12.3.0 giữ nguyên. Không cài classifier-cpu.txt lên môi trường này.
- B0, V8S/context-v1, CUDA `cuda:0`, FP32, **batch 1**, sampling **1 Hz**. Batch 1
  nhanh nhất trong ma trận đã đo tại `outputs/verify-b0-01`; giữ checkpoints,
  calibration và runtime E009 đã pin, không tự đổi precision hoặc CPU fallback.
- Web tại **http://127.0.0.1:8765**, JPEG 85, transport 250 ms, MP4 tối đa 512 MiB.
  Video không hợp lệ, quá hạn, đổi checksum hoặc không đủ quyền bị từ chối.
- `execution.json` pin parity/profile/code của lượt GPU và quyết định này.
  Đây là lựa chọn chạy web từ evidence đã có, không đặt numerical tolerance mới
  hoặc suy benchmark tuần tự thành SLA/quality acceptance.

## Chạy trên laptop

Giải nén `video-web.zip` vào thư mục mới, riêng khỏi repository đang dùng. Bên
trong có `RUN.ps1`, `src`, `configs`, `requirements` và model dependencies.
Mở PowerShell tại thư mục giải nén, dùng Python CUDA cũ:

```powershell
$python = 'D:\ky 7 ptit\PTHTTM\AI-Exam-Monitoring\.venv\Scripts\python.exe'
$video = Read-Host 'Duong dan day du den MP4'
$deadline = Read-Host 'Han xoa goc, yyyy-MM-ddTHH:mm:ss+07:00'
.\RUN.ps1 -Python $python -Source $video -DeleteBy $deadline `
  -ConfirmSourceRights -NotTestOrHoldout
```

Launcher kiểm đúng GPU/packages, cài đúng web-only dependencies nếu thiếu bằng
`--no-deps` (không cài Torch), tạo receipt local và in đường dẫn JSON, rồi mở
server. Vào địa chỉ trên, chọn **MP4 và receipt JSON vừa in**, tải lên, bấm
**Bắt đầu**. Model B0 được khóa trong phiên. Dừng server bằng Ctrl+C; launcher
khôi phục cwd/PYTHONPATH/PYTHONDONTWRITEBYTECODE khi kết thúc.

Nguồn phải có quyền local QA, không test/holdout, còn deadline gốc tối đa 7 ngày.
Có thể dùng lại video của lượt GPU khi quyền vẫn còn hiệu lực; không đổi deadline
để gia hạn nguồn cũ. Không ghi toàn bộ observations thành log sự kiện hoặc kết luận
gian lận. `/review` giữ workflow offline có sẵn, ngoài phạm vi lượt chạy này.

## Kiểm chứng và giới hạn

GPU đã chạy B0, parity 5 frame/90 crop không đổi flags; các batch 1/2/4 đều
completed. Profile batch 1: mean 932 ms, p95 985 ms/frame với 18–19 bbox/frame.
Code numerical phải khớp source đo; transport web có tests riêng. Máy development
CPU chỉ kiểm được phần mềm, package và guards; xác nhận upload/phát bằng GPU thật
cần mở gói này trên laptop. Chưa công bố tốc độ/chất lượng web ngoài các số đo đó.
