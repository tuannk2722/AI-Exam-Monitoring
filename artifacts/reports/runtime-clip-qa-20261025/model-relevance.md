# E008-A1 và E005-Dual ROI liên quan thế nào đến lỗi runtime?

Đối chiếu code/config/metadata local ngày 25/10/2026 theo yêu cầu owner. Đây là phân tích và đề xuất, không thay model prototype G0, không inference/train mới, không nghiệm thu labels hoặc role policy.

## Ba vấn đề cần tách riêng

| Vấn đề | Evidence / trạng thái | A1 và Dual ROI có giúp trực tiếp không? |
|---|---|---|
| Box trùng/lồng nhau | Đã quan sát ở source/gallery, nhiều anchor cùng người; không phải mọi overlap đều là duplicate | Không. Cả hai nhận ROI sau detector, không thực hiện person detection hoặc NMS |
| Crop nhạy, ảnh hưởng ngữ cảnh hàng xóm | Cùng người/cùng frame có score khác nhau và crop chứa thiết bị hàng xóm; attribution còn draft cần owner review | Có liên quan về kiến trúc, đáng làm đối chứng riêng; chưa có evidence giải quyết lỗi runtime |
| Vai trò người trong phòng | YOLO chỉ lọc `person`; classifier chỉ có phone/looking, không có đầu ra vai trò hoặc policy eligibility | Không. Người di chuyển không tự là giám thị; ngồi không tự là thí sinh. Đây là capability/scope còn thiếu, không là lỗi đã đo của role model |

Evidence runtime: [QA 1 Hz](qa-1hz.md). Các anchor không là track ID; chưa có nhãn role accepted. Không tự lọc theo đồng phục, dáng đứng/ngồi hoặc score looking để quyết định vai trò.

## E008-A1: person-box spatial pooling, vẫn thấy context

Theo [proposal V14](../../../configs/experiments/E008-V14-LOOKING-20261024/proposal.yaml), A1 là DINOv2 ViT-S/14, input context 336 px, `person_2x2`. [spatial_pooling.py](../../../src/ai_exam_monitoring/training/spatial_pooling.py) nối CLS với 4 vùng pooling theo diện tích giao patch/bin trong person rectangle, tạo 1.920 chiều. Rectangle được map qua rounded letterbox; [loader](../../../src/ai_exam_monitoring/training/adaptation_data.py) chọn vùng person thay context.

**A1 không cắt bỏ ảnh hàng xóm trước backbone và không là attention mask cô lập người.** [Model forward](../../../src/ai_exam_monitoring/training/adaptation_model.py) tính tokens toàn context trước pooling; CLS và self-attention vẫn có thể chứa thông tin ngoài person box. Box sai/trùng vẫn làm pooling sai hoặc tạo nhiều predictions; điện thoại trên bàn ngoài person box có thể ít được nhấn mạnh. Đó là giả thuyết cần kiểm, không kết luận chắc A1 sẽ tốt hơn hoặc tệ hơn G0 trên clip này.

Trong [screening E008 V14](../e008-v14-colab-20261024/results-20261025.md), cùng seed 20261023 và cùng validation:

| Arm | Macro AP | Looking AP | Looking precision / recall |
|---|---:|---:|---:|
| G0 | 0,9178 | 0,9041 | 0,7931 / 0,7931 |
| A1 | 0,8893 | 0,8446 | 0,6944 / 0,8621 |

A1 tăng recall looking nhưng nhiều false positives hơn, không thắng screening; chỉ A1 một seed nên không tổng quát hóa thành thất bại của mọi cách dùng ROI. Validation development có 29 looking positive, không đủ support lịch sử; 69/156 crop có person box bằng context nên A1/G1 pooling cùng vùng ở những crop đó. Đây không là phép đo attribution trên camera hiện tại.

Checkpoint A1 screening được metadata pin SHA `47a016e20c726e8bfcaf2c2fa2ce71054b86d4a8a3e8b84173c7ef6ccb2aa0cf`, calibration phone/looking `[0.4009137451648712, 0.3031960725784302]`. [Handoff](../e008-v14-colab-20261024/checkpoints-20261025.md) chỉ nhận ba G0; kiểm filesystem outputs hiện tại không có best.pt A1. Cloud availability chưa được kiểm, không hứa checkpoint còn trên Drive. Nếu owner muốn chạy A1 sau đối chứng detector, cần exact bundle/checkpoint/config/calibration/source/license, loader geometry và approval use scope riêng; không dùng ngưỡng G0 cho A1.

