# Rubric áp dụng cho audit legacy V11

Đây là cách áp dụng các tiêu chí đã duyệt sau V9 vào **đề xuất mới của cohort 836**, không là sửa contract hoặc hồi tố accepted releases. Owner còn phải nghiệm thu batch/ngoại lệ. Các quyết định sửa một crop ở vòng trước không tự thành threshold chung.

## Nguồn thẩm quyền

| Nguồn | Tiêu chí mang sang audit |
|---|---|
| [Device rubric 15/10](../E004-device-consistency-20261015/rubric.md) | Phone identity → attribution → absence; nhìn độc lập; kiểm input 224; không nâng known từ source/frame khác |
| [Owner occlusion 15/10](../E004-device-consistency-20261015/owner-direction.md) | Vật bị che hoàn toàn có thể N nếu tay/vùng còn lại đủ; không áp cho tay mất hoặc vật còn lộ mơ hồ |
| [Refinement 15/10](../E004-crop-bundle-refinement-20261015/README.md) | Tinh gọn crop theo anchor/evidence, không lấy số lượng làm acceptance |
| [Crop closure 15/10](../E004-crop-closure-20261015/README.md) | Crop/nhãn/membership là các phần phải review; sửa nhãn không thay geometry acceptance |
| [New bundle closure 16/10](../E004-new-bundle-closure-20261016/README.md) | Chọn thêm đúng người/context; recrop hoặc bổ sung không tự kế thừa nhãn |
| [Owner review 17/10](../frame-crop-audit-20261016/OWNER-REVIEW-20261017.md), [Accepted](../frame-crop-audit-20261016/OWNER-ACCEPTED-20261017.md) | Đối chiếu nguồn/crop/input, sửa geometry và nhãn theo evidence; owner quyết định batch và ngoại lệ |
| [Additional closure 17/10](../frame-crop-additional-20261017/README.md), [owner receipt](../frame-crop-additional-20261017/owner-accepted.json) | Có thể giữ, loại hoặc thay geometry; crop mới cần kiểm lại hai target, không ép quota |
| [Data contract hiện hành](../../../docs/data.md) | Hai target độc lập, U masked; accepted data bất biến, provenance/rights/group/test guards giữ nguyên |

## Phone_use

- **P:** còn cấu trúc nhận dạng mobile trong crop/input: mặt kính/màn hình lớn và viền đủ phân biệt calculator, hoặc mặt sau có đặc trưng như cụm camera. Thiết bị đúng tay hoặc bàn/sách của anchor, có tương tác/attribution rõ. Không đòi bật sáng, thấy chữ/app, hoặc thấy cả hai tay nếu đã có mobile rõ.
- **N:** tay và vùng thao tác đủ kiểm, không có phone hoặc thiết bị chưa phân loại còn lộ. Calculator có keypad rõ, laptop/tablet/camera/điện thoại bàn không tự thành phone P; vẫn kiểm tay còn lại và phone khác. Vật bị giấy/vật khác che hoàn toàn có thể N theo ngoại lệ owner nếu phần quan sát còn lại đủ.
- **U:** chỉ thấy khối chữ nhật, màu vỏ, lưng/cạnh trơn, chấm mờ, mảnh thiết bị chưa phân loại; tay dưới bàn/ngoài khung hoặc attribution chưa rõ. Không dùng tư thế cầm/bấm hay phone của người cạnh. Không chuyển U thành N chỉ vì không nhìn thấy phone.

## Looking_around

- **P:** đầu/hướng nhìn đủ rõ ra ngoài vùng bài riêng, sang người khác hoặc ra trước/ngoài vùng làm việc với context xác định. Không suy P từ phone P hoặc chỉ hơi nghiêng đầu.
- **N:** đầu/hướng nhìn rõ vào trang, thiết bị hoặc vùng thao tác của chính người đó. Không bắt thấy con ngươi nếu đầu/context đủ. Tư thế viết một mình chưa đủ nếu mặt/đích bị che hoặc không xác định.
- **U:** mất đầu, tóc/hood/tay che và không còn hướng/đích chắc, mắt nhắm/ngủ hoặc context mơ hồ. “Chưa đủ P” không tự N. Cúi xuống dưới bàn chỉ P khi đích ngoài vùng bài đủ rõ, không suy từ động tác cúi.

## Crop và quyết định membership

1. Native phải khớp context ROI của source, không nhầm frame/người. Person box chỉ người đích; context chứa đủ đầu, tay và vùng bài/thiết bị liên quan. Không tự lấy group box làm person box.
2. Đánh giá RGB input 224: anchor phải đọc được, nhãn known còn evidence sau resize. Source chỉ hỗ trợ attribution/geometry; không truyền chi tiết mất ở input hoặc thông tin từ frame khác. Không sharpen/inpaint hoặc đặt cutoff pixel/tỷ lệ che mới.
3. Nhiều người, nền stock hoặc crop nhỏ không tự bị loại. Cần xét người đích trội, vùng thao tác, nhiễu và độ rõ từng target. Không lấy người trước/sau thay evidence cho anchor. Crop có nhóm cạnh tranh hoặc sai person box đưa `recrop`, không chỉ sửa label để bỏ qua lỗi geometry.
4. Giữ được một target chắc vẫn có thể giữ crop, target còn lại U. U/U không đưa supervision. Source thiếu pixels không thể cứu bằng nới; lỗi ảnh ghép/chất lượng có thể cần rút crop dù còn một nhãn đọc được. Rút supervision không là xóa nguồn.
5. Recrop là derivative mới, kiểm lại native/input và cả hai target trước nghiệm thu; không tự nhân bản tất cả người trong nhóm hoặc nhập mọi frame gần nhau. Không ép cân bằng/quota hoặc tự đổi split/group.
6. `N/N` không tự thay metadata `confirmed_working`/normal context. Audit không tạo normal-context claim, rights/license approval hoặc identity/session grouping mới. Revision sau nghiệm thu cần kiểm đầy đủ các field đó theo contract và input hiện hành.

Quyền audit này không mở reserve/test, inference/training hoặc release mới. Các nhãn, split, pins accepted hiện tại giữ nguyên cho đến khi owner chốt revision có phạm vi rõ.
