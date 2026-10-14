# E004-RC1 — Ablation initialization × learning rate

**Draft, chờ owner duyệt thiết kế/compute. Không runnable và chưa chạy.** [Variables](plan.yaml), [audit thị giác](../../../artifacts/reports/E004-visual-audit-20261014/README.md). User đã yêu cầu tiếp tục nghiên cứu; các giá trị mới bên dưới được đề xuất cụ thể ở bước này, không suy approval từ receipt E004 cũ.

## Câu hỏi và thiết kế

Audit thấy các lỗi có evidence rõ ở 224 và L4 làm mất một số TP của LP, bên cạnh phone nhỏ/low-detail. Ưu tiên kiểm recipe trước khi tăng resolution hoặc thu thêm đại trà. Thiết kế 2×2 tách initialization với LR; không đổi cả hai rồi quy gain cho một yếu tố.

| Run đề xuất | Head ban đầu | LR layer4 |
|---|---|---:|
| E004-RC1-R-H | Shared random head E004 | 0,0001 |
| E004-RC1-W-H | Head LP best epoch 10 | 0,0001 |
| E004-RC1-R-L | Shared random head E004 | 0,00001 |
| E004-RC1-W-L | Head LP best epoch 10 | 0,00001 |

Giữ 716 train/71 selection, diagnostic cũ, 224, ImageNet backbone ban đầu, BN eval, head LR 0,001, AdamW/weight decay 0,0001, batch 16, CPU 4 threads, seed 42, không augmentation/scheduler, threshold 0,5. Max 50 epochs, patience 10/min_delta 0,0001. Best theo raw minimum selection BCE của completed epoch như E004. Không đổi cohort hoặc nhãn accepted.

R-H là comparator chạy trên cùng code mới có instrumentation với các nhánh còn lại; không dùng việc refactor để tự train lại historical E004. Run E004 cũ bất biến và chỉ là sanity reference. Không tạo hypothesis mới cho R-H như thể đó là phương pháp khác; nó phục vụ matched comparison của study này.

Warm branch chỉ copy head từ LP bundle đã pin; backbone luôn reset về ImageNet và optimizer reset. LP đã dùng selection71 để chọn epoch10: đây là thiết kế hậu nghiệm trên development đã biết, không independent validation. Warm branch có thêm lịch sử học head; contrast đo tác động thực dụng của initialization/pipeline, không so bằng tổng optimizer updates. Seed mới chưa được cấp trong đợt này; nếu có gain sẽ đề xuất confirmation riêng, không gọi một seed là ổn định.

## Quan sát sớm và bảo toàn

Đo train/selection BCE và macro AP ở epoch0 và sau steps15/30 của epoch1. Chỉ diagnostic; không đổi checkpoint selection, early stopping hoặc threshold. Diagnostic không tiêu thụ sampler, không đổi RNG/optimizer/BN, khôi phục train mode. Với resume giữa epoch, chỉ output của completed epoch có authority; diagnostic records phải ghi attempt/step và không giả thành committed history. Tổng thời gian tính cả diagnostic trong wall budget.

Mỗi main run tối đa 2 giờ wall time, chạy tuần tự, tổng tối đa 8 giờ; smoke/recovery tối đa 30 phút tổng. **Trần training 8,5 giờ, không phải dự báo phải dùng hết.** Wall-time exhaustion giữ INTERRUPTED theo lifecycle, không tự tăng budget, batch/LR hoặc chạy thêm seed. Phần evaluation development/verification thực hiện một lần theo outputs sau run, không benchmark lại 500 lần vì architecture/input không đổi.

## Implementation sau approval

Tái dùng adaptation model/trainer/config; mở schema/version đúng scope cho head provenance và diagnostic schedule. Không nhét warm head vào schema random rồi giả seed là provenance. Head mới có parent checkpoint SHA, epoch, tensor digest; kiểm keys/shapes/finiteness và exact weights/head pins. Guard v1/v2 và final-test không nới; code mới tạo identity mới, giữ source snapshot cũ để tái lập E004.

Tests cần có: head extraction bằng đúng fc của parent; backbone reset; optimizer reset; random baseline compatibility; diagnostic không đổi weights/RNG/sampler/BN/mode sau tiếp tục train; resume và early best epoch parity; unknown/mask và budgets giữ nguyên. Smoke kiểm hai initialization, hai LR, một recovery drill trong tổng budget; configs smoke tách riêng và không dùng checkpoint smoke để initialize main runs. Source/tests checks PASS trước materialize receipt/config mới.

Sau owner duyệt plan, có thể freeze exact runnable configs và code/pins từ implementation đúng variables này, chạy smoke rồi bốn main runs trong budget mà không hỏi lại cùng scope. Nếu implementation cần đổi scientific variables/cohorts/selection rule/budget, dừng phần đó và nêu delta. Không ghi approval receipt trước khi có lời duyệt thật.

## Đọc kết quả và điểm dừng

Primary contrast BCE selection; báo thêm macro/per-target AP, precision/recall/FPR tại 0,5, train/selection gap, tất cả family và ngoài CF-Q072. Không chỉ báo arm tốt nhất. Không dùng diagnostic49 để chọn winner khi selection đi ngược. Không đặt ngưỡng gain mới chưa được duyệt: contrast là descriptive ở một seed, cần đọc mức độ và tradeoffs.

Nếu gain chỉ nằm ở train hoặc không giữ ranking/family behavior, không kéo dài epochs; quay lại evidence/data/input. Nếu chỉ một arm tốt lên, ghi exploratory candidate-for-further-research, không Selected. Đợt này không giải quyết M4 hoặc independence; waiver cũ không trở thành quyền final-test mới. Reserve199 và test11 giữ đóng; không thêm nguồn, weights, labels, augmentation hoặc architecture khác.

## Quyết định owner cần chốt

Duyệt hoặc sửa **matrix 4 runs, head LP epoch10, LR layer4 1e-4/1e-5, diagnostic schedule và trần 8,5 giờ training CPU**, kèm implementation/fixtures → freeze exact configs → smoke → main runs → development analysis trong scope trên. Đây là phần mới chưa có trong approval ngày 13/10.
