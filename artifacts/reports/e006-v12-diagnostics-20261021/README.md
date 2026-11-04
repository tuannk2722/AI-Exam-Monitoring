# Chẩn đoán E006 trên V12 — 21/10/2026

**Phân tích cached predictions hoàn tất; visual review là Draft chờ owner chốt bốn ngoại lệ. Ưu tiên làm rõ nhãn và coverage trước khi thêm detector.** Không train, inference hoặc mở media test; không thay nhãn, crop, split, thresholds hay artifacts E006/V12. Branch: `research/e006-v12-diagnostics-20261021`.

## 1. Phạm vi và bằng chứng

- Inputs: package `pilot-b-20261020-v12`; SQRT và RATIO R4, mỗi recipe ba seed 20261020/20261021/20261022. Config chẩn đoán: [JSON](../../../configs/diagnostics/e006-v12-20261021.json).
- Kiểm checksum inventory/manifest, checksum file của từng run và SHA của config/run/metrics/predictions train/selection; đối chiếu exact membership, labels, masks, source và group. Không kiểm lại checkpoint vì không load model. [Input pins](input-pins.json).
- 7.776 prediction rows = 6 × (1.092 train + 204 val); 48 confusion comparisons khớp số đã lưu, gồm hai split × hai target × hai threshold modes × sáu run. [Parity](confusion-parity.json).
- `fixed`: threshold 0,50. `calibrated`: threshold validation đã lưu riêng từng run, **không fit lại**. Bảng consensus train cũng áp threshold validation này; parity train đối chiếu riêng thresholds train đã lưu, không lẫn hai mục đích. U không tạo TP/FP/FN/TN.
- Shortlist deterministic: ưu tiên lỗi ổn định 3/3 seed SQRT, tối đa bốn mẫu mỗi target/FP/FN; ưu tiên khác source/group rồi margin. Có thêm TP/TN/U. Train controls dùng cùng quy tắc; U được chọn theo margin score, không phải random sample.
- Đã xem 37 crop: 25 val và 12 train; 33 crop khớp native ROI pixel, bốn crop derivative khớp provenance nguồn/ROI/output. Đã xem source có anchor/context box, crop và input 224 của cả 37. Mười hai train controls có preview epoch 5; xem thêm 11 epoch của bốn mẫu CB-0428, E004-CF-C021-R03, G23-B01-F00003, EXP-CM-003. Không tuyên bố visual audit toàn bộ V12 hoặc toàn bộ lỗi.

## 2. Lỗi lặp lại, không chỉ nhiễu seed

Đơn vị bên dưới là **sample–target**, nhãn V12 hiện hành; ba seed không là ba validation độc lập.

| Recipe / ngưỡng | Phone FP 3/3 | Phone FN 3/3 | Looking FP 3/3 | Looking FN 3/3 |
|---|---:|---:|---:|---:|
| SQRT / 0,50 | 5 | 13 | 29 | 12 |
| SQRT / hiệu chỉnh | 15 | 3 | 18 | 15 |
| RATIO / 0,50 | 14 | 5 | 50 | 5 |
| RATIO / hiệu chỉnh | 13 | 4 | 20 | 15 |

SQRT hiệu chỉnh có 51 lỗi ổn định trên 48 crop; phone có 27 ca sai ít nhất một seed và 23 ca sai ít nhất hai seed, looking tương ứng 56 và 41. Hai recipe cùng sai ổn định trên **16 phone sample–target và 31 looking sample–target**. Đổi weighting chưa loại được phần lớn lỗi chung; không suy nguyên nhân nhãn từ sự đồng thuận của model.

Danh sách lỗi ≥ 2/3 seed theo cả hai ngưỡng ở [recurrent-errors.json](recurrent-errors.json); toàn bộ scores/outcomes kể cả controls/U ở [consensus local](../../../data/interim/e006-v12-diagnostics-20261021/consensus.json). [Summary](summary.json) giữ đếm đầy đủ, `mixed` gồm các mẫu đổi outcome giữa seed.

## 3. Coverage sau audit V12

| Split / target | P (groups) | N (groups) | U (groups) |
|---|---:|---:|---:|
| Train phone | 187 (42) | 456 (106) | 449 (95) |
| Val phone | 35 (25) | 94 (48) | 75 (54) |
| Train looking | 339 (87) | 744 (147) | 9 (7) |
| Val looking | 65 (40) | 139 (80) | 0 (0) |

