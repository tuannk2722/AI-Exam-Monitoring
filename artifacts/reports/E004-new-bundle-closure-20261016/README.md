# Chốt 92 crop và bổ sung theo 8 ảnh khoanh đỏ

Ngày **16/10/2026**: đã chốt **92 crop**, sửa **9 cặp nhãn**, không loại thêm crop trong shortlist owner đã review. Bổ sung **13 crop Draft** từ frame gốc sạch; cả **14 vị trí khoanh đỏ** đã có mapping, gồm NA-008 đã tồn tại đúng frame 21 nên không tạo bản trùng.

Mở [gallery hiện hành](../../../outputs/E004-new-bundle-closure-20261016/index.html): mặc định hiển thị 13 crop bổ sung, có bộ lọc 92 crop đã chốt và toàn bộ 105 crop. Chỉ cần review phần mới tại [owner-review.md](owner-review.md). Hồ sơ trước đã pin nên được giữ nguyên; revision này là kết quả mới, không ghi đè gallery/ledger cũ.

## Chốt batch hiện có

[Owner review được lưu nguyên bản](owner-review-input.md), [closure receipt](closure-receipt.json), [ledger 92 crop](closed-ledger.json), [delta](label-deltas.json). Có 82 dòng approve theo chỉ dẫn không nhận xét, 10 dòng xử lý nhận xét; NB-0030 giữ N/N, 9 dòng đổi như sau. `final_labels` là nhãn chốt; `draft_labels` giữ lịch sử trước review.

| ID | Trước | Chốt |
|---|---|---|
| NB-0013 | U/N | N/N |
| NB-0015 | U/N | N/N |
| NB-0032 | N/U | N/P |
| NB-0063 | U/P | U/N |
| NB-0067 | N/N | N/P |
| NB-0034-R1 | N/P | N/N |
| NB-0041-R1 | N/P | N/N |
| NBX-004 | N/N | U/N |
| NBX-005 | N/N | U/N |

NB-0013 và NB-0015 được ghi nhận **quyết định nhãn cụ thể của owner**, thay đánh giá che tay quá thận trọng ở Draft; không tự mở rộng thành quy tắc “ảnh nét thì phone N” hoặc “mọi tay khuất đều N”. NBX-004/005 vẫn U theo review owner vì phần bàn/tay không đủ. Quyết định này không hồi tố nhãn của 240 crop đã chốt trước.

Đã đối chiếu thêm [bốn mẫu accepted trước](../../../outputs/E004-new-bundle-closure-20261016/accepted-comparison.jpg): CB-0026, CB-0055-R1, CB-0571-R1 và G2-A12-F005. Mờ và mất vùng quan sát là hai yếu tố riêng: các mẫu N này còn cho review vùng tay/bàn; CB-0571-R1 dùng ngoại lệ vật che hoàn toàn đã được owner duyệt. Không lấy một ảnh mờ có N để tự chuyển mọi ảnh rõ nhưng mất tay sang N.

NB-0032 chốt P cho looking theo owner: đầu/tay giơ ngoài vùng bài; so với NB-0048 N/P và NB-0080 N/N trong batch vừa duyệt, nhìn tờ bài đang cầm vẫn khác cử chỉ giơ tay ngoài bài. Không tạo quy tắc mọi vật giơ lên đều P. NB-0067 đúng anchor áo xanh tiền cảnh quay sang bên; NB-0034-R1 và NB-0041-R1 nhận quyết định N về đích nhìn của owner, không đòi phải thấy mắt nhưng cũng không tự gán P vì đầu hơi nghiêng.

NB-0063: đã mở source frame 77. Dù source cho thấy hai tay không có thiết bị, crop được review cắt mất bàn tay phía trái; giữ phone U trên chính input, looking N theo owner. Không dùng thông tin ngoài crop để gán N, và không âm thầm đổi geometry của mẫu đã review.

## Bổ sung vòng đỏ

| Frame A | Vị trí được khoanh | Kết quả |
|---|---|---|
| 9 | Người áo xanh hàng sau trái | NC-001 |
| 21 | Người đeo kính phía trước, calculator hồng | Đã có NA-008; giữ crop đã approve |
| 19 | Người tóc dài tiền cảnh trái | NC-002 |
| 16 | Người đeo kính trái; người áo xanh giữa | NC-003, NC-004 |
| 14 | Người tiền cảnh trái; người đeo kính giữa | NC-005, NC-006 |
| 13 | Năm người, theo thứ tự vòng đỏ từ trái sang phải | NC-007 đến NC-011 |
| 3 | Người đeo kính bên trái | NC-012 |
| 2 | Người đeo kính phía phải | NC-013 |

[Mapping máy đọc](marked-anchor-map.json), [ledger bổ sung](additions-ledger.json), [bảng 13 input](../../../outputs/E004-new-bundle-closure-20261016/additions-board.jpg). Đã mở cả 8 frame gốc và kiểm tất cả 13 input 224. Ảnh có vòng đỏ chỉ dùng để xác định anchor và được lưu kèm hashes; crop lấy từ source sạch, không chứa nét vẽ. Khung chữ nhật giữ chi tiết rồi letterbox 224 bằng hàm preprocessing hiện có, không kéo méo hoặc tăng nét AI.

NC-003 và NC-012 cùng anchor ở frame 16/3: frame 16 lộ cạnh/lưng nên U/N, frame 3 còn thấy keypad calculator nên N/N. Đây là khác biệt evidence trong từng input, không truyền loại vật từ frame khác. NC-009 sau kiểm native thấy đủ hai tay nên N/N. NC-010 vẫn U/N do tay bị người phía trước che. 13 crop không đồng nghĩa 13 người mới; giữ những frame cụ thể owner yêu cầu, có thể cùng người với mẫu khác nhưng không tạo lại NA-008 cùng frame/context.

## Kiểm tra và phạm vi

[Validation](validation.json) và [result pins](result-pins.json) ghi kiểm integrity, coverage và gallery. Receipt chỉ chốt nhãn/crop hiện có, không phải canonical release/train approval; 17 dòng không nằm trong shortlist trước vẫn giữ trạng thái lịch sử, không tự approve theo câu “không nhận xét”. Crop bổ sung vẫn Draft; không đổi split, person geometry, model hoặc chạy train/test. Không sửa contract chung trong task này.
