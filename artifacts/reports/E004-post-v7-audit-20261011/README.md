# Audit E004 sau release V7 — 2026-10-11

**V7 hợp lệ cho local classifier research; E004 vẫn Draft và chưa đủ evidence để run với mục tiêu promotion/generalization.** Audit mới đóng inventory coverage của toàn bộ 375 actual new-train crops, không tuyên bố đã đo đầy đủ mọi phenotype chưa có annotation. Điểm thiếu lớn nhất là new-development/independent holdout, taxonomy/QA224 toàn cohort và independence. Hai ZIP owner cung cấp có giá trị để tiếp tục shortlist, không tự trở thành nguồn holdout độc lập.

Quyền sử dụng cả hai ZIP đã được owner xác nhận ngày 2026-10-11; tiếp tục xử lý local và không hỏi lại quyền. Không train, inference mới, mở media test 11, sửa labels/splits/gates/pins hay upload. Core trainer không đổi. [Freeze/implementation plan Draft](../../../configs/experiments/E004-freeze-proposal-20261011.md) là đề xuất cụ thể để review, không approval.

## 1. Inputs, phương pháp và cách đọc matrix

Đã đọc AGENTS, index/status/TASK, data/training/system/development/reference/operations, decisions registry, E004 proposal/YAML, original ADR-011/012/013/017/018 và E004 preparation qua Git `ab34b32`, V7 pointer/approval/verification, V6/V7 manifests/ledgers, audit 2026-10-10, QA224/ownership/review/pairs archived đúng SHA, trainer/config/loss/evaluator/checkpoint và tests liên quan. Original lịch sử có câu “chưa V7” phản ánh thời điểm cũ; release receipt V7 ngày 2026-10-10 quyết định trạng thái dữ liệu hiện tại. Không lấy kết luận stale ở cuối preparation thay receipt.

Định nghĩa cohort: **V7 manifest usage=train và sample_id không thuộc full V6 review ledger**, không chỉ ID mới so train 317 hoặc glob crop folder. Kết quả đúng 375, canonical P/N/U lấy strict codec/manifest; source/crop join exact SHA. Đã hash từng 375 current train crop và kiểm metadata pins trong release pointer; không rehash toàn test/media archive hoặc dựng lại release đã accepted. Metadata archive được đọc theo original path, kiểm blob SHA/size; không extract toàn archive.

Đầu ra:

- [Matrix CSV 375 dòng](coverage-matrix.csv): thuận tiện lọc; [JSONL đầy đủ evidence/unknowns](coverage-matrix.jsonl).
- [Aggregates](coverage-summary.json), [pairs](pairs.json), [comparator48 verification](comparator48-verification.json), [added development](added-development-verification.json), [cached baseline48](cached-comparator48-baseline.json).
- [Audit hai ZIP và 40 raw shortlist items](source-zip-audit.json), [visual observations 8 mẫu](source-visual-review.json), [input pins](input-pins.json), [validation](validation.json), [phương pháp tái lập](build_evidence.py).

`P/N/U` là **actual canonical counts**. `registered_group`/conservative family là boundary chống leakage đã accepted, **không** independent person/session/room. `new_independence_proven=false` nghĩa chưa có proof, không khẳng định các cảnh thật sự phụ thuộc. `phenotypes_explicit_draft`, bucket và literal text mentions là metadata phân tích/Draft; không label approval. Null/unknown không là absent/negative. Không suy independent groups từ unique SHA, filename hoặc project mới.

## 2. Coverage actual 375 new-train

| Target / tổ hợp | Actual counts | Unknown hoặc giới hạn |
|---|---:|---|
| Phone P / N / U | **141 / 93 / 141** | 37,6% phone cells unknown |
| Looking P / N / U | **97 / 163 / 115** | 30,7% looking cells unknown |
| Fully-known / partially-known / U-U | **119 / 256 / 0** | 31,7% fully-known; 256 unknown cells, không fill N |
| PP / PN / NP / NN | **20 / 13 / 9 / 77** | Không đủ suy completeness mọi slice |
| PU / NU / UP / UN | **108 / 7 / 68 / 73** | Target order phone→looking |
| Distinct source images / crop hashes / components | **327 / 375 / 289** | Không là 289 sessions |
| Parent-linked | **37 crops / 16 components** | 338 crops ở 273 components không chứa V6 ledger ID; chưa proof independence |
| Verified new independent groups / exam camera contexts | **0 / 0** | Group video/session/room/subject IDs null ở 375/375 |

