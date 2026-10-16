# Chốt batch 247 crop sau owner review

Ngày chốt: **16/10/2026**; giữ ID hồ sơ đã khởi tạo ngày 15/10. **240 crop giữ lại, 7 crop loại khỏi batch**, sửa 3 cặp nhãn. [Receipt](closure-receipt.json) chốt nhãn và crop hiện có; không phải release train. [Ledger](candidate-ledger.json) giữ đủ 247 dòng và nguyên provenance. [Review owner được lưu nguyên bản](owner-review-input.md).

Trong ledger closure, `final_labels` và `closure_disposition` là kết luận hiện hành; các trường Draft/evidence kế thừa giữ lịch sử revision trước, không dùng chúng thay nhãn chốt.

| Crop | Trước | Chốt | Bằng chứng |
|---|---|---|---|
| CB-0514-R1 | U/N | P/N | Thiết bị thứ hai trên bàn có mặt kính xanh và viền; không dựa vào lưng vật trong tay. |
| CB-0487 | P/N | U/N | Vật cầm chỉ lộ lưng; mảnh tối sau tay không đủ phân biệt thiết bị tại input 224. |
| G2-A12-F005 | U/P | N/P | Theo owner và kiểm ảnh: tay cầm bút, tay gần miệng; đầu hướng ngoài vùng bài riêng. |

CB-0449 giữ P/N vì phần mặt kính và viền còn đủ phân biệt. Không nâng toàn bộ cụm vật đen thành P: độ che hoặc màu đen không quyết định loại vật. Các trường hợp chỉ còn khối mờ, mặt sau hoặc cạnh không phân biệt được vẫn U. CB-0609-R1 giữ U/P: ngay frame gốc, đầu bàn tay vẫn bị người khác che; mở rộng crop không tạo đủ bằng chứng absence.

Loại 5 U/U theo owner: CB-0601-R1, CB-0673, CB-0702, CB-0718-R1, G3-A05-F003. Loại thêm G5-A05-F109 và G5-A06-F099 theo quyền owner cho phép: nhiều người và hướng đầu cạnh tranh làm attribution không rõ. Đây là quyết định QA crop, không phải kết luận đã đo tác hại model. Không xóa ảnh gốc.

Các crop không được đề cập được ghi nhận approval batch của owner. Ngoại lệ được giải quyết bằng audit theo yêu cầu owner, không ghi giả rằng owner đã trực tiếp chọn từng nhãn sửa. [37 kết luận ngoại lệ](exception-findings.json) và [3 delta](label-deltas.json) giữ lý do từng mẫu. Phân bố 240 crop: P/N 69, P/P 9, N/N 22, N/P 9, U/N 92, U/P 39.

Đã kiểm tất cả source/crop/input SHA-256 và cả hai bộ pins của revision trước; originals không thay đổi. Canonical person geometry, lineage/group, membership/split và training recipe vẫn cần gate riêng. Không lấy context box làm person box; không đổi V9 hoặc chạy model/train/test.

Bước tiếp theo độc lập: [audit bộ ZIP mới](../E004-new-bundle-audit-20261015/README.md).
