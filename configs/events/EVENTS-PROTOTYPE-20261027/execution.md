# Thực thi events đã được duyệt

Owner đã review và approve toàn bộ README proposal: rules, implementation/synthetic tests và một cached replay. [Authorization](owner-authorization.json) pin snapshot proposal, [rule thực thi](approved-rule.yaml), C10 acceptance/session/assignments/projection và parent authorization. README/rule draft giữ nguyên làm snapshot được duyệt; trạng thái hiệu lực nằm trong receipt này, không yêu cầu duyệt lại.

CLI: `python -m ai_exam_monitoring.inference.events --authorization configs/events/EVENTS-PROTOTYPE-20261027/owner-authorization.json --output outputs/events-prototype-20261027`.

Output phải đúng path được pin, chưa tồn tại; không chạy lại vào path mới để vượt ngân sách một replay. Nếu thất bại, giữ failed outcome và lập quyền retry riêng. Cached input được kiểm trước/sau, không load model hoặc decode media. Không mở risk/web hoặc nghiệm thu chất lượng events từ software PASS.

[Kết quả và kiểm tra](../../../artifacts/reports/events-prototype-20261027/README.md). Mọi artifact tiếp tục giữ deadline media cũ, không upload/gia hạn.