Group counts giữa P/N/U có thể chồng lấp, không cộng thành số nhóm độc lập. Đây là leakage groups đã review, trong đó có nhóm gom bảo thủ; không gọi chúng là số session/camera xác minh độc lập. [Coverage đầy đủ](coverage.json) có source × target × state × số records/groups và co-occurrence.

Những thiếu hụt cần xử lý theo thứ tự:

1. **Ranh giới nhãn còn cần kiểm ở một số ca**, không phải toàn bộ dữ liệu sai. Bốn ngoại lệ trong §4 được phát hiện cả ở lỗi lẫn controls/U. Đặc biệt mẫu được model dự đoán đúng theo nhãn hiện hành vẫn có thể cần review loại thiết bị.
2. **Phone P tập trung nguồn/nhóm:** 78/187 P train (41,7%) thuộc `E004-crop-bundle-20261014`, toàn nguồn này chỉ có một leakage group bảo thủ. 90 crop YouTube mới chỉ đóng góp 14 P phone, thuộc một group; không phải 90 phone positives độc lập.
3. **Thiếu P cùng miền:** train `owner-frames-part01`, `part02`, `part05` lần lượt phone P/N/U = 0/27/11, 0/22/6, 0/35/21. Val cùng source có P, nhưng thuộc groups khác. Nếu bổ sung phải tìm scene/session mới có quyền và group review; không chuyển val sang train, không nhân thêm frame gần nhau để tăng quota.
4. **Thiếu N để đo riêng nguồn:** val `classroom_attitude` có phone 14 P/0 N/18 U. Nguồn có support ít không đủ kết luận riêng, dù metric nhìn tốt. Không tự cân lại validation sau thấy lỗi.
5. **Looking cần phân biệt vùng làm việc:** viết/đọc, đứng đọc sách, quay đầu khỏi bài và thiếu context đang cùng xuất hiện trong lỗi. SQRT có 6 looking FP ổn định ở `classroom_attitude`, 8 FN ổn định ở owner part01/02. Đây là ưu tiên chọn thêm cặp đối chứng cùng bối cảnh, không kết luận mọi mẫu thuộc nguồn đó sai.
6. **U không chỉ là ảnh xấu:** phone U chiếm 41,1% train và 36,8% val. Trong shortlist có vật nhìn cạnh, attribution/context yếu và một ca đề xuất đổi U → P. Chưa visual review đủ 524 phone U để định lượng tỷ lệ từng nguyên nhân; không ép U thành N. Looking val không có U, không dùng điều này chứng minh mọi nhãn looking đều rõ.

## 4. Kết quả visual review và bộ ví dụ nhãn

[Gallery local không hiển thị nhãn/scores](../../../data/interim/e006-v12-diagnostics-20261021/index.html) → [nhận xét từng mẫu](VISUAL-REVIEW.md) → [bộ ví dụ và phiếu ngoại lệ](LABEL-REVIEW.md). Exact crop/source/card SHA và observations ở [visual-findings.json](visual-findings.json). Owner có thể tự review batch; không cần người thứ hai.

| ID | Điểm cần owner chốt | Đề xuất Draft | Quyết định của owner |
|---|--
| `G12-A01-F00053-R02` | V12 phone P, vật trông như calculator với phím vật lý | P → N nếu xác nhận calculator và vùng quan sát đủ absence mobile | N/N |
| `V7-D-009` | V12 phone U, điện thoại cầm trong tay rõ | U → P; giữ looking N | P/N |
| `EXP-SCB-021` | V12 looking P, đầu cúi nghiêng gần sách/bút, đích nhìn chưa rõ | Chốt P có evidence hay cần U/N; đề xuất U nếu không rõ | N/P |
| `V7-C-075` | V12 looking P, quay đầu nhưng mắt gần khép, thiếu vùng bài/đích nhìn | P → U nếu không có evidence bổ sung | U/P |

Các nhãn này vẫn giữ nguyên trong package và mọi phép đếm trên. Không tính “metrics cải thiện sau sửa nhãn” hoặc tự loại mẫu để tăng score. Nếu owner giữ nhãn thì lưu lý do; nếu đổi thì tạo revision/release mới đúng quy trình, không sửa bytes V12.

Một số quan sát có tác dụng phân biệt giả thuyết:

