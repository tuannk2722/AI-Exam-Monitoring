# E008 — Quyết định chuyển phase prototype ngày 25/10/2026

ID: `E008-PROTOTYPE-20261025`. Owner: chủ repository. Trạng thái: **Accepted cho chuyển phase và chọn model prototype**.

## Authorization và phạm vi

Owner yêu cầu không tiếp tục mục tiêu 80/80/20, sau đó trả lời “approve, tiến hành thực hiện đi! làm trên branch mới giúp tôi”. Khi được hỏi chọn checkpoint, owner chọn “Dùng G0 seed 20261023 cho prototype”; với runtime, owner chọn “Chuẩn bị đề xuất detector/crop và yêu cầu video để tôi duyệt”. Đây là approval cho chuyển phase, không là approval của proposal runtime chưa có lúc trả lời.

Dừng cải thiện classifier tại E008; không cần E009 để đạt numerical gate trước khi tích hợp prototype. Supersede riêng vai trò chặn chuyển phase prototype của precision/recall ≥ 80%, FPR ≤ 20% trong `TRAIN-VAL-ACCEPTANCE-20261017` và yêu cầu model Selected theo chất lượng nghiên cứu ở downstream. Không thay gate tính toán, support, nhãn/splits, số liệu hoặc decision lịch sử. Looking thiếu support và chưa đạt P/R vẫn được báo nguyên trạng.

Model được chọn cho prototype là `E008-V14-G0-S20261023`, checkpoint `best.pt`, epoch 8. Chọn run screening thắng đã xác định trước confirmation, không chọn lại seed theo điểm validation. Quyết định này không gán trạng thái Selected cho evaluation nghiên cứu hoặc nghiệm thu toàn hệ thống.

- Checkpoint: `outputs/E008-V14-Colab-20261024/runs/E008-V14-G0-S20261023/best.pt`.
- SHA256: `cb86da628495996a15135d0d1b400ef410d29383c49f20e6c763c838eb85b500`.
- Target order: `[phone_use, looking_around]`; ngưỡng giữ nguyên `[0.5, 0.3914746344089508]` từ `calibration.json` cùng run.
- Preprocessing/model lấy từ `resolved-config.json` và source đã pin của run; runtime adapter mới có identity riêng, không nới evaluator lịch sử để chạy code mới.
- Evidence: [kết quả](results-20261025.md), [checkpoint import](checkpoint-import-20261025.json). Validation là development, không holdout độc lập; chưa đo chất lượng video.

## Bước tiếp theo và giới hạn

[Proposal runtime](../../../configs/runtime/RUNTIME-PROTOTYPE-20261025/README.md) đã được owner duyệt tiếp trong hội thoại; [authorization](../../../configs/runtime/RUNTIME-PROTOTYPE-20261025/owner-authorization.json) ghi scope implementation/synthetic. Video thật vẫn chờ rights đúng clip. Sau đó triển khai source → frame/time → person → crop → classifier có provenance; QA trước tracking/events/web. Các gate tracker/rules/risk, media rights và nghiệm thu video vẫn áp dụng. Không cấp training, final-test access, upload, public deployment hoặc thay license repository. Không sửa bytes/pins/results E008 cũ.
