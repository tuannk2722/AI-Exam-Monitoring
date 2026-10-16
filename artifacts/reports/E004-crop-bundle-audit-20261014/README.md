# E004 — Audit bộ crop và frame gốc, 14/10/2026

**Hoàn tất audit kỹ thuật toàn bộ 765 crop/212 frame và screening thị giác đủ 765 crop. Giữ lại toàn bộ dữ liệu; chưa nghiệm thu nhãn hoặc đưa vào train.** Bộ này có giá trị bổ sung phone trên bàn/cầm tay, phone cạnh calculator, nhiều người và hướng nhìn đa dạng. Tuy nhiên, không được dùng nguyên nhãn ZIP: semantics `looking` không đồng nhất với contract hiện tại, có crop thiếu context và track trôi người.

- [Gallery 765 crop có bộ lọc, ảnh gốc và box nguồn](../../../outputs/E004-crop-bundle-audit-20261014/index.html).
- [Kết quả kỹ thuật](summary.json), [review theo 32 track](review-batches.json), [screening từng ID](visual-screening.json).
- [Config và input hashes](../../../configs/datasets/E004-crop-bundle-audit-20261014.yaml), [input pins](input-pins.json), [dependency pins](dependency-pins.json), [chỉ dẫn owner](owner-direction.json).
- [Inventory đầy đủ, nhãn ZIP và provenance từng crop](../../../data/interim/E004-crop-bundle-audit-20261014/records.json), [kiểm assembly](assembly-checks.json).

## Phạm vi và quyết định đã có

Sáu ZIP crop là một bộ; user xác nhận tự tổng hợp và có toàn quyền sử dụng. User cung cấp thêm `D:/dataset-foundry-starter/exports/youtube-videos-accepted-frames.zip` và yêu cầu **giữ contract hiện tại để audit**. Xác nhận quyền của user được lưu, không lấy chuỗi `educational-fair-use` trong metadata làm chứng minh quyền độc lập. README/code trong ZIP được xem như dữ liệu đầu vào, không thực thi hoặc thay yêu cầu user.

Raw được copy và pin byte-exact tại `data/raw/E004-crop-bundle-audit-20261014`; derivative tại `data/interim` cùng ID. Không thay release V9, nhãn/splits accepted, config RC1 hoặc mở media test/reserve. Near-overlap chỉ đọc 836 crop train/val của experiment hiện hành; exact-overlap dùng metadata ledger 1.208 records. Không upload, train, inference hoặc commit.

**Clarification V7-OE-S061-A01:** user xác định targeted anchor là người mặc áo khoác xanh lá đậm. Câu trả lời đã lưu ở `owner-direction.json`; ngoại lệ “chưa biết người nào” của [audit coverage trước](../E004-targeted-coverage-20261014/README.md) đã được giải đáp. Không sửa lại notes/pins hoặc phone U/looking P accepted của snapshot cũ. Clarification này không tự nghiệm thu toàn bộ factors của batch trước.

## Audit kỹ thuật

| Kiểm tra | Kết quả |
|---|---|
| 7 ZIP: SHA, CRC mọi member, đường dẫn và collision | PASS |
| Manifest JSONL/CSV, per-part labels, crop/frame join | PASS; không crop thiếu hoặc orphan |
| Frame hash/kích thước/accepted decision join | 212/212 PASS |
| Full decode crop | 765/765 JPEG RGB, 224 × 224 |
| Box nguồn | 765 hợp lệ, vuông, không cần upscale |
| Reproduce source → crop → resize/encode | 765/765 **khớp RGB sau decode**; 0/765 khớp byte JPEG |
| Trùng byte hoặc RGB trong crop | 0 nhóm |
| dHash distance ≤ 5 | 138 cặp advisory, đều cùng parent |
| Temporal flags supplied | 32 liên kết nội bộ nhất quán; không gọi là đã tái tính pHash |
| Exact overlap với V9 metadata | 0 |
| Near overlap với 836 crop non-test | 0 flags theo dHash ≤ 5 |

