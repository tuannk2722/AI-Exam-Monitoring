# Owner review batch 04 — nhãn ảnh mới, hai recrop và ba cặp gần lặp

Thứ tự nhãn luôn là **Phone / Looking**. Đây là bản dự thảo để owner nghiệm thu theo batch; chưa là chốt release hoặc chia split. Không cần nhập lại nhãn từng ảnh: có thể duyệt nhóm và chỉ ghi ID ngoại lệ.

Batch 03 đã áp: 51 recrop được duyệt, NB-0031 loại; B01/B03 P/N, tám ca B khác U/N. E004-EX-C184 giữ **U/N**, ngoại lệ phone U riêng cho crop quay lưng theo xác nhận chat; không mở rộng thành quy tắc chung.

## A. Hai crop theo anchor anh đã chỉ rõ

[So sánh trước/sau](../../../data/interim/v12-reconcile-20261022/anchor-recrops-after-batch03/comparison.jpg). [Tọa độ và pins](geometry-anchor-batch03.json).

| Mục | Crop | Đề xuất | Cần chốt |
|---|---|---|---|
| A01 | G07-B12-F00029 | Giữ recrop mới, N/N | Người tóc buộc ở giữa; đã bớt người bên trái, giữ đầu và tay của anchor. |
| A02 | G22-B16-F00034 | Giữ recrop mới, **U/N** | Người tóc buộc bên phải. Có vật tối màu trên bàn gần sách, chưa phân biệt phone với calculator; không phải U vì khuất tay. |

**Quyết định A01:** approve

**Quyết định A02:** approve

## B. Hai nhãn mới cần chú ý

| Mục | Crop | Dự thảo trước → đề xuất | Lý do |
|---|---|---|---|
| B01 | [NEW-025](../../../data/interim/v12-reconcile-20261022/additional/NEW-025.png) | N/P → **U/P** | Vật tối dạng thiết bị trên bàn; ảnh nhỏ, chưa xác định được phone. |
| B02 | [NEW-032](../../../data/interim/v12-reconcile-20261022/additional/NEW-032.png) | N/P → **N/U** | Thấy phía sau đầu, chưa đủ rõ mức xoay ngang để gán P. Phone N vì không có vật nghi phone nhìn thấy; ngoại lệ C184 không tự áp sang ảnh này. |

**Quyết định B01:** approve

**Quyết định B02:** N/N

**Lưu ý:** với những crop có góc camera sau lưng thì chỉ khi thấy người đó quay mặt sang nganh hai bên hoặc ngoảnh hẳn về phía sao thì mới looking_around P.

## C. Đề xuất loại ba ảnh mới gần lặp

Không trùng bytes hoặc RGB, nhưng khác biệt quan sát không bổ sung rõ tư thế/hành vi của người chính. Đề xuất giữ crop cũ và loại bản mới; chưa áp loại trước khi owner chốt.

| Mục | Giữ | Đề xuất loại | Evidence |
|---|---|---|---|
| C01 | G2-A01-F001 | NEW-012 | [So sánh hàng dưới](../../../data/interim/v12-reconcile-20261022/boards/near-repeat-details-01.jpg): cùng tư thế cúi viết, nội dung chính gần lặp. |
| C02 | CB-0405 | NEW-052 | [So sánh hàng trên](../../../data/interim/v12-reconcile-20261022/boards/near-repeat-details-02.jpg): cùng người cầm phone, cùng bố cục/tư thế. Kết luận này thay đánh giá sơ bộ “distinct variant” ở pair 7 của vòng trước. |
| C03 | G13-B03-F00010 | NEW-056 | [So sánh hàng trên](../../../data/interim/v12-reconcile-20261022/boards/near-repeat-details-01.jpg): cùng tư thế cầm phone và cúi đầu, chủ yếu khác chi tiết tái tạo. |

NEW-119/NEW-121 đã đối chiếu riêng: hướng đầu khác thấy rõ khi xem lớn, đề xuất giữ cả hai. Không yêu cầu chốt lại NEW-120/122 đã được anh duyệt.

**Quyết định C01–C03 (duyệt cả nhóm hoặc ghi ngoại lệ):** giữ NEW-012 N/N, loại G2-A01-F001, giữ CB-0405 U/N, loại NEW-052, giữ NEW-012 P/N, loại G2-A01-F001, 

## D. Nghiệm thu batch nhãn và khung người của ảnh mới

[Nhãn đủ 156 ảnh](additional-annotations-draft-r4.json), [khung người và pins](additional-geometry-draft-r3.json). 153 ảnh đang đề xuất giữ; NEW-021, NEW-057, NEW-150 đã loại theo vòng trước. Nếu duyệt loại cả ba mục C, còn 150 ảnh mới. A/B/C tường minh có ưu tiên hơn duyệt chung D.

Khung đỏ là người chính; toàn ảnh đầu vào vẫn giữ làm context. Đã xem lại đủ tám bảng sau sửa khung. Đây là nhãn do agent dự thảo và kiểm, **chưa phải owner đã nghiệm thu toàn bộ 156 ảnh**.

| Khoảng ID | Bảng nhãn và khung người |
|---|---|
| NEW-001–020 | [Bảng 1](../../../data/interim/v12-reconcile-20261022/boards/new-final-draft-01.jpg) |
| NEW-021–040 | [Bảng 2](../../../data/interim/v12-reconcile-20261022/boards/new-final-draft-02.jpg) |
| NEW-041–060 | [Bảng 3](../../../data/interim/v12-reconcile-20261022/boards/new-final-draft-03.jpg) |
| NEW-061–080 | [Bảng 4](../../../data/interim/v12-reconcile-20261022/boards/new-final-draft-04.jpg) |
| NEW-081–100 | [Bảng 5](../../../data/interim/v12-reconcile-20261022/boards/new-final-draft-05.jpg) |
| NEW-101–120 | [Bảng 6](../../../data/interim/v12-reconcile-20261022/boards/new-final-draft-06.jpg) |
| NEW-121–140 | [Bảng 7](../../../data/interim/v12-reconcile-20261022/boards/new-final-draft-07.jpg) |
| NEW-141–156 | [Bảng 8](../../../data/interim/v12-reconcile-20261022/boards/new-final-draft-08.jpg) |

**Quyết định D (duyệt batch nhãn/khung người hoặc ghi ID cần sửa):** NEW-004 P/N, NEW-025 U/N, NEW-032 N/N, NEW-069 exclude và sẽ được thay bằng crop tôi gửi trong khung chat nhãn N/N, NEW-085 N/N, NEW-099 exclude, NEW-120 N/N, NEW-124 U/P, NEW-125 exclude, NEW-130 exclude, NEW-133 N/N

## Giới hạn còn phải xử lý trước kế hoạch release

Đã đối chiếu thị giác 134/156 ảnh mới với một họ cảnh cũ; 22 ảnh thuộc 8 họ cảnh còn chưa xác định được crop gốc. Đây là suy luận từ nội dung, không xác minh recipe tạo ảnh. Không yêu cầu anh tìm lại lịch sử generate; agent tiếp tục phần đối chiếu và đề xuất nhóm chống leakage trước chia split. Không tự coi các ảnh mới là mẫu độc lập.

Đã xem 91 cặp vòng trước và 153 cặp mở rộng, với đính chính NEW-052 ở trên. Kết quả là sàng lọc có evidence, không bảo đảm toán học rằng không còn mọi dạng gần trùng. Còn hoàn thiện tọa độ person geometry cho recrop cũ, hợp nhất nhóm liên quan và QA sau quyết định batch này. Chưa release hoặc train.
