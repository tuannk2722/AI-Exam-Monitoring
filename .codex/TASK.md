# REPO-REVIEW-CLEANUP-COMMIT-20261018 — Kiểm tra, dọn dẹp và commit trạng thái E005 V11

- Trạng thái: kiểm tra và dọn dẹp hoàn tất; bàn giao bằng commit Git của task này; scope do user yêu cầu: kiểm tra codebase/status hiện tại, dọn an toàn và commit trên nhánh `experiment/e005-pilot-b-v11`.

## Yêu cầu và hiện trạng
- Đã đọc AGENTS, docs/00-INDEX.md, docs/status.md, TASK trước, docs/development.md và docs/storage.md; đối chiếu Git diff và file thực tế.
- Working tree có pipeline matched-adaptation-v3, test E005 mới, configs E005-V11-20261018 và reports e005-v11-adaptation-20261018 chưa commit.

## Quyết định và inputs
- Giữ nguyên approval E005-V11-EXECUTION-APPROVAL-20261018, configs/pins và dataset V11 pilot-b-20261017-v11.
- Không chạy lại training/smoke hoặc mở test thật; không đổi scientific variables hay acceptance. Software checks dùng synthetic fixtures.
- Retention theo docs/storage.md: bảo toàn raw, dataset/model hiện hành, dependencies và evidence độc nhất.

## Outputs và vòng đời
- Commit source/tests/docs/config/metadata nhỏ đúng scope hiện tại; không push.
- Chỉ dọn cache/tooling/scratch sau inventory exact paths/hashes và kiểm dependencies; giữ canonical outputs của 5 run E005 cùng init/pretrained.
- Không sửa bytes của configs/approvals/artifacts đã pin. TASK này thay TASK execution cũ, không là approval hay worklog.

## Contract impact và checks
- Không đổi contract; không sửa spec.
- Review diff, kiểm traceability code/config/approval/run và kết quả status; Ruff, strict Mypy, compile và full unittest phù hợp phạm vi training.
- Trước commit: review staged diff, scripts/check_repo.py --require-git; sau commit kiểm Git sạch. Nếu thay đổi cấu trúc rộng thì kiểm clean checkout theo development.

## Checkpoint và bàn giao
- Review source và producer/consumer training/evaluation; giữ code identity `241460325c026eb4aee270f8a3f8e9eedef8fde1ee9276d23fdc29d5a7ce1a7a` để bảo toàn reload và approvals.
- Ruff toàn src/tests/scripts PASS; strict Mypy PASS (43 source files); compileall PASS; full unittest PASS (170 tests, 222,427 giây, có classifier dependencies).
- Cả 5 configs: approval/readiness PASS; 65 artifacts theo checksums của 5 runs PASS; summary metrics/learning curves và gallery khớp outputs. Không chạy training/inference trên dataset thật hoặc mở test.
- Sửa docs/status.md: phone AP của S1-AUG trên legacy_val_192 là 0,8606 (trước ghi nhầm 0,8431); thêm reference schema v3 và giới hạn CPU; rút metrics khỏi reports index. Làm rõ giả thuyết nguyên nhân chưa có đối chứng, model tensors giống nhau không đồng nghĩa checksum bundle giống nhau.
- Thêm .gitattributes cho exact CRLF bytes của E005 configs/protocol/approval khi checkout; không sửa configs/pins.
- Đã dry-run exact cache paths/SHA-256 rồi dọn 12 thư mục cache (39.480.818 bytes); kiểm 137 protected files trước/sau PASS, code identity không đổi. Giữ dataset/model/raw/init/pretrained và toàn bộ canonical run evidence.
- `git diff --check` chỉ báo 4 dòng trống EOF ở adaptation_config.py, adaptation_metrics.py, adaptation_model.py và data.py. Giữ bytes vì source đã pin; không đổi hash/approval chỉ để sửa whitespace.
- Inventory/patch/checkout kiểm tra tạm được dọn sau xác minh; outputs/_scratch không có scratch cũ khác. Không dọn local environment hoặc lịch sử payload ngoài scope cache.
- Staged diff đã review; checker --require-git PASS. Snapshot Git không có run binaries: checker PASS, tree parity với index PASS, exact bytes 13 JSON/YAML E005 PASS và code identity giữ nguyên. Commit đúng 30 file source/tests/docs/config/metadata; xác minh Git sạch sau commit, không push.
- Hiện trạng khoa học: 5 run FINISHED; S1-AUG tốt nhất trong ma trận một seed nhưng chưa vượt đồng thời cổng 80/80/20; continue_research_only, chưa Selected. Không tự triển khai vòng nghiên cứu hoặc mở downstream/test mới.
