# Audit crop bổ sung ngày 17/10/2026

## Kết luận sau review owner — đã chốt

**Giữ 172 crop bổ sung**: 146 crop duyệt mặc định; 34 ID có nhận xét đã kiểm riêng. Trong 180 crop gốc, loại 9, thay 3 bằng 4 khung cắt, giữ 168 khung gốc. Cùng bộ 98 đã chốt trước đó là **270 crop đã nghiệm thu crop/nhãn/membership**, chưa nhập release V10 hoặc gán split.

**[Mở gallery đã chốt](../../../data/interim/frame-crop-additional-20261017/accepted.html)** · [ZIP 172 crop và input](../../../data/interim/frame-crop-additional-20261017/accepted-172.zip) · [Receipt đầy đủ](owner-accepted.json) · [Kiểm tra](owner-accepted-validation.json)

- Không cần vòng owner review mới: áp dụng quyết định mặc định và quyền chốt ngoại lệ trong tin nhắn owner. Nhãn/crop khác biệt được ghi rõ ở bảng dưới.
- Loại cả 7 ID có dấu `*`: không đủ bằng chứng hướng nhìn ổn định ở crop hiện tại; không đổi thành N chỉ để giữ mẫu. G03 có sách dựng theo hướng đầu nhưng mắt bị che nên cũng không khẳng định đang đọc sách hay nhìn ngoài bài.
- Loại G06-B02 và G06-B03: chữ chồng/sát vùng đầu. Chưa có thí nghiệm chứng minh ảnh hưởng thực tế đến model; vì vậy không khẳng định chữ vô hại. Cắt hết chữ sẽ mất đầu, nên chọn loại theo điều kiện owner, không xóa chữ bằng sửa ảnh.
- G11-B04 chốt N/N: frame gốc cho thấy cấu trúc phím calculator. G10-B04 chốt N/N sau đối chiếu crop viết bài cùng video và vùng tay/bàn của chính anchor.
- G04-B07 tách thành G04-B07-F00037-R02 (nam) và G04-B15-F00037 (nữ), đều N/N. Crop nữ còn một phần người nam ở mép trái vì bỏ hết sẽ mất tay anchor; người nữ và vùng viết nằm giữa, không còn hai anchor ngang vai trò.
- G05-B02 dùng R02, tập trung nữ bên phải, N/P; không thêm crop nữ bên trái vì đã có B01. G23-B09 dùng R02 bỏ mặt tiền cảnh, N/N.
- Chỉ thêm 4 geometry mới trong thư mục candidates hiện có; gallery đã chốt dùng lại bytes crop/input cũ cho phần giữ. Ledger, gallery và ZIP Draft giữ nguyên hash; nội dung review của owner được lưu nguyên trong [snapshot](owner-review-input.md). Phần bên dưới là báo cáo và review trước khi chốt, không phải trạng thái hiện hành.

### Đối chiếu 34 ID được owner nêu

