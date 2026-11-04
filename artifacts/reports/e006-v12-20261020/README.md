# Báo cáo thực nghiệm E006 trên Dataset V12

**Review độc lập ngày 21/10/2026: 1 smoke và 9 research run FINISHED; 10/10 reload exact parity khớp artifacts. Không research run nào qua đồng thời Precision ≥ 80%, Recall ≥ 80%, FPR ≤ 20% cho cả hai target, kể cả sau hiệu chỉnh ngưỡng. Quyết định nghiên cứu: tiếp tục nghiên cứu, chưa Selected.**

Báo cáo này đã được đối chiếu trực tiếp với config, protocol, run record, checkpoint, history, predictions và evaluation; không lấy machine summary làm nguồn kết luận. Evidence kiểm chi tiết: [review-audit.json](review-audit.json).

## 1. Phạm vi, dữ liệu và phê duyệt

- [Owner authorization](owner-authorization.json), [thiết kế](../../../configs/experiments/E006-V12-20261020/README.md), [campaign R4](../../../configs/experiments/E006-V12-20261020/r4/campaign.json). Tối đa 9 research run và smoke, CPU 4 threads, 7.200 giây/run; khởi tạo ImageNet IMAGENET1K_V1 và head mới, không warm-start model cũ.
- V12: 1.092 train / 204 val; phone val **35 P / 94 N / 75 U**, looking val **65 P / 139 N / 0 U**. U giữ mask 0. Validation có 110 nhóm; positive phone 25 nhóm, positive looking 40 nhóm.
- 11 mẫu test giữ reserved holdout; không có test evaluation trong artifacts được kiểm. Việc được giữ lại không tự chứng minh độc lập hoặc đủ support cho final test.
- Validation được dùng chọn epoch, recipe, early stopping **và hiệu chỉnh threshold**; đây là development, không là holdout độc lập. Ba seed dùng cùng validation, không phải ba tập kiểm định độc lập.
- Screening: LP và bốn S1 trên seed 20261020. Chọn hai S1 theo gate pass, Macro AP, BCE và tên recipe; vì tất cả fail gate nên SQRT/RATIO được chọn theo AP. Hai recipe này chạy thêm seed 20261021/20261022. Không chạy các nhánh confirmation còn lại.

## 2. Thực thi và kiểm chứng

- Smoke 4 epoch kiểm interruption/resume và chuyển sang fine-tune; [reload exact parity PASS](verified-smoke.json). Chín research run thuộc R4 hoàn tất, mỗi run có standalone evaluation tương ứng.
- Đã kiểm SHA mọi file được liệt kê trong checksums của 10 run và 10 evaluation, tensor digest của best checkpoint, best/last epoch và quy tắc chọn best từ history; config/approval/readiness research; exact train/val membership, labels, masks, groups và record digests với V12.
- Đã so sánh toàn bộ validation metrics/predictions với standalone evaluation đã lưu. Tính lại AP theo nhóm score bằng nhau và confusion matrix bằng Python độc lập; BCE từ probabilities khớp trong sai số 1e-6. Hiệu chỉnh threshold được kiểm lại bằng hàm protocol hiện hành. Không chạy lại model hoặc mở test trong review này.
- Source smoke cũ được bảo toàn theo [source-preservation.json](source-preservation.json); không còn cây `outputs/E006-V12-runtime`. Source research nằm ở `src`, artifacts từng run ở `outputs/<run-id>/`.

## 3. Recipe thực tế

Single-crop ResNet18, RGB letterbox bilinear 224. MLP: **LayerNorm → Dropout → Linear 512→128 → GELU → Dropout → Linear 128→2**, dropout 0,3. Không phải ReLU hoặc một mô hình pose/gaze chuyên biệt.

S1 dùng AdamW, head LR **3e-4**, layer4.1 LR **3e-5**, weight decay 0,01; warmup head 3 epoch rồi cosine, BN eval, batch 16, max 12 epoch, patience 6. Augmentation: horizontal flip 0,5; brightness/contrast jitter 0,15; saturation 0,1; random erasing 0,15; box jitter 0. Không dùng RandomResizedCrop hoặc Affine trong single-crop này. Smoothing 0,05, unknown masked.

REF/FROZEN dùng pos_weight [1,13; 1,46]; SQRT [1,56; 1,48]; RATIO [2,44; 2,19]. Đây là các giá trị làm tròn đã chốt. FROZEN giữ backbone đóng với lịch LR head khớp REF. LP là linear head, backbone đóng, không augmentation/smoothing/weighting; LR và weight decay cũng khác S1. Vì vậy LP→FROZEN không cô lập tác động riêng head hoặc augmentation.

