# Audit looking_around — E007 V13 ngày 24/10/2026

**Đã sửa công cụ audit; chưa có model looking đạt yêu cầu.** Audit độc lập dùng artifacts đã lưu của D1 và R0 ở seeds 20261023/20261024/20261025. Không train, inference mới, final test, đổi nhãn/split/crop/threshold hay sửa pins E007/V13. [Config audit](../../../configs/diagnostics/e007-v13-looking-20261024.json), [kết quả E007 gốc](../e007-v13-colab-20261024/README.md), [proposal bước xử lý E008](../../../configs/experiments/E008-V13-LOOKING-20261024/README.md).

Đã kiểm đầy đủ 1.119 train / 185 val mỗi run: prediction SHA, membership, labels/masks/groups/target order, fixed và calibrated confusion. V4 dùng lại cặp ngưỡng selection cho train; unknown không thành negative. [48 ô parity](confusion-parity.json), [130 input pins](input-pins.json). Chỉ kiểm artifacts cần audit; không đọc lại checkpoint đã retire hoặc tự phục dựng payload lịch sử. Audit trước cloud đã kiểm trainer/reload/selection; audit này không thay receipt đó.

| D1 seed | Looking AP train / val | Ngưỡng đã freeze | TP / FP / FN / TN val | Precision / recall / FPR val |
|---|---|---:|---|---|
| 20261023 | 0,9945 / 0,7241 | 0,308626 | 26 / 20 / 7 / 132 | 56,52% / 78,79% / 13,16% |
| 20261024 | 0,9563 / 0,7662 | 0,499876 | 23 / 8 / 10 / 144 | 74,19% / 69,70% / 5,26% |
| 20261025 | 0,9841 / 0,7458 | 0,437784 | 23 / 10 / 10 / 142 | 69,70% / 69,70% / 6,58% |

[Operating envelopes](operating-envelopes.json) xét mọi score boundary, ties cùng nhóm và endpoints: không seed D1 nào có threshold looking đạt 80/80/20 trên val. Khi recall ≥ 80%, precision tối đa chỉ 55,10% / 52,94% / 55,77%. Train có threshold khả thi cả ba seed, nhưng không đem threshold train thay threshold đã freeze. Đây là khoảng cách ranking/generalization, không phải bằng chứng evaluator làm sai. Với 33 positive, recall ≥ 80% cần ít nhất 27 TP; nếu TP = 27 thì precision ≥ 80% cho phép tối đa 6 FP. FPR hiện qua gate nhưng precision/recall còn thiếu.

[Coverage](coverage.json): looking train 179 P / 931 N / 9 U, val 33 P / 152 N / 0 U; positive groups 74/21. Không thiếu support toàn val theo protocol. Small-anchor val chỉ có 7 P thuộc 2 nhóm; AP khoảng 0,43–0,52 không đủ chứng minh ROI là nguyên nhân chính. Trong 5 FN ổn định, có cả crop native nhỏ 114 × 117 và ảnh lớn 1.086 × 1.448; không có căn cứ lọc ảnh nhỏ hoặc tăng resolution hàng loạt.

Đã xem **90 crop khác nhau**: 43 ca ban đầu và 47 bổ sung, bao phủ đủ **20 lỗi looking val và 41 lỗi looking train lặp ít nhất 2/3 seed**, cùng các đối chứng TP/TN/U/phone. [Danh mục ban đầu](review-selection.json), [bổ sung](supplementary-review.json), [nhận xét từng lỗi](visual-findings.json). Trong 20 lỗi val có 7 FP và 5 FN sai cả ba seed; 8 ca còn lại sai 2/3. Số này khác union tất cả lỗi sai ít nhất một seed. Gallery local ở [ban đầu](../../../data/interim/looking-around-audit-20261024/index.html) và [bổ sung](../../../data/interim/looking-around-audit-20261024/supplementary/index.html); không upload và không đưa media vào Git.

## Kết luận từ hình và policy

Các nhận xét là Draft thị giác của agent, không thay nghiệm thu owner hoặc chứng minh cơ chế nhân quả. Đối chiếu [policy hiện hành](../v12-reconcile-20261022/owner-policy-20261023.md), nhãn V13 và tám [ảnh upstream đã kiểm SHA](upstream-context.json). “Source” trong gallery chính là reviewed crop input của V13, **không mặc nhiên là toàn ảnh camera**. NEW-058/NEW-132 không có exact original-camera provenance; giữ unknown upstream. Tám ảnh upstream được mở riêng chỉ để hiểu bối cảnh, không coi bbox V12 là geometry mới của V13.

