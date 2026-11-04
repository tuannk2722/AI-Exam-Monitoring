# Batch 03 — Phone còn khác biệt và crop lại

Đã áp batch 02, gồm câu trả lời chat **B03 N/P**. Hiện có **1.166 candidate cũ + 153 ảnh mới**; đây chưa là release. Bản hợp nhất hiện hành: [reconciled-review-r4.json](reconciled-review-r4.json); ảnh mới: [additional-annotations-draft-r3.json](additional-annotations-draft-r3.json).

Thứ tự nhãn **Phone / Looking**. Anh có thể duyệt từng nhóm và chỉ ghi ngoại lệ, nhưng cần một câu duyệt tường minh cho nhóm; ô trống không tự là đồng ý. Không cần review lại batch 01/02.

## A. Áp quy tắc khuất tay/bàn — thông tin đã thực hiện

Đã rà 121 candidate cũ còn phone U. 22 crop không thấy phone/vật nghi phone được chuyển sang N theo [policy anh vừa chốt](owner-policy-20261023.md), không đổi Looking. 10 crop ở nhóm B dưới đây vẫn giữ U trong r4, chờ quyết định. 89 crop khác giữ U vì còn vật cần phân biệt; việc giữ lại chưa là nghiệm thu release.

22 ID đã đổi: E004-CN-043, E004-EX-C184, EXP-SCB-030, G02-A02-F00009-R02, G11-B09-F00008, G2-A09-F001, G4-A02-F125, G5-A11-F047, NB-0023, SCB-read-015, SCB-read-028, SCB-turnhead-005, SCB-write-015, V6-CA-034, V6-EX-038, V6R2-MP-017, V6R2-MP-050, V6R2-MP-072, V7-C-001-R03, V7-C-009-R03, V7-C-039, V7-D-053. [Audit từng dòng và SHA](phone-policy-audit.json).

Ở ảnh mới, 13 dòng phone U do occlusion đã đổi thành N trong r3, gồm NEW-010 N/N đúng quyết định riêng của anh. NEW-021, NEW-057, NEW-150 đã loại; giữ cả NEW-120 và NEW-122. Không đưa lại các crop review_only cũ đã bỏ.

## B. 10 ca có dáng điện thoại nhưng hiện còn U

Tôi đề xuất **P/N cho cả 10 crop** dưới đây theo hình dáng vật và cách tương tác. Tôi không dựa riêng vào tư thế tay trống. Cần anh đối chiếu vì nhãn U hiện có có thể phản ánh một vật khác mà anh đã nhận ra; đề xuất chưa ghi đè.

![B01–B05, trái sang phải](../../../data/interim/v12-reconcile-20261022/boards/phone-positive-review-01.jpg)
![B06–B10, trái sang phải](../../../data/interim/v12-reconcile-20261022/boards/phone-positive-review-02.jpg)

| Câu | Crop | Điểm cần đối chiếu | Quyết định owner |
|---|---|---|---|
| B01 | V7-A-004-ADD02 | Vật mỏng dài được cầm phía trên bài, ngón tay tương tác mặt trước | Approve |
| B02 | V7-B-001 | Cầm vật nhỏ dạng phone ngay phía trên vở | U/N |
| B03 | V7-B-031-R03 | Vật trắng dựng đứng trong hai tay, ngón tay thao tác mặt trước | Approve |
| B04 | V7-B-047 | Vật đen cầm thấp trên bàn, hai tay thao tác | U/N |
| B05 | V7-B-057 | Vật chữ nhật nhỏ cầm ngang trên sách | U/N |
| B06 | V7-B-077-R03 | Vật đen mỏng cầm bằng hai tay | U/N |
| B07 | V7-D-051 | Vật nhỏ có viền màu, một tay cầm và một tay chạm | U/N |
| B08 | V7-OE-S104-A01 | Vật mỏng đặt ngang trong tay đưa gần miệng | U/N |
| B09 | V7-OE-S108-A01 | Vật mỏng áp tai, cạnh vật lộ bên bàn tay | U/N |
| B10 | V7-OE-S111-A01-R03 | Một tay cầm vật áp tai trong khi tay kia viết | U/N |

**Quyết định chung nhóm B (hoặc ghi ngoại lệ theo ID):**

