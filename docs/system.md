# Đặc tả hệ thống AI Exam Monitoring

Quy định phạm vi, kiến trúc, contracts và acceptance. Không lưu tiến độ, metrics runs hoặc backlog. Owner: chủ repository. Đọc [status](status.md) để biết implementation đã đạt tới đâu; [index](00-INDEX.md) định tuyến hồ sơ liên quan.

## 1. Phạm vi và mục tiêu

Sản phẩm là nghiên cứu/demo phát hiện **hành vi quan sát được** trong video phòng thi. Đích demo là một camera trực tiếp (có thể từ điện thoại) hoặc video upload đang phát, có bbox/nhãn hành vi trên hình và log bằng chứng bên cạnh. Review là thao tác nhanh trên log. Quy mô tham chiếu khoảng 10–15 người nhìn thấy; năng lực thực tế phải đo. Không kết luận gian lận, định danh sinh viên hoặc tự động kỷ luật. Nhiều camera, cloud production, xác thực phức tạp và temporal neural model ngoài phạm vi hiện tại.

Yêu cầu owner `LIVE-DEMO-FOUNDATION-20261027` supersede riêng recorded-only/review-first, không hồi tố acceptance offline. [Thiết kế live](live-monitoring.md) đã được owner duyệt ở cấp thiết kế/bộ khung ngày 28/10/2026; inputs/numeric policy chưa xác định được ghi riêng. Spec là đích cần xây, không tuyên bố đã có live runtime.

Hai hành vi đã chốt: `phone_use` và `looking_around`. Kiến trúc B đã được owner chọn; không mở lại A/B vì thiếu model đủ tốt. Classifier trên reviewed crops và automatic crop/video là các phạm vi nghiệm thu riêng.

## 2. Kiến trúc và trách nhiệm

Luồng đích:

```text
Camera hoặc video upload được phép sử dụng
  → frame + source time + session/epoch identity
  → detector person
  → crop context đúng người
  → classifier [phone_use, looking_around]
  → track tạm thời trong session
  → temporal events
  → bbox/nhãn đúng frame + evidence + log phiên cập nhật
  → người xem mở bằng chứng và quyết định nhanh
```

Core không import FastAPI/UI/database. Notebook chỉ exploration/launcher; logic tái dùng ở `src`. Không tạo module rỗng, metric giả hoặc kiến trúc dịch vụ phân tán để chuẩn bị cho phần chưa đến gate.

Risk là nhánh mở sau, không là điều kiện để hiển thị monitoring/log. Preview,
AI và bằng chứng phân biệt tốc độ và độ trễ; không ghép bbox cũ lên frame mới.

## 3. Yêu cầu và bằng chứng nghiệm thu

Các dòng dưới đây là yêu cầu/tiêu chí; có ID không có nghĩa đã triển khai hoặc PASS. Trạng thái triển khai ở [status](status.md); giới hạn code ở [reference](reference.md). Khi nghiệm thu, gắn requirement ID với test/report/protocol và version cụ thể; software fixtures không thay đánh giá dữ liệu/model/video.

