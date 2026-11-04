# Nghiên cứu E007 trên V13 — 23/10/2026

**Khuyến nghị: giữ V13, khởi tạo sạch, nâng representation có đối chứng; chưa có bằng chứng bảo đảm một config sẽ tạo đột phá.** Với ngân sách owner nêu 4–8 giờ GPU, ưu tiên DINOv2 ViT-S/14 frozen và fine-tune hai block cuối, đối chiếu ResNet18 ở 224/336 và random erasing. Không triển khai đồng thời kiến trúc ROI, focal loss, sampler mới và selection mới. [Proposal và config Draft](../../../configs/experiments/E007-V13-20261023/README.md) là đầu ra để review; chưa là config executable hoặc approval.

## 1. Phạm vi và độ tin cậy

Đọc contracts/index/status/decisions, configs và báo cáo E001–E006, các nhánh E004 RC1/C345, E005, diagnostics E006, release V13, code loader/model/preprocess/loss/train/evaluate/campaign. Đối chiếu source tại Git `baafc41e163d984a948e5974aa9581668f73d7f7`; source không sửa trong nghiên cứu. Tính lại metadata V13, delta cùng ID và threshold envelope từ predictions đã lưu của sáu run E006 SQRT/RATIO. Kiểm SHA predictions/history theo checksums của run. Không load checkpoint, forward model, train, tải weights, upload media hoặc mở historical test.

- [Metadata audit](metadata-audit.json): counts/groups, source provenance, geometry proxy, kích thước từ metadata, overlap và input SHA.
- [Cached scores và delta](cached-score-and-delta-audit.json): transitions, cùng crop/cùng known-label denominator, AP tính độc lập bằng tổng precision tại từng nhóm score bằng nhau, exhaustive observed-score thresholds.
- [Synthetic checks](synthetic-checks.json): unknown có gradient 0; counterexample cho calibration giới hạn miền.
- [Đối chiếu bản kế hoạch ngoài repo](external-plan-review.md): bản Markdown đang mở trong Downloads có một số nhận định đúng nhưng nhiều số liệu/diễn giải cần sửa; không dùng làm approval.

Không audit lại toàn bộ ảnh bằng mắt. Kích thước không đo kích thước điện thoại/khuôn mặt; area ratio không đếm người. Group là nhóm leakage bảo thủ, không phải số camera/session độc lập. Kết quả lịch sử trên cohort khác nhau không tạo thành đường tiến bộ cùng benchmark.

## 2. Lịch sử thực sự nói gì?

| Thí nghiệm | Dữ liệu train / development | Kết quả và bài học |
|---|---|---|
| E001, V4 | 60 / 13 | Frozen ResNet18 + linear; macro AP 0,9273 nhưng looking recall 0 tại 0,5; support rất nhỏ |
| E002, V5 | 80 / 13 | Cùng val 13, AP 0,9809 nhưng BCE xấu hơn E001; ranking tốt không bảo đảm operating point |
| E003, V6 | 317 / 50 | AP 0,7878; không so trực tiếp với val 13 |
| E004 V9 | 716 / 71 | LP 0,5754; layer4 0,5412; fine-tune overfit rất nhanh |
| E004 RC1 | 716 / 71 | Warm head + LR cao tốt nhất matrix: AP 0,6076; giảm LR đơn thuần không giúp |
| E004 C345 | 1.061 / 71 | AP 0,6005; phone recall tăng nhưng FPR lên 84,85%; thêm ảnh không tự tạo generalization |
| E005 V11 | 1.185 / 266 | S1-AUG 0,7378, phone AP 0,8161 / looking 0,6595; dual ROI 0,7119, best trước unfreeze |
| E006 V12 | 1.092 / 204 | SQRT mean AP 0,6823 ± 0,0100; RATIO 0,6815 ± 0,0085; không qua đồng thời quality gates |

Nguồn: [baseline](../baseline-review-20261011/README.md), [E004 nguyên nhân](../E004-root-cause-20261014/README.md), [RC1](../E004-RC1-execution-20261014/README.md), [C345](../E004-train-enrollment-20261016/README.md), [E005](../e005-v11-adaptation-20261018/README.md), [E006 review](../e006-v12-20261020/README.md). Sáu mã experiment không phải sáu lần fine-tune nối tiếp; E004–E006 còn gồm nhiều arms.

