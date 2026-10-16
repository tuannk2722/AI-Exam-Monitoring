# E004 — Enrollment 345 crop và research C345

**Đã hoàn tất enrollment và experiment được duyệt.** V10/development có 1.061 train, giữ nguyên bytes/nhãn của 345 crop mới và nội dung 1.208 records parent. E004-C345-W-H FINISHED sau 11 epochs, best epoch 1; reload scores/metrics khớp hoàn toàn. **Bổ sung dữ liệu chưa giải quyết thiếu hụt chất lượng: looking cải thiện nhưng phone false positives tăng mạnh; chưa model Selected.**

- [Gallery geometry](../../../outputs/E004-train-enrollment-20261016/index.html): đủ 345 crop, khung xanh là person box đã được owner nghiệm thu batch. Chữ Draft trong gallery/proposal là snapshot trước approval; không dùng bộ box này để tuyên bố annotation detector hoàn chỉnh.
- [Geometry source pixels](geometry-proposals.json), [provenance native/derived](derivative-provenance.json), [ledger review-only](../../../data/interim/E004-train-enrollment-20261016/pending-ledger.jsonl).
- [Lineage/membership](lineage-proposal.md): owner duyệt 345 crop trong một quarantine group bảo thủ; giữ nguyên các tập cũ. Không xác nhận độc lập với protected pool.
- [Experiment](experiment-proposal.md): owner duyệt một run tối đa 2 giờ CPU, recipe W-H cố định, chỉ thêm dữ liệu; [config và protocol](../../../configs/experiments/E004-C345-20261016/README.md).
- [Owner direction](owner-direction.md): scope user đã duyệt; không yêu cầu review lại labels/crop đã accepted.
- [Approval cụ thể](owner-enrollment-approval.json), [package pointers](package-pointers.json), [deterministic rebuild/bytes/code parity](package-validation.json), [input/gallery validation](input-gallery-validation.json).

| Package | Train | Val | Test giữ nguyên | Review-only | Excluded |
|---|---:|---:|---:|---:|---:|
| V10 canonical | 1.061 | 49 | 11 | 403 | 29 |
| C345 development | 1.061 | 120 | 11 | 332 | 29 |

Development 120 gồm 71 selection và 49 diagnostic như baseline; không thêm test/holdout từ batch mới. 345 crop gồm 240 batch cũ + 92 batch mới + 13 bổ sung owner đã duyệt. Train mới có phone 325 P / 295 N / 441 U; looking 289 P / 564 N / 208 U; 412 crop có cả hai target known. 78 phone P bổ sung vẫn tập trung ở 3 parent videos; coverage chỉ bù một phần, không coi số lượng crop là bằng chứng đủ đa dạng.

## Contract đã thực hiện

177 crop khớp tuyệt đối native ROI; 168 là resized/reencoded imports. V2 ghi source SHA, ROI RGB SHA, output format/dimensions, review gắn crop SHA và evidence. Exporter yêu cầu exact crop bytes; loader kiểm output integrity. Native pixel guard giữ nguyên. V1 serialization không thêm field null; toàn bộ 776 canonical V9 records round-trip JSON nguyên vẹn và development loader kiểm 847 records PASS.

Không đưa bbox context thành person bbox để qua gate. Không giả định decoder JPEG biết đúng recipe upstream. Không dựng lại crop rồi áp approval SHA cũ. Dữ liệu/pins đã seal giữ nguyên; những thay đổi này chỉ áp dụng cho package mới.

## Validation và execution

Hai package rebuild độc lập khớp checksum hoàn toàn, loader PASS. Native guard và V1 serialization giữ nguyên; derived input có pin bytes/source/ROI/dimensions/format. Source changes so với baseline chỉ ở schema/exporter/derived loader checks và công cụ audit; training math/model/transform không đổi. Các tests schema/package/review/training adaptation và strict mypy cho source đã đổi đều PASS; kết quả software không thay nghiệm thu chất lượng.

[Enrollment validation](enrollment-validation.json) kiểm riêng nhãn cuối, source/crop SHA, ROI và role train của đủ 345 records. Quy tắc absence khi vật che hoàn toàn áp dụng theo approval cho batch mới; không relabel V9. Vì vậy đây là phép thử bổ sung batch cùng nhãn accepted hiện hành, không tách riêng ảnh hưởng số lượng ảnh khỏi khác biệt annotation policy theo thời điểm. Không thể dùng kết quả này để kết luận riêng từng yếu tố là nguyên nhân.

Smoke một epoch FINISHED, standalone bundle reload PASS. Recipe giữ seed 42, warm head epoch 10, layer4 LR 0,0001, head LR 0,001, batch 16, threshold 0,5. Số updates mỗi epoch tăng 45 → 67; không phải so sánh equal-update. Không dùng smoke để đổi recipe. [Run integrity](run-integrity.json) kiểm config/code, sampler từng epoch, tensor checkpoint, best minimum BCE, lịch diagnostics và reload exact parity. [Software validation](software-validation.json) giữ scope checks.

## Kết quả trên selection 71 giữ nguyên

[Comparison và errors/family](comparison.json) dùng cached scores RC1-W-H đã đối chiếu checksum ledger trong archive lịch sử; không chạy lại model cũ dưới code mới. Threshold cố định 0,5. BCE tính độc lập từ probabilities có sai số làm tròn khoảng 1e-8 so logits của trainer.

