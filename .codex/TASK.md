# RUNTIME-CLEANUP-COMMIT-20261025

- Trạng thái: code/docs đã kiểm, commit local; xóa 9 roots chờ thủ công do policy chặn trên feat/runtime-prototype-e008.

## Scope và authorization

Owner yêu cầu cleanup codebase, xóa sạch ba lần thử nghiệm video và mọi artifacts/config/report liên quan, commit phase runtime mới. Yêu cầu mới cho phép retire cả metadata thử nghiệm, không chỉ media. Đã đối chiếu Git/index/status/TASK, storage/development, runtime code/tests/config và các incoming references. Không thay model/thresholds/crop/data hoặc mở training/inference. Không push.

## Inputs được bảo toàn

Giữ V14/E008, G0 checkpoint/calibration/resolved config, DINO source/license, YOLO weights và receipt, config prototype/authorization, source/tests tái dùng và quyết định chuyển phase. Video nguồn Downloads giữ nguyên; scope xóa chỉ trong workspace.

## Cleanup và lifecycle

Xóa outputs của 3 clip, lượt full-frame partial, reports/receipts/audit riêng và configs QA 1/2 Hz; scratch synthetic/settings thừa. Inventory/hash và protected pins trước/sau trong outputs/runtime-prototype-20261025/cleanup-manifest.json; receipt tóm tắt trong report runtime. Cập nhật status/index/usage loại references đã retire; không giả model/video được nghiệm thu. Không xóa env hoặc inputs nghiên cứu.

## Checks và bàn giao

Đã review source/staged diff và links; 233 tests PASS trong 315,717 giây; Ruff PASS, strict mypy 61 files PASS, compileall/pip check PASS. Checker workspace báo 6 files config thử nghiệm chưa stage (do chưa xóa); không stage để qua gate. Snapshot sạch của index đã PASS checker --require-git, 13 runtime tests và detector receipt pin. Commit chỉ source/docs/config prototype/metadata cần giữ; không chứa 3 thử nghiệm hoặc media. Xóa bị automatic approval review chặn (blocked by policy, không chi tiết); đã hỏi owner thao tác thủ công, không sửa policy. Protected inputs 11 files PASS. Checkout kiểm riêng ở outputs/_scratch/runtime-clean-checkout-20261025 được gỡ sau kiểm commit.