| ID | Requirement | Bằng chứng / điều kiện nghiệm thu |
|---|---|---|
| FR-DATA-01 | Dataset version rõ, có schema/ledger/manifest/rights/assignment/freeze/checksum và owner approval | Schema/inventory/pins/QA và receipt release; mutation tạo release mới |
| FR-CLS-01 | Hai target độc lập, unknown masked; normal là metadata review | Codec/loss/metric tests bảo vệ target order/masks; không output normal hoặc softmax |
| FR-EXP-01 | Run có hypothesis, config/code/data/environment pins, status, checkpoints, metrics và decision | Run artifacts và resume checks cùng identity; OOM/interruption không tự đổi config |
| FR-EVAL-01 | Model/epoch/threshold chọn bằng development; test chỉ mở theo protocol freeze riêng | Protocol/approval/pins và access evidence; guard holdout xuyên output theo protocol được duyệt |
| FR-VID-01 | Recorded video có source checksum, frame index, video time và prediction có provenance | Integration kiểm source → frame/time → prediction và session outcome |
| FR-CROP-01 | Person/context crop giữ đúng bằng chứng thuộc anchor, preprocessing khớp training | Detector/license/runtime policy được duyệt và source → crop → input QA |
| FR-TRK-01 | Track ID tạm thời trong một session; có đo switch/fragmentation/loss/occlusion | Benchmark ByteTrack đề xuất với phương án khả thi khác hoặc no-tracking baseline |
| FR-EVT-01 | Nhiều observation theo temporal rule có version mới tạo event | Fixtures/event validation với duration/gap/aggregation được duyệt |
| FR-RSK-01 | Proposed: risk giải thích được từ event history, bounded/decaying, tách model confidence | Chốt semantics/công thức/threshold/reset; chưa là numerical contract Accepted |
| FR-EVD-01 | Evidence trỏ exact source frame/time/checksum và model/rule/event versions | Kiểm truy vết evidence; retention/access/deletion phải chốt trước media người thật |
| FR-REV-01 | Người xem lại video/evidence, ghi chú, bác false positive hoặc xác nhận hành vi | Kiểm luồng review local với evidence thật và ghi nhận quyết định người xem; không tự kết luận kỷ luật |
| FR-UI-01 | Camera hoặc upload → bắt đầu → video/detection trong phiên → log/bằng chứng → quyết định nhanh; light/dark | End-to-end theo §5; không đợi AI xử lý toàn file; stack ở [decision registry](decisions.md) |
| FR-LIVE-01 | Bbox/nhãn đúng session/epoch/frame/geometry; hiển thị độ trễ và trạng thái AI | Kiểm late results/đổi nguồn và capture-to-result trên máy demo |
| FR-LIVE-02 | Buffer giới hạn; dropped/missing frames được ghi nhận, không giả đủ cadence/temporal support | Overload/disconnect/seek/stop không tăng queue vô hạn hoặc nối sai event; policy online riêng |
| FR-LOG-01 | Log trong phiên, click evidence, xác nhận/bỏ qua/chưa rõ; quyết định lưu riêng | Không spam mỗi frame; review gắn bằng chứng đã xem; reconnect không mất quyết định |

Khi task liên quan requirement đã có, sửa producer/consumer và kiểm regression của đường đó. Khi liên quan requirement chưa có, ghi rõ gate còn thiếu trước implementation; agent vẫn được làm proposal hoặc phần độc lập được user yêu cầu, không tự suy quyền train/thu thập/upload.

## 4. Contract giữa các bước

Contract liên bước dưới đây tương ứng `contracts/domain.py`; đây không phải schema DB. Thay contract phải xét producer/consumer và version. Chi tiết adapter/giới hạn implementation ở [reference](reference.md).

| Entity | Fields và invariants |
|---|---|
| `BoundingBox` | `xmin,ymin,xmax,ymax,coordinate_space`; tọa độ hữu hạn, min < max; pixel không âm, normalized trong [0,1] |
| `FrameRef` | `session_id,frame_index,video_time_ms,source_uri`; index/time không âm; thời gian video khác thời gian xử lý/DB |
| `Prediction` | `prediction_id,frame,model_version,task,label,confidence,bbox,class_id?`; confidence trong [0,1], label mô tả quan sát; không dùng cheating/cheater/no_cheating/suspicious_person |
| `TrackObservation` | `session_id,track_id,frame,bbox,source_prediction_ids`; track ID không là danh tính ngoài session |
| `BehaviorEvent` | Event/session/track/behavior, frame/time window, aggregated confidence, model/rule versions, prediction refs; end không trước start; status hiện `candidate/confirmed/dismissed` |

Slice prototype dùng contract `recorded-observations-v1` theo [thiết kế runtime được duyệt](../configs/runtime/RUNTIME-PROTOTYPE-20261025/README.md): metadata pins source/model/config/code/environment; mỗi frame có index/time, geometry và danh sách observation (có thể rỗng), mỗi anchor có hai score theo target order, ngưỡng và cờ vượt ngưỡng. Anchor ID chỉ trong frame, không là track hay danh tính. `session.json` có trạng thái cuối completed/failed; `frames_processed` chưa xác nhận session thành công. Không sửa dataclass `Prediction` để chứa payload riêng này.

Các entity tương lai như model registry và risk snapshot chỉ định fields/persistence
khi thực hiện slice tương ứng; không thêm database schema hoặc service phụ trước scope.

