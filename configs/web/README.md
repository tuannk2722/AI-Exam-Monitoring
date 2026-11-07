# WEB-REVIEW-20261027 — Phạm vi UI local

Màn hình giám sát `/` hiện dùng [B0 mặc định/B448 tùy chọn](E009-MODELS-20261107/README.md) theo quyết định owner ngày 07/11/2026. Phạm vi bên dưới giữ pipeline review offline lịch sử tại `/review`.

Owner yêu cầu triển khai UI end-to-end ngày 27/10/2026 theo bản phác thảo
`AI-Exam-Monitoring-Web-Review-UI-Plan.md`, bổ sung light/dark và ưu tiên workflow AI.
Trong hội thoại cùng task, owner chọn **SQLite local riêng** và trả lời
**“Duyệt, giữ nguyên pipeline (đề xuất)”** cho video mới có receipt riêng.

## Phạm vi được duyệt

- FastAPI/Jinja2/JavaScript/SQLite theo ADR-007, chạy loopback trên máy owner.
- Đọc artifacts thật; lưu review riêng với candidate/confirmed/dismissed/uncertain,
  lý do, ghi chú, cờ đánh dấu, tổng kết và nhập/xuất JSON.
- Video mới dùng nguyên V8S → context-v1 → G0 1 Hz, C10 10 Hz và event rule
  3 mẫu dương liên tiếp/span ≥ 2 giây. Mỗi clip có receipt quyền media riêng;
  output mới, không tự confirmed hoặc nghiệm thu chất lượng.
- Giữ model, thresholds, tracking variables và semantics đã chốt. Risk chưa mở.
  Không train/test holdout, cloud upload, auth phức tạp hoặc SLA mới.

## Cấu hình và identity

[review.yaml](review.yaml) trỏ runtime/tracker/rule hiện hành. Job mới ghi SHA
các config, code identity, environment, source SHA và deadline trước thực thi.
Rule lịch sử được **tái dùng semantics** theo approval web này; `rule_id` vẫn là
version rule, không là identity job mới. Deadline mỗi phiên lấy từ receipt clip,
không lấy deadline hoặc quyền chạy một lần của campaign lịch sử.

Approval web hiện tại không sửa hoặc ghi đè bất cứ receipt/config đã pin có
`web: false`. Các trường đó vẫn mô tả scope của lượt chạy lịch sử. Không gọi lại
entry point replay một lần của campaign; adapter web tái dùng `run_video`,
`tracker_factory`, `assignments`, `aggregate` với identity/output mới.

C10 hiện yêu cầu FPS nguyên chia hết cho 10 để giữ nhịp sampling đúng. Clip khác
định dạng này báo lỗi; không tự resample hoặc đổi rule.
