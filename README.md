# AI Exam Monitoring

Nghiên cứu/demo hành vi quan sát được trong video phòng thi: person detector → context crop → classifier multi-label → tracking/events → human review. Không định danh sinh viên hoặc tự kết luận kỷ luật.

- [Trạng thái dự án](docs/status.md): capability, input và công việc đang xem xét.
- [Đọc theo task](docs/00-INDEX.md): contracts, implementation reference và hồ sơ cần chọn.
- [System spec](docs/system.md), [data contract](docs/data.md), [training contract](docs/training.md): yêu cầu có hiệu lực.
- [Development](docs/development.md): setup/checks/workflow; [operations](docs/operations.md): restore/backup khi cần; [storage](docs/storage.md): lưu trữ và retention.
- [Reports](artifacts/reports/README.md): nghiên cứu, releases, kết quả/evidence; [experiments](configs/experiments/README.md): config/proposal/approval.

Agent bắt đầu với AGENTS/index/TASK, không đọc mọi report/archive. Results thuộc hồ sơ theo đối tượng; spec chỉ đổi khi contract đổi. Git lưu source/config/metadata nhỏ; data/model/media theo DVC/storage đúng quyền, pointer không là binary backup.

## Chạy web trên laptop GPU

Baseline hiện tại: upload MP4 có receipt → B0 CUDA FP32 batch 1 → ảnh phân tích/bbox
và hai hành vi → pause/resume/seek/stop. AI lấy mẫu 1 Hz; màn hình nhận các frame đã
phân tích qua MJPEG, không phải video gốc 25–30 FPS hoặc bản phân tích mọi frame.
Tracking/events online và camera chưa tích hợp; `/review` giữ pipeline offline riêng.

Máy đã kiểm: Dell G15 5511, i5-11400H, RAM 16 GB, RTX 3050 Laptop 4 GB, Windows 11.
Dùng Python 3.11.9 và môi trường CUDA đã chạy B0: Torch 2.8.0+cu128,
Torchvision 0.23.0+cu128, Ultralytics 8.3.221, OpenCV 4.11.0.86, NumPy 2.4.6,
Pillow 12.3.0. Không cài requirements CPU hoặc extra ML tổng quát đè môi trường này.

Sau khi clone/pull bản có các thay đổi này, mở PowerShell tại root repo. Lần đầu,
cần gói `video-web.zip` đã bàn giao để lấy model ngoài Git; không giải nén gói đè repo:

```powershell
$python = 'D:\ky 7 ptit\PTHTTM\AI-Exam-Monitoring\.venv\Scripts\python.exe'
$video = Read-Host 'Duong dan day du den MP4'
$deadline = Read-Host 'Han xoa goc, yyyy-MM-ddTHH:mm:ss+07:00'
.\RUN.ps1 -Python $python -Artifacts 'D:\duong-dan\video-web.zip' `
  -Source $video -DeleteBy $deadline -ConfirmSourceRights -NotTestOrHoldout
```

`RUN.ps1` dùng source của repo hiện tại, khôi phục **chỉ input còn thiếu** theo
[manifest](configs/web/LAPTOP-VIDEO-20261108/inputs.json), từ chối file đã có nhưng
khác checksum, kiểm GPU/packages, chỉ cài web-only dependencies nếu thiếu, tạo
receipt rồi mở web. Model không tự tải từ Internet; Git/DVC chưa cung cấp remote
đã xác minh cho bộ model này. Gói cũ vẫn dùng được để lấy đúng model theo manifest.

Những lần sau bỏ `-Artifacts` nếu input vẫn đầy đủ. Vào **http://127.0.0.1:8765**,
chọn MP4 và receipt JSON launcher vừa in, tải lên rồi bấm **Bắt đầu**. Receipt giữ
deadline gốc tối đa 7 ngày, đúng quyền local QA và không test/holdout. Không gia hạn
video cũ bằng receipt mới. Ctrl+C dừng server; launcher khôi phục môi trường shell.

CLI `python -m ai_exam_monitoring.web --workspace .` mặc định chọn
`configs/web/LAPTOP-VIDEO-20261108/web.yaml`; cần package/source của repo hiện tại
trong môi trường Python. `RUN.ps1` đã thiết lập đường dẫn này. Đường CPU cũ chỉ
chọn tường minh bằng `--config configs/web/review.yaml` với môi trường CPU phù hợp;
không có fallback GPU → CPU tự động.

### Phát triển AI tiếp

Training vẫn độc lập với web. Profile hiện tại chỉ xác nhận B0 và phiên bản code
suy luận đã đo. Sửa các file numerical dùng chung với training có thể làm profile
B0 từ chối chạy; không sửa hash hoặc bỏ guards để vượt kiểm tra. Model E mới phải
đi cùng checkpoint/config/calibration và profile tích hợp phù hợp; không ghi đè
`best.pt` hoặc coi việc đổi tên file là đã tích hợp model. Thêm hành vi/đổi kiến trúc
cần cập nhật adapter/UI tương ứng, không thuộc baseline này.

[Quyết định gốc](configs/web/LAPTOP-VIDEO-20261108/README.md) và execution/runtime
pins giữ nguyên; hướng dẫn chạy từ repo hiện hành ở mục này. Web GPU toàn luồng
vẫn cần xác nhận trên laptop thật; software tests không thay xác nhận đó.

## Bố cục

| Nơi | Trách nhiệm |
|---|---|
| src / tests / requirements | Logic tái dùng, regression fixtures, môi trường |
| configs | Variables/proposal/approval theo identity |
| docs | Contracts, hướng dẫn và status hiện hành |
| data/raw / interim / processed | Nguồn / chuẩn bị-review / package versioned; metadata cũ không bảo đảm package đầy đủ |
| outputs | Model, run artifacts, gallery và scratch |
| artifacts/reports | Evidence/kết quả theo source, release, run; không chạy script lịch sử như workflow mặc định |
| archive | Binary backup/nguồn và registry; Git chỉ giữ metadata |

[Lưu trữ hiện hành](docs/storage.md) quy định giữ/nghỉ lưu; [availability](artifacts/reports/storage-retention-20261016/availability.json) chỉ rõ payload còn sẵn. Source layout không đổi sau cleanup; chưa có kho ảnh chung hoặc cleanup tự động định kỳ.
