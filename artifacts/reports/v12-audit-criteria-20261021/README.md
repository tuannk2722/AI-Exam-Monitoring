# Tiêu chí audit V12 — nghiên cứu ngày 21/10/2026

**Khuyến nghị: rà toàn bộ 1.296 crop train/val một lần theo rubric thống nhất, sau khi chốt semantics và thử rubric trên một batch nhỏ. Không lọc hàng loạt bằng kích thước, độ nét hoặc việc model hiện tại đoán đúng.** Chưa thực hiện audit/relabel toàn bộ, release, training hay inference. Test vẫn đóng. Branch giữ `research/e006-v12-diagnostics-20261021`.

## 1. Quyết định mới của owner và phạm vi còn Draft

Owner đã ghi trong [README chẩn đoán](../e006-v12-diagnostics-20261021/README.md):

| ID | Quyết định phone / looking |
|---|---|
| G12-A01-F00053-R02 | N/N |
| V7-D-009 | P/N |
| EXP-SCB-021 | N/P |
| V7-C-075 | U/P |

Hai quyết định đầu khác nhãn V12; hai quyết định sau giữ nhãn V12. Đây là quyết định owner theo từng ID, không phải bốn case còn chờ chốt. V12 và metrics cũ chưa bị sửa; các đề xuất khác trong report trước không tự trở thành nhãn mới.

Trong turn này owner chọn mục tiêu looking: **“Quay đầu sang bên/sau; nhìn thẳng phía trước không tính”.** Hướng mục tiêu đã rõ. Rubric chi tiết bên dưới là đề xuất để cụ thể hóa, chưa là contract release mới. Đặc biệt mốc phía trước được đề xuất theo bàn/ghế/hướng ngồi làm bài của anchor, không theo camera. Quy tắc mới khác contract hiện hành “nhìn ngoài vùng bài làm”; cần version/decision và migration trước relabel hàng loạt. Không tự diễn giải quyết định bốn ID thành approval mọi nhãn theo rubric mới.

## 2. Bằng chứng đã kiểm trong repository

- Đọc data contract, `training/data.py::letterbox`, `adaptation_data.py::ImageCohort.model_batch`, config SQRT R4 và coverage diagnostics. Classifier hiện nhận single context RGB, letterbox bilinear 224 × 224; không có input video lân cận, head crop chuyên biệt, head direction/reference riêng hoặc phone bbox riêng ở đường single-crop.
- Đã xem cả chín ví dụ user nêu bằng native ROI → accepted crop → exact letterbox input. `CB-0024` hiện hành trong supervision là **CB-0024-R1**, không tự coi ID cũ là file đang train. Tất cả chín mẫu là train; source/crop SHA được kiểm, ROI derivative được đối chiếu.
- Đã đọc header kích thước của 1.092 train + 204 val, không mở media test. [Size impact](size-impact.json) là phép tính giả định, không sửa membership. [Examples](examples.json) và [input pins](input-pins.json) giữ identity. [Gallery](../../../data/interim/v12-audit-criteria-20261021/index.html) giữ ba mức ảnh; [local artifacts](local-artifacts.json) pin evidence.

### Ví dụ phone cụ thể

| Nhóm owner xác nhận | IDs | Phone state trong V12 | Kết luận cho rubric |
|---|---|---|---|
| Calculator cầm tay | CB-0001, CB-0006, CB-0024-R1 | U, U, U | Có thể dùng nhận biết chuyên môn của owner; không mặc định cứ thiết bị cầm tay là phone. Xác nhận calculator chưa tự chứng minh absence phone ở phần bàn/tay còn lại |
| Phone cầm tay | CB-0008, CB-0017, CB-0020-R1 | U, U, U | Owner đã nêu loại thiết bị; ảnh có vật màu tối với hình dáng khác nhóm trắng. Không tự giả định nhìn thấy màn hình/camera/phím nếu crop không thể hiện. Ghi evidence và mức quan sát của từng ảnh |
| Phone trên bàn | ADD-Y01-F00099-M01-R02, CB-0473, CB-0543-R1 | U, P, P | Bàn có phone gắn đúng anchor vẫn P theo semantics hiện hành. ADD-Y01 còn cần kiểm attribution/chi tiết vật ở rìa bàn trong batch mới; CB-0543 đồng thời có calculator cầm tay và vật owner xác nhận là phone trên giấy |

