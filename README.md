# AI Exam Monitoring

Nghiên cứu/demo hành vi quan sát được trong video phòng thi: person detector → context crop → classifier multi-label → tracking/events → human review. Không định danh sinh viên hoặc tự kết luận kỷ luật.

- [Trạng thái dự án](docs/status.md): capability, input và công việc đang xem xét.
- [Đọc theo task](docs/00-INDEX.md): contracts, implementation reference và hồ sơ cần chọn.
- [System spec](docs/system.md), [data contract](docs/data.md), [training contract](docs/training.md): yêu cầu có hiệu lực.
- [Development](docs/development.md): setup/checks/workflow; [operations](docs/operations.md): restore/backup khi cần; [storage](docs/storage.md): lưu trữ và retention.
- [Reports](artifacts/reports/README.md): nghiên cứu, releases, kết quả/evidence; [experiments](configs/experiments/README.md): config/proposal/approval.

Agent bắt đầu với AGENTS/index/TASK, không đọc mọi report/archive. Results thuộc hồ sơ theo đối tượng; spec chỉ đổi khi contract đổi. Git lưu source/config/metadata nhỏ; data/model/media theo DVC/storage đúng quyền, pointer không là binary backup.

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
