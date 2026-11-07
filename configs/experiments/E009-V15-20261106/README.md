# E009 V15 — Training trên Colab Pro

**Campaign đã FINISHED; xem [kết quả audit ngày 07/11](../../../artifacts/reports/e009-v15-colab-20261106/results-20261107.md). Không Run all hoặc resume campaign đã hoàn tất.** Hồ sơ bên dưới giữ thiết kế/approval và launcher đã dùng; không tự cấp quyền run thêm, test hoặc promotion.

**Owner đã approve phương án và yêu cầu thực hiện ngày 06/11/2026.** [Authorization](owner-authorization.json) pin đúng proposal đã review; proposal giữ nguyên bytes và chữ Draft như snapshot trước approval. Trần **12 giờ GPU**, không ép dùng hết. Owner chọn tự upload/chạy notebook như E008; actual GPU smoke/research chưa chạy trong workspace local.

[Variables/protocol đã duyệt](proposal.yaml) giữ ma trận/số liệu cấu hình; [audit metadata V15](data-audit.json) là snapshot tính lại bằng codec. [Execution design và exact input pins](execution-design.json) cùng [sidecar enrollment](enrollment.json), [provenance thực thi](provenance-execution.json) nối dataset V15 với preparer. Scope mở implementation, private Colab/Drive và smoke/research theo proposal; test/promotion và thay model prototype giữ đóng. Source chưa commit/push trong task này.

Execution design supersede [design ban đầu](design.json) ở phần metadata origin: sửa tag của 26 crop val cũ đã chuyển sang train thành `old_val_moved_to_train`. Giữ nguyên cả bản đã pin; [receipt](../../../artifacts/reports/e009-v15-colab-20261106/sidecar-revision.json) đối chiếu đủ 1.721 record. Nhãn, split, nhóm, bytes V15 và recipe không đổi. Archive ban đầu chưa upload, đã được thay bởi execution bundle dưới đây.

## Cách chạy

**Notebook hiện tại dành cho recovery campaign đã dừng ngày 07/11.** Owner đã duyệt [ngoại lệ budget](recovery-authorization-20261107.json): 45 phút/research run, giữ tổng 720 phút/pool research 500 phút. Giữ execution bundle đã upload. Để tiếp tục, giữ `RESUME = True`, xác nhận runtime cũ dừng rồi đặt `OLD_RUNTIME_STOPPED = True`, dùng A100-SXM4-80GB/cùng environment và Run all. Không chạy lại sáu smoke; extension kiểm bytes/parity/reload rồi mở research. Notebook chứa extension/authorization có SHA riêng; package tạo checkpoint không đổi. Hạn tổng gốc 13:33:15 ngày 07/11/2026 giờ Việt Nam; không reset. Các bước bên dưới mô tả launcher ban đầu, không dùng `RESUME = False` với campaign đang có.

