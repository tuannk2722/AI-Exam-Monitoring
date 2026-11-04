# E007 V13 — proposal representation và đối chứng

**Draft, chưa executable/chưa approval implementation scientific hoặc run.** Owner yêu cầu nghiên cứu kỹ và cho biết có thể dùng Colab/GPU cloud, ngân sách khoảng 4–8 giờ. Đề xuất dưới đây là kết quả cụ thể để owner duyệt, không tự thuê GPU/upload/train. [Evidence và audit](../../../artifacts/reports/e007-v13-research-20261023/README.md); [config thiết kế](proposal.yaml).

## 1. Lựa chọn đề xuất

Ưu tiên **tier 8 giờ**, tối đa 5 screening + 4 confirmation runs. Challenger chính: DINOv2 ViT-S/14 với input 336, MLP 128, frozen và mở hai transformer blocks cuối sau 3 epoch head-only. ResNet18 trên V13 là đối chứng; không warm-start E006.

Lý do chọn hướng: V13 đã thay đổi policy/known supervision mạnh; cần baseline mới trước. Thử representation khác pretrained ResNet18 có khả năng tìm thêm gain mà không cần invent nhiều modules/loss. DINO frozen kiểm representation; DINO partial kiểm adaptation. Không có benchmark V13 chứng minh DINO sẽ thắng; tên model mới không là nghiệm thu.

## 2. Ma trận và biến cố định

| Arm | Encoder / input | Phần học sau warmup | Erasing | Contrast |
|---|---|---|---|---|
| R0 | ResNet18 ImageNet V1 / 224 | layer4.1 + head | 0,15 | Mốc recipe E006 cập nhật SQRT theo V13; không tái lập E006 vì data/platform/protocol mới |
| R1 | Như R0 / 224 | Như R0 | 0 | R1−R0 kiểm erasing |
| R2 | Như R1 / 336 | Như R1 | 0 | R2−R1 kiểm resolution |
| D0 | DINOv2 `dinov2_vits14` / 336 | Head only cả run | 0 | Challenger representation; so R2 là package model/scope, không causal effect riêng pretraining |
| D1 | Như D0 / 336 | Blocks 10,11 (0-based) + final norm + head | 0 | D1−D0 kiểm partial adaptation, cùng initial state/head/data order/augmentations |

Các arms không phải nối tiếp checkpoint; D0/D1 bắt đầu cùng pretrained và random head đã pin theo seed. R0/R1/R2 chia sẻ initial head cùng seed. Không dùng best D0 chọn bằng val rồi gọi D1 là đối chứng độc lập. Head warmup 3 epoch, không ramp LR trong warmup; D1 unfreeze từ epoch 4 với LR backbone 1e-5 rồi cosine. Heuristic LR này cần smoke finite/compute, không được tune bằng smoke metrics.

Biến chung: target order `[phone_use, looking_around]`; manifest train/val đúng V13; batch 16, uniform permutation không drop; AdamW head LR 3e-4, weight decay 0,01; max 12 epochs, patience 6, min_delta 1e-4; cosine sau warmup, min LR ratio 0,1. R0–R2 layer4.1 LR 3e-5; BN eval. MLP `LayerNorm → Dropout(0,3) → Linear(d,128) → GELU → Dropout(0,3) → Linear(128,2)`.

Loss giữ global-known normalized masked BCE, smoothing đối xứng 0,05, pos_weight `[1,4142135623730951; 2,280595825313147]` từ train. Việc giữ loss là chủ đích để không trộn representation study với loss study; chưa tuyên bố smoothing/weighting là tối ưu. Không focal/ASL/oversampling/EMA/MixUp/CutMix ở matrix này.

Preprocess RGB full-context letterbox bilinear, fill `[124,116,104]`, ImageNet mean/std như hiện tại. DINO input 336 chia hết patch 14; không dùng default center-crop làm mất context. Đây là adaptation preprocess được đề xuất, phải có parity tests; không nói giống toàn bộ official inference recipe. Features DINO = normalized CLS + mean normalized patch tokens, 768 chiều; không pool registers (bản này không registers), không lấy ImageNet classifier logits. No-grad frozen prefix nhưng các blocks được mở phải nhận gradient; train/eval và stochastic-depth policy explicit, đề xuất stochastic depth 0.