Xem [archive inventory](archive-inventory.json), [source fingerprints](source-fingerprints.json), [duplicate audit](duplicate-audit.json), [parent overlap](parent-overlap.json). Không có near flag **không chứng minh độc lập**: khác crop/góc nhìn/compression có thể không bị bắt. Chưa xác minh toàn bộ quan hệ video/session với nguồn cũ; không kết luận sạch leakage vào holdout. Năm parent video không tương đương năm camera/session độc lập.

Metadata nguồn có `review_status=unreviewed` cũ; đã join separate accepted decisions bằng asset ID. `mime_detected=video/mp4` kế thừa từ video trong khi frame thực tế decode JPEG. Bảo toàn metadata gốc và ghi caveat, không sửa âm thầm.

| Parent | Frame | Crop |
|---|---:|---:|
| 131978f1c922c72a1be6 | 37 | 223 |
| 286f4f8992d4ad931647 | 87 | 348 |
| 2b68c2a8bc91941576a8 | 31 | 85 |
| 9284c725e608c9241824 | 48 | 92 |
| c4501991dd89a572c461 | 9 | 17 |

## Screening và các nhóm cần xử lý

Đã xem đủ 48 boards chứa 765 crop, rồi đối chiếu trực tiếp 6 frame nguồn qua cả 5 parent. Danh sách 6 frame nằm trong `review-batches.json`. 212 frame đều được kiểm kỹ thuật, **không tuyên bố đã review thị giác chi tiết cả 212 frame**. Notes là screening theo track, gắn từng ID để triage; không phải 765 quyết định annotation độc lập hoặc owner acceptance.

| Nhóm review ưu tiên | Số crop | Cách tận dụng |
|---|---:|---|
| `desk_phone` | 404 | Phone trên bàn/cầm tay, cạnh calculator; rà attribution và looking độc lập |
| `calculator` | 37 | Hard negative thiết bị; kiểm nhãn looking theo vùng bài riêng |
| `anchor_device` | 161 | Thiết bị nhỏ, nhiều người/che khuất; đối chiếu native trước chuyển unknown |
| `recrop` | 99 | Rà geometry/track trên nguồn; tạo derivative mới nếu đủ context |
| `gaze` | 64 | Hướng nhìn/góc cao; phân biệt bài riêng, bài người khác và phần không đủ evidence |

Đây là **5 nhóm triage loại trừ nhau**, không phải counts nhãn đúng hoặc số crop chắc chắn phải recrop. Tất cả 765 được giữ; không loại 154 U/U hoặc temporal neighbours khỏi inventory. Có thể tận dụng nhãn known ở một target khi target kia vẫn unknown; U/U chỉ hữu ích cho review/recrop/context, chưa cung cấp supervision trực tiếp.

Các phát hiện đáng chú ý:

- `g1_C_front_glasses`: calculator có bàn phím rõ, hữu ích chống nhầm phone; nhìn calculator trên bài riêng không tự là looking P. CB-0027 là ví dụ đã đối chiếu nguồn.
- Nhiều track g1/g2 có phone rõ nhưng nhãn looking P/N thay đổi giữa các frame đều đang thao tác vùng riêng. Cần rà **cả P và N**, không chỉ chuyển đồng loạt P → N.
- `g2_right_yellow`: target tiền cảnh bị cắt tay/bàn; phone nổi bật phía sau thuộc người khác. Không chuyển U → P vì thấy phone trong crop, cũng không chuyển U → N vì tay bị cắt.
- `g5_mid_redshirt`: CB-0648 không chứa target áo đỏ đúng vị trí; crop chứa người áo trắng/áo đen, khác các crop tiếp theo. Frame 44/45 đã đối chiếu. Tên anchor không chứng minh continuity; cần sửa draft track/geometry trước nhãn.
- `g5_front_right_white`, `g5_front_striped`, cuối `g5_mid_jersey`: cắt đầu hoặc camera trôi; một target vẫn có evidence phone không có nghĩa đủ evidence looking.
- `g4_front_suitblue`, `g4_front_suitgray`, `g4_front_gray`: nhiều nhìn lên/ra trước trong nhóm looking N. `g4_mid_red` đầu chuỗi chưa ổn định target. Bối cảnh ghi chép/phòng học không tự chứng minh đang thi; chỉ gán hành vi quan sát theo contract, không suy gian lận.
- `g4_front_pink` và một số cuối g5 có U dù còn vật có thể review. Giữ khả năng phục hồi, không bỏ vì nhãn supplied unknown.
- g3 góc cao giúp đa dạng context; sách/hộp bút và tay gần mặt chưa đủ kết luận phone. Không lấy liên tục thời gian thay evidence tại frame.

