# RUNTIME-QA-PREP-20261025 — Protocol QA video mới

Trạng thái: **Draft, đã được giao chuẩn bị; chưa là quyền chạy media hoặc nghiệm thu chất lượng.** Owner: chủ repository. Task ngày 25/10/2026 được duyệt sau audit codebase: hoàn thiện runtime và chuẩn bị protocol QA. Không mở lại ba thử nghiệm đã retire. Protocol này phục vụ FR-VID-01 và FR-CROP-01 trong [system](../../../docs/system.md); không là final test, benchmark tracking hoặc nghiệm thu demo.

## 1. Câu hỏi và cấu hình giữ nguyên

Kiểm chuỗi video → person → context crop → input → hai score để xác định lỗi thuộc detection, crop/attribution, classifier hay thời gian xử lý. Chỉ sau owner review batch và quyết định crop phù hợp mới đề xuất slice tracking.

Dùng [runtime.yaml đã duyệt](../RUNTIME-PROTOTYPE-20261025/runtime.yaml) và [authorization](../RUNTIME-PROTOTYPE-20261025/owner-authorization.json): full-frame, YOLOv8n CPU, context-v1, G0 seed 20261023 CPU FP32/batch 1, preprocessing 336 px và calibration đã pin. Ngưỡng phone/looking lần lượt `0.5` và `0.3914746344089508`. Không tune sau xem clip; không sửa YAML/pins đã duyệt. Sampling 1/2 Hz chỉ là khả năng code; muốn dùng phải tạo identity/config và approval mới, xác định lại phạm vi bỏ sót giữa các mốc. Session/output mới không bắt buộc đổi runtime identity khi variables giữ nguyên.

## 2. Đầu vào cần bổ sung trước run

Đề xuất lượt đầu một MP4 local 30–60 giây, camera cố định, 3–5 người, thấy được đầu/tay/bàn; ưu tiên clip diễn lại có quyền sử dụng. Sau review lượt đầu mới đề xuất clip đại diện 10–15 người. Đây là phạm vi QA đề xuất, không là quota dữ liệu hoặc SLA đã Accepted.

Owner cung cấp đường dẫn local và xác nhận quyền xử lý đúng clip; không tìm hoặc tải clip thay owner. Agent ghi SHA256, metadata kỹ thuật và tạo receipt từ [mẫu](../RUNTIME-PROTOTYPE-20261025/media-approval.example.json) theo lời duyệt thực tế. Không ghi danh tính/đường dẫn riêng tư vào Git. Receipt phải xác nhận không phải test/holdout, chỉ local owner, không upload/third-party processing, retention tối đa 7 ngày. Không giả status approved từ approval phần mềm.

Trước inference, đóng phạm vi clip và các đoạn quan sát cần review: hành vi phone, nhìn quanh, hoạt động dễ nhầm và vùng bị che nếu clip có. Thiếu tình huống nào thì ghi thiếu coverage, không tự suy negative. Owner duyệt protocol và receipt gắn exact clip; lựa chọn clip/đoạn không dựa trên score model. Không yêu cầu owner annotate từng frame: agent chuẩn bị batch và ngoại lệ, owner review/chốt.

## 3. Thực hiện và bằng chứng kỹ thuật

1. Kiểm config approval và tất cả pins; ghi code identity, OS/CPU/RAM và môi trường thực tế. Giữ model/config cũ, runtime code mới có provenance riêng.
2. Tạo output mới dưới `outputs/<session-id-moi>`. Dùng CLI hiện có trong README runtime với exact source/receipt. Một lượt QA ban đầu, không tự chạy lặp/tune. Không có warm-up riêng; ghi rõ điều này khi báo timing.
3. CLI preflight decode toàn clip rồi xử lý full-frame. Kiểm frame count, index, timestamp tăng nghiêm ngặt; lỗi decode/pin/rights dừng, không tự đổi codec, timestamp hoặc bỏ frame.
4. Đối chiếu `session.json` completed với outcome cuối JSONL, nguồn SHA và checksums. Có `frames_processed` chưa đủ. Frame không detection vẫn phải có record. Lỗi giữ failed outcome; `failed_frame_index` chỉ frame nguồn đang xử lý, null nếu iterator chưa cung cấp frame, không gán frame trước đó làm lỗi.
5. Giữ JSONL, session/config/code/environment/checksums và gallery local để review. Gallery mặc định tối đa 19 frame đều theo thời gian, dành một slot cho lỗi. Không đọc gallery như toàn bộ video hoặc tự coi kỹ thuật PASS là chất lượng PASS.

