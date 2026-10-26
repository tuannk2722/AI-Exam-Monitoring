# QA sơ bộ runtime clip — 25/10/2026

**Đã dừng full-frame theo quyền owner giao; phân tích phần đã có. Chưa nghiệm thu chất lượng crop/video, chưa mở tracking/events.** Giữ model G0 seed 20261023, calibration và context-v1. Không train, tune hoặc inference lại để làm báo cáo.

## Phạm vi và bằng chứng

Owner cung cấp clip và xác nhận toàn quyền sử dụng trong hội thoại. Sau khi thấy lượt chạy kéo dài, owner hỏi có nên dừng để phân tích ngay và cho phép agent tự thực hiện nếu hợp lý. Agent kiểm tiến độ, thấy còn gần 2 giờ theo tốc độ quan sát rồi terminate đúng hai process Python của lượt runtime. Không terminate process không liên quan.

Source 60 giây, 1.800 frame, 30 FPS, 1280 × 720; chỉ xử lý local. Receipt và lời duyệt ở [media approval](../../../outputs/runtime-clip-qa-20261025/media-approval.json), [decision](../../../outputs/runtime-clip-qa-20261025/owner-decision.md), pin [protocol](../../../configs/runtime/RUNTIME-QA-PREP-20261025/README.md) tại thời điểm chạy. Clip là input QA do owner chỉ định, không là test/holdout hoặc dữ liệu mới của V14.

- [Gallery QA partial](../../../outputs/runtime-clip-qa-20261025/partial-qa/index.html): source/boxes/crop/input của 5 frame, không phụ thuộc gallery cuối vốn chưa được runtime ghi.
- [Audit số liệu](../../../outputs/runtime-clip-qa-20261025/partial-qa/summary.json), [biên bản dừng và inventory SHA](../../../outputs/runtime-clip-qa-20261025/partial-qa/interruption.json), [execution](../../../outputs/runtime-clip-qa-20261025/execution.json).
- [Output gốc](../../../outputs/runtime-clip-qa-20261025/session/predictions.jsonl) và provenance trong cùng thư mục được giữ nguyên. Media và metadata liên kết clip ở local, không đưa vào Git; retention đến 01/11/2026 theo deadline session, hoặc xóa sớm theo yêu cầu, không xóa source ngoài workspace.

## Kết quả kỹ thuật và thời gian

| Nội dung | Kết quả |
|---|---|
| Frame hoàn tất có record | 436/1.800, khoảng 24,2%; index 0–435, thời gian video 0–14,5 giây |
| Observations | 9.450; mỗi frame 17–27 detections, không đồng nghĩa số người duy nhất |
| Gallery đã có | Frame 0/100/200/300/400; 105 anchor crops, từ 0 đến 13,33 giây |
| Thời gian CLI đến dừng | 2.170,21 giây ≈ 36 phút 10 giây; exit code -1 |
| Throughput ước lượng đầu-cuối | 0,201 frame/giây; bao gồm startup và overhead, không phải riêng model forward |
| Thời gian còn lại ngoại suy | Khoảng 113 phút, giả sử tốc độ và số detections tương tự; không là SLA |
| JSONL | Không dòng malformed; index liên tục, time tăng, boxes trong frame, score hữu hạn [0,1], cờ đúng ngưỡng |
| Bảo toàn | Source SHA và config approval/7 pins kiểm lại PASS sau dừng; SHA output partial ghi riêng |

JSONL chưa có final outcome; `session.json` vẫn `running` là trạng thái cũ do terminate không đi qua khối finally của Python. **Không sửa output gốc thành completed, không tạo checksums giả như run hoàn tất.** Biên bản interruption mới ghi trạng thái thực tế, xác minh không còn process runtime. Không có thống kê mean/p50/p95/RAM cuối nên không bịa các số này từ elapsed.

Cờ dự đoán trên 9.450 observations: phone 2.025, looking 2.269, đồng thời 314. Đây không phải số người, event hay TP/FP; observations gần nhau theo thời gian và detections trùng phụ thuộc mạnh, không tính accuracy/precision/recall từ các counts này.

## Review thị giác — draft cho owner

