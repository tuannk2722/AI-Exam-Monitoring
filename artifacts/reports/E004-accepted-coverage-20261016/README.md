# E004 — Tổng hợp crop accepted và đánh giá thiếu hụt

Ngày 16/10/2026. **Đã chốt 13 crop NC theo approval mới của owner; tổng cộng 345 crop mới accepted. Ưu tiên toàn bộ 345 crop cho train, không phân bổ thêm crop mới vào test/reserve. Coverage được bù một phần đáng kể, chưa đủ bằng chứng kết luận đã giải quyết các lỗi RC1.**

Approval ở đây chốt nhãn và crop hiện có. Dataset đang dùng optimizer vẫn là 716 train; 1.061 là quy mô dự kiến nếu toàn bộ 345 crop vượt các bước chuẩn hóa geometry/lineage/release. Không có training, inference hoặc chuyển tập cũ trong task này.

## Inventory đã chốt

| Batch | Accepted | Phone P / N / U | Looking P / N / U | Biết cả hai target |
|---|---:|---|---|---:|
| [Closure cũ](../E004-crop-closure-20261015/README.md) | 240 | 78 / 31 / 131 | 57 / 183 / 0 | 109 |
| [Closure bộ mới](../E004-new-bundle-closure-20261016/README.md) | 92 | 0 / 62 / 30 | 19 / 71 / 2 | 60 |
| NC-001 đến NC-013, approval lần này | 13 | 0 / 9 / 4 | 0 / 13 / 0 | 9 |
| **Tổng mới** | **345** | **78 / 102 / 165** | **76 / 267 / 2** | **178** |
| Train RC1 hiện có | 716 | 247 / 193 / 276 | 213 / 297 / 206 | 234 |
| **Dự kiến gộp vào train** | **1.061** | **325 / 295 / 441** | **289 / 564 / 208** | **412** |

[Ledger hợp nhất](accepted-ledger.json) chỉ lấy `final_labels` của hai closure, và nhãn Draft đã được owner approve cho 13 NC. [Receipt mới](approval-13.json) thay trạng thái Draft của 13 NC, không sửa bytes của snapshot cũ. NA-008 chỉ tính một lần trong 92; 7 crop bị loại và các shortlist lịch sử không cộng trở lại. Metadata nhãn gốc trong ZIP không là authority.

Mỗi dòng giữ upstream ledger, SHA source/crop/input, ROI và nhãn cuối. `preferred_role=train` ghi ưu tiên owner; `assigned_split=null` và `training_ready=false` phản ánh chưa có canonical enrollment. Không điền person box bằng context box để vượt gate.

## Bù được những thiếu hụt nào?

Đối chiếu [visual audit](../E004-visual-audit-20261014/README.md), [RC1](../E004-RC1-execution-20261014/README.md), [root cause](../E004-root-cause-20261014/README.md) và [targeted coverage](../E004-targeted-coverage-20261014/README.md). Targeted review chỉ có 44 train và 31 selection được chọn có chủ đích; các số factor của review này không phải census toàn bộ 716 train. Không cộng metadata hints thành ground truth.

| Thiếu hụt / vấn đề | Bổ sung đã xác nhận | Đánh giá hiện tại |
|---|---|---|
| Ít supervision mới thực sự vào optimizer | Có 345 crop accepted; 523 target-cell known mới; 178 crop biết cả hai target | Đủ một batch train bổ sung có ý nghĩa. Chưa có tác dụng optimizer cho đến khi được đóng package và dùng trong run |
| Phone trên bàn, phone trong tay, phân biệt calculator | Thêm 78 phone P và 102 phone N. Ví dụ phone trên bàn CB-0063, CB-0065; calculator N CB-0026, CB-0030-R1; NC-002, NC-006, NC-012 bổ sung calculator N | Đã bù ví dụ thị giác và hard negatives; chưa chứng minh tăng recall hoặc giảm FP. Không coi mọi N là calculator |
| Phone mờ, khuất, chỉ thấy lưng/cạnh | 165 phone U giữ đúng uncertainty; 77/78 P cũ có evidence code SCREEN, 1 P là adjudication riêng CB-0514-R1 | **Chưa xác nhận bù đủ positive khó.** U không giám sát trực tiếp phone; không đổi thành P/N để tăng số lượng |
| Looking ngoài vùng bài riêng | Thêm 76 P trên cả 7 parent video IDs | Có thêm supervision liên quan, chưa có số đo recall mới. Không suy gaze từ nhãn phone |
| Looking vào vùng bài, viết/đọc, calculator | Thêm 267 looking N; chỉ 2 looking U | Bù N mạnh hơn P. Tỷ lệ looking P trong known giảm từ 41,8% xuống 33,9% nếu gộp; cần theo dõi recall, không kết luận cân bằng hơn chỉ vì nhiều ảnh |
| Nhiều crop cùng người/nguồn | Không có exact crop/input duplicate; 345 crop đến từ 7 parent video IDs, 151 source frame khác nhau | Không tương đương 345 người hoặc 151 tình huống độc lập. Vẫn có tương quan theo người/video/góc quay |
| Sai attribution, mất chi tiết ở input 224 | Các crop đã qua các vòng review/recrop và owner approve; inventory kiểm hash input 224 | Task này không chứng minh representation đã hết lỗi. Không thay resolution hoặc architecture khi chưa có ablation |
| Overfit và kết quả phụ thuộc family | Batch mới tăng dữ liệu cùng bối cảnh lớp học | Chưa giải quyết bằng chứng thực nghiệm. RC1 overfit nhanh; không có cơ sở hứa thêm epochs sẽ cải thiện |