Online frame identity/live log là slice mới: epoch phân biệt reconnect/seek;
source time khác clock xử lý. `FrameRef` và schema sealed giữ nguyên cho offline.
[Thiết kế live](live-monitoring.md) đề xuất timing, buffer, snapshot/revision và
seal cuối phiên. [LIVE-VIDEO-WEB-20261028](../configs/web/LIVE-VIDEO-WEB-20261028/README.md)
đã được owner duyệt riêng cho API upload/điều khiển/MJPEG/SSE và metadata
`online-video-web-session-v1`: một phiên local, receipt/hash/deadline bắt buộc,
snapshot trạng thái đầy đủ khi reconnect, command ID/epoch chống thực thi lặp.
Lựa chọn [model E009 cho prototype](../configs/runtime/RUNTIME-E009-20261107/README.md) bổ sung web config/session v2: B0 mặc định hoặc B448, một model chạy cả hai nhãn, khóa theo phiên và lưu checkpoint/calibration/preprocessing provenance. API/state và tương thích v1 ở [web selector](../configs/web/E009-MODELS-20261107/README.md). Không chuyển nghiệm thu G0/tracking/events sang các model này.

Giới hạn và config ở hồ sơ này. Metadata vận hành riêng không phải session AI
đã seal hoặc event evidence; observations tức thời không được ghi thành quyết
định review. SQLite live log/revision vẫn cần slice riêng, không sửa schema review
legacy. Numeric policy đã được duyệt tại
[LIVE-TIMING-20261028](../configs/tracking/LIVE-TIMING-20261028/README.md): detector
10 Hz, tolerance 50 ms sau mốc; thiếu slot detector reset continuity, thiếu G0 ngắt
segment; G0 mỗi 10 slot và
candidate giữ ≥ 3 positives liên tiếp/span thật ≥ 2 giây. Chưa bật log online hoặc
nghiệm thu chất lượng/cadence thực từ approval implementation này.

Slice web local theo [WEB-REVIEW-20261027](../configs/web/README.md) lưu review riêng
bằng `event-human-review-v1`, gắn `events_sha256` và event ID. Quyết định gồm
candidate/confirmed/dismissed/uncertain, lý do, ghi chú và cờ đánh dấu; revision
kiểm xung đột ghi. `uncertain` không sửa contract BehaviorEvent phía trên.
Disposition cấp phiên không xác nhận từng event. SQLite/JSON review không mutate
artifacts AI; persistence review theo [scope web](../configs/web/README.md).

Slice events theo [rule prototype được duyệt](../configs/events/EVENTS-PROTOTYPE-20261027/execution.md) join observations G0 1 Hz với C10 theo exact frame/time/anchor/box. `temporal-event-candidates-v1` bọc `BehaviorEvent` với support refs namespaced theo parent session, source/model/tracker/rule pins, scores/count và observed span. Chỉ xuất candidate; không bridge missing/unknown/negative/null hoặc nối khác ID. Mean score không là xác suất event đã calibrated; span là last minus first observation, không nội suy duration liên tục. Session completed/failed tách quality acceptance; risk/web vẫn có gate riêng.

Slice tracking theo [thiết kế được duyệt](../configs/tracking/TRACKING-PROTOTYPE-20261026/execution.md) xuất `track-assignments-v1` riêng: arm ID, parent session SHA, frame index/time và đúng một assignment cho mỗi anchor gốc. Assignment giữ person box gốc, track ID hoặc null và reason; box tracker nếu có là field riêng. Track ID chỉ có nghĩa trong arm/session; không gộp hoặc tạo behavior predictions cho frame thiếu observation. `tracking-session-v1` và benchmark outcome phân biệt completed/failed với quality acceptance. Không thay dataclass `TrackObservation` hoặc output runtime cũ; event contract thuộc slice riêng ở trên, risk chưa mở.

## 5. Yêu cầu vận hành và luồng người dùng

Slice offline đầu giữ workflow đọc/xử lý artifacts. Đích mới: chọn camera hoặc upload video có quyền → kiểm input/kết nối → bắt đầu → video/detection/log cập nhật → mở evidence và review nhanh → dừng hoặc EOF. Video chiếm phần chính, log cạnh bên và drawer bằng chứng; diagnostics/export mở khi cần. Không bắt buộc đi qua hub/workbench/summary. Server validate input; limit cụ thể chốt theo cấu hình demo.

Video upload phát theo media clock và phân tích khi phát; pause/seek đồng bộ với backend. Camera cần xử lý mất nguồn và stop giải phóng capture. Missing/gap không tạo prediction giả hoặc nối event. Khi AI không theo kịp, báo xử lý chậm và coverage thực; không dùng FPS preview làm FPS AI. Transport, nhãn tức thời so với temporal log và hướng persistence live đã được duyệt ở cấp [thiết kế](live-monitoring.md); numeric jitter/gap/reset theo LIVE-TIMING-20261028 ở trên. Cấu hình máy và receipt camera còn cần cụ thể hóa trước thực thi tương ứng.

