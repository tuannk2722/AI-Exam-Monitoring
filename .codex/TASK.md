# E009-CLOSEOUT-WEB — Cleanup/commit E009 và tích hợp model đã chốt

- Trạng thái: hoàn tất cleanup/commit E009 và tích hợp B0/B448 vào giám sát web; checks bàn giao PASS.

## Yêu cầu và hiện trạng
Owner yêu cầu cleanup codebase rồi commit trước; tiếp theo đóng khung hai hành vi E009 để hoàn thiện demo và nghiên cứu hành vi mới sau. Owner đã chọn rõ: một phiên chọn B0 hoặc B448 chạy cả hai nhãn, B0 mặc định. Đã đọc AGENTS/index/status/TASK/development/storage/live design và đối chiếu Git. Worktree đang chứa toàn bộ E009 implementation/audit chưa commit từ baseline 79c04ce.

## Quyết định và inputs
Đủ best/last B0-S20261106, B448-S20261110, C0-S20261107; metadata audit có findings nhưng rank và gates giữ nguyên. Giữ checkpoint/calibration/preprocessing/seed của B0 và B448; C0 chỉ control. Không train thêm E009, không final test, không ensemble hoặc ghép hai model theo target. Cho phép prototype web tích hợp theo lựa chọn owner; không gọi kết quả development là nghiệm thu holdout tổng quát. Model/source/data và receipts đã pin bất biến.

## Outputs và vòng đời
Commit pha 1 chỉ source/docs/config/metadata E009; không media/model/ZIP/env/cache vào Git. Dọn scratch đã xác nhận không còn dependencies; không retry tooling cũ bị policy chặn. Sau commit mới sửa runtime/web bằng config/authorization version mới, giữ G0 artifacts và phiên lịch sử. Không push/deploy/cloud/send messages.

## Contract impact và checks
Cleanup giữ contract và source snapshot đã train; kiểm package identity và pins trước commit, Ruff/Mypy/targeted checks, index/registry --require-git, inspect staged diff và clean checkout. Bản source 68802787… đã có full-suite evidence 399 tests; không train/smoke lại chỉ vì cleanup. Integration: khảo sát classifier/runtime/factory/session/UI và consumer trước thay, ghi scope chọn model và provenance mỗi phiên; kiểm fixtures API/classifier/cross-session/browser thích hợp, không tự benchmark/claim real-time.

## Checkpoint và bước tiếp
Cleanup đã commit `da64704`, Ruff/Mypy/9 recovery tests và checker index/checkout sạch PASS. Đã khảo sát classifier, runtime guards, factory online, upload/session, API/UI và consumer tests. Đã materialize quyết định owner/config runtime v5 và web v2: B0 mặc định/B448 tùy chọn, một model xử lý cả hai nhãn, khóa suốt phiên và lưu provenance; v1/legacy giữ tương thích. Giữ V8S/context-v1/CPU FP32/cadence hiện tại. Receipt video mới gắn runtime family E009; không tự đổi receipt cũ. Ruff/Mypy, 43 runtime tests, 2 classifier tests và 21 web tests (2 browser opt-in skipped) PASS; browser monitor chạy riêng trên Chrome PASS. Hai checkpoint thật load/forward ảnh tổng hợp PASS, không inference dataset/video người thật hoặc claim CUDA/SLA. Diff và staged diff đã rà, checker index thật PASS; training snapshot giữ ở commit trên, tích hợp được commit riêng, không push. Công việc sau task này là hoàn thiện demo theo scope riêng, không tự train thêm E009.
