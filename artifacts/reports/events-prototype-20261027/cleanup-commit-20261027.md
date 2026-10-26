# Cleanup và tách commit tracking/events

Owner đã chấp nhận kết quả candidates và yêu cầu cleanup kỹ, hai commit riêng. Nghiệm thu được ghi trong receipt companion, không mutate session/candidates hoặc diễn giải thành confirmed từng dòng.

Đã rà source/docs/config/reports, bỏ dòng trống thừa ở source tracking mới, cập nhật trạng thái events đã accepted và bỏ câu trạng thái cũ “events ở bước thiết kế”. TASK được thay bằng đúng task cleanup/commit. Bảo toàn bytes template gallery và config/report đã pin qua Git attributes; không chỉnh pins để khớp normalization.

Commit tracking giữ implementation/tests/templates, N0/B0/B1/C5/C10 và research/closeout; hai files draft proposal events đi cùng handoff vì closeout đã tham chiếu. Commit events giữ implementation/tests, approved rules/authorization, replay evidence và owner acceptance. Media/model/cache không đưa vào Git; không push.

## Kiểm tra

- Full suite: **303 tests PASS**, 210,760 giây. Ruff toàn src/tests/scripts PASS; strict mypy 73 files PASS.
- Tracking staged snapshot trong checkout riêng không chứa local data/model: checker `--require-git` PASS và 22 tracking tests PASS. Các metadata/config đã pin được kiểm byte-for-byte trong index.
- Event staged snapshot riêng: checker `--require-git` và 10 event tests PASS; checker workspace/index đầy đủ PASS. Kiểm 32 pin edges trong index khớp SHA. Hai checkout tạm đã gỡ bằng Git worktree, helper/manifest tạm đã dọn sau kiểm; không còn payload scratch của task.
- 52 exact input/evidence pins được đối chiếu trước và sau cleanup source/docs, không đổi. Không chạy inference, không retire accepted output hoặc dataset/model đang có consumers.
- Staged diff không binary/media/credentials; config/report JSON parse được. Caches và generated checkout không được stage.

## Cleanup chưa thực thi được

Lệnh PowerShell xóa `.mypy_cache`, `.ruff_cache` và `__pycache__` trong src/tests/scripts/tools đã kiểm path workspace nhưng **automatic approval review từ chối: “blocked by policy”**. Lệnh bị chặn trước chạy, 0 file bị xóa. Không dùng cách khác để vượt chặn. [Manifest cache](cleanup-cache-manifest.json) ghi exact files/bytes/hashes còn lại; không tuyên bố workspace hết cache.

Dataset/model, runtime/tracking/events canonical outputs và gallery/audit evidence giữ nguyên vì còn phục vụ truy vết nghiệm thu, không là rác chỉ vì stage đã đóng. Deadline media không thay đổi. Scratch kiểm commit được quản lý riêng; availability cuối ghi trong TASK/bàn giao.
