# LIVE-COMPUTE-20261028 — Chuẩn bị GPU và đo runtime

## Thẩm quyền và scope

Ngày 28/10/2026, owner chốt baseline giao diện/logic web, yêu cầu cleanup, commit
rồi tiếp tục theo kế hoạch GPU/batching, profiling, camera và temporal log.
Baseline web đã commit `2c9d8fa`, runtime `6f4cbe3`. Scope implementation và fixtures
được mở; chưa có cấu hình GPU thực, benchmark model thật hoặc SLA Accepted.
Owner xác nhận tải demo **dưới 15 người, 5–10 phút**. Dùng 14 người / 10 phút làm
mốc kiểm tải đích; không tự giảm `max_det=100` xuống 14 hoặc bỏ người ngoài scope.

Giữ V8S/context-v1/G0 seed 20261023, pins, preprocessing, FP32 và thresholds.
Không sửa runtime v1–v4, receipt CPU, code training/evaluator hoặc artifacts lịch sử.
Config GPU được chọn sau khi biết máy và đo; không ghi một bản `approved` giả định
cho thiết bị chưa có. Web vẫn chạy baseline CPU, không tự chuyển khi thấy CUDA.

## Phần mềm hiện có

- `ExecutionSettings`: CPU hoặc `cuda:N` tường minh, batch 1..100; upper bound theo
  max_det hiện hữu, không phải capacity đã benchmark. CUDA thiếu/OOM trả lỗi;
  không giảm batch, đổi device hoặc precision ngầm. Một owner gọi model; context
  FP32 tắt autocast/TF32 và khôi phục flags sau lỗi, không bảo đảm bitwise parity.
- `BundleClassifier.predict_batch`: letterbox/normalize giữ nguyên, một chunk crop
  cùng frame, bảo toàn thứ tự, kiểm count/shape/finite và không giữ GPU tensors
  sau khi trả scores. `predict` và các caller cũ giữ batch 1.
- `FrameProcessor` nhận batch size và profiler tùy chọn. Chia crop theo chunk,
  kể cả tail; giữ anchor/geometry/sink. Không gọi classifier khi không detection.
  Batch không gộp khác frame/epoch và không thay cadence detector/tracker.
- `create_execution_processor`: chỉ parent runtime V8S v4; kiểm manifest package
  trước load model. Manifest mới phải pin đủ các package trong receipt; chỉ cho
  phép khác biến thể wheel Torch 2.8.0/torchvision 0.23.0, không nâng public version
  hoặc bỏ guard. Các package khác giữ exact version; parent receipt giữ nguyên.
- `StageProfiler`: timings có đồng bộ CUDA, count/mean/max toàn lượt và p50/p95
  của cửa sổ hữu hạn được ghi rõ. Stage frame bao gồm các stage con, không cộng
  các số này thành tổng. Classify gồm preprocess, transfer, forward và trả scores.
- CLI profile chạy tuần tự, không pacing theo media clock, không là online SLA.
  Tách load/warm-up/đo; decode một lượt, lấy mẫu theo parent runtime. Chưa đo
  encode/browser, tracker/events hoặc camera; các stage chưa chạy giữ count 0.

## Chuẩn bị máy, không gọi model

```powershell
.venv/Scripts/python.exe -B -m ai_exam_monitoring.inference.hardware_probe
```

Probe chỉ đọc OS/CPU/RAM, versions, CUDA device/VRAM/capability và driver qua
`nvidia-smi` với timeout 5 giây. Không camera, media, weights, download, hostname,
GPU UUID hoặc environment credentials. Không có CUDA vẫn trả inventory để phân
biệt máy không có NVIDIA với môi trường đang cài Torch CPU. Không tự cài driver
hay thay `.venv` đang dùng. Laptop thật cần environment riêng phù hợp và exact pins.

## Cấu hình và authorization trước profile model thật

`runtime-execution-profile-v1` là cấu hình công cụ mới, tách khỏi runtime gốc.
Các field bắt buộc, không có device/batch/package mặc định:

