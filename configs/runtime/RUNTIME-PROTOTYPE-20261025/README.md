# Runtime prototype — Đề xuất ngày 25/10/2026

Trạng thái: **Accepted cho detector/license/crop/output và implementation ngày 25/10/2026**; [authorization](owner-authorization.json) ghi lời duyệt và config digest. Approval gốc áp dụng cho implementation và synthetic checks; quyền media theo receipt riêng của từng lượt. Quyết định [chuyển phase và chọn G0](../../../artifacts/reports/e008-v14-colab-20261024/prototype-decision-20261025.md) đã Accepted; không hỏi lại phần đó. Thiết kế slice đầu đã materialize thành [runtime.yaml](runtime.yaml); chưa cấp quyền chạy trên media chưa duyệt.

## Thiết kế đề xuất

Recorded video local → frame/time → detector person → context crop → hai score G0 → JSONL và gallery QA. Chưa thêm tracking/risk/web trong slice này. Logic ở `src/ai_exam_monitoring/inference`, variables runtime ở YAML mới sau approval; không đổi training configs đã pin hoặc evaluator lịch sử.

| Thành phần | Thiết kế được duyệt | Lý do / giới hạn |
|---|---|---|
| Detector | Ultralytics YOLOv8n pretrained COCO, chỉ `person`; xác minh taxonomy của weights, không dùng detection class ID làm target classifier | Tái dùng dependency/adapter hiện có; chưa có benchmark phòng thi |
| License | Owner chấp nhận hướng AGPL-3.0 của Ultralytics cho prototype; không tự đổi license repository hoặc công khai source | Nếu không chấp nhận, chuẩn bị detector khác trước implementation |
| Variables detector | `imgsz=640`, `conf=0.25`, `iou=0.7`, `max_det=100`, FP32, local CPU | Giá trị khởi đầu để QA, không là quality threshold hay SLA; không tự tune sau xem clip |
| Sampling | Xử lý mỗi frame được decode ở slice đầu; dùng timestamp video do decoder cung cấp, kiểm đơn điệu; thiếu timestamp hợp lệ thì báo lỗi | Không lấy chỉ số detection làm chỉ số frame; không bỏ frame im lặng; chưa hứa realtime |
| Person box | Clip vào frame; floor cạnh trái/trên, ceil cạnh phải/dưới, XYXY right/bottom exclusive; reject box rỗng/nonfinite | Geometry có provenance từ detector; không ước lượng phần người bị che |
| Context crop v1 | Mở rộng mỗi bên trái/phải 20% chiều rộng person box, phía trên 10% chiều cao và phía dưới 20%; clip vào ảnh | Heuristic mới để giữ đầu/tay/bàn, không tuyên bố tương đương reviewed crops; không gán thiết bị hàng xóm cho anchor |
| Classifier | G0 seed 20261023, best checkpoint đã chọn; `eval`, FP32, batch 1, CPU, không augmentation | Runtime mới phải có receipt riêng; không gọi CPU là tái lập CUDA bitwise |
| Preprocess | RGB, letterbox bilinear 336 px; fill `[124,116,104]`, mean `[0.485,0.456,0.406]`, std `[0.229,0.224,0.225]`, global mean pooling | Tái dùng đúng transform/model theo config và kiểm pixel parity; ngưỡng từ calibration, không lấy scalar `threshold` trong config training |

