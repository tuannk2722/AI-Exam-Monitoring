# V12-COMMIT-MERGE-20261020 — Lưu và merge trạng thái audit/V12

- Trạng thái: đang làm; owner yêu cầu cleanup, commit toàn bộ thay đổi hợp lệ và merge vào experiment/e005-pilot-b-v11.
- Inputs: audit/v11-legacy-crops-20261018 tại 44d6a5d, hồ sơ legacy/YouTube/consolidation/V12; đã đọc index/status/storage/operations/development.
- Scope: giữ source/config/docs/metadata trong Git; media/package/backup giữ local theo retention. Không upload, train hoặc sửa accepted pins.
- Cleanup: kiểm inventory/dependencies; giữ nguồn và evidence review, chỉ dọn cache tái tạo được. Scratch release đã dọn. Manifest/checks ở hồ sơ V12 commit-handoff.json.
- Checks: staged diff, checker --require-git, checksum protected trước/sau cleanup, clean checkout metadata. Không đổi contract/spec.
- Tiếp: cleanup theo manifest, stage đúng scope, kiểm index, commit và fast-forward merge; xác minh Git sạch.