| Ca lỗi ổn định | Quan sát và hướng xử lý |
|---|---|
| E004-EX-C003 — FP | Nhìn xuống bài, tay chống trán, camera bên; giữ difficult negative, không đổi thành looking P vì thấy mặt nghiêng |
| G01-A02-F00001-R02, G01-B02-F00009 — FP | Crop nhỏ, tư thế theo bàn/đọc giấy; camera chéo và đầu nghiêng cần phân biệt với quay sang người khác |
| G08-B02-F00001 — FP | Toàn cảnh cho thấy hướng nhìn về phía trước lớp; crop hẹp mất mốc bố trí lớp |
| V7-A-074 — FP | Góc bên, ngồi hướng theo bàn; mặt profile không tự là head-turn |
| V7-C-046-R05, V7-OE-S094-A01-R04 — FP | Toàn cảnh xác nhận cả lớp cùng hướng; nhãn N có căn cứ, không lấy taxonomy nguồn hoặc profile làm P |
| G12-A02-F00007 — FN | Nhìn lệch sang người bên cạnh, nhiều người/thiết bị trong context; cần quan hệ đầu–thân–bàn, không trộn phone với looking |
| G19-A01-F00052 — FN | Đầu quay ngang, native nhỏ/mờ; upsample 336 không tạo lại chi tiết mắt |
| NEW-058, NEW-132 — FN | Quay về bên/sau, có ca rõ ở input 336; không thể quy tất cả FN cho thiếu pixel |
| V7-C-111 — FN | Đầu lệch so với thân/hướng ngồi; người lớn/phòng họp khác phần lớn ảnh classroom, chưa đủ support để kết luận source kém |

Train bổ sung có cùng dạng FP: nhìn phía trước từ camera bên, cúi đọc/viết, che một phần đầu hoặc góc từ sau. Cặp NEW-147 P / NEW-149 N có người/cảnh tương tự nhưng khác quay đầu; model vẫn nhầm N và có lúc bỏ P. Đây là đối chứng định tính hữu ích cho học quan hệ tư thế, không phải chứng minh hai ảnh độc lập hoặc đề xuất đổi grouping. ADD-Y01-F00099-M01-R02 là FN train ổn định duy nhất; cue nhẹ/đích nhìn cần context, chưa có căn cứ chắc chắn để bác nhãn owner. Nhận xét không tự chuyển ca khó thành U hoặc remove.

Đường DINO hiện tại lấy normalized CLS nối mean patch tokens toàn ảnh, gồm padding; không nhận person_box để pooling, không giữ các vùng head/body riêng. Khả năng mất cấu trúc vùng và phụ thuộc góc camera là giả thuyết có căn cứ để làm đối chứng, **chưa xác minh bằng can thiệp model**. Giữ neg khó và cues quay đầu bên/sau trong train; không mine val thành train, relabel để tăng điểm, ensemble ba seed hoặc hạ gate.

## Lỗi phần mềm đã xử lý và bước tiếp

`training.diagnostics` đã nhận `run_root` để audit runs nested E007, chấp nhận endpoints V4 nhưng giữ guard V3, và từ chối threshold train khác selection ở V4. Gallery dùng kích thước config thật; layout cũ cao 310 px còn dán input 336 tại y = 55 sẽ cắt mất 81 px dưới. Bản mới giữ đủ input và augmentation, không ghi nhầm 224. Thêm `review_sample_ids` để không bỏ các lỗi cùng nhóm khi shortlist đa dạng, và xuất operating envelope từ cached scores. Đây là lỗi/cải tiến công cụ chẩn đoán, không phải lỗi làm thay đổi predictions training E007.

[E008 Draft](../../../configs/experiments/E008-V13-LOOKING-20261024/README.md) là bước xử lý cụ thể: đối chứng G0 global / G1 context spatial / A1 anchor spatial, giữ recipe D1, tối đa 7 research run và trần 4 giờ GPU mới. Thiết kế giữ spatial bins để kiểm cue đầu/thân, có control cùng số chiều để tách anchor pooling khỏi tăng head capacity. Chưa duyệt hoặc triển khai scientific; không bảo đảm sẽ đạt gate. Nếu không cải thiện, dừng nhánh và thiết kế bổ sung nguồn/context riêng, không tìm hyperparameters vô hạn.

Checks phần mềm và integrity được ghi tại [checks.json](checks.json). Software PASS không phải acceptance looking/model. Spec không đổi. Media ở data/interim là evidence review local cần giữ cho đến khi owner quyết định; không là cache/scratch. Không tạo environment mới, không khôi phục checkpoints cũ, không commit/stage trong task này.
