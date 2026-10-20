# Quyết định owner cho V12

Ngày ghi nhận: 20/10/2026. Đây là bản ghi yêu cầu trong hội thoại, không phải approval do agent suy từ kết quả kiểm tra.

- Owner đã review `crop-review-consolidation-20261019/README.md`; “những crop không được nhắc đến thì mặc định approve”.
- Owner yêu cầu chốt toàn bộ thay đổi, rà lại chuỗi audit và đóng gói/release version mới, có thể kế thừa config V11 và điều chỉnh phù hợp.
- Review 15 dòng được bảo toàn tại `owner-final-review.md`; nhãn theo thứ tự phone / looking.
- Owner trả lời “Chỉ giữ V6-EX-027” cho xung đột gần trùng EX022/EX027. Giữ EX027 N/P, loại EX022 và EX010-R06 theo quyết định mới.
- Owner trả lời “Duyệt phương án này” cho bảng phân bổ cụ thể: **1.092 train / 204 validation / 11 test giữ nguyên**, 90 crop YouTube vào train; không chia frame cùng video qua validation; Y03/Y05 gom nhóm bảo thủ.

Scope: release dataset local cho classifier research. Không train, smoke, test inference, upload hoặc commit. Test chỉ được hash/decode/copy cho kiểm toàn vẹn và bảo toàn nội dung, không visual review hoặc prediction.

Parent V11, config/receipt và kết quả E005 giữ nguyên. Validation vẫn là development validation và có lịch sử model exposure; nhãn/membership V12 thay đổi nên metrics V11 không tự chuyển sang V12.