Quan sát chuyên môn của owner là evidence annotation hợp lệ; không cần model hiện tại đồng ý. Tuy nhiên, agent không có cơ sở xác nhận độc lập mọi vật nhìn từ mặt lưng/cạnh chỉ bằng các crop này. Nếu owner nhận biết từ cảnh/chuỗi frame rõ hơn, ghi nguồn evidence đó và tách nó khỏi mức thông tin hiện có trong input tĩnh. Không broadcast nhãn cho cả video chỉ vì một frame rõ; cùng người có thể đổi hoặc cùng lúc dùng hai thiết bị. Tất cả nhãn mới cần batch review đúng ID/SHA trước release.

## 3. Kích thước crop: đo bằng chứng, không chỉ đo khung ảnh

Không có ngưỡng crop tối thiểu được chứng minh cho hai target và camera của dự án trong các nguồn nghiên cứu đã đọc. Mốc 224 là kích thước tensor của recipe hiện tại, không phải tiêu chuẩn native crop.

Với crop W × H, hệ số resize xấp xỉ **s = 224 / max(W, H)**. Vật có kích thước w × h trong crop còn khoảng s·w × s·h tại input, sai khác tối đa do làm tròn. Ví dụ vật rộng 20 px: trong crop có cạnh dài 800 px thì còn 5,6 px; crop cạnh dài 200 px thì khoảng 22,4 px. Đây là phép tính hình học minh họa, **không phải cutoff 20 px hoặc đảm bảo học được**.

Đề xuất quy tắc crop:

1. Lưu derivative mới từ frame nguồn ở độ phân giải native, giữ provenance; tránh resize trước rồi crop/resize tiếp khi source còn đủ. V12 accepted không được ghi đè. PNG có thể tránh thêm mất mát do nén mới, nhưng không phục hồi thông tin đã mất trong video/JPEG nguồn.
2. Giữ rõ anchor, đầu/vai/thân nhìn thấy, tay và vùng bàn/thiết bị liên quan. Không cắt điện thoại hoặc bàn chỉ để làm mặt to. Khi context chứa người khác, cần đủ dấu hiệu phân biệt anchor; detector người gần nhất không giải quyết attribution.
3. Crop đủ context nhưng không chứa nền thừa quá mức. Không ép mọi crop thành vuông hoặc cùng native width/height; letterbox đã giữ aspect ratio. Padding/crop policy cụ thể cần batch thử và owner chốt, chưa đặt tỷ lệ tự động.
4. Xem lại **đúng input 224** để kiểm cue của từng target. Không yêu cầu toàn ảnh nét đều; cần cue liên quan còn phân biệt được. Mắt không rõ không tự loại looking nếu hướng đầu tương đối vẫn rõ.
5. Nếu context cần cho phone làm đầu quá nhỏ, hoặc crop chặt đầu làm mất phone, đó là trade-off của input chung. Ưu tiên ghi cờ cần recrop/representation; không đổi ground truth hoặc xóa cả ảnh để che giới hạn model. Head/hand ROI hay resolution lớn hơn chỉ là thiết kế cần đối chứng sau, không tự triển khai.
6. Training crop phải có khả năng tái tạo hợp lý từ person detection/context policy ở runtime. Hand-pick một vật bằng biết trước nhãn mà runtime không có cách lấy tương tự có thể tạo lệch phân bố.

