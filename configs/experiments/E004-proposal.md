# E004 — Hồ sơ thiết kế và quyết định đang mở

**Draft, chưa quyền training/final test/promotion.** Đây là bản diễn giải đang làm, được chuyển từ training spec ngày 2026-10-11; không là ExperimentConfig, không đổi pins hoặc thay approval. [YAML lịch sử đã pin](E004-plan.yaml) giữ nguyên bytes; [audit gốc](../../artifacts/reports/E004-v7-fit-audit-20261010/README.md) và [input pins](../../artifacts/reports/E004-v7-fit-audit-20261010/input-pins.json) là evidence.

Audit bổ sung ngày 2026-10-11: [inventory coverage 375 new-train, gaps và hai ZIP owner cung cấp](../../artifacts/reports/E004-post-v7-audit-20261011/README.md). [Đề xuất freeze và implementation plan](E004-freeze-proposal-20261011.md) cụ thể hóa comparator/selection cohorts, mini-batch objective, BN/checkpoint/resume và test plan; toàn bộ choices mới vẫn Draft. Owner đã xác nhận quyền sử dụng cả hai ZIP trong scope xử lý local; không hỏi lại quyền. Taxonomy/QA224 và provenance independence chưa hoàn tất chỉ vì inventory đã đủ.

Quyền theo hành động và contract chung ở [training](../../docs/training.md); dùng [status](../../docs/status.md) để biết proposal đang được ưu tiên. Khi thiết kế được duyệt, tạo config/approval đúng identity; không sửa YAML lịch sử. Kết quả run thuộc outputs/reports của run, chỉ giữ decision/lifecycle và link kết quả ở hồ sơ này.

## 1. Proposal đang hoạt động: E004 — Draft, snapshot 2026-10-11

Đây là nơi cập nhật lifecycle E004. Khi Accepted, Rejected hoặc Superseded, ghi ngày/scope/evidence và proposal thay thế nếu có; giữ hypothesis/recipe từng revision đã pin. Results hoàn tất thuộc artifacts/reports/<experiment-id>/; không thay tên E004 thành ID mới trên nội dung lịch sử. Ngày snapshot phản ánh tình trạng hồ sơ, không là ngày chạy experiment.

Snapshot này: E004 chưa triển khai/chạy; recipe/compute/comparator/holdout và numerical gates chưa được chốt. Đây là trạng thái của proposal này, không phải giới hạn lâu dài của trainer hoặc dự án.

Owner chọn tiếp tục classifier trên reviewed crops, tìm nguồn holdout công khai mới. Proposal `configs/experiments/E004-plan.yaml` chưa có approved ExperimentConfig, data/split/payload/holdout pins vẫn null; `training_approved=false`, `final_test_approved=false`, `eligible_for_promotion=false`. Phần dataset gate v7 đã hoàn tất local; recipe/metrics/compute/holdout chưa chốt.

