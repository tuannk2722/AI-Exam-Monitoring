# E006 — Training tự động trên V12

Owner duyệt tối đa 9 research run + 1 smoke, local CPU 4 threads, tối đa 7.200 giây
mỗi run. Mục tiêu là chất lượng development trên V12; không yêu cầu so gain với E005.
Phê duyệt ở [owner authorization](../../../artifacts/reports/e006-v12-20261020/owner-authorization.json).

Revision research hiện hành: [r4/design.json](r4/design.json), [r4/campaign.json](r4/campaign.json).
Campaign đã hoàn tất. Thư mục `r4` giữ cấu hình research đã pin; `r2` chỉ giữ cấu hình và protocol cần cho smoke thành công. Các nhánh không chạy trong R4 vẫn thuộc plan đã pin.

## Ma trận và lựa chọn

- Seed đầu 20261020: LP; S1-REF với pos_weight [1,13; 1,46]; S1-SQRT với
  [1,56; 1,48]; S1-RATIO với [2,44; 2,19]; S1-FROZEN với [1,13; 1,46].
- S1-FROZEN giữ backbone đóng nhưng lịch LR của head giống S1-REF, gồm warmup
  3 epoch trước cosine. Các recipe khác giữ recipe S1 E005, input 224, MLP 128,
  dropout 0,3, smoothing 0,05, max 12 epoch, patience 6. LP giữ recipe LP.
- Chọn hai trong bốn recipe S1 theo thứ tự: qua cổng hiệu chỉnh 80/80/20,
  Macro AP cao hơn, BCE thấp hơn, tên recipe để phá hòa. Lặp hai seed 20261021/20261022.
  Các config nhánh không được chọn giữ nguyên và không chạy.
- Tổng hợp ba seed: số run qua cổng, mean Macro AP, SD thấp hơn, mean BCE thấp hơn.
  Chỉ đề xuất recipe để owner xem xét; không tự promotion hoặc chọn Selected.
- Tất cả khởi tạo sạch từ IMAGENET1K_V1 và head mới, dùng cùng head ban đầu
  cho các recipe cùng seed/kiến trúc. Không warm-start E005.

## Dữ liệu và đánh giá

V12 giữ nguyên 1.092 train / 204 val; 11 test đóng. Protocol pin exact records,
family assignments, reserved holdout và lát cắt theo nguồn/owner/legacy.
U giữ mask 0. Mức tối thiểu 30 P / 30 N / 5 nhóm P / 5 nhóm N; nguồn thiếu support
là INCONCLUSIVE. Không biến waiver research thành waiver quality gate.

Giữ checkpoint theo Macro AP; báo BCE không weighting, AP, confusion matrix,
ngưỡng 0,50 và ngưỡng hiệu chỉnh theo code hiện hành; bootstrap theo nhóm ở 0,50,
nguồn/lát cắt và FP/FN. Val đã dùng chọn epoch/recipe/ngưỡng, không là holdout độc lập.
Phone val chỉ có 35 P; không diễn giải một seed như bằng chứng ổn định.

## Tự động hóa và điều kiện dừng

`campaign_prepare` materialize exact configs từ `design.json`, không chạy training.
`campaign` chạy độc lập với phiên chat; không polling model hoặc gọi API.
Smoke 4 epoch gồm intentional interrupt sau epoch 1, resume cùng identity,
chuyển từ warmup sang layer4.1 và standalone reload exact parity.
Research readiness pin receipt của smoke đã kiểm chứng.

Sau smoke, mỗi run phải FINISHED và reload parity PASS mới sang run tiếp.
Lỗi integrity, OOM, hết wall budget hoặc evaluator lỗi: dừng, ghi trạng thái và report;
không tự giảm batch, đổi variables, mở test hoặc cấp lại approval.
Runner không tự chạy lại output đã tồn tại; lock chặn launch trùng.

Chạy nền ẩn trên Windows, giữ hệ thống không idle sleep trong thời gian pipeline.
Không thể tiếp tục khi máy tắt/reboot. Chạy từ `src/ai_exam_monitoring` như các run trước;
không có cây source runtime trong outputs. Code identity được kiểm trước mỗi run;
không sửa source khi queue đang chạy. Exact source của smoke cũ đã được bảo toàn
theo `source-preservation.json`, chỉ restore tạm khi cần tái lập.

Kết quả và phân tích đã kiểm chứng: [E006 report](../../../artifacts/reports/e006-v12-20261020/README.md).
`campaign-state.json` và `selection.json` lưu trạng thái hoàn tất và lựa chọn recipe.

Artifacts: `outputs/<run-id>/` chứa run record, resolved config, provenance,
best/last checkpoint, history, metrics, predictions và checksums; standalone evaluation
ở `outputs/<run-id>-val-evaluation/`. Source smoke được bảo toàn theo
`source-preservation.json` trong hồ sơ report. Không stage/upload binaries.

Campaign này đã kết thúc; nghiên cứu tiếp cần identity và config mới theo phạm vi được duyệt.
