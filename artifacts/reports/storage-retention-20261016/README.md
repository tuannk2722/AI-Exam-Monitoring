# Retention tài sản hiện hành — 16/10/2026

Trạng thái: hoàn tất; [receipt](receipt.json) và [xác minh độc lập](validation.json) PASS. Owner đã approve trong hội thoại việc ưu tiên dataset/model hiện hành, chấp nhận không tái lập toàn bộ lịch sử và yêu cầu commit trước khi dọn.

## Baseline và quyền
Baseline `999c0cce08a6f9a4002693d29be578fcba803dc8` lưu source/docs/config/metadata trước cleanup; không chứa binary. 164 unit tests PASS, Ruff PASS, strict Mypy 43 source files PASS, checker require-git PASS và clean checkout checker PASS. Git attributes C345 giữ bytes đã pin. Whitespace trong tài liệu gốc giữ nguyên.

[Chính sách được duyệt](../../../docs/storage.md) thay đề xuất xóa hàng loạt ở baseline. Không đổi nhãn, split/group, metrics, model selection hoặc quyền test. Không train/inference/upload.

## Inventory và thực hiện
[Script vận hành một lần](cleanup.py) tái dùng common.history và integrity hiện có. Mặc định chỉ plan; backup và apply là bước riêng. Plan ghi hash/size từng file được bảo vệ và từng file nghỉ lưu; apply preflight toàn bộ trước khi unlink, không xóa file tracked hoặc path ngoài workspace.

Giữ V10 canonical, C345 development, cohort/reserve, tất cả model chính/pretrained, raw/interim, gallery và metadata. Giữ last.pt C345 và checkpoint nhỏ E001–E003 theo consumer audit; bỏ weights smoke/resume E004 lịch sử đã đóng, crops active của V4–V9/V9 development, ba ZIP execution V9/RC1/C345 cùng cache bản copy. Archive nguồn và snapshot source code nhỏ giữ nguyên; hardlink history giữ nguyên.

## Availability và giới hạn
Metadata/checksum cũ được giữ nguyên để đọc kết quả, không cam kết dataset lịch sử còn đầy đủ hoặc resume run cũ. Không dùng V10 thay version cũ để tuyên bố tái lập. Tài sản nguồn còn trong archive được truy theo inventory khi cần; không tự mở test/reserve.

Backup hiện hành nằm cùng ổ D, không chống hỏng ổ. Remote chưa xác minh/upload. Không xóa backup ngoài workspace. Preview vẫn giữ vì chưa chứng minh mọi ảnh có thể tái tạo mà không mất evidence.

Dependency phát hiện khi đối chiếu code: error_audit và evaluator baseline kiểm toàn bộ checksums.json. Giữ C345 last.pt để audit hiện hành không hỏng; standalone load_bundle E004 chỉ cần tập artifacts inference. [Plan v1](plan-v1.json) được thay bằng [plan v2](plan.json) trước xóa, không thay pins gốc. [Consumer evidence](consumer-dependencies.json). Backup checkpoint bổ sung riêng, không reseal ZIP đã tạo.

## Backup đã kiểm
- [Backup hiện hành](backup-verification.json): 10.880 file, archive/current-assets-20261016.zip.
- [Checkpoint phụ thuộc](dependency-backup-verification.json): 4 file, archive/current-run-dependencies-20261016.zip.
- Cả hai đã verify nội dung và restore byte-exact toàn bộ. Lần đầu restore gặp giới hạn đường dẫn Windows, đã thử lại bằng extended path; [ghi nhận](restore-retry.json). Scratch đã dọn.
- DVC pointer/registry chỉ định danh ZIP; không tạo thêm cache copy, không remote upload. Archive nguồn được giữ riêng, không nhúng lặp vào backup hiện hành.
- Backup là snapshot trước cleanup; tài liệu availability hiện hành ở Git/hồ sơ này có ưu tiên hơn mô tả storage tại thời điểm snapshot.

## Kết quả cuối
- Xóa 4.950 file theo plan v2, tổng 12,31 GB; 10.260 file bảo vệ giữ nguyên hash. Hai package hiện hành qua integrity.
- Toàn workspace tính bytes file duy nhất (loại trùng hardlink): 22,28 GB → 11,99 GB, giảm ròng khoảng 10,29 GB, đã tính hai backup mới. Đây không phải phép đo allocation vật lý; thay đổi vài KB tài liệu sau phép đo không ảnh hưởng số làm tròn.
- Nạp model C345 bằng load_bundle hiện hành PASS, toàn bộ 17 checksum của run và 45 result pins khớp; 110 source/config/requirements không đổi so baseline. Không train/inference/test access.
- [Availability hiện hành](availability.json) chỉ rõ archive giữ/retire và package cũ không đầy đủ. Source raw/interim, gallery, cohort/reserve và model chính giữ nguyên.
- [Ghi nhận resume](resume-observation.json): receipt hoàn tất xuất hiện trong lúc preflight resume; lượt resume dừng trước unlink. Đã bổ sung exclusive apply lock và kiểm bằng stub, không apply thêm. Gián đoạn kết nối tool không chứng minh subprocess đã dừng.
- Commit trước cleanup: 999c0cc. Các thay đổi chính sách/receipt sau cleanup chưa commit; không upload/push.

Context agent đã thống nhất theo yêu cầu owner: [policy](../../../docs/storage.md) giữ quy tắc, [availability](availability.json) đủ 10 archive gồm hai backup mới; status chỉ giữ hiện trạng. Restore chỉ khi task cần và đủ inputs; immutable không đồng nghĩa giữ payload vĩnh viễn. Kiểm 80 local links, registry/availability/presence và repo checker PASS; không sửa source/config hoặc hồ sơ đã pin.
