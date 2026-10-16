# E004 — tinh gọn crop, sửa nhãn Draft và mở rộng anchor

Bản ngày 15/10/2026 thay **đề xuất shortlist** của study ngày 14/10, sau review mới của owner. Kết quả: **247 crop / 84 anchor trong 5 parent video**, gồm 151 ứng viên từ 765 crop gốc, 92 crop mới và 4 crop bổ sung cũ. Có 645 alternatives và 13 withheld, tất cả vẫn được giữ local. **Đây là batch Draft để nghiệm thu, chưa là dataset Accepted hoặc bằng chứng model tốt hơn.** Raw, V9, nhãn/splits accepted và recipe RC1 không đổi.

Mở [gallery mới](../../../outputs/E004-crop-bundle-refinement-20261015/index.html), mặc định chỉ hiện shortlist. Có thể lọc crop mới, nhãn thay đổi, alternatives, withheld và tìm theo ID/anchor. [Bảng owner review](owner-review.md) có sẵn 247 ID; có thể chốt batch và ghi ngoại lệ, không cần gán lại từng ảnh. Review cũ được giữ nguyên trong [snapshot](owner-review-original.md); không sửa README mà owner đã viết.

## Phạm vi đã kiểm

- Xem lại từng ứng viên hiệu lực của **765 ID** qua 54 bảng theo 32 anchor, gồm 573 crop gốc và 192 recrop đã có. Đây không phải xem lại riêng 192 crop lỗi đã được thay thế; bản gốc vẫn nằm trong audit trước.
- Xem đủ **212 frame** qua 53 bảng tổng quan, mỗi frame hiển thị 960 × 540; mở chi tiết source cho 25 trường hợp nhãn/che khuất trọng điểm. Không tuyên bố mọi pixel của 212 frame đều được xem ở độ phân giải gốc.
- Theo dõi thay đổi tư thế, hướng đầu và camera trong cả 5 chuỗi; tạo 135 crop native cho 52 anchor đề xuất, sửa box theo frame khi camera dịch, xem crop và **toàn bộ 135 input 224**. Chọn 92; 34 alternatives và 9 withheld trong phần mới. Xem lại 5 crop bổ sung cũ, giữ 4; nối olive và áo xanh nhạt vào đúng anchor mới để không đếm trùng.
- Sáu ảnh có nét đánh dấu của owner chỉ làm tài liệu chỉ dẫn, đã pin ở [reference-pins](reference-pins.json); không dùng các ảnh có nét đỏ làm dữ liệu train.

[Ledger 905 ứng viên](candidate-ledger.json) giữ SHA nguồn/crop/input, nhãn Draft cũ/mới, lý do, disposition và ứng viên đại diện cùng anchor. [Coverage frame](frame-coverage.json) dẫn tới toàn bộ 212 frame; [observations crop mới](new-observations.json), [quyết định 32 nhóm cũ](visual-decisions.json) và [summary](summary.json) là evidence cụ thể. Quan sát và nhãn vẫn có thể cần owner sửa; không gọi kiểm ảnh là ground truth tự động.

## 1. Vì sao cần giảm crop lặp

Phản ánh của owner đúng: bộ lọc dHash trước chỉ tìm ảnh rất gần nhau và đã giữ quá nhiều frame của cùng người. Hai anchor có tới **87 crop/người**; thêm góc tay rất nhỏ không tạo thêm 87 người hoặc 87 bối cảnh độc lập. Bản trước cũng bổ sung người quá ít; không có evidence cho phép kết luận tất cả người chưa crop đều bị loại bởi tiêu chí chất lượng.

Lần này chọn theo **người + tình huống quan sát**, sau khi xem cả chuỗi: viết/đọc, cầm hoặc đặt thiết bị, phone cùng calculator, hướng ra ngoài bài rõ, mức che khuất khác, thay đổi góc camera có ích. Không áp quota cứng mỗi người và không xóa ảnh raw. Nhóm 87 ảnh CB-0282–0368 còn 8; CB-0398–0484 còn 7. Các nhóm owner nêu CB-0001–0025 / 0026–0062 / 0063–0087 / 0088–0112 còn 6 / 7 / 5 / 5. Tối đa shortlist hiện là 8 crop/anchor. [Bảng trước/sau từng anchor](track-summary.json).

