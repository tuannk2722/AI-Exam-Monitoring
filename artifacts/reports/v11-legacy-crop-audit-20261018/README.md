# Audit 836 crop lịch sử trong V11 — 18/10/2026

**Hoàn tất audit; đề xuất Draft, chưa owner nghiệm thu và chưa sửa dataset.** Branch `audit/v11-legacy-crops-20261018`. Đã xem từng crop ở native và input 224 × 224; áp dụng rubric sau V9 cho phạm vi owner chọn.

Mở [gallery local](../../../data/interim/v11-legacy-crop-audit-20261018/index.html) để lọc theo hành động, thay nhãn, nguồn hoặc ID. Có crop gốc, input PNG, source có khung và các board đã dùng để review. [Bảng từng crop](DECISIONS.md) đọc được ngay trong Git; [decisions.json](decisions.json) là dữ liệu đề xuất, không phải manifest enrollment. Thứ tự mọi cặp nhãn: **phone_use / looking_around**.

## Phạm vi và kết quả

Owner chọn **836 crop: 765 baseline V9 (716 train + 49 val lúc V9) và 71 development cùng thời kỳ**. Tất cả vẫn có trong V11, hiện là 644 train + 192 val; review không phân biệt vai trò. Baseline hiện 576 train + 189 val; development hiện 68 train + 3 val. Không mở test 11 hoặc reserve holdout. Đây là audit cohort đã chọn, không phải audit toàn bộ 1.451 train/val V11.

| Đề xuất | Số crop | Train hiện tại | Val hiện tại | Ý nghĩa |
|---|---:|---:|---:|---|
| Giữ geometry | 707 | 552 | 155 | 334 giữ cả nhãn; 373 có đề xuất đổi ít nhất một target |
| Sửa geometry, duyệt lại | 93 | 63 | 30 | Đề xuất withheld crop hiện tại; chưa có khung mới được nghiệm thu |
| Rút khỏi supervision | 36 | 29 | 7 | 35 ca U/U; 1 ca có dải ảnh ghép gây lỗi chất lượng |
| Tổng | 836 | 644 | 192 | Mỗi ID có một quyết định cuối và evidence |

`keep` chỉ đề xuất giữ khung, không đồng nghĩa giữ nhãn cũ hoặc đã Accepted. `recrop` không cam kết cứu được mẫu: chọn đúng một anchor, giữ đủ đầu/tay/vùng bài, render lại input rồi duyệt mới. Nhãn ghi tại các ca này mô tả evidence của crop hiện tại, **không truyền sang geometry mới**. `exclude` là rút supervision trong một revision tương lai, không xóa raw/source hoặc sửa V11.

## Những vấn đề cần xử lý trước

1. **Nhãn phone cũ còn dựa vào khối chữ nhật/lưng trơn hoặc thiếu kiểm absence.** Trong 707 ca đề xuất giữ geometry, có 82 P → U vì mất đặc trưng mobile, 32 N → U vì tay/vật mơ hồ, 19 P → N khi vật/vùng thao tác đủ loại mobile; chiều ngược lại có 115 U → N và 3 U → P. Đây là đánh giá thủ công theo evidence hiện tại, không là tỷ lệ lỗi ground truth đã nghiệm thu. Ví dụ `V7-B-086`: thiết bị là điện thoại bàn, không phải mobile; `V6R2-MP-040`: chỉ còn mặt/lưng mờ tại input, không nâng P từ tư thế cầm.
2. **Looking còn nhiều U lịch sử dù hướng đầu và vùng bài đủ rõ.** Trong nhóm giữ khung, đề xuất 157 U → N và 28 U → P; đồng thời có 17 P → N, 15 N → P và 5 known → U. Xét độc lập với phone; nhìn phone của chính mình có thể là looking N. Không yêu cầu con ngươi, không tự N vì đang cầm bút, không suy gaze từ tư thế ngủ.
3. **Person box bao nhóm hoặc attribution chưa đủ rõ.** Ví dụ `E004-EX-C089`, `E004-CN-052`, `V7-B-062`: cần khung một người rồi duyệt lại. Không loại tất cả ảnh có nhiều người: `E004-CN-053` và `V7-B-016` vẫn có anchor/vùng bài đọc được. Danh sách 93 ca và hướng sửa nằm trong bảng quyết định; chưa thực hiện recrop trong lượt audit này.
4. **Crop quá mờ/che khuất hoặc source không có pixels để cứu.** 35 ca U/U đề xuất rút supervision. Kích thước chỉ là evidence mô tả, không là cutoff. Kiểm cuối đã giữ lại `EXP-SCB-024` (U/P) và `SCB-read-019` (U/N), dù nhỏ, vì còn đọc được một target. `V6R2-MP-008` đã mất mặt ở mép source nên nới crop không phục hồi được.
5. **Source ghép cần xử lý riêng.** `V6-EX-030` có dải cảnh khác ở đáy, thấy trong source và crop. Đề xuất loại crop hiện tại; không tự inpaint hoặc hợp thức hóa bằng nhãn có thể đọc ở phần trên.

