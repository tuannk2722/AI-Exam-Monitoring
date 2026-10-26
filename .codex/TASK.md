# CLEANUP-COMMIT-20261027 — Nghiệm thu events, cleanup và hai commit

- Owner đã review candidates/kết quả giám sát và chấp nhận cho prototype. Yêu cầu cleanup kỹ, commit riêng tracking và events; không push.
- Đã đối chiếu index/status/contracts, Git, storage/development và inputs đã pin. Không gọi model hoặc mở risk/web.
- Ghi receipt nghiệm thu events riêng, không sửa candidates thành confirmed từng dòng hoặc đổi session đã seal. Cập nhật trạng thái hiện hành; giữ giới hạn tracking/classifier.
- Cleanup caches có thể tái tạo và scratch rỗng, rà source/docs; giữ dataset/model/inputs và evidence canonical đang có consumers. Kiểm exact paths trong workspace trước xóa, lưu manifest và hashes bảo toàn.
- Commit tracking gồm implementation/tests/gallery/config/research và closeout C10; proposal events draft là hồ sơ handoff đã được closeout pin/tham chiếu. Commit events gồm rules được duyệt, implementation/tests/replay/acceptance và trạng thái sau nghiệm thu. Không media/model/cache vào Git.
- Kiểm Ruff/mypy/tests, staged diff, checker require-git trên từng snapshot commit và clean checkout; kiểm pins giữa working tree và Git. Dọn checkout/cache sau kiểm, báo hai hashes và final clean status.
- Trạng thái: đã kiểm đủ hai snapshot và tách commit tracking/events theo yêu cầu; nghiệm thu events đã ghi receipt. Không push hoặc mở risk/web.
- Checks: full suite 303 tests PASS, Ruff PASS, mypy 73 files PASS; checker require-git trên workspace và từng snapshot PASS. Snapshot tracking 22 tests/events 10 tests PASS, 32 staged pin edges khớp; 52 input/evidence paths bảo toàn.
- Cleanup source/docs và hai checkout/helper tạm đã hoàn tất. Xóa cache bị automatic approval review chặn trước chạy: 126 files/42.749.409 bytes còn lại, 0 file cache đã xóa. Không bypass. Manifest/giới hạn ở artifacts/reports/events-prototype-20261027/cleanup-commit-20261027.md. Evidence/model/dataset giữ nguyên.
