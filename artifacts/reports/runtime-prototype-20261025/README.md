# Runtime prototype — Bàn giao phần mềm ngày 25/10/2026

Owner duyệt [thiết kế và config](../../../configs/runtime/RUNTIME-PROTOTYPE-20261025/README.md), rồi xác nhận chưa có clip và yêu cầu hoàn tất code/synthetic tests trước. Branch `feat/runtime-prototype-e008`. Không training, final test hoặc inference trên dữ liệu người thật.

## Context và implementation

Đã đối chiếu system/data/training/development/reference, registry/status, E008 results/checkpoint import, full bundle/config/calibration/source/license pins và code producer/consumer. Giữ nguyên trainer/evaluator và artifacts lịch sử. Adapter mới tái dùng `AdaptationModel`, local DINO source loader, `letterbox`, FilePin/provenance; checkpoint vẫn là G0 seed 20261023 được owner chọn.

CLI `inference.runtime` thực hiện person → crop → hai score, giữ frame rỗng, source/config/model/code/environment provenance, outcome completed/failed và gallery review. Timestamp lấy từ decoder, không suy từ số detection; reject clip thiếu metadata/timestamp hoặc decode không đủ. Config/runtime identity riêng cho CPU; không tuyên bố parity CUDA hoặc acceptance chất lượng.

[Detector receipt](detector-acquisition.json) ghi URL/SHA/taxonomy và package pins. [Environment freeze](environment-freeze.txt) giữ dependencies thực tế; OpenCV 4.11.0.86 được chọn để không hạ NumPy đang có. YOLOv8n local là input runtime cần giữ; không nằm trong Git. Cache/settings có thể tạo lại từ pinned inputs, không là evidence độc nhất.

## Validation và giới hạn

[Synthetic check](synthetic-check.json): real weights YOLOv8n xử lý ảnh màu trơn không detection; real G0 trả hai score hữu hạn. Pipeline decode/inference clip tự tạo 3 frame hoàn tất; fixture detector riêng trong kiểm thử đi qua crop → classifier thật. Không fake predictions trong production hoặc dùng fixture làm metric chất lượng. Software tests kiểm geometry, target order, ngưỡng, frame rỗng, timestamps/decode, input/pin/rights failures, preprocessing parity và output preservation.

Software handoff không xác nhận chất lượng phát hiện người/hành vi, false/missed behavior hoặc crop đúng anchor. Các lượt video phát sinh sau đó thuộc scope cleanup riêng của owner. Gallery cần owner review trước tracking/events; labels/metrics E008 giữ nguyên. Runtime ghi latency/RAM thực thi, không có SLA; retention deadline ghi trong session nhưng chưa có tự động xóa. Chỉ xử lý MP4 có metadata hợp lệ, không hứa hỗ trợ mọi codec/VFR hỏng timestamp. Commit phase runtime theo yêu cầu cleanup riêng; không push.

[Cleanup mới](cleanup-20261025.md) ghi scope owner yêu cầu dọn scratch/settings và ba thử nghiệm video, cùng tình trạng thực thi. Giữ weights/receipt/config prototype và source/tests.

Checks cuối: full suite 231 tests PASS trong 288,745 giây (trước thêm test session); runtime mới nhất 12 tests PASS, generic inference 4 tests PASS. Ruff PASS; strict mypy 61 source files PASS; compileall/pip check PASS. Repo checker PASS trên index hiện có, chưa bao gồm files mới chưa stage. CI classifier job đã thêm runtime fixtures.