| ID gốc | Kết quả cuối | Căn cứ / xử lý |
|---|---|---|
| G01-B01-F00009 | Loại | Dấu *: mặt nhỏ và mờ, tay che vùng mặt; không đủ xác nhận hướng nhìn ngoài bài ở chính crop. Ghi nhận đề xuất U/P của owner nhưng áp dụng điều kiện loại khi looking không rõ. |
| G01-B03-F00009 | Loại | Dấu *: đầu hơi hướng trước, mặt và mắt thiếu chi tiết; không đủ phân biệt nhìn bài với nhìn ngoài bài. Không giữ N theo giả định cũ. |
| G01-B05-F00009 | Loại | Dấu *: đầu hơi ngẩng nhưng mắt mờ và tay sát mặt; không đủ kết luận P/N ổn định từ crop. |
| G02-B02-F00009 | U/N | Một bên tay bị che hoàn toàn bởi người ngồi trước, còn hướng đầu như vậy vẫn là đang nhìn vào bài của mình |
| G03-B04-F00008 | Loại | Dấu *: đầu quay cạnh nhưng tay che mắt/mặt; sách dựng trùng hướng quay. Không xác định đang nhìn sách hay ngoài sách, nên loại thay vì suy P từ góc đầu hoặc N từ việc cầm sách. |
| G04-B05-F00033 | U/N | Một tay bị che |
| G04-B06-F00035 | U/N | Vật đang cầm trên tay chưa xác định được chính xác là gì |
| G04-B07-F00037 | Thay bằng G04-B07-F00037-R02, G04-B15-F00037 | Crop đang bị dính hai người, có thể tách thành 2 crop tương ứng với 2 bạn ngồi cạnh nhau |
| G04-B11-F00001 | U/N | Tay và bàn bị che nên không thể quan sát được hết |
| G04-B14-F00001 | U/N | Một bên tay vẫn bị che |
| G05-B01-F00001 | U/N | Một bên tay vẫn bị che |
| G05-B02-F00015 | Thay bằng G05-B02-F00015-R02 | Crop đang bị dính hai người, trong đó bạn nữ trái bị che một phần còn bạn nữ phải looking_around P |
| G05-B03-F00039 | U/N | Các vật trên bàn rất mờ, chỉ thấy vật đen thôi không thể chắc chắn phone P được |
| G06-B02-F00003 | Loại | Owner đề nghị loại nếu chữ ảnh hưởng. Chữ phủ sát/chồng vùng tóc và đầu; không có bằng chứng chứng minh vô hại, cắt bỏ chữ sẽ mất đầu. Loại, không inpaint hoặc tạo nhãn U/N để cứu crop. |
| G06-B03-F00003 | Loại | Chữ phủ sát/chồng vùng tóc và đầu, kèm che khuất. Không thể bảo đảm vô hại hoặc bỏ chữ bằng crop mà giữ đủ đầu; loại theo điều kiện owner. |
| G06-B08-F00005 | Loại | Dấu *: mũ/khẩu trang và ảnh mờ làm thiếu dấu hiệu mắt, hướng đầu gần phía trước; chưa đủ phân biệt khỏi vùng bài. |
| G06-B09-F00005 | U/P | Bị che |
| G07-B04-F00012 | N/P | Đang quay sang bên cạnh |
| G08-B04-F00001 | Loại | Dấu *: mặt quá nhỏ, hướng trước và cúi nhẹ khó phân biệt; không giữ P khi chưa có bằng chứng rõ. |
| G08-B06-F00001 | Loại | Dấu *: hai người chồng nhau; cô lập người nam trước sẽ cắt vùng tay/bài hoặc vẫn giữ người sau. Hướng nhìn cũng không rõ, nên loại theo quyền owner cho phép. |
| G10-B03-F00001 | N/P | Đầu và hướng nhìn không vào own-paper |
| G10-B04-F00001 | N/N | N/N theo owner, đối chiếu G10-A01-F00008 và các crop viết bài cùng video: tay viết và tay giữ trang đều thấy; không thấy mobile hoặc thiết bị mơ hồ. Không dùng việc các crop khác là N làm bằng chứng duy nhất. |
| G11-B01-F00008 | N/N | N/N theo owner: tay còn lại đặt sát mặt, không mất hoàn toàn; khung hiện tại đã bỏ device người cạnh bên. |
| G11-B04-F00008 | N/N | N/N: đối chiếu crop và frame gốc thấy lưới phím của calculator, không chỉ một mặt kính đen của phone. Phần bàn/tay quan sát còn lại không có phone rõ; giấy che một phần áp dụng ngoại lệ absence đã duyệt. |
| G11-B07-F00008 | U/P | Một phần tay vẫn bị che bởi người ngồi trên, hướng nhìn chắc chắn là looking_around P rồi |
| G13-B09-F00025 | U/P | Một tay đặt dưới bàn |
| G23-B04-F00007 | N/P | Tay và bàn có thể quan sát rõ ràng, một tay đang cầm bút, không có vật gì gây nhiễu cả |
| G23-B09-F00011 | Thay bằng G23-B09-F00011-R02 | Đang nhìn vào own-paper, dịch crop một tí để không bị dính mặt của bạn tiền cảnh |
| G23-B11-F00012 | U/N | Một tay dưới bàn |
| G26-B03-F00002 | U/N | Đang nhìn own-paper |
| G26-B08-F00003 | U/N | Đầu hơi chếch sang bên tí thôi nhưng vẫn là nhìn own-paper |
| G26-B09-F00004 | U/N | Một bên tay hoàn toàn không thấy |
| G26-B11-F00027 | U/N | Tư thế cầm vật rất quen thuộc rồi |
| G27-B03-F00016 | U/P | Bị che |

Kiểm kỹ thuật: 172 crop/source/input parity PASS; toàn bộ 180 crop cũ giữ hash; parent ledger/ZIP giữ hash; ZIP CRC/membership và 344 đường dẫn gallery PASS. Không thay contract, labels của bộ 98, dataset V10, split hoặc train/test.

