# Nghiệm thu phân bổ dataset và mức đạt — 17/10/2026

**Owner đã nghiệm thu phân bổ dataset và mức đạt sau train. Thiết kế/cách tiến hành train chưa được chốt và các đề xuất train vừa tạo đã được gỡ theo yêu cầu owner.**

[Receipt nghiệm thu và phạm vi](owner-acceptance.json) là nguồn quyết định hiện hành. Không lấy chữ Draft trong snapshot allocation hoặc hồ sơ kiểm trước nghiệm thu làm trạng thái approval hiện tại; cũng không suy approval dataset thành approval cách train.

## Phần đã nghiệm thu

| Tập | Crop | Phone P / N / U | Looking P / N / U | Nhóm phân bổ |
|---|---:|---|---|---:|
| Train | 1.185 | 323 / 411 / 451 | 318 / 678 / 189 | 274 |
| Validation | 266 | 72 / 96 / 98 | 74 / 146 / 46 | 155 |
| Tổng | 1.451 | 395 / 507 / 549 | 392 / 824 / 235 | 429 |

Tỷ lệ 81,7% / 18,3%, giữ nhóm nguồn nguyên khối. 270 crop mới chia **196 train / 74 validation**. Danh sách ID, nhóm và nhãn chính xác ở [allocation.json](allocation.json), SHA `8d8eaf076c25f10b4d74e37ac5d7416217441b101c7cbec484480e64d969e24e`. File được chuyển nguyên bytes từ vị trí config cũ; trạng thái Draft bên trong là lịch sử, được receipt hiện hành supersede riêng về nghiệm thu.

Pool gồm 1.061 train + 120 val C345 development và 270 crop owner đã duyệt. Không cộng thêm V10 lần nữa. 332 review-only, 29 excluded và 11 test của package hiện hành ngoài pool; không mở pixels/features/predictions của các records đó. Holdout để sau; test/reserve vẫn đóng.

Các parent groups, source/crop/RGB/video liên quan và quarantine cảnh nghi ngờ được giữ cùng phía như allocation đã duyệt. 429 nhóm là đơn vị phân bổ bảo thủ, không phải 429 lớp hoặc người độc lập được xác minh. Không đổi nhãn/crop accepted; U tiếp tục mask theo target.

[Gallery validation đã nghiệm thu phân bổ](../../../outputs/train-val-plan-20261017/index.html) tham chiếu crop hiện có, không nhân bản ảnh. **Đã triển khai thành [release V11](../dataset-release-20261017/README.md) theo yêu cầu owner sau nghiệm thu. V10 và C345 development vẫn giữ nguyên bytes và split.**

## Mức đạt và cách diễn giải kết quả

Ưu tiên owner: cân bằng báo nhầm và bỏ sót. Trên validation đã chốt, **mỗi target** phone_use và looking_around phải đạt:

- Precision ≥ 80%.
- Recall ≥ 80%.
- FPR ≤ 20%.
- Tối thiểu 30 P, 30 N và 5 nhóm có P, 5 nhóm có N để áp dụng cổng số liệu. Đây là điều kiện support, không chứng minh đủ power thống kê hoặc độc lập nguồn.

Cả hai target phải đạt; không dùng trung bình che target yếu. Báo P/N/U, TP/FP/FN/TN, precision/recall/F1/FPR/AP, macro masked BCE/AP khi có thể tính, denominator, kết quả từng nguồn và batch mới, lỗi FP/FN và giới hạn bất định. Metric không đủ điều kiện là null/INCONCLUSIVE; không biến U thành N hoặc thay thiếu support bằng PASS.

Riêng 74 crop mới: phone **10 P / 45 N / 19 U**, looking **25 P / 49 N / 0 U**. Không đủ support nói trên để kết luận đạt chắc riêng batch mới; vẫn phải báo kết quả và giới hạn. Chưa có census yếu tố calculator/occlusion được nghiệm thu cho toàn bộ validation; không bịa số lượng theo yếu tố từ nhãn N.

