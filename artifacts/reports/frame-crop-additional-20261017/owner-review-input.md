# Audit crop bổ sung ngày 17/10/2026

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