E006 train AP cuối khoảng 0,964–0,970 trong khi best val khoảng 0,673–0,693; best epoch 5–7. Đây là dấu hiệu overfit/khác biệt train–development, chưa xác định riêng cơ chế shortcut hay lỗi nhãn. Không có lý do mặc định tăng epochs, mở toàn backbone hoặc tiếp tục tìm pos_weight trên nhiều seed. SQRT–RATIO mean chênh 0,00081 quá nhỏ để gọi là bước tiến chắc chắn.

Kiểm exhaustive threshold trên sáu runs xác nhận **cả 12 cặp run–target đều không có điểm đạt 80/80/20** trên V12. Với SQRT seed 20261020, precision cao nhất khi recall ≥ 80% chỉ 63,27% phone và 53,06% looking. Như vậy vấn đề không chỉ ở ngưỡng 0,5 hay grid calibration.

## 3. V13 thay đổi bài toán

| Split / target | P / N / U | Nhóm P / N / U |
|---|---|---|
| Train phone | 342 / 684 / 93 | 96 / 157 / 21 |
| Train looking | 179 / 931 / 9 | 74 / 207 / 7 |
| Val phone | 55 / 120 / 10 | 38 / 59 / 7 |
| Val looking | 33 / 152 / 0 | 21 / 82 / 0 |

Train 1.119 crop/239 nhóm; val 185 crop/92 nhóm; test 0. Không overlap ID, crop SHA, canonical source SHA hoặc group đã biết giữa train và val. Các nhóm P/N/U chồng nhau. Không diễn giải overlap bằng 0 thành độc lập nguồn vì exact parents của 21 ảnh generated chưa rõ.

Trên **890 ID giữ vai trò train**, phone có 71 U→P và 156 U→N; looking có 147 P→N. Trên **167 ID giữ vai trò val**, looking có 27 P→N và 1 N→P. Đó là delta theo quyết định audit, không tự chứng minh tất cả nhãn cũ là lỗi annotation thay vì thay đổi ranh giới policy. Nhãn/policy accepted của V13 được giữ.

167 ID val chung chỉ có **166 crop SHA không đổi**. Trên cùng 166 crop và cùng known looking labels, dùng nguyên scores E006 SQRT seed 20261020: AP theo nhãn V12 là 0,65017; theo nhãn V13 là 0,22707. Đây là **sensitivity với nhãn**, không phải E006 evaluation đầy đủ trên V13, không phải kết quả train E007. Phone so sánh cùng known subset chỉ có 116 crop và giữ AP 0,78520. Không trộn subset này với AP phone 0,72209 trên đầy đủ V12 val. Kết quả ủng hộ khởi tạo sạch từ pretrained, không warm-start checkpoint E006 đã học policy cũ.

Weighting train-only nếu dùng SQRT: `[sqrt(684/342), sqrt(931/179)] = [1,4142135624; 2,2805958253]`. Không dùng tỷ lệ validation; không bê `[1,56; 1,48]` sang V13 rồi gọi là SQRT của V13. Đây là recipe tham chiếu được đề xuất, chưa chứng minh optimum.

### Precision là ràng buộc chặt hơn FPR 20%

Với P/N cố định, điều kiện chính xác là `TP ≥ ceil(0,8 P)` và `FP ≤ min(floor(TP/4), floor(0,2 N))`.

- Phone: TP ≥ 44; tại TP = 44 cho phép FP ≤ 11 (FPR ≤ 9,17%); tại TP = 55 có thể FP ≤ 13.
- Looking: TP ≥ 27; tại TP = 27 cho phép FP ≤ 6 (FPR ≤ 3,95%); tại TP = 33 có thể FP ≤ 8.

Không đổi gate thành FPR cố định 3,95%/9,17%. Một lỗi FN looking tương đương 3,03 điểm phần trăm recall. Support toàn val đạt mức 30 P/N và 5 nhóm P/N lịch sử, nhưng chỉ 33 looking P nên ước lượng còn nhạy; seed khác nhau không tạo validation độc lập.

### Coverage còn hạn chế