V7 toàn train 689 vẫn phone 233/184/272, looking 210/277/202 và fully-known 215. Train317→689 là +372 net sau parent changes, khác gross375 new-train. Accepted val 49/test11 không có validation mới. Những counts này không đóng G3 test.

### Theo source family/provider

Family vận hành ở matrix là whole-family conservative component; source/provider chỉ taxonomy provenance. Các group counts dưới đây **không cộng để tìm total289** vì component có thể nối nhiều providers.

| Provider, new crops | Components chạm tới | Phone P/N/U | Looking P/N/U | Fully-known |
|---|---:|---|---|---:|
| Classroom Attitude 84 | 62 | 68/10/6 | 12/16/56 | 22 |
| Open Images train 104 | 96 | 27/36/41 | 24/53/27 | 36 |
| COCO train 2017 37 | 36 | 20/8/9 | 9/11/17 | 11 |
| Commons classroom gapfill 46 | 19 | 24/8/14 | 11/20/15 | 17 |
| RF v1 30 | 23 | 2/12/16 | 15/15/0 | 14 |
| SCB Head 32 | 24 | 0/1/31 | 22/10/0 | 1 |
| SCB HRW 22 | 21 | 0/3/19 | 1/21/0 | 3 |
| Student Behaviour 12 | 10 | 0/12/0 | 0/12/0 | 12 |
| Exam Cheating keaor 6 | 4 | 0/3/3 | 2/4/0 | 3 |
| WMF public video 2 | 1 | 0/0/2 | 1/1/0 | 0 |

Source confounding vẫn đáng kiểm: new Classroom phone 68/78 known là P (87,2%); new Head looking 22/32 P; HRW 21/22 N. Nhãn Student mới toàn NN giúp negatives nhưng không thêm phone P hay looking P. Đây là distribution evidence, không causal proof model học shortcut. Tăng provider count không chứng minh camera/session diversity.

### Theo domain và ownership

| Domain metadata giữ nguyên | Crops | Phone P/N/U | Looking P/N/U |
|---|---:|---|---|
| classroom_or_exam_context | 196 | 73/43/80 | 54/82/60 |
| auxiliary_out_of_exam | 127 | 46/38/43 | 28/56/43 |
| classroom_or_learning_context_pending_anchor_review | 30 | 14/6/10 | 8/14/8 |
| public_auxiliary_or_classroom_context_pending_review | 14 | 1/6/7 | 5/8/1 |
| auxiliary_workshop | 3 | 3/0/0 | 1/1/1 |
| educational_workshop_context | 2 | 1/0/1 | 1/1/0 |
| auxiliary_home_learning | 1 | 1/0/0 | 0/1/0 |
| auxiliary_educational_event | 1 | 1/0/0 | 0/0/1 |
| computer_room_education_context_unverified | 1 | 1/0/0 | 0/0/1 |

Tag rộng classroom196 không chứng minh primary exam camera: chỉ 73 phone P/43 N trong tag này, 80 phone U. 52 ngoài hai tag lớn không được tự cộng thành primary domain; 44 giữ tên domain pending lịch sử và 1 computer-room-unverified cần classification domain rõ hơn. Tên pending không đảo acceptance crop/label hiện hành: canonical records đã owner accepted, domain taxonomy chưa hoàn chỉnh.

Canonical semantics bảo đảm 141 phone P có approved anchor-link evidence và 93 N có observation review. **Ownership subtype** chỉ có historical Draft finding crop-SHA khớp ở34 crops:26 direct hand/own desk/lap,1 old recrop/anchor pending finding,7 observation/ownership unknown;341 chưa subtype taxonomy. Finding pending cũ không là blocker hiện hành sau owner recrop approval. Không diễn giải “anchor-link accepted” thành confirmed ownership cá nhân hoặc camera/session metadata.

### Phenotype và input224

| Evidence layer | Actual count với definition này | Phần unknown |
|---|---:|---|
| Historical acquisition A / B / C / D hints, exact current-crop join | 56 / 74 / 99 / 36 | 110 không có bucket join; bucket không là full phenotype |
| A phone P/N/U; B phone P/N/U | 32/24/0; 37/34/3 | A không bảo đảm mọi P đều desk-phone; B không bảo đảm mọi device đều small tại224 |
| C looking P/N/U; D fully-known | 48/51/0; 4/36 | D có PP2/PN1/NN1, không 36 co-occurrence |
| Accepted complete phenotype taxonomy | **0/375** | Không có đồng nhất phone-context/visibility/workarea/head-direction/size bins cho toàn cohort |
| QA224 findings crop-SHA khớp | **104/375 = 27,7%** | **271/375 = 72,3%** không finding quality áp dụng được |
| Trong104 QA224 Draft | **94 clear / 10 ambiguous** | Không đẩy10 ambiguous thành negative hoặc loại khỏi train |
| Historical recrop QA hash mismatch | **4** | Nằm trong271 unknown; review cũ không kế thừa |
| Phone ROI224 có tọa độ Draft | **3/375** | 372 không ROI; không có accepted numeric size bins |

Release verification đã PASS generation/pixel equality input224 cho375; quality nhìn thấy tại224 là phép đo khác. Audit này **không visual-review lại375 ảnh**: inventory đủ375, những chiều chưa có evidence vẫn unknown. Cần batch QA mới theo exact crop/input hashes để có taxonomy phủ toàn bộ.

Literal-search reasons phục vụ tìm review, không là slice enrollment hoặc absence proof: desk mentions41 crops (phone 38P/1N/2U), small12 (12P), partial16 (7P/2N/7U), crowded53, own-workarea100, read/write80. Counts có overlap; chữ “che tay”, “không đủ own workarea” có thể xuất hiện trong câu phủ định nên **không dùng các số này làm actual phenotype support hay G/M PASS**. Matrix giữ exact matched text và review reasons để owner/agent đối chiếu. Explicit R8 phenotype tags cũng Draft; không tự gán taxonomy cho các crop khác.

### Matched-pair quality

22 raw target-specific P/N combinations trên 19 exact source images, 39 distinct endpoints: phone 5 pairs/5 images; looking 17 pairs/16 images. Cả hai endpoints giữ broad classroom tag ở 4 phone pairs và 12 looking pairs; tag đó chưa chứng minh primary exam camera. Exact-image bảo đảm cùng ảnh, thường là người khác nhau; không same-person counterfactual, không 22 sessions, không proof camera diversity. Metadata/context QA chưa xác nhận matched primary-domain quality toàn bộ 22.

R5 162 proposals chỉ138 còn cả hai endpoints actual train và đúng P/N;24 invalid current endpoints/polarity. Trong138:132 source-context (95,7%),5 same-image,1 same-scene. `source_context` là match yếu khác người/cảnh/camera; không session-match. Không cộng138+22 hoặc cộng R8/public pairs vì overlap. Đề xuất quality rubric Draft: Q0 source-context, Q1 exact-image polarity, Q2 verified same camera/workarea + attribution/context/224 matching, Q3 independent-family contrasted conditions. Hiện đã đo Q0/Q1; **chưa có complete Q2/Q3 enrollment accepted**, không gán zero physical pairs thật sự tồn tại.

## 3. Định lượng gaps và ưu tiên marginal value

Không lấy review budgets80/80/100/40 lịch sử làm accepted quota. Không thể tính “thiếu bao nhiêu desk-phone” theo quota không có authority; có thể tính **missing evidence** dưới đây. Expected marginal value là hypothesis định tính, không dự báo ΔAP/recall thiếu run.