## 4. Review batch và phân loại lỗi — đề xuất chờ owner chốt

Agent dùng gallery/source và các đoạn đã chọn trước score để lập bảng review local. Ngoài frame có observation, phải xem người bị bỏ sót và vùng không detection trên source. Các case chọn bổ sung sau xem score ghi riêng là chẩn đoán, không gộp thành mẫu đại diện. Gallery hiện có không tự trích mọi đoạn hành vi; nếu cần export thêm media thì ghi phạm vi trong receipt/output mới trước thực hiện.

| Nội dung | Cách ghi đề xuất |
|---|---|
| Truy vết | Source SHA, frame index/time, anchor trong frame hoặc mã review local khi không có detection; không giả track ID |
| Person | Người nhìn thấy bị bỏ sót, detection trùng/sai, che khuất hoặc không đủ quan sát |
| Crop | Đúng anchor, thiếu đầu/tay/bàn, lẫn người/điện thoại bên cạnh, cắt mất bằng chứng; dẫn source → box → crop → input |
| Hai target | Review riêng phone/looking theo semantics hiện hành; P/N/U, unknown không tính thành negative; giữ score và ngưỡng riêng với nhận xét |
| Lỗi và giới hạn | Báo nhầm/bỏ sót tại observation đã review; phân biệt lỗi detector/crop với classifier, chưa kết luận nhân quả nếu chưa đủ bằng chứng |
| Quyết định owner | Chấp nhận crop cho scope clip, cần revision, hoặc chưa đủ bằng chứng; ghi ngoại lệ và phạm vi áp dụng |

Đề xuất báo counts và mẫu số của cohort đã review, coverage và danh sách FP/FN cụ thể. Chưa tự chọn IoU matching, tỷ lệ chất lượng, event duration hoặc ngưỡng pass hệ thống. Không suy precision/recall toàn video từ gallery, không tính false/missed events khi chưa có event contract. Không dùng QA này làm holdout độc lập hoặc thêm vào V14.

## 5. Hiệu năng và giới hạn phép đo

Ghi resolution/FPS/duration, số frame/observations, hardware/OS/dependencies, startup, elapsed, mean/p50/p95 frame và peak RSS từ output. `startup_seconds` gồm preflight decode và model initialization; `frame_processing_ms` gồm detector/classifier/JSONL/gallery I/O nhưng không gồm thời gian lấy frame từ iterator. `elapsed_seconds` bắt đầu sau kiểm config/media và tạo output, kết thúc trước ghi session cuối/checksums; không phải tổng thời gian CLI. Peak RSS là peak process, không phải RAM tăng thêm riêng inference. CPU-only, không báo VRAM giả.

Nếu cần thời gian đầu-cuối, ghi wall-clock quanh toàn lệnh CLI, tách khỏi elapsed nội bộ. QA một lượt, không warm-up riêng nên không gọi là benchmark ổn định hoặc SLA. Không tự suy realtime từ FPS nguồn; benchmark lặp/tối ưu cần phạm vi riêng sau evidence lượt đầu.

## 6. Điều kiện kết thúc và bước sau

- Hoàn tất kỹ thuật: pins/rights đúng, session completed, provenance/checksums/index/time nhất quán. Nếu failed, xử lý lỗi trước lượt mới; giữ evidence trong retention cho phép.
- Hoàn tất QA: owner review batch và ngoại lệ, ghi kết luận có scope cho detector/crop cùng hạn chế classifier/coverage. Chưa đặt numerical quality gate; không tự đánh dấu Accepted chỉ từ completed hoặc tests PASS.
- Nếu crop không phù hợp: đề xuất revision mới dựa trên lỗi cụ thể, owner duyệt trước đổi variables. Nếu phù hợp: chuẩn bị benchmark tracking; không tự mở tracking/events/risk/web.
- Media/crops/gallery chỉ local, tối đa 7 ngày hoặc xóa sớm theo yêu cầu; runtime chưa tự xóa. Owner chịu trách nhiệm lịch lưu/xóa, agent chỉ thực thi theo inventory/scope. Metadata liên kết về clip cũng giữ local; chỉ đưa tóm tắt phi định danh được phép vào report. Không commit media.

Phần cần owner chốt trước lượt đầu: exact clip và rights, protocol/cohort review đề xuất ở trên. Detector/license/model/crop đã duyệt không hỏi lại. Chưa có clip thì task preparation vẫn hoàn thành, trạng thái chất lượng video vẫn pending.
