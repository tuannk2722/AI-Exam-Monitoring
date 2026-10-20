# Rubric R2 — áp dụng quyết định Accepted V10/V11

Thứ tự nhãn là **phone_use / looking_around**; P/N/U độc lập cho từng target. U được mask, không phải negative. Nguồn chuẩn: [device consistency 15/10](../../E004-device-consistency-20261015/rubric.md), [ngoại lệ occlusion owner](../../E004-device-consistency-20261015/owner-direction.md), [review 17/10](../../frame-crop-audit-20261016/OWNER-REVIEW-20261017.md), [chốt cuối 17/10](../../frame-crop-audit-20261016/OWNER-ACCEPTED-20261017.md), và [batch bổ sung V11](../../frame-crop-additional-20261017/README.md). Quyết định cuối supersede đề xuất trước đó, đặc biệt G23-A03 và G27-A02/A03.

## Phone

- **P:** nhận được mobile trong crop và input 224; mặt trước có cấu trúc màn hình/mặt kính và viền đủ phân biệt, hoặc mặt sau có camera/ống kính tách biệt. Không bắt buộc màn hình sáng hay đọc được chữ. Một vùng sáng, hình chữ nhật, màu ốp hoặc kiểu cầm không đủ.
- **U:** lưng trơn/cạnh/chấm nhòe, vật chưa phân loại, tay/vùng thao tác thiếu evidence, hoặc attribution chưa chắc. Không biến nhận dạng thất bại thành N. Không truyền nhận diện từ frame khác hoặc chi tiết source đã mất ở input.
- **N:** phần tay và vùng thao tác đủ kiểm absence, không có mobile hay vật mơ hồ còn lộ. Calculator cần cấu trúc phím/màn hình phân biệt được; laptop/tablet/landline có dây không là mobile. Kiểm phần còn lại trước khi N.
- Ngoại lệ owner cho vật che hoàn toàn không đồng nghĩa mọi tay khuất là N. Tay chống cằm/khoanh tay có thể N khi hình học và phần còn lại đủ rõ; tay mất dưới bàn/ngoài ảnh mà chưa đủ absence giữ U.

Comparator U/N: G04-A03-F00074-R02, G14-A04-F00011, G14-A07-F00018, G18-A02-F00007, G23-A03-F00009. Comparator P/N: G05-A01-F00039, G18-A01-F00001, G20-A03-F00073. G27-A02/A03 là xác nhận attribution cụ thể của owner, không cho phép gán mọi phone gần anchor thành P.

## Looking

- **P:** đầu/hướng nhìn đủ rõ ra trước, lên, sang bên hoặc sang bài/người khác, rời vùng bài/thao tác riêng. Cầm bút không tự làm N.
- **N:** hướng về trang/vùng thao tác hoặc thiết bị riêng đủ rõ. Hơi nghiêng đầu nhưng vẫn hướng bài là N; không lấy phone P để suy looking P.
- **U:** mất đầu, che mặt/đích, mờ, nhắm mắt/úp đầu hoặc context không đủ phân biệt hướng. Không bắt buộc nhìn thấy con ngươi nếu hướng đầu/context đã rõ.
- Theo rubric 15/10, cúi hẳn dưới bàn ngoài vùng giấy có thể P nếu context đủ rõ. Không áp dụng cho mọi đầu cúi hoặc mọi phone cầm thấp. Các ca `l_below` được đánh dấu riêng để owner xem khi nghiệm thu.

Comparator N/P: G10-B03-F00001, G07-B04-F00012; U/P: G11-B07-F00008; U/N dù hơi nghiêng: G26-B08-F00003.

## Anchor và crop

Person box phải chỉ một người; classifier chỉ nhận RGB, không nhận lời giải thích hoặc box overlay. Phần người phụ nhỏ ở mép/nền được phép khi anchor trội và attribution rõ. Nhiều mặt/thân tương đương, tay/phone người cạnh hoặc đầu tiền cảnh cạnh tranh cần sửa geometry. Giữ đủ đầu, tay và vùng hành vi cần thiết; không dùng cutoff kích thước tùy ý, không thêm pixels, không inpaint.

Source dùng kiểm anchor và khả năng sửa khung. Nếu source đã mất/che phần cần thiết, nới crop không phục hồi evidence. Có một known target vẫn có thể giữ; U/U không có supervision. Overlay chỉ ở nền không tự làm crop không đạt; đè vùng hành vi phải xét riêng.

`keep` chỉ đề xuất giữ geometry và nhãn; `recrop` đề xuất tạm rút crop hiện tại rồi thử derivative mới, kiểm source → crop → input và duyệt lại cả hai target; `exclude` đề xuất rút supervision hiện tại. **250 ca recrop chưa có crop thay thế hoặc tọa độ mới được kiểm chứng.** Không tự kế thừa nhãn quan sát của khung cũ cho khung mới. Không đổi group/split/rights, không tự gán confirmed_normal chỉ vì N/N.

[16 comparator và SHA](comparators.json) · [Mã lý do](reason-codes.json) · [Kiểm tra chéo phone P](phone-confirmation.md).