---

**180 crop Draft từ 19 video**, sau khi đối chiếu 187 ảnh đánh dấu trong `additional.zip` với các chuỗi frame nguồn. Có 172 mã anchor cục bộ; đây không phải số người độc lập giữa các video. Batch bổ sung chờ owner nghiệm thu crop/nhãn, chưa enrollment.

[Mở gallery bổ sung](../../../data/interim/frame-crop-additional-20261017/index.html) · [Gói ZIP review](../../../data/interim/frame-crop-additional-20261017/additional-review.zip)

## Bộ 98 crop đã chốt

[Kết luận đã nghiệm thu](../frame-crop-audit-20261016/OWNER-ACCEPTED-20261017.md): G23-A03-F00009 U/N; G27-A02-F00022 và G27-A03-F00031 P/P theo quyết định owner. G06 dùng R02; loại G14-A10-F00018 và G17-A01-F00012. Approval đã có hiệu lực, không cần duyệt lại. Hồ sơ đối chiếu trước đó giữ làm lịch sử.

## Cách chọn và giới hạn

- Xem ảnh đánh dấu và các chuỗi frame gốc liên quan. Dấu đánh dấu là đầu mối tìm anchor, không tự động trở thành crop. Cắt từ frame nguyên bản không có nét đánh dấu.
- Giữ vùng đầu, tay, vật và trang bài cần để quan sát hành vi; ưu tiên anchor rõ, hạn chế người cạnh bên. Loại các thử nghiệm mất tay/đầu tại mép nguồn, nhiễu anchor hoặc trùng trạng thái đã giữ. Không yêu cầu toàn thân nếu vùng hành vi ngồi tại bàn đã quan sát được.
- Gallery xếp theo video → anchor → frame. Chọn thêm frame của cùng anchor khi trạng thái/hành động có thay đổi đáng xem. Chưa có bảng lớp/buổi học nên không ghép danh tính giữa video.
- Nhãn theo thứ tự phone_use / looking_around: P = positive, N = negative, U = chưa đủ bằng chứng. Nhãn mới là đề xuất; canonical targets vẫn null và mask 0. U không được coi là negative.
- Độ phân giải nguồn nhỏ và che khuất vẫn là giới hạn cần xem ở native crop lẫn input 224 px. Kiểm hash loại trùng hoàn toàn không chứng minh độc lập nguồn hoặc loại hết tương đồng thị giác.
- G14-B15-F00059 là đề xuất frame khác cho vị trí từng bị loại ở G14-A10; không khôi phục hay sửa quyết định loại crop cũ.

## Evidence và kiểm tra

- [Ledger 180 đề xuất](review-index.json): geometry, lý do, nhãn, nguồn và SHA từng crop. Các ID accepted liên quan được liệt kê theo cùng video, không khẳng định cùng người.
- [Bao phủ 187 ảnh đánh dấu](marked-frame-coverage.json): mapping đã đối chiếu thị giác, crop mới/cũ từ frame đó và ghi chú chuỗi. Đây là coverage ở mức frame, không phải annotation đầy đủ mọi người trong ảnh.
- [Các crop thử bị loại](rejected-trials.json): chỉ các phương án đã thử cắt, không phải tổng số người được đánh dấu nhưng không chọn.
- [Kiểm xuất gói](validation.json): 180 crop, parity vùng cắt/input PASS; 0 trùng hash nội bộ, 0 trùng hash với bộ 98. Phân bố đề xuất: N/N 99; U/N 37; N/P 22; U/P 11; P/N 9; N/U 2.
- [Kiểm bàn giao](handoff-validation.json): hash ledger/receipt/gói, CRC ZIP và đường dẫn gallery.

Owner chỉ cần review batch bổ sung theo yêu cầu “owner nghiệm thu batch và ngoại lệ” trong [AGENTS.md](../../../AGENTS.md). Chưa thay đổi release V10, split, train hoặc test.

Kiểm hồi quy công cụ crop: unittest source_review **6/6 PASS**, derived_crop **2/2 PASS**. Worksheet khớp ledger sau định dạng, Python syntax PASS; Ruff PASS với E501 bỏ qua riêng lệnh kiểm các worksheet do chuỗi lý do/HTML dài. Không đổi cấu hình lint project. Đã dọn preview/QA scratch và bytecode sau khi giữ đầy đủ evidence xuất gói.

## Kết quả review của owner

