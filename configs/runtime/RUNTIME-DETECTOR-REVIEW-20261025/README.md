# RUNTIME-DETECTOR-REVIEW-20261025 — Đối chứng detector/crop

**Draft reviewable; owner đã giao chuẩn bị thiết kế, chưa chốt numerical variables/acceptance hoặc cấp run mới.** Căn cứ [QA 1 Hz](../../../artifacts/reports/runtime-clip-qa-20261025/qa-1hz.md) và [đánh giá A1/Dual ROI](../../../artifacts/reports/runtime-clip-qa-20261025/model-relevance.md). Không thay config/protocol đã pin hoặc biến kết quả QA thành acceptance.

## A. Đối chứng box trùng trước, giữ classifier/crop

Đề xuất dùng đúng 19 frame gallery đã có của lượt 1 Hz (0 đến 59 giây), cùng source SHA và PNG/checksums. Đây là cohort development đã xem, không holdout. Owner review batch hiện có, agent chuẩn bị draft quan hệ cùng người/khác người và ngoại lệ; không yêu cầu owner annotate từng ảnh từ đầu. Trước đánh giá định lượng, phải có danh sách người nhìn thấy theo từng frame, kể cả người baseline bỏ sót; mã chỉ local trong frame, không là identity/track. Các draft unknown không tự trở thành matching ground truth.

| Arm đề xuất | NMS IoU | Conf | Những gì giữ nguyên |
|---|---:|---:|---|
| D0 | 0,70 | 0,25 | YOLOv8n weights/package, imgsz 640, max_det 100, CPU FP32, person-only |
| D1 | 0,50 | 0,25 | Như D0 |
| D2 | 0,30 | 0,25 | Như D0 |

Đây là ba điểm đối chứng hữu hạn, không sweep mở hoặc tune sau xem kết quả. Stage detector-only: 19 × 3 = 57 frame forwards, chưa chạy G0 cho mọi arm. Baseline D0 phải đối chiếu source/boxes/conf với cached output; sai parity phải giải thích trước kết luận. Không dùng lại post-NMS boxes rồi chạy NMS lần hai để giả kết quả đổi threshold; phải lấy output detector từ cùng nguồn với từng cấu hình, giữ boxes float trước rounding nếu công cụ hỗ trợ.

Đề xuất matching visual có owner review theo người/frame, không tự chọn IoU matching threshold cho box bán thân/toàn thân. Mỗi người có 0/1/n boxes: miss = 0; duplicate extras = max(n−1, 0); unmatched false box ghi riêng. So theo từng frame và tổng, nêu số trường hợp unknown. Owner không cần người review thứ hai. Giữ crop/input đủ bằng chứng để xem box được giữ có mất tay/bàn/đầu không.

Tiêu chí **đề xuất chờ duyệt**: ít duplicate extras hơn D0, không phát sinh người baseline đã thấy bị mất trên cohort reviewed; không đổi một lỗi duplicate thành lỗi mất người bị che. Không dùng tổng detections giảm làm success. Nếu không arm nào thỏa thì không chọn winner; chỉ lúc đó mới thiết kế containment-aware rule/Soft-NMS hoặc detector khác với approval riêng. Không tự chọn largest-box hoặc highest-score là box đúng.

Nếu detector-only có winner, đề xuất bước riêng chạy G0/context-v1 trên các frame/anchors thay đổi, giữ calibration và đối chiếu attribution/visibility, rồi mới quyết định prototype revision. Chưa cấp quyền classifier rerun trong stage A này; không mở tracking/events.

## B. Attribution và các model cũ

Giữ các cặp cùng người/cùng frame khác context để owner chốt: đủ context, phone thuộc anchor hay hàng xóm, bằng chứng thiếu/unknown. Bảng score hiện có là diagnostic, không dùng score cao hơn để chọn crop đúng.

A1 chỉ xét đối chứng sau stage A/crop review và khi đủ exact checkpoint. So G0/A1 trên cùng source, person/context geometry, preprocessing đúng từng model, dùng calibration riêng; đánh giá theo từng anchor có nhãn reviewed và tách nhóm multi-person/phone ngoài person box/occlusion. Không đổi detector đồng thời. E005-Dual ROI chưa executable do payload retired, giữ ở nhánh phân tích; không tự train lại. Chi tiết cơ chế, kết quả và availability ở companion model assessment.

## C. Vai trò/eligibility

Đề xuất tạm thời giữ mọi person observation phục vụ diagnostic và đánh dấu vai trò chưa xác định; không đưa người đi lại vào cảnh báo thí sinh hoặc tự tuyên bố đó là giám thị. Chưa có event pipeline, nên đây là quyết định về scope downstream cần owner chốt, không là một filter đã triển khai. Nếu owner cần chỉ thí sinh ngay, xác định eligibility bằng thông tin owner cung cấp/review trước, không dùng quần áo, dáng đứng/ngồi hoặc score hành vi làm bằng chứng role. Seat mapping/role model tự động là scope thiết kế khác, chưa thêm vào slice này.

## Inputs, implementation và bàn giao sau approval

[Variables draft](proposal.yaml) không được runtime loader nhận như executable config. [Batch review local](../../../outputs/runtime-detector-review-20261025/index.html) dẫn đúng cached source/crop/input; [manifest](../../../outputs/runtime-detector-review-20261025/cohort.json) pin source/predictions/checksums, 19 frames và các pair candidates, owner decisions null. Media giữ deadline của session gốc, không kéo dài bằng tạo derivative.

Sau owner chốt A và cohort review: thích nghi công cụ reusable trong `src/ai_exam_monitoring/inference`, variables trong identity mới, synthetic checks cho parity/geometry/no-overwrite trước detector run. Không nới loader prototype chỉ để nhận biến mới; không sửa snapshot source/model cũ. Run có output/pins/code/environment và failed/completed riêng. Stage A không đổi domain schema; role/classifier adapter cần thiết kế đúng slice nếu được giao tiếp.

Owner cần quyết định: duyệt ma trận D0/D1/D2 cùng tiêu chí bảo toàn người; duyệt cách review cohort; giữ role unknown trong diagnostic hay ưu tiên chốt eligibility trước downstream. A1 không bắt buộc cho stage detector, không chặn phần độc lập vì thiếu checkpoint.
