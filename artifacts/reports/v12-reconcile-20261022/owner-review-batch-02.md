# Batch 02 — Ngoại lệ sau sàng lọc toàn bộ candidate

Đã áp các quyết định tường minh batch 01 vào `reconciled-review-r2.json`. Đã loại 221 crop review_only không có nội dung ghi đè trong JSON; không hỏi lại các crop này. Hiện còn 1.169 crop cũ giữ/recrop và 156 ảnh mới đang kiểm. Đây chưa là bản release.

Thứ tự nhãn **Phone / Looking**. Các đề xuất dưới đây chưa ghi đè r2. Anh có thể duyệt theo từng nhóm, chỉ ghi khác biệt; cột trả lời để trống không được coi là đồng ý. Những crop không xuất hiện ở đây tiếp tục theo JSON/V12 và các quyết định đã duyệt.

## A. Khép lại batch 01

[Phân tích và nguồn tham khảo thiết bị](device-observability.md): giữ **NB-0003, NB-0007 N/N**; giữ **EXP-SCB-021 N/P**. Không cần anh xác nhận lại ba kết luận phù hợp quyết định đã đưa ra. Không kết luận hiệu quả train khi chưa thực nghiệm.

![Q01 và các ca thiết bị](../../../data/interim/v12-reconcile-20261022/boards/focused-06.jpg)

| Câu | Crop | Đề xuất và lý do | Quyết định của owner |
|---|---|---|---|
| A01 | E004-CF-C011 | Đổi **N/P → N/U**: giữ nhãn phone biết chắc, mask Looking vì tóc che hướng đầu. Thông tin anh xác nhận quay sau vẫn lưu trong evidence. Nếu anh không muốn giữ mẫu chỉ có một target biết thì chọn **loại**. Tôi rút đề xuất N/N của batch trước. | Approve |

## B. Hướng đầu và hướng nhìn

![B01–B04](../../../data/interim/v12-reconcile-20261022/boards/flags-02.jpg)
![B05 ở hàng dưới bên trái](../../../data/interim/v12-reconcile-20261022/boards/flags-01.jpg)
![B06 ở hàng dưới bên phải](../../../data/interim/v12-reconcile-20261022/boards/flags-06.jpg)
![B07 ở hàng trên bên trái](../../../data/interim/v12-reconcile-20261022/boards/flags-07.jpg)
![B08 ở hàng trên bên trái](../../../data/interim/v12-reconcile-20261022/boards/flags-08.jpg)

| Câu | Crop | Hiện tại → đề xuất | Lý do cần đối chiếu | Quyết định của owner |
|---|---|---|---|---|
| B01 | E004-CN-018 | N/P → **N/N** | Đầu nghiêng sang vai, không thấy quay ngang/sau rõ; phân biệt nghiêng đầu với quay đầu. | Approve |
| B02 | V7-OE-S116-A01 | U/P → **U/N** | Mặt và thân hướng phía trước; chưa thấy nhìn bài khác. | Approve |
| B03 | E004-EX-C026 | N/N → **N/P** | Người nghiêng và hướng mặt rõ sang bên, nhìn ra khỏi bài mình. | |
| B04 | V6-CA-031, V6R2-EX-008-R04 | **Giữ N/P** | Sau kiểm ảnh riêng, mắt/đầu hướng sang vùng bàn cạnh; mục thông tin, không yêu cầu quyết định lại nếu anh không thấy khác. | Approve |
| B05 | G09-B05-F00043 | N/P → **N/N** | Đầu hơi chéo, không thấy đích nhìn là bài người khác; chưa đạt mức quay ngang rõ theo rubric mới. | Approve |
| B06 | G03-B14-F00033 | N/P → **N/N** | Nhìn gần thẳng, chỉ lệch nhẹ. | Approve |
| B07 | G07-B04-F00012 | N/P → **N/U** | Nhìn xuống lệch bên; crop không đủ để xác định đang nhìn bài mình hay bài bên cạnh. | Approve |
| B08 | G23-B06-F00008 | N/P → **N/U** | Góc mặt gần máy ảnh nhưng tương quan với thân/bàn bị cắt và mờ; cần anh chỉ rõ nếu giữ P. | Approve |

