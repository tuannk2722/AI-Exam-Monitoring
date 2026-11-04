# Kiểm chứng cadence tracking ngày 27/10/2026

Đã hoàn tất ma trận theo [thiết kế đã pin](../../../configs/tracking/TRACKING-CADENCE-20261027/README.md), tiếp nối [research B0/B1](../tracking-prototype-20261026/research-20261027/README.md). **Chọn C10 làm candidate cho bước kiểm chứng tiếp theo**, theo ủy quyền quyết định kỹ thuật của owner; chưa nghiệm thu tracking hoặc mở events/risk/web. B0 giữ vai trò baseline đối chứng, output cũ bất biến.

## Thực thi và kết quả

Một cache 10 Hz gồm 600 samples: 60 samples gốc được giữ nguyên observations, 540 detector forwards mới, 0 classifier forwards mới. C5 replay 300 samples, C10 replay 600 samples, cùng B0 association policy và lost window khoảng 2 giây. Không đổi model, threshold, crop, role hoặc scores G0. Run hoàn tất trong khoảng 205 giây; riêng detector khoảng 143 giây. Đây là xử lý offline, không chứng minh real-time 10 Hz.

| Arm | Assigned trên 1.162 anchors chung | Null | ID tại hai anchors lỗi 8 → 9 giây |
|---|---:|---:|---|
| B0 1 Hz | 1.103 (94,92%) | 59 | 10 → 10, nối nhầm người |
| C5 5 Hz | 1.141 (98,19%) | 21 | 10 → 28 |
| C10 10 Hz | 1.152 (99,14%) | 10 | 10 → 32 |

Coverage là tỷ lệ tracker xuất ID, không phải độ chính xác association. Số ID xuất hiện trên projection chung là 53 ở C5 và 66 ở C10; không dùng số này làm metric fragmentation khi chưa có GT và accounting người/duplicate.

## Audit và quyết định

- Đã xem đủ 21 samples C5 và 41 samples C10 trong cửa sổ 7–11 giây, tập trung vùng người đội mũ/người áo trắng đi qua. Người đi qua giữ trajectory riêng; không thấy T10 chuyển sang người đó như B0. Người ngồi vẫn mất/đổi ID sau che khuất: C5 xuất hiện T31/T32; C10 xuất hiện T38/T39. Khắc phục lỗi nối nhầm cụ thể không đồng nghĩa phục hồi identity xuyên occlusion.
- Đoạn 35–40 giây: xem full scene tại 11 mốc mỗi arm và trace dày người đi qua. C5 T92 kết thúc ở 39,0 giây, null tại 39,2 rồi T95 từ 39,4; C10 giữ T101 trên cả 51 samples. C10 có lợi ích continuity cụ thể, nên hai cadence không tương đương để mặc định chọn C5 rẻ hơn.
- Xem tám cặp có dịch chuyển tâm box lớn nhất mỗi arm. Nhiều cặp do box đổi từ thân trên sang toàn thân hoặc người đi qua mép ảnh; những crop chỉ còn đỉnh đầu giữ mức uncertain, không gán chắc identity chỉ bằng hình dạng đầu. Không thấy thêm mixed-person rõ trong tập audit này.
- Đối chiếu 17 crops thuộc các nhóm coverage thấp/duplicate từ research trước: cả C5/C10 giữ ID tại các anchors đã xem. Duplicate vẫn còn, ví dụ anchor thuộc B0 T55 tại 36 giây vẫn được C5/C10 gán ID; cadence không phải bộ lọc duplicate.

**Lý do chọn C10:** xử lý được lỗi đã biết và giữ trajectory 35–40 giây tốt hơn C5, thêm 11 assignments trên các anchors chung. Đổi lại cần khoảng gấp đôi samples detector so với C5 và vẫn có fragmentation; không tuyên bố thắng toàn clip hay tổng quát sang camera khác. C5 giữ comparator tiết kiệm compute. Chưa đổi runtime mặc định 1 Hz/G0 hoặc triển khai live pipeline.

[Gallery B0/C5/C10](../../../outputs/tracking-cadence-20261027/index.html) có 60 mốc chung và các frame dày trong hai cửa sổ. [Audit boards](../../../outputs/tracking-cadence-audit-20261027/) giữ case, motion, top jumps và coverage crops. [Evidence và checksums](evidence.json) ghi provenance, phạm vi audit và quyết định; session đã seal vẫn ghi pending visual audit tại thời điểm chạy, báo cáo này là kết quả audit bổ sung, không reseal session.

## Kiểm tra và bước tiếp

22 tracking tests và 22 runtime tests PASS; Ruff phần Python mới PASS; strict mypy PASS 72 source files. Repository checker không `--require-git` PASS; chưa stage/commit nên không coi đó là chứng nhận Git đã chứa files mới. Kiểm SHA toàn bộ manifest output mới và input pins; cached parent observations khớp nguyên trạng. Gallery mở được trong browser với ba canvases và dữ liệu đúng arm.

Ma trận cadence hoàn tất. Bước tiếp theo là audit association/duplicate có hệ thống trên toàn clip cho C10 và chuẩn bị cách xử lý tracklet đứt qua occlusion trước temporal aggregation. Chưa có GT chuẩn để báo HOTA/IDF1; không dùng coverage làm acceptance threshold. Nếu cần appearance/ReID, phải lập thiết kế riêng với weights/license/compute và đối chứng C10; không tự tải model hoặc suy paper bảo đảm sửa được lỗi. Không yêu cầu owner tự chọn thuật toán hay annotate từng ảnh.

Media, cache và audit boards local owner-only, không upload, cùng deadline **01/11/2026 15:55:06 Việt Nam**. Metadata nhỏ giữ trong repo; chưa commit. Không sửa các hồ sơ research/config/output đã pin trước đó.
