# Audit legacy V11 — R2

**Đã review riêng 836/836 crop; kết luận là Draft chờ owner nghiệm thu batch.** R2 thay đề xuất R1 cho phạm vi này sau phản hồi về phone, looking và anchor. R1 giữ nguyên bytes để truy vết. Đây là audit và đề xuất, chưa phải dataset revision.

Phạm vi owner chọn: 765 crop baseline V9 + 71 development cùng thời kỳ, hiện là 644 train + 192 val V11; cùng tiêu chí cho cả hai split. Không mở test/reserve. Branch: `audit/v11-legacy-crops-20261018`.

## Kết quả

| Đề xuất | Số crop | Ý nghĩa |
|---|---:|---|
| Giữ geometry | 537 | Duyệt nhãn R2 trên crop hiện tại |
| Sửa geometry rồi review lại | 250 | Tạm rút crop hiện tại; chưa có crop thay thế được duyệt |
| Rút supervision | 49 | Không đủ evidence/geometry phù hợp để giữ hiện tại |

Đã kiểm tra chéo toàn bộ 64 ứng viên phone P trên native và PNG input 224: chuyển 3 ca sang U, còn 61 P trong toàn cohort, kể cả các khung đang cần sửa. Không có crop giữ geometry với U/U. Xem số lượng nhãn thay đổi và so sánh R1 trong [summary.json](summary.json).

## Xem từng crop

- [Gallery R2: source, native và PNG 224; lọc ID/xử lý](../../../../data/interim/v11-legacy-crop-audit-20261018-r2/index.html).
- [DECISIONS R2 — đủ 836 ID và lý do](DECISIONS.md), [JSON có nhãn V11/R1/R2](decisions.json), [ghi chú thủ công](review-notes.psv).
- [Rubric và các quyết định Accepted áp dụng](RUBRIC.md), [kiểm tra chéo phone P](phone-confirmation.md).
- [Kiểm tra toàn vẹn/coverage](validation.json), [SHA media](media-checksums.sha256), [pins bảo toàn R1](parent-pins.json).

File `../DECISIONS.md` đang mở trong IDE là **R1**. Kết quả mới ở **`r2/DECISIONS.md`** và gallery có hậu tố **`-r2`**.

## Evidence và giới hạn

Mỗi crop có một ghi chú riêng, tham chiếu bảng/ô source–native–input; không dùng nhãn R1 làm fallback. Bảng tổng quan JPEG phục vụ xem cùng context; kiểm tra chéo phone P dùng PNG input không mất chất lượng. Source thumbnail R1 được tái sử dụng sau kiểm pin; R1 đã đối chiếu 836 ROI với 718 source blob đúng SHA. Crop V4–V9 cũ đã retire, audit dùng bytes V11 hiện hành của đúng cohort.

`observed_states` mô tả evidence trên khung hiện tại. `proposed_supervision_states` chỉ có giá trị cho `keep`; recrop/exclude là null. Lý do từng ID và mã geometry chỉ rõ vấn đề cần xử lý, **không chứng minh đã có geometry thay thế đạt chuẩn**. Chưa tạo 250 crop mới, chưa thay accepted labels/geometry/membership, chưa train/inference/test hoặc commit/push. Gallery kiểm dữ liệu/links và cú pháp JavaScript; chưa có kiểm render qua browser.

Bước sau audit: owner nghiệm thu batch và ngoại lệ; với nhóm recrop, tạo derivative ở revision riêng rồi kiểm lại cả hai nhãn trước enrollment. Nếu thử khung vẫn thiếu evidence/anchor thì rút crop, không ép giữ số lượng. Approval dataset/release mới vẫn cần đúng scope theo AGENTS; báo cáo này không thay approval.