| Ưu tiên | Gap đã đo | Bổ sung/shortlist đề xuất | Expected marginal value và điều kiện dừng |
|---|---|---|---|
| P0 evaluation | 0 new-development accepted;0 independent holdout accepted; comparator13 groups tập trung | Reserve các families mới trước train, verify provenance/session/room/camera; whole-family dev và package holdout riêng, blind two-target QA | Cao nhất cho **khả năng kiểm hypothesis/claim**, chưa hứa training gain. Thêm10k train cùng family không giảm gap này. Thiếu provenance ⇒ giữ research pool, không freeze holdout. |
| P1 taxonomy/QA | 271 quality224 unknown;372 ROI chưa đo;256 target cells U;44 domain tags pending +1 unverified | Agent chuẩn bị batch evidence hiện có, prioritize desk/small/partial/crowded/own-workarea và recrop4; annotate analysis taxonomy/source→crop→224, giữ U nếu không rõ | Chi phí acquisition thấp; tăng đo được coverage và loại uncertainty khỏi claim. Max256 cells **có thể xem lại**, không hứa256 thành known. QA không thay đổi accepted labels thiếu evidence/version approval. |
| P1 new contextual negatives | New Classroom phone 68P/10N; PP20/PN13/NP9; bucket D chỉ4 fully-known | Cùng room/workarea/posture: mobile on desk/held/at-ear đối với pen/calculator/book/hand-to-face, phone người khác; cả bốn target combinations | Dự kiến giúp attribution/shortcut control hơn tăng held-phone dễ. Ưu tiên một verified family có cả P/N hơn20 variants cùng frame; Δmetric unknown. Không gán N từ empty labels. |
| P1 looking contexts | Head 22P/10N, HRW 1P/21N; looking-side/crowded subtype incomplete | Side/forward/up ngoài own page đối với đọc/viết/head tilt/chống đầu trong cùng camera; drafting từ behavie Look Around/Normal/Bend | Tiềm năng cao nếu crop giữ own workarea và units được dựng lại; dùng classroom thật cho dev là giá trị evaluation, không gọi chưa proven family là independent. |
| P2 small/partial phone | B74 chỉ acquisition hint;3 ROI224 Draft;10 QA ambiguous | StudentClassroomBehavior phone/Using_phone và behavie phone; source→anchor→crop→224 QA + size/visibility metadata | Có nhiều raw opportunities nhưng small source object box không là person crop, downsampling/blur còn giới hạn. Nếu native evidence thiếu thì U; không tăng resolution/recrop release cũ ngầm. |
| P3 auxiliary/parent variants | 127 auxiliary tag;37 new crops parent-linked;91-crop old Student group vẫn còn | Dùng auxiliary matched negatives chọn lọc; ưu tiên giảm unknown và bổ sung contextual N trước thêm variants | Expected domain marginal value thấp/không rõ khi chỉ cùng scene hoặc ngoài exam; không bù primary holdout bằng stock/COCO/OI. |

Với G3 Draft, package holdout hiện **0 enrolled known P/N** cho mỗi target nên còn tối thiểu100P và100N mỗi target,10 evidenced independent groups, P/N mỗi loại≥5 groups và≥2 contexts. Đây là deficit so **Draft test criteria**, không quota train hoặc kết luận raw sources không có100 positives. Các slices M4 còn0 accepted enrolled support dưới protocol freeze; không dùng raw text/bucket counts để trừ20P/20N. Slice overlap có thể chia sẻ records; không cộng budgets tùy ý.

Bổ sung theo small pilot batch diverse-family, review yield/unknown/provenance/224 trước tiếp nhận thêm; không đi theo số ZIP/annotation. Owner nghiệm thu batch/exceptions, agent chuẩn bị anchor/group/QA Draft bằng công cụ đã có, không yêu cầu owner annotate từng ảnh. Quyết định source roles/splits vẫn cần exact policy; audit này chưa tạo membership release mới.

## 4. Hai ZIP Roboflow — kết quả local audit và shortlist

