# WEB-REVIEW-20261027 — Giao diện human review local

- Trạng thái: hoàn thành implementation và kiểm chứng phần mềm; cleanup file tạm bị policy chặn. Owner yêu cầu end-to-end theo UI Plan, thêm light/dark; ưu tiên AI.

## Yêu cầu và hiện trạng
- Đã đọc index/status/system/development/decisions/reference, UI Plan và code runtime/tracking/events/gallery. Git sạch trước task. Chưa có web; stack ADR-007: FastAPI/Jinja2/JS/SQLite.
- Ba màn hình: quản lý phiên, bàn duyệt, tổng kết. Batch acceptance không xác nhận từng event. Risk hiển thị chưa mở.

## Quyết định và inputs
- User hiện tại mở implementation web local. Không sửa approvals/config/artifacts đã pin có web=false (phạm vi lịch sử).
- Inputs: outputs/events-prototype-20261027, runtime-v8s-session-20261026-r2, tracking-cadence-20261027/C10 qua provenance pins; giữ retention gốc.
- Owner chọn SQLite local riêng và duyệt giữ nguyên pipeline cho clip mới có receipt riêng. Scope ở configs/web/README.md; không hỏi lại.
- Không train, đổi threshold/model, upload hoặc tự nghiệm thu chất lượng.

## Outputs và vòng đời
- Source src/ai_exam_monitoring/web, config riêng, hướng dẫn docs. Review mới dưới outputs/web-review, không sửa artifacts AI.
- Scratch outputs/_scratch/web-review-20261027; dọn sau kiểm. Không media/DB vào Git.

## Contract impact và checks
- Giữ contracts AI; uncertain thuộc review riêng, không đổi BehaviorEvent đã seal. Bổ sung slice event-human-review-v1 theo persistence được owner duyệt vào system; fields/cách dùng tại docs/web-review.md.
- Kiểm API/provenance/media/review/nhập/xuất, Ruff/mypy và browser light/dark; không chạy lại model chỉ để kiểm UI.

## Checkpoint và bàn giao
- Đã triển khai FastAPI/Jinja2/JS: ba views, light/dark, filters/candidates/short/tracks, overlay/focus/zoom, nhịp 1 Hz/10 Hz, timeline/filmstrip/crop/input, SQLite revision, review/import/export và tổng kết. Worker mới tái dùng runtime/tracker/aggregate, không gọi lại campaign replay.
- Đã kiểm 5 tests API/persistence/pipeline synthetic, browser synthetic và browser chỉ đọc phiên thật: 55 events, 20 phone, 169 chuỗi ngắn, 1.162 observations; không ghi quyết định vào dữ liệu thật (SQLite thật 0 rows). Ruff toàn repo PASS, mypy 79 files PASS, JS syntax/compile/diff PASS. Full suite 309 tests OK, 1 skip browser tùy chọn; nhóm web 6 tests gồm browser chạy riêng PASS. Browser kiểm light/dark, desktop/mobile, phím tắt, step frame, lưu/nhập/xuất/reload.
- Owner đã yêu cầu cleanup và commit snapshot Web Review trước khi tạo branch riêng cho demo live. Stage đúng source/docs/config/tests; kiểm index và diff trước commit, không push.
- Không chạy inference thật mới hoặc tự nghiệm thu chất lượng model/video. Đã kiểm lại pins phiên gốc. Server preview đã dừng bằng Ctrl+C của exec session.
- Automatic approval review chặn nguyên lệnh cleanup trước thực thi với “blocked by policy”; không bypass xóa file. Còn hai screenshots synthetic ở outputs/_scratch/web-review-20261027, web __pycache__, test_web pyc và thư mục test lỗi C:/Users/OS/AppData/Local/Temp/tmp2echhxln. Không có media thật trong screenshots test. Dữ liệu/model/evidence gốc giữ nguyên.
- Cleanup theo yêu cầu mới vẫn bị automatic approval review chặn trước thực thi, lý do “blocked by policy”. Không bypass; file tạm ignored không vào commit. Phần source và kiểm Git tiếp tục độc lập.
- Bàn giao: docs/web-review.md; chạy .venv/Scripts/python.exe -m ai_exam_monitoring.web, mở http://127.0.0.1:8765. Snapshot này được commit trước khi mở hướng live; không push.