Nên nghiệm thu theo ba nhóm trong gallery, ưu tiên 93 geometry và 36 loại, sau đó nhóm 373 giữ khung nhưng đổi nhãn. Owner chỉ cần chốt batch và các ngoại lệ. Sau nghiệm thu mới chuẩn bị revision dataset mới, kiểm coverage/rights/group/masks/normal-context và allocation đúng scope; không tự mở training hoặc thay accepted split.

## Rubric và cách kiểm

[Rubric áp dụng và traceability](RUBRIC.md) tổng hợp tiêu chí sau V9, gồm [quy tắc mobile/absence](../E004-device-consistency-20261015/rubric.md), [ngoại lệ che hoàn toàn được owner duyệt](../E004-device-consistency-20261015/owner-direction.md), cùng các vòng crop closure/owner review ngày 15–17/10. Không đặt threshold pixel/confidence hoặc quota giữ/loại mới.

- Lượt đầu đủ 836 crop trên 70 board native/input, ẩn nhãn và scores trong hình. Lượt sâu gồm 259 ca `inspect`/`recrop`, trên 44 board source/native/input; nhãn cũ chỉ hiện ở lượt sâu để đối chiếu. Kiểm lại riêng toàn bộ 38 ca từng đề xuất loại trên 7 board source/native/input, đổi quyết định của 2 ca. Không dùng prediction/model score để chọn nhãn.
- V11 crop của cohort trùng source/geometry/labels lịch sử V9. Xác minh SHA và kích thước từng crop; 836 ROI có RGB đúng với source tương ứng trong archive đã pin, 718 source duy nhất. Source chỉ đọc theo SHA của cohort. [Input pins](input-pins.json), [kiểm source](source-validation.json), [lineage từng crop](cohort.json).
- Input dùng `source_review.preview_input`: RGB, bilinear, letterbox 224 × 224, fill `(124, 116, 104)`. PNG gallery được đối chiếu hash RGB, không sharpen/inpaint. Source thumbnail để kiểm khung/attribution; không gán known target nhờ chi tiết mất sau resize. Audit này xét input crop 224 theo rubric dữ liệu, không mô phỏng mọi augmented/anchor view của E005.
- Kiểm trùng **trong 836 crop**: không có nhóm native RGB hoặc input RGB trùng hoàn toàn; không có cùng source SHA hoặc cùng leakage group đi qua cả train/val. [Overlap inventory](overlap.json) vẫn liệt kê các crop chung source. Điều này không chứng minh độc lập người/scene/session, không thay đánh giá near-duplicate toàn V11. Không đổi grouping/split hoặc chọn bớt frame bằng ngưỡng tự đặt.

## Evidence, tái lập và giới hạn

[summary.json](summary.json) giữ thống kê và chuyển nhãn; [visual-notes.psv](visual-notes.psv), [deep-notes.psv](deep-notes.psv), [deep-index.json](deep-index.json), [confirmation-notes.json](confirmation-notes.json) giữ evidence các lượt. Quyết định cuối ưu tiên confirmation → deep → lượt đầu; không sửa ghi chú cũ để che thay đổi nhận định. Tất cả là agent Draft, không phải owner annotation/acceptance và không là accuracy/model evaluation.

Gallery/media nằm ở `data/interim/v11-legacy-crop-audit-20261018`, pointer [review-pointer.json](review-pointer.json). Metadata/source worksheet ở report, media không vào Git và không upload. Board review thực tế được bảo toàn tại `boards/`; scratch đã dọn sau khi kiểm SHA khớp 114 bản giữ lại. SHA media tại [media-checksums.sha256](media-checksums.sha256). [Kết quả kiểm artifact](validation.json) ghi coverage, hash và giới hạn kiểm gallery; [software checks](software-checks.json) giữ lệnh/tests và scope cleanup.

Worksheet dùng môi trường `.venv` hiện có, không cài thêm package:

```powershell
.venv/Scripts/python.exe -X utf8 artifacts/reports/v11-legacy-crop-audit-20261018/prepare.py
.venv/Scripts/python.exe -X utf8 artifacts/reports/v11-legacy-crop-audit-20261018/deep_review.py
.venv/Scripts/python.exe -X utf8 artifacts/reports/v11-legacy-crop-audit-20261018/package_review.py
```

Cần V11 crop bytes và `archive/e004-v9-consolidation-20261013.zip` đúng pin. Các lệnh dựng preview/tổng hợp lại **không tự thực hiện visual review** và không thay confirmation notes. Không mở lại archive khác hoặc restore retired release để lấp thiếu input.

Accepted V11 và receipts/config/run E005 giữ nguyên. Nếu owner chốt nhãn mới, metrics E005 cũ vẫn thuộc ground truth V11 cũ; không diễn giải chênh metrics như model gain trên cùng ground truth. Chưa đánh giá tác động chất lượng model, chưa có release mới, chưa commit/push.
