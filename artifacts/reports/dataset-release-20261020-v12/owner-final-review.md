# Hợp nhất audit crop — hoàn tất, chờ review thay đổi

Đã xử lý 836 crop legacy, 71 crop YouTube và 83 vùng được đánh dấu trong 41 ảnh `additional.zip`.
Hai file review của owner và ZIP vẫn khớp SHA ban đầu; crop không nhận xét được giữ approved
theo chỉ dẫn.

[Mở gallery hợp nhất](../../../data/interim/crop-review-consolidation-20261019/index.html).
Bạn chỉ cần review **273 mục thay đổi**, gồm:

- **168 crop mới hoặc cắt lại**, trong đó 19 crop từ ảnh bổ sung.
- **3 thay đổi nhãn** cần xác nhận; 20 trường hợp nhãn đã được đối chiếu riêng với nhận xét/source.
- **20 đề xuất loại trùng**, mỗi mục hiển thị crop bỏ và bản giữ lại.
- **82 đề xuất rút crop** vì không tìm được khung thay thế đáp ứng tiêu chí; lý do từng mục có
trong gallery.

Các crop approved giữ nguyên không nằm trong danh sách review. Quyết định owner đã exclude cũng
không bị hỏi lại.
Nhãn theo thứ tự **phone / looking**; U được giữ khi bằng chứng không đủ, không biến tay khuất
thành N.
Xác nhận phone của owner cho CA001/S023 đã được áp dụng đúng phạm vi, không suy thành nghiệm thu
crop mới.

## Kết quả và kiểm tra

- 324 phương án cắt đã được xem xét; 168 bản được chọn sau QA native/input 224 và loại trùng.
- 338 cặp đã được đối chiếu trực quan: 331 cặp ban đầu và 7 cặp phát sinh sau hợp nhất.
  244 cặp nguồn tương đồng đã có kết quả; cohort Draft cuối gồm **685 crop**, không
còn cặp trùng pixel.
  Tương đồng không tự quyết định loại; giữ những khác biệt về vùng người, hướng đầu hoặc thao tác.
- Cả 41 ảnh bổ sung có quyết định từng vùng: đề xuất, được đại diện bởi crop có sẵn, hoặc không
đạt geometry.
  Người được đánh dấu không bắt buộc có crop.
- Hàng đợi recrop, diễn giải nhận xét và nhãn/geometry đều bằng 0. 907 records có disposition và
liên kết outputs.
- Đã kiểm SHA nguồn/crop đầu vào; bản crop được chọn khớp từng pixel với vùng nguồn và input 224
khớp pipeline.

## Hồ sơ để kiểm tra lại

- `delta-review.json`, `final-dispositions.json`, `final-draft-cohort.json`: thay đổi và trạng
thái cuối từng crop.
- `additional-final-slots.json`: đủ 83 vùng/41 ảnh, lý do và đại diện.
- `final-duplicate-review.json`, `final-duplicate-review-post.json`, `duplicate-decisions.json`:
đối chiếu trùng.
- `source-pair-final-coverage.json`, `geometry-review.json`, `qa-*.json`: nguồn và QA từng
phương án.
- `progress-summary.json`, `checkpoint-validation.json`: số lượng và kiểm tra tự động.
- `input-pins.json`, `owner-inputs/`: review gốc và provenance.

Đây là **hoàn tất audit**, chưa là nghiệm thu dataset mới. Crop/nhãn mới và đề xuất rút vẫn chờ
owner duyệt.
Các trial bị thay thế hoặc không chọn được giữ làm bằng chứng, không nằm trong cohort cuối.
Accepted V11, splits, model và E005 không thay đổi; không train, test, upload hoặc commit.
Y05 vẫn giữ lưu ý lineage của audit YouTube; chưa gán split hoặc xác nhận là nguồn độc lập.

## Kết quả review của owner

| ID | Kết quả |
|---|---|
| ADD-Y01-F00004-M01 | P/N |
| ADD-Y06-F00027-M01 | N/P |
| ADD-Y06-F00012-M02 | N/U |
| ADD-Y05-F00069-M02 | U/P |
| V7-OE-S042-A01-R03 | exclude |
| V7-PF-C-003-R03 | exclude |
| EXP-RF-006-R04 | N/N |
| V6R2-CA-008-ADD04 | P/N |
| V7-OE-S076-A01-R04 | N/N |
| V7-A-004-R05 | P/N |
| V7-OE-S043-A02-R04 | P/P |
| V7-OE-S090-A01-R05 | N/U |
| V7-OE-S023-A01-R03 | exclude |
| V6R2-CA-009-R03 | P/P |
| V6R2-EX-010-R06, V6-EX-027 | Giữ  V6-EX-027 N/P, loại V6R2-EX-010-R06 |