Ảnh lặp có thể giúp mô hình gặp biến thiên thật về che khuất/góc nhìn, nhưng lặp cùng evidence chủ yếu làm người/phòng đó xuất hiện nhiều hơn trong loss nếu sampling đều từng ảnh. Tăng số ảnh như vậy không bảo đảm tổng quát hóa tốt hơn. Nghiên cứu về [shortcut learning](https://arxiv.org/abs/2004.07780) mô tả việc mô hình dựa vào dấu hiệu dễ học nhưng kém chuyển miền; đây là rủi ro phù hợp để kiểm, chưa phải chẩn đoán đã chứng minh cho RC1. Nghiên cứu [near-duplicates trong CIFAR](https://arxiv.org/abs/1902.00423) chỉ ra bias khi trùng qua train/test; không dùng kết quả đó để khẳng định mọi ảnh lặp trong train đều có hại.

Muốn chứng minh lợi ích của shortlist, sau nghiệm thu cần một so sánh được duyệt: cùng initialization/recipe, cohort development cố định và ranh giới family, so bộ tinh gọn với bộ nhiều frame; báo cả tổng compute/steps vì số ảnh khác làm số bước mỗi epoch khác. Task này chưa train hoặc chọn threshold. Không chia random frame để tạo val/test mới.

## 2. Phone, calculator và P/N/U

Giữ [contract hiện tại](../../../docs/data.md): `phone_use` bao gồm mobile đang cầm/tương tác **hoặc nằm trên bàn/sách riêng có attribution rõ**. Tên target không có nghĩa chỉ tính lúc đang sử dụng. Nhìn calculator/phone trong vùng bài riêng không tự làm `looking_around=P`.

| Evidence trong đúng crop | Phone Draft | Cách xử lý |
|---|---|---|
| Mobile nhận diện được, nằm trong tay hoặc vùng bàn riêng của anchor | P | Không cần đồng thời thấy toàn bộ hai tay; phải phân biệt mobile với vật khác và đúng người |
| Calculator rõ; tay và vùng bàn liên quan đủ quan sát, không có mobile | N | N là absence mobile, không phải “có calculator” |
| Calculator rõ nhưng tay/vùng bàn khác bị che | U | Không đủ evidence cho absence; calculator và phone có thể cùng xuất hiện |
| Tay che một phần vật, vẫn còn cấu trúc nút bấm/màn hình đủ phân biệt calculator | Có thể N | Chỉ khi đồng thời đủ quan sát vùng còn lại; không dùng tỷ lệ che cố định |
| Chỉ mặt lưng, miếng đen/hồng/trắng, cạnh mỏng, vật nhỏ hoặc attribution không rõ | U | Màu sắc, hình chữ nhật hoặc thao tác bấm không đủ xác nhận phone |
| Chỉ frame trước/sau cho biết loại vật | U tại crop thiếu evidence | Frame khác giúp theo dõi anchor và chọn cảnh tốt hơn, không thay evidence của crop |

Ví dụ đã sửa: CB-0009/0012 → U/N; 0014/0016 → P/N nhất quán với vật nhìn được; 0017 → P/P; 0024-R1/0025-R1 → U/N. CB-0043/0044/0045/0052 giữ U/N vì phần nhận dạng còn quá ít; 0046/0048/0049/0050/0051/0054/0056 có nút calculator đủ rõ và vùng liên quan đủ quan sát nên N/N. CB-0057/0059/0060/0062 → U/N, không kế thừa calculator từ frame trước. Không gọi vật hồng ở 0098/0102–0105 là mobile: U/N.

**Model hiện tại không xuất ra lớp calculator.** Code [AdaptationModel](../../../src/ai_exam_monitoring/training/adaptation_model.py) là ResNet18 với `Linear(512, 2)` cho hai target. Nó có thể học các dấu hiệu phân biệt qua negative calculator tốt và positive có phone, nhưng chưa có bằng chứng rằng đã phân biệt đúng hai loại vật. P/N/U là trạng thái annotation: known target dùng loss/metric, U bị mask; U không phải lớp thứ ba được head hiện tại học. Điểm sigmoid thấp cũng không tự chứng minh “đã nhìn thấy và xác nhận không có phone”.

## 3. Looking cần nhìn gì

Ưu tiên **hướng đầu/nhìn kết hợp vị trí vùng bài riêng**. Mắt là evidence bổ sung khi thấy rõ; không bắt buộc luôn nhìn được con ngươi. Thân người/tư thế viết/tay cầm bút chỉ là context, không đủ làm quy tắc gán nhãn một mình.

| Quan sát | Looking Draft |
|---|---|
| Đầu/nhìn quay rõ sang người khác hoặc ra ngoài vùng bài, context xác định được | P |
| Hướng đầu còn xác định được vào giấy/thiết bị trong vùng riêng, không có evidence nhìn ngoài | N |
| Chỉ nghiêng đầu, cúi người, mắt không rõ và hướng/vùng bài cũng không rõ | U |
| Tay che một phần mặt nhưng hướng đầu vào trang riêng vẫn rõ | Có thể N |
| Mất đầu, người khác che hướng đầu, back view không đủ diễn giải | U |

Không có quy tắc “che mắt là U”, “tay ôm đầu là P”, “đang viết luôn là N” hoặc tỷ lệ che 50%/80%. CB-0055-R1 → N/N; nhóm CB-0063–0087 → P/N sau đối chiếu hướng bài, gồm các ID owner chỉ ra. CB-0097 → U/N và được đưa lại vào shortlist; không còn withheld chỉ vì phone U. CB-0111-R1 bị loại khỏi shortlist do che anchor quá nhiều. Ảnh tĩnh không xác nhận nhìn lâu bao nhiêu, ý định hay gian lận.

## 4. 224 là input, không phải khuôn cắt nguồn

[Loader](../../../src/ai_exam_monitoring/training/data.py) chuyển crop sang RGB và letterbox bilinear vào 224 × 224 với fill `[124,116,104]` theo recipe hiện hành. Crop native có thể là hình chữ nhật ở độ phân giải nguồn; 135 crop mới giữ native PNG rồi mới tạo preview 224. Không kéo méo người hoặc ép context thành ô vuông để thỏa input.

Batch thường cần tensor cùng kích thước và 224 là lựa chọn hiện tại để dùng recipe/compute nhất quán. Nó không phải kích thước duy nhất có thể train ResNet; implementation có adaptive pooling. Tham khảo [ResNet của torchvision](https://docs.pytorch.org/vision/main/models/resnet.html). Tăng input có thể giữ thêm chi tiết từ source đủ nét nhưng tốn compute và không phục hồi chi tiết vốn đã mất. Đổi size là biến experiment mới, cần so sánh được duyệt; chưa đổi loader/config RC1 trong task này.

Dính một phần đầu/tay người khác không tự làm crop vô dụng. Cần thấy rõ **ai là anchor**, tay/bàn nào thuộc người đó, và evidence cần thiết còn trong crop. Nếu cắt chặt làm mất phone hoặc context hướng nhìn thì phải nới; nếu nới khiến attribution không xác định được thì để U target liên quan hoặc withheld. Không xóa người khác bằng inpainting/mask tùy tiện vì làm thay đổi dữ liệu.

Một giới hạn thực sự của code hiện tại: classifier chỉ nhận RGB crop, không nhận person box/anchor mask để biết owner muốn nhắm người nào. Vì vậy crop có hai người nổi bật tương đương vẫn rủi ro dù reviewer biết anchor. Gallery ghi mô tả người mới và cho mở frame/box; việc person box, work-context và exact crop acceptance vẫn phải hoàn tất trước đóng package. Không dùng context box thay person box.

## 5. Đa dạng và những người được đánh dấu

Đã mở rộng ở cả 5 parent, theo frame có giá trị quan sát. 52 anchor được thử bằng 135 crop mới; 50 anchor trong số đó vào shortlist. Hai nhóm mới bị withheld toàn bộ là G1-A08 (biên nguồn cắt anchor/vùng bài) và G2-A05 (người trước che tay và context hướng nhìn). Các trường hợp khác chỉ giữ frame hữu ích: ví dụ G5-A03 giữ frame 99 rõ đầu hơn; G5-A08 giữ frame 99, không nhân các frame bị người trước che; nhóm camera xa chỉ dùng nhãn looking nếu phone không đủ evidence.

Thêm 2 anchor từ các bổ sung cũ chưa nằm trong 52 nhóm mới (nữ áo sọc xanh G2-A14 và nữ áo trắng G5-A14) tạo tổng **84 anchor**, tính cả 32 anchor gốc. Olive CB-NEW-03 và áo xanh nhạt CB-NEW-05 đã nối alias tương ứng; không đếm thêm người vì đổi ID.

| Nhãn Draft shortlist | Số crop |
|---|---:|
| P/N | 105 |
| P/P | 19 |
| N/N | 20 |
| N/P | 7 |
| U/N | 56 |
| U/P | 34 |
| P/U | 6 |

Tăng đa dạng anchor vẫn chưa tăng số phòng/session độc lập. Các video cùng lớp/đồng phục/bố cục có thể liên quan; 5 parent hash khác không tự là 5 family độc lập. Nhiều người mới chủ yếu bổ sung looking với phone U, nên không tuyên bố đã bù đủ difficult negatives phone/calculator hoặc mọi thiếu hụt sau RC1.

## Phương án bổ sung model nhận diện vật

Khuyến nghị trước mắt: hoàn thiện batch ảnh/nhãn nhất quán và tập kiểm phone-only, calculator-only, cả hai, vật mơ hồ, device của người cạnh bên; chưa thay kiến trúc chỉ vì audit này. Không gộp calculator-only với negative phone khi tay/bàn thiếu evidence.

Nếu mục tiêu là xuất rõ **phone hay calculator**, một nhánh nhận diện vật ở độ phân giải đủ lớn là proposal hợp lý hơn việc kỳ vọng head hai target tự cung cấp lớp vật. Detector COCO thông dụng có `cell phone` nhưng **không có calculator trong 80 lớp**; dùng nguyên trọng số đó không hoàn tất yêu cầu phân biệt hai loại. [Danh sách lớp chính thức](https://docs.ultralytics.com/datasets/detect/coco).

Phạm vi thay đổi cần thiết nếu owner chọn hướng này:

1. Dataset vật thể riêng: bbox mobile/calculator và quy tắc vật mơ hồ/che khuất, annotation completeness, quyền/weights/license và family splits. Đây là contract khác với chỉ annotate một person anchor.
2. Nhánh object detector hoặc object ROI classifier; nối object với đúng tay/bàn/person bằng evidence association, có trạng thái không chắc. “Không detect được” không tự thành phone N.
3. Runtime person → context crop → classifier B (hiện chưa end-to-end) thêm object inference và association. Giữ looking branch riêng; object detector không giải quyết hướng nhìn.
4. Version output/evaluator/config mới nếu thay interface; đo confusion phone↔calculator, lỗi gán device sang người khác, recall theo kích thước/che khuất, latency và quality trên cohort được phép. Chốt quy tắc fusion/abstention trước chạy, không tự thêm threshold vào RC1.

Một hướng khác là head phụ phân loại vật hoặc hai nhánh crop context + ROI thiết bị; cũng cần annotation/object localization và kiểm ROI sai. Chưa có evidence để chọn detector/model cụ thể hoặc bảo đảm phương án nào tốt nhất. Task này không tải weights, chạy model mới, sửa schema, mở test hoặc train.

## Đối chiếu review và bàn giao

[Owner-resolution](owner-resolution.md) xử lý đủ 10 dòng review mới, kể cả dòng trùng CB-0046. Có **87 thay đổi nhãn Draft** so với study trước trong 765 ứng viên hiệu lực. Alternatives là mẫu không ưu tiên cho batch tinh gọn, không phải nhãn excluded accepted hoặc khẳng định vô giá trị. Các cột canonical vẫn null/mask 0 để không bị hiểu là manifest train.

[Validation](validation.json) kiểm pins, geometry/source pixels, input 224, ledger/frame/counts, mask/split và đường dẫn. [Software checks](software-validation.json) ghi kết quả checker, lint và bộ lọc gallery. Kiểm kỹ thuật không thay owner acceptance. Media ở `data/interim` và `outputs` cùng ID, ngoài Git; report/metadata/worksheet ở thư mục này. Không commit/upload.

Validation PASS: 905 ứng viên có hash source/crop/input khớp, 332 PNG khớp pixel crop từ source và preview, 5.565 kiểm đường dẫn. Gallery đã render trong Chrome headless và kiểm trang đầu ở 1440 × 1100; các bộ lọc/phân trang được kiểm bằng JavaScript. Checker không dùng `--require-git`; thư mục mới vẫn untracked, chưa coi là đã giao qua Git. [Pins kết quả audit](result-pins.json) giữ đúng phiên bản bàn giao, không thay acceptance receipt.

Tái lập từ root bằng `.venv/Scripts/python.exe`: `revise.py` → `expand.py` → `qa-boards.py` → `assemble.py` → `validate.py`; `prepare.py` chỉ dùng khi bắt đầu revision, vì nó tạo lại inventory pending. Các worksheet chỉ vật hóa quan sát thủ công; không dùng chúng làm annotator tự động cho nguồn khác. Không chạy lại renderer sau nghiệm thu/pin release; thay đổi tiếp phải tạo revision mới.

Bước tiếp là owner nghiệm thu batch 247 crop và ngoại lệ trong gallery/bảng review. Sau đó mới hoàn thiện person boxes/context/evidence receipt, lineage và đề xuất membership/splits; chưa có quyền tự chọn train/val/test hoặc train tiếp.
