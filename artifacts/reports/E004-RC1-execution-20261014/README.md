# E004-RC1 — Initialization × learning rate

**Bốn runs FINISHED và development reload PASS. Khuyến nghị Continue research, chưa Selected.** [Approval](owner-approval.json), [plan](../../../configs/experiments/E004-RC1-20261014/plan.yaml), [execution companion](../../../configs/experiments/E004-RC1-20261014/EXECUTION.md). Test 11/reserve 199 vẫn đóng; không tự promotion.

Implementation đã qua 46 training regression tests và Ruff/strict mypy: [software validation](software-validation.json). [Source cũ](original-source-snapshot.json) bảo toàn identity E004 trước sửa; source mới có identity riêng. Không reseal old run/config/approval.

Đã freeze configs và kiểm inputs: [smoke preflight](smoke-preflight.json), [main preflight](main-preflight.json). [Smoke/recovery PASS](smoke-acceptance.json) dùng 1.482,825 giây trong trần 1.800 giây. [Trạng thái](execution-state.json) FINISHED. CLI logs ở outputs/E004-RC1-execution-20261014/cli-logs; history/checkpoints/diagnostics ở outputs từng ID. [Results và contrasts đầy đủ](results.json), [learning curves local](../../../outputs/E004-RC1-execution-20261014/learning-curves.html).

| Main run | Head khởi tạo | LR layer4 |
|---|---|---:|
| E004-RC1-R-H | Shared random head E004 | 0,0001 |
| E004-RC1-W-H | LP best epoch10 FC | 0,0001 |
| E004-RC1-R-L | Shared random head E004 | 0,00001 |
| E004-RC1-W-L | LP best epoch10 FC | 0,00001 |

Giữ 716 train/71 selection, diagnostic 49/comparator 48/added 35; input 224, BN eval, AdamW/head LR 0,001/weight decay 0,0001/batch 16/seed 42. Trần main 2 giờ mỗi run, tổng smoke/recovery 30 phút. Warm branches có thêm lịch sử học head; contrasts đo initialization/pipeline thực dụng trên development đã dùng, không independent causal/generalization claim. Không sửa parent configs, labels, splits hoặc quota waiver.

## Kết quả selection 71

Mỗi run hoàn tất 11 epochs và chọn best epoch 1, đúng minimum BCE ở completed epochs. Threshold giữ 0,5; phone 27 P/33 N/11 U, looking 28 P/38 N/5 U. Unknown được mask.

| Model | BCE ↓ | Macro AP ↑ | Phone precision / recall | Looking precision / recall | Phone / looking FPR |
|---|---:|---:|---|---|---|
| Frozen LP cũ, tham chiếu | 0,67785 | 0,57537 | 58,8% / 37,0% | 60,0% / 32,1% | 21,2% / 15,8% |
| R-H, random / LR cao | 0,70932 | 0,54123 | 45,5% / 18,5% | 33,3% / 7,1% | 18,2% / 10,5% |
| W-H, warm / LR cao | **0,65365** | **0,60763** | 62,5% / 37,0% | 54,5% / 21,4% | 18,2% / 13,2% |
| R-L, random / LR thấp | 0,71229 | 0,46948 | 40,6% / 48,1% | 57,1% / 28,6% | 57,6% / 15,8% |
| W-L, warm / LR thấp | 0,72298 | 0,58214 | 56,3% / 33,3% | 50,0% / 21,4% | 21,2% / 15,8% |

W-H là arm tốt nhất theo primary BCE và macro AP của matrix. So frozen LP, BCE giảm 0,02420 và macro AP tăng 0,03226, phone recall bằng nhau nhưng looking recall giảm 10,7 điểm phần trăm. Vì vậy không gọi W-H cải thiện mọi operating behavior hoặc là model ready. Frozen LP là tham chiếu historical đã có, không train lại trong study.

## Contrasts và nguyên nhân đã kiểm

| Contrast, candidate trừ control | Delta selection BCE ↓ tốt | Delta macro AP ↑ tốt | Kết luận descriptive ở seed 42 |
|---|---:|---:|---|
| W-H trừ R-H: warm head, LR cao | −0,05568 | +0,06640 | Initialization/pipeline ảnh hưởng rõ trong study; warm head hữu ích ở recipe LR cao |
| W-L trừ R-L: warm head, LR thấp | +0,01069 | +0,11266 | Ranking cải thiện nhưng BCE xấu hơn; hiệu ứng không đồng nhất giữa metrics |
| R-L trừ R-H: giảm LR, random head | +0,00296 | −0,07175 | LR thấp không giúp selection; phone recall tăng kèm FPR cao |
| W-L trừ W-H: giảm LR, warm head | +0,06933 | −0,02549 | LR thấp kém hơn với warm head ở recipe này |

