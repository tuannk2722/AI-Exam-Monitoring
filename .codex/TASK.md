# LIVE-DEMO-APPROVAL-COMMIT-20261028 — Chốt approval, cleanup và commit

- Trạng thái: hoàn tất hồ sơ approval và checks; cleanup payload tạm bị policy chặn; đang commit theo yêu cầu owner.

## Yêu cầu và hiện trạng
- Đã đọc AGENTS, index/status, TASK trước, system/development/storage, live design và diff thực tế.
- Branch feat/live-monitoring-demo, parent 996c52c. Owner review/approve thiết kế rồi yêu cầu chốt approval, cleanup và commit; chưa có live runner/UI.
- Giữ thay đổi owner đang có: xóa docs/web-review.md và thay incoming links; không restore tài liệu đã xóa. Sửa dấu câu còn sót ở reference.

## Quyết định và inputs
- Approval ngày 28/10/2026 tại docs/live-monitoring.md và registry: thiết kế/bộ khung Accepted; không hỏi lại transport, bbox/log hoặc revision review đã duyệt.
- Máy/GPU/iPhone model, numeric jitter/gap/SLA và receipt camera chưa có giá trị cụ thể; approval không tự điền giá trị hoặc là live quality acceptance/run permission mới.
- Không train, model/camera inference, đổi pins hoặc push.

## Outputs và vòng đời
- Commit source/tests/docs/config metadata đúng scope. Không binaries/media/cache/DB vào Git.
- Đã inventory hai screenshots synthetic: synthetic-dark.png 106 788 bytes, synthetic-light.png 105 662 bytes; cache Python trong src/tests/scripts và Ruff/mypy là disposable.
- Lệnh cleanup có containment/reparse/tracked-file checks, hash manifest và protected metadata before/after đã bị automatic approval review từ chối trước thực thi với “blocked by policy”. Không bypass. Ảnh/cache ignored còn nguyên; manifest dự kiến không được tạo; dữ liệu/model/evidence không bị thay.
- Scratch clean checkout tại outputs/_scratch/live-demo-commit-check-20261028 chỉ để kiểm commit; dọn bằng git worktree remove sau kiểm. Không đụng các scratch/report lịch sử khác hoặc temp ngoài workspace.

## Contract impact và checks
- Không thêm contract; chốt approval thiết kế đã review. Schema/model/event rule lịch sử giữ nguyên.
- Ruff toàn src/tests/scripts PASS; strict mypy 80 source files PASS.
- Streaming 6, events 10, Web Review 5, repo checker 13 tests PASS (34 tổng); không chạy browser/model thật vì UI/AI production không đổi.
- Kiểm links tài liệu đã xóa, staged diff, checker --require-git trước commit; checker và streaming tests trên clean checkout sau commit.

## Checkpoint và bàn giao
- Đã hoàn thành phần source/docs được duyệt, chốt rõ inputs/numeric policy còn mở và Superseded recorded-only/review-first.
- Commit trên branch hiện tại; không push. Sau commit xác nhận Git sạch và chỉ còn một worktree. Cleanup ảnh/cache bị policy chặn là giới hạn riêng, không cản commit.
- Bước tiếp theo khi được yêu cầu: runtime xử lý từng frame và luồng video online, sau đó camera/GPU/log/UI theo thiết kế đã duyệt.
