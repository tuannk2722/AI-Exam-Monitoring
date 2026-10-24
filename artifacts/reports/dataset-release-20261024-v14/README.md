# Release V14 — 24/10/2026

**Đã release local `pilot-b-20261024-v14`, sử dụng đủ 53 crop mới trong train.** Owner giao agent chốt nhãn, chọn allocation và release; quyết định cuối yêu cầu đưa toàn bộ crop mới vào sử dụng. [Receipt](owner-direction.json) ghi đúng phạm vi ủy quyền, không giả định owner đã tự review từng nhãn.

| Phần | Số crop |
|---|---:|
| Train | 1.199 |
| Validation/development | 156 |
| Test | 0 |
| Manifest được sử dụng | **1.355** |
| Excluded, chỉ giữ metadata trong ledger | 2 |

Hai crop `G01-A02-F00001-R02`, `G01-B02-F00009` bị loại theo yêu cầu owner vì chất lượng kém. Chúng không có trong manifest hoặc crop payload V14; V13 giữ nguyên bytes và pins. Không đổi nhãn hoặc geometry của 1.302 crop V13 được giữ lại.

## Nhãn và nguồn ảnh mới

Đã kiểm đủ 53 PNG từ ZIP, không có duplicate SHA/RGB nội bộ. Review từng crop ở native và letterbox 336 px; kiểm lại overlay person box, sửa các box cắt tóc/tay trước export. Nhãn Phone / Looking theo [policy hiện hành](../v12-reconcile-20261022/owner-policy-20261023.md); điện thoại trên bàn đúng anchor vẫn phone-positive, calculator không phải phone, góc camera sau/nghiêng không tự là looking-positive. Không suy work context từ hai nhãn negative.

- [Inventory gốc và mapping tên ZIP → ID](inventory.json): các trường label null là snapshot lúc nhập, không phải nhãn cuối.
- [Nhãn cuối, lý do, person box, exact SHA và lineage từng crop](visual-review.json).
- [Bảng nhãn 53 crop để đọc nhanh](labels.md).
- [Similarity triage](similarity-triage.json): 3 ứng viên gần nhất trong V13 cho mỗi ảnh thematic, tổng 99 cặp đã xem; dHash chỉ hỗ trợ shortlist.
- ZIP nguyên bản giữ tại `data/raw/owner-generated-20261024/temp.zip`; nguồn crop tại `data/interim/v14-generated-review-20261024/images`. [Source roots](source-roots.json) phục vụ exporter chuẩn.

Owner xác nhận 20 ảnh có tên ID được generate chỉ từ đúng 5 parent tương ứng. 33 ảnh nhóm `1.*`, `2.*`, `3.*` được generate theo mục tiêu sửa lỗi và không có exact parent ID; hồ sơ giữ rõ giới hạn này. Không coi khác SHA hoặc ảnh generate là nguồn độc lập mới. Quyền dùng là nghiên cứu local do owner yêu cầu; không suy ra giấy phép phân phối công khai hoặc quyền upload từ việc cung cấp ZIP.

## Allocation để dùng toàn bộ crop mà không tách nhóm nguồn

[Allocation và danh sách 27 crop chuyển split](allocation.json) ghi toàn bộ 6 nhóm được chuyển **val → train**: parent của `E004-EX-C003`, `G06-A01-F00012`, `NEW-132`, `V7-A-074`, `V7-C-046-R05` và nhóm G12.

`1.9.png` có bối cảnh/nhân vật rất giống `G12-B03-F00001`. Đây là quan hệ nghi vấn thị giác, không là parent đã xác minh. Xử lý bảo thủ: gộp cả 33 ảnh thematic với nhóm G12 ở train, chuyển đủ 9 crop cũ của nhóm đó. Với 20 derivative có parent đã xác nhận, giữ cùng leakage group với parent và chuyển cả nhóm nguồn. Không chuyển riêng một crop rồi để crop cùng nguồn ở val. Phương án review-only trước đó đã được thay thế theo yêu cầu mới nhất của owner.

Val còn 86 nhóm, 44 phone-positive / 105 negative / 7 unknown và 29 looking-positive / 127 negative. Không thêm synthetic vào val, không chuyển train cũ sang val. Cả 53 ảnh mới có supervision cho hai target và đều nằm trong manifest train.

## Kiểm tra và cách dùng tiếp

[Validation](validation.json) kiểm schema, source/crop pixel parity, payload SHA, strict loader, membership, đủ 53 generated train và không có known group trộn train/val. Tái dựng đảo thứ tự records cho exact payload giống nhau; 30 regression tests schema/exporter PASS. [Pins](package-pointers.json), [config](../../../configs/datasets/pilot-b-20261024-v14.json), [inputs bảo toàn](input-pins.json) và [class weights từ train](train-class-weights.json) là evidence dùng tiếp. Đọc manifest qua loader; không glob crop folder để chọn dữ liệu.

Val V14 đã đổi composition và được hình thành sau audit lỗi E007: **chỉ là development validation, không phải independent holdout**. Giới hạn exact lineage của 33 ảnh mới và 21 generated kế thừa V13 vẫn tồn tại; kiểm nhóm/SHA không chứng minh mọi quan hệ nguồn tiềm ẩn đã được biết.

[Companion E008 V14](../../../configs/experiments/E008-V14-LOOKING-20261024/README.md) giữ approval thiết kế và pins đầu vào mới. Khi tiếp tục E008, chạy mới G0/G1/A1 trên cùng V14, cùng protocol; không warm-start checkpoint E007 đã dùng val cũ để selection, không dùng E007/V13 metrics làm baseline trực tiếp để tuyên bố tác động của pooling. Không đổi thresholds/gates hoặc mở test trong task này. Chưa train/inference/upload.
