# E009-CLOSEOUT-WEB — Cleanup/commit E009 và tích hợp model đã chốt

- Trạng thái: pha 1 cleanup/commit E009; sau đó pha 2 nghiên cứu và tích hợp web.

## Yêu cầu và hiện trạng
Owner yêu cầu cleanup codebase rồi commit trước; tiếp theo đóng khung hai hành vi E009 để hoàn thiện demo và nghiên cứu hành vi mới sau. Owner đã chọn rõ: một phiên chọn B0 hoặc B448 chạy cả hai nhãn, B0 mặc định. Đã đọc AGENTS/index/status/TASK/development/storage/live design và đối chiếu Git. Worktree đang chứa toàn bộ E009 implementation/audit chưa commit từ baseline 79c04ce.

## Quyết định và inputs
Đủ best/last B0-S20261106, B448-S20261110, C0-S20261107; metadata audit có findings nhưng rank và gates giữ nguyên. Giữ checkpoint/calibration/preprocessing/seed của B0 và B448; C0 chỉ control. Không train thêm E009, không final test, không ensemble hoặc ghép hai model theo target. Cho phép prototype web tích hợp theo lựa chọn owner; không gọi kết quả development là nghiệm thu holdout tổng quát. Model/source/data và receipts đã pin bất biến.

## Outputs và vòng đời
Commit pha 1 chỉ source/docs/config/metadata E009; không media/model/ZIP/env/cache vào Git. Dọn scratch đã xác nhận không còn dependencies; không retry tooling cũ bị policy chặn. Sau commit mới sửa runtime/web bằng config/authorization version mới, giữ G0 artifacts và phiên lịch sử. Không push/deploy/cloud/send messages.

## Contract impact và checks
Cleanup giữ contract và source snapshot đã train; kiểm package identity và pins trước commit, Ruff/Mypy/targeted checks, index/registry --require-git, inspect staged diff và clean checkout. Bản source 68802787… đã có full-suite evidence 399 tests; không train/smoke lại chỉ vì cleanup. Integration: khảo sát classifier/runtime/factory/session/UI và consumer trước thay, ghi scope chọn model và provenance mỗi phiên; kiểm fixtures API/classifier/cross-session/browser thích hợp, không tự benchmark/claim real-time.

## Checkpoint và bước tiếp
Đang rà pending E009 files, commit cleanup trước; chốt B0 mặc định/B448 tùy chọn đã có owner approval, không hỏi lại phần này.
