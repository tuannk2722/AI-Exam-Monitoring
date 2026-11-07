# E009 — Model cho demo hai hành vi

Owner đóng khung E009 cho `phone_use` và `looking_around`, chuyển sang hoàn thiện demo. [Quyết định](decision.json) ghi lựa chọn đã xác nhận: mỗi phiên dùng B0 hoặc B448 cho cả hai nhãn, B0 mặc định. Đây là lựa chọn sử dụng trong prototype local; không thay findings hoặc trạng thái nghiệm thu nghiên cứu của [audit E009](../../../artifacts/reports/e009-v15-colab-20261106/results-20261107.md).

| Lựa chọn | Checkpoint đại diện | Input | Ngưỡng phone / looking |
|---|---|---|---|
| [B0](B0.yaml), mặc định | `E009-V15-B0-S20261106/best.pt` | 336 × 336 | 0.2072346806526184 / 0.451124370098114 |
| [B448](B448.yaml) | `E009-V15-B448-S20261110/best.pt` | 448 × 448 | 0.3575829863548279 / 0.5 |

Cả hai là DINOv2 ViT-B/14, global CLS + mean patch; chọn một checkpoint xử lý đồng thời hai nhãn. B0 đứng đầu thứ hạng E009 nên làm mặc định; B448 là phương án thay thế đã audit. Không ensemble, ghép model theo nhãn, dùng threshold 0,5 chung hoặc chọn lại seed. Giữ RGB letterbox bilinear, mean/std/fill theo resolved config. Unknown và giới hạn looking trong cohort old-train chuyển sang val giữ nguyên; không train thêm hoặc mở final test.

Runtime v5 bổ sung binding model/run/image size vào classifier; mỗi YAML có authorization riêng khớp digest và pin quyết định. Checkpoint/config/calibration/bundle/run đều pin SHA256. Giữ detector V8S, receipt license, detector selection, context-v1, CPU FP32, batch 1, 4 threads và sampling 1 Hz của runtime trước. Chưa chọn CUDA hoặc chứng minh tốc độ live. Source training gốc được giữ tại commit `da64704`, package SHA `68802787f7ee3d892073ff46e6657d45f0d74d283fab5a8ad3582f0795876c29`; source tích hợp web có identity mới, không sửa identity checkpoint hoặc evaluator lịch sử.

Web chính đọc [allowlist model](../../web/E009-MODELS-20261107/monitor.yaml). Chọn model trước upload; không đổi giữa phiên, kể cả pause/seek. Phiên mới lưu model ID, checkpoint/calibration SHA, thresholds, preprocessing và runtime digest. Chỉ model đã chọn được load khi bắt đầu; không nạp đồng thời cả hai. Config G0 và sessions cũ giữ nguyên; `/review` cùng pipeline offline C10/events tiếp tục contract lịch sử, không tự áp dụng rule G0 sang model mới.

Receipt video cho các phiên E009 cần `runtime_id: RUNTIME-E009-20261107`, cùng hash nguồn/quyền sử dụng/deadline thực còn hạn theo policy hiện hành. Hai lựa chọn cùng runtime family và khác config SHA; receipt có quyền cho family này dùng được cho cả hai. Không tự sửa receipt G0 cũ hoặc gia hạn media. Mở UI bằng `.venv/Scripts/python.exe -m ai_exam_monitoring.web --workspace .`; chọn model rồi upload MP4 và receipt phù hợp.

Kiểm bàn giao: Ruff/strict Mypy PASS; 43 runtime tests và 2 classifier tests PASS; nhóm web 21 tests OK (2 browser opt-in skipped), riêng browser monitor đã bật và PASS trên Chrome với fixtures tổng hợp, kiểm lựa chọn/khóa model/reload/pause/seek/stop và light/dark. Hai checkpoint B0/B448 thật đã load qua runtime v5 và forward trên một ảnh RGB tổng hợp, output hữu hạn, đúng size/thresholds; không gọi dataset hoặc video người thật. Đây là kiểm integration CPU, không là parity CUDA, benchmark tốc độ hoặc nghiệm thu chất lượng demo.