| ID | Kết quả | Chú thích |
|---|---|---|
| G01-B01-F00009 | U/P | * Một tay đưa lên mặt chứ không phải tư thế chống tay, còn một tay kia thì để dưới bàn |
| G01-B03-F00009 | Xem xét | * Tư thế đầu này là đang nhìn thẳng về phía trước, nhưng cần xem lại các crop tương tự như này xem đang gán looking_around là gì |
| G01-B05-F00009 | Xem xét | * Hướng đầu của bạn này cũng gần giống với crop G01-B03-F00009, đầu hơi hướng thẳng về phía trước |
| G02-B02-F00009 | U/N | Một bên tay bị che hoàn toàn bởi người ngồi trước, còn hướng đầu như vậy vẫn là đang nhìn vào bài của mình |
| G03-B04-F00008 | Xem xét | * Tay che hoàn toàn mặt nhưng với tư thế như vậy thì đang quay sang bên cạnh rồi, còn việc nhìn vào sách được giơ ra đúng hướng quay mặt mà coi looking_around N thì tôi chưa biết |
| G04-B05-F00033 | U/N | Một tay bị che |
| G04-B06-F00035 | U/N | Vật đang cầm trên tay chưa xác định được chính xác là gì |
| G04-B07-F00037 | Sửa lại crop | Crop đang bị dính hai người, có thể tách thành 2 crop tương ứng với 2 bạn ngồi cạnh nhau |
| G04-B11-F00001 | U/N | Tay và bàn bị che nên không thể quan sát được hết |
| G04-B14-F00001, G05-B01-F00001 | U/N | Một bên tay vẫn bị che |
| G05-B02-F00015 | Sửa lại crop | Crop đang bị dính hai người, trong đó bạn nữ trái bị che một phần còn bạn nữ phải looking_around P |
| G05-B03-F00039 | U/N | Các vật trên bàn rất mờ, chỉ thấy vật đen thôi không thể chắc chắn phone P được |
| G06-B02-F00003, G06-B03-F00003 | Loại | Hai crop này bị dính chữ vậy có ảnh hưởng tới quá trình học của model không? Nếu không thì cứ giữ nhưng giá trị phải lần lượt là U/N, U/N vì đều bị che một ít  |
| G06-B08-F00005 | Xem xét | * Chất lượng ảnh kém nên không xác định được chính xác hướng nhìn, nhưng tư thế này là đang nhìn về phía trước |
| G06-B09-F00005 | U/P | Bị che |
| G07-B04-F00012 | N/P | Đang quay sang bên cạnh |
| G08-B04-F00001 | Xem xét | * Hướng đầu và mắt nhìn thẳng về phía trước |
| G08-B06-F00001 | Sửa lại crop | * Hiện đang bị dính 2 người, nếu không có cách nào cắt đề không bị dính thì loại luôn đi cũng được. Nam áo xanh trắng đầu và hướng nhìn đang hơi nhìn thẳng về phía trước |
| G10-B03-F00001 | N/P | Đầu và hướng nhìn không vào own-paper |
| G10-B04-F00001 | N/N | Rất nhiều crop dạng như này thì đều phone N thì phải, bạn có thể kiểm tra lại |
| G11-B01-F00008 | N/N | Tay còn lại đặt lên mặt, không bị che quá nhiều |
| G11-B04-F00008 | Xem xét | Vật không chắc chắn là phone, vì nếu quan sát kỹ thì sẽ thấy phần trên màu đen giống với phone nhưng dưới có nút bấm của calculator |
| G11-B07-F00008 | U/P | Một phần tay vẫn bị che bởi người ngồi trên, hướng nhìn chắc chắn là looking_around P rồi |
| G13-B09-F00025 | U/P | Một tay đặt dưới bàn |
| G23-B04-F00007 | N/P | Tay và bàn có thể quan sát rõ ràng, một tay đang cầm bút, không có vật gì gây nhiễu cả |
| G23-B09-F00011 | N/N | Đang nhìn vào own-paper, dịch crop một tí để không bị dính mặt của bạn tiền cảnh |
| G23-B11-F00012 | U/N | Một tay dưới bàn |
| G26-B03-F00002 | U/N | Đang nhìn own-paper |
| G26-B08-F00003 | U/N | Đầu hơi chếch sang bên tí thôi nhưng vẫn là nhìn own-paper |
| G26-B09-F00004 | U/N | Một bên tay hoàn toàn không thấy |
| G26-B11-F00027 | U/N | Tư thế cầm vật rất quen thuộc rồi |
| G27-B03-F00016 | U/P | Bị che |