## 4. Kết quả toàn bộ runs

| Run | Best / kết thúc epoch | Macro AP | BCE | Phone AP | Looking AP | Thời gian train (phút) |
|---|---:|---:|---:|---:|---:|---:|
| `E006-V12-SMOKE` | 4 / 4 | 0.6766 | 0.5323 | 0.7039 | 0.6493 | 10.4 |
| `E006-V12-LP-S20261020-R4` | 12 / 12 | 0.6231 | 0.4690 | 0.6170 | 0.6292 | 22.6 |
| `E006-V12-S1-REF-S20261020-R4` | 5 / 11 | 0.6821 | 0.4657 | 0.7047 | 0.6594 | 20.7 |
| `E006-V12-S1-SQRT-S20261020-R4` | 5 / 11 | 0.6926 | 0.4703 | 0.7221 | 0.6630 | 20.9 |
| `E006-V12-S1-RATIO-S20261020-R4` | 7 / 12 | 0.6904 | 0.5687 | 0.7441 | 0.6367 | 22.7 |
| `E006-V12-S1-FROZEN-S20261020-R4` | 5 / 11 | 0.6562 | 0.5097 | 0.6796 | 0.6328 | 26.8 |
| `E006-V12-S1-SQRT-S20261021-R4` | 7 / 12 | 0.6817 | 0.4598 | 0.7197 | 0.6438 | 40.3 |
| `E006-V12-S1-SQRT-S20261022-R4` | 6 / 12 | 0.6726 | 0.4786 | 0.7057 | 0.6394 | 22.2 |
| `E006-V12-S1-RATIO-S20261021-R4` | 7 / 12 | 0.6805 | 0.4999 | 0.7147 | 0.6463 | 19.5 |
| `E006-V12-S1-RATIO-S20261022-R4` | 6 / 12 | 0.6735 | 0.5314 | 0.7068 | 0.6402 | 23.8 |

Thời gian là elapsed_seconds của trainer, chưa gồm standalone evaluation; smoke gồm thời gian resume. Smoke là kiểm kỹ thuật có lịch 4 epoch, không dùng để xếp hạng recipe.

### 4.1. Operating point sau hiệu chỉnh trên validation

| Run | Target | Threshold | Precision | Recall | FPR | TP / FP / FN / TN | Gate |
|---|---|---:|---:|---:|---:|---|---|
| LP / 20261020 | phone_use | 0.276181 | 59.1% | 74.3% | 19.1% | 26 / 18 / 9 / 76 | FAIL |
| LP / 20261020 | looking_around | 0.352530 | 65.8% | 73.8% | 18.0% | 48 / 25 / 17 / 114 | FAIL |
| S1-REF / 20261020 | phone_use | 0.254489 | 64.0% | 91.4% | 19.1% | 32 / 18 / 3 / 76 | FAIL |
| S1-REF / 20261020 | looking_around | 0.540000 | 66.7% | 70.8% | 16.5% | 46 / 23 / 19 / 116 | FAIL |
| S1-SQRT / 20261020 | phone_use | 0.345395 | 63.3% | 88.6% | 19.1% | 31 / 18 / 4 / 76 | FAIL |
| S1-SQRT / 20261020 | looking_around | 0.555726 | 66.2% | 72.3% | 17.3% | 47 / 24 / 18 / 115 | FAIL |
| S1-RATIO / 20261020 | phone_use | 0.544352 | 66.7% | 85.7% | 16.0% | 30 / 15 / 5 / 79 | FAIL |
| S1-RATIO / 20261020 | looking_around | 0.765354 | 66.2% | 66.2% | 15.8% | 43 / 22 / 22 / 117 | FAIL |
| S1-FROZEN / 20261020 | phone_use | 0.338928 | 61.2% | 85.7% | 20.2% | 30 / 19 / 5 / 75 | FAIL |
| S1-FROZEN / 20261020 | looking_around | 0.634194 | 68.9% | 64.6% | 13.7% | 42 / 19 / 23 / 120 | FAIL |
| S1-SQRT / 20261021 | phone_use | 0.297429 | 60.8% | 88.6% | 21.3% | 31 / 20 / 4 / 74 | FAIL |
| S1-SQRT / 20261021 | looking_around | 0.527759 | 62.7% | 72.3% | 20.1% | 47 / 28 / 18 / 111 | FAIL |
| S1-SQRT / 20261022 | phone_use | 0.345295 | 64.4% | 82.9% | 17.0% | 29 / 16 / 6 / 78 | FAIL |
| S1-SQRT / 20261022 | looking_around | 0.600000 | 66.7% | 70.8% | 16.5% | 46 / 23 / 19 / 116 | FAIL |
| S1-RATIO / 20261021 | phone_use | 0.431778 | 63.0% | 82.9% | 18.1% | 29 / 17 / 6 / 77 | FAIL |
| S1-RATIO / 20261021 | looking_around | 0.600000 | 61.5% | 73.8% | 21.6% | 48 / 30 / 17 / 109 | FAIL |
| S1-RATIO / 20261022 | phone_use | 0.510000 | 67.5% | 77.1% | 13.8% | 27 / 13 / 8 / 81 | FAIL |
| S1-RATIO / 20261022 | looking_around | 0.660000 | 63.2% | 73.8% | 20.1% | 48 / 28 / 17 / 111 | FAIL |

