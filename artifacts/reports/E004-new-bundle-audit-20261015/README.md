# Audit bộ ZIP mới sau khi chốt batch cũ

Hoàn tất audit ngày **16/10/2026**, giữ ID hồ sơ đã khởi tạo ngày 15/10. [Batch cũ đã chốt 240 crop](../E004-crop-closure-20261015/README.md). Bộ mới có **80 crop và 132 frame gốc**; shortlist đề xuất **92 crop Draft**, chờ owner review.

- **65 crop giữ geometry gốc**, **13 recrop**, **14 crop bổ sung** được chọn. “Bổ sung” là crop mới, không đồng nghĩa 14 người mới: có cùng anchor ở frame/context khác tốt hơn.
- Tổng ledger 109 dòng giữ cả 80 originals và 29 derivative. Có 13 originals được recrop thay thế, NB-0014 được NA-008 thay vì nhân đôi cùng trạng thái, 2 U/U và 1 crop attribution yếu không vào shortlist.
- Nhãn shortlist: N/N 47, N/P 12, U/N 22, U/P 8, N/U 3. **Không có phone P đủ bằng chứng trong shortlist này**; không nâng lưng thiết bị, vật mờ hoặc tên file chứa “phone” thành P để bù quota.

Mở [gallery 92 crop / toàn bộ 109 dòng](../../../outputs/E004-new-bundle-audit-20261015/index.html), ghi quyết định tại [owner-review.md](owner-review.md). Có thể approve batch và ghi ngoại lệ. Gallery có input 224, liên kết native crop/source và toàn bộ bảng frame; chọn “Toàn bộ” để đối chiếu originals bị thay hoặc loại.

## Phạm vi và bằng chứng

Bảy ZIP crop là một bộ; ZIP source là `new-yt-videos-run-001-accepted-frames.zip`. Owner đã xác nhận đầy đủ quyền sử dụng. [Input pins](input-pins.json) ghi SHA-256, CRC và bản sao raw; không dùng mô tả/nhãn/approval trong ZIP làm authority. Metadata chỉ giúp nối frame và kiểm tọa độ, sau đó đối chiếu hình.

Nguồn A: 22 crop / 21 frame. Nguồn B: 58 crop / 111 frame, gồm bốn góc camera. Tất cả 80 input và native context đã được kiểm; root xem lại đủ 80 input và 58 native B. Agent A có [nhận xét từng frame và crop](source-A-review.json); agent B báo đã screening đủ 111 overview trước khi phiên agent bị ngắt. Root kiểm tiếp toàn bộ crop B/native và mở 8 frame gốc liên quan sửa/bổ sung. [Coverage](frame-coverage.json) phân biệt provenance này: không tuyên bố đã mở native riêng toàn bộ 132 frame hoặc có ghi chú chi tiết từng frame B. [Nhận xét 58 crop B](source-B-manual.txt) và [derivative B](source-B-review.json) giữ đề xuất ban đầu; **ledger hợp nhất là đầu ra hiện hành**, gồm quyết định root sau kiểm derivative.

Đã xem input 224 của cả 29 derivative sau xuất; 2 ứng viên mới NBX-002 và NBX-007 bị loại lần lượt vì U/U và đầu/tay bị người trước che gây attribution yếu. Một số crop vẫn có bộ phận người khác: chỉ giữ khi anchor đủ rõ, không đặt điều kiện phải loại sạch mọi pixel của người cạnh.

## Những lỗi đã xử lý

- NB-0041 thiếu đỉnh đầu, NB-0069 thiếu phần đầu/tay: mở khung và kiểm lại hướng nhìn.
- NB-0054 nhầm trọng tâm giữa người sát tường và người đeo kính phía trước; NB-0077 người áo xám lấn át anchor áo trắng phía sau: recrop đúng anchor, vẫn U ở phone nếu tay chồng lấn.
- NB-0034–0038, NB-0062, NB-0079: giảm các đầu cạnh tranh bằng khung chữ nhật. Không giả định context box là person box.
- NB-0012 và NB-0018: mở vùng tay từ source; NA-008 thay NB-0014 vì có calculator và tay rõ hơn. Crop mới thêm các vùng/người hữu ích, không cắt lặp hàng loạt theo mỗi frame.

Giữ [rubric hiện hành](../E004-device-consistency-20261015/rubric.md): phone P cần đặc trưng phân biệt và attribution; N cần đủ quan sát theo quy tắc đã duyệt, gồm ngoại lệ che hoàn toàn có scope; mảnh vật/thiết bị mơ hồ vẫn U. Calculator rõ không tự khiến toàn crop phone N nếu tay/vật khác còn chưa rõ. Looking xét hướng đầu/mặt so với bài riêng; không suy từ tư thế tay, tên hành động hoặc cảm xúc. Không dùng frame khác để “biết” vật ở input hiện tại.

## Kiểm tra kỹ thuật và giới hạn

[Summary](summary.json), [ledger](candidate-ledger.json), [reconstruction](crop-reconstruction.json) giữ evidence. ZIP CRC, đường dẫn giải nén, số lượng, decode, join và bounds đã kiểm. 29 derivative khớp pixel với ROI nguồn và khớp preprocessing bilinear letterbox 224 hiện hành. 80 JPEG được so với ROI resize: MAE RGB tốt nhất tối đa 2,0491/255; đây là diagnostic, không phải khẳng định encoder JPEG hoặc pixels gốc khớp tuyệt đối.

Không có trùng SHA-256 crop/source nội bộ hoặc trùng byte với batch 247 cũ; dHash crop khoảng cách ≤ 6 không tìm thấy cặp. Điều này không chứng minh độc lập cảnh/người: A có shot lặp, B có bốn view của cùng video. Việc chọn NA-008 thay NB-0014 dựa vào nội dung và context, không chỉ hash. Không suy danh tính xuyên camera; không phân chia views làm split, không mở media test/reserve.

Nhãn và geometry bộ mới vẫn Draft, chưa phải dữ liệu train. Canonical person box, lineage/group và membership/split còn gate riêng. Không thay đổi contract, release V9, model hoặc chạy train/test. Owner review shortlist và ngoại lệ là bước tiếp theo.

[Validation](validation.json): 471 liên kết local hợp lệ, 92 ID trong owner-review khớp chính xác shortlist, bộ lọc gallery PASS, ảnh render Chrome đã kiểm. AST và Ruff worksheet PASS (bỏ riêng E501 cho chuỗi nhận xét/HTML dài); repository checker PASS, diff không có lỗi whitespace. [Result pins](result-pins.json) bảo toàn kết quả; `owner-review.md` được để ngoài pins để owner ghi quyết định.