## C. Phone, calculator và thiết bị chưa rõ

![C01–C03](../../../data/interim/v12-reconcile-20261022/boards/flags-05.jpg)
![C04–C05](../../../data/interim/v12-reconcile-20261022/boards/focused-02.jpg)
![C06–C07](../../../data/interim/v12-reconcile-20261022/boards/flags-06.jpg)
![C08: G13-B03 ở giữa hàng dưới](../../../data/interim/v12-reconcile-20261022/boards/flags-03.jpg)
![C08: G14-B15 ở trên bên phải](../../../data/interim/v12-reconcile-20261022/boards/flags-06.jpg)
![C08: hai crop còn lại ở hàng dưới](../../../data/interim/v12-reconcile-20261022/boards/flags-07.jpg)

| Câu | Crop | Hiện tại → đề xuất | Lý do | Quyết định của owner |
|---|---|---|---|---|
| C01 | V7-D-042 | N/N → **P/N** | Vật cầm có màn hình và viền phone; vẫn xử lý yêu cầu recrop bớt laptop. | Trong crop thì target anchor đang cầm bút, tay đặt trên quyển gì đó bé bé giống với notebook chứ không có vật gì có màn hình và viền phone cả. Bạn hãy kiểm tra thật kỹ xem crop này có gây nhầm lẫn hay bất cứ ảnh hưởng gì xấu khi đưa vào sử dụng không, nếu có thì loại đi |
| C02 | V7-D-031 | P/N → **U/N** | Vật đen không đủ dấu hiệu để phân biệt phone và thiết bị khác; tư thế cầm chưa đủ. | Loại crop đi, bỏ hoàn toàn, không đưa nó vào bất cứ đâu cả vì background không phải trong phòng học |
| C03 | E004-EX-C082 | U/N → **P/N** | Mặt lưng và cụm camera phone rõ ở tay. | Approve |
| C04 | E004-SX-C005 | P/N → **U/N** | Thiết bị cầm ngang, chỉ thấy màn hình đen/cạnh; còn nghi vấn phone/tablet. | P/N |
| C05 | E004-CN-026 | P/N → **U/N** | Thiết bị rộng có thể tablet/e-reader; chưa đủ để giữ mobile P. Nếu anh xác nhận tablet và không phone khác thì N/N. | P/N |
| C06 | CB-0479 | U/N → **P/N** | Có vật dạng phone trên vở và thiết bị cầm tay; cần đối chiếu dấu hiệu mobile ở bản 224. | Approve |
| C07 | CB-0294 | U/N → **P/N** | Calculator riêng trên bàn, vật cầm mỏng dài có dáng phone; nếu chưa phân biệt chắc thì giữ U/N. | P/N |
| C08 | G13-B03-F00010, G14-B15-F00059, G23-A04-F00014, G13-B10-F00034 | N/N → **U/N** | Chủ yếu thấy cạnh/mặt lưng nhỏ; dấu hiệu vỏ calculator kém rõ hơn NB-0003/NB-0007/NA-005. Đề xuất U theo quy tắc anh đã chốt, không ép N chỉ vì thiếu camera. Có thể trả lời riêng từng ID. | G13-B03-F00010 U/N, G14-B15-F00059 N/N, G23-A04-F00014 U/N, G13-B10-F00034 U/N |

## D. Gần lặp và biến thể mới

![D01–D02: ảnh bên trái hàng trên/giữa ở bảng này](../../../data/interim/v12-reconcile-20261022/boards/flags-04.jpg)
![D01–D02: ảnh đối chiếu](../../../data/interim/v12-reconcile-20261022/boards/flags-08.jpg)
![D03](../../../data/interim/v12-reconcile-20261022/boards/flags-09.jpg)
![D04: cặp 76](../../../data/interim/v12-reconcile-20261022/boards/duplicates-13.jpg)
![D05: cặp 89](../../../data/interim/v12-reconcile-20261022/boards/duplicates-15.jpg)