Mức đạt này áp dụng cho bằng chứng development trên validation đã chốt. Không tự là final test, holdout độc lập, nghiệm thu vận hành hoặc model Selected. **Ngưỡng xác suất dự đoán và protocol thực thi đánh giá cụ thể sẽ được xác định cùng thiết kế mới; receipt này không chốt chúng.** Không nhầm ngưỡng precision/recall/FPR đã duyệt với threshold biến score thành P/N.

## Phần đã gỡ và agent tiếp theo phải hiểu

Theo yêu cầu owner, đã bỏ thư mục proposal mới `configs/datasets/train-val-20261017` sau khi giữ allocation về report. README và evaluation proposal trong thư mục đó đã được retire; receipt giữ đường dẫn/hash để giải thích lịch sử, không giữ các nội dung đó làm hướng dẫn active.

Không còn đề xuất active cho model/pretrained/head, cách khởi tạo, tiêu chí chọn checkpoint, early stopping, threshold 0,5, recipe, config chạy, smoke, compute hoặc budget từ đợt lập kế hoạch này. Những điều này **chưa được owner nghiệm thu và không được tự kế thừa**. Không xóa hay thay các configs, runs, models lịch sử đã accepted/pin của dự án.

Một dữ kiện cần giữ để thiết kế mới đánh giá đúng: allocation có **178 train cũ chuyển val**, 106 val cũ chuyển train, 14 val cũ ở lại val và 883 train cũ ở lại train. Lịch sử một model đã tiếp xúc dữ liệu nào cần được khai báo khi diễn giải kết quả. Hồ sơ này ghi dữ kiện đó, không áp đặt cách khởi tạo hoặc kiến trúc train.

Agent tiếp theo:

1. Đọc [status](../../../docs/status.md), [registry](../../../docs/decisions.md), report này và receipt để nhận đúng phạm vi đã duyệt; không hỏi lại allocation hoặc mức đạt nếu không thay chúng.
2. Dùng [pointer V11](../dataset-release-20261017/package-pointers.json) cho dataset đã triển khai. Giữ nguyên danh sách ID/nhãn/crop và các giới hạn trên; không ghi đè package hoặc tự chia lại split.
3. Tiếp nhận thiết kế train mới từ owner. Không tự dựng lại proposal đã gỡ, không lấy cấu hình thí nghiệm cũ hoặc worksheet phân bổ làm chỉ dẫn train mới.
4. Chỉ tạo hồ sơ/config thực thi tương ứng khi thiết kế và quyền thực hiện đã rõ. Task cleanup này không cấp quyền train, smoke hoặc mở test/holdout.

## Bằng chứng còn giữ

- [Input pins](input-pins.json), [pool inventory](pool-inventory.json): provenance 1.451 crop, nhãn, SHA và nhóm nguồn.
- [Nearest cho 270 crop](nearest-existing.json), [cross-group triage](cross-group-triage.json), [visual review](visual-review.json): đã xem 25 representative frames, 7 parent scenes và 50 nearest pairs. Min dHash mới–cũ là 10, không cặp khác parent group trong pool có dHash ≤ 6; đây chỉ là triage, không chứng minh hết near-duplicates/độc lập session.
- [Validation trước nghiệm thu](validation.json) giữ nguyên bytes/pins. Field `evaluation_proposal_sha256` nay trỏ tới nội dung đã retire có chủ ý; không restore proposal hoặc sửa pin cũ để lấp chỗ trống.
- [Kiểm bàn giao sau cleanup](cleanup-validation.json): bảo toàn allocation/pins, phạm vi retire và đường dẫn hiện hành.
- `inventory.py` và `allocate.py` là worksheet phân tích dữ liệu, không phải pipeline train. `allocate.py` chỉ đối chiếu kết quả với allocation đã giữ, không ghi đè nó. Không tự chạy lại worksheet lịch sử như một bước tiếp theo của task.

Commit trạng thái trước khi lập phương án: **c00b159**. Không có train/smoke/enrollment nào được chạy trong đợt lập phương án hoặc cleanup này.
