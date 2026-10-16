# Rubric thống nhất cho 247 crop

Thứ tự `[phone_use, looking_around]`; thực thi contract và [ngoại lệ owner](owner-direction.md). Không đổi lớp model, không tự đặt ngưỡng pixel/tỷ lệ che/confidence.

## Phone: identity → attribution → absence

1. **P:** mobile nhận dạng được trong chính crop, đúng tay/bàn/sách anchor. Mặt trước còn đủ cấu trúc mặt kính/màn hình lớn và viền máy để phân biệt keypad calculator; khối chữ nhật tối không đủ. Mặt sau cũng có thể P nếu rõ đặc trưng như cụm camera, không chỉ chấm nhòe. Phone rõ đủ P dù tay kia khuất hoặc có calculator/vật mơ hồ khác.
2. **U:** vật còn lộ nhưng chỉ là lưng/cạnh trơn, mảnh bị che, mờ mất đặc trưng hoặc attribution chưa rõ. Đen/trắng/hồng/xanh áp cùng quy tắc. Dáng cầm, bấm ngón cái, đốm sáng hay biết loại vật từ frame khác không thay identity trong crop.
3. **N:** không có phone rõ hoặc thiết bị chưa phân loại còn lộ; tay/vùng bàn đủ review. Calculator có phím rõ hỗ trợ N nhưng không tự đủ: kiểm phone khác và tay khuất. Không cần đặt tên chính xác mọi vật nếu cấu trúc đủ loại phone, ví dụ tập giấy/túi mềm có nếp.
4. **Ngoại lệ đã duyệt:** vật bị giấy/vật khác che hoàn toàn có thể N nếu điều kiện còn lại đủ. Không áp cho vật còn lộ mơ hồ hoặc bàn tay mất hoàn toàn. N chỉ là absence trong vùng quan sát theo quy tắc mới.

| Tình huống | P | N | U |
|---|---|---|---|
| Mặt sau | Đặc trưng mobile phân biệt được hoặc phone khác rõ | Loại mobile bằng cấu trúc vật, đủ absence còn lại | Lưng trơn, màu vỏ, chấm nhòe |
| Mờ | Đặc trưng nhận dạng vẫn còn | Đủ phân biệt vật không phải phone và review absence | Mất đặc trưng hoặc tay/vùng cần thiết không rõ |
| Che một phần | Phần còn lại đủ nhận phone | Đủ nhận calculator/vật khác và absence | Cạnh/mảnh không phân biệt được |
| Che hoàn toàn | Có phone khác rõ | Ngoại lệ owner, tay/phần còn lại đủ quan sát | Tay/vùng liên quan cũng mất hoặc attribution mơ hồ |

Không bắt phone bật sáng/thấy chữ hoặc app. Calculator cũng có màn hình; sáng một mình không phân biệt hai loại. Không dùng màu vỏ để gán nhãn.

## Crop, source và input

Xem đủ 247 input 224 × 224. Source cùng frame kiểm anchor/geometry/chi tiết; frame khác không truyền nhãn. Không gán known target chỉ nhờ chi tiết đã mất sau resize; input thiếu evidence giữ U trong đề xuất này. Không tăng nét AI/inpainting. Crop/bytes/recipe không đổi; khôi phục evidence cần derivative/input revision riêng.

Nhiều người không tự buộc U nếu phone đúng anchor rõ; cũng không được lấy phone người cạnh bên. Classifier hiện chỉ có RGB/hai output, không nhận anchor box/mask. G5-A05-F109 và G5-A06-F099 có cờ xem geometry trước package; nhãn đúng người không thay crop acceptance.

## Looking độc lập

P cần hướng đầu/nhìn rõ ngoài vùng bài riêng và context; N cần hướng vào vùng riêng đủ rõ. Không bắt buộc thấy con ngươi. Che mặt một phần vẫn có thể N/P khi hướng rõ; mất đầu/đích mơ hồ là U. “Không chắc P” không tự N. Nhìn thiết bị trong vùng riêng là N khi hướng/đích rõ. Cúi hẳn dưới bàn ngoài vùng giấy có thể P khi context đủ; chỉ cúi/nghiêng chưa đủ.

## Giới hạn

Manual Draft có evidence từng crop, không là thuật toán nhận vật hoặc accuracy. U không là lớp thứ ba model học; known targets chỉ vào loss/metrics sau acceptance. Không ép giảm U để tăng mẫu. 658 alternatives/withheld cũ không xét lại trong vòng 247 này; nếu lấy lại phải review rubric mới, không nhập batch/train theo nhãn lịch sử.
