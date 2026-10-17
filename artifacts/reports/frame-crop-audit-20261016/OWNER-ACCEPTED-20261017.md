# Chốt 98 crop — owner duyệt ngày 17/10/2026

Owner duyệt toàn bộ phương án trước, với ba sửa cuối: **G23-A03-F00009 U/N** vì vật trắng trong tay chưa rõ; **G27-A02-F00022 và G27-A03-F00031 P/P** vì owner xác nhận phone trong crop gắn với anchor. Không còn 28 đề xuất chờ duyệt của vòng này.

Giữ **98 crop**, gồm **G06-A03-F00012-R02** thay khung cũ. Loại G14-A10-F00018 và G17-A01-F00012. G18-A03-F00001 U/N, F00010 U/P giữ đúng quyết định trước. Nhóm theo video và anchor; không ghép danh tính/lớp khi chưa có mapping.

[Receipt và đủ 98 nhãn/SHA](owner-accepted-20261017.json) · [Gallery đã chốt](../../../data/interim/frame-crop-accepted-20261017/index.html) · [ZIP 98 crop và metadata](../../../data/interim/frame-crop-accepted-20261017/accepted-98.zip).

Receipt này supersede trạng thái chờ duyệt của OWNER-REVIEW-20261017.md và ledger đề xuất, không sửa bytes các hồ sơ đó. Approval chỉ cho crop/nhãn/membership; chưa nhập V10, chưa assignment/split hoặc train. Crop bổ sung từ additional.zip là batch review riêng.

Phone U có mask 0 nên không tạo nhãn negative đối nghịch trong loss/metric; nó loại target phone khỏi supervision. Tuy vậy, dùng U cho positive owner đã xác nhận sẽ mất tín hiệu học hợp lệ. Vì vậy hai G27 được chốt P theo quyết định cụ thể; không dùng số người còn trong crop để tự gán mọi thiết bị lân cận cho mọi anchor khác.

Kiểm: 98 PNG exact SHA từ crop đã review (gồm revision G06), đúng ba correction cuối và hai ID loại; ZIP CRC/membership PASS. Không sửa dataset hiện hành.
