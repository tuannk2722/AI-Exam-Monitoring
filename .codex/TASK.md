# LIVE-VIDEO-WEB-20261028 — Nối video online với giao diện local

- Trạng thái: kiểm lại cleanup và commit baseline web/video theo yêu cầu owner ngày 28/10/2026, sau đó mở task GPU/batching và profiling riêng.

## Yêu cầu và hiện trạng
- Runtime đã commit `6f4cbe3`. Staged checker PASS; clean checkout đúng commit: checker Git và 16 tests online PASS; checkout đã dọn. Không push.
- Đã đọc lại index/status/TASK, development, system, live design, scope/config web; kiểm code processor/runner, app/catalog/pipeline/store, assets và tests web hiện có. Các quyết định runtime/C10/events từ task trước vẫn giữ đúng scope.
- Web hiện chỉ đọc artifacts và chạy offline jobs. Bước này nối upload video đã có quyền → runner online → MJPEG/SSE → màn hình giám sát, điều khiển nguồn server và báo coverage/độ trễ.

## Quyết định và inputs
- Owner đã review giao diện và chốt thiết kế/logic hiện tại; tiếp tục yêu cầu cleanup, commit rồi triển khai GPU/batching và công cụ đo. Chốt baseline không phải nghiệm thu hiệu năng/chất lượng model hoặc approval numeric policy live còn mở.
- Thiết kế LIVE-DEMO-FOUNDATION-20261027 đã Accepted: monitoring chính, đúng frame/epoch, bounded buffers, MJPEG/SSE/POST, giữ review legacy.
- Không tự chọn numeric gap/jitter hoặc gắn C10/event acceptance cho stream bỏ mẫu. Chỉ hiện observations tức thời; temporal log và SQLite revision là slice tiếp theo sau policy cụ thể.
- Owner duyệt phương án LIVE-VIDEO-WEB-20261028 trong hội thoại: “Duyệt phương án này”. Được materialize API, config, upload limits 512 MiB/64 KiB, metadata riêng, MJPEG/SSE/POST và UI; giữ nguyên phạm vi chưa temporal events/review mới.
- Owner xác nhận máy mượn đáp ứng mức sàn, ưu tiên thiết kế ổn định và tương thích; không cần hỏi tiếp model iPhone. Chưa có evidence hardware để chốt GPU config/SLA; tiếp tục video CPU độc lập. Không tự mở camera, train, đổi model/thresholds hoặc inference người thật.

## Outputs và vòng đời
- Source/tests/assets web; config mới đúng ID; reference/status/spec chỉ cập nhật đúng impact. Không mutate config/runtime/receipt hoặc SQLite legacy đã có.
- Upload nếu triển khai lưu local theo receipt/deadline, tên opaque; không lấy filename người dùng làm path. Synthetic fixtures tự dọn; preview/tooling tạm chỉ dưới outputs/_scratch nếu cần.

## Contract impact và checks
- FR-VID-01, FR-UI-01, FR-LIVE-01/02; không tuyên bố FR-LOG-01 đã hoàn thành khi chỉ có observations.
- Kiểm quyền/hash/deadline/giới hạn upload, một runner, start/reconnect/stop/seek, bounded subscriber, epoch stale, lifecycle shutdown, legacy regression; browser synthetic light/dark khi có UI; Ruff/mypy/checker/diff.

## Checkpoint và bàn giao
- Commit đầu `6f4cbe3` đã xong và kiểm clean checkout; không push. Phần web tiếp theo hiện chưa stage/commit.
- Đã materialize config/API/metadata riêng theo approval. Monitor giữ một upload/runner và chặn inference đồng thời với offline jobs; streaming upload có size/hash/rights/deadline guards và cleanup partial. `verify_media_receipt` tách reusable validation khỏi hash file, giữ validator offline.
- UI `/` giám sát light/dark; `/review` giữ workflow cũ. MJPEG đúng frame, SSE full snapshot khi reconnect, pause/seek/stop theo server; command ID/epoch chống retry side effect. Browser cũng vô hiệu ảnh/observations khi deadline hết dù SSE đã kết thúc.
- Preview fan-out một JPEG mới nhất, kiểm lại epoch sau encode; không queue theo subscriber. Metadata vận hành chưa là artifact AI sealed; không lưu predictions/crops/evidence để review online. Không sửa SQLite legacy, model/pins hoặc rules C10/events.
- 54 regression tests runtime/online/streaming/legacy web/preview PASS; 12 API monitor tests PASS; 1 browser synthetic E2E PASS, gồm deadline sau terminal: tổng 67 tests. Ruff/checker cấu trúc/diff PASS; strict mypy 85 source files PASS trên bản cuối. CI classifier cài web extra đã có và chạy các suites web/preview; browser vẫn opt-in.
- Đã kiểm trực quan screenshots synthetic light/dark; sửa containment ảnh trong viewer. Đã kiểm exact paths, reparse/tracking guards và SHA rồi dọn hai screenshots cùng thư mục outputs/_scratch/live-video-web-20261028. Không media/model thật hoặc checkout còn lại; không tạo service server lâu dài.
- Kiểm cuối thấy cache Python/Ruff phát sinh trong workspace: đã inventory/hash và dọn 135 files / 1.941.085 bytes, chỉ trong __pycache__ của src/tests/scripts và .ruff_cache. Containment/reparse/tracked-file guards PASS; 20 files source/config/docs/tests của task giữ SHA trước/sau cleanup. Không đụng dataset/model hoặc .venv.
- Đã cập nhật system/registry theo contract mới được duyệt, reference/status/index theo capability. Chưa temporal tracking/events, stable log review, camera/GPU hoặc benchmark/chất lượng trên media thật.
- Kiểm trước commit baseline: full suite 349 tests PASS (2 skip), browser opt-in PASS riêng, Ruff/strict mypy 85 files và staged checker PASS. Browser test đã bỏ assertion tiêu đề bị owner ẩn; dọn HTML comment/CSS không còn dùng, giữ bố cục đã review.
- Cleanup lần này inventory 198 cache files / 49.495.030 bytes. Automatic approval review chặn lệnh xóa với lý do `blocked by policy`; chưa xóa. Manifest tạm ở thư mục TEMP hệ điều hành, tên `exam-monitor-cache-cleanup-20261028.json`; không chứa media/credentials. Không thử đường xóa khác để vượt policy. Cleanup source đã hoàn tất, không stage cache.