- Nhóm train lớn nhất có 367/1.119 crop (32,8%) và 118/342 phone P (34,5%). Không tự inverse-group sampling: nhóm này là quarantine bảo thủ, không nhất thiết một scene. Sampling mới còn thay đổi objective vốn giả định uniform permutation.
- Sau nối **exact upstream provenance**, owner part02 train vẫn 0 phone P / 23 N / 3 U, val 7 P / 31 N / 1 U; part05 train 0 P / 45 N / 3 U, val 2 P / 5 N. Không gán 136 new train thiếu exact upstream source về các nguồn này chỉ bằng visual similarity, nên counts chỉ mô tả phần truy được nguồn.
- 149 NEW records thiếu exact upstream source: 136 train / 13 val. Trong đó **21 ảnh được xác nhận generated đều ở train**. Không gọi toàn bộ NEW là ảnh generated; phần còn lại có visual lineage với mức evidence riêng.
- Canonical `source_id` của cả 1.304 crop là bundle `reviewed-crop-inputs-20261023`. Báo cáo theo source hiện tại sẽ chỉ có một hàng. Cần sidecar pinned provenance/slice enrollment, không sửa accepted manifest.
- 719/1.119 train và 131/185 val có cạnh dài > 224; 481 train/87 val > 336. Median cạnh dài 293/324. Có căn cứ **thử** 336 để giảm downsampling; không bảo đảm cue nhỏ còn tồn tại. Pixel budget 336²/224² = 2,25; không suy latency cũng đúng 2,25 lần.
- 348 train/48 val có anchor/context area < 0,70. Gọi là `small_anchor_fraction`, không gọi 31,1% ảnh đa người đã xác minh.

## 4. Audit implementation: giữ gì, sửa gì?

| Phát hiện | Evidence code | Hướng E007 |
|---|---|---|
| Mask/target order và BCE logits đúng ở đường đã đọc; synthetic unknown gradient = 0 | `adaptation_metrics.minibatch_loss`, `data.labels`, `metrics` | Giữ global known normalization; không ép U thành N |
| GPU chưa được thực thi dù parser nhận cuda/auto; environment hard-code cpu; checkpoint RNG thiếu CUDA | `adaptation_train.infer/train_images`, `artifacts.environment`, `train.rng_state/restore_rng`, `adaptation_evaluate` | Bắt buộc device transfer model/batch/targets/masks/support, RNG CUDA, optimizer-state restore, environment GPU/CUDA/cuDNN và evaluator tương ứng; fail nếu GPU yêu cầu không có |
| Preparer chỉ đọc allocation `assignments/role/group`, V13 dùng `rows/split/group_id` | `campaign_prepare.prepare` | Adapter schema explicit + verify exact membership/approval, không heuristic đoán keys |
| Preparer copy reservation 11 test từ parent rồi kiểm đúng test ID set; V13 test rỗng nên không chạy nguyên xi | `campaign_prepare.prepare` | Protocol mới zero-test chỉ khi release approval/status đúng; historical protocols không sửa; không dùng điều kiện số test = 0 đơn độc để bỏ guard |
| Readiness v2 yêu cầu waiver fields lịch sử; không tự tương đương với approval V13 | `adaptation_data._waiver/validate_readiness` | Freeze research scope/limitations đúng E007; không fabricate waiver hoặc independence PASS |
| Calibration đang fit trên từng cohort, kể cả train, dù tên flag là `calibrate_thresholds_on_val` | `adaptation_train.cohort_report`, caller loop trong `run_adaptation` | Fit một lần trên selection, reuse pair cho train/slices/evaluator; E006 val không bị chứng minh sai bởi lỗi naming/scope này |
| Candidates chỉ xét scores trong [0,05; 0,95] cộng grid | `adaptation_metrics.calibrate_optimal_thresholds` | Exact score breakpoints với ties/biên/saturated score policy rõ, giữ null precision khi không dự đoán positive; synthetic example bỏ lỡ perfect ranking dưới 0,05; không giúp sáu E006 đã kiểm |
| Best epoch dùng macro AP rồi BCE; unweighted BCE history khác weighted smoothed objective | `adaptation_train.train_images` | Giữ selection để đối chứng, đặt tên diagnostics rõ; báo AP từng target, gate shortfall tại checkpoint đã chọn; không đổi selection hậu nghiệm |
| Single-crop bỏ qua explicit anchor coordinates | `adaptation_model.forward/_extract_backbone_features` | Attribution là limitation thật; ROI là nhánh nghiên cứu sau nếu lỗi còn tập trung ở small-anchor slice, chưa chứng minh là nguyên nhân chính |
| Backbone hard-code ResNet18 và prefix no_grad; không thể đổi tên config thành ViT/ConvNeXt hoặc mở layer3 | `adaptation_model`, whitelist `adaptation_config` | Adapter encoder/head/policy riêng có tests; freeze modes và optimizer groups kiểm từng tên; giữ behavior legacy |
| Cache transform keyed chỉ theo sample index trong cohort object | `ImageCohort._ensure_cached` | Mỗi config/cohort mới hoặc key transform digest; không reuse object/cache giữa 224 và 336 |
| Jitter không gian chỉ ở dual branch; E006 box_jitter = 0 từ đầu | `adaptation_data.model_batch`, E006 YAML | Đây không là bug làm mất augmentation đã yêu cầu; spatial augmentation mới cần ablation/geometry QA, không gọi là fix nguyên nhân overfit |
| Dual anchor crop lấy từ native context PIL trước letterbox, không từ tensor context 224 | `ImageCohort._ensure_cached`, `data.extract_anchor_subcrop` | Không quy thất bại dual-ROI cho double resize mặc định; upstream derivative có thể đã resize nhưng phải kiểm riêng |