Nghiệm thu end-to-end phải dùng video được phép, model đã chọn, crop policy/rule versions và kết quả thật. Đo trên hardware/OS/dependencies đã pin: resolution/FPS/duration, startup/warm-up/repeats, throughput, mean/p50/p95 latency, peak RAM/VRAM, tracking loss/switch và false/missed events. **Chưa có SLA FPS/latency toàn video hoặc quality threshold hệ thống Accepted.** Các chỉ tiêu classifier theo experiment protocol không tự chuyển thành SLA video.

Ngân sách hiện có 0 đồng. Local cho development/audit/inference; Colab Free là hướng GPU nghiên cứu đã chốt. Phần cứng demo live chưa được owner chọn; GPU local là đề xuất, không là quyền mua/thuê hoặc cam kết hiệu năng. Mỗi benchmark/run phải pin hardware/environment; ngoại lệ compute lịch sử không cấp quyền run mới. Yêu cầu live đã mở scope thiết kế, không tự mở cloud/thu nhận media hoặc đổi model.

Media người thật cần policy văn bản cho consent, access, third-party processing, retention/deletion và incident handling trước thu nhận/ghi/upload. Policy prototype local đã được duyệt trong thiết kế runtime (owner-only, không upload, tối đa 7 ngày; rights theo từng clip vẫn bắt buộc); retention cho scope khác chưa chốt; [retention workspace nghiên cứu](storage.md) không thay policy này hoặc cấp quyền thu nhận/upload media. Không real identity trong tên file/manifest, không credential trong Git/TASK/log; không upload media vào API/W&B khi thiếu quyền. Nguồn đã có approval giữ đúng scope, không hỏi lại phần không đổi.

## 6. Điều kiện chuyển bước

Thứ tự phụ thuộc: dataset/annotation QA → baseline/evaluation → dữ liệu đánh giá độc lập/cải tiến model → runtime crop/video → tracking/events → web. Bảng này giữ điều kiện chuyển bước; [status](status.md) dẫn tới công việc/proposal đang hoạt động.

| Hành động | Điều kiện áp dụng |
|---|---|
| Nghiên cứu/proposal và phần độc lập | Đúng user scope; dùng evidence đã có, không tự mở train/test/upload hoặc quyết định scientific còn thiếu |
| Đóng release | Membership/rights/groups/splits/QA/approval theo data §4; release không tự cấp quyền chạy experiment |
| Implementation, smoke và run model | Theo các quyền riêng ở training §3; design được duyệt trước implementation liên quan, smoke là kiểm chứng thực thi sau đó |
| Final evaluation và Selected | Protocol/access/quality gates theo training spec; FINISHED hoặc unit PASS không thay acceptance |
| Runtime crop/video | Detector/license/crop policy được chốt; QA source → crop → input và integration có provenance |
| Tracking/events/risk | Model Selected phát prediction thật; benchmark tracker, event fixtures/rules và risk semantics được duyệt trước slice tương ứng |
| Web/system evaluation/demo | Domain/event gate, UI đọc output thật; offline và live/file-stream integration theo slice. Live cần source/device/gap/evidence policy riêng; đo hardware và báo giới hạn theo §5 |

Ngoại lệ prototype theo [E008-PROTOTYPE-20261025](../artifacts/reports/e008-v14-colab-20261024/prototype-decision-20261025.md): owner đã bỏ 80/80/20 khỏi điều kiện chuyển phase và chọn checkpoint G0 cho tích hợp thử nghiệm. Model được chọn đúng use scope prototype có thể thay điều kiện Selected nghiên cứu trong lộ trình downstream; detector/license/crop QA, tracker/rules/risk, media rights và nghiệm thu video vẫn phải được duyệt theo slice. Không biến quality gate lịch sử thành PASS hoặc tự cấp nghiệm thu demo.

Gate chặn hành động thuộc scope của nó. Proposal hoặc phần độc lập được user yêu cầu vẫn có thể tiến hành; không suy thành quyền mở downstream ngoài scope đã duyệt hoặc nghiệm thu demo từ approval prototype. Checklist scientific còn mở thuộc proposal được dẫn từ status; owner chốt phương án có evidence/acceptance, không phải tự annotate từng ảnh.