Web metadata đã kiểm ngày 2026-10-11 tại [StudentClassroomBehavior](https://universe.roboflow.com/ljx-6evwu/studentclassroombehavior-fe7wq), [behavie](https://universe.roboflow.com/class-zsme9/behavie). Version/license trong data.yaml/README khớp hai projects owner đưa; owner use authorization được lưu riêng. License badge không cung cấp session/room provenance. Không hỏi lại quyền.

| ZIP | Exact SHA256 | Ảnh train/valid/test | Structural findings |
|---|---|---|---|
| StudentClassroomBehavior.v1i.yolov8.zip | `392052c71bcbfd084a330c3ff8cd1f28a1087e30afeef107fe85ab14acbf400d` | 7081/1020/848 =8949 | 2 invalid files/2 zero-size lines; no missing/orphan/empty/decode failure; data.yaml trùng3 ZIP entries cùng bytes |
| behavie.v2i.yolov8.zip | `b90b3d95eb671bd0e454723036bcf62596e0ebafd8616e69a95c894576433057` | 2879/699/55 =3633 | 296 empty label files;0 strict-invalid/missing/orphan/decode failure |

Toàn 12582 ảnh được decode và parse nhãn bằng validator active; file invalid không đóng góp partial class stats. Mỗi ZIP0 exact/RGB duplicate groups; giữa hai ZIP0 shared exact/RGB hashes. Filename lineage heuristic: Student7353 keys/1596 repeated groups (không cross upstream split); behavie3595 keys/38 repeated groups,**34 qua upstream split**. Đây là lineage flags, không session count hoặc automatic groups.

Cached dHash64 distance≤4 screening với798 fingerprint records metadata V6/V7: Student**2004/8949** ảnh bị flag;1799 có matches current train,1348 review-only,542 excluded,31 val,2 test. Categories overlap, không cộng. Behavie**11/3633**, đều match review-only. No exact-byte matches với V7 source hashes. Fingerprint pool không phủ mọi public/new source và chưa exhaustive original upstream; ngoài threshold không proof disjointness. **Không xem test 11 media/predictions**, chỉ stored source fingerprint metadata. Các evaluation-family flags quarantine khỏi training cho tới whole-family review; Student còn rủi ro nhập Discuss qua re-export, không mở membership nguồn đã loại tự động.

Raw strict-valid annotations Student: phone 3744, Using_phone9774, turn_head2514; behavie phone 1892, Look Around3839, Normal4959. Đây là boxes, không actual canonical crops/P/N hoặc independent samples. Student phone/Using_phone bbox median13×20/15×18 pixels (min phone 5×3); cần dựng person anchor/context. Behavie phone median72×52, Look Around93×92; không bảo đảm full person/workarea. Behavie export stretch1960×1080; cần QA geometry/evidence, không tự “undo” raw. Empty labels296 không là296 negatives.

Đã xem 4 source-class-stratified hash-first shortlisted samples mỗi ZIP, không representative/full visual audit. Student samples cho thấy phone/Using_phone object boxes nhỏ, turn_head head boxes, writing upper-person box; behavie phone/Look Around/Bend Over The Desk thường upper/head region, Normal upper-person. Cảnh quan sát có cả phòng học crowded và source quality khác nhau; không suy camera/session ID hoặc canonical targets. Chi tiết8 technical IDs/source hashes/notes ở [visual observations](source-visual-review.json); preview local đã dọn sau verification, raw ZIP giữ nguyên Downloads.

**Shortlist40 Draft items** trong source audit:20 mỗi ZIP,4 mỗi class-hint bucket; dedup RGB, loại cached exact/near flags, deterministic source hash order. Student: phone/Using_phone/turn_head/writing/reading; behavie: phone/Look Around/Normal/Bend Over The Desk/Hand Under Table. Không có classifier predictions, không source-class→target mapping. “Không flag” chỉ eligibility để xem, không independence accepted.

Ưu tiên **behavie** cho batch khảo sát contextual P/N/own-workarea vì nhiều behavior contrasts và ít overlap flags hơn trong pool đã kiểm; vẫn cần whole-family provenance và no-random-frame split. **StudentClassroomBehavior** ưu tiên small/partial phone và source unit review; expected independent-domain marginal value còn thấp/unknown vì nhiều near matches và box nhỏ. Chỉ enroll exact crops sau owner batch QA; không tự reserve/gọi một ZIP primary holdout hoặc train toàn bộ12582 ảnh.

## 5. Comparator48, new-development và holdout feasibility

Comparator48 đã verify lại **source/crop/phone/looking target reviews/values/masks/context/rights giữ nguyên** V6→V7; literal group/review version khác. Full retained val 49 mapping14→14 bijective, không merge/split; comparator48 **13 groups**,15 fully-known,phone 16P/19N/13U,looking 17P/11N/20U. Hai groups 21+10 chiếm**64,6% comparator48**; phone P ở4 groups,looking P ở6. Khả thi cho matched development comparison sau owner freeze; không independent holdout và không exact literal identity preservation.

Cached E003 score baseline trên48, không inference: phone TP9/FP2/FN7/TN17,recall 0,5625/precision0,8182/FPR0,1053; looking TP11/FP1/FN6/TN10,recall 0,6471/precision0,9167/FPR0,0909. Nếu giữ development Draft +0,20/+0,15 **relative cached48**, phone cần≥13/16TP vàlooking≥14/17TP (net+4/+3), kèm precision không giảm>0,05/FPR không tăng>0,05. Với denominators19N/11N, thêm1FP đã vượt FPR allowance0,05 cả hai targets. Đây là arithmetic feasibility, không model forecast/Accepted gate; candidate – control adaptation report riêng.

Added37 V6 so V5 có phone 10P/19N/8U; retained36 V7 phone 9P/19N/8U; comparator-retained35 phone 9P/18N/8U. Draft recall≥0,60 khi dùng subset35 nghĩa≥6/9 TP, không “60% của37 crop”. Exact lists/support đã lưu; endpoint thay đổi cần owner freeze trước run, không gọi same37. Historical metric val 50→49 tăng recall do annotation/cohort, không E004 gain.

New-development: **chưa có accepted new records**, nguyên V7 val 49 inherited. Không đổi split V7 để vá. Hai ZIP có raw candidate pools nhưng session/room/camera/person provenance chưa supplied trong payload; new-development whole-family có thể chuẩn bị, acceptance/sampling chưa freeze. Holdout: feasibility **chưa chứng minh**; quyền sử dụng đã có, independence/lineage/support/use-once guard còn thiếu. Full protocol recommendation ở [freeze proposal](../../../configs/experiments/E004-freeze-proposal-20261011.md).

## 6. G0–G5, M1–M7 và numeric authority

ADR-011/012/013/018 semantics/codec/masks/mobile-only Accepted; V7 owner receipt Accepted đúng local release. E004 recipe/comparator/numeric model gates và ADR-017 **Draft**, YAML pins vẫn null và approvals false. Original ADR017 yêu cầu G0–G3 trước E004 run promotion-oriented; data release approval không bỏ yêu cầu này. Design approval trước implementation, smoke sau design, không chờ candidate FINISHED để duyệt design.

| Gate | Authority / hiện trạng | Kết luận |
|---|---|---|
| G0 | Draft recipe/compute/metrics/protocol, chưa exact approved ExperimentConfig | OPEN |
| G1 | V7 local Accepted; holdout QA/rights/provenance/pins/package chưa accepted | PARTIAL, không PASS |
| G2 | Holdout independent với development E001–E004 chưa có proof | OPEN |
| G3 | Draft≥100P/100N mỗi target,≥10 independent groups,P/N≥5 groups mỗi loại,≥2 verified camera/room contexts | Chưa enrolled support; không trừ train 233P |
| G4 | Chưa fine-tune implementation/run/full bundle/smoke-resume-reload evidence | OPEN; E003 head.pt không full adapted model |
| G5 | Chưa candidate/holdout freeze hoặc cross-output use-once guard | OPEN; current evaluator chỉ pin config/checkpoint/data, thiếu package-independent access |

| Quality gate — toàn bộ Draft | Numeric đề xuất **giữ nguyên** | Audit status |
|---|---|---|
| M1 | Per-target precision≥0,85;recall≥0,80;FPR≤0,10 | Chưa E004 final metric |
| M2 | Per-target AP≥0,80;macro AP≥0,85 | Chưa đo; macro không bù weak target |
| M3 | Macro masked BCE≤0,90×constant **train-prevalence** BCE cùng holdout | Chưa đo; không fit prevalence từ holdout |
| M4 | Predefined desk/small-partial/looking-side-forward/crowded/read-write-rest contexts; mỗi applicable target/slice≥20P/20N từ≥3 evidenced groups;recall≥0,70,precision≥0,80,FPR≤0,15 | Enrollment chưa freeze; positive-only slice không đủ |
| M5 | Group-bootstrap5.000 seed 42,95%percentileCI;lower recall≥0,65/lower precision≥0,70/upper FPR≤0,20;≥95%valid resamples từng metric | Method/fixtures chưa implemented/approved; bootstrap không proof independence |
| M6 | CPU batch 1/4threads;10warm-up/500measures;p95≤200ms/crop,peakRSS≤1GiB;decode/transform/forward, startup riêng | Chưa benchmark; không video SLA hoặc training-memory guarantee |
| M7 | Rights/software/source scope/restore/checksums/full bundle/owner promotion record | Source local permission có; model evidence/decision chưa có |

AND tất cả quality gates sau eligibility đủ; null/insufficient support ⇒ INCONCLUSIVE/Continue, không quality PASS. Nonfinite/integrity/protocol sai ⇒ evaluation invalid. Không hạ thresholds, sửa pins, đổi slices/sampling hay bỏ holdout để pass. Development targets +0,20phone/+0,15looking/precision−0,05/FPR+0,05/added-phone≥0,60 cũng Draft cần comparator endpoint freeze riêng.

## 7. Implementation/reproducibility và bàn giao

[Plan](../../../configs/experiments/E004-freeze-proposal-20261011.md) có8 work packages,10 nhóm meaningful tests, recipe control/candidate, objective với train-wide known denominators, explicit BN-affine policy, full-state checkpoint/resume/cache invalidation/evaluator/bundle và local holdout-use-once registry. Tất cả choices mới là Draft; trainer/config/model/evaluator hiện chỉ frozen-feature full-batch head, không thể layer4 chỉ bằng YAML.

Control và candidate cần cùng data/order/head init/input/optimizer-head/budget/protocol/compute; chỉ layer4 adaptation thay đổi. Giữ legacy objective/config/evaluator identity; code mới có identity mới. Reproducibility lưu code/config/data/split/encoding/weights/cohort/protocol/seed/environment/command/status/checkpoint/metrics/checksums và owner decisions, không reseal historical evidence.

Audit checks, output digests và preservation ở [validation](validation.json); methodology/source provenance ở [pins](input-pins.json). Không chạy ML suite/smoke/train/inference vì không đổi runtime training code. Report/index/proposal links và diff được kiểm; không stage/commit. Kết quả inventory hoàn thành; taxonomy unknown/protocol/experiment/holdout acceptance là các việc còn mở đã định lượng, không được audit tự chốt.

**Integrity limitation phát hiện khi bàn giao:** `E004-v7-fit-audit-20261010/README.md` có SHA actual `3dfaddaee1c2b905cf59dd510616934b7596a0a38811f3a55fa14199584f7ded`, khác seal expected `ce6cfe937cc357a23b4f61f8a88ad1f46ed0b960589b18cce6633254e08704fd`. Current bytes khớp cả Git HEAD và original archive; mismatch đã có trước task. Không sửa README cũ, seal/pointer hoặc reseal. Historical README seal **không PASS**; các measurement JSON của audit cũ và toàn seal release V7 khớp. Số đo mới tính lại từ exact manifest/ledger và QA blobs/pins có kiểm SHA, không phụ thuộc việc coi README cũ là sealed evidence hợp lệ. Validation ghi exception cụ thể; không gọi toàn historical audit seal PASS hoặc tự bỏ integrity guard để chạy experiment.
