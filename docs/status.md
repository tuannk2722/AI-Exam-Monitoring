# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-11-09**. Chỉ giữ capability/ưu tiên hiện hành, không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data | V15 local accepted: 1.721 crop, 1.377 train / 344 val development / 0 test; chỉ hai target cũ. Chưa có release năm nhãn | [V15 release/pointers](../artifacts/reports/dataset-merge-20261106/README.md) |
| Model | E009 đã đóng; B0 mặc định, B448 tùy chọn cho prototype hai nhãn. Checkpoints đã audit; findings export sát ngưỡng và giới hạn looking/development validation giữ nguyên; chưa final-test acceptance độc lập | [Audit E009](../artifacts/reports/e009-v15-colab-20261106/results-20261107.md), [checkpoint audit](../artifacts/reports/e009-v15-colab-20261106/checkpoints-20261107.md), [model runtime](../configs/runtime/RUNTIME-E009-20261107/README.md) |
| Web laptop | Hồ sơ B0 CUDA FP32 batch 1, 1 Hz; upload/pause/seek/stop, MJPEG/SSE. Source refactor chưa được profile tích hợp; guard GPU cũ sẽ chặn. Chưa camera hoặc tracking/events/review online | [Cách chạy từ repo](../README.md#chạy-web-trên-laptop-gpu), [setup đã pin](../configs/web/LAPTOP-VIDEO-20261108/README.md) |
| Runtime/review offline | CLI person → context crop → G0, tracking C10, temporal candidates và web/SQLite review riêng đã có; acceptance chỉ trong scope prototype đã duyệt | [Reference](reference.md), [scope web](../configs/web/README.md) |
| Storage | Giữ dataset/model hiện hành và evidence/pins; payload lịch sử có phần đã retire, DVC pointer không chứng minh bytes còn tồn tại hoặc remote backup | [Storage](storage.md), [availability](../artifacts/reports/cleanup-20261024/README.md) |

## Ưu tiên hiện hành

Theo [LABEL-CONTRACT-20261109](decisions.md), workflow audit/review/QA, trainer representation, calibration/reporting và runtime/web video đã refactor cho hai/năm target; V1/V2 dữ liệu giữ nguyên. Dữ liệu ngoài vẫn phải audit từ đầu, chưa nhập/release; chưa train hoặc đổi model demo. Calibration năm nhãn cần mục tiêu từng target trong protocol, chưa chốt con số. Temporal events/campaign ranking cũ giữ scope hai nhãn. API và giới hạn ở [reference](reference.md#training-code).

Cấu hình laptop vẫn pin B0, RTX 3050 4 GB / RAM 16 GB, CUDA FP32 batch 1, 1 Hz. Refactor đã đổi numerical source: guard của `outputs/verify-b0-01` sẽ chặn chạy cấu hình GPU cũ từ source hiện tại; pins/evidence không sửa. Gói/source gốc giữ scope đã đo; source/model mới cần kiểm chứng tích hợp riêng ở bước 5. Software tests không thay nghiệm thu GPU/video.

## Stage runtime đã đóng

Stage V8S → context-v1 → G0, 1 Hz / 60 samples, đã [nghiệm thu trên clip hiện tại](../artifacts/reports/runtime-clip-qa-20261025/stage-acceptance-20261026.json). C10 và events có [closeout tracking](../artifacts/reports/tracking-cadence-20261027/closeout-20261027.md) và [acceptance riêng](../artifacts/reports/events-prototype-20261027/acceptance-20261027.md). Giữ giới hạn detector/classifier, fragmentation/duplicate; batch acceptance không confirmed từng event, không chứng minh chất lượng video mới hoặc real-time SLA. Risk chưa mở.

E001–E009, V13/V14 và các đối chứng D2/pose/V8S/V10S là hồ sơ lịch sử theo [reports index](../artifacts/reports/README.md), không backlog hoặc quyền chạy lại. V15 val có 197 crop train lịch sử chuyển sang theo nguyên nhóm, chỉ là development; không so trực tiếp metrics khác cohort. Giữ approvals/pins, media deadlines và giới hạn test access gốc; thay contract nhãn không relabel/reseal artifacts hoặc mở lại test.
