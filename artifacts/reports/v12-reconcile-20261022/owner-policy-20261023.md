# Quy tắc nhãn trong đợt đối soát V12

Decision ID: `V12-RECONCILE-PHONE-20261023`. Owner xác nhận trực tiếp trong hội thoại ngày 23/10/2026; phạm vi là candidate hiện tại và 156 ảnh bổ sung, trước release kế tiếp.

> trong toàn bộ crop hiện tại bị khuất tay/bàn sẽ ko khiến phone U mà phone U chỉ là do có vật gây nhiễu thôi. ví dụ crop có bàn clear nhưng tay đặt dưới bàn thì phone N, tương tự các trường hợp khác.

Áp dụng: không thấy phone hoặc vật nghi phone trong vùng ảnh quan sát được thì phone N, kể cả tay dưới bàn, ngoài crop hoặc bị che. N diễn tả absence trong ảnh; không chứng minh phía sau vật che không có phone. Nếu có vật nhìn thấy nhưng chưa phân biệt được phone với vật khác thì U, theo câu trả lời trước của owner: “U nếu chưa phân biệt được phone với vật khác”. Tư thế cầm có evidence nhận diện phone hoặc đặc điểm phone rõ có thể P; không ép vật mơ hồ thành P chỉ vì hình chữ nhật.

Quyết định này **thay phần điều kiện nhìn thấy tay/bàn** của `E004-PHONE-OCCLUSION-20261015` trong revision đang đối soát. Không sửa dữ liệu, nhãn, metrics hoặc pins của release V12 đã accepted. Không tự gán thiết bị người khác cho anchor. Nhãn từng crop vẫn phải đối chiếu nội dung; không chuyển tất cả U thành N.

Looking theo yêu cầu owner của đợt audit: quay hẳn sang bên hoặc ra sau là P; hơi chéo nhưng nhìn bài người khác cũng P; đầu thẳng hoặc hơi chéo còn lại N khi đủ quan sát. Thiếu evidence hướng đầu/đích nhìn giữ U. Thứ tự nhãn luôn là Phone / Looking.

Owner trả lời bổ sung B03 trong hội thoại: **E004-EX-C026 N/P**. Bản owner-review-batch-02.md giữ nguyên, câu trả lời chat được ghi trong batch02-receipt.json.

Quy tắc được duyệt không thay acceptance toàn batch, geometry, grouping, split hoặc release. Các snapshot mới ghi rõ nguồn quyết định và giữ snapshot trước để đối chiếu.

Với góc camera sau lưng, chỉ gán Looking P khi thấy người quay mặt ngang hẳn sang hai bên hoặc ngoảnh hẳn về sau, theo quyết định owner batch 04. Góc quay camera từ sau tự nó không khiến Looking P hoặc U.