Threshold được fit trên chính val; không diễn giải metrics này như chất lượng trên dữ liệu mới. Khi không có threshold thỏa gate trong tập ứng viên, code chọn phương án giảm tổng thiếu hụt các gate, rồi F1 và khoảng cách đến 0,5; không đơn thuần tối đa F1.

### 4.2. Tổng hợp ba seed

| Recipe | Macro AP mean ± sample SD | BCE mean | Số run qua cả hai target |
|---|---:|---:|---:|
| S1-SQRT | 0.6823 ± 0.0100 | 0.4696 | 0 / 3 |
| S1-RATIO | 0.6815 ± 0.0085 | 0.5333 | 0 / 3 |

| Recipe | Target | Ngưỡng | Precision mean | Recall mean | FPR mean | TP mean |
|---|---|---|---:|---:|---:|---:|
| S1-SQRT | phone_use | 0,50 | 66.9% | 53.3% | 9.9% | 18.67 |
| S1-SQRT | phone_use | hiệu chỉnh riêng từng seed | 62.8% | 86.7% | 19.1% | 30.33 |
| S1-SQRT | looking_around | 0,50 | 55.8% | 76.9% | 28.8% | 50.00 |
| S1-SQRT | looking_around | hiệu chỉnh riêng từng seed | 65.2% | 71.8% | 18.0% | 46.67 |
| S1-RATIO | phone_use | 0,50 | 62.0% | 76.2% | 17.4% | 26.67 |
| S1-RATIO | phone_use | hiệu chỉnh riêng từng seed | 65.7% | 81.9% | 16.0% | 28.67 |
| S1-RATIO | looking_around | 0,50 | 45.7% | 85.6% | 48.2% | 55.67 |
| S1-RATIO | looking_around | hiệu chỉnh riêng từng seed | 63.6% | 71.3% | 19.2% | 46.33 |

Các giá trị là trung bình metric từng run, không phải confusion matrix gộp và không làm tròn TP mean thành một số ca thực. Ví dụ SQRT phone 53,3% = 18,67/35 TP trung bình, không phải 19/35; RATIO 76,2% = 26,67/35, không phải 27/35.

Chênh mean Macro AP SQRT−RATIO chỉ **0,00081**; ba seed chưa đủ chứng minh ưu thế ổn định hoặc ý nghĩa thống kê. Screening seed được tính trong mean ba seed, nên đây không phải xác nhận độc lập hoàn toàn. SD giữa seed không đo uncertainty do chọn mẫu dữ liệu. Bootstrap 5.000 lần theo nhóm được lưu trong metrics ở ngưỡng 0,50; không áp khoảng đó sang ngưỡng hiệu chỉnh.

## 5. Learning curves và đối chứng

- Trên seed 20261020: FROZEN−LP = **+0,0331 AP** (3,31 điểm phần trăm), là tác động tổng hợp nhiều thay đổi. REF−FROZEN = **+0,0259 AP**, là đối chứng sát hơn cho việc mở layer4.1. SQRT còn đổi weighting nên không gộp SQRT−FROZEN thành hiệu quả riêng của unfreeze.
- REF/SQRT/RATIO đạt best ở epoch 5–7. Cuối run, train AP khoảng 0,964–0,970 trong khi val AP thấp hơn best: dấu hiệu phù hợp với overfitting. Không có căn cứ tăng epoch đơn thuần từ các curves này.