Đã xem contact sheet của toàn bộ 105 crops ở 5 frame gallery, boxes frame 0 và crop/input phóng lớn của các case nổi bật. Đây là triage thị giác, không phải 105 nhãn ground truth đã được owner nghiệm thu. Chưa đo detection recall hoặc matching IoU; không suy từ số detections rằng đã thấy đủ người.

| Finding | Evidence cụ thể | Ý nghĩa |
|---|---|---|
| Nhiều detections cho cùng người | Frame 0: a013/a014/a017/a018 quanh cùng người sát mép phải; a020/a021, a019/a022 cũng có box lồng nhau | 24 detections frame 0 không tương đương 24 người. Chạy classifier lặp trên crop cùng người làm tăng chi phí và có thể tạo tín hiệu mâu thuẫn cho downstream |
| Crop ảnh hưởng mạnh score | Frame 400 a013 và a021 cùng người: phone 0,1699 so với 0,8549; looking 0,1116 so với 0,4597. Cả hai input thấy thiết bị cầm tay; crop rộng thêm người phía trước | Hai observation cùng frame vượt ngưỡng khác nhau. Chưa quy nguyên nhân riêng cho context hay scale/letterbox; cần đối chứng được duyệt, không tự sửa padding |
| Có ví dụ phone gắn cờ phù hợp | Frame 0 a000/a001/a006: phone lần lượt 0,6845/0,8516/0,8467, dấu hiệu thiết bị nhìn thấy | Pipeline có tín hiệu hữu ích; chưa đủ suy độ chính xác tổng thể |
| Có ví dụ cần review bỏ sót phone | Frame 100 a003 score khoảng 0,019; frame 400 a003 score 0,0496: crop cho thấy vật cầm tay dạng điện thoại | Draft nghi FN, cần owner xác nhận semantics/attribution; không tự relabel data hoặc giảm ngưỡng |
| Looking cần review kỹ hơn | Ví dụ frame 0 a005/a008/a012 và frame 400 a003 có lưng/đầu hoặc đích nhìn khó diễn giải; nhiều cờ looking vẫn vượt ngưỡng | Không coi cờ là nhìn bài người khác; review context và unknown trước chốt FP/FN |

Context crop nhiều trường hợp chứa thêm người/tay/thiết bị của hàng xóm; đôi lúc phần đầu hoặc thân của anchor bị khuất. Điện thoại nhỏ ở hàng xa vẫn có thể thấy nhưng nhạy với crop/scale. Gallery partial thiên về 14,5 giây đầu, không đại diện toàn 60 giây. Đoạn che khuất 30–40 giây trong kế hoạch chưa được inference; không có evidence runtime cho đoạn đó. Không có tracking nên không nối anchor ID qua frame hoặc đếm người duy nhất.

## Hướng đi sau báo cáo

1. Owner review batch và các case trùng box/crop nhạy score trước khi nghiệm thu crop. Không nên tiếp tục full-frame CPU cùng cấu hình chỉ để chờ đủ phút video; tốc độ hiện tại cho giá trị QA thấp so với chi phí.
2. Đề xuất lượt QA mới lấy mẫu 1 Hz trên toàn 60 giây (60 frame) để tăng coverage thời gian, giữ model/crop/ngưỡng. Đây chỉ là đề xuất, cần config identity và approval riêng; 1 Hz không phù hợp để chứng minh recall hành vi ngắn hay làm benchmark tracking. Chưa chạy lượt này. Với chi phí quan sát hiện tại, riêng inference 60 frame có thể khoảng 5 phút cộng startup, chỉ là ngoại suy.
3. Đề xuất benchmark detector/duplicate handling trên cohort đã review trước mở tracking. Không tự chỉnh conf/IoU hoặc thêm suppression rule; box lồng nhau và người che nhau cần evidence, không thể xóa mọi box overlap.
4. Sau khi có coverage và crop QA phù hợp mới đi tiếp tracker/events. Chưa có căn cứ cần train lại classifier hoặc đổi calibration từ lượt partial này.

Giữ nguyên kết quả E008 và các configs/receipts đã pin. Kết luận hiện tại: **software có thể tạo observation thật, nhưng full-frame CPU chậm và detector/crop còn vấn đề cần review; chưa có acceptance chất lượng video.**
