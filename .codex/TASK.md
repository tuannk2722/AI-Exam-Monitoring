# FIVE-LABEL-EXECUTION-20261109 — Chuẩn bị training và runtime/web

- Trạng thái: hoàn tất bước 3–4 ở mức software/fixtures; commit local nhánh research/behavior-expansion theo yêu cầu owner. Không mở run, smoke với input thật, final test, profile hoặc đổi model demo.

## Yêu cầu và hiện trạng
Bước 1–2 đã có contract và workflow audit/review/QA năm nhãn, regression V1/V2; các thay đổi còn trong working tree tại main 339985a. Dữ liệu ngoài phải audit từ đầu, không có intake riêng. Đã đọc AGENTS/index/status, training/data/development/reference và producer/consumer config, loader, model, loss, calibration, runtime và web liên quan trước sửa.

## Quyết định và inputs
Giữ LABEL-CONTRACT-20261109 và thứ tự phone_use, looking_around, sleeping, hand_raising, standing_up; sleeping/looking chỉ ràng buộc ground truth/QA. Owner yêu cầu refactor trực tiếp code dùng chung, không mở phiên thực thi/pipeline riêng; đã duyệt loss tổng quát theo K và calibration có mục tiêu từng nhãn tường minh, chưa chốt con số. Chưa cho phép recipe/run hoặc deployment mới. Đã báo sửa numerical source làm guard demo GPU cũ từ chối source hiện tại; không sửa accepted data/model/config/receipts/pins để qua guard.

## Outputs và vòng đời
Refactor code hiện có theo metadata, không thêm phiên thực thi/pipeline hoặc experiment/data giả trong production. Fixtures synthetic trong thư mục tạm tự dọn; không tải weights/media hoặc stage/commit. Cache five-label-types của task trước còn do lệnh xóa đã bị automatic approval review chặn; không thử đường khác.

## Contract impact và checks
Giữ semantics/pins cũ; metadata năm nhãn bind target order/encoding/semantics trên API dùng chung. Kiểm masks/support, hai/năm đầu ra, calibration/reload/report, metadata và UI, regression cũ, lint/type/full suite khi source ổn định. Software PASS không thay acceptance dữ liệu/model/GPU.

## Checkpoint và bàn giao
Đã tổng quát config/encoding, loader, head/loss, calibration/reporting, classifier/frame processor, playback/overlay và web monitor theo metadata. Fixtures kiểm canonical train/reload/resume năm nhãn, masks/AP unavailable, preservation evidence, head/encoding/protocol sai và luồng hai nhãn. Temporal pipeline và campaign ranking giữ scope hai nhãn, chặn binding năm nhãn trước model/GPU/run setup.

Full suite 453 tests OK/skipped 4; sau bổ sung guard campaign, 29 tests training/representation/campaign liên quan PASS. Chrome UI hai/năm nhãn và upload/overlay/metadata PASS. Ruff, strict Mypy 97 files, syntax/UTF-8, links/anchors, diff và checker index tạm PASS; index thật không sửa. README/reference/status đã thay nội dung hiện hành, không thêm report. Configs/artifacts/pins giữ nguyên; không stage/commit. Bước 5 chưa mở: cần dataset/model/protocol và scope tích hợp thật riêng; source hiện tại khác bốn numerical pins của profile GPU B0 cũ nên guard sẽ chặn.
