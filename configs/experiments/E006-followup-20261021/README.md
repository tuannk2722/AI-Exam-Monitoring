# E006 follow-up — đối chứng random erasing

**Draft ngày 21/10/2026; chưa approved, chưa executable config, chưa quyền smoke/run/test.** Owner đã giao chẩn đoán và đề xuất, chưa chọn scientific variables của run mới. [Bằng chứng](../../../artifacts/reports/e006-v12-diagnostics-20261021/README.md) và [review nhãn](../../../artifacts/reports/e006-v12-diagnostics-20261021/LABEL-REVIEW.md) là đầu vào.

## Câu hỏi và giả thuyết

Random erasing không biết vị trí bằng chứng hành vi. Preview đúng seed/index của E006 cho thấy vùng mặt có thể bị che trong khi looking label vẫn known. Kiểm xem bỏ riêng erasing có cải thiện khả năng phân biệt trên development hay chỉ làm overfit thêm. Không coi preview là bằng chứng augmentation gây lỗi model.

## Thiết kế đề xuất duy nhất

| Biến | Arm control | Arm candidate |
|---|---|---|
| Recipe | SQRT single-crop ResNet18/MLP theo E006 | Giống control |
| `random_erasing_prob` | 0,15 | 0,00 |
| Seed screening | 20261020 | 20261020 |
| Khởi tạo | ImageNet weights đúng pin, head mới | Cùng initialization/RNG policy |
| Dataset/cohorts/labels/masks | Một package accepted đã freeze cho cả hai arm | Giống control |
| Schedule, layer4.1, dropout, smoothing, weighting, các augmentation khác | Giữ recipe SQRT E006 | Giống control |
| Checkpoint selection / threshold protocol | Giữ val Macro AP, BCE tie-break và calibration protocol E006 | Giống control |

Đề xuất hai run mới có identity/config riêng trên cùng code/environment. Không lấy E006 khác dataset hoặc khác validation labels làm matched control. Ngay cả khi giữ V12, dùng identity mới; không sửa E006 đã pin. Tắt erasing dùng biến đã có, không cần thiết kế backbone hay detector mới.

## Dataset và thứ tự trước run

1. Owner chốt bốn ngoại lệ và bộ ví dụ. Nếu sửa nhãn/crop/membership thì cần package mới và delta approved trước khi materialize config; nếu giữ nguyên thì V12 vẫn là input. Chưa tự đặt số version tiếp theo hoặc chọn membership.
2. Chốt scope bù coverage riêng. Không đưa dữ liệu mới chỉ vào một arm. Cùng validation đã chốt cho cả hai; không cân/lọc lại sau thấy score. Hai arm vẫn là development, không independent test.
3. Giữ training recipe làm đối chứng: nếu dataset mới không đủ điều kiện áp recipe hiện hành hoặc cần đổi weighting thì phải revision proposal trước khi chạy, không silent thay biến trong một arm.
4. Exact run IDs, package/config/code/weights/environment/protocol pins và owner compute approval cần hoàn tất. Đề xuất local CPU 4 threads, tối đa 7.200 giây mỗi research run theo mức tham chiếu E006, **không kế thừa quyền compute E006**. Smoke chỉ theo readiness của cấu hình mới được duyệt, không tự chạy.

## Đo và quyết định

- Báo P/N/U và groups, AP/BCE, precision/recall/FPR/confusion từng target ở 0,50 và ngưỡng calibration riêng theo cùng protocol, số lỗi lặp đã review còn tồn tại, learning curves và reload parity.
- Giữ gate đã có: precision ≥ 80%, recall ≥ 80%, FPR ≤ 20% cho cả hai target, support như protocol. Không chọn chỉ vì looking recall tăng khi phone giảm hoặc false positives tăng. Một seed chỉ screening; không gọi chênh nhỏ là ổn định/thống kê có ý nghĩa.
- Nếu candidate vẫn fail: tiếp tục nghiên cứu, không Selected; dùng loại lỗi còn lại để quyết định bù dữ liệu hay pilot định vị phone. Không tự chạy thêm seed/recipe.
- Nếu candidate có tín hiệu cải thiện: owner xem mức cải thiện từng target, uncertainty và trade-off trước duyệt xác nhận nhiều seed. Final-test/candidate freeze/Selected là scope riêng, không nằm trong proposal này.

## Khi nào mới ưu tiên detector

Chỉ mở proposal phone detector nếu còn lỗi phân biệt/định vị mobile dù source đủ evidence, và có data/bbox completeness, attribution-to-anchor, license/pretrained/compute được chốt. Đánh giá cả detector và phone target cuối cùng trên cùng cohort; không map “không detect” thành N. Looking cần hướng xử lý riêng. Không thay kiến trúc B hoặc model downstream bằng proposal này.
