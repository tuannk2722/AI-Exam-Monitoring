# E004 — Đề xuất freeze protocol và implementation plan, 2026-10-11

**Draft để owner review; không cấp quyền implementation scientific, smoke thật, training, final test hoặc promotion.** Bản này bổ sung [proposal active](E004-proposal.md), giữ nguyên [YAML đã pin](E004-plan.yaml) và original ADR-017 ở Git `ab34b32`. Evidence mới: [audit sau V7](../../artifacts/reports/E004-post-v7-audit-20261011/README.md). Không đổi contract [training](../../docs/training.md)/[data](../../docs/data.md).

## 1. Freeze theo từng hành động

| Mốc | Đối tượng phải pin / bằng chứng | Quyền và blocker |
|---|---|---|
| F0 — design | Recipe dưới đây, objective version/BN/sampler/checkpoint/cache/test-access contract; scope local CPU và budget; numeric gates/claim | Owner chốt thiết kế trước implementation liên quan. Audit/proposal không là approval. Smoke không là điều kiện để bắt đầu duyệt design. |
| F1 — data/evaluation | V7 manifest/ledger/payload/config/approval; comparator48 IDs/labels/masks/map; new-development package; holdout source/rights/provenance và sampling/support | V7 local Accepted. Các phần khác chưa Accepted. Không tự chuyển train sang val/test hoặc đổi V7. |
| F2 — software/smoke readiness | Exact source commit + package identity, config schema version, synthetic tests; smoke được phép với exact inputs/compute và output riêng | Smoke thật chỉ sau scope riêng. PASS không thay G0–G3; original ADR-017 không cho run E004 promotion-oriented khi G0–G3 chưa đóng. |
| F3 — matched runs | Hai config hashes/approvals/run IDs, cùng data/preprocess/head init/order/objective/selection/budget/environment; v7 loader/preservation verification | Owner duyệt quyền run đúng identity. Chưa chạy hai run. Diagnostic scope khác cần owner chọn riêng, không tự bỏ yêu cầu holdout của E004. |
| F4 — candidate | Một checkpoint/bundle/threshold, metrics/CI/slice implementation, holdout inventory và protocol digests; development review | Candidate freeze sau run hợp lệ; quyền final evaluation cấp riêng. Không đưa control/E003 vào holdout. |
| F5 — final/promotion | Use-once receipt, final metrics/support/CI/benchmark/restoration và M1–M7 AND; owner decision | Không tự Selected từ FINISHED hoặc development gain. |

Owner là chủ repository, solo review hợp lệ. Không yêu cầu người thứ hai. Không hỏi lại quyền sử dụng hai ZIP đã được owner xác nhận ngày 2026-10-11; membership/role/group/label/protocol vẫn là quyết định khác.

## 2. Cohorts và comparator

**Đề xuất lựa chọn:** dùng new-development độc lập theo whole-family làm cohort chọn epoch; giữ historical comparator48 và val 49 để báo chẩn đoán sau selection. Mỗi cohort có vai trò riêng đã pin. Nếu owner chọn historical val 49 cho selection thì ghi rõ diagnostic research và thiếu new-development; lựa chọn đó không tự giải quyết mục tiêu generalization hoặc bỏ G1–G3.

Comparator48 dùng nguyên danh sách trong [verification mới](../../artifacts/reports/E004-post-v7-audit-20261011/comparator48-verification.json). Pin source/crop/target evidence/values/masks/work context/rights, dataset/encoding/split versions và ID order. Full val 49 có 14 old→14 new groups bijective; comparator48 chỉ 13 groups vì loại singleton `EXP-SCB-002`. Pin mapping toàn 49 và mapping subset theo ID; kiểm không merge/split và whole-family không qua train. Không đổi literal group/review hashes của V6/E003.

So adaptation **candidate trừ matched frozen control** trên cùng cohort/labels/masks. E003 cached-score comparison chỉ lịch sử, dùng đúng cache SHA và 48 retained IDs; không inference E003 trên final holdout. Val50→49 có annotation/cohort effect, tách khỏi model effect. Không lựa intersection mới sau khi thấy score.

Added37 lịch sử: đúng `val 50 V6 − val 13 V5`, pin danh sách trước run. Sau CA041 rời val còn 36 IDs; sau loại EXP-SCB-002 khỏi comparator còn 35. Cần freeze lại endpoint/subset và denominator phone known P, không giữ tên “37” rồi thay tập âm thầm. Audit tính và ghi exact IDs/support tại [added-development-verification](../../artifacts/reports/E004-post-v7-audit-20261011/added-development-verification.json).

