# Đối soát review V12 — checkpoint 23/10/2026

**Đang audit, chưa chốt dataset hoặc kế hoạch release.** V12 và các pins gốc giữ nguyên.
Owner yêu cầu rà toàn bộ 1.639 crop, áp JSON theo delta, loại crop không dùng khỏi
release tương lai và kiểm 156 ảnh bổ sung trước khi lập kế hoạch release mới.

## Trạng thái sau quyết định batch 04

**Ảnh thay NEW-069 đã import xong**, cùng ID và N/N. Snapshot hiện hành sau import: [inventory 1.312 candidate](candidate-inventory-batch04-r2.json), [nhãn mới r7](additional-annotations-r7.json), [geometry mới r6](additional-geometry-r6.json), [lineage r3](additional-lineage-r3.json), [nhóm draft r2](leakage-groups-draft-r2.json). Tổng 1.163 crop cũ + 149 ảnh mới. Các mô tả thiếu file và số đếm ở checkpoint trước bên dưới đã superseded.

[Checks import](replacement-import-checks.json): toàn bộ candidate khớp SHA, không trùng bytes/RGB, pin ledger V12 nguyên. Tám ảnh gần nhất theo dHash đã xem và khác cảnh; NEW-069 mới/NEW-070/crop nguồn cùng họ cảnh nhưng khác thiết bị hoặc động tác tay. Giữ chung nhóm draft, không coi ảnh mới là độc lập. NEW-070 có phone và nhãn P/N; ảnh thay NEW-069 là calculator N/N. [Preview 224](../../../data/interim/v12-reconcile-20261022/boards/NEW-069-replacement-224.png) đã kiểm; chưa chốt release vì còn nghiệm thu geometry/grouping và giới hạn lineage nêu dưới.

Đã áp quyết định trong owner-review-batch-04.md và làm rõ mục C qua chat: giữ NEW-012 N/N, loại G2-A01-F001; giữ CB-0405 U/N, loại NEW-052; giữ NEW-056 P/N, loại G13-B03-F00010. NEW-025 chốt U/N theo phần D. E004-EX-C184 hiện là **N/N**, không có ngoại lệ phone U.

Snapshot hiện hành: [crop cũ r8](reconciled-review-r8.json), [nhãn mới r6](additional-annotations-draft-r6.json), [geometry mới r5](additional-geometry-draft-r5.json). Có 1.163 candidate cũ và 148 ảnh mới đang có bytes; NEW-069 cũ đã loại, sẽ thay bằng ảnh chat mới **cùng mã NEW-069, N/N**. Chưa có file bytes của ảnh thay thế; sau import dự kiến tổng 1.312 candidate, trước QA cuối.

Đã duyệt hai recrop theo anchor ở phần A. [Geometry 53 recrop cũ](old-recrop-geometry-draft-r2.json) đã chuyển tọa độ và kiểm thị giác, sửa 12 bbox thiếu phần đầu/tay/chân; không đổi pixels crop. [Bảng kiểm lại](../../../data/interim/v12-reconcile-20261022/boards/old-recrop-geometry-corrections.jpg). Đây là draft geometry, chưa tự cấp release acceptance.

[Đề xuất nhóm chống leakage](leakage-groups-draft.json) có 334 nhóm cho 1.311 candidate hiện có bytes. Dùng lineage V12 và liên hệ cảnh đã xem, nối qua ID bị loại chỉ để giữ quan hệ nguồn; các ID bị loại không là thành viên candidate. Chưa chia split; còn giới hạn 22 ảnh/8 họ cảnh chưa xác định parent cũ, nên chưa chốt nhóm hoặc release.

Các checkpoint bên dưới là lịch sử; trạng thái sau batch 04 ở trên có ưu tiên khi tiếp tục.

## Input và quy tắc áp dụng
Checkpoint hiện hành: **[Batch 04 cần owner review](owner-review-batch-04.md)** gồm hai recrop, hai đề xuất nhãn, ba đề xuất loại gần lặp và nghiệm thu chung ảnh mới. Các kết quả vòng trước bên dưới giữ làm lịch sử; dùng snapshot hiện hành sau đây khi tiếp tục:

