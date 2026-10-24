# Tra cứu kết quả và bằng chứng

Index theo đối tượng; không là bảng metrics hoặc backlog. Hồ sơ đã pin là snapshot, kể cả chữ “next”, “pending” hoặc lệnh CLI cũ. [Status](../../docs/status.md) chỉ công việc hiện hành; [operations](../../docs/operations.md) xử lý historical paths/restore. Không sửa report/card/receipt đã seal để cập nhật tiến độ.

[Nghiên cứu E007 trên V13](e007-v13-research-20261023/README.md): audit lịch sử/code/config, coverage V13 và cached scores E006; hướng representation mới và proposal 4–8 giờ GPU. Chưa train hoặc đổi accepted inputs.

[E007 Colab và kết quả V13](e007-v13-colab-20261024/README.md): smoke và 9 research FINISHED, import/checksums/reload đã kiểm; D1 cải thiện ổn định, phone qua gate cả ba seed, looking chưa qua. Chưa Selected hoặc final test.

[E008 — chuyển phase prototype](e008-v14-colab-20261024/prototype-decision-20261025.md): owner bỏ gate chuyển phase 80/80/20 và chọn G0 seed 20261023; kết quả nghiên cứu giữ nguyên, thiết kế runtime đã duyệt; [bàn giao software/synthetic](runtime-prototype-20261025/README.md), chưa nghiệm thu chất lượng video.

[E008 V14 — kết quả Colab](e008-v14-colab-20261024/results-20261025.md): 4 smoke + 5 research FINISHED; audit metadata PASS, G0 thắng screening, looking chưa đạt. [Ba run G0 đã nhận đủ best/last và kiểm integrity local](e008-v14-colab-20261024/checkpoints-20261025.md); chưa Selected.

[Audit looking E007 ngày 24/10](looking-around-audit-20261024/README.md): cached scores sáu run, visual review lỗi looking tái diễn và upstream context; sửa diagnostics V4/336 px. Snapshot proposal E008 giữ nguyên; approval và dữ liệu mới ở companion V14.

[E006 V12 — training tự động](e006-v12-20261020/README.md): smoke, screening và
xác nhận qua seed theo phạm vi owner duyệt; runner tổng hợp số liệu, agent kiểm và
viết report cuối, test đóng.

## Releases và nghiên cứu dữ liệu

[Release V14 ngày 24/10](dataset-release-20261024-v14/README.md): local accepted, dùng đủ 53 crop mới trong train; loại 2 crop chất lượng kém, chuyển cả 6 nhóm nguồn liên quan sang train. Release dùng tiếp trước E008; validation development thay đổi, pins V13 giữ nguyên.

[Release V13 ngày 23/10](dataset-release-20261023-v13/README.md): parent V14 và input E007, local accepted sau audit V12; dùng đủ 21 ảnh generated owner duyệt. Loader/rebuild checks và giới hạn lineage trong report; pins lịch sử giữ nguyên.

[Đối soát review V12 và ảnh bổ sung ngày 22/10](v12-reconcile-20261022/README.md): evidence JSON delta, audit nhãn/geometry/trùng lặp và các batch owner đã chốt, dẫn tới release V13; các snapshot draft giữ nguyên.

[Cleanup ngày 23/10](cleanup-20261023/README.md): exact manifest và restore locator cho 4.690 file đã dọn; protected bytes được kiểm trước/sau. Availability này bổ sung đợt retention 16/10.

[Bàn audit toàn bộ accepted V12](v12-full-audit-20261021/README.md): đủ 1.639 crop mọi role, 48 nhóm thị giác, preview 224 và lưu/export review. Owner cho phép mở test cũ để visual audit; không gán nhãn hoặc chia split mới.

[Tiêu chí audit V12 ngày 21/10](v12-audit-criteria-20261021/README.md): nghiên cứu crop/quality/semantics, chín ví dụ và tác động lọc kích thước. Owner chọn looking là quay đầu bên/sau, phía trước không tính; rubric chi tiết còn Draft, chưa relabel/release.

[Chẩn đoán E006/V12 ngày 21/10](e006-v12-diagnostics-20261021/README.md): lỗi qua sáu run, coverage, 37 crop visual review và bộ ví dụ P/N/U; bốn ngoại lệ Draft chờ owner, proposal đối chứng erasing riêng; không train/test hoặc sửa V12.