Trong 240 crop cũ, 11 mẫu có nhãn cuối phone N và evidence code CALC. Đây là phần calculator đã được ghi rõ, không phải toàn bộ calculator trong 345 crop. Evidence codes/phone_reason lịch sử phải đọc cùng closure adjudication: CB-0514-R1 đã đổi P, CB-0487 đã đổi U; không dùng code cũ để ghi đè nhãn cuối. Không thực hiện một vòng tái gán nhãn ngoài approval trong task này.

Mật độ biết cả hai target tăng có điều kiện từ 32,7% lên 38,8%. Tuy nhiên 165/345 crop mới (47,8%) không cung cấp loss phone; chúng vẫn hữu ích cho looking khi nhãn looking known. Tăng dữ liệu này không tương đương thêm 345 ví dụ phone.

## Độ đa dạng và giới hạn lineage

| Parent video ID | Crop | Phone P / N / U | Looking P | Source frame |
|---|---:|---|---:|---:|
| 131978f1c922c72a1be6 | 57 | 27 / 6 / 24 | 9 | 30 |
| 286f4f8992d4ad931647 | 71 | 35 / 4 / 32 | 10 | 40 |
| 2b68c2a8bc91941576a8 | 47 | 16 / 4 / 27 | 12 | 21 |
| 9284c725e608c9241824 | 41 | 0 / 7 / 34 | 18 | 21 |
| c4501991dd89a572c461 | 24 | 0 / 10 / 14 | 8 | 9 |
| 17e642e8e71392e7c926 | 42 | 0 / 28 / 14 | 2 | 16 |
| bb408b342822941f3212 | 63 | 0 / 43 / 20 | 17 | 14 |

**Toàn bộ 78 phone P mới nằm trong 3 parent videos đầu; 105 crop của bộ mới nhất không có phone P.** Đây là giới hạn quan trọng hơn tổng số crop. Bốn view của video B vẫn là một parent video. Parent IDs khác nhau cũng chưa chứng minh khác phòng, người hoặc nguồn gốc. Anchor keys ở các batch không đồng nhất, NC chưa có canonical anchor key; không báo chúng thành số người độc lập.

Kiểm toàn bộ 345 crop/input không có trùng SHA crop hoặc RGB input 224. So sánh SHA source/crop với metadata của development package và canonical V9 không thấy overlap chính xác. Kết quả này không loại trừ cùng video bị encode lại, cùng người hoặc near-duplicate khác frame. Không mở media test/reserve; cần đóng lineage trước release, đặc biệt tránh đưa cùng family với selection/test vào train. Nếu phát hiện xung đột, giữ phần liên quan ngoài enrollment và báo owner, không tự chuyển holdout sang train.

## Phương án ưu tiên train và bước tiếp

1. Giữ cả 345 crop accepted trong inventory; ưu tiên 345/345 cho train, **0 crop mới cho test/reserve**. Chưa có bằng chứng trùng chính xác để bỏ thêm crop accepted trong lần tổng hợp này. Sampling/cắt giảm theo người chỉ nên chốt sau khi thống nhất anchor lineage; không dùng tên anchor ZIP như định danh người chắc chắn.
2. Chuẩn hóa person boxes, anchor/group lineage và provenance cho package kế tiếp bằng công cụ hiện có; giữ nguyên crop bytes/nhãn accepted. Kế thừa quyết định semantics che hoàn toàn đúng scope và các adjudication riêng, không hồi tố nhãn V9. Package cần ghi rõ semantics revision; đánh giá ảnh hưởng tương thích các negatives trước release.
3. Giữ selection 71 hiện có để so sánh với RC1, giữ diagnostic/test/reserve cũ đúng vai trò. Test/holdout không cập nhật gradient, nhưng giúp phát hiện học thuộc và kiểm chứng khả năng tổng quát hóa. Không tạo thêm holdout từ batch mới trong đề xuất này.
4. Khi package đủ điều kiện, chuẩn bị experiment so sánh tác động **chỉ bổ sung dữ liệu** với baseline phù hợp, cùng selection và các biến còn lại được pin. Không đồng thời đổi resolution/model/threshold để rồi không biết cải thiện do đâu. Run config/approval là bước riêng; chưa chạy trong task này.

Không cần chờ thu thập thêm thật nhiều crop mới trước khi chuẩn hóa batch này. Ngược lại, chưa thể tuyên bố đạt M1/M2/M3 chỉ từ coverage: RC1 còn thiếu recall và có overfit; chất lượng sau bổ sung phải được đo bằng run có đối chứng. Nếu tiếp tục bổ sung dữ liệu sau đó, ưu tiên phone P có đặc trưng phân biệt thật ở input, trên nguồn/góc quay đa dạng, nhất là desk/held/partial khó; không ưu tiên thêm hàng chục frame gần giống của cùng anchor.

## Kiểm chứng và tái lập

[analyze.py](analyze.py) là worksheet của hồ sơ này, không exporter hoặc CLI mới. [summary.json](summary.json) giữ counts, nguồn và overlap; [input-pins.json](input-pins.json) giữ inputs; [accepted-ledger.json](accepted-ledger.json) giữ 345 dòng. Script kiểm 49 upstream pinned files, SHA source/crop/input từng dòng, input 224, IDs và checksum manifest. Membership train/selection lấy từ resolved config RC1 đã pin: development manifest có 847 records, trong đó 120 val bao gồm 49 diagnostic và 71 selection; không lấy cả 120 làm selection.

Giới hạn: phép so sánh coverage dựa trên accepted labels và evidence review đã có, không phải visual census factor mới của mọi crop train. Không truy cập test/reserve pixels, không chạy model, không đo quality mới. Validation kỹ thuật không thay nghiệm thu canonical dataset/model.
