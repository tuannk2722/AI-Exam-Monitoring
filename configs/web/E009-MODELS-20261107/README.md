# Model E009 trên màn hình giám sát

Theo [quyết định owner](../../runtime/RUNTIME-E009-20261107/decision.json), [monitor.yaml](monitor.yaml) dùng schema `online-video-web-config-v2`: allowlist B0/B448 và B0 mặc định. `configs/web/review.yaml` chọn config này cho `/`; config monitor v1 vẫn đọc được khi được chỉ định. Chi tiết model, pins và cách chạy ở [runtime E009](../../runtime/RUNTIME-E009-20261107/README.md).

`GET /api/monitor/state` trả thêm `models` và `default_model`. `POST /api/monitor/uploads` nhận `model_id` tùy chọn; bỏ qua dùng B0. Server chỉ nhận ID trong allowlist; path hoặc ID khác bị từ chối. Lựa chọn cố định khi tạo phiên. Không có API đổi model giữa upload/start/pause/seek hoặc khi phiên còn hoạt động; muốn đổi phải kết thúc phiên và tạo phiên mới.

`online-video-web-session-v2` giữ fields v1 và thêm `model_id`, `model_label`, `classifier` gồm run ID, checkpoint/calibration pins, target order, thresholds và preprocessing. Runtime/web config snapshot và code/environment vẫn được pin riêng; finish upload/start kiểm lại runtime và metadata. Restart xử lý phiên v1/v2 đang dở thành failed, giữ model provenance và deadline ban đầu. UI hiển thị model của phiên sau reload và khóa selector khi phiên đang hoạt động. Review offline, transport MJPEG/SSE, retention và semantics observations không đổi.