1. Upload **[e009-colab-execution-bundle.zip](../../../outputs/E009-V15-Colab-20261106/e009-colab-execution-bundle.zip)** vào **My Drive/E009/**, giữ private; hoàn tất upload trước khi cấp GPU. Notebook chỉ nhận đúng execution bundle đã pin.
2. Upload [E009-V15-Colab.ipynb](../../../notebooks/E009-V15-Colab.ipynb) lên Colab, chọn GPU mạnh nhất khả dụng. Kernel Python 3.13 được hỗ trợ để điều phối: notebook tự cài CPython 3.12.12 riêng bằng uv 0.9.7 cho launcher/train. High RAM tùy nhu cầu/cấp phát; không cần đổi kernel hoặc cài ML thủ công vào kernel. ZIP hiện tại giữ nguyên.
3. Giữ `RESUME = False`, bấm **Run all**, mount đúng Drive. Notebook kiểm SHA bundle và từng member, tạo environment riêng, rồi gọi canonical campaign. Profile full/core chọn từ VRAM trước training; đừng sửa YAML hoặc chạy arm thủ công.
4. Output tại **My Drive/E009/E009-V15-COLAB-20261106/**. Epoch recovery, head initialization, configs, best/last và source bundle được giữ private. Notebook in đường dẫn ZIP **E009-V15-results-metadata-<attempt timestamp>.zip** sau lượt chạy; tải ZIP đó về để audit. ZIP metadata không chứa checkpoints.
5. Khi hoàn tất hoặc lỗi, notebook gọi `runtime.unassign()` để ngắt tài nguyên. Nếu phiên chết trước export, giữ folder campaign/recovery và setup logs; không Run all như campaign mới.

Để recovery sau khi đã xác minh runtime/process cũ dừng: dùng **đúng notebook/bundle**, bật `RESUME = True` và `OLD_RUNTIME_STOPPED = True`. Launcher đọc journal và manifest đã commit, giữ original timestamp; runner chỉ khôi phục bytes đã verify và bỏ qua run FINISHED đã kiểm. GPU/environment khác, thiếu checkpoint, divergent local output hoặc hết budget đều dừng; không xóa folder/đổi hash để qua. Giữ cùng runtime version; environment closure đầu tiên được pin để dựng lại môi trường khi cần. Lượt setup bị ngắt chưa có receipt hoàn chỉnh cần giữ logs và review, không reset journal.

[Handoff local và giới hạn kiểm](../../../artifacts/reports/e009-v15-colab-20261106/README.md) phân biệt software/preflight với actual GPU smoke và kết quả model.

## 1. Evidence và lựa chọn kỹ thuật

- [E007](../../../artifacts/reports/e007-v13-colab-20261024/README.md): DINOv2-S finetune hai block cuối vượt frozen DINO và ResNet18 trên cùng V13. D1 mean macro AP 0,8429 so với R0 0,5335. Đây là cơ sở chọn representation hiện hành, không dùng để dự báo điểm V15.
- [E008](../../../artifacts/reports/e008-v14-colab-20261024/results-20261025.md): G0 global pooling thắng G1/A1 spatial; mean macro AP G0 0,9152, looking recall cả ba seed là 23/29. Best epoch 8–10, dừng sớm ở 14–16 trong cap 24. Giữ G0 làm baseline, chưa có cơ sở ưu tiên thêm spatial pooling hoặc kéo hàng trăm epoch.
- [V15](../../../artifacts/reports/dataset-merge-20261106/README.md) đã đổi membership/split và bổ sung các ca khó. 197 crop từng ở train lịch sử nay thuộc val. Mọi arm E009 phải bắt đầu từ pretrained gốc + head mới + optimizer mới; kể cả checkpoint screening E009 cũng không dùng làm initialization cho arm hoặc seed khác.
- DINOv2-B là đối chứng representation lớn hơn trong cùng họ model: khoảng 86 M tham số so với S khoảng 21 M; upstream công bố kết quả transfer tốt hơn trên một số benchmark. Đây là **giả thuyết cần kiểm trên V15**, không bảo đảm model lớn hơn sẽ tốt hơn. Dùng bản LVD142M không registers, không lấy ImageNet classifier head. [README/model card chính thức](https://github.com/facebookresearch/dinov2/blob/main/README.md), [model card](https://github.com/facebookresearch/dinov2/blob/main/MODEL_CARD.md).
- Tăng 336 → 448 cho grid patch 24 × 24 → 32 × 32. Có 786 crop train và 171 crop val có cạnh dài native > 336; có cơ sở thử giữ thêm chi tiết đầu/thiết bị trước tokenization. 84 crop val có cạnh dài ≤ 224 và 44 crop có cạnh ngắn < 120; tăng resolution không khôi phục evidence đã thiếu. DINO hỗ trợ kích thước chia hết cho 14 theo model card, còn lợi ích thực tế phải đo.

Không đưa DINOv3, ViT-L/G, full-backbone finetune, MixUp/CutMix, random crop/erasing, ensemble hoặc TTA vào ma trận này. DINOv3 cần tích hợp và quyết định nguồn/license riêng; model lớn/đa lượt tăng chi phí inference; các phép trộn/xóa ảnh có thể làm mất attribution hoặc cue phone/head. Chưa có evidence để ưu tiên chúng thay các đối chứng có thể giải thích bên dưới. [DINOv3 upstream](https://github.com/facebookresearch/dinov3), [license riêng](https://github.com/facebookresearch/dinov3/blob/main/LICENSE.md).

## 2. Dữ liệu và loss

Giữ V15 nguyên bytes, nhãn, group và split; không tạo V16 hoặc chia lại để nâng metric. Val là development đã dùng chọn epoch/recipe/ngưỡng, không phải independent holdout. Không có test trong package.

| Split | Crop / nhóm | Phone P / N / U | Looking P / N / U | Nhóm P / N của looking |
|---|---:|---:|---:|---:|
| Train | 1.377 / 219 | 397 / 896 / 84 | 323 / 1.046 / 8 | 70 / 194 |
| Val | 344 / 119 | 100 / 223 / 21 | 81 / 261 / 2 | 41 / 104 |

Phone val có 52 nhóm P / 72 nhóm N. Cả hai target đã đủ support theo gate lịch sử: ≥ 30 P/N và ≥ 5 nhóm P/N; điều này chỉ làm gate có thể tính, không làm kết quả độc lập. Unknown giữ mask 0. Prevalence baseline và class weights chỉ tính từ train known positions.

Giữ Balanced Smoothed BCE hiện hành, smoothing 0,05; SQRT pos weights V15 là **[1,502307209641576; 1,7995527480124769]** theo thứ tự phone/looking. Không giữ weights V14 hoặc tính từ val. Loss chuẩn hóa theo known support toàn train cho từng target, rồi trung bình hai target; batch thiếu known ở một target đóng góp 0 cho target đó, không biến U thành N.

Sampling vẫn là permutation mỗi epoch, không replacement. Nhóm train lớn nhất 367 crop, khoảng 26,65%; 252 imports và 74 generated kế thừa đều train-only. Giữ diagnostic theo nguồn/family, không tự inverse-weight theo leakage group: nhóm này là ranh giới bảo thủ, không phải số quan sát độc lập đã xác minh. Không hard-mine val errors vào sampler hoặc bỏ crop owner đã chọn.

## 3. Ma trận đề xuất

Mỗi run dùng CUDA FP32, TF32 tắt, batch 16, workers 0, threads 4. Global features là CLS nối mean patch tokens; head 128 hidden/dropout 0,3/two logits độc lập. Mọi arm có head LR 3e-4, AdamW WD 0,01, warmup head-only 3 epoch, cap 24, patience 6, min_delta 1e-4, cosine về 0,1 × LR. Đây là cùng horizon; đổi cap làm thay lịch LR nên không kéo dài riêng arm đang có điểm đẹp.

| Arm | Encoder | Input | Block cuối được mở + norm | Backbone LR | Đối chứng chính |
|---|---|---:|---:|---:|---|
| C0 | DINOv2-S/14 | 336 | 2 | 1e-5 | Recipe G0, train mới trên V15 |
| S448 | S/14 | 448 | 2 | 1e-5 | Resolution so với C0 |
| SL | S/14 | 336 | 2 | 3e-6 | Adaptation nhẹ hơn C0 |
| SH | S/14 | 336 | 2 | 3e-5 | Adaptation mạnh hơn C0 |
| S4 | S/14 | 336 | 4 | 3e-6 | Depth so với SL, giữ LR |
| B0 | DINOv2-B/14 | 336 | 2 | 1e-5 | Representation so với C0 |
| BL | B/14 | 336 | 2 | 3e-6 | Representation so với SL |
| B448 | B/14 | 448 | 2 | 3e-6 | Resolution so với BL |

Giữ letterbox bilinear/fill/normalize hiện hành, hflip 0,5 và photometric jitter nhẹ; không box jitter/erasing. Head S có input 768, B có input 1.536. Các arm cùng encoder/seed dùng cùng initial head và thứ tự sample/augmentation; không thể ghép cùng head S/B do khác dimension. Prefix encoder frozen vẫn chạy no-grad, không cache frozen features qua augmentation hoặc qua encoder đã thích nghi.

**Profile chọn bằng GPU/VRAM trước mọi training hoặc xem score:** `full` khi CUDA khả dụng và VRAM ≥ 40 GiB, chạy đủ tám arm; `core` khi 14 ≤ VRAM < 40 GiB, chạy năm arm S. GPU thấp hơn dừng. Ưu tiên premium GPU nếu Colab cấp, không giả định có A100/H100. Actual smoke phải kiểm memory/time; tên GPU hay dung lượng danh nghĩa không thay smoke. OOM/không đạt thời gian thì dừng, không tự đổi profile, batch hoặc precision trong campaign đã khởi tạo.

1. Screening toàn bộ arm của profile ở **hai seed 20261106/20261107**, hoàn tất seed đầu rồi seed sau. Rank trên kết quả tổng hợp hai seed, không dùng một seed may mắn.
2. Chọn hai recipe đầu theo quy tắc đã khai trong YAML; lấy union với C0. Chạy thêm **20261108/20261109/20261110**. Tái dùng hai screening run trong thống kê năm seed, không train lại chúng.
3. Full tối đa **16 + 9 = 25 research run**; core tối đa **10 + 9 = 19**. Nếu C0 đã nằm trong top hai thì dedup, còn 22 hoặc 16 run. Không tự thử thêm hyperparameter/seed vì còn CU hoặc sau khi xem errors.

## 4. Chọn epoch, ngưỡng và kết luận

Giữ rule chọn checkpoint: max val macro AP, tie min raw masked BCE, rồi earliest epoch. Hiệu chỉnh đúng một cặp threshold bằng `calibrate_exact` sau chọn checkpoint; dùng lại cho train/val/slices/reload. Báo thêm ngưỡng 0,5 để nhìn calibration. Không chọn ngưỡng mới sau khi xem báo cáo hoặc fit lại trong bootstrap.

Recipe ranking: số seed đạt đồng thời hai target → tổng target pass → mean shortfall với 80/80/20 → mean macro AP → mean raw BCE → ít tham số/input nhỏ hơn → arm ID. Screening dùng hai seed, cuối dùng năm seed; không đổi rule theo model thắng. Support và gate mỗi target giữ precision ≥ 0,8, recall ≥ 0,8, FPR ≤ 0,2.

Đề xuất thêm mục tiêu ổn định **ít nhất 4/5 seed cùng đạt hai target** để gọi là research candidate E009. Đây là tiêu chí đang xin duyệt, không sửa gate artifact cũ hoặc đồng nghĩa Selected. Nếu không đạt, ghi Continue với evidence; không đổi nhãn/split/gate để qua. C0 có thể thắng; không bắt buộc chọn B hoặc 448.

Mỗi recipe cuối báo đủ năm seed, mean/sample SD, confusion/support P/N/U, AP và P/R/F1/FPR. So paired với C0 trên **cùng V15**, bootstrap nguyên 119 nhóm, 2.000 lần, giữ chung draws giữa recipe và năm seed; threshold giữ fixed. Dùng interval như mô tả development sau selection, không dùng nó để chứng minh generalization. Các slice nhỏ chỉ diagnostic và ghi support; không tuning slice riêng.

Handoff một checkpoint có cả hai target: trong các seed đạt cả hai gate của recipe được chọn, lấy seed có macro AP ở vị trí lower median, tie theo seed tăng dần. Nếu không có seed pass thì chỉ bàn giao research, không tự đóng candidate. Giữ best/last của mọi run cho tới khi audit và owner chốt retention. Không ghép phone của model này với looking của model khác. Không refit trên train+val vì sẽ mất cohort đánh giá hiện tại.

Model lớn hơn có thể chậm hơn đáng kể. E009 chỉ chọn research candidate; model/runtime đang tích hợp vẫn G0 cũ. Sau nghiên cứu mới đề xuất benchmark inference trên máy demo và quyết định thay model theo scope riêng; ưu tiên model nhỏ hơn khi chất lượng tương đương, không tuyên bố CUDA train nhanh đồng nghĩa CPU live nhanh.

## 5. Ngân sách 12 giờ và phục hồi

| Phần | Trần phút |
|---|---:|
| Mount/verify/setup và environment | 40 |
| Actual GPU smoke | 70 |
| Research, gồm reload và sync từng run | 500 |
| Audit/export/sync cuối | 45 |
| Reserve được bảo vệ | 65 |
| **Tổng** | **720** |

Mỗi research run + reload + final sync có cap **20 phút**. 25 × 20 = 500 phút là **phép cấp ngân sách**, chưa phải benchmark hoặc dự báo thời gian đo được. Không hứa chạy đủ full trên mọi GPU. Smoke phải dự báo cap 24 epoch từ elapsed run full 5 epoch × 24/5 × 1,25, cộng reload và final sync đã đo; dùng bound của arm smoke đắt hơn cho shape tương ứng. Peak VRAM ≤ 85% tổng VRAM; mọi active encoder/resolution phải qua shape/finite/gradient checks. Nếu không qua thì không mở research.

Smoke có ba arm theo profile, mỗi arm một full 5 epoch và một interrupt sau epoch 3 → resume tới 5: tối đa sáu run. Kiểm chuyển head-only → finetune, frozen prefix/norm đúng policy, optimizer/RNG/permutation/history/tensors best/last và standalone reload. Run smoke không tham gia ranking hoặc được tái dùng làm checkpoint research.

Đếm thời gian từ **lần launcher đầu tiên**, gồm setup/smoke/lượt lỗi/recovery, lưu timestamp/deadline trên Drive và không reset khi reconnect. Đây là cap wall-clock bảo thủ hơn thời gian GPU active, không phải số CU billing đo được. Dừng mở training trước phút 610 và chỉ admit run khi đủ toàn bộ cap còn lại; giữ 110 phút cuối cho audit/reserve. Nếu hết ma trận sớm thì sync rồi unassign ngay.

[Colab FAQ](https://research.google.com/colaboratory/faq.html) nêu rõ GPU/tài nguyên và thời lượng không được bảo đảm; Pro có thể bị ngắt khi hết CU. Không coi 12 giờ owner chọn là cam kết phiên chạy liên tục. Upload bundle private trước khi cấp GPU; kiểm CU/rate đang hiển thị trong tài khoản trước launcher, không tự mua thêm. Không cần High RAM nếu actual host-memory preflight đã đủ.

Giữ setup Python **3.12.x**, Torch **2.8.0+cu128**, torchvision **0.23.0+cu128** theo recipe đã chạy E008; ghi actual Python/driver/GPU/VRAM/pip freeze trước smoke. Notebook dùng CPython **3.12.12** thật trong subprocess/venv dù kernel Colab là 3.13; uv dùng bản phân phối `python-build-standalone` của Astral. Không giả phiên bản hoặc nới `requires-python <3.13`. Cài interpreter tính vào budget hiện hành. [Tài liệu uv](https://docs.astral.sh/uv/guides/install-python/).

Giữ FP32/TF32 tắt cho tất cả arms. AMP/BF16/compile không tự làm metric tốt hơn và hiện chưa thuộc parser/trainer; triển khai chúng sẽ thêm biến precision/resume/kernel vào experiment. Với budget này ưu tiên capacity/resolution và xác nhận nhiều seed. Nếu actual smoke không đủ nhanh, dừng và review revision riêng thay vì bật AMP giữa chừng. [PyTorch AMP 2.8](https://docs.pytorch.org/docs/2.8/amp.html), [giới hạn reproducibility](https://docs.pytorch.org/docs/2.8/notes/randomness.html).

Owner xác nhận Drive còn gần **5 TB**; đây là thông tin owner cung cấp, chưa đo qua tài khoản trong task này. Trước launch kiểm còn tối thiểu 50 GB và local disk/RAM đủ theo actual bundle/checkpoint sizes; không cần mua storage. Dataset dùng working copy trên local disk Colab để tránh đọc ảnh qua Drive ở mỗi batch.

Checkpoint epoch đồng bộ atomic tar sang private Drive theo `recovery.py`; giữ cả initialization artifacts, configs/approval/protocol, pinned source, source bundle và runtime receipt. Metadata ZIP không thay backup best/last. Runner hiện copy lại toàn bộ thư mục campaign ở mỗi `sync()`, sẽ lặp ghi các model đã hoàn tất khi tăng số run: E009 cần sync chỉ file thay đổi, verify hash và publish atomic. Đo cả epoch recovery/final sync trong smoke; CUDA nhanh không bù được Drive I/O chậm.

Recovery chỉ sau xác minh process cũ dừng và hashes khớp; tiếp tục cùng config/code/runtime/GPU identity. Colab cấp GPU/environment khác thì không bypass resume guard; giữ partial và trình revision/attempt mới trong cap còn lại. Không giả định toàn campaign có thể tự resume chỉ vì một run có `--resume`.

## 6. Implementation và gates

Các phần dưới đã được triển khai và kiểm local; [handoff](../../../artifacts/reports/e009-v15-colab-20261106/README.md) giữ kết quả. Bảng đối chiếu scope so với V4/V5, không là backlog chạy thêm ngoài ma trận.

| Phần hiện hành | Đã có | Thay đổi cần duyệt/triển khai |
|---|---|---|
| `adaptation_config.py`, `encoders.py`, `adaptation_model.py` | V4/V5 chỉ DINO-S, hardcode blocks 10/11, head 768 | Schema mới dự kiến V6, enum S/B, last-N ∈ {2,4}, prefix no-grad và head dim đúng encoder; giữ V1–V5 nguyên semantics |
| `representation_prepare.py` | Một screening seed, materialize old enrollment/provenance schema, hardcode float32/S model | Tái dùng preparer với fields V6/profile/two seeds; tạo sidecars E009 từ V15, kiểm membership/group/rights đầy đủ |
| `representation_campaign.py` | Một champion + control; reject campaign đã có; copy toàn campaign khi sync | Rank hai seed, top hai + C0, caps/reserve gồm sync, incremental hash-verified sync, verified continuation/finished-run skip, persisted deadline; không duplicate run |
| `adaptation_train/evaluate.py`, dispatch | Masked loss, epoch RNG/optimizer, full bundle/reload guards | Dispatch V6 đúng; assert legacy behavior và C0 V6 tương đương C0 V5 cùng tensor/config; không nới code/runtime guard |
| `colab_bundle.py` / notebook | Allowlist, pinned inputs, launcher riêng E008 | Bundle/launcher E009 mỏng; add V15 enrollment dependencies; đủ head initialization và full checkpoints trong backup; không copy thuật toán train vào notebook |

V15 `allocation.json` có status mô tả và structure khác enrollment mà preparer hiện nhận; không đưa thẳng file vào để rồi đổi status release cho qua. Tạo adapter/sidecar E009 có pins về originals. Slice hiện tại dùng `source.image_width/height` có thể là frame đầy đủ: E009 phải tính native crop extent từ context/crop dimensions, đồng thời phân biệt unresolved upstream với original source, không gom mọi crop mới thành một nguồn giả.

Source DINO đã pin `7764ea0…` có cả factory S/B; source archive và weights S đã verify SHA khi build. Weights B chính thức đã tải và pin SHA `0b8b82f85de91b424aded121c7e1dcc2b7bc6d0adeea651bf73a13307fad8c73`; [receipt nguồn/license](../../../artifacts/reports/e009-v15-colab-20261106/pretrained.json). Strict state load, features 336/448 khớp upstream và gradient policy trên tensor tổng hợp CPU đã PASS; [receipt](../../../artifacts/reports/e009-v15-colab-20261106/official-model-checks.json). Null trong proposal Draft giữ snapshot, không lọt vào execution design/FilePin; không dùng checkpoint E008 làm initialization.

Software gates trước bundle gồm schema rejection/identity, source factory/features parity, gradient/freeze mọi scope, geometry/cache 336/448, masked loss/support, paired selection/confirmation dedup, budget/resume/corrupt-snapshot refusal, bundle allowlist và synthetic interruption/reload. V6 đã có telemetry peak VRAM allocated/reserved và elapsed train/epoch-sync; runner ghi reload/final-sync. Actual CUDA smoke mới đo memory/time trên môi trường Colab và mở research; unit/local PASS không thay GPU smoke hoặc nghiệm thu model.

## 7. Approval và execution scope

Owner đã duyệt **ma trận có hai profile, variables/protocol ở YAML, trần 12 giờ, triển khai V6 và runner, rồi smoke/research trên private Colab/Drive với đúng V15**; [receipt](owner-authorization.json) giữ chỉ đạo thực tế. Gate theo [AGENTS](../../../AGENTS.md) và [training §3](../../../docs/training.md#3-experiment-contract-và-quyền-theo-hành-động): quyền research chỉ mở sau actual CUDA smoke đúng identity, không test/promotion.

Materialize exact configs/pins từ thiết kế đã duyệt, theo luồng software → bundle → actual GPU smoke → research → audit. Không hỏi lại từng arm/seed đúng scope. Preparer đăng ký trước mọi tổ hợp arm/seed; runner chỉ thực thi screening và union finalists/C0 theo cap, các config không được chọn không là run còn thiếu. Đổi biến/nguồn/precision ngoài proposal cần revision có identity riêng. Test, promotion và thay runtime model vẫn là quyết định riêng.