[Release V12 ngày 20/10](dataset-release-20261020-v12/README.md): chốt review legacy/YouTube và allocation owner; package local accepted, kiểm loader/rebuild/test preservation. Không train.

[Hợp nhất review legacy và YouTube ngày 19–20/10](crop-review-consolidation-20261019/README.md): hồ sơ review cuối của owner, đã được chốt qua release V12; một gallery chỉ thay đổi. Kế tiếp hai hồ sơ audit dưới đây.

[Audit ZIP sáu lớp học ngày 18–19/10](youtube-frame-audit-20261018/README.md): xem 115 frame, đề xuất 71 crop sau QA native/input; snapshot Draft lịch sử, quyết định cuối ở V12. Y05 có cờ scene-family với G17 cũ.

[Audit cohort lịch sử V11 ngày 18/10 — R2](v11-legacy-crop-audit-20261018/r2/README.md): review lại đủ 836 crop theo quyết định Accepted V10/V11; 537 giữ geometry (310 đổi nhãn), 250 cần recrop/review mới, 49 đề xuất rút supervision. Có ghi chú từng ID và gallery R2; snapshot Draft lịch sử; nghiệm thu cuối ở V12, V11 giữ nguyên. R1 được bảo toàn để truy vết.

[Release V11 ngày 17/10](dataset-release-20261017/README.md): parent V12, đã đóng gói từ allocation và 270 crop nghiệm thu; có pointer, kiểm rebuild, backup local và cleanup; không chạy train.

[Nghiệm thu phân bổ và mức đạt ngày 17/10](train-val-plan-20261017/README.md): 1.185 train / 266 validation đã duyệt; mỗi target precision/recall ≥ 80%, FPR ≤ 20%. Cách train chưa được chốt, proposal train mới đã gỡ theo owner; chưa chạy train.

[Audit và crop 5 ZIP frames ngày 16–17/10](frame-crop-audit-20261016/README.md): xem 536 frame/27 video, bàn giao 100 crop Draft theo video/anchor; gallery, pixel QA và provenance, chưa enrollment.

[Chốt 98 crop ngày 17/10](frame-crop-audit-20261016/OWNER-ACCEPTED-20261017.md): owner đã nghiệm thu crop/nhãn và membership, gồm G06 R02 và ba quyết định nhãn cuối; chưa enrollment. [Đối chiếu trước nghiệm thu](frame-crop-audit-20261016/OWNER-REVIEW-20261017.md) giữ làm lịch sử.

[Chốt crop additional.zip ngày 17/10](frame-crop-additional-20261017/README.md): sau review owner giữ 172 crop, loại 9 và thay 3 bằng 4 geometry; đã nghiệm thu crop/nhãn/membership, chưa enrollment. Cùng bộ 98 trước đó là 270 crop đã chốt.

[Tổng hợp accepted và coverage ngày 16/10](E004-accepted-coverage-20261016/README.md): owner approve đủ 13 NC; hợp nhất 345 crop mới (240 + 92 + 13), ưu tiên toàn bộ cho train. Dự kiến 1.061 train nếu đủ gate; 78 phone P mới tập trung ở 3 parent videos, chưa chứng minh giải quyết lỗi RC1. Có ledger, receipt và kiểm overlap; chưa canonical release/train.

[Chốt bộ mới và bổ sung theo vòng đỏ ngày 16/10](E004-new-bundle-closure-20261016/README.md): chốt 92 crop theo owner, sửa 9 cặp nhãn; 14 vị trí khoanh đỏ bao phủ bằng 13 crop Draft mới và NA-008 đã có. Gallery hiện hành phân biệt phần đã chốt và phần bổ sung.

[Chốt batch cũ và audit bộ ZIP mới](E004-crop-closure-20261015/README.md): batch cũ giữ 240 crop, loại 7 và sửa 3 cặp nhãn theo review owner; [bộ mới](E004-new-bundle-audit-20261015/README.md) có 80 crop / 132 frame, shortlist 92 crop Draft gồm recrop và bổ sung, chưa release/split/train.

[Thống nhất phone/calculator sau review 247 crop](E004-device-consistency-20261015/README.md): kiểm đủ batch, sửa 77 cặp nhãn Draft, 242 shortlist và 5 U/U withheld; ngoại lệ vật che hoàn toàn theo quyết định owner có scope, không hồi tố release cũ.