- [Reconciled r6](reconciled-review-r6.json): 1.165 candidate cũ, 474 remove; đã áp batch 03 và [ngoại lệ E004-EX-C184 U/N](batch03-chat-addendum.json).
- [51 recrop được duyệt](geometry-approved-batch03.json), [hai recrop theo anchor](geometry-anchor-batch03.json) còn chờ nghiệm thu. Crop approval không tự chốt bbox người cho release.
- [Nhãn mới r4](additional-annotations-draft-r4.json), [geometry mới r3](additional-geometry-draft-r3.json): đủ 156 ảnh, hiện giữ 153; chưa áp đề xuất loại NEW-012/052/056, chưa owner nghiệm thu toàn bộ nhãn mới.
- [153 cặp gần trùng mở rộng](dedup-expanded-visual-screen.json) đã xem; đính chính NEW-052 từ vòng trước. [Checks](batch03-checks.json): 1.318 candidate không trùng bytes/RGB, 53 crop khớp ROI, bounds/pins 156 ảnh hợp lệ, ledger V12 nguyên pin. Không suy thành bảo đảm sạch mọi dạng gần trùng.
- [Lineage r2](additional-lineage-draft-r2.json): 134 ảnh có họ cảnh cũ đối chiếu thị giác; 22 ảnh trong 8 họ cảnh chưa rõ parent. Không xác minh recipe hoặc duyệt group/split.

Sau batch 04 còn hoàn thiện person geometry của recrop cũ, hợp nhất nhóm liên quan và QA candidate cuối trước tổng hợp coverage/kế hoạch release.


[Inputs/pins](inputs.json) ghi SHA của bản JSON và ZIP đã sao chép byte-exact vào
`data/interim/v12-reconcile-20261022/inputs`. JSON khớp cohort, đủ inventory ID/SHA
và ledger V12 đã pin. Mục không xuất hiện hoặc trường nhãn để trống kế thừa V12;
P/N/U tường minh ghi đè, không dùng `done=false` để phủ nhận review của owner.

- Looking P khi quay hẳn sang bên/sau; hơi chéo nhưng nhìn bài người khác cũng P.
  Đầu thẳng hoặc hơi chéo còn lại N khi đủ quan sát; thiếu evidence giữ U.
- Phone: owner xác nhận thêm trong hội thoại ngày 22/10: **U nếu chưa phân biệt
  được phone với vật khác**. Không gán P chỉ từ tư thế tay mơ hồ.
- Không suy nhãn từ tên file ZIP. Ảnh được owner mô tả là generate từ crop hiện tại;
  lineage phải đối chiếu bằng ảnh/evidence, chưa xác nhận recipe tạo ảnh. Không tự
  coi ảnh bổ sung là quan sát độc lập hoặc đưa sang split mới.
- Ghi chú crop lại cũng là yêu cầu, kể cả nút action để trống/keep. Crop mới đổi
  pixels phải được kiểm evidence/geometry lại, không tự kế thừa crop acceptance cũ.

## Đối soát kỹ thuật đã hoàn thành

| Hạng mục | Kết quả |
|---|---:|
| Crop V12 approved trong phạm vi | 1.639 |
| Mục JSON có nhập | 776 |
| ID không có mục JSON, kế thừa toàn bộ | 863 |
| Giữ theo action sau merge | 1.362 |
| Owner chọn remove | 248 |
| Owner chọn recrop | 29 |
| Crop có ghi chú | 54 |
| Hợp action recrop và ghi chú, cần kiểm geometry | 55 |
| Phone thay đổi state so với V12 | 288 |
| Looking thay đổi state so với V12 | 232 |
| Ảnh PNG mới decode được trong ZIP | 156 |
| Nhóm trùng bytes / RGB toàn bộ 1.795 ảnh | 0 / 0 |
| Cặp dHash distance ≤ 6, chỉ là shortlist | 91 |

[Review hợp nhất](reconciled-review.json), [ảnh bổ sung](additional-inventory.json),
[kiểm tiếp nhận](intake-checks.json), [sàng lọc trùng](duplicate-screen.json).
Giá trị U/U ở inventory ảnh mới là placeholder chưa annotation, không phải kết luận thị giác.

Đã đối chiếu source SHA toàn inventory: 282 nhóm cùng source, gồm 811 records;
cùng source có thể là **khác người** nên không tự loại. Không có cặp cùng source SHA
với person-box IoU ≥ 0,5 trong lần sàng lọc này. [Source overlap](source-overlap.json),
[anchor candidates](same-source-anchor-candidates.json). Các ngưỡng chỉ để tìm ca cần
xem, không là tiêu chí nghiệm thu hoặc bằng chứng không còn trùng. Đã thấy trực quan
cặp cùng ảnh/cùng anchor nhưng source SHA khác; vì vậy kiểm hash đơn thuần chưa đủ.

## Checkpoint hiện hành — 23/10/2026