| Recipe / seed | Best val AP | Cuối run train AP | Cuối run val AP |
|---|---:|---:|---:|
| LP / 20261020 | 0.6231 | 0.8184 | 0.6231 |
| S1-REF / 20261020 | 0.6821 | 0.9681 | 0.6627 |
| S1-SQRT / 20261020 | 0.6926 | 0.9649 | 0.6687 |
| S1-RATIO / 20261020 | 0.6904 | 0.9636 | 0.6748 |
| S1-FROZEN / 20261020 | 0.6562 | 0.8424 | 0.6429 |
| S1-SQRT / 20261021 | 0.6817 | 0.9690 | 0.6698 |
| S1-SQRT / 20261022 | 0.6726 | 0.9697 | 0.6463 |
| S1-RATIO / 20261021 | 0.6805 | 0.9654 | 0.6677 |
| S1-RATIO / 20261022 | 0.6735 | 0.9665 | 0.6511 |

## 6. Nguồn dữ liệu và lỗi cần review

Bảng dưới chỉ dùng **S1-SQRT / seed 20261020**, không trộn số của nhiều model. Support P/N là số nhãn biết của target. Các nguồn dưới đều thiếu ít nhất một điều kiện support để nghiệm thu riêng.

| Nguồn | Phone P / N | Phone AP | Looking P / N | Looking AP |
|---|---:|---:|---:|---:|
| classroom_attitude | 14 / 0 | unavailable | 5 / 27 | 0.4898 |
| owner-frames-part01-20261016 | 3 / 9 | 0.5889 | 7 / 15 | 0.6555 |
| owner-frames-part02-20261016 | 5 / 30 | 0.8444 | 10 / 32 | 0.5677 |
| consolidated-frames-20261013 | 1 / 1 | 1.0000 | 0 / 5 | unavailable |
| coco_2017_train | 0 / 2 | unavailable | 2 / 3 | 1.0000 |
| exam_cheating_keaor | 3 / 6 | 0.8056 | 5 / 7 | 0.7100 |

`consolidated-frames` không có looking positive; COCO không có phone positive. Metric thiếu support giữ trạng thái unavailable. AP = 1 trên một vài mẫu không là chứng cứ tổng quát tốt.

Lỗi có margin lớn của cùng run, tại ngưỡng hiệu chỉnh:

| Target | ID | Lỗi | Score | Threshold |
|---|---|---|---:|---:|
| phone_use | V7-A-008 | FP | 0.776182 | 0.345400 |
| phone_use | V7-C-132 | FP | 0.716660 | 0.345400 |
| phone_use | G27-A04-F00043 | FP | 0.714441 | 0.345400 |
| looking_around | EXP-SCB-021 | FN | 0.071866 | 0.555700 |
| looking_around | V7-C-075 | FN | 0.159038 | 0.555700 |
| looking_around | V7-D-009 | FP | 0.905161 | 0.555700 |

Đây là danh sách lỗi theo nhãn và score, không phải kết luận về vật cầm trong tay, liếc mắt hay nguyên nhân cơ học. Review này không thực hiện visual audit mới. Các trường `in_new270`/`in_unexposed_val_88` của gallery là tên legacy hard-code; false không chứng minh không có exposure khi protocol V12 không đăng ký các slice tên đó.

## 7. Kết luận và hướng tiếp theo

1. **Thực thi kỹ thuật hoàn tất; chất lượng chưa đạt mục tiêu 80/80/20.** Phân biệt FINISHED/reload PASS với nghiệm thu model. Không có approval Selected hoặc production trong review này.
2. **Giữ SQRT làm recipe tham chiếu development theo quy tắc đã chốt**, vì mean AP nhỉnh hơn và BCE thấp hơn; không gọi chênh 0,00081 là ưu thế chắc chắn. RATIO là đối chứng trade-off, không phải lựa chọn nghiệp vụ đã chứng minh.
3. RATIO tại 0,50 tăng looking recall lên 85,6% nhưng precision chỉ 45,7% và FPR 48,2%. Sau hiệu chỉnh, SQRT/RATIO đều còn precision/recall thiếu gate; không giải quyết bằng tuyên bố recall cao riêng lẻ. Phone_use/looking_around là target quan sát, không tự chứng minh hành vi gian lận.
4. Ưu tiên review lỗi chung qua seed và bù coverage đúng nguồn theo quy trình dữ liệu đã duyệt; không tự sửa nhãn/split. Nếu thử recipe tiếp, cần hypothesis/config mới, giữ số biến thay đổi có kiểm soát. Curves hiện tại không ủng hộ mở sâu hoặc train lâu hơn một cách mặc định.
5. Không có đối chứng tách audit nhãn, recrop và YouTube, nên không kết luận V12 gây ra gain hay SD nhỏ chứng minh dataset đã giải quyết vấn đề. 681 crop audit accepted đã bao gồm 90 YouTube, không phải hai lượng bổ sung độc lập.
6. Giữ test đóng; trước final test cần candidate/protocol/use scope và đủ bằng chứng support/independence theo approval riêng.