Augmentation giữ implementation hiện tại: hflip 0,5, brightness/contrast 0,15, saturation 0,1; box jitter 0. Erasing chỉ R0. Không spatial jitter/rotation/hue mới. D0 frozen vẫn tính features theo augmented images từng epoch; không cache một vector cố định rồi vô tình bỏ augmentation. Cache decoded uint8 có key data/transform; tách cohort instances theo config.

## 3. Selection, calibration và confirmation

Trong mọi arm: chọn **một checkpoint đầy đủ** bằng max val macro AP; tie min raw masked BCE; tie tiếp epoch sớm. Min_delta chỉ cho early stopping. Lưu AP từng target trong history để phân tích nhưng không lấy best khác epoch cho mỗi target. Calibration chỉ một lần trên val của checkpoint đã chọn; thresholds áp sang train/slices và reload evaluator.

Đề xuất exact PR breakpoints, ties là một nhóm, score decision ≥ threshold. Xét đủ score trong [0,1], endpoints/all-positive/all-negative bằng policy tường minh của schema mới, không clip scores hoặc dựa vào grid. Không có predicted positive thì precision null, không fake PASS. Giữ thứ tự chọn threshold: feasible 80/80/20 → F1 lớn nhất → biên nhỏ nhất giữa các gate lớn nhất → gần 0,5 → threshold thấp nhất; khi không feasible dùng min tổng shortfall rồi F1/gần 0,5/threshold thấp nhất. Tie policy phải được freeze trước run; không sửa evaluator lịch sử.

Chọn champion screening theo: cả hai target pass gates → số target pass → tổng gate shortfall thấp hơn → macro AP cao hơn → BCE thấp hơn → arm ID. Support gates vẫn 30 P/N, ≥5 nhóm P/N; kiểm thực tế từ V13, không hạ gates. Đây là selection development có bias, không holdout. Tất cả candidates dùng cùng protocol, không chọn criterion sau thấy kết quả.

Tier 8: screening seed 20261023; repeat champion và **R0** ở seeds 20261024/20261025 (4 run). Nếu champion = R0, chỉ repeat R0 hai seed; không tự dùng ngân sách thừa để thêm kiến trúc. Báo từng seed và paired deltas với R0; screening seed không phải confirmation độc lập. Không hứa statistical significance với hai seed xác nhận.

Tier 4: chỉ R0/R1/D0 screening và hai seed bổ sung cho champion; không R2/D1 hoặc paired R0 confirmation nếu champion khác R0. Vì thế không kết luận riêng resolution hoặc gain ổn định so R0; D0 so R1 còn thay resolution/representation/scope. Tier phải chốt trước screening, không đổi do thấy metrics.

## 4. Budget và stop rules

| Budget tier | Smoke/benchmark tối đa | Research runs | Cap mỗi run gồm reload/report | Setup/evaluation/recovery reserve | Tổng cap |
|---|---:|---:|---:|---:|---:|
| Khuyến nghị 8 giờ | 45 phút | ≤9 | 40 phút | 75 phút | 480 phút |
| Tiết kiệm 4 giờ | 45 phút | ≤5 | 30 phút | 45 phút | 240 phút |

Các số là **trần đề xuất, chưa đo throughput**, không dự báo số giờ thực tế hoặc giá thuê. Chọn một GPU ≥16 GB VRAM làm target dự kiến, FP32, workers 0; không khóa một GPU type khi chưa biết provider. Compute identity thực tế cần được freeze. Chưa chọn paid service hoặc đồng ý mức phí nào.

