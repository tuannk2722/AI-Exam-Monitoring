# Kết quả pose diagnostic — 26/10/2026

## Kết luận

**Run completed; candidate chưa đạt feasibility, không promotion hoặc suppression.** Owner đã duyệt exact README/proposal, [authorization](../../../configs/runtime/RUNTIME-D2-POSE-DIAGNOSTIC-20261026/authorization.json) pin hai snapshot. Giữ proposal draft gốc nguyên bytes; authorization là evidence approval. Không inference lặp, tuning hoặc đổi D2/G0.

[Gallery](../../../outputs/runtime-d2-pose-diagnostic-20261026/index.html), [run](../../../outputs/runtime-d2-pose-diagnostic-20261026/run.json), [pair comparison](../../../outputs/runtime-d2-pose-diagnostic-20261026/pairs.json), [acquisition](../../../configs/runtime/RUNTIME-D2-POSE-DIAGNOSTIC-20261026/acquisition.json). YOLOv8n-pose official, SHA c6fa93dd1ee4a2c18c900a45c1d864a1c6f7aba75d84f91648a30b7fb641d212, 6.832.633 bytes. Phiên bản package/config/source/environment ghi trong run. 19 source frame forwards đã thực hiện, không extra real-media smoke; khoảng 9,73 giây đoạn run sau ghi environment, không là benchmark/SLA hoặc tổng thời gian tác vụ.

## Đối chiếu accepted references

| Case | Owner | Proposed | Pose support hai box |
|---|---|---|---|
| C01 | Same | Unknown | [7,21] / [7,21] |
| C02 | Same | Unknown | [] / [] |
| P04 | Same | Unknown | [] / [] |
| P06 | Same | Unknown | [] / [10,20] |
| P01 | Different | Unknown | [6] / [] |
| P02 | Different | Different | [8] / [19] |
| P03 | Different | Unknown | [] / [4] |
| P05 | Different | Unknown | [] / [18] |

Pose ID chỉ có nghĩa trong frame. Không có wrong_same hoặc wrong_different trên 8 references, nhưng 7 unknown; 0/4 duplicate được giải quyết. Không diễn đạt thành 100% precision/an toàn. Trên 259 cặp giao nhau: 102 different_proposed, 157 unknown, 0 same_proposed. Những cặp chưa review vẫn không có ground truth; không gọi 102 dự đoán là đúng.

Có 416 pose instances qua 19 frame. Trong 342 D2 anchors: 80 có 0 support, 210 có 1, 51 có 2 và 1 có 3. Đó là số support theo rule đầu/vai đã duyệt, không số người thật hoặc recall pose. Kiểm visual overlay C01 cho thấy các pose chồng nhau ở vùng người bên phải; mapping xác nhận ambiguity. C02/P04 thiếu support không tự chứng minh ảnh không có đầu/vai: có thể do confidence, containment hoặc pose prediction; chưa phân rã nhân quả từng điều kiện. Không sửa owner labels/keeper.

## Ý nghĩa và bước tiếp theo

Rule dựa trên containment của đầu/vai và unique pose không đủ dùng cho duplicate ở cohort này. Không giảm minimum points, tăng NMS suppression hoặc lấy pose confidence cao nhất sau khi xem kết quả để qua gate. Việc giữ unknown thực thi đúng abstain nhưng không hoàn thành mục tiêu xử lý duplicate.

D2 tiếp tục baseline với duplicate đã biết. Candidate này dừng ở diagnostic; không đưa vào runtime. Nếu tiếp tục nhánh tự động, cần một hypothesis khác được thiết kế riêng (ví dụ đánh giá detector/refinement trực tiếp theo person instance và người bị che), với candidate/variables/chi phí và cohort acceptance cụ thể. Không hứa đổi model sẽ xử lý được; không lặp vòng owner review cùng các cặp đã accepted. Bộ 4 same/4 different và keeper đã có được tái dùng làm development references, không đổi thành test độc lập.

## Kiểm tra và retention

4 tests synthetic PASS: thiếu đầu/vai, nhiều support, tất cả điểm đầu visible phải nằm trong box, missing/nonfinite => abstain. Ruff PASS; strict mypy toàn 66 source files PASS. CI thêm test_pose_diagnostic.py. Run preflight kiểm authorization/proposal/design, 7 input pins, weights, packages, source PNG pins/deadline; nhãn accepted chỉ đọc sau matching. Checksum mọi run artifacts PASS. Gallery links kiểm tồn tại; kiểm mẫu overlay C01. Không sửa source sau khi run để đổi prediction; không stage/commit.

Media deadline giữ 01/11/2026 15:55 giờ Việt Nam. Outputs chứa overlay diagnostic mới, source links và metadata có pins; không upload. Không scratch/checkout mới; weights và run là evidence được giữ trong outputs, không đưa binary vào Git.