Random erasing hiện chọn mỗi cạnh dưới S/4; diện tích vùng xóa tối đa xấp xỉ **6,25%**, không 25%. Vùng nhỏ vẫn có thể che cue quan trọng; diagnostics đã có ví dụ che đầu. Vì vậy đối chứng p = 0 so với 0,15 hợp lý, chưa chứng minh nguyên nhân.

Smoothing đối xứng kết hợp positive weight làm tối ưu độc lập cho negative thành `p* = wε/(1−ε+wε)` với ε = 0,025: khoảng 0,0350 phone và 0,0552 looking cho SQRT V13. Đây là ảnh hưởng score scale; **không đồng nghĩa FPR** ở threshold đã fit tăng tới giá trị đó. Focal/ASL thay đổi ưu tiên gradient, không bảo đảm hard negatives được phân biệt hoặc precision tăng. Chưa có cơ sở đưa cả focal, positive-only smoothing và weighting mới vào main run rồi quy gain cho một yếu tố.

## 5. Hướng nghiên cứu ưu tiên

**DINOv2 ViT-S/14 là challenger ưu tiên, không phải winner đã biết.** Lý do: E001–E006 đều xoay quanh ImageNet ResNet18; representation pretrained bằng self-supervision trên dữ liệu đa dạng là một trục thay đổi thực chất. Frozen probe giúp kiểm representation với ít tham số học; fine-tune hai block cuối kiểm xem adaptation có giúp hay lại overfit. Paper DINOv2 báo khả năng chuyển đặc trưng trên nhiều image/pixel tasks, không có benchmark V13. [Paper gốc](https://arxiv.org/abs/2304.07193).

Official repo có ViT-S/14 khoảng 21 M tham số, weights backbone và bản có/không registers; code/weights DINOv2 thường dùng Apache-2.0. Đề xuất đúng `dinov2_vits14` không registers; không dùng pretrained ImageNet classifier head, không suy license sang các model chuyên ngành cùng repo. Phải pin revision/weights SHA và lưu license trước chạy. [Official repo](https://github.com/facebookresearch/dinov2). Feature đề xuất: normalized CLS 384 + mean normalized patch tokens 384, head MLP 768→128→2; 336 chia hết patch 14 tạo lưới 24×24. Đây là thiết kế E007, không giữ nguyên toàn bộ evaluation recipe của paper. [Encoder API](https://github.com/facebookresearch/dinov2/blob/main/dinov2/models/vision_transformer.py).

| Phương án | Quyết định đề xuất trong 4–8 giờ |
|---|---|
| ResNet18 224/336 và erasing ablation | Cần làm mốc cùng V13, rẻ và dễ giải thích |
| DINOv2-S frozen / last two blocks | Ưu tiên thử representation mới; không dùng model lớn/full fine-tune mặc định |
| ConvNeXt-Tiny ImageNet1K V1 | Alternative nếu owner ưu tiên torchvision-only; không cộng thêm tự động vào matrix. Official model có khoảng 28,6 M tham số, pretrained recipe riêng; ImageNet accuracy không dự báo V13. [Torchvision 0.23](https://docs.pytorch.org/vision/0.23/models/generated/torchvision.models.convnext_tiny.html) |
| DINOv3 | Có implementation/weights mới nhưng license riêng và thêm điều kiện truy cập/pinning; chưa cần đổi hướng chỉ vì mới hơn. [Official repo](https://github.com/facebookresearch/dinov3) |
| ROI pooling / task-specific heads | Hợp lý để kiểm attribution, nhưng chưa là lựa chọn đầu khi representation cũ chưa có đối chứng mới; cần letterbox coordinate tests và context cho phone trên bàn |
| Focal/ASL, group sampler, MixUp/CutMix | Hoãn; ASL được đề xuất cho imbalance multi-label nhưng không tự giải quyết 2-label V13 và masks/attribution. [ASL paper](https://arxiv.org/abs/2009.14119) |
| Detector phone / pose / gaze / temporal model | Không đủ annotations/protocol hiện tại; mở task riêng nếu error evidence đòi hỏi, không thay looking bằng gaze label hoặc suy thời lượng từ ảnh tĩnh |

Nghiên cứu LP-FT cho thấy fine-tune có thể làm giảm OOD performance so với probe khi shift lớn; điều đó hỗ trợ giữ frozen control, không chứng minh V13 đang gặp đúng cơ chế ấy. [Paper LP-FT](https://arxiv.org/abs/2202.10054).

DINO global features vẫn không nhận explicit person_box; đổi encoder không tự giải quyết attribution. Mean patch pooling còn bao gồm vùng padding của letterbox. Đây là trade-off của matrix nhỏ để kiểm representation trước; nếu small-anchor errors không giảm thì ROI-guided pooling là follow-up có căn cứ hơn, không tuyên bố DINO đã thay thế được nó.

## 6. Điều kiện thực thi và đánh giá

Chi tiết numbers, arms, budgets và câu hỏi owner ở [proposal](../../../configs/experiments/E007-V13-20261023/README.md). Mặc định khuyến nghị tier 8 giờ để giữ đối chứng và xác nhận paired seeds; tier 4 giờ thu hẹp câu hỏi, không hứa giải đáp resolution và fine-tune cùng lúc.

CUDA support phải kiểm interruption/resume trên **cùng environment**, không hứa bitwise CPU↔GPU hoặc GPU khác nhau. PyTorch không bảo đảm reproducibility giữa platform/release; seed chưa đủ. [PyTorch 2.8 reproducibility](https://docs.pytorch.org/docs/2.8/notes/randomness.html). Đề xuất FP32 đầu tiên để giảm biến; AMP chỉ revision đã approve và có scaler/checkpoint/finite-step tests, không tự bật để cứu OOM. [PyTorch AMP](https://docs.pytorch.org/docs/2.8/notes/amp_examples.html).

Manifest hiện chỉ cho `local_classifier_research`; lựa chọn GPU cloud chưa đồng nghĩa quyền chuyển 1.304 ảnh lên dịch vụ cụ thể. Cần owner chốt provider/private storage/use scope trước upload; không sửa accepted manifest để bypass guard. Có thể hoàn thiện implementation/software fixtures trước khi có quyền upload.

Đánh giá giữ toàn bộ val 185, masks và gates; báo fixed 0,5 và val-calibrated, AP/BCE/TP/FP/FN/TN, source slices từ provenance, small-anchor và native-size slices, intervals theo group với thresholds cố định. CI development sau selection/calibration vẫn optimistic; không đổi thành holdout. Không hard-negative mine từ val rồi thêm vào train. Không tự bỏ 21 generated hoặc đổi allocation. Nếu cần holdout độc lập, làm nguồn/protocol riêng; không phải điều kiện để thiết kế E007, nhưng là giới hạn của kết luận generalization.

Thành công nghiên cứu phải phân biệt: ranking/gate cải thiện cùng cohort, ổn định qua seed và hạn chế theo nguồn; **FINISHED không Selected**. Nếu DINO frozen không giúp và fine-tune tăng train nhưng không tăng val, dừng tìm hyperparameters rộng; dùng errors để xác định attribution/cue/domain rồi mới chọn ROI/data follow-up. Không tuyên bố có đột phá trước khi chạy.
