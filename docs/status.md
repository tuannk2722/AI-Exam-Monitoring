# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-10-25**. Chỉ giữ trạng thái hiện hành, thay nội dung khi tiến độ đổi; không append nhật ký/metrics/mọi task. Không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data engineering | V14 local accepted: 1.355 crop sử dụng, 1.199 train / 156 val development / 0 test; dùng đủ 53 crop mới | [V14 release/pointers](../artifacts/reports/dataset-release-20261024-v14/README.md) |
| Baseline | E001–E003 FINISHED, Continue research; chưa model Selected | Reports → runs/baseline |
| Model improvement | E008 V14: 4 smoke + 5 research FINISHED; audit metadata PASS. G0 thắng, phone qua gate 3/3 seed G0; looking chưa đạt, chưa Selected. Đã nhận đủ best/last ba run G0 và kiểm integrity local | [Kết quả E008](../artifacts/reports/e008-v14-colab-20261024/results-20261025.md), [checkpoint](../artifacts/reports/e008-v14-colab-20261024/checkpoints-20261025.md) |
| Runtime | Đã có CLI recorded-video → person → context crop → G0, pins/rights guards và gallery QA; có full-frame và sampling 1/2 Hz; chưa nghiệm thu chất lượng video | [Reference](reference.md), [system](system.md) |
| Tracking/events/risk/web | Chưa end-to-end; tracker/rules/risk còn quyết định mở | [Decisions](decisions.md), system acceptance |
| Tooling/storage | Sau E007 đã nghỉ lưu payload lịch sử và bản trùng: 8.971 files, 9,959 GiB logical; giữ V13/nguồn độc nhất, ba best D1 và ba best R0 cùng metadata | [Cleanup/availability 24/10](../artifacts/reports/cleanup-20261024/README.md), [chính sách](storage.md) |

## Ưu tiên hiện hành

Owner đã duyệt [chuyển phase prototype](../artifacts/reports/e008-v14-colab-20261024/prototype-decision-20261025.md), dừng cải thiện classifier E008 và chọn G0 seed 20261023, giữ checkpoint/preprocessing/ngưỡng. 80/80/20 không còn chặn chuyển phase prototype; kết quả nghiên cứu và hạn chế support/validation giữ nguyên. [Đề xuất runtime](../configs/runtime/RUNTIME-PROTOTYPE-20261025/README.md) đã được owner duyệt detector/license/crop/output và implementation; config đã materialize. Owner yêu cầu dọn toàn bộ ba thử nghiệm video và hồ sơ riêng; không giữ các lượt đó làm backlog hoặc nghiệm thu. Giữ implementation/config prototype cho phase runtime tiếp theo; tình trạng dọn ghi ở [cleanup](../artifacts/reports/runtime-prototype-20261025/cleanup-20261025.md). [Bàn giao runtime](../artifacts/reports/runtime-prototype-20261025/README.md); chưa nghiệm thu chất lượng video.

## Phạm vi hiện hành

Dataset dùng tiếp là [V14 accepted](../artifacts/reports/dataset-release-20261024-v14/README.md): 1.199 train / 156 val development / 0 test. Dùng đủ 53 crop generated mới trong train; exclude G01-A02-F00001-R02 và G01-B02-F00009, chuyển đủ 27 crop thuộc 6 nhóm nguồn liên quan từ val sang train. Nhãn/geometry/bytes V13 giữ lại không đổi. Validation đã đổi composition và không là holdout độc lập; giữ giới hạn lineage của ảnh generated. V13/E007 và pins lịch sử được bảo toàn.

- [E006 V12](../artifacts/reports/e006-v12-20261020/README.md) hoàn tất; SQRT là recipe tham chiếu development, chưa đạt đồng thời cổng chất lượng cho cả hai target. Chưa model Selected. Các test cũ đã được mở visual audit trong scope V13; không phát sinh quyền inference/final-test mới.
- [E007 V13 Colab](../configs/experiments/E007-V13-20261024/README.md) hoàn tất 9 research run trên L4 trong khoảng 42 phút; artifacts cloud đã import và kiểm checksum/reload. D1 là hướng nghiên cứu chính, nhìn quanh là phần còn thiếu; chưa test/promotion. Ma trận đã dùng đủ số run được duyệt, không tự chạy thêm dù còn thời gian. [Evidence](../artifacts/reports/e007-v13-colab-20261024/README.md); proposal 23/10 giữ snapshot gốc.
- [E008 V14 Colab](../configs/experiments/E008-V14-LOOKING-20261024/README.md) đã hoàn tất trên A100: 4 smoke + 5 research, khoảng 37 phút. Audit metadata/checksums/predictions/calibration và reload evidence PASS. G0 thắng screening nên chỉ G0 được confirmation hai seed; không chạy thêm khi còn ngân sách. Looking vừa thiếu support (29 positive), vừa chưa đạt đồng thời precision/recall; Continue research, chưa Selected. Đã import đủ ba thư mục G0, kiểm SHA và cấu trúc sáu checkpoint best/last; [receipt](../artifacts/reports/e008-v14-colab-20261024/checkpoint-import-20261025.json). Không chạy inference mới; giữ campaign/recovery trên Drive. [Kết quả và lỗi bền vững](../artifacts/reports/e008-v14-colab-20261024/results-20261025.md) giữ evidence nghiên cứu; hướng review/cải thiện tiếp trong report không còn là backlog hiện hành sau quyết định chuyển phase. Không so trực tiếp E007/V13 hoặc hạ gate để công bố đạt.
- [Diagnostics V12](../artifacts/reports/e006-v12-diagnostics-20261021/README.md) và [audit](../artifacts/reports/v12-reconcile-20261022/README.md) giữ evidence. Các checkpoint candidate/quarantine cũ đã được thay bằng V13 accepted; không lấy chúng làm backlog.
- [Đối chứng erasing](../configs/experiments/E006-followup-20261021/README.md) chưa run approval. Không tự chuyển configs E005/E006 sang V13 hoặc train lại.
- [Cleanup ngày 23/10](../artifacts/reports/cleanup-20261023/README.md) ghi availability mới cho cache, candidate crops và bản làm việc E004 trùng archive. Giữ metadata/pins, archive, datasets/models và nguồn rebuild V13; [availability 16/10](../artifacts/reports/storage-retention-20261016/availability.json) áp dụng cho phần không được đợt mới cập nhật.
- [Cleanup sau E007 ngày 24/10](../artifacts/reports/cleanup-20261024/README.md) supersede availability cũ cho exact paths được nghỉ lưu. Không giả định checkpoint E001–E006, E007 last/smoke/nonchampion hoặc crops lịch sử còn tại working paths; metadata/pins giữ nguyên. Source và model best D1/R0 hiện hành được bảo toàn.
- Runtime/downstream theo [system gates](system.md#6-điều-kiện-chuyển-bước); G0 seed 20261023 đã được chọn riêng cho prototype theo ngoại lệ mới; chưa model demo Selected theo chất lượng nghiên cứu hoặc quality threshold/SLA toàn video Accepted. Phần độc lập được user yêu cầu vẫn tiếp tục.