## C. Hai crop cần chỉ rõ người mục tiêu

![C01 bên trái, C02 bên phải](../../../data/interim/v12-reconcile-20261022/boards/anchor-questions-03.jpg)

Hai crop đang N/N; tôi chưa đổi nhãn hoặc pixels. Person box cũ bao vùng có nhiều người gần nhau, không đủ chắc để tự thu hẹp vào một người.

| Câu | Crop | Cần anh chỉ rõ | Trả lời owner |
|---|---|---|---|
| C01 | G07-B12-F00029 | Người đeo kính ở tiền cảnh bên trái, hay người tóc buộc ở giữa? | người tóc buộc ở giữa, crop lại sao cho khít người đó và ít bị dính những bạn xung quanh |
| C02 | G22-B16-F00034 | Người bên trái chỉ thấy một phần mặt/tay, hay người tóc buộc bên phải? | người tóc buộc bên phải, crop lại sao cho khít người đó và ít bị dính bạn ngồi cạnh. Cũng cần xem xét là phone N hiện có hợp lý với toàn bộ quyết định phone hiện tại không |

## D. Duyệt theo batch 52 crop đề xuất

Đã xử lý 52/54 yêu cầu geometry; 2 crop chờ nhóm C. Đây là crop hình chữ nhật từ pixels hiện có, không tạo thêm nội dung. Đã xem lại toàn bộ preview 224; đầu/tay/vật liên quan được giữ để đánh giá nhãn. Một số người chồng lấn vẫn còn vì không thể bỏ bằng crop chữ nhật mà giữ đủ evidence. Không kéo méo hoặc dùng ảnh tạo sinh để xóa người.

[Biên crop và SHA output](geometry-proposals.json), [tọa độ dự thảo](geometry-boxes-draft.json). Ảnh đầu vào chuẩn 224 dùng hàm preview và màu padding của bàn audit hiện có. Nhãn in trên bảng là nhãn đang dùng/đề xuất kế thừa, chưa là acceptance mới. V7-B-061 còn U/N cho tới quyết định riêng; không nằm trong 10 đề xuất nhóm B.

V7-D-042: rút nhận định trước rằng có màn hình phone. Giữ N/N theo xác nhận bút/sổ của anh; crop đề xuất bớt phần laptop bên phải và dưới, vẫn giữ vùng sổ và tay. Chưa có bằng chứng thực nghiệm để kết luận ảnh này gây hại model; không loại chỉ từ suy đoán đó.

![Crop 01–08](../../../data/interim/v12-reconcile-20261022/geometry-proposals/after-224-01.jpg)
![Crop 09–16](../../../data/interim/v12-reconcile-20261022/geometry-proposals/after-224-02.jpg)
![Crop 17–24](../../../data/interim/v12-reconcile-20261022/geometry-proposals/after-224-03.jpg)
![Crop 25–32](../../../data/interim/v12-reconcile-20261022/geometry-proposals/after-224-04.jpg)
![Crop 33–40](../../../data/interim/v12-reconcile-20261022/geometry-proposals/after-224-05.jpg)
![Crop 41–48](../../../data/interim/v12-reconcile-20261022/geometry-proposals/after-224-06.jpg)
![Crop 49–52](../../../data/interim/v12-reconcile-20261022/geometry-proposals/after-224-07.jpg)

**Quyết định chung nhóm D (duyệt batch hoặc ghi ID cần sửa/loại):** Những crop cần sửa E004-EX-C043 U/N, E004-EX-C184 U/N, E004-EX-C190 U/N, NB-0031 exclude. Còn lại approve

Đã kiểm lại 1.319 candidate khi thay bằng 52 crop đề xuất: không trùng bytes/RGB; không thêm cặp dHash ≤ 6 liên quan các crop đổi pixels. Đây chỉ là kiểm kỹ thuật và shortlist, không chứng minh đã sạch gần trùng toàn cục. [Kết quả](geometry-duplicate-check.json).

Sau batch này vẫn cần hoàn thiện person geometry/lineage ảnh mới, đối chiếu nearest/cross-source còn lại, gắn evidence đúng SHA và tổng hợp coverage. Chưa chia split hoặc lập release để tránh chốt trước dữ liệu.