**Tham chiếu proposal đã pin:** YAML Draft trên là input lịch sử trong `artifacts/reports/E004-v7-fit-audit-20261010/input-pins.json`, nên giữ exact bytes dù chưa Accepted. Field `model_acceptance_adr` trỏ `docs/decisions/ADR-017-e004-classifier-promotion-gates.md` là **original path lịch sử**, không còn là file active. Nội dung gate để đọc/làm task ở [gate bên dưới](#e004-promotion-gates); original tra Git `ab34b32:docs/decisions/ADR-017-e004-classifier-promotion-gates.md` hoặc inventory history theo docs/operations.md khi cần exact evidence. Các path đã retire trong README audit cũng là historical locators. Không sửa YAML/receipt để làm khớp cấu trúc docs mới; revision proposal tương lai có identity/pins riêng.

`TBD-E004-RECIPE.resolve_when` trong snapshot YAML gộp approval và smoke readiness. Cách thực hiện theo training contract: owner duyệt design/protocol/config trước implementation liên quan; smoke được phép kiểm chứng thực thi sau đó; smoke PASS là readiness trước run, không phải điều kiện duyệt design ban đầu. Việc làm rõ trình tự không cấp quyền chạy E004.

Hypothesis: sau targeted data/QA, mở layer 4 có thể thích nghi desk-phone và hướng nhìn tốt hơn frozen probe trên **cùng v7/protocol**, rồi kiểm độc lập trước xét promotion. Không hứa mức gain hoặc suy recipe được approve vì config đã tồn tại.

| Biến | Control đề xuất | Candidate đề xuất |
|---|---|---|
| Model | `E004-LP-control`: encoder frozen + head mới | E004: layer 4 + head trainable, các phần trước frozen |
| BN / initialization | Running statistics eval; head seed 42 mới | Cùng BN/head policy; không warm-start head E003 |
| Input/loss/threshold | RGB letterbox 224, no augmentation, masked macro BCE, 0.5 | Giữ cùng control để đo adaptation |
| Optimizer/budget | AdamW head LR 0.001, decay 0.0001, batch 16, max 50 epochs/patience 10/min_delta 0.0001 | Head LR 0.001, layer 4 LR 0.0001, cùng budget/seed/batch |
| Selection/compute | Raw minimum masked val BCE; CPU 4 threads proposed | Cùng policy; CPU ngoại lệ/budget phải owner duyệt mới |

**Toàn bảng là Draft.** Trainer hiện feature-cache/frozen-head nên không chạy candidate chỉ bằng sửa YAML. Sau khi owner chốt design, cần trainable/BN policy thật, mini-batch masked objective, optimizer groups, checkpoint đủ backbone+head/optimizer/RNG/scheduler nếu có, resume/cache invalidation/evaluator và model bundle. Kiểm frozen vs trainable weights/buffers, uninterrupted–resumed parity và metrics reload bằng fixtures; smoke local trước run thật. Input 384/resolution ablation là experiment riêng chưa approved.

Comparator development chưa Accepted: v7 val 49 từ val 50 sau `V6-CA-041` rời val và `EXP-SCB-002` đổi label. 48 retained IDs giữ source/crop/target/mask/context/rights nhưng literal group/review identity versioned; mapping toàn retained val49 là 14 old groups ánh xạ 1–1 sang 14 new groups, còn comparator48 có 13 groups. Phải owner freeze IDs/label contract/group mapping và protocol trước run; không tự dùng intersection tùy ý hoặc gọi 49 là cùng 50.

Audit dùng **cached E003 scores**, không model inference, minh họa recall phone 0.529→0.563 và looking 0.611→0.647 khi đổi labels/cohort sang v7. Cùng model mà metric đổi: đây là annotation/cohort effect, không E004 gain. Không chạy E003 trên final holdout mới để dựng comparison.

<a id="e004-promotion-gates"></a>

## 2. ADR-017 — acceptance/promotion gates của proposal E004

ADR-017 vẫn **Draft**. Nội dung proposal được giữ ở đây để owner/agent tiếp tục chốt, không phải metrics Accepted hoặc quyền execution. Scope nếu được chốt chỉ Selected cho nghiên cứu classifier trên reviewed crops/nguồn được phép; không tự đóng runtime/video/web/giám sát cá nhân. Đây không là bộ numerical gates mặc định cho mọi experiment tương lai. G0 là điều kiện trước training trong proposal; G1–G3 là readiness dữ liệu đánh giá, G4 là bằng chứng run, G5 là quyền final evaluation; toàn bộ cùng quality gates phục vụ xét promotion. Không yêu cầu candidate FINISHED trước implementation. Thứ tự/chấp thuận từng hành động theo training contract và approval riêng; không tự bỏ yêu cầu holdout của E004.

| Gate điều kiện | Trạng thái hiện tại / điều kiện đề xuất |
|---|---|
| G0 | Metrics/recipe/protocol được owner approve trước training; hiện còn Draft |
| G1 | V7 và holdout riêng accepted với rights/QA/pins/không unresolved overlap; v7 local đã đạt, holdout thiếu |
| G2 | Holdout independent với E001–E004 theo provenance/lineage/person/session/room; chưa có |
| G3 | Đề xuất mỗi target test≥100 known P và 100 N; ≥10 independent groups, P/N mỗi loại ở≥5 groups; ≥2 camera/room contexts xác minh. Không lấy train 233 phone P hoặc 100 consecutive frames thay test support |
| G4 | Candidate FINISHED, smoke/resume/reload PASS, full bundle đủ backbone+head/preprocess/targets/threshold và version pins; hiện chưa E004 implementation/run |
| G5 | Một candidate/config/checkpoint/protocol/holdout freeze; owner cấp một final evaluation, guard chặn lặp kể cả đổi output; chưa triển khai cross-output holdout access |

G0–G5 đủ mới đủ điều kiện xét; proposal quality gates dùng AND:

| Gate quality Draft | Giá trị đề xuất, chưa Accepted |
|---|---|
| M1 | Mỗi target precision≥0.85, recall≥0.80, FPR=`FP/(FP+TN)`≤0.10 |
| M2 | AP mỗi target≥0.80, macro AP≥0.85 |
| M3 | Macro masked BCE≤0.90×constant train-prevalence control BCE trên cùng holdout |
| M4 | Predefined slices desk/small-partial phone, looking-side-forward, crowded, đọc/viết/chống đầu negatives; mỗi target/slice đủ≥20 P/20 N từ≥3 evidenced groups; recall≥0.70, precision≥0.80, FPR≤0.15 |
| M5 | Cluster bootstrap 95% CI: lower recall≥0.65, lower precision≥0.70, upper FPR≤0.20; resample whole groups 5.000 lần seed 42, percentiles 2.5/97.5,≥95% resamples có valid denominators |
| M6 | Classifier benchmark local pinned: batch 1/4 CPU threads, 10 warm-up/500 lượt trên development crops frozen; p95≤200 ms/crop, peak RSS≤1 GiB. Timing decode/letterbox/normalize/forward, startup riêng; không video SLA hoặc số đã đo |
| M7 | Rights/license/scope, restore/checksums/full model bundle và owner promotion record PASS |

Support/independence/CI thiếu hoặc precision null ⇒ INCONCLUSIVE/Continue, không quality PASS. Nonfinite/integrity/protocol sai ⇒ evaluation không hợp lệ. Không chọn slice theo predictions/đổi sampling để đủ số hoặc dùng macro bù target yếu. Bootstrap không chứng minh provenance independence.

Proposal development “bước nhảy” trước đây: phone recall+0.20, looking+0.15, precision không giảm>0.05, FPR không tăng>0.05; added 37 phone recall≥0.60. Đây là Draft trên cohort/comparator cần freeze lại theo v7; không Accepted hoặc independent-gain claim. Gates phải chốt trước nhìn kết quả mới, không hạ sau test để promotion.

## 3. Việc cần làm tiếp theo

1. Inventory matrix đủ 375 new train đã có ở audit bổ sung; tiếp tục đóng taxonomy/QA/provenance còn unknown và thiết kế dữ liệu evaluation mới theo policy owner, không random-split lại release. Đây là bước data, không tự sửa recipe để bỏ qua thiếu evidence.
2. Owner chốt comparator, recipe/compute, numerical gates và holdout/use scope với exact versions/pins. Có thể đề xuất experiment local chẩn đoán giới hạn nếu owner chọn, nhưng không tự thu hẹp mục tiêu E004/generalization.
3. Triển khai phần fine-tune/checkpoint/resume/evaluator đã duyệt, meaningful synthetic tests và smoke; chạy matched control/candidate với approval riêng.
4. Review development evidence theo cùng labels/masks, freeze một candidate trước final evaluation riêng. Selected chỉ sau đủ evidence/gates và owner ký decision.

TBD owners đều là chủ repository: `TBD-E004-RECIPE/COMPUTE` (biến/compute chưa duyệt), `TBD-E004-COMPARATOR` (cohort/group mapping chưa freeze), `TBD-E004-HOLDOUT-SOURCE` (data rights/provenance/support chưa đạt), `TBD-METRIC-01` (numerical gates chưa Accepted). Agent chuẩn bị proposal có phương án/chi phí/evidence/acceptance, không bắt owner làm thủ công hoặc coi bản Draft là approval.
