# EVENTS-PROTOTYPE-20261027 — Đề xuất temporal event candidates

Trạng thái: **Draft, chờ duyệt rule mới trước implementation**. Tracking C10 đã được [owner chốt](../../../artifacts/reports/tracking-cadence-20261027/closeout-20261027.md), bỏ audit toàn clip. Không yêu cầu duyệt lại tracker. Proposal là bước tiếp theo theo FR-EVT-01 và system §6; không mở risk/web.

## Phương án đề xuất

Tạo CLI offline đọc predictions V8S/G0 và projection C10 tại cùng 60 mốc 1 Hz; join exact frame/time/anchor/person box, kiểm source/parent/config hashes và completed outcome. Không gọi detector/classifier, không tạo scores tại frame tracking 10 Hz. Dùng ngưỡng G0 đã pin và đúng target order, không tuning lại từ clip này.

Với mỗi `(session, arm C10, track_id, behavior)`, tạo **candidate** khi có ít nhất **3 observations vượt ngưỡng liên tiếp ở 1 Hz**, khoảng cách đúng **1.000 ms**, thời gian từ observation đầu đến cuối ít nhất **2.000 ms**. Dùng cùng rule khởi đầu cho phone_use và looking_around; đây là heuristic prototype cần duyệt, không threshold chất lượng đã được chứng minh.

- Observation không vượt ngưỡng, thiếu/unknown, null track hoặc mất mốc 1 Hz sẽ cắt chuỗi. Không bridge gap, không merge qua ID khác. Không bỏ qua observations âm để nối hai đoạn dương.
- Candidate kéo dài đến observation dương liên tiếp cuối; EOF flush chuỗi đủ điều kiện. Chuỗi ngắn được accounting nhưng không thành event.
- `aggregated_confidence` là trung bình cộng scores hỗ trợ, không xác suất calibrated của event. Giữ min/max/count để review.
- `observed_span_ms = end - start`, không cộng thêm một giây và không khẳng định hành vi liên tục giữa frames.
- Hai hành vi độc lập. Không cộng duration/count giữa tracks để suy số người hoặc risk. Duplicate có thể tạo candidate trùng; giữ limitation, không tự suppress theo IoU/role.
- Mọi event là `candidate`; confirmed/dismissed chỉ từ human review sau này. Không kết luận gian lận.

Rule này loại spike đơn lẻ, không nối hành vi qua khoảng thiếu evidence/đứt ID. Đổi lại có thể bỏ lỡ hành vi ngắn và chia nhỏ đoạn khi score dao động. Bản đầu ưu tiên truy vết; không coi rule sửa lỗi tracking.

## Contract và deliverables sau duyệt

Tái dùng `BehaviorEvent` cho core, không sửa dataclass nếu adapter đáp ứng được. Wrapper `temporal-event-candidates-v1` giữ source/runtime/model/tracker/rule pins, exact anchor references, scores, span/count và limitations. `source_prediction_ids` dùng namespace parent session + anchor; không giả đã có Prediction object upstream.

Outputs riêng: session completed/failed, config/code/environment/input pins, events JSONL, accounting null/chuỗi ngắn và checksums. Evidence chỉ references exact source/frame/anchor đã có, không export thêm media. Core trong src, YAML chứa variables, CLI không import web. Không sửa predictions/assignments cũ.

## Phạm vi đề nghị duyệt

1. [Rule](rule.yaml): 3 observations liên tiếp, spacing 1 giây, span tối thiểu 2 giây, không bridge gap, mean score, candidate-only.
2. Implementation và synthetic fixtures: boundary 2/3 observations, negative/unknown/missing/null/ID change, hai labels, EOF, duplicate/irregular samples, exact join/input mutation, outcome/expiry.
3. Một lượt replay cached trên clip đã duyệt, không model inference mới; kiểm accounting/provenance, báo candidate counts như diagnostic, không acceptance event quality hoặc audit lại tracking toàn clip.

Trước run freeze config và pins; giữ local owner-only/deadline cũ, không upload/gia hạn. Sau replay bàn giao candidates và giới hạn; quality acceptance event riêng. Không cấp quyền risk/web hoặc threshold sweep.
