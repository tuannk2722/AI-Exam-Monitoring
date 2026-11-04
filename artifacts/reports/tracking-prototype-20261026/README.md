# Benchmark tracking — 26/10/2026

**Cập nhật quyết định 27/10:** owner giao agent nghiên cứu và tự chọn arm. [Research/visual audit](research-20261027/README.md) và [selection](../../../configs/tracking/TRACKING-PROTOTYPE-20261026/selection-20261027.json) chọn B0 làm baseline prototype; cả hai arm có lỗi nối ID giữa hai người, chưa đạt gate temporal aggregation. Phần pending dưới đây là trạng thái bàn giao ngày 26/10, không còn yêu cầu owner tự chọn lại thuật toán.

Scope được owner duyệt: replay N0/B0/B1 trên detections của V8S/context-v1/G0, 60 samples ở 1 Hz. [Thiết kế và authorization](../../../configs/tracking/TRACKING-PROTOTYPE-20261026/execution.md). Giữ nguyên detector/classifier/calibration; không model inference mới, không events/risk/web.

## Kết quả kỹ thuật

[Benchmark](../../../outputs/tracking-prototype-20261026/benchmark.json) completed cho cả ba arms. [Evidence receipt](evidence.json) giữ exact pins và số liệu; mỗi arm có config/code/environment/session/checksums riêng. Đây là clip development đã biết, không là holdout độc lập.

| Arm | Assigned / observations | Chưa gán | Track IDs | Gap trong chuỗi assigned | Mean / p95 update (ms) |
|---|---:|---:|---:|---:|---:|
| N0 | 1.162 / 1.162 | 0 | 1.162 | 0 | 0,037 / 0,052 |
| B0 | 1.103 / 1.162 | 59 | 40 | 22 | 7,077 / 9,538 |
| B1 | 905 / 1.162 | 257 | 29 | 15 | 7,956 / 12,260 |

Track count không phải số người; gap tự động không phải fragmentation đã xác minh. Coverage cao hơn không chứng minh ít ID switch hơn. B1 tạo ít tracks và nhiều null hơn; chưa chọn winner. Timing chỉ association/mapping trên CPU, không gồm detector/classifier/decode/gallery, không là end-to-end FPS hoặc SLA.

## Batch review

[Gallery](../../../outputs/tracking-review-20261026/index.html) và [batch](../../../outputs/tracking-review-20261026/batch.json) giữ source frame/time/SHA cùng anchor mapping ba arms. Nhóm track do thuật toán draft; owner xem batch/ngoại lệ, ghi uncertain khi không rõ. Không tự tạo ground truth từ ID tracker. Gallery có nút xuất JSON; reviewer không phải annotate từng ảnh.

Gallery completed: 60 source frames, 169 cases gồm nhóm track và các sample chưa gán; lọc gap để ưu tiên review. 19 source frames tham chiếu V8S khớp byte; 19 benchmark file hashes và 63 review file hashes PASS. UI đã kiểm trong browser: ba canvas 1.280 × 720, chuyển sample 0 → 59, lọc gap; không đánh dấu review thay owner.

Chưa có owner quality acceptance hoặc identity ground truth. ID switch, fragmentation, detection/association loss theo person-samples và occlusion recovery chưa được công bố; technical null counts không thay các metrics đó. Stage tracking chưa đóng; events/risk/web chưa mở.

## Bảo toàn và giới hạn

Input parent session/predictions/config khớp SHA trước và sau replay. Không sửa parent accepted hoặc configs đã pin. Input chỉ có detections từ confidence 0,25, person box đã làm tròn và 1 Hz; không đánh giá đầy đủ ByteTrack trên raw detections/30 FPS. Duplicate/misses của V8S giữ nguyên, role unknown.

Media và browser review draft local owner-only, deadline 01/11/2026 15:55:06 Việt Nam; không upload/commit media hoặc gia hạn. Source clip kiểm SHA, không ghi đường dẫn riêng tư vào report.

## Kiểm chứng phần mềm

14 tracking tests PASS, gồm index mapping qua high/low subsets, đảo thứ tự detections, late appearance, gap/expiry, reset session, invalid geometry/time, parent mutation, approval/retention và failed outcome. 22 runtime tests và 5 contract tests PASS. Ruff cho phần đổi và strict mypy 71 source files PASS. Software tests không thay owner review hoặc scientific acceptance.

Checker cấu trúc repository, links và diff whitespace PASS; chưa stage/commit nên không kiểm delivery index bằng --require-git. Browser export JSON đã kiểm, giữ winner pending và 0 samples được đánh dấu thay owner. Lệnh dọn Ultralytics/settings.json phát sinh từ synthetic test bị automatic approval review chặn với lý do blocked by policy; file untracked còn nguyên, không thuộc deliverables, không bypass.
