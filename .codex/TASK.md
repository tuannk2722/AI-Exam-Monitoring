# LAPTOP-VIDEO-20261108 — Hoàn tất bàn giao baseline web GPU từ repository

- Trạng thái: hoàn thành phần source/setup/bàn giao; chờ owner cấp quyền commit/merge. Chưa stage, commit, push hoặc merge. Xác nhận web GPU trên laptop thật vẫn là kiểm chứng riêng.

## Yêu cầu và hiện trạng
Đã đọc AGENTS/index/status và đối chiếu nhánh feat/gpu-laptop-test tại c06c83a. Mục tiêu: bàn giao baseline upload MP4/B0 CUDA FP32 batch 1, sampling 1 Hz từ repo, có đủ metadata Git và đường khôi phục model, chọn đúng profile khi mở web và mô tả khớp capability thực tế.

## Quyết định và inputs
User cho xử lý dứt điểm các điểm review để chuẩn bị merge. Giữ nguyên runtime E009, model, calibration, thresholds và các pins đã duyệt. Ba JSON parity/profile/code ở outputs/verify-b0-01 giữ nguyên bytes/path. Model vẫn ngoài Git; tái dùng video-web.zip hiện có, chỉ khôi phục đúng dependencies đã kiểm checksum, không chép source/config đè repo. CLI mặc định chọn profile laptop GPU, CPU chọn config tường minh. Không camera, tracking/events online hoặc thay kiến trúc AI. Giữ integrity guard numerical source; không suy profile B0 thành quyền chạy model E mới.

## Outputs và vòng đời
Source/tooling và hướng dẫn chạy từ repo; manifest input triển khai không chứa media/env/credentials. Metadata kiểm chứng được đưa vào phạm vi Git bằng ngoại lệ chính xác. Một launcher dùng chung repo/gói ZIP; giữ nguyên hồ sơ config/receipt đã pin. Scratch kiểm restore/checkout/package ở thư mục tạm và dọn sau kiểm. Không tạo report hoặc log cleanup mới.

## Contract impact và checks
Không đổi contract AI, session hoặc scientific acceptance; không sửa spec. Kiểm restore thiếu input/sai checksum/không overwrite/sai path, CLI mặc định và override CPU, launcher, source hash guards, Git delivery metadata và dependency closure. Lint/type, tests consumers và browser; full suite trước bàn giao. Kiểm checkout tạm với Git index riêng, không stage index workspace. Máy development CPU không thay xác nhận web GPU trên laptop thật.

## Checkpoint và bàn giao
`RUN.ps1` là launcher duy nhất dùng chung repo/ZIP, CLI mặc định profile GPU; CPU chọn config tường minh. `inputs.json` định danh 13 dependencies ngoài Git; restore từ gói cũ chỉ lấy input còn thiếu, từ chối sai hash/overwrite và không chép source/config. Ba JSON kiểm chứng được allowlist chính xác, giữ bytes bằng attributes; checker kiểm cả bytes Git index. Hướng dẫn hiện hành ở README root; hồ sơ config đã pin giữ nguyên.

426 tests OK/skipped 2; browser monitor PASS; Ruff, strict Mypy 97 source files, syntax 163 files, checker và diff PASS. Bản sao sạch gồm 1.631 file bàn giao với index riêng đã qua `--require-git`, restore đủ 13 inputs từ ZIP cũ, kiểm runtime/execution pins, imports và web assets/API; source/metadata không đổi và index thật giữ nguyên. Gói duy nhất `outputs/laptop-video/video-web.zip` đã cập nhật, kiểm SHA mọi thành viên và launcher; manifest giữ checksum. Scratch checkout/restore/package/type đã dọn. Giữ numerical source guards, không thay model/ngưỡng hoặc tuyên bố nghiệm thu web GPU từ kiểm phần mềm CPU. Bước tiếp chỉ là owner review/cấp quyền commit/merge; không tự mở camera/tracking hoặc nghiên cứu AI mới.
