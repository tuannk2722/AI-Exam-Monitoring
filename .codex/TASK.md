# CI-FIX-20261105 — Sửa hai job CI của commit runtime

- Trạng thái: hoàn tất bản sửa và kiểm tra local; owner đã yêu cầu commit và push branch `feat/live-monitoring-demo`.

## Yêu cầu và hiện trạng
- Baseline `cbff0f4d7fbe9deb204460734dcf56140ca83183`, working tree ban đầu sạch; đã fetch origin.
- Đã đọc AGENTS, index, status, development, template và TASK cũ; đối chiếu workflow, dependencies, producer/consumer runtime và campaign cùng tests liên quan.
- `quality` chỉ cài base/dev nhưng import frame processor đi qua `person.RuntimeConfig` tới training artifacts và Torch. `classifier-tests` chạy mypy trên Ubuntu, nơi `ctypes.windll` không tồn tại trong typeshed.

## Quyết định và inputs
- User đã cho phép sửa lỗi CI, commit và push branch hiện tại. Giữ các nhóm dependency và gate CI hiện có.
- `RuntimeConfig` trong `person.py` chỉ dùng làm annotation; đặt trong `TYPE_CHECKING` đã có để fixtures không kéo dependency ML.
- Campaign dùng `sys.platform == "win32"` cho hai lời gọi Windows API để mypy nhận diện đúng platform; giữ nguyên flags và logic thực thi.
- Không train, load weights hoặc dùng media thật; không sửa dataset, model, pins, receipts hay approvals lịch sử.

## Outputs và vòng đời
- Giữ code sửa, regression test và TASK; không tạo report/spec mới.
- Môi trường base và cache mypy tạm ở `outputs/_scratch/ci-fix-20261105`; đã thử dọn bằng PowerShell sau khi xác minh target nằm trong workspace và không có file tracked, nhưng automatic approval review chặn lệnh với lý do `blocked by policy`. Giữ nguyên scratch, không thử cách khác để vượt policy; scratch bị Git ignore và không đưa vào commit.

## Contract impact và checks
- Không đổi contract — không sửa spec/status/index.
- Tái hiện base thiếu Torch; kiểm fixtures runtime/timing, campaign, full synthetic suite, Ruff, strict mypy cho Windows và Linux, compile trong RAM, checker `--require-git`, diff và staged diff.
- Software PASS không thay nghiệm thu model, dữ liệu hoặc GPU.

## Checkpoint và bàn giao
- Đã tái hiện chính xác hai lỗi trước sửa: base suite 354 tests lỗi import tại hai module; mypy Linux báo hai lỗi `windll`.
- Bản sửa: chuyển import annotation của `RuntimeConfig` vào `TYPE_CHECKING`; dùng guard platform được mypy hiểu cho Windows API; thêm regression subprocess chặn import Torch, torchvision, Ultralytics và OpenCV cho frame/live primitives.
- Sau sửa: base/dev mới cài, không Torch: 378 tests PASS, 212 skip; full suite có classifier/runtime/web: 383 tests PASS, 2 browser opt-in skip. Không chạy media/model thật.
- Strict mypy với `--platform linux` và `--platform win32`: PASS, 92 source files mỗi lần; Ruff trên cả môi trường hiện có và base mới cài PASS; compile 150 Python files trong RAM PASS; checker `--require-git` và diff PASS.
- Bàn giao bằng commit chỉ gồm TASK, hai module và regression test. Giữ workflow/dependencies hiện có; trạng thái push và CI từ xa tra commit/PR trên GitHub, không suy PASS từ kết quả local.