New-development là package/assignment mới từ **families chưa dùng**, cả hai target QA và các contrasts, không đổi release V7. Sampling quyết định trước predictions. Chỉ những group có provenance đã xác minh được dùng để claim independent evidence; unknown lineage quarantine theo vai trò. Không lấy raw upstream train/valid/test phân vai E004.

Holdout riêng: nguồn/group chưa dùng phát triển E001–E004, provenance graph person/session/room/camera và cross-source overlap review, rights/use scope đã xác nhận, blind annotation, pin sampling mixture trước inference. Hai ZIP mới là candidate pools; chưa đủ independence để chọn holdout. Nếu ưu tiên dùng một family cho holdout thì reserve trước draft training selection; không xem candidate scores. Raw label names chỉ gợi ý tìm ảnh, không canonical labels.

M4 slices phải là **context enrollment** độc lập khỏi P/N và scores: desk/workarea có thể quan sát; small/partial device opportunity có geometry/visibility và N vật gây nhầm; hướng nhìn so own workarea; crowded anchor; posture đọc/viết/nghỉ. Định nghĩa bbox/visibility bins từ distribution và owner chốt trước training; không tự đặt ngưỡng pixel. Một crop có thể thuộc nhiều slices, report overlap và denominators. Positive-only “desk-phone P” không có precision/FPR hợp lệ. Chưa đạt support thì INCONCLUSIVE, không đổi slice để pass.

## 3. Matched control và candidate — toàn bộ recipe Draft

