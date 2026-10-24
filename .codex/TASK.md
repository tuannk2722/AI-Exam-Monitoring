# CLEANUP-E007-20261024 — Dọn tài sản nghiên cứu và commit

- Trạng thái: hoàn tất cleanup và commit theo yêu cầu owner; protected verification, Git checker và kiểm tra checkout sạch đều PASS.

## Yêu cầu và hiện trạng

Đã đọc index/status/storage/operations và đối chiếu Git. E007 FINISHED, D1 là hướng chính nhưng looking chưa đạt; chưa Selected. Giữ các thay đổi E007 chưa commit, không train/inference mới.

## Quyết định và inputs

Owner cho phép nghỉ lưu tài sản cũ không còn ích cho phát triển. Lập exact manifest/hash trước xóa; giữ V13, nguồn recrop/QA độc nhất, pretrained DINO/ResNet, ba best D1 và ba đối chứng R0 cùng metadata/predictions/config/code. Không sửa pins hoặc tuyên bố lịch sử còn tái lập đầy đủ. Archive nguồn không coi là cache.

## Outputs và vòng đời

Report cleanup-20261024 giữ manifest/protected snapshots/availability/receipt. Script audit E007 đã bảo toàn nguyên bytes trong report trước dọn scratch. Cache/duplicate bundle/scratch/checkpoint cũ được xét theo dependency. Không tác động Downloads ngoài workspace.

## Contract impact và checks

Không đổi thuật toán/schema/labels/splits. Source identity E007 giữ nguyên. Kiểm protected hashes trước/sau; regression/source checks; stage đúng source/docs/config/metadata, require-git checker và inspect staged diff trước commit. Không stage media/checkpoints/env/cache/credentials. Git attributes giữ exact bytes các config E007.

## Checkpoint và bàn giao

Đã xóa 8.971 files / 9,959 GiB logical, ổ D tăng 7,674 GiB trống. Workspace còn khoảng 13,748 GiB; 21.177 protected files giữ nguyên SHA/size PASS, sáu best D1/R0 còn đủ. Manifest/receipt/verification ở report cleanup-20261024, storage/status/operations đã cập nhật availability. 210 tests/Ruff/mypy PASS; không train/inference mới. E007 source/config pins giữ nguyên; staged exact bytes 47 artifacts đã kiểm. Cache/scratch không còn file; automatic review chặn riêng xóa cây thư mục rỗng “blocked by policy”, để nguyên, không bypass. Require-git checker và staged diff PASS. Checkout sạch của commit đã kiểm repository PASS và source SHA E007 giữ nguyên `e7810ca31a9a1bf1d2f110f1b348dafe8130f7f2717cb504ff0736f9a23cc8f7`; không còn bước nghiên cứu hoặc train trong task cleanup này.