Nguồn chính thức đã tra ngày 25/10/2026: [YOLOv8](https://docs.ultralytics.com/models/yolov8/), [predict parameters](https://docs.ultralytics.com/modes/predict/), [Ultralytics licensing](https://www.ultralytics.com/license). Ultralytics công bố lựa chọn AGPL-3.0 và Enterprise; không coi pretrained weights là mặc nhiên miễn điều kiện sử dụng. Đã tải weights chính thức, pin SHA/taxonomy và môi trường tại [receipt](../../../artifacts/reports/runtime-prototype-20261025/detector-acquisition.json). Dùng Ultralytics 8.3.221 và OpenCV 4.11.0.86 để giữ NumPy/Torch hiện hành. Thiếu pin thì dừng run.

## Output và QA trước downstream

Đề xuất JSONL runtime có version riêng, không thay dataclass `Prediction` hiện hành: metadata source/model/config/code/environment hashes; observation gồm frame index/time, anchor ID trong frame, person/context boxes, detector confidence, hai score, target order, ngưỡng và hai cờ vượt ngưỡng. Hai cờ không là nhãn ground truth hoặc kết luận gian lận. Frame không detection có record để phân biệt với lỗi xử lý; lỗi có kết quả failed riêng, không giả completed. Không gán track ID khi chưa tracking.

Tests dùng synthetic fixtures cho geometry/clipping, RGB/letterbox parity, thresholds/order, empty frame, timestamps, input/checksum failures và output không ghi đè. Checkpoint loader kiểm SHA/config/target order, không fallback random hoặc tự tải pretrained. QA thực tế xuất tối đa 20 frame phân bố đều theo thời gian và các lỗi kỹ thuật, gồm source → box → crop → input để owner review batch. Báo người bị bỏ sót, crop sai anchor, lẫn người khác, thiếu context, false/missed behavior và latency/RAM; không gán PASS chất lượng từ software checks. Owner quyết định chấp nhận crop hoặc revision mới trước tracking/events; không sửa V14.

## Video và policy đầu vào cần owner cung cấp/chốt

Đề xuất bắt đầu một clip MP4 ghi sẵn dài 30–60 giây, một camera cố định, đủ thấy đầu/tay/bàn, khoảng 3–5 người cho smoke; sau đó mới clip đại diện 10–15 người theo MVP. Đây là phạm vi thử, không sửa mục tiêu sản phẩm. Clip diễn lại hành vi được đồng ý sử dụng là lựa chọn ưu tiên; YouTube/public link tự nó không chứng minh rights. Không dùng holdout/test hoặc nguồn chưa rõ quyền.

Trước media run cần đường dẫn local và xác nhận quyền xử lý cho scope demo; ghi checksum, nguồn/rights và policy không chứa danh tính. Đề xuất chỉ chủ repository truy cập local, không third-party processing/upload; không thu âm phục vụ pipeline. Giữ clip/crops/gallery tối đa 7 ngày kể từ lần QA, hoặc xóa sớm theo yêu cầu chủ dữ liệu; giữ metadata phi định danh để truy vết. Xóa theo inventory đã duyệt và xác minh; nếu sai quyền/lộ media thì dừng xử lý, thu hồi quyền truy cập và báo owner. Đây là policy cho slice được duyệt; vẫn cần rights/consent đúng clip, không tự cấp consent hoặc lệnh xóa dữ liệu hiện hành.

## Phạm vi approval thiết kế

Owner duyệt detector/license, variables/crop/output contract và software implementation/tests ở trên. Download weights chính thức và pin dependency được bao gồm nếu owner duyệt phương án; media smoke chỉ sau khi có clip và policy/rights cụ thể. Nếu chưa có video vẫn có thể triển khai và kiểm synthetic sau design approval. Approval thiết kế không bao gồm training, final test, upload hoặc tracking/risk/UI. Commit source được owner yêu cầu riêng trong task cleanup.


## Thực thi và giới hạn hiện tại

Cài thêm `requirements/runtime-cpu.txt` vào môi trường classifier CPU hiện có; không cài đồng thời OpenCV headless từ `requirements/ml.txt`. [Environment freeze](../../../artifacts/reports/runtime-prototype-20261025/environment-freeze.txt) ghi môi trường đã kiểm. [Bàn giao software](../../../artifacts/reports/runtime-prototype-20261025/README.md) ghi tests và giới hạn.

CLI (chỉ chạy khi đã có receipt media do owner duyệt):

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.inference.runtime --config configs/runtime/RUNTIME-PROTOTYPE-20261025/runtime.yaml --workspace . --source <clip-local.mp4> --media-approval <receipt.json> --output outputs/<session-moi>
```

Dùng [receipt mẫu chưa duyệt](media-approval.example.json) để chuẩn bị theo đúng SHA clip; không đổi `status` thành approved nếu chưa có quyết định owner. CLI không thu nhận URL/webcam, không mở test dataset, không tự download hoặc tune threshold. Video phải có frame count/FPS hợp lệ và timestamp decoder tăng nghiêm ngặt; clip không đáp ứng sẽ bị từ chối, không tự suy timestamp từ FPS. Preflight decode toàn clip trước lượt inference để chọn gallery theo thời gian; không bỏ frame. Tối đa 19 frame QA đều theo thời gian và một slot cho lỗi kỹ thuật.

Output có `session.json` (trạng thái cuối có thẩm quyền), `predictions.jsonl`, config/code/environment provenance, checksums và `index.html`/PNG QA. Mỗi record frame giữ cả trường hợp không detection. `frames_processed` chưa có nghĩa session completed; chỉ outcome cuối và session mới xác nhận sau kiểm source SHA. Lỗi trước inference vẫn ghi failed session; không log đường dẫn media trong thông báo lỗi/provenance command. Gallery chỉ xem local và cần owner review; 7 ngày retention được ghi trong session, chưa có tác vụ tự xóa. Metadata cũng cần giữ local nếu có thể liên kết về clip.


## Điểm xuất phát cho phase tiếp theo

Owner yêu cầu dọn ba thử nghiệm video và các configs/receipts/results riêng ngày 25/10/2026; không dùng lại output đó làm evidence nghiệm thu. Giữ config prototype và các pins model/detector phục vụ tích hợp. Code vẫn hỗ trợ schema v2 với `sampling_hz` là số nguyên 1 hoặc 2; lượt mới cần config identity/approval và media receipt riêng, không sửa config prototype đã pin. Sampling giữ frame index/time gốc, không đảm bảo phát hiện hành vi giữa hai mốc. [Cleanup và bàn giao](../../../artifacts/reports/runtime-prototype-20261025/cleanup-20261025.md) ghi availability và checks.