## E005-Dual ROI: hai nhánh cùng backbone và geometry tương đối

[Thiết kế E005](../../../configs/experiments/E005-V11-20261018/README.md) có hai arm Dual ROI `AC-L4B1` và `AC-L4`. Code trích anchor subcrop từ context image theo person box với padding 0,05, letterbox 224 px; chạy shared ResNet18 cho anchor/context, nối `fa`, `fc`, `fa - fc` và 6 số `[rx1, ry1, rx2, ry2, rw, rh]` thành 1.542 chiều trước MLP. [Geometry/extraction](../../../src/ai_exam_monitoring/training/data.py), [forward](../../../src/ai_exam_monitoring/training/adaptation_model.py).

Kiến trúc này có thông tin anchor/context tường minh hơn G0 và phù hợp để đặt giả thuyết attribution. Tuy nhiên nó vẫn học từ cả hai nhánh, không có ownership constraint bắt buộc; thiết bị ngoài person ROI có thể mất ở nhánh anchor, còn context vẫn chứa người khác. Anchor là subcrop từ ảnh context đã lưu, không mặc nhiên là ROI native từ source video. Nhận xét trong report cũ về resize/mờ/head lớn là giả thuyết, chưa được tách bằng đối chứng nhân quả.

Trên **V11**, [kết quả E005](../e005-v11-adaptation-20261018/README.md): Dual ROI Macro AP 0,7119, single-crop S1-AUG 0,7378; slice multi-person-context có Macro AP 0,5952 so với 0,6339, support thấp nên không dùng làm quality acceptance. Hai dual arms chọn epoch 2 trong warm-up, cùng model tensors tại best; không coi là hai xác nhận độc lập cho representation. Không so trực tiếp các số V11 này với V14 để xếp hạng khả năng runtime.

Hai best.pt Dual ROI đã nghỉ lưu trong [manifest cleanup](../cleanup-20261024/cleanup-manifest.json), filesystem hiện tại không có. Metadata/pins còn nguyên; không train lại để lấp checkpoint thiếu. Chỉ xét restore nếu task yêu cầu và tìm được exact backup được xác minh. Đổi sang native ROI hoặc kiến trúc mới là experiment khác, không gọi là tái lập E005.

## Tích hợp không chỉ là thay đường dẫn weights

[BundleClassifier](../../../src/ai_exam_monitoring/inference/classifier.py) chủ động chỉ nhận G0/global_mean/seed đã duyệt và một tensor context. A1 cần `context + pooling_box`; Dual ROI cần `anchor + context + geometry`, preprocessing/calibration riêng. Model forward E005 có fallback single tensor bằng anchor=context, nhưng dùng nó sẽ mất ý nghĩa Dual ROI; không dùng fallback để vượt việc thiếu geometry. Không nới guard hoặc sửa evaluator lịch sử cho convenience.

## Kết luận sử dụng

Ưu tiên đối chứng detector trước với G0 giữ nguyên để tách nguyên nhân box trùng. Sau khi owner chốt anchor/crop batch, A1 là ứng viên attribution hợp lý để so sánh trên cùng source/anchor/context nếu có checkpoint đúng pins; E005 chủ yếu là bài học thiết kế và evidence lịch sử, chưa là phương án thay model tức thì. Role/eligibility phải có quyết định riêng; hai model không giải quyết nó.

[Proposal đối chứng](../../../configs/runtime/RUNTIME-DETECTOR-REVIEW-20261025/README.md) tách ba nhánh, không gom thay detector, model, crop và roles vào một run. Không hứa A1/Dual ROI sửa được lỗi hiện tại trước phép đo có ground truth đúng scope.

Metadata c?a 5 run ??i chi?u trong task ?? ???c ki?m theo checksums l?ch s?; [b?ng evidence local](../../../outputs/runtime-detector-review-20261025/model-evidence.json) l?u metrics v? hashes t??ng ?ng. Ki?m metadata kh?ng ch?ng minh checkpoint payload c?n t?n t?i.
