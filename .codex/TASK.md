# LIVE-RUNTIME-20261028 — GPU/batching, profiling và timing online

- Trạng thái: hoàn tất slice phần mềm GPU/batching/profiling và timing/candidate fixtures; owner yêu cầu cleanup codebase và commit slice này trước khi sang bước tiếp. Chưa hoàn tất tích hợp camera/log hoặc nghiệm thu máy thật.

## Yêu cầu và hiện trạng
- Baseline web/video đã chốt và commit `2c9d8fa`; runtime nền `6f4cbe3`. Full suite 349 tests PASS (2 skip), browser riêng PASS, Ruff/mypy 85 files/staged checker PASS. Clean checkout `2c9d8fa`: checker và web suite 19 tests PASS (2 skip); checkout đã dọn. Không push.
- Cleanup source bỏ HTML/CSS tiêu đề đã ẩn, sửa test đúng UI owner review. Inventory 198 cache files / 49.495.030 bytes; lệnh xóa bị automatic approval review chặn `blocked by policy`, cache còn nguyên. Manifest tạm `exam-monitor-cache-cleanup-20261028.json` trong TEMP hệ điều hành. Không thử cách khác để vượt policy.
- Đã đối chiếu index/status/system/live/reference/development/storage; code classifier/person/frame_processor/online_video/runtime_config, model/preprocessing/encoder/device training, web monitor/transport; runtime V8S receipt/selection/approval và report session r2, E008 prototype decision; C10/event rule cho ranh giới downstream.
- Máy hiện tại Torch CPU, chưa có environment laptop mượn. Owner chốt tải demo: dưới 15 người, 5–10 phút; chuẩn bị kiểm tải 14 người / 10 phút, không gọi đây là capability đã đạt.

## Quyết định và inputs
- Tiếp tục theo hướng owner đã duyệt: giữ V8S/context-v1/G0, checkpoint/preprocessing/thresholds; thêm device/batch adapter và profiling, sau đó camera/log. Không train hoặc thay rule C10/events.
- API nội bộ execution/batch có tham số tường minh, FP32 trước; CUDA thiếu hoặc OOM phải fail, không âm thầm đổi batch/device. Receipt packages CPU cũ giữ exact guard; môi trường GPU phải có pin/authorization mới trước chạy thật.
- Không materialize config GPU được nghiệm thu hoặc chuyển web mặc định sang GPU khi chưa có parity/profile trên máy đích. Không chạy model/media thật trong task kiểm phần mềm.
- Owner duyệt tiếp LIVE-TIMING-20261028: “Duyệt policy để triển khai và kiểm bằng fixtures”. Detector slot 100 ms/tolerance 50 ms; G0 mỗi 10 slot, missing detector reset continuity, missing G0 ngắt segment, ≥ 3 positives/span thật ≥ 2 giây. Wire schema log/evidence camera và quyền media camera còn mở; không hỏi lại policy đã Accepted.

## Outputs và vòng đời
- Logic tái dùng ở inference; tests synthetic/temp tự dọn; hướng dẫn compute/protocol đúng ID ở configs/runtime/LIVE-COMPUTE-20261028. Không sửa source training hoặc runtime/config/receipt/artifact đã pin.
- Hardware probe chỉ đọc thông tin máy/packages, không capture, load weights hoặc download; không đưa hostname/identity vào output.

## Contract impact và checks
- Giữ contract web/offline events/review/runtime v1–v4; cập nhật live spec/registry đúng numeric timing được duyệt. Internal adapter giữ producer/consumer offline; cấu hình profile mới cần exact environment và approval trước chạy model thật.
- Kiểm batching/order/tail/empty/nonfinite/shape, CPU scalar parity, device fail-fast, package guard, timing CUDA synchronization/rolling bounds và model state; consumer runtime/online/web, Ruff/mypy/checker/diff. CUDA thực và model parity chưa thể nghiệm thu bằng fixtures.

## Checkpoint và bước tiếp
- Đã có ExecutionSettings, classifier batch, processor chunking, guarded execution factory, bounded stage timings, hardware probe và profile CLI có approval/source/deadline/output guards. Không thay mặc định web/CLI cũ hoặc source training.
- Đã triển khai timing/candidate primitives theo approval: slot selector, continuity theo mẫu thực xử lý, timestamp thật, bounded segments, ID ổn định, late result/gap/reset. Không tracker/camera thật, persistence evidence hoặc live review mới.
- Full suite cuối 382 tests PASS (2 skip); browser opt-in PASS riêng. Sau đó bổ sung guard CUDA mất lúc đọc memory counters: profile suite 7 tests PASS; timing suite 12 tests PASS. Fixture 14 người / 10 phút kiểm bounded metadata, không phải phép đo hiệu năng thật. Ruff, strict mypy 92 source files, checker `--require-git` và diff PASS; compile 150 Python files trong RAM, không tạo bytecode.
- Full suite sau GPU từng phát hiện race EOF ở monitor: trạng thái completed có thể đến sau take_result nhưng trước snapshot, bỏ frame cuối. Đã sửa drain trước công bố EOF và thêm test tái hiện deterministic; monitor suite 13 tests và full/browser cuối PASS. Không thay API hoặc UI.
- Probe local xác nhận Torch 2.8.0+cpu, CUDA unavailable, RAM khoảng 8 GB; không chạy model thật hoặc camera. Policy numeric đã Accepted, không hỏi lại. Kế tiếp: inventory laptop để materialize profile/parity, adapter camera và wire/persistence evidence/review riêng trước nối UI; các phần độc lập vẫn có thể tiếp tục.
- Đã dọn 16 thư mục cache (`.ruff_cache`, `.mypy_cache`, `__pycache__` trong `src`, `tests`, `scripts`, `outputs/encoder-source`: 222 files / 49.822.066 bytes) và 2 thư mục rỗng (`outputs/_scratch`, `outputs/live-video-web`), kiểm tra không chứa file được Git track hoặc artifact đã pin. Stage và commit đúng phạm vi slice `LIVE-RUNTIME-20261028`, không push. Dataset/model và inputs đã pin không có diff.