Nghiên cứu [FixRes](https://proceedings.neurips.cc/paper_files/paper/2019/hash/d03a857a23b5285736c4d55e0bb067c8-Abstract.html) cho thấy quy mô vật thể và khác biệt preprocessing train/test ảnh hưởng classification. Đây là lý do kiểm scale/pipeline; paper không cung cấp ngưỡng crop phòng thi hoặc chứng minh tăng resolution luôn tốt hơn.

### Nếu lọc bằng kích thước file thì mất bao nhiêu?

Giả định yêu cầu **cả width và height của file crop ≥ ngưỡng**:

| Ngưỡng minh họa, không khuyến nghị | Train còn / 1.092 | Looking P train còn / 339 | Val còn / 204 | Phone P val còn / 35 |
|---|---:|---:|---:|---:|
| 128 px | 877 | 247 | 156 | 34 |
| 224 px | 612 | 147 | 91 | 17 |
| 320 px | 210 | 52 | 54 | 11 |

224 sẽ bỏ 480 train (44,0%) và 113 val (55,4%), mất 192/339 looking P train (56,6%); phone P val còn 17, dưới mức support 30 đang dùng. 168 crop train đang lưu đúng 224 × 224 là derivative; kích thước file không nói lên lượng chi tiết native. Đây là bằng chứng trực tiếp chống đặt hard cutoff tùy ý, không phải lý do giữ mọi crop bất kể evidence.

## 4. Độ nét: tách nhãn thật, bằng chứng trong ảnh và eligibility

Đề xuất sidecar audit theo từng target; chưa thêm field vào canonical schema:

| Mức quan sát | Tiêu chí | Hành động đề xuất |
|---|---|---|
| Rõ | Có đặc trưng trực tiếp đủ phân biệt target, attribution rõ; input còn giữ cue | Giữ P/N theo semantics, không cần ảnh đẹp toàn cảnh |
| Khó nhưng có evidence | Nhỏ/mờ/che một phần, vẫn có cơ sở phân biệt và đúng anchor | Giữ mẫu khó; đánh dấu slice chất lượng để đo riêng |
| Mất cue sau preprocessing | Source/native có evidence, nhưng input hiện tại không còn đủ | Ưu tiên recrop từ source hoặc proposal đổi input; không lấy class prediction làm nhãn, không tự đổi P thành N |
| Không đủ evidence | Không phân biệt được ngay cả sau xem nguồn hợp lệ, hoặc không rõ anchor | U cho target trong revision sau owner review; target khác có thể vẫn known |
| Lỗi kỹ thuật/geometry | Decode hỏng, sai anchor, crop mất vùng quan trọng | Sửa derivative/review mới hoặc ngoài supervision; raw giữ nguyên |

Không suy từ “người chưa phân biệt được” rằng model chắc chắn không học được; đây là proxy QA, không là định lý về khả năng model. Ngược lại, sự tự tin của người từng biết cảnh không chứng minh ảnh tĩnh có đủ signal để model tổng quát hóa.

Nếu biết loại vật từ evidence ngoài crop nhưng cue trong input mất hoàn toàn, cần giữ riêng fact nguồn và đánh giá observability. Schema hiện tại buộc mask theo P/N/U, **không hỗ trợ một cờ eligibility độc lập cho mỗi target known**. Vì vậy chưa tự đặt known P + mask 0, chưa thêm schema hoặc tự drop record. Batch mới phải chốt cách xử lý theo contract: recrop, review U theo evidence ảnh của target, hoặc review-only khi không đủ supervision.

Không dùng một ngưỡng variance-of-Laplacian toàn ảnh để quyết định tốt/xấu: nền chữ/sách có nhiều cạnh không chứng minh mặt/phone đủ rõ. Có thể dùng đo tự động để xếp hàng review sau khi hiệu chỉnh theo ROI, camera/scale, nhưng chưa có threshold approved. Nghiên cứu [Dodge & Karam](https://arxiv.org/abs/1604.04004) đo tác động blur/noise và các dạng méo ảnh lên classification; không đưa cutoff chung cho phone/head trong dataset này.

## 5. Looking theo mục tiêu owner vừa chọn

**Đề xuất diễn giải: trạng thái đầu quay rõ sang bên hoặc ra sau so với hướng ngồi làm bài của chính anchor.** Không gọi nó là xác định eye gaze, đích nhìn, nhìn bài người khác hay bằng chứng gian lận. Ảnh tĩnh chỉ cho thấy trạng thái hướng đầu, không chứng minh động tác chuyển hướng hoặc thời lượng.

| Tình huống | Nhãn đề xuất theo mục tiêu mới |
|---|---|
| Đầu quay rõ trái/phải/sau so với hướng bàn/ghế; đủ anchor/reference | P, dù không thấy own-paper hoặc chi tiết mắt |
| Nhìn thẳng phía trước, kể cả ngẩng khỏi bài | N nếu đủ quan sát hướng đầu/reference |
| Cúi đầu đọc/viết theo hướng ngồi, không quay ngang/sau | N nếu đủ quan sát; cúi không đồng nghĩa luôn N khi thực tế vẫn quay ngang |
| Chỉ nghiêng đầu sang vai (roll), không quay ngang/sau | Không tự P; N nếu quan sát đủ, U nếu không rõ |
| Chỉ liếc mắt trong khi đầu vẫn phía trước | N cho target head-turn đã chọn, không tuyên bố không có eye-gaze lệch |
| Nhìn nghiêng trong ảnh vì camera quay chéo, nhưng đầu vẫn theo hướng bàn/ghế | N; góc so với camera không phải góc quay của hành vi |
| Mặt khuất, không xác định được hướng đầu hoặc hướng phía trước của người đó | U; back view không tự N hoặc P |
| Đầu có quay nhưng không phân biệt được lệch nhẹ thông thường với quay sang bên | U/ca biên chờ bộ ví dụ chuẩn; chưa áp angle cutoff tự bịa |

Không bắt buộc thấy **tờ bài riêng**, nhưng cần đủ mốc xác định hướng của người đó: bàn/ghế, vai/thân và bố trí chỗ ngồi. Vai/thân chỉ là cue; nếu cả thân xoay cùng đầu thì không thể dùng thân hiện tại làm baseline duy nhất. Khi không có mốc, chỉ biết “mặt đang nghiêng đối với camera”, chưa biết head-turn tương đối. Không cần seat map trong implementation hiện tại; đây là yêu cầu evidence/crop, còn cách runtime giữ baseline cần thiết kế riêng.

Hướng mắt có thể hỗ trợ khi nhìn được, nhưng không nên là điều kiện bắt buộc cho mục tiêu này. Nếu muốn phát hiện người liếc mắt mà đầu không quay thì phải mở rộng target, quality requirements và model/evaluation tương ứng. [GazeFollow](https://people.csail.mit.edu/khosla/papers/nips2015_recasens.pdf) kết hợp hướng đầu với scene để dự đoán đích nhìn; [Gaze360](https://arxiv.org/abs/1910.10088) còn mô hình hóa uncertainty và thông tin thời gian. Các nghiên cứu này giúp phân biệt head orientation với gaze target, không chứng minh classifier hiện tại có các năng lực đó.

Với lựa chọn mới, không tiếp tục rule “nhìn phía trước ngoài trang giấy là P” của hướng cũ. Cần rà cả positives lẫn negatives/unknowns, giữ originals và semantics version. Metrics E006 chỉ mô tả task cũ; không so trực tiếp như cùng ground truth sau migration. Bốn quyết định owner giữ lại vẫn là evidence đúng scope, không tự coi chúng đã cover mọi ca biên của taxonomy mới.

## 6. Phone: dùng chuyên môn, nhưng chuyển thành evidence nhất quán

**Có thể và nên dùng kinh nghiệm thực tế của owner khi annotation.** Không bắt buộc thấy chữ trên màn hình, camera lens hay toàn bộ bàn phím trong mọi ảnh. Hình dáng, kết cấu thân máy, cách bố trí phím/màn hình và góc nhìn quen thuộc có thể hỗ trợ; cần chỉ ra cue và mức chắc chắn thay vì “vật đen là phone, vật trắng là calculator”. Màu sắc, nhìn xuống, cầm tay hay ngồi phòng thi không đủ một mình.

Quy tắc đề xuất giữ theo contract phone hiện hành:

- **P:** có ít nhất một mobile nhận diện đủ chắc, gắn đúng anchor, được cầm/tương tác hoặc đặt trên vùng bàn/sách thuộc anchor. Không yêu cầu đang dùng. Tên kỹ thuật `phone_use` rộng hơn cách hiểu thường ngày “đang thao tác”; mô tả hiển thị nên rõ phạm vi quan sát.
- **N:** vùng quan sát cần thiết đủ, xác nhận không có mobile gắn anchor. Thấy calculator trong tay chỉ loại phone ở vật đó; vẫn kiểm bàn và tay còn lại. CB-0543-R1 minh họa trường hợp calculator và phone có thể cùng tồn tại.
- **U:** thiết bị chưa phân loại chắc, một phần vật còn lộ mơ hồ, thiếu tay/vùng cần quan sát hoặc chưa rõ thuộc người nào; giữ ngoại lệ absence có scope đã duyệt, không tự nới/thu hẹp bằng quy tắc mới.

Thấy phone trên bàn **chưa đủ nếu không biết của anchor nào**. Own-paper không bắt buộc là vật thể được annotate riêng, nhưng quan hệ vùng bàn–người vẫn cần evidence. Bằng chứng sequence có thể giúp xác định loại/attribution cho reviewer, song phải ghi provenance và không suy every frame chứa đủ cue. Không gán cùng nhãn cho cả nhóm CB chỉ từ màu thiết bị hay cùng một người.

## 7. Có audit toàn bộ không và làm sao tránh mất dữ liệu vô ích?

Lần này **có lý do rà toàn bộ train/val** vì semantics looking thay đổi, không chỉ vì E006 chưa đạt. Phạm vi đầu: 1.296 supervision crops non-test. Review-only 332 chỉ xem lại khi có cơ hội giải quyết blocker/observability dưới rubric mới; không phục hồi hàng loạt 418 excluded/replaced records hoặc các crop parent đã bị supersede. Không mở 11 reserved test để chọn rubric/threshold/ảnh đẹp.

Đề xuất thứ tự:

1. Chốt target definition và bộ ca biên, nhất là head-turn với camera chéo và phone mặt lưng/đặt bàn. Trial trên batch phân tầng nhỏ để phát hiện mâu thuẫn trước khi rà toàn bộ; số lượng batch sẽ chốt ở task audit, chưa đặt quota mới tại đây.
2. Chuẩn bị tự động gallery source/native/crop/input, draft P/N/U và flags; owner review theo batch/ngoại lệ. Khi review nhãn ẩn scores và nhãn đề xuất ở lượt đầu. Không bắt owner annotate từng ảnh từ đầu.
3. Ghi nhãn và quality/attribution riêng theo target. Rà cả TP/TN/U và lỗi; không chọn lọc theo model. Nhóm cùng source/scene thuận tiện cho review nhưng không thay group/split accepted.
4. Trước drop, ưu tiên: giữ mẫu khó hợp lệ → sửa crop từ nguồn nếu có → chỉ U target thiếu evidence → review-only/U-U nếu cả hai không đủ. Không xóa raw, không ép U thành N, không giảm dataset chỉ để có hình đẹp.
5. Xuất delta **trước khi release**: P/N/U và groups theo target/source, bao nhiêu giữ/recrop/relabel/withdraw, nhóm/camera khó bị mất, support val và co-occurrence. Nếu thiếu support không thể khẳng định nghiệm thu; giữ cảnh báo và bù đúng nguồn/nhóm, không hạ gate hoặc chuyển val sang train.
6. Owner chốt delta/crop policy/semantics version và release mới; sau đó baseline mới trên task mới. Tạm đặt proposal random-erasing sau bước này, không chạy trên taxonomy đang chuyển đổi. Không sửa hoặc ghi đè E006/V12 để tạo so sánh giả cùng ground truth.

“Lần audit cuối” nên có nghĩa là **đóng một version dataset với rubric và coverage có thể truy vết**, không phải đảm bảo mọi dữ liệu/camera tương lai đều đã giải quyết. Điều kiện kết thúc hợp lý: mọi record trong scope có disposition rõ, ca biên đã được xử lý hoặc giữ U/review-only có lý do, delta/support/groups được kiểm, owner chốt release. Không cần ép unknown về 0.

## 8. Ít ảnh hơn có làm thực tế kém đi?

Có thể. Loại nhãn sai có thể giúp học; loại nhiều mẫu khó nhưng đúng có thể làm thiếu miền thực tế. Chưa có thực nghiệm để dự đoán dấu hoặc mức thay đổi độ chính xác của dự án. Ảnh cùng scene gần giống không tương đương nhiều nhóm mới. Chỉ giữ dữ liệu rõ/đẹp có nguy cơ tạo train–deployment shift; [WILDS](https://proceedings.mlr.press/v139/koh21a.html) cho thấy chênh phân bố thực tế có thể làm hiệu năng giảm rõ rệt. Không suy rằng mọi cleanup đều gây giảm từ paper này.

Đánh giá mới cần giữ các slice chất lượng/góc máy thực tế và báo coverage. Nếu runtime có nhánh “không đủ bằng chứng”, đo cả accuracy/precision trên phần kết luận được **và tỷ lệ không kết luận**; không được loại hết ca khó rồi chỉ công bố metric đẹp. [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html) minh họa trade-off risk–coverage; đây là nguyên tắc đánh giá tham khảo, không là đề xuất cài model đó.

**Code hiện tại mask U khỏi loss/metrics nhưng model vẫn xuất hai scores; U trong annotation không tự tạo output abstain ở runtime.** Không giả định đã có nhánh từ chối hoặc quality gate production. Muốn thêm phải chốt contract/calibration riêng. Nếu camera không giữ đủ cue ở khoảng cách thực tế, cần cải thiện nguồn video, crop/representation hoặc giới hạn use scope; không có tiêu chí audit nào bảo đảm bù lại thông tin không tồn tại.

## 9. Bàn giao và giới hạn

- Đây là nghiên cứu, 9 ví dụ được xem mới và phép đếm kích thước; chưa đánh giá lại 1.296 nhãn theo rubric mới, chưa biết chính xác sẽ giữ được bao nhiêu mẫu.
- Không chọn min face/device pixels, blur score hay head yaw threshold vì chưa có đo/đối chứng thích hợp cho dữ liệu này. Các số 128/224/320 chỉ minh họa hậu quả lọc, không là recommendation.
- Nguồn nghiên cứu là papers/project của tác giả; kết quả khác dataset không là guarantee cho ResNet18/V12. Các quy tắc cụ thể cho dự án được ghi là đề xuất/suy luận, tách khỏi kết quả published.
- Evidence local được giữ; không thay source, accepted data/config/pins hoặc nội dung owner vừa sửa. Spec chưa đổi trong lượt này. Checks: role/SHA 9 ví dụ, native ROI provenance, tổng đếm train/val và links/diff; không cần chạy ML tests vì không sửa source.