**Giả thuyết warm head được hỗ trợ một phần; giả thuyết chỉ giảm LR để cứu model không được hỗ trợ ở 1e-5 này.** Không suy mọi LR thấp đều sai, mọi warm start đều tốt hoặc đã chứng minh feature distortion là cơ chế. LP parent đã chọn epoch bằng chính selection 71; study là refinement trên development đã biết, một seed, không độc lập hoặc significance/stability claim.

R-H tái lập **toàn bộ history/metrics và predictions của năm cohorts** E004-V9-L4 cũ, best model tensor digest cũng khớp. [Comparator parity](comparator-parity.json). Như vậy schema mới/diagnostics không làm lệch recipe cũ; chênh lệch ở nhánh khác đi cùng variables được duyệt.

### Overfitting và quan sát sớm

| Arm | Selection BCE epoch 0 | Step 15 / step 30 | Epoch 1 / epoch 11 | Train BCE epoch 11 |
|---|---:|---|---|---:|
| R-H | 0,77865 | 0,71973 / 0,79067 | 0,70932 / 2,37671 | 0,000179 |
| W-H | 0,67785 | 0,76575 / 0,67879 | 0,65365 / 2,09087 | 0,000173 |
| R-L | 0,77865 | 0,74140 / 0,75116 | 0,71229 / 1,35906 | 0,021393 |
| W-L | 0,67785 | 0,73453 / 0,75666 | 0,72298 / 1,35577 | 0,015243 |

Epoch 0 warm branches khớp BCE/AP parent LP đúng hoàn toàn; backbone không mang adaptation state/optimizer từ parent. W-L làm xấu BCE so chính initialization LP ngay ở tất cả điểm đã đo, gồm completed epochs; W-H tốt lên ở epoch 1 rồi overfit. Các điểm quan sát sớm đã đo không tìm được checkpoint tốt hơn W-H epoch 1 theo BCE. Không loại trừ cửa sổ chưa đo giữa steps; không dùng hậu nghiệm để đổi checkpoint selection hoặc chạy thêm lịch mới.

LR thấp giảm tốc độ ghi nhớ train nhưng không tạo gain selection bền ở matrix này. Không có cơ sở tăng epochs; early stopping đã giữ checkpoint đầu cho cả bốn arms. [Canonical curves](../../../outputs/E004-RC1-execution-20261014/learning-curves.html) có y scale riêng được ghi rõ, không so độ dốc trực quan giữa các panel.

### Family và diagnostic cohorts

| Arm | Phone TP ngoài CF-Q072 / 8 P | Looking TP ngoài CF-Q072 / 11 P |
|---|---:|---:|
| R-H | 1 | 0 |
| W-H | 1 | 3 |
| R-L | 2 | 3 |
| W-L | 2 | 2 |

Phone TP W-H tăng từ 5 lên 10 so R-H, cả năm TP thêm nằm trong CF-Q072; ngoài family lớn vẫn 1/8. Looking có gain ngoài CF-Q072 nhưng còn bỏ sót 8/11. Đây là diagnostic hậu nghiệm trên support nhỏ, không M4/independent slice. CF-Q072 vẫn 45/71 crop; không loại family khó hoặc đổi membership để đẹp số.

| Diagnostic, BCE / macro AP | R-H | W-H | R-L | W-L |
|---|---|---|---|---|
| Diagnostic 49 | 0,57700 / 0,82472 | 0,60210 / 0,80814 | 0,62581 / 0,78556 | 0,64147 / 0,80218 |
| Comparator 48 | 0,58881 / 0,82555 | 0,61302 / 0,80856 | 0,62893 / 0,78971 | 0,65752 / 0,80403 |
| Added 35 | 0,63959 / 0,70896 | 0,66865 / 0,67005 | 0,66586 / 0,71687 | 0,73969 / 0,71618 |

Các subsets diagnostic chồng nhau và chưa độc lập; không cộng support hoặc dùng chúng chọn winner thay selection. W-H cải thiện selection nhưng giảm quality diagnostic so R-H: cohort dependence vẫn hiện diện.

## Khoảng cách promotion và hướng tiếp

