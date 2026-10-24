# Đặc tả training và evaluation

## 1. Phạm vi

Contract experiment, loss/metrics, provenance, test access và promotion. Recipes/numerical gates của từng experiment nằm trong hồ sơ được duyệt, không trở thành default toàn dự án. [Configs index](../configs/experiments/README.md) dẫn tới proposal/config/approval; [reports index](../artifacts/reports/README.md) dẫn tới results/error analysis; [reference](reference.md#training-code) mô tả trainer/CLI hiện có. Không thêm kết quả run hoặc việc tiếp theo vào spec.

## 2. Dữ liệu, loss và metrics

Loader phải kiểm payload/inventory, schema/encoding, membership/usage/rights/split/freeze và approval đúng scope trước sử dụng. Unknown không thành negative; không glob crops hoặc đưa review-only/U-U vào supervision. Guard implementation cụ thể xem reference; thiếu input xử lý theo [retention](storage.md#thiếu-input), không bỏ kiểm tra.

JSON unknown là null/mask 0; tensor có placeholder để tính nhưng loss/metric chỉ lấy known positions. Objective full-batch cần known support cho mỗi target. Với mini-batch phải chốt aggregation/empty-target handling; không biến U thành N hoặc sửa loss ngầm để tránh batch lỗi.

Metrics giữ P/N/U, TP/FP/FN/TN, precision/recall/F 1/AP từng target, macro masked BCE và macro AP. AP non-interpolated, equal scores xử lý theo nhóm. Macro AP chỉ có khi cả hai target có AP hợp lệ. Thiếu P hoặc N thì metric unavailable/null; không positive predictions thì precision null, không fake 0 hoặc PASS. Co-occurrence báo fully-known denominator/support; thiếu support thì không công bố như metric đáng tin.

Đối chứng hằng dùng prevalence chỉ tính từ train, không fit prevalence trên val/test. Ngưỡng quyết định theo protocol được duyệt; không fit ngưỡng trên test. Selection/hyperparameter dùng development; validation đã dùng chọn epoch không là holdout độc lập. Báo cùng cohort/labels/masks/protocol trước so delta; AP cao không bảo đảm chất lượng tại operating point đã chọn trong protocol.

Riêng [E007 V13 đã duyệt](../configs/experiments/E007-V13-20261024/README.md), schema `representation-adaptation-v4` hiệu chỉnh một cặp ngưỡng trên validation sau chọn checkpoint, xét các mốc score và endpoints đã định nghĩa, rồi giữ nguyên cặp đó cho train/validation/slices/reload. GPU FP32 và trạng thái RNG CUDA thuộc identity/resume; research chỉ chạy sau smoke trên cùng môi trường. Đây là development trên release không có test, không thay semantics hoặc pins của trainer lịch sử.

## 3. Experiment contract và quyền theo hành động

Một run cần ID/owner/hypothesis/parent, config digest, code identity/Git commit+dirty, data/split/encoding/payload/weights versions, environment/dependencies/seed, command, start/end/status, metrics, artifacts/checksum và observation/decision. W&B optional disabled, không thay bản lưu local; không log media chưa có quyền.

Phân biệt quyền theo hành động; bảng này không cấp approval mới hoặc thay numerical gates:

| Hành động | Điều kiện trước hành động | Kết quả không tự cấp quyền |
|---|---|---|
| Proposal/nghiên cứu | User scope và evidence được phép; ghi rõ phần Draft | Không tự cấp quyền implementation scientific chưa chốt, run hoặc test |
| Implementation và software fixtures | Design/contract thay đổi đã được duyệt đúng phạm vi; phần độc lập theo yêu cầu user có thể làm trước | Code/tests PASS không là run approval hoặc model acceptance |
| Smoke dùng dữ liệu/weights thật | Config/scope/inputs/compute được phép cho smoke; kiểm pins và môi trường | Smoke kiểm chứng design sau approval, không là điều kiện để owner bắt đầu duyệt design |
| Training run | Recipe/config/data/compute/protocol và approval đúng identity; readiness/smoke cần thiết đã PASS | FINISHED không Selected; không mở final test |
| Final test | Candidate/protocol/holdout được freeze, quyền truy cập riêng và guard theo protocol | Không được tuning hoặc mở lại chỉ vì đổi output |
| Selected/promotion | Evaluation hợp lệ, quality gates được chốt và owner decision đúng use scope | Không tự nghiệm thu runtime/video/demo |

Ngoại lệ chuyển phase [E008-PROTOTYPE-20261025](../artifacts/reports/e008-v14-colab-20261024/prototype-decision-20261025.md) cho phép chọn model cho tích hợp prototype dù chưa đạt numerical gates nghiên cứu. Ghi rõ use scope và hạn chế trong decision riêng, giữ nguyên kết quả/gates/Selected lịch sử; không thay final-test access hoặc nghiệm thu chất lượng video.

Proposal cụ thể có thể yêu cầu điều kiện chặt hơn. Điều kiện holdout/promotion không tự trở thành điều kiện mọi software task; run chẩn đoán scope khác vẫn cần owner duyệt riêng, không tự thu hẹp proposal hiện hành để chạy. Workflow cho **một experiment mới được duyệt**:

1. Xác định hypothesis và biến thay đổi từ lỗi/data đã biết; tạo ID/config/protocol/approval rõ scope. Không sửa run/config đã pin hoặc reuse output để thử recipe khác.
2. Kiểm đủ dataset/split/label/rights/freeze/pretrained và version/pins, hardware/budget, source checkout/dependencies. Code khác historical SHA cần run identity mới hoặc restore source gốc; không sửa pin để hợp thức hóa.
3. Smoke riêng kiểm loader, objective, shapes/masks, optimizer trainable/frozen policy, memory và checkpoint interruption/resume. Không smoke lại run đã xong nếu không có thay đổi cần kiểm.
4. Chạy trainer vào output mới. Resume chỉ cùng identity; CLI xem implementation reference. Run train chỉ train/val, không test.
5. Kiểm status/last/best/history/config/environment/checksums; reload validation bằng evaluator và đối chiếu reproducibility. Phân tích errors/slices bằng score đã lưu trước khi quyết định bước sau.
6. Chỉ freeze candidate/protocol và mở final test khi có approval riêng, đủ support/rights/independence. Không đổi model/threshold/slice rồi thử lại cùng test sau thấy kết quả.
7. Ghi decision Continue/Rejected/Candidate/Selected có evidence và limitations. FINISHED là trạng thái kỹ thuật, không Selected; promotion cần owner nghiệm thu.

Output chính `outputs/<ID>/` có `run.json`, `resolved-config.json`, `best.pt`, `last.pt`, `history.json`, `metrics.json`, `predictions-train.json`, `predictions-val.json`, features/cache và `checksums.json`; reports nhỏ giữ trong Git khi cần bàn giao. Retention sau khi đóng run theo [chính sách tài sản hiện hành](storage.md): chỉ nghỉ lưu checkpoint khi không còn consumer cần file; không sửa checksum gốc hoặc nới evaluator. Checkpoint last giữ head/optimizer/RNG/epoch/best/early-stop/history; writes atomic. Resume từ chối code/config/data/features khác. OOM/FAILED/INTERRUPTED phải ghi đúng status và lỗi; không giảm batch hoặc đổi config trong cùng identity.
