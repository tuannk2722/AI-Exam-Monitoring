# Recipe, kết quả và phân tích baseline E001–E003

Tổng hợp chuyển từ training spec ngày 2026-10-11, dựa trên hồ sơ runs/audit đã có; không chạy lại model hoặc test. Recipe/metrics thuộc đúng run/cohort lịch sử, không là default cho run mới. Không append experiment mới vào hồ sơ này.

Nguồn: [E001](../E001/run.json), [E002](../E002/run.json), [E003](../E003/run.json); metrics/approval chi tiết qua [reports index](../README.md). Quy định chung ở [training contract](../../../docs/training.md); giới hạn code hiện tại ở [implementation reference](../../../docs/reference.md).

## 1. Recipe lịch sử E001–E003 và giới hạn implementation

ADR-014/015/016 và approval riêng lần lượt cho E001/v4, E002/v5, E003/v6. Ngoại lệ CPU chỉ ba run/smoke theo config đã pin; không kế thừa sang run mới. YAML cũ có comments pending từ lúc proposal nhưng receipt hiện `status=approved` và pin resolved config; giữ nguyên bytes/config lịch sử, không dùng comment để phủ nhận approval hoặc sửa pin.

| Thành phần | Recipe Accepted riêng E001–E003 |
|---|---|
| Backbone | ResNet18 `IMAGENET1K_V1`, local weights `outputs/pretrained/resnet18-f37072fd.pth`; SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec` |
| Trainable | Linear head 512→2; encoder parameters frozen, BatchNorm eval/buffers giữ nguyên, feature forward no_grad |
| Output | Hai logits độc lập; sigmoid scores theo `[phone_use, looking_around]`; positive decision score ≥0.5 |
| Input | RGB, letterbox bilinear 224 giữ full context; resize cạnh dài 224 và round cạnh ngắn (tối thiểu 1), center padding `[124,116,104]` |
| Normalize | Mean `[0.485,0.456,0.406]`, std `[0.229,0.224,0.225]`; không stretch/silent crop/đổi EXIF sau annotation |
| Feature extraction | Batch 16, CPU 4 threads; cache 512 features pin source/crop/data/transform/encoder identity, không tái dùng sai version |
| Objective | `macro_masked_bce`: mean BCEWithLogits của known samples mỗi target, rồi mean hai target; unknown không denominator/gradient |
| Optimization | Head AdamW, LR 0.001, weight_decay 0.0001; full-batch update, seed 42, deterministic settings |
| Budget chính | Max 200 epochs, patience 20, min_delta 0.0001; smoke configs riêng 3 epochs/interruption-resume |
| Selection | Best theo raw minimum validation masked BCE, tie giữ epoch sớm. min_delta chỉ điều khiển early-stop reference/patience, không thay rule best checkpoint |

Các số trên là recipe lịch sử Accepted, **không default khoa học cho mọi model mới**. Biến nằm trong `configs/experiments/E001.yaml`/E002/E003 và smoke tương ứng. `ExperimentConfig` hiện từ chối keys thiếu/lạ, values unresolved/nonfinite, model/device/optimizer/loss/transform khác whitelist; chỉ hỗ trợ `resnet18_frozen_linear` CPU. Đổi tên YAML không triển khai fine-tune hoặc GPU.

Backbone chỉ load weights local đúng SHA; không tự download, random fallback hoặc đổi license. `best.pt` hiện chứa head/config/identity/epoch, không standalone backbone. Dùng lại model phải có đúng pretrained + preprocess/target order/threshold; model bundle tự chứa đủ backbone là việc chưa hoàn tất cho deployment/promotion.

## 2. Kết quả đã thực hiện

Snapshot runs E001–E003: cả ba **FINISHED**, decision `continue_research_only`; chưa model Selected. Cả ba học linear head mới trên cùng ResNet18 pretrained đóng băng, không fine-tune backbone. Trạng thái kỹ thuật/decision này gắn với từng run lịch sử, không áp dụng cho experiment tiếp theo.

| Run / dataset | Train / val | Best / completed epochs | Val masked BCE | Val macro AP | Kết luận |
|---|---|---|---:|---:|---|
| E001 / v4 | 60 / 13 | 12 / 32 | 0.547727 | 0.927296 | Baseline frozen probe hoàn tất; chưa promotion |
| E002 / v5 | 80 / 13 | 7 / 27 | 0.633363 | 0.980867 | H 1 chưa được ủng hộ: BCE tăng 0.085636 so E001 trên cùng val 13; AP/looking tốt hơn nhưng phone recall giảm |
| E003 / v6 | 317 / 50 | 45 / 64 | 0.610775 | 0.787808 | H 1 development được ủng hộ so train-prevalence control BCE 0.691101; chưa chứng minh cải thiện nhân quả/generalization |

Confusion validation tại threshold 0.5; precision/recall dưới đây trên known labels:

| Run | Phone TP/FP/FN/TN | Phone precision / recall | Looking TP/FP/FN/TN | Looking precision / recall |
|---|---|---|---|---|
| E001 | 7/1/0/0 | 0.875 / 1.000 | 0/0/3/3 | null / 0.000 |
| E002 | 4/0/3/1 | 1.000 / 0.571 | 1/0/2/3 | 1.000 / 0.333 |
| E003 | 9/2/8/18 | 0.818 / 0.529 | 11/1/7/10 | 0.917 / 0.611 |

Val 13 support phone 7 P/1 N/5 U, looking 3 P/3 N/7 U. Val 50 phone 17 P/20 N/13 U, looking 18 P/11 N/21 U. Val 50 có thêm 37 development crops; không so scalar BCE/AP E003 trên 50 với E001/E002 trên 13 để kết luận model gain. E003 train/val gap BCE 0.132558, val 15 FN/3 FP; source/group concentration và labels còn hạn chế.

**E001 final test đã thực hiện đúng một protocol approved**, không còn là tập test mới: 11 crops, BCE 0.569219, macro AP 1.0; phone 2 P/2 N/7 U có TP 2/FP 2/FN 0/TN 0, precision 0.5/recall 1; looking 2 P/7 N/2 U có TP 0/FP 0/FN 2/TN 7, precision null/recall 0. AP 1.0 ở support rất nhỏ không chứng minh operating point hoặc generalization. E002/E003 không test inference mới.

Ba run và pretrained/metrics/checkpoints thật ở outputs với DVC local pointers. Frozen config/approval nằm trong `configs/experiments/` và `docs/experiments/E001-approval.json`/E002/E003; final protocol E001 ở `E001-final-test-protocol.json`. Primary metrics/confusion ở `artifacts/reports/E001|E002|E003/metrics.json`, E001 test riêng `test-metrics.json`; run/code/environment/checksums là authority cho exact reproduction. Không cần Markdown card riêng cho từng lần chạy để biết kết quả trên.

## 3. Phân tích lỗi E003 đã làm và hệ quả

Audit source/crop/input 224 của **46 FN (21 phone/25 looking) và 3 FP validation**, 49 target errors trên 48 ảnh; số lỗi có thể overlap trên cùng crop. Các factors dưới đây là quan sát/hypothesis, chưa kết luận nhân quả hoặc tỷ lệ lỗi toàn dataset.

| Failure mode đã quan sát | Bằng chứng | Hành động hợp lý |
|---|---|---|
| Phone trên bàn/sách | 6/8 phone FN val là desk-phone, 6/8 visually small, 4/8 partial; nhiều pose nghỉ/chống đầu/crowded | Tuyển desk/partial-phone trong primary domain, đi kèm negatives cùng pose/workarea; giữ mobile-presence semantics |
| Phone train vẫn bỏ sót | 13 FN, 12 held-phone, 11 partially occluded, 9 visually small; có auxiliary/non-exam | Không quy mọi lỗi cho unseen source hoặc chỉ hạ threshold; kiểm representation/224 evidence |
| Looking side/context | 7 FN val đều head-side/turn, 5 crowded; 1 cần review đọc sách vs nhìn bên | Review gaze/vùng bài đúng anchor; matched positives/negatives đọc/viết, không mọi turn_head là P |
| Ambiguous/low detail | Looking train 18 FN: 10 low-detail, 8 small-evidence, 9 cần rà label; factors overlap | Tách clear/unknown theo evidence, cải thiện provenance và nguồn trước model lớn |
| FP khó | `V6-EX-042` nghiêng viết,`V6-SB-047` viết/noise score 0.50043,`V6R2-EX-008` cầm bút nhìn bên nhưng phone score 0.72816 | Hard negatives, cả phone N/looking P; không đặt mọi tay gần mặt là phone |

7/8 phone FN val bị downsample ở 224; `P022-person-01` cạnh dài 139 nên upscale. Tăng 384 là hypothesis riêng, chưa ablation và không cứu ảnh gốc thiếu evidence. V7 đã materialize owner decisions của 12 ambiguous/conflict cells; không tự review lại/relabel v6 hoặc coi toàn 375 new train đã có measured targeted slice support.

V7 cải thiện supervision train nhưng chưa có new validation/independence/holdout; gần 69% train vẫn chỉ known một target. Targeted train gain và packaging PASS không là model-quality gain. Các số source/group/pair/224 coverage hiện hành ở [data research](../data-research-20261011/README.md).