Các số tiếp nhận phía trên là snapshot merge ban đầu. Đã áp batch 01/02, gồm B03
E004-EX-C026 N/P trả lời trong chat. [Receipt 01](batch01-receipt.json),
[receipt 02](batch02-receipt.json). File owner đã viết được giữ nguyên.

| Phần | Kết quả hiện hành | Evidence |
|---|---|---|
| Crop cũ | 1.137 keep, 29 recrop, 473 remove; 1.166 candidate | [r4](reconciled-review-r4.json) |
| Ảnh bổ sung | 153 keep, 3 remove: NEW-021, NEW-057, NEW-150; giữ NEW-120/122 | [Draft r3 đủ 156 dòng](additional-annotations-draft-r3.json) |
| Rà policy phone U cũ | 121 crop: đổi 22 sang N; 10 đề xuất P chưa áp; 89 giữ U | [Audit từng dòng](phone-policy-audit.json) |
| Phone U mới do occlusion | 13 dòng chuyển N, gồm NEW-010 theo quyết định riêng | [Receipt 02](batch02-receipt.json) |
| Geometry cũ | 52 crop đề xuất đã xem lại; 2 chờ chỉ rõ người mục tiêu | [Biên/pins](geometry-proposals.json) |
| Trùng sau thay 52 crop đề xuất | 1.319 candidate; 0 nhóm trùng bytes/RGB; 0 cặp dHash ≤ 6 liên quan pixels mới | [Kiểm](geometry-duplicate-check.json) |

[Policy owner ngày 23/10](owner-policy-20261023.md): khuất tay/bàn không tự là phone U;
không thấy phone/vật nghi phone thì N, có vật nhìn thấy chưa phân biệt được thì U.
Spec đã ghi phạm vi revision này; không hồi tố V12. 221 review_only không có ghi đè
nội dung đã rút và không được phục hồi. R2/r3 cũ giữ truy vết, không thay r4 hiện hành.

Đã sàng lọc 1.169 candidate cũ trước 3 quyết định loại thêm của batch 02; 1.166 hiện tại
đều nằm trong phạm vi đã xem. Đã xem 156 ảnh mới và bản 224, cùng 91 cặp shortlist.
[Đối chiếu cặp](duplicate-visual-screen.json). Không kết luận sạch gần trùng toàn cục.

**Cần owner review [batch 03](owner-review-batch-03.md)**: 10 đề xuất phone P, 2 anchor,
duyệt theo batch 52 recrop. Proposal chưa là accepted person geometry; review phải gắn
SHA mới. Preview 224 dùng `source_review.preview_input`, fill `[124, 116, 104]` như bàn
audit. V7-D-042 giữ N/N theo bút/sổ owner xác nhận; rút suy đoán màn hình phone trước đó.
Nghiên cứu thiết bị trước đó vẫn giữ NB-0003/NB-0007 N/N và EXP-SCB-021 N/P.

## Checkpoint trước batch 01 — đã được thay thế bởi mục hiện hành

Đã xem lượt sàng lọc **300 / 1.639 crop cũ** (boards existing 001–015), toàn bộ
**156 / 156 ảnh mới** (additional 001–008), cùng các bảng phóng lớn detail/pairs/questions.
Chưa hoàn tất rà native và input 224 từng ảnh, annotation ảnh mới, xử lý geometry,
hoặc đối chiếu hết các cặp gần trùng. Không ghi các ảnh chưa xem là đã PASS.

[Batch 01: 9 câu hỏi, 12 crop](owner-review-batch-01.md) gồm ca nhãn và trùng lặp
đã được xem phóng lớn. Các đề xuất ở đó **chưa ghi đè owner delta**. Có thể trả lời
theo Q01–Q09; các phần không phụ thuộc quyết định này tiếp tục được audit.

## Checks và bước tiếp

Module `data.review_reconcile` dùng strict PilotRecord để đối chiếu ledger;
5 regression tests kiểm kế thừa/explicit U/done=false/pins/ID/RGB shape/review_only PASS;
Ruff và mypy phần source mới PASS trong lần thực thi trước gián đoạn.
Chưa có validation cho release vì chưa tạo release. Không train/inference/upload.

Tiếp theo: áp owner batch 03; hoàn thiện geometry/person anchor 153 ảnh mới và 2 ngoại lệ;
nearest/cross-source ngoài shortlist, lineage/grouping và QA crop cuối. Chỉ tổng hợp
coverage/membership/kế hoạch release sau khi chốt. Không phục hồi 418 excluded của V12.
Boards/proposals đang là evidence owner review nên giữ local, không đưa media vào Git.
[Checks checkpoint hiện hành](checkpoint-checks.json).