[Tinh gọn và mở rộng bộ crop sau review mới](E004-crop-bundle-refinement-20261015/README.md): thay đề xuất shortlist trước bằng 247 crop / 84 anchor, sửa rubric và nhãn Draft, bổ sung người qua frame gốc; chưa nghiệm thu release/split.

[Đối chiếu review owner, recrop và shortlist bộ crop](E004-crop-bundle-review-20261014/README.md): đủ 765 crop/212 frame; 192 recrop, 5 mẫu bổ sung, 710 mẫu trong shortlist Draft; 40 ngoại lệ đối với cột nhãn owner, chưa nghiệm thu release/split.

[Audit bộ 765 crop và 212 frame gốc](E004-crop-bundle-audit-20261014/README.md): kiểm kỹ thuật toàn bộ và screening đủ crop; 5 batch Draft, giữ contract hiện tại, chưa nghiệm thu nhãn/split hoặc train.

Snapshot E004 lịch sử: [V9 hợp nhất và review mới đã nghiệm thu](E004-v9-consolidation-20261013/README.md), [release pointer](E004-v9-consolidation-20261013/v9-release-pointer.json). V9 local Accepted, không tự cấp quyền run/test.

Snapshot trước: [mở rộng hai ZIP và rà lại nguồn cũ](E004-source-expansion-20261013/README.md), [batch 199 crop đã nghiệm thu](E004-source-expansion-20261013/REVIEW.md). Tổng 308 anchors đã nghiệm thu; [V8 local Accepted](E004-source-expansion-20261013/v8-release-pointer.json) thêm 27 train. [Package prepared trước](E004-consolidated-frames-20261013/package-pointers-r2.json) và các snapshot cũ giữ nguyên.

| Đối tượng | Hồ sơ | Nguồn / giới hạn |
|---|---|---|
| Nghiên cứu nguồn, releases v4–v7, coverage, holdout research | [Tổng hợp đến 2026-10-11](data-research-20261011/README.md) | Diễn giải chuyển từ spec, không audit mới; original qua Git/archive locators |
| v4 | [Report](pilot-b-release-acceptance-20261005/README.md), [approval](pilot-b-release-acceptance-20261005/owner-approval.json) | Local release; remote scope riêng |
| v5 | [Report](pilot-b-v5-release-20261007/README.md), [pointer](pilot-b-v5-release-20261007/release-pointer.json) | Parent v4 và metadata dependencies đúng pins |
| v6 | [Report](pilot-b-v6-release-20261007/README.md), [pointer](pilot-b-v6-release-20261007/release-pointer.json) | Validation development, không independent holdout |
| v7 | [Report](pilot-b-v7-release-20261010/README.md), [pointer](pilot-b-v7-release-20261010/release-pointer.json) | Pointer pin card/approval/manifest/verification; không tự train/upload |
| v8 và E004 source expansion | [Report](E004-source-expansion-20261013/README.md), [pointer V8](E004-source-expansion-20261013/v8-release-pointer.json), [cohorts](E004-source-expansion-20261013/cohort-package-pointers.json) | 199 crop accepted; 27 train bổ sung, development/reserve chưa final freeze |
| Audit v7 cho E004 | [Kết luận](E004-v7-fit-audit-20261010/README.md), [pins](E004-v7-fit-audit-20261010/input-pins.json) | Cached scores, không prediction mới hoặc approval E004 |
| Audit E004 sau V7, 2026-10-11 | [Matrix/gaps/nguồn/comparator/gates](E004-post-v7-audit-20261011/README.md) | Inventory đủ 375 new-train; taxonomy/independence unknown giữ nguyên; protocol/plan vẫn Draft |
| E004 source review và pilot, 2026-10-11–12 | [Nghiệm thu hiện hành/QA/gaps](E004-source-review-20261011/REVIEW-OWNER-20261012.md), [owner receipt](E004-source-review-20261011/owner-review-receipt-20261012.json), [snapshot đầu](E004-source-review-20261011/README.md) | 56 anchors đã nghiệm thu nhãn/geometry, 136 nguồn đã xem; ledger review-only, chưa independent group hoặc assignment mới |