| Metric | RC1-W-H, 716 train | C345-W-H, 1.061 train |
|---|---:|---:|
| Macro masked BCE ↓ | 0,65365 | 0,68406 |
| Macro AP ↑ | 0,60763 | 0,60051 |
| Phone AP | 0,67092 | 0,60879 |
| Phone precision | 62,50% | 47,17% |
| Phone recall | 37,04% | 92,59% |
| Phone FPR | 18,18% | 84,85% |
| Phone TP / FP / FN / TN | 10 / 6 / 17 / 27 | 25 / 28 / 2 / 5 |
| Looking AP | 0,54435 | 0,59223 |
| Looking precision | 54,55% | 68,75% |
| Looking recall | 21,43% | 39,29% |
| Looking FPR | 13,16% | 13,16% |
| Looking TP / FP / FN / TN | 6 / 5 / 22 / 33 | 11 / 5 / 17 / 33 |

Phone tìm thêm 15 positives nhưng thêm 22 false positives, dự đoán P cho 53/60 mẫu phone known. Vì vậy recall cao không đồng nghĩa phân biệt phone/calculator tốt hơn. Looking tìm thêm 5 positives, FP giữ 5; đây là cải thiện có ích nhưng recall vẫn thấp. 42 target-cell đổi quyết định: 20 lỗi được sửa và 22 lỗi mới. Không suy toàn bộ FP là calculator: chưa có factor census accepted cho mọi lỗi selection.

Ngoài CF-Q072 (26 crop), phone TP tăng 1/8 → 7/8 nhưng FP tăng 1/12 → 10/12; looking TP tăng 3/11 → 4/11, FP giữ 1/14. Gain không chỉ nằm trong family lớn, nhưng lỗi phone lan rộng. CF-Q072 vẫn chiếm 45/71 crop; không loại family để làm đẹp số. Family ít P/N có metric unavailable đúng contract.

| Diagnostic cohort, BCE / macro AP | RC1-W-H | C345-W-H |
|---|---|---|
| Diagnostic 49 | 0,60210 / 0,80814 | 0,64511 / 0,84167 |
| Comparator 48 | 0,61301 / 0,80856 | 0,64706 / 0,84490 |
| Added 35 | 0,66865 / 0,67005 | 0,73952 / 0,75302 |

Các diagnostic subsets chồng nhau, không cộng support hoặc dùng để đổi selection. AP tăng trên diagnostic trong khi BCE xấu hơn cho thấy kết quả phụ thuộc cohort và operating point; không có cải thiện đồng nhất.

## Đánh giá thiếu hụt và quyết định

Train loss giảm từ 0,45226 ở epoch 1 xuống 0,000110 ở epoch 11; selection BCE tăng từ 0,68406 lên 2,15880. Early stopping giữ epoch 1. **Overfit vẫn rõ, không có cơ sở tiếp tục thêm epochs theo recipe này.**

Trên development, M1 không đạt (phone FPR 84,85%; looking recall 39,29%); M2 không đạt; M3 không đạt (BCE / constant train-prevalence BCE = 0,97966, yêu cầu ≤0,9). M4 INCONCLUSIVE. Đây không phải kết quả final-test gates. Khuyến nghị **Continue research**, không chọn C345 làm model thay thế hoặc mở downstream.

345 crop đã thực sự vào optimizer và bù supervision/coverage; không phải chỉ nằm trong inventory. Tuy nhiên phone P vẫn tập trung 3 nguồn, 165 phone U mới không cung cấp phone loss, representation 224 và attribution vẫn chưa được ablation. Chưa đủ evidence quy nguyên nhân suy giảm riêng cho annotation policy, tương quan nguồn, số updates hay representation. Không đổi nhãn accepted để ép metrics tăng.

Hướng nghiên cứu tiếp theo cần proposal riêng: dùng danh sách lỗi hiện có đối chiếu evidence phone/calculator/attribution và native/224, rồi thiết kế một thay đổi có đối chứng. Chưa tự chạy model phụ, đổi resolution/sampling/threshold hoặc thêm run. Scope enrollment + một research run được duyệt đã hoàn thành.

## Sự cố ngắt, recovery và bảo toàn

Khi owner báo history dừng, không còn process Python nhưng run.json vẫn RUNNING; last.pt/history đã commit epoch 8. Không đủ evidence xác định nguyên nhân, đặc biệt không khẳng định quota usage gây kill process. [Recovery receipt](orphan-recovery.json) và snapshot riêng giữ nguyên trạng trước phục hồi. Đã kiểm identity/config/history/sampler, ghi INTERRUPTED minh bạch và resume bằng process nền độc lập từ epoch 9; không sửa checkpoint hoặc recipe. Inventory checksum recovery được tạo sau crash, không được coi là checksum có trước crash.

Run FINISHED 11 epochs/737 updates, best epoch 1. Tổng budget ghi nhận 3.198,706 giây, gồm **toàn bộ khoảng từ start đến recovery được tính bảo thủ, cả downtime**; không gọi đây là thời gian CPU thực. Smoke 434,764 giây riêng. Run còn dưới trần 7.200 giây. Không có phép so uninterrupted-vs-resumed trên chính dataset này; đã kiểm sampler, checkpoint state và standalone reload.

[Backup local và restore drill](backup-receipt.json), [cleanup receipt](cleanup-receipt.json), [result pins](result-pins.json) giữ evidence bàn giao. Backup cùng ổ không chống hỏng ổ; không upload. Git chưa stage/commit, không đưa media/model vào Git.

Không inference final test/reserve; exporter chỉ kiểm integrity và sao chép các artifacts cũ. Originals/pins upstream giữ nguyên. Snapshot proposal/gallery/ledger pending là evidence trước approval; canonical package và receipt mới xác định trạng thái hiện hành.
