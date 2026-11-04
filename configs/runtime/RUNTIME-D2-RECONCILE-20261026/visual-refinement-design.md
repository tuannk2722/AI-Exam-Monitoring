# Xác minh cùng người và chọn crop — thiết kế sau pair audit

## Scope và evidence

Owner duyệt tiếp tục thiết kế ngày 26/10/2026. Companion của duplicate-design.md đã pin; không thay bytes hoặc approval lịch sử. [Pair audit](../../../artifacts/reports/runtime-clip-qa-20261025/pair-audit-20261026.md) có 4 same (C01/C02/P04/P06), 4 different (P01/P02/P03/P05). Đây là development shortlist, không test hoặc đại diện toàn video. D2/G0/context-v1 giữ baseline.

## Khoảng thiếu trong code hiện tại

PersonDetector trong src/ai_exam_monitoring/inference/person.py trả xyxy/confidence, không head/pose/mask/identity. crop_boxes mở rộng hình chữ nhật theo margins và clip biên ảnh, không phân quyền thiết bị thuộc ai. Runtime gọi classifier trên context; không có pair verifier. A1/Dual ROI cũng không phải duplicate detector theo model-relevance.md. Vì vậy chưa thể hiện thực xác minh từ đầu/thân bằng cách chỉ nối các output sẵn có; cần thiết kế và chọn nguồn tín hiệu bổ sung.

## Luồng đề xuất

1. Candidate generation: diagnostic dùng toàn bộ 259 cặp giao nhau trong 19 frame đã audit; giao > 0 chỉ để liệt kê, không quyết định suppression. 8 cặp accepted là đối chứng cố định. Cặp không giao chưa được bảo đảm recall; không tuyên bố giải quyết mọi duplicate.
2. Visual verification: đối chiếu vị trí vùng đầu/thân của anchor trên source, kiểm khả năng hai box trỏ cùng người hay hai người che nhau. Output đề xuất same / different / unknown cùng evidence và phiên bản verifier; không dùng score phone/looking, màu áo đơn độc hoặc phần người hàng xóm nằm trong context để kết luận cùng người. Hiện chỉ owner relations là evidence accepted; chưa có model tự động thực hiện bước này.
3. Conflict handling: different/unknown giữ cả hai. Không lấy connected components để gộp bắc cầu: A cùng B, B cùng C chưa đủ tự gộp cả nhóm nếu A/C unknown hoặc different. Nhóm có quan hệ mâu thuẫn giữ nguyên chờ review.
4. Crop keeper: chỉ xét nhóm same đã xác minh; so crop gốc với source về đầu, tay/bàn nhìn thấy và nhiễu từ người khác. Chưa crop nào phù hợp hoặc không phân định được thì giữ observations gốc và đánh dấu unresolved, không ép chọn largest/highest confidence/highest behavior score. Chưa union box, đổi margins, mask/recrop hoặc lấy max score giữa hai crop.
5. Diagnostic output riêng: pair evidence, relation source (owner/model), quyết định đề xuất, keeper/reason, phần bị mất hoặc còn unknown và mapping tới originals. Không ghi đè detections/predictions/nhãn, không đếm suppression proposed thành thành công thực tế.

## Lựa chọn thiết kế được đề xuất

Bước gần nhất là chốt mục tiêu crop trên 4 cặp same bằng [gallery keeper](../../../outputs/runtime-d2-keeper-review-20261026/index.html). Đây là human-reviewed reference, không phải thuật toán runtime. Không cần model mới cho bước này.

Sau đó thiết kế một candidate verifier từ tín hiệu head/pose hoặc person-instance có localization tường minh. Cần chọn exact model/source/checkpoint/license, preprocessing, mapping nhiều đầu/người trong ROI, chi phí và ngưỡng abstain trước implementation/run. Không mặc định upper-third box là đầu, không mặc định cosine DINO/G0 là xác suất cùng người. DINO/G0 embedding similarity là hướng phụ cần đối chứng riêng nếu localization không khả thi, chưa được chọn hoặc chạy.

## Tiêu chí kiểm candidate đề xuất

- Báo riêng từng cặp trong 4 same và 4 different; không tự gộp thành accuracy toàn video.
- Mục tiêu: không đề xuất gộp 4 cặp different; giải quyết 4 same và crop keeper được owner chấp nhận. Nếu còn unknown, báo unresolved và chưa đạt đủ mục tiêu, không tính là đúng.
- Đối chiếu source → original boxes → keeper crop → classifier input để phát hiện mất đầu/tay/bàn hoặc đổi ownership. C01 là case bắt buộc về phone của hàng xóm; không tự đổi nhãn hành vi.
- Kiểm thêm người ngoài shortlist trên cohort trước kết luận không mất người. Không tinh chỉnh rồi gọi chính 8 cặp là test độc lập.
- Chỉ sau accepted candidate và crop QA mới thiết kế session tích hợp với ID/receipt mới, exact variables/pins và deadline hợp lệ.

## Quyết định còn thiếu và lifecycle

Cần owner review keeper C01/C02/P04/P06; quan hệ same không cần hỏi lại. Lựa chọn model/variables của verifier là bước thiết kế tiếp, không được suy approval từ approval thiết kế này. Không tải model, inference, train, sửa spec/runtime hoặc mở tracking/events. Gallery tái dùng links tới ảnh local đã pin, giữ deadline nguồn 01/11/2026 15:55 Việt Nam, không upload/copy media.