| Biến | E004-LP-control | E004 layer4 candidate |
|---|---|---|
| Encoder/head | ResNet18 frozen hoàn toàn + Linear(512,2) mới | Stem/layer1–3 frozen; layer4 + Linear mới trainable |
| Pretrained | Local IMAGENET1K_V1, SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec` | Cùng weights, không download/fallback |
| Initialization | Head snapshot độc lập seed 42 sau load backbone; pin initial tensor digest | Load chính snapshot head của control; không E003 warm-start |
| BN | Running mean/var/num_batches_tracked bất biến; mọi BN eval | Mọi BN eval; layer4 affine weight/bias **đề xuất trainable**, BN các tầng trước frozen. Phải chốt rõ trước coding |
| Inputs | RGB letterbox bilinear 224, fill [124,116,104], mean [0.485,0.456,0.406], std [0.229,0.224,0.225]; target order [phone_use,looking_around] | Giống control; no augmentation, FP 32 |
| Optimization | AdamW head LR 0.001, WD 0.0001 | Head LR 0.001 + layer4 LR 0.0001, WD 0.0001 cho cùng policy gồm affine/bias; không tự thêm no-decay rule |
| Batches | 16, deterministic uniform permutation từng epoch, drop_last=false, workers=0, không class/group reweight | Cùng ID permutation/order, batch boundaries và tail batch |
| Budget/selection | 50 epochs tối đa, patience10/min_delta0.0001; best là raw min global val macro BCE, tie giữ epoch đầu | Giống control; early-stop reference riêng best như trainer hiện tại |
| Operating point | 0.5 cả hai targets; development diagnostics không tune threshold | Giống control; final chỉ một candidate |
| Compute | Local CPU, 4 threads, dependency/environment pin; thời gian chưa đo | Ngoại lệ CPU mới và wall-time budget cần owner chốt; không tự cloud/upload |

Đề xuất chạy cùng đường image mini-batch cho hai model để giảm khác biệt pipeline. Control có thể dùng frozen 512 feature cache sau kiểm parity, nhưng optimization mini-batch phải cùng objective/order; không tái dùng E003 full-batch trainer rồi gọi matched recipe. Candidate không dùng frozen 512 features. Không cần cache layer3 trong lượt đầu; nếu muốn cache prefix sau này phải có config/version/shape/digest và parity riêng, không thêm ngầm.

`eval()` thay đổi hành vi lớp, không tự tắt gradients; layer4 phải đi qua autograd. Các tầng frozen có thể dùng no_grad cho prefix rồi truyền tensor thường vào layer4; không wrap toàn encoder trong no_grad/inference_mode. Cơ sở API: [PyTorch autograd](https://docs.pytorch.org/docs/2.14/notes/autograd.html), [BatchNorm](https://docs.pytorch.org/docs/2.14/generated/torch.nn.BatchNorm2d.html). Đây là đề xuất cho repo; không đổi environment historical Torch 2.8 bằng version docs mới.

## 4. Objective mini-batch và null policy cần freeze

Giữ objective full-cohort: với N records, K_t là known count của target t **từ train manifest**,

`L_full = (1/2) Σ_t [Σ_i m_it × BCEWithLogits(z_it,y_it) / K_t]`.

Đề xuất objective mini-batch version mới:

`L_batch = N/(2×b) × Σ_t [Σ_(i trong batch) m_it × BCEWithLogits(z_it,y_it) / K_t]`, b là batch size thực tế.

Ở predictions cố định, trung bình các batch có trọng số b/N khớp L_full, và batch uniform có kỳ vọng đúng objective. Không trung bình các target có mặt theo denominator batch vì sẽ đổi trọng số trong các batch partial-known. Nếu một target không known trong batch thì tổng của nó bằng 0, **vẫn chia hai targets**; không fabricate N/U. K_t=0 toàn train ⇒ từ chối. Batch toàn unknown ⇒ lỗi membership/contract; U/U vốn không được vào supervision. Không label-balance/resample để né empty target.

End-of-epoch train/val BCE được tính lại ở checkpoint hiện tại, accumulate per-target sums/known counts toàn cohort, không lấy mean loss từng batch. Loss/metrics unknown giữ mask và chỉ tính known entries; JSON null không thành nhãn 0. AP non-interpolated với tie grouping, precision null khi không positive predictions, missing P/N metric null, FPR null khi không N. Nonfinite known scores/loss/gradients ⇒ FAILED, không epsilon/clip để qua gate.

Không sửa hàm `masked_loss` v1 vốn yêu cầu full-batch support cả hai target để giữ historical contracts. Version config/objective mới phải phân biệt formula/normalization/empty handling và cache fingerprint; no scheduler/no grad clipping/augmentation nếu chưa có quyết định riêng.

## 5. Implementation theo module hiện có

| Work package | Module/consumer hiện có | Deliverable và exit check |
|---|---|---|
| I1 config/approval | training/config.py, train.py, evaluate.py | Schema/version mới cho model policy, mini-batch/BN/LR groups/cohort/protocol pins. Unknown/extra/null/nonfinite keys fail; approval digest đúng từng ID. Giữ parsing E001–E003 và original pins. |
| I2 data/protocol | training/data.py, pilot_schema.py, integrity.py | Tái dùng strict codec/payload/rights/freeze; validate exact cohort membership + whole-family mapping. V7 đã release không đủ chứng minh loader E004 readiness: chạy verify đúng config trong smoke được phép. Independent dev/holdout không cần đưa vào V7 manifest. |
| I3 model | training/model.py | Thêm policy partial fine-tune; fixed prefix + layer4 autograd, BN buffers freeze, explicit trainable parameter names; head init digest; optimizer groups không overlap/omission. Không sửa FrozenEncoder semantics cũ. |
| I4 objective/trainer | training/metrics.py, train.py | Formula/version mới; sampler riêng, tail/empty handling, global metrics; raw-min best và early-stop state. Prediction exports không có holdout. |
| I5 checkpoint/resume | training/artifacts.py, train.py, model.py | last/best chứa **backbone+head**; optimizer/moments, Python/NumPy/Torch RNG + sampler generator/permutation/cursor, epoch/global step, best/early_reference/stale/history, schema/config/identity/parameter groups. Atomic writes; nếu chỉ checkpoint epoch-boundary thì interruption giữa epoch restart từ epoch đã commit, khai báo rõ. Không gọi resume arbitrary batch nếu thiếu cursor. |
| I6 evaluator/bundle | training/evaluate.py, metrics.py | Load full model không pretrained ngoài; same preprocess/targets/threshold, exact code/environment/protocol; export confusion/AP/BCE/slices/FPR và constant từ train prevalence. Bundle receipt license/version/checksums. Identity toàn package giữ nguyên cho historical evaluator; code mới ⇒ identity mới, không sửa hash cũ. |
| I7 holdout access | evaluate.py + helper canonical trong training sau design approval | Local append-only access registry keyed **holdout payload**, bảo vệ across output/protocol/model names; atomic reserve trước mở crops/weights inference; pending/failed/consumed đều chặn auto-repeat, explicit owner protocol cho recovery sau crash. Không overwrite/delete receipt để retry. V1 chỉ quản lý một workspace/registry, không claim distributed enforcement. |
| I8 uncertainty/benchmark | metrics/evaluator + CLI/helper riêng theo responsibility | Group-bootstrap seed 42/5000, validate denominators; benchmark đúng M6 trên development, RSS + timing protocol; lưu method/environment/bundle digest. Không benchmark dùng holdout. |

Core tái dùng trong `src`, variables trong config và notebooks chỉ launcher. Không sao chép trainer E003 hoặc builder v7 thành version-specific scripts. Plan không mở runtime/tracker/risk/web contracts.

## 6. Meaningful test plan

| Test | Fixture / assertion cần PASS trước run |
|---|---|
| T1 config/approval | Legacy v1 configs vẫn load; new schema từ chối unapproved digest, null pins, extra fields, invalid enum/device/LR/target order; approval control không dùng cho candidate. |
| T2 masks/objective | Batches thiếu known một target, unequal known counts, tail b=1, U entries có giá trị tùy ý; hand-calculated global loss/gradient parity ở model cố định, U có zero gradient; K=0/all-U fail; JSON U không đổi thành N. |
| T3 freeze/autograd | Một optimizer step thật trên synthetic images: head và layer4 có finite nonzero grads/updates; stem/layer1–3 parameters và mọi BN buffers bitwise unchanged; `train()` không bật BN running stats; affine policy đúng. Control backbone hoàn toàn unchanged. |
| T4 matching/cache | Pin head initial digest và permutations bằng nhau; cached-control vs uncached logits/parity ở cùng weights; crop/config/code/weights/transform change làm cache invalid; candidate từ chối frozen512 cache. |
| T5 resume | CPU deterministic uninterrupted vs epoch-boundary interrupted/resumed: full state tensors/optimizer/RNG/order/history/best/stale/scores khớp; thay config/data/cohort/objective/BN/code/environment ⇒ reject; failure ghi đúng status, không tự đổi batch. Serialized .pt bytes không cần bằng nhau nếu container khác, so tensors/digests chuẩn hóa. |
| T6 evaluator/bundle | Reload full bundle tại process mới không original pretrained; score/BCE/AP/confusion/best epoch khớp training export, exact ID order; target order/crop hash/code mismatch fail; no holdout records trong train/cache. |
| T7 metrics/gates | Hand-counted FP/FN/FPR, AP ties, no-positive-predictions null, missing P/N null; macro không bù target yếu; M4 positive-only/insufficient support INCONCLUSIVE. Bootstrap whole groups (group duplicates không inflate independence), >=95% valid resamples, seed deterministic, invalid precision denominator xử lý từng metric. |
| T8 use-once | Missing approval fail trước media; attempt thứ hai với output/model/protocol khác bị block cùng holdout; concurrent reservation chỉ một thắng; crash-after-reserve không được rerun tự động; tampered receipt/inventory fail closed. |
| T9 benchmark | B1/4threads, warm-up 10/measured500, decode+transform+forward trong timing, startup riêng, hashes ngoài loop; pin crop order/OS/CPU/environment/RSS semantics. Không fake M6 PASS từ synthetic speed. |
| T10 regression | Existing tests/test_training.py + test_training_preservation.py và trực tiếp consumers schema/preprocess/approval/evaluator; Ruff/strict mypy/compile/checker theo development. Clean checkout không dựa binaries khi thay rộng. |

Sau synthetic PASS và design/data/compute approvals: smoke thật với config/identity/output riêng kiểm memory/time, one-step updates, checkpoint/reload và recovery. Smoke budget không phải 50-epoch run. Sau smoke PASS owner/run approvals đã đủ thì chạy matched control/candidate; không hỏi lại quyền đúng scope đã có. OOM/budget/interrupt ghi FAILED/INTERRUPTED; đổi variables tạo identity mới.

## 7. Reproducibility contract và decision record

Run lưu ID/role/owner/hypothesis/parent; Git commit+dirty+diff digest và package code identity; exact config/approval/protocol/cohort/label/group-map digests; dataset manifest/ledger/payload/split/encoding/weights; seed/deterministic flags/head initial digest/permutations; Python/OS/CPU/Torch/Torchvision/Pillow/NumPy dependencies/threads/workers; command/start/end/status và resource observations. Không sửa historical pins khi package code đổi.

Local artifacts mới: run.json/resolved-config.json/environment.json/initialization.json/last.pt/best.pt/history.json/predictions-train.json/predictions từng development cohort/metrics.json/checksums.json/full bundle + receipt. Resume chỉ same identity; config/compute/data khác là run mới. Predictions giữ null/mask/target order và stable ID order. Final test protocol/receipt tách biệt, không artifact test trong cache train/development.

Parity: synthetic deterministic CPU cùng environment yêu cầu exact tensor/state parity khi khả thi; real smoke reload cùng environment đề xuất score absolute tolerance 1e-6, confusion/ID/mask/best epoch exact, BCE/AP tolerance1e-6. Đây là tolerance **Draft phải freeze trước smoke/run**, không sửa sau khi fail. Cross-platform chỉ claim theo environment/tolerance được duyệt, không hứa bitwise chung Windows/Colab.

Owner decisions còn mở: comparator/selection-cohort và added subset; design/objective/BN-affine/recipe/compute budget; numerical gates giữ nguyên hay revision có rationale **trước predictions mới**; source roles + new-development/holdout membership/provenance/sampling/claim. Chưa có các decisions này thì tiếp tục research/software scope độc lập được giao, không chạy E004 hoặc mở final test.
