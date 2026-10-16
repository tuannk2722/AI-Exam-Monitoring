# E004-PHONE-OCCLUSION-20261015

Owner: repository-owner; ngày 15/10/2026. **Accepted cho quy tắc**, không là nghiệm thu 247 nhãn/release.

Agent hỏi về CB-0571-R1: review đề xuất phone N khi giấy che hoàn toàn vùng thiết bị, khác điều kiện absence trước đây. Owner chọn nguyên văn: **“Đổi quy tắc: vật bị che hoàn toàn có thể tính N”**. Owner trả lời **“bỏ qua”** cho dấu `*` ở CB-NEW-04.

Áp dụng từ revision này và revision tiếp theo dẫn quyết định: vật bị giấy/vật khác che hoàn toàn, không còn phần thiết bị mơ hồ lộ ra, tay và vùng quan sát còn lại đủ review không có phone nhìn thấy thì **có thể N**. Không suy phone vô hình từ frame khác. N này là absence theo evidence quan sát được, không khẳng định thực tế chắc chắn không có phone sau vật che.

Không tự động N: tay mất khỏi crop/dưới bàn, attribution mơ hồ hoặc vật **còn lộ một phần** không phân biệt được vẫn U nếu không có phone khác rõ. Phone khác nhận dạng được và gắn anchor có ưu tiên P. Không mở rộng thành mọi ảnh không nhận ra phone đều N.

Scope: E004-device-consistency-20261015, 247 crop từ refinement. Không hồi tố accepted V9/releases/metrics/pins; không đổi schema/encoding/model/splits. Package mới cần ghi semantics revision trong provenance/evidence; không so metrics hai phiên bản như cùng ground truth khi chưa đối chiếu delta. Quyết định không cấp quyền train/final test.

Các semantics khác giữ nguyên: mobile, attribution, calculator không tự negative, U masked, nhìn thiết bị trong vùng riêng không tự looking P. Refinement cũ giữ snapshot/pins; rubric cũ được supersede bởi [rubric mới](rubric.md) đối với batch này.