M1 yêu cầu precision ≥85%, recall ≥80%, FPR ≤10% mỗi target; cả bốn arms còn cách xa trên selection. M2 yêu cầu AP mỗi target ≥0,80 và macro ≥0,85; W-H macro 0,60763 và AP phone/looking 0,67092/0,54435. M3 yêu cầu BCE ≤0,9 constant train prevalence; mức cần khoảng 0,62765, W-H là 0,65365 (ratio khoảng 0,9373). Đây là development comparison, không final-test gate result.

Phép tính independent từ cached scores khớp confusion/AP/BCE; xét mọi threshold tại unique scores cho thấy **không target nào của bốn arms có điểm đạt đồng thời M1**. Chỉ đổi threshold không đủ. Threshold feasibility chỉ diagnostic hậu nghiệm, không chọn operating point mới. M4 vẫn INCONCLUSIVE; waiver independence/support không miễn chất lượng. Không mở reserve/test cho W-H hiện tại.

Khuyến nghị **Continue research** cho tất cả arms. Giữ W-H là evidence về recipe có ích, chưa freeze candidate promotion và chưa chạy confirmation seeds chỉ để củng cố một gain nhỏ/gắn family. Kết quả giúp loại bỏ hai hướng lặp vô ích ở scope hiện tại: tăng epochs theo recipe cũ và chỉ hạ layer4 LR xuống 1e-5.

Bước tiếp hợp lý là **đo targeted coverage trên train và đối chiếu selection**, dựa vào audit thị giác đã có: desk/held/partial phone, calculator/pen hard negatives, looking ngoài own-workarea so đọc/viết, evidence native/224 và context nhiều người. Công cụ draft matrix và shortlist; owner review batch/ngoại lệ, không annotate lại toàn bộ corpus. Chưa đặt quota, tuyển nguồn, đổi labels/splits hoặc training variables mới từ kết quả này.

Nếu matrix cho thấy train thiếu tình huống rõ tương ứng, ưu tiên bổ sung khác family/camera với hard negatives cùng pose. Nếu train có đủ evidence rõ nhưng classifier vẫn nhầm attribution/own-workarea, đề xuất input/representation riêng trước khi implementation. Resolution chỉ ưu tiên khi evidence nguồn còn mà mất tại 224; không cứu source vốn thấp chi tiết. Cần thiết kế/approval mới cho các changes/run đó. Study RC1 được duyệt đã hoàn tất, không tự chạy thêm arms/seeds.

## Validation, thời gian và bảo toàn

[Run integrity](run-integrity.json) PASS exact code/config/tensors/checksums, best raw minimum completed-epoch BCE, 45 steps/epoch, shared sampler, lịch diagnostic và budgets. [Development reload](evaluation-verification.json) PASS cả bốn cohorts mỗi model; max absolute prediction delta 0, masks/decisions/metrics exact parity. Không benchmark lại vì architecture/input không đổi; không tuyên bố SLA video hoặc latency mới.

Recorded main time: R-H 1.104,728 s; W-H 1.110,658 s; R-L 1.177,997 s; W-L 1.051,887 s. Tổng main 4.445,270 s (74,1 phút), smoke/recovery 1.482,825 s (24,7 phút); **tổng recorded training 5.928,095 s (98,8 phút)** dưới trần 30.600 s. Không gồm toàn bộ review/software checks/điều phối/reload/backup; không suy thời gian khoa học tiếp theo từ số giờ compute này.

Smoke W-L dùng revision B2 để kết hợp interrupt/resume và phần budget còn lại; configs đầu giữ bytes. [Budget revision](smoke-budget-revision.json), [recovery boundary](recovery-boundary.json). Real smoke chứng minh preserve completed epoch/tiếp tục epoch 2; full uninterrupted/resumed tensor/optimizer/RNG parity được synthetic fixtures kiểm, không gọi real smoke là đã chạy một duplicate đối chứng nữa. [Verification notes](verification-notes.json) giải thích pretrained ImageNet thiếu BN counters, đã kiểm default 0 và stored buffers exact; không đổi trainer sau freeze.

[Source snapshot mới](source-snapshot.json), [restore verification cũ/mới](source-restore-verification.json), [reproduction locators](reproduction-inputs.json). [Backup local/restore](backup-receipt.json) và [cleanup](cleanup-receipt.json) có receipts sau khi seal kết quả; backup cùng ổ chưa chống hỏng ổ. Git chưa stage/commit; media/models không đưa vào Git và không upload. Software PASS không thay owner model acceptance.