Card/manifest/coverage ở package mà pointer chỉ tới; có thể không hiện diện trong clean Git checkout. Metadata report được Git giữ để hiểu scope và tìm restore. Không cần đọc mọi record để hiểu task.

## Experiments

[Thực nghiệm E005 trên Dataset V11 ngày 18/10](e005-v11-adaptation-20261018/README.md): 1 smoke và 4 run đối chứng (`E005-V11-LP`, `E005-V11-S1-AUG`, `E005-V11-AC-L4B1`, `E005-V11-AC-L4`) FINISHED, reload exact parity PASS; `E005-V11-S1-AUG` đạt cao nhất, chưa đồng thời vượt cổng 80/80/20 cho cả hai target; Continue research, test 11 giữ đóng.

[E004 V9 execution freeze](E004-v9-execution-20261013/README.md): matched control/layer4 FINISHED; development evaluation và benchmark hoàn tất, khuyến nghị Continue research, test đóng.

[Phân tích nguyên nhân sau E004](E004-root-cause-20261014/README.md): đối chiếu lịch sử, code và cached scores; phân biệt overfitting, giới hạn dữ liệu/cohort và giả thuyết khắc phục; chưa cấp quyền run/test mới.

[Audit thị giác E004](E004-visual-audit-20261014/README.md): 31 crop selection qua 10 family, evidence source/crop/input 224 và nhận xét Draft; dẫn tới proposal ablation E004-RC1, chưa train mới.

[E004-RC1 execution](E004-RC1-execution-20261014/README.md): bốn arms FINISHED, reload parity PASS; warm head/LR cao tốt nhất matrix nhưng chưa đạt quality, Continue research; test đóng.

[Targeted coverage sau RC1](E004-targeted-coverage-20261014/README.md): matrix 716 train/71 selection, 44 train xem mới và 31 selection từ audit trước; factors Draft, gallery chờ owner review, chưa mở nguồn/run mới.

| Đối tượng | Kết quả / evidence | Config và quyền |
|---|---|---|
| E001 | [Run](E001/run.json), [metrics](E001/metrics.json), [test metrics](E001/test-metrics.json) | [Config](../../configs/experiments/E001.yaml), [approval](../../docs/experiments/E001-approval.json), [final protocol](../../docs/experiments/E001-final-test-protocol.json) |
| E002 | [Summary](E002/summary.json), [metrics](E002/metrics.json), [comparison](E002/comparison.json) | [Config](../../configs/experiments/E002.yaml), [approval](../../docs/experiments/E002-approval.json) |
| E003 | [Summary](E003/summary.json), [metrics](E003/metrics.json), [errors](E003/error-analysis.json) | [Config](../../configs/experiments/E003.yaml), [approval](../../docs/experiments/E003-approval.json) |
| Baseline review | [Recipe/results/errors E001–E003](baseline-review-20261011/README.md) | Snapshot chuyển từ spec, không ghép cohort khác để kết luận gain |
| E004 software readiness | [Implementation/validation](E004-software-readiness-20261012/README.md) | Synthetic I1–I8 và regression; chưa release hoặc run thật |

Experiment đang thiết kế: [configs index](../../configs/experiments/README.md). Run mới có hồ sơ riêng; chỉ thêm locator ở đây, không nối vào baseline lịch sử. Checkpoints/predictions ở `outputs/<ID>` theo run pins; restore không cấp test access.

## Vận hành

[Cleanup sau E007 ngày 24/10](cleanup-20261024/README.md): nghỉ lưu tài sản lịch sử không còn phục vụ hướng D1 theo manifest; bảo toàn V13, nguồn độc nhất, model best D1/R0 và bằng chứng nghiên cứu.

[E004 enrollment và run C345](E004-train-enrollment-20261016/README.md): V10/development có 1.061 train; research FINISHED, reload exact parity; looking cải thiện nhưng phone false positives tăng, Continue research.

[Handoff 2026-10-11](repository-handoff-20261011/README.md) giữ snapshot checks/backup và original locator. Các tổng hợp mới trên không thay receipt gốc hoặc là data/model acceptance mới.

[Retention tài sản hiện hành 16/10/2026](storage-retention-20261016/README.md): chính sách owner duyệt, availability mới và evidence cleanup; report cũ không chứng minh payload còn tồn tại.