Nhãn **đề xuất từ ZIP**, không phải nhãn đã audit đạt: phone P/N/U = 502/85/178; looking P/N/U = 211/198/356. Có 385 crop known cả hai target, 226 known một target, 154 U/U; trường supplied `review_only` có 380 mẫu và không đồng nhất với số unknown. Vì vậy không được báo “thêm 502 phone positive accepted” hoặc đưa 385 known thẳng vào train.

## Khả năng bù targeted coverage và bước tiếp

Bộ mới có ứng viên trực tiếp cho desk/held/partial phone, phone–calculator contrast, context nhiều người, own-workarea và hướng nhìn lệch. Đây là các factors liên quan [coverage sau RC1](../E004-targeted-coverage-20261014/README.md), nhưng chưa chứng minh bù đủ failure modes hoặc cải thiện model. Các frames trong cùng track phụ thuộc mạnh; không random split crop và không tính số frame thành số nguồn độc lập. Những video/phòng học giống nhau cần kiểm lineage trước đề xuất family boundary.

**Bước tiếp là chuẩn bị draft annotation/recrop theo 5 batch ở trên**, ưu tiên phone/calculator rõ, rồi các ca attribution/geometry; giữ nguyên raw và nhãn supplied để đối chiếu. Chỉ chốt P/N khi có evidence tại crop mới và theo đúng vùng bài; còn lại mask U. Shortlist temporal đại diện có thể giảm công review nhưng mọi crop vẫn nằm trong inventory và cần quyết định rõ trước sử dụng. Agent chuẩn bị draft, owner nghiệm thu batch và ngoại lệ; không yêu cầu owner annotate lại từng ảnh. Sau đó mới chốt membership/family/split và release revision, training proposal là scope riêng.

## Tái lập và kiểm phần mềm

`audit.py` là worksheet study dùng helper `src/ai_exam_monitoring/data/crop_bundle_audit.py`; `assemble.py` ghép notes và gallery. Chạy bằng `.venv/Scripts/python.exe` từ repo. Audit từ chối ghi đè technical summary đã tồn tại; muốn tái lập cần workspace/output mới đúng pins, không xóa evidence để chạy lại. Assembly chỉ tái tạo presentation và screening của study chưa seal.

Tests trực tiếp helper: 5 PASS. Kết quả lint/type/checker và kiểm links/pins cuối cùng ở [validation](validation.json). Không thay trainer/loader production; thêm module audit làm code tree khác snapshot RC1 nên không dùng identity mới để giả tái lập run cũ. Media/raw/boards giữ ngoài Git; bản copy cùng ổ không là off-device backup.

## Kết quả review của onwer

**Nhận biết calculator**: thường có màu đen trắng, xanh biển, hồng, và có thể thêm một vài màu nữa, mặt trước của nó khá dễ để phân biệt với phone bởi nó có các nút bấm nồi lên. Hiện nay đa số mọi người sử dụng calculator lại Casio FX 580, có 3 tông màu chính là trắng mặt sau và đen viền trắng mặt trước (phổ biến nhất), hồng, xanh da trời nhạt. Ngoài ra cũng có sử dụng 2 loại khác nữa trong đó một cái là màu đen 2 mặt còn cái kia là mặt sau màu xanh trời đậm mặt trước là trắng đục. 