- `E004-EX-C008` cầm phone rõ và `G06-A02-F00012` có phone trên bàn vẫn là FN ổn định. Không thể giải thích tất cả FN bằng mất chi tiết ở 224.
- `G05-B02-F00015-R02` chỉ 77 × 85, nhưng `G27-B02-F00016` 85 × 116 vẫn là looking TP ổn định. Kích thước nhỏ là cờ QA, chưa là ngưỡng xóa ảnh.
- `E004-CN-048` đứng đọc sách là looking FP ổn định; `V7-A-008` dùng laptop là phone FP ổn định. Cần hard negatives và kiểm shortcut tư thế/context, chưa có bằng chứng nhân quả model dùng đặc trưng nào.
- Trong augmentation tái tạo, `EXP-CM-003` epoch 6 bị erasing che vùng miệng/má; `G23-B01-F00003` epoch 9 mất một phần vùng đầu. Cùng sample index/seed/epoch/config của SQRT seed 20261020; chỉ transform, không forward. Bằng chứng cho thấy augmentation có thể làm yếu cue, **không chứng minh nó gây metrics thấp**. Hai mẫu phone P xem 11 epoch chưa thấy mất hết phone vì erasing.

Ảnh chuỗi epoch đã xem: [EXP-CM-003](../../../data/interim/e006-v12-diagnostics-20261021/augmentation-033.png), [G23-B01-F00003](../../../data/interim/e006-v12-diagnostics-20261021/augmentation-029.png), [CB-0428](../../../data/interim/e006-v12-diagnostics-20261021/augmentation-026.png), [E004-CF-C021-R03](../../../data/interim/e006-v12-diagnostics-20261021/augmentation-027.png).

## 5. Hướng xử lý và một thực nghiệm đề xuất

1. Owner review bộ ví dụ và bốn ngoại lệ. Rubric giữ semantics hiện hành: phone trên bàn thuộc anchor vẫn P; ảnh tĩnh không suy gian lận/duration. Không biến sự đồng ý với hướng nghiên cứu thành approval nhãn mới.
2. Nếu xác nhận sửa dữ liệu: lập delta đúng ID/SHA, kiểm nhóm/cohort và đóng package mới sau approval. Ưu tiên giải quyết các ambiguity tương tự bằng shortlist, chưa có bằng chứng cần lọc lại toàn bộ. Ảnh khó có evidence vẫn giữ. Không recrop tự động hoặc xóa raw.
3. Bù coverage có mục tiêu: phone P trên bàn/áp tai cùng miền với nhóm train hiện thiếu P; phone N với calculator/laptop/bút; looking P/N cùng context bài làm; đa dạng nhóm thật. Trước thu nhận phải chốt nguồn/quyền và group, không đặt quota tùy ý trong report này.
4. **Thực nghiệm duy nhất đề xuất sau chốt dataset: SQRT matched control random erasing 0,15 so với 0,00**, các biến khác giữ nguyên. [Proposal Draft](../../../configs/experiments/E006-followup-20261021/README.md) có thiết kế hai arm, điều kiện dataset/compute và quyết định; chưa executable hoặc run approval. Đây là kiểm giả thuyết augmentation cụ thể; không kỳ vọng tự giải quyết coverage/nhãn.
5. Chỉ ưu tiên phone detector nếu sau review còn cụm lỗi xác định/phân biệt phone rõ và đủ nguồn/bbox/attribution để làm pilot. Detector không giải quyết looking và không phục hồi thông tin không có trong ảnh. Person detector của kiến trúc B là phạm vi khác. Chưa chọn model/pretrained/license hoặc mở downstream.

## 6. Giới hạn và bàn giao

- Shortlist có chủ đích, chưa là ước lượng tỷ lệ lỗi nhãn hoặc quality toàn dataset. Cùng validation đã exposure/selection/calibration; không là holdout độc lập. Không so AP E005/V11 và E006/V12 như cùng ground truth.
- Không thay support/gates 80/80/20, không hạ acceptance để hợp thức hóa candidate. Không mở 11 test; metadata manifest được đọc để lọc role nhưng media/test scores không được truy cập.
- Source/config/test mới làm code identity hiện tại khác historical run; không dùng evaluator hiện tại để reload E006 hoặc sửa code pin cũ. Diagnostic chỉ đọc cached artifacts.
- Local gallery/consensus/augmentation là evidence cần giữ cùng [local-artifacts.json](local-artifacts.json), không đưa media vào Git. Source và V12 hiện hành giữ nguyên. Checks cuối và giới hạn Git index ở [handoff-checks.json](handoff-checks.json).
- CLI tái dùng: `python -m ai_exam_monitoring.training.diagnostics --config <diagnostic-config.json> --workspace .`; cần output mới. Không chạy lại đè lên hồ sơ này. Config chẩn đoán không là config train.
