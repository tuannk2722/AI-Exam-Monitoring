# CI-E009-RECOVERY — Sửa discovery khi không có Torch

- Trạng thái: đã sửa và kiểm local PASS; bàn giao bằng commit/push theo yêu cầu owner.

## Yêu cầu và hiện trạng
Đã đọc AGENTS/index/status và đối chiếu source/workflow. Job quality chạy unittest với base/dev, không cài Torch. Test recovery import Torch, artifacts và recovery extension vô điều kiện, gây lỗi discovery. Worktree sạch trước task.

## Quyết định và inputs
Theo convention tests ML hiện có: guard imports và skip tests cần ML khi thiếu Torch/torchvision. Giữ tests notebook thuần standard library chạy trong quality. Không cài ML cho quality hoặc sửa recovery/notebook/config/checkpoint đã pin. User yêu cầu commit và push; không force push.

## Outputs và vòng đời
TASK, test recovery và workflow classifier để tests ML không bị bỏ sót sau khi quality skip. Kiểm thiếu Torch bằng subprocess cô lập imports, không tạo env mới/tải weights hoặc data. Không thêm report/spec/status cho bug discovery.

## Contract impact và checks
Không đổi contract. Kiểm recovery có Torch, full unittest discovery khi chặn Torch, Ruff/diff/checker index; inspect staged diff trước commit và push branch hiện tại.

## Checkpoint và bàn giao
Đã guard ML imports, giữ hai tests thuần standard library chạy khi thiếu Torch, skip bảy tests cần ML; thêm recovery suite vào job classifier-tests. Discovery mô phỏng không có Torch: 406 tests OK, skipped 234; có Torch: 9 recovery tests PASS. Ruff và diff check PASS. Không đổi source recovery/notebook/model/pins; chỉ ba file TASK/test/workflow. Kiểm index/staged diff trước commit, push branch hiện tại; kết quả CI remote phải đọc từ lượt chạy mới, không suy từ local PASS.