Không có cặp nào dưới đây trùng bytes. Cần chốt mức giữ biến thể gần nhau; cùng cảnh nhưng khác người/hành vi không mặc nhiên là trùng cần xóa.

| Câu | Cặp | Đề xuất | Quyết định của owner |
|---|---|---|---|
| D01 | V6R2-MP-012 / V6R2-MP-081 | Gần cùng tư thế tay che miệng, phone trên bàn. **Giữ MP-081 P/N, loại MP-012**, nối cùng family. Khác vị trí ngón tay nhẹ, không gọi là cùng frame chắc chắn. | Approve |
| D02 | V6-CA-039 / V6R2-CA-014 | Cùng cảnh nhưng đầu, tay và hướng mắt khác nhau; **giữ cả hai N/N**, nối family. | Approve |
| D03 | E004-EX-C045 / E004-EX-C193 | Pose viết và nội dung rất gần nhau, khác biên/góc nhẹ. **Giữ C045 N/N, loại C193** để giảm lặp, nối family. | Approve |
| D04 | NEW-120 / NEW-122 | Cả hai quay sang cùng phía, mức quay chênh nhỏ. **Giữ NEW-120 N/P, bỏ NEW-122** để giảm lặp. | Giữ cả hai |
| D05 | NEW-149 / NEW-150 | Cùng phone P, đầu hướng trước/hơi chéo đều N; khác rất ít. **Giữ NEW-149 P/N, bỏ NEW-150**. | Approve |

## E. Ảnh mới cần kiểm riêng

![E01–E02: cặp 45 và 46](../../../data/interim/v12-reconcile-20261022/boards/duplicates-08.jpg)
![E03: cặp 29](../../../data/interim/v12-reconcile-20261022/boards/duplicates-05.jpg)

| Câu | Crop | Đề xuất | Quyết định của owner |
|---|---|---|---|
| E01 | NEW-021 | **N/U**, chưa rõ quay ngang đủ mức hay hơi chéo; phần tay bị sách che. Đề xuất loại nếu anh không thấy ích lợi so với các biến thể rõ hơn. | Loại |
| E02 | NEW-010 | **U/N**, tay/vùng bàn bị cắt nên không chắc phone N; chưa thấy thay đổi hữu ích rõ so với ảnh cũ đã bỏ. Đề xuất loại. | N/N |
| E03 | NEW-057 | **U/N**, vùng tay/bàn bị che, mặt gần thẳng. Đề xuất loại nếu mục tiêu là thêm mẫu rõ; ảnh gần như giữ nguyên vấn đề quan sát ở bản cũ. | Loại |

Ba ảnh cũ đối chiếu ở nhóm E đều đã bị loại và **không được đưa lại vào candidate**. ZIP là input mới được anh yêu cầu kiểm riêng, vì vậy NEW IDs vẫn cần quyết định theo nội dung.

## Phần tiếp theo sau batch

Nhãn dự thảo đủ 156 ảnh ở [additional-annotations-draft-r2.json](additional-annotations-draft-r2.json), cập nhật 23/10 sau khi xem toàn bộ bản 224 px. NEW-010 và NEW-021 đã đồng bộ nhãn dự thảo với nhóm E; chữ nhãn trên bảng ảnh 224 cũ vẫn phản ánh r1. Các dòng chưa có acceptance và vẫn chờ geometry; ảnh đổi pixels phải QA lại. Chưa phát hành, chưa chia split. Tiếp tục 54 yêu cầu geometry còn hiệu lực, đối chiếu lineage/nearest ngoài shortlist, kiểm ảnh sau crop và tổng hợp coverage sau khi chốt các ngoại lệ.
