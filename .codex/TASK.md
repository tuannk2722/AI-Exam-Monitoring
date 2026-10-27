# LIVE-VIDEO-RUNTIME-20261028 — Refactor runtime và runner video online

- Trạng thái: hoàn tất phần refactor và runner video online nội bộ; owner yêu cầu implementation ngày 28/10/2026, sau khi tự dọn ảnh/cache cũ. Chưa nối UI/log/camera/GPU.

## Yêu cầu và hiện trạng
- Đã đối chiếu AGENTS, index/status, system/development/reference, template, thiết kế live, registry và code/tests runtime/video/streaming/web pipeline. Git sạch tại 680dce2, branch feat/live-monitoring-demo.
- Runtime offline decode hai lượt và ghi QA; worker web chạy runtime rồi tracking/events. Tách frame processor dùng chung và runner file một lượt theo media clock, buffer giới hạn, pause/seek/stop, kết quả đúng epoch/frame.

## Quyết định và inputs
- LIVE-DEMO-FOUNDATION-20261027 Accepted thiết kế ngày 28/10; request hiện tại cho implementation runtime/video online.
- Đã đọc scope V8S/G0, session report 26/10, C10 closeout, events execution/acceptance và WEB-REVIEW-20261027. Giữ pins, CPU FP32/batch 1, context-v1, target order và thresholds; không rerun model để kiểm refactor.
- Sampling file dùng semantics first-at-or-after hiện có, giữ timestamp gốc. Không tự làm tròn để qua event validator. Online tracking/events cần numeric jitter/gap policy riêng; đợt core này chỉ observations tức thời, chưa C10/log temporal, camera/GPU/UI/transport hoặc schema SQLite.
- Đường production phải kiểm config/pins/receipt/source SHA/deadline; fixtures synthetic là tests riêng, không fallback giả.

## Outputs và vòng đời
- Source/tests trong inference; reference/status cập nhật capability thực tế. Không sửa sealed artifacts/configs/receipts hoặc spec khi contract không đổi.
- Owner yêu cầu commit phần hoàn tất rồi tiếp tục tích hợp ngày 28/10/2026. Stage đúng source/tests/docs/CI; không media/model, train/test holdout, upload hoặc push. Synthetic tests dùng thư mục tạm tự dọn; tránh tạo bytecode/cache trong workspace khi kiểm.

## Contract impact và checks
- Không đổi schema offline hoặc persistence/wire schema. API nội bộ giữ source identity, bounded buffers và lifecycle theo thiết kế đã duyệt.
- Kiểm parity frame/geometry/flags/QA, lỗi decode/inference, EOF/stop/pause/seek, backpressure và late result; regression runtime/streaming/tracking/events/web; Ruff và strict mypy. Software PASS không là quality/SLA acceptance.

## Checkpoint và bàn giao
- `frame_processor.py`: detector/classifier protocols, snapshot anchors và xử lý frame dùng chung; `runtime.py` tái dùng processor, giữ writer/QA/outcome. `video.py`: sampler tăng dần giữ PTS/semantics cũ.
- `online_video.py`: factory kiểm config/pins/rights/deadline/SHA; một decoder và một worker model, pending/result giới hạn, media clock, pause/resume, seek theo exact frame index với epoch mới, EOF drain và stop cooperative. Seek decode lại từ đầu để giữ exact index/PTS; chưa tối ưu keyframe seek. Model/native read phải trả về trước khi `join` xác nhận giải phóng.
- Clock runner dùng `perf_counter_ns` monotonic độ phân giải cao, tránh timestamp trùng của `monotonic_ns` trên Windows/Python 3.11. Consumer dùng cùng clock để tính tuổi ảnh, kiểm epoch trước hiển thị; không ghép bbox lên preview khác.
- Tests online 16, runtime 22, streaming/tracking/events/web review/repo checker 56: tổng 94 PASS. Có MP4 synthetic decode thật với model fixtures riêng, parity observations/geometry/flags, overload, kết quả trước EOF, pause/seek/stop, startup/inference/decode failures và expiry. Không gọi model/media thật.
- Ruff toàn src/tests/scripts PASS; strict mypy 82 source files PASS; checker cấu trúc PASS; diff whitespace PASS. `--require-git` báo đúng 3 files source/tests mới chưa trong index; không stage để vượt gate. CI classifier đã thêm suite online; mô phỏng thiếu Torch xác nhận skip 16 tests, không lỗi import ở base job.
- Đã cập nhật reference/status/index theo capability thực tế, không sửa system/live spec hoặc pins. Đang chốt commit theo yêu cầu mới; kiểm staged diff và checker Git trước commit, clean checkout sau commit. Tests dùng thư mục tạm tự dọn, không tạo preview trong workspace.
- Phần tiếp theo: adapter upload/UI/transport và persistence log theo thiết kế đã duyệt; tracking/events online cần numeric gap/jitter policy trước khi nối. Camera cần thiết bị/receipt; GPU cần adapter/config và parity/profile riêng. Chưa benchmark hoặc nghiệm thu chất lượng/hiệu năng online.