Trước research: smoke phải đo full pipeline gồm decode/augmentation/eval/checkpoint, memory peak; kiểm ResNet và DINO adapter, transition, interruption/resume, standalone reload. Synthetic fixtures không tính model-quality. Full-data timing chỉ sau smoke approval. Nếu estimate một run 12 epochs + reload vượt cap hoặc không fit VRAM, dừng nhánh liên quan và đề xuất revision compute/config; **không** giảm batch/resolution, bật AMP, đổi GPU/scheduler hoặc tăng budget âm thầm. Hết global cap thì dừng queue, báo incomplete; không chọn theo kết quả partial rồi gọi campaign hoàn thành.

Đếm thời gian GPU được cấp, kể cả setup/idle/retry/recovery; shutdown GPU sau đồng bộ artifacts đã kiểm. Không chạy song song nhiều GPU. Software preparation thực hiện local trước để tránh đốt giờ thuê. Không tự dùng hết budget nếu evidence không đáng tiếp tục.

## 5. Implementation cần duyệt và kiểm

1. Schema mới cho E007/device/encoder/protocol; dispatch không sửa semantics v1/v2/v3 đã pin. Preparer đọc schema allocation V13 explicit, zero-test chỉ qua exact accepted release/protocol; masks/rights/group guards giữ nguyên. Không gọi campaign_prepare cũ bằng proposal YAML này.
2. GPU plumbing và runtime/checkpoint contract: actual device, CUDA/cuDNN/GPU model, torch/torchvision build, backend flags, RNG CPU/CUDA, optimizer device, atomic epoch boundary, full bundle và standalone reload. FP32 + deterministic policy cụ thể; reject unsupported kernels thay vì silent fallback. Same-environment resume test, không hứa cross-platform bitwise.
3. Encoder adapter DINO pinned source/weights/license; support `weights=None` + local state load, không remote code/latest network download lúc train. Generalize head feature dim, param groups và freeze policy; test tên tham số + gradients + mode. ResNet historical behavior giữ nguyên.
4. Calibration val-only và exact thresholds phiên bản mới; test missing P/N, unknown, ties, 0/1 boundaries, empty predictions, fixed-pair source/slices, và threshold reuse từ train/report/evaluator.
5. Provenance sidecar pinned, upstream unknown giữ unknown; separate generated21 slice chỉ train, small-anchor/native-size val slices có support rõ. Không gọi proxy crop area là people count; không mutate release.
6. Tests thích hợp theo development: Ruff/mypy, training/config/loader/preprocessing/evaluator/campaign fixtures; zero-test regression và legacy preservation. Smoke thật kiểm transition/resume/reload trên actual GPU sau exact config approval. Không fake PASS receipt để qua gate.

Không cần sửa system/training/data spec cho kết quả nghiên cứu này. Nếu implementation cần contract public mới, quyết định/schema được freeze trong thiết kế revision đã approve, cập nhật reference đúng API sau triển khai.

## 6. Owner cần chốt để đi tiếp

- **Thiết kế:** duyệt hướng DINOv2-S frozen/partial + matrix và metric policy ở trên, hoặc chọn ConvNeXt-Tiny thay DINO (cần revision rõ). Đề xuất tier 8 giờ; tier 4 nếu muốn thu hẹp.
- **Cloud scope:** provider/GPU/private storage nào, và quyền đưa đúng V13 lên môi trường đó. Accepted release chỉ có `local_classifier_research`; không tự suy quyền upload từ việc cân nhắc cloud. Có thể duyệt implementation trước, giữ upload/run đóng.
- **Exact execution sau implementation:** pin revision/weights SHA/license, Linux CUDA environment, protocol/cohorts/configs/seed/budgets và smoke/run action. Không dùng placeholder SHA hoặc tự viết owner approval khi chưa có lời duyệt.

Yêu cầu xác nhận này đến từ [AGENTS](../../../AGENTS.md) (không tự chốt pretrained/training variables) và [training contract §3](../../../docs/training.md) (proposal không cấp implementation scientific/run/test). Công việc nghiên cứu đã được phép vẫn hoàn tất ở report/config Draft; không yêu cầu owner duyệt một ý tưởng chưa có artifacts cụ thể.