| ID | Kết quả | Chú thích |
|---|---|---|
| CB-0001 -> CB-0017 | Nhiều vấn đề | Trong loạt crops này có xuất hiện thêm người đằng sau targeted anchor như vậy có ảnh hưởng gì không? CB-0006 looking_around rất rõ, vật màu trằng anchor cầm là calculator còn vật màu đen là phone |
| CB-0018 -> CB-0025 | Nhiều vấn đề | Trong loạt crops này có 2 targeted anchors, có vài crops có một anchor looking_around khá rõ | 
| CB-0027, CB-0029, CB-0031 -> CB-0062 | N/N | Đang cầm calculator |
| CB-0030 | Lỗi crop | Mất đầu anchor, nếu đủ thì sẽ là N/P |
| CB-0063 -> CB-0087 | P/N | Màu đen là phone còn màu trắng là calculator. Với tư thế cúi gằm mặt xuống bàn như vậy thì coi looking_around là N có hợp lý không? Vì theo tôi thì không nên chỉ dựa vào hướng mắt mà 80% dựa vào tư thế nữa. Một vài crop có dính thân người của anchor khác thì có ảnh hưởng gì không? |
| CB-0088 -> CB-0112 | Nhiều vấn đề | Gần như toàn bộ crops đều bị dính người khác vào, đặc biệt là từ 0106 -> 0112 thì chẳng biết ai là targeted anchor. CB-0100 looking_around rõ, CB-0101 tay che đầu nhưng tư thế như vậy thì chắc chắn là looking_around |
| CB-0113 -> CB-0149 | P/N | Vật màu trắng cầm trên tay là calculator, vật đặt trên bàn là phone. Càng về những crops sau thì người ngồi bên targeted anchor đang bị xuất hiện nhiều hơn trong crop |
| CB-0150 -> CB-0174 | P/N | Vật màu đen trắng xuất hiện trong một vài crops là calculator còn vật còn lại đặt trên bàn là phone. Từ 0167 -> 0174 xuất hiện 4 người trong crop |
| CB-0175 -> CB-0199 | P/N | Vật màu xanh da trời trắng là calculator còn cái kia là phone |
| CB-0200 -> CB-0223 | P/N | Vật màu đen trắng là calculator. Từ 0217 -> 0223 xuất hiện phần đầu của người ngồi phía trước targeted anchor trong crop |
| CB-0224 -> CB-0252 | Nhiều vấn đề | Không biết ai là targeted anchor vì crop có tới 4-5 người. Nếu targeted anrchor là nam áo trắng ở giữa thì vật trong tay rất khó phân biệt nhưng tôi chắc chắn đó là phone, còn bạn xử lý sao thì tùy |
| CB-0253-> CB-0281 | P/N | Phone có màn hình sáng còn calculator màu đen, crop bị dính ít thân người của bạn ngồi cạnh |
| CB-0282 -> CB-0368 | P/N | Phone và calculator trong loạt crops này phân biệt khá rõ |
| CB-0369 -> CB-0397 | P/N | Phone và calculator trong loạt crops này phân biệt khá rõ, các crops bị dính đầu bạn nam phía trước |
| CB-0398 -> CB-0484 | Phone và calculator trong loạt crops này phân biệt khá rõ, crop có bị dình bạn ngồi sau targeted anchor, CB-0451 dính bạn ngồi phía trước |
| CB-0485 -> CB-0513 | P/N | Calculator màu xanh da trời nhạt |
| CB-0514 -> CB-0542 | Nhiều vấn đề | Loạt crops này không làm rõ được targeted anchor, dính quá nhiều người |
| CB-0543 -> CB-0571 | Crop lệch | Targeted anchor bị cắt lệnh khỏi khung hình, nếu như cắt đúng thì sẽ là P/N |
| CB-0572 -> CB-0597 | Crop chưa bao hết anchor | Tôi chưa biết frames gốc như nào nhưng nếu có thể cắt được tổng quát hơn thì tốt. CB-0582 có looking_around, còn lại thì P/N |
| CB-0598 -> CB-0603 | Crop chưa bao hết anchor | Tôi chưa biết frames gốc như nào nhưng nếu có thể cắt được tổng quát hơn thì tốt. Từ đó phải kiểm tra lại phone và looking_around |
| CB-0604, CB-0607 -> CB-0610 | Crop chưa bao hết anchor | Cần xem lại frame gốc rồi crop lại |
| CB-0605, CB-0606 | N/N | CB-0605 đang cầm calculator |
| CB-0611 -> CB-0617 | Nhiều vấn đề | Crop dính người khác và cắt mất người, trong một vài crops có phone có calculator có looking_around |
| CB-0618 -> CB-0630 | P/N | Calculator màu trằng đen, phone màu đen. CB-0626, CB-0627 looking_around, crops có dình ít cơ thể người khác |
| CB-0634 -> CB-0643 | Crop linh tinh | Kiểm tra kỹ lại |
| CB-0644 -> CB-0646 | P/N | Calculator màu xanh là cây, crop có dình ít vai của người bên cạnh |
| CB-0648 | N/N | Nếu targeted là bạn nữ áo trắng thì vật bị tay đè nên là calculator, cần chỉnh lại crop |
| CB-0649 -> CB-0652 | P/N | Crop có nhiều người nhưng vẫn phân biệt được targeted anchor |
| CB-0653 -> CB-0656 | P/N | Calculator màu xanh da trời nhạt, phone đặt trên sách trên bàn, crop có nhiều người nhưng vẫn phân biệt được targeted anchor |
| CB-0659, 0662, 0666, 0667, 0668, 0669, 0672 | P/N | Crop dính người ngồi sau nhưng vẫn phân biệt được targeted anchor. Phone màu đen đặt trên sách trên bàn |
| CB-0657, 0658, 0663, 0670, 0671 | P/P | Crop dính người ngồi sau nhưng vẫn phân biệt được targeted anchor. Phone màu đen đặt trên sách trên bàn |
| CB-0660, 0664, 0665 | P/U | Crop dính người ngồi sau nhưng vẫn phân biệt được targeted anchor. Phone màu đen đặt trên sách trên bàn |
| CB-0673 -> CB-0683, CB-0694 -> CB-0702 | P/P | Crop dính nhiều người nhưng vẫn phân biệt được targeted anchor. Phone màu đen đặt trên sách trên bàn |
| CB-0684 -> CB-0693 | P/N | Crop dính nhiều người nhưng vẫn phân biệt được targeted anchor. Phone màu đen đặt trên sách trên bàn |
| CB-0703, 0706, 0708, CB-0710 -> CB-0714 | N/P | Có một vài crops anchor để tay dưới bàn thì có thể phone U. Một vài crops bị dình người ngồi bên cạnh |
| CB-0704, 0705, 0707, 0709 | N/N | Có một vài crop tay không rõ có thể để phone U |
| CB-0715 -> CB-0748 | Crop linh tinh | Crop lại toàn bộ, vì không biết ai là targeted anchor |
| CB-0749 | U/N | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone. Khuất 2 bàn tay, bị dính một chút người ngồi cạnh |
| CB-0750, 0753 | N/P | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone. Crop bị dình người ngồi cạnh, 0750 tay cầm vật gì đó nhưng chắc chắn không phải phone |
| CB-0751, 0752, 0754 | N/N | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone. Vật ở tay hơi khó phân biệt nhưng chắc chắn không phải phone |
| CB-0755, 0758, 0759 | N/N | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone. Crop bị dính người bên cạnh |
| CB-0756, 0757 | N/P | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone. Tư thế và hướng đầu không nhìn vào own-paper, crop bị dính bạn bên cạnh |
| CB-0760 | N/N | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone. Tay đang cầm tài liệu, crop bị dính bạn bên cạnh |
| CB-0761 | U/N | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone. Chất lượng ảnh kém nên không nhìn được tay, crop bị dính bạn bên cạnh |
| CB-0762 | N/N | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone. Chất lượng ảnh kém nên không nhìn được đang cầm gì nhưng chắc chắn đó không phải phone |
| CB-0763 -> CB-0765 | N/N | Trên bàn có nhiều đồ vật gây nhiễu nhưng đó không phải phone |