# Bàn review toàn bộ accepted crop V12

Mở [giao diện audit](../../../data/interim/v12-full-audit-20261021/index.html) bằng
browser trên máy này. Chạy trực tiếp bằng `file://`, không cần server hoặc Internet.

## Phạm vi đã đưa vào

**1.639 / 1.639 records có disposition approved trong ledger V12**, không lọc theo
usage, split, nhãn cũ, source hoặc kết quả model:

| Vai trò cũ, chỉ để đối soát | Số crop |
|---|---:|
| Train | 1.092 |
| Validation | 204 |
| Test | 11 |
| Review-only, gồm các cohort chưa được phân bổ | 332 |
| Tổng accepted | **1.639** |

418 records excluded không phải accepted; danh sách đầy đủ nằm trong
[inventory-check.json](inventory-check.json). Không thêm lại bản crop đã bị thay thế.
Đối chiếu các manifest local và trạng thái dự án không thấy package holdout accepted
riêng hiện hành ngoài inventory này. Không cộng chồng V11/V10 hoặc development
packages lịch sử vì sẽ lặp crop hoặc khôi phục crop đã excluded.

User ngày 21/10/2026 yêu cầu mở hết accepted, gồm test/holdout, để audit trước chia
lại tập. **11 crop test cũ đã được materialize vào giao diện audit**; danh sách ở
inventory-check. Đây là exposure cho visual review, không chạy prediction, metric,
tuning hoặc training. V12 cũ và freeze/pins không thay đổi; không được coi việc chia
lại các ảnh đã review là tự tạo ra holdout độc lập. Split mới chưa được thực hiện.

## Cách review

- Lưới 12 crop/trang, 48 nhóm gần nhau về hình ảnh; ô chọn nhóm và tìm ID/tag/ghi chú.
  Mặc định hiển thị tất cả theo thứ tự tương đồng. Lọc chưa chốt, đã chốt, đánh dấu,
  cần crop lại, đề xuất loại hoặc ảnh được phóng lên 224.
- Bên phải là crop hiện tại và **224 × 224 CSS pixels**. Bản train được tạo bằng
  RGB letterbox bilinear, fill `[124, 116, 104]`, đúng recipe E006 SQRT. Không kéo méo,
  không normalization hiển thị hoặc augmentation ngẫu nhiên. Browser zoom 100%
  khi so độ lớn; CSS pixel không nhất thiết là pixel vật lý màn hình.
- Viền cam ở crop bên trái chỉ đúng person anchor từ geometry cũ, có thể tắt.
  Viền không có trong ảnh đầu vào train. Bấm ảnh trái mở bytes crop gốc trong tab mới.
- Nhãn review mới để trống. Metadata cũ (nhãn, role, source, lineage, blockers)
  ẩn mặc định, chỉ hiện khi chủ động bật. Không có scores hoặc nhãn gợi ý.
- Phone/Looking P/N/U riêng với quyết định giữ/crop lại/đề xuất loại/cần xem thêm.
  Có góc nhìn, tag tự đặt, note từng crop và note từng nhóm. “Đã chốt” cần xác nhận
  riêng; sửa nội dung sẽ bỏ trạng thái chốt. Đề xuất loại không bắt buộc chọn nhãn.
- Phím trái/phải chuyển crop khi không nhập liệu; nút “Crop chưa chốt tiếp theo”
  bỏ qua crop đã xong trong nhóm đang chọn. Tìm toàn inventory bằng nhóm “Tất cả”.
- Nháp tự lưu trong localStorage của browser. **Xuất JSON sau mỗi phiên** để có bản
  backup và chuyển máy/browser; localStorage không phải bản lưu bền vững. Nhập JSON
  kiểm cohort/ID/crop SHA/giá trị và hỏi trước khi thay toàn bộ nháp. Nháp chưa tự áp
  vào canonical ledger, release hoặc split mới.

## Cách nhóm và giới hạn

Feature không dùng nguồn/nhãn/split: màu RGB 8 × 8, cạnh grayscale và tỉ lệ crop.
Farthest-first k-means deterministic (48 nhóm), rồi nearest-neighbor order trong
nhóm. Đây là **tương đồng thị giác thô**, không tự nhận diện phone, hướng đầu hoặc
góc camera, và không là leakage group. Có nhóm chứa nhiều nguồn; hai ảnh tương tự
có thể khác nhãn. Xem [overview local](../../../data/interim/v12-full-audit-20261021/group-overview.png).
Nhóm lớn vẫn được phân trang; không bỏ ảnh để cân số lượng nhóm.

Gợi ý tự động chỉ dựa trên resize/derivative: đối chiếu chi tiết ở 224, kiểm frame
gốc khi cần, ghi rõ vùng thiếu đầu/vai/tay/bàn. Ghi chú nhóm nhắc xem mẫu tương phản.
Không phân tích để gán nhãn hoặc kết luận ảnh xấu từ kích thước. Các ví dụ phone
trong trao đổi trước là câu hỏi xin ý kiến, **không được nhập thành owner decisions**.
Looking quay đầu bên/sau là hướng mục tiêu owner chọn; giao diện không đổi data spec
hay áp rubric mới vào release đã accepted.

## Implementation và kiểm tra

- [Config](../../../configs/diagnostics/v12-full-audit-20261021.json) pin ledger và
  recipe, explicit test visual access; builder từ chối ghi đè output đã tồn tại.
- [Module](../../../src/ai_exam_monitoring/data/review_workspace.py) tái dùng strict
  PilotRecord, crop SHA và preview_input. Assets HTML/CSS/JS đi cùng package Python.
- [Inventory](accepted-inventory.json), [coverage/pins](inventory-check.json),
  [checks](checks.json), [browser checks](ui-checks.json). UI test dùng profile tạm
  riêng; lựa chọn test không phải quyết định owner và đã xóa khỏi profile trước chụp.
- 4 regression tests grouping/coverage; 6 tests source_review (gồm preview parity).
  Ruff và mypy phần thay đổi; JS syntax và browser thật: navigation, search,
  save/reload, export/download/import, reject sai cohort/SHA và kích thước preview.
- Toàn bộ crop copy giữ SHA gốc; toàn bộ preview đối chiếu pixel với hàm letterbox
  của trainer. Không model forward, không thay nhãn/split hoặc chạy training.

Review xong mới tổng hợp đề xuất giữ/crop lại/loại, coverage và các ràng buộc lineage
để thiết kế split/release mới. Review-only còn blockers cũ không tự đủ điều kiện train
chỉ vì đã có nhãn mới. Không stage/commit trong task này.