| Field | Ý nghĩa |
|---|---|
| `profile_id` | ID mới mỗi bộ variables/môi trường; không tái dùng output |
| `runtime` | FilePin path/SHA của runtime V8S gốc; loader vẫn kiểm toàn bộ pins/approval |
| `device`, `batch_size` | CPU hoặc cuda:N và chunk size cụ thể; chọn từ máy/phép đo |
| `packages` | Exact package manifest bằng keys receipt detector, đối chiếu máy thực |
| `warmup_samples`, `measured_samples` | Số mẫu nguồn dùng warm-up và đo, nguyên dương |
| `timing_window` | Số timings gần nhất mỗi stage dùng percentile; count/mean/max toàn lượt |
| `approval_ref` | JSON local: status approved, profile_id, config_sha256 theo digest_json, scope local_runtime_compute_profile, decision_ref |

Không materialize YAML/authorization chạy thật trước khi có environment và input.
Media receipt vẫn phải khớp runtime parent và SHA nguồn, còn deadline, không test
hoặc holdout. Approval compute không cấp quyền media mới hoặc gia hạn receipt.

Sau khi có exact config được duyệt:

```powershell
.venv/Scripts/python.exe -B -m ai_exam_monitoring.inference.profile_runtime `
  --config <profile.yaml> --workspace . --source <video.mp4> `
  --receipt <receipt.json> --output outputs/<profile-id>
```

Output mới có `config.json`, `runtime.json`, `receipt.json`, `hardware.json`,
`code.json`, `samples.jsonl`, `profile.json` và checksums. Chỉ metadata/timing/count,
không ảnh/crop/scores hoặc bản copy video. `runtime-compute-profile-result-v1`
ghi completed/failed, số warm-up/mẫu đã đo, source/config/code/env refs, deadline,
timing, RSS quan sát tại ranh giới mẫu và peak allocated/reserved của Torch CUDA.
RSS quan sát không phải true peak RAM toàn hệ thống; VRAM allocator không bao gồm
mọi ứng dụng hoặc Camo. Lỗi/EOF sớm giữ failed record và giải phóng decoder; không
coi lượt thiếu mẫu là PASS. Input/config/receipt được kiểm lại cuối lượt. Tool
không đọc lại output sau deadline, không render bằng chứng hoặc tự chọn model.

## Protocol đích và bước còn lại

1. Nhận inventory laptop, kiểm môi trường, chuẩn bị các profile CPU FP32 batch 1
   và CUDA FP32 với các batch ứng viên phù hợp VRAM. Mỗi cấu hình có identity riêng;
   số lượt/mẫu cụ thể chốt trước chạy, không tự benchmark sweep vô hạn.
2. Parity riêng trên cùng input được phép: so preprocessing/crop, scores, flags
   và detector geometry/count. Báo delta thực, trường hợp gần ngưỡng và flags đổi;
   không dùng tolerance của fixture thành quality gate hoặc sửa thresholds để qua.
   Công cụ timing hiện không thay công cụ parity hay báo cáo visual QA.
3. Đo compute từng stage trên tải ít người và gần 14 người, tách warm-up. Chốt
   batch/config từ throughput, p95 và VRAM; không tự chuyển FP16/TensorRT/model khác.
4. Sau camera và nhánh detector/tracker được nối, chạy end-to-end 5 phút rồi
   10 phút ở tải cao nhất: capture-to-result, tuổi ảnh trên browser, dropped/gaps,
   RAM/VRAM dài hạn, mất nguồn/stop/reconnect/EOF. Đo encode/transport/UI riêng.
   Instrumentation hiện chưa là harness cho bước này.
5. Temporal slots/jitter/gap/reset đã được owner duyệt tại
   [LIVE-TIMING-20261028](../../tracking/LIVE-TIMING-20261028/README.md); receipt camera
   và evidence retention cần chốt trước thu người thật. Giữ log candidate khi đủ
   support, stable ID/evidence revision đã duyệt; không tái sử dụng acceptance C10
   cho cadence bất quy tắc hoặc tạo positives từ frame thiếu.

Không cần owner chốt lại iPhone/iOS hay thiết kế đã Accepted. Thông tin cần tiếp
là inventory laptop để đóng compute profile, và scope nguồn/quyền camera trước
capture; không tự coi những phần còn mở là đã hoàn tất.

## Nguồn kỹ thuật

Đối chiếu PyTorch **2.8** đang pin: CUDA thực thi bất đồng bộ, phép đo wall time
cần đồng bộ, TF32 được kiểm riêng cho matmul/cuDNN; theo
[CUDA semantics](https://docs.pytorch.org/docs/2.8/notes/cuda.html).
Không nâng dependencies để khớp tài liệu latest. Software fixtures chỉ chứng minh
logic adapter/timing; chưa chứng minh tốc độ hoặc parity của model thật trên GPU.
