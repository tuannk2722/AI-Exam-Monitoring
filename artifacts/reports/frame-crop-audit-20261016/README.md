# Audit và crop 5 ZIP frames — 16–17/10/2026

Đã xem 536 frame theo chuỗi trong 27 thư mục nguồn, lần lượt ZIP 01 → 05. Batch bàn giao có **100 crop native PNG, từ 91 frame, thuộc 72 anchor cục bộ trong 26 video**. Đây là batch **Draft để owner review**, chưa nhập V10, chưa có nhãn canonical hoặc split mới.

- [Mở gallery local](../../../data/interim/frame-crop-audit-20261016/index.html): cùng video và cùng anchor nằm cạnh nhau; có frame gốc, khung person/context, input 224 px, lý do chọn và toàn bộ frame của video.
- [Bộ PNG + metadata ZIP](../../../data/interim/frame-crop-audit-20261016/crops-review.zip).
- [Thư mục crop thuần](../../../data/interim/frame-crop-audit-20261016/crops): `part_XX/GXX/AXX/*.png`, không trộn revision đã bỏ.

| ZIP | Frame đã xem | Nhóm nguồn | Crop bàn giao |
|---|---:|---:|---:|
| 01 | 108 | 6 | 24 |
| 02 | 107 | 6 | 21 |
| 03 | 107 | 5 | 21 |
| 04 | 107 | 5 | 19 |
| 05 | 107 | 5 | 15 |
| Tổng | 536 | 27 | 100 |

## Cơ sở chọn và cách review

Đọc [contract dữ liệu](../../../docs/data.md), [targeted coverage sau RC1](../E004-targeted-coverage-20261014/README.md), [V10 và kết quả C345](../E004-train-enrollment-20261016/README.md) trước khi chọn. Ưu tiên phân biệt phone/calculator/bút và nhìn ngoài vùng bài so với đọc/viết đúng trang; không đặt quota số crop. Một số cảnh là làm thủ công, ăn kem, họp hoặc thuyết trình; hướng nhìn không được diễn giải thành gian lận.

Xem đủ 72 board nguồn, mỗi board tối đa 9 frame, theo thứ tự từng video; mở lại các frame cần đo khung hoặc phân biệt vật. Tạo crop bằng geometry quan sát, rồi xem toàn bộ crop cạnh input 224 px. Vòng cuối rà lại cả 5 ZIP, mở lại nguồn của các khung sát tóc/tay. Không chạy detector/model mới và không xem predictions để quyết định nhãn.

Person box bao phần cơ thể **nhìn thấy trong nguồn**, context giữ đầu, tay và vùng hành vi có liên quan. Không dựng lại bộ phận bị che hoặc mất khỏi frame. Khi phải giữ người lân cận, anchor vẫn là trọng tâm; nguồn và overlay cho phép kiểm tra attribution. Khung không bị ép vuông. Crop PNG khớp pixel ROI nguồn, không chỉnh ảnh hoặc upscale native; input 224 chỉ là preview letterbox.

Mỗi anchor giữ 1–3 crop theo thay đổi thao tác/hướng đầu; không cắt mỗi lần xuất hiện. Có **11 đề xuất bị bỏ sau crop QA** do source mất đầu/tay, blur hoặc không còn evidence đủ rõ. G15 không giữ crop vì native quá mờ. Các revision cũ không thuộc batch 100 ảnh.

[Frame audit](frame-audit.json) có đúng 536 dòng, liên kết board, SHA, quyết định đề xuất/không đề xuất thêm và nhận xét chuỗi. Với frame không được chọn, nhận xét ở mức chuỗi, không phải lý do riêng cho từng người. Đây là lựa chọn mẫu classifier; không phải annotation detector đầy đủ mọi người, cũng không chứng minh không còn anchor hữu ích nào khác.

## Nhãn và giới hạn

Thứ tự Draft là `[phone_use, looking_around]`, P/N/U theo contract. Tổng: 30 đề xuất phone P; 33 đề xuất looking P; 30 cặp N/N. Có 32 crop chứa ít nhất một target U. Không dùng label nguồn có sẵn vì ZIP chỉ chứa frame. Toàn bộ canonical targets vẫn null, masks `[0, 0]`, usage `review_only`, split null, owner approval false.

Vật đơn sắc chỉ lộ cạnh/mặt lưng, tay khuất hoặc chưa rõ thuộc ai được giữ U. Máy tính có phím rõ không phải phone. Một số phone ở trên bàn vẫn là P khi gắn được với anchor, dù đang viết. Nhãn negative chỉ là đề xuất để owner nghiệm thu; chưa phải ground truth. Crop resolution nhỏ chỉ hỗ trợ tư thế rõ trong một số góc camera cao, không đủ suy diễn vật nhỏ hoặc chi tiết mắt.

Theo câu trả lời owner ngày 17/10: **chưa có mapping lớp/buổi học, giữ nhóm theo video**. Anchor là continuity cục bộ của chỗ ngồi/cảnh, không phải danh tính và không ghép người giữa video. Các nhóm G01/G08/G10/G19, G04/G11, G18/G20, G22/G23 có dấu hiệu cảnh tương đồng; đây chỉ là gợi ý, chưa xác nhận cùng room/session. Các nhóm khác cũng chưa được chứng minh độc lập.

[Đối chiếu lineage](lineage-review.json): không có source SHA hoặc tên thư mục trùng metadata 1.553 record của V10. **Chưa kiểm near-duplicate toàn bộ V10**, vì đổi tên/resize hoặc quay lại cùng phòng vẫn có thể trùng nguồn. Không dùng kết quả exact-match bằng 0 làm bằng chứng novelty hoặc đủ gate enrollment. Không mở media của pool test/reserve hiện hành.

## Evidence và kiểm tra

- [Inventory](inventory.json): ZIP SHA/bytes, member, 536 file SHA/RGB SHA, dimensions, dHash, 27 nhóm và 72 boards. CRC/decode ban đầu PASS; 507 frame 640 × 360, 17 frame 534 × 360, 12 frame 360 × 640. Không trùng exact bytes/RGB trong nguồn.
- [Lựa chọn và loại sau QA](selection-draft.json), [crop proposals](crop-proposals.json), [index file review](review-index.json), [revision không thuộc batch cuối](superseded-proposals.json).
- [Validation](validation.json): toàn bộ source bytes/RGB, bounds/containment, native ROI pixels/SHA, input 224 parity/SHA, Draft masks/splits và coverage 536 frame PASS. Không có crop trùng exact RGB. Tối đa 3 crop/anchor; không dùng ngưỡng dHash tự đặt để phê duyệt near-duplicate.
- SHA metadata V10 được ghi nhận trong validation. Không sửa V10, production code, spec, labels/splits hiện hành hoặc train.

[Kiểm bàn giao](delivery-validation.json): 1.701 tham chiếu local và 127 ID HTML hợp lệ; ZIP CRC, exact PNG bytes và membership 100 crop PASS. Worksheet syntax, Ruff syntax/import checks và format PASS; `git diff --check` PASS. Đã render gallery local để kiểm bố cục. Không thay production nên không chạy lại ML/training suite.

Quyền sử dụng: owner xác nhận 27 video và toàn quyền sử dụng trong yêu cầu; thực hiện audit/crop local. Không upload media. Review assets nằm trong data/interim; Git chỉ giữ report/worksheet/metadata. Preview tạm được dọn sau khi board và evidence cần review đã chuyển vào `data/interim/.../review`.

## Tái tạo worksheet

Chạy từ repository root bằng `.venv/Scripts/python.exe -X utf8` theo thứ tự:

1. `artifacts/reports/frame-crop-audit-20261016/audit.py` — kiểm ZIP, giải nén nguyên bytes nếu chưa có, xác minh exact bytes nếu đã có, tạo boards. ZIP gốc cần còn ở đường dẫn Downloads đã pin.
2. `artifacts/reports/frame-crop-audit-20261016/build_review.py` — dùng geometry Draft đã lưu; tái dùng `source_review.write_pending_crop`, không annotate lại bằng model. Candidate đã tồn tại phải giữ cùng geometry/states/reason; đổi crop cần revision mới.
3. `artifacts/reports/frame-crop-audit-20261016/finalize_review.py` — kiểm tất cả crop, export theo video/anchor, tạo gallery/ZIP/metadata đối chiếu.

Kiểm bàn giao độc lập bằng `artifacts/reports/frame-crop-audit-20261016/verify_delivery.py`.

Các script là worksheet của batch, không là API production. Gallery dùng file local, không cần server. Sau review, owner có thể chốt/loại theo candidate ID; enrollment và quyết định group/split là bước riêng. Task hiện tại hoàn tất ở audit + crop + bộ review.

## Kết quả review của owner

**Vấn đề chung**: G05-A01-F00039, G04-A03-F00074-R02, G03-A02-F00018, G14-A02-F00047, G14-A04-F00011, G14-A05-F00012, G14-A07-F00018, G14-A09-F00027, G14-A10-F00018, G18-A01-F00001, G18-A02-F00007,  G18-A02-F00010, G18-A03-F00001, G18-A03-F00010,  G19-A01-F00039, G19-A01-F00052, G20-A02-F00001,  G20-A02-F00020, G20-A03-F00073, G23-A03-F00009. Trong toàn bộ những crop mà tôi nêu ra thì đều có dạng là tay cầm vật chưa rõ ràng, có thể là phone/calculator/whatever. Vậy nên phải kiểm tra thật kỹ để gán giá trị sao cho phù hợp với những crop trong dataset hiện có nhất. Tôi không nói là toàn bộ crop tôi nêu ở trên đều phải đưa về phone U đâu mà là bạn cần kiểm tra lại thật kỹ xem cái nào thực sự có thể phân biệt được và trong bộ dataset hiện tại thì những crop gần tương tự như vậy đang gán như nào đề có thể chốt một hướng đồng nhất. 

| ID | Kết quả | Chú thích |
|---|---|---|
| G01-A01-F00001-R02 | Xem xét | Mặc dù bàn tay của một tay không nhìn được nhưng đó là tư thế chống cằm, vậy thì có nên tính là phone U không? |
| G02-A02-F00015 | Xem xét | Mặc dù ảnh hơi mờ nhưng vật đặt trên bàn có mặt trước như vậy mà không quy thành calculator được hả? |
| G04-A02-F00014-R03 | Xem xét | Bàn và tay nhìn khá rõ chỉ là phần bàn tay của một tay bị che mất còn toàn bộ phần tay đó vẫn được quan sát khá rõ, như vậy có nên tính là phone U không? Vì trong bộ dataset hiện tại tôi nhớ là cũng có crop dạng như này rồi nhưng để giá trị là gì thì tôi không nhớ |
| G04-A03-F00074-R02 | U/N | Vật cầm trên tay như thế sao mà biết là calculator? Bạn suy ra từ frame trước hả? |
| G06-A03-F00012 | Xem xét crop | Nếu đưa crop như này vào train thì phone trên bàn chỉ có thể là của người trong crop thôi chứ làm gì còn ai nữa mà bên cạnh. Cái này cần làm rõ lại |
| G08-A01-F00009-R02 | N/N | Với crop này thì hoàn toàn có thể biết được không có vật gì giống phone hay gây nhiễu ở tay cả, chỉ có mỗi cái là một tay đang cầm bút thì có thể khó nhìn chút |
| G08-A01-F00014-R02 | Xem xét | Tư thế của người trong crop là một tay khoanh vào còn tay kia cầm bút, ảnh hơi mờ nhưng vẫn có thể quan sát được hết tay. Vậy thì để phone U có hợp lý không? |
| G09-A02-F00043, G09-A02-F00105 | Xem xét | Việc tay bị băng bó thì có gì gây nhiễu hay nhầm lần hay khó xác định mà lại để phone U? Nếu đưa vào train khiến AI nhầm lẫn à? Chứ tôi thấy so clear là phone N |
| G10-A01-F00008 | N/N | Ảnh rõ ràng, tay có thể quan sát rõ ràng, chống vào đầu thì có gì nhiễu mà để phone U? Crop này còn rõ ràng hơn crop G01-A01-F00001-R02 |
| G10-A01-F00013 | N/P | Quan sát được rất rõ toàn bộ cơ thể và cả bàn mà |
| G13-A06-F00021 | Xem xét | Tay có thể quan sát rõ, bàn thì cũng không có gì gây nhiễu. Vậy để phone U có hợp lý không? |
| G14-A02-F00047 | Xem xét | Với cách cầm như kia thì theo toàn bộ những crop tương tự trong dataset hiện tại thì phải để là U chứ, nhưng crop có quan sát được trên bàn có một phần bàn phím laptop thì từ đó có bắt phone P không? Kiểm tra lại xem. Còn looking_around tôi đề xuất là N vì mắt và hướng đầu không lệch quá so với own-paper |
| G14-A04-F00011 | Xem xét | Tương tự crop G14-A02-F00047, có xuất hiện laptop nên cầm xem xét lại để thống nhất cách xử lý chung |
| G14-A07-F00018 | Xem xét | Ảnh hơi mờ nên mấy chấm đen (cụm camera sau) có thực sự chấp nhận được không? |
| G14-A09-F00027 | Xem xét | Với crop như này mà biết nó là laptop sao? Hay bạn dựa vào frame gốc vậy? |
| G14-A10-F00018 | Xem xét | Crop đang dính thiết bị của bạn ngồi cạnh như vậy có ổn không? Và thứ mà targer anchor cầm không hề quan sát được rõ, nếu theo bộ dataset hiện tại nó phải là phone U chứ |
| G16-A02-F00027 | Xem xét | Phone U thì tôi còn có thể tạm chấp nhận mặc dù phone đặt trên bàn nhưng với tư thế đó thì hoàn toàn không looking_around, một tay che mặt nhưng bộ dataset hiện tại đã có nhiều crop kiểu như vậy rồi mà. |
| G17-A01-F00012 | Xem xét | Target anchor đang ngồi nghiêng thôi chứ tôi thấy đầu vẫn nhìn vào own-paper, với chất lượng ảnh và hơi xa như này thì cũng hơi khó phân biệt vậy nên nếu cho vào mà làm ảnh hưởng tới kết quả model thì hoàn toàn có thể loại |
| G18-A02-F00007, G18-A02-F00010 | Xem xét | Crop như này thì có chắc chắn được là phone P không? |
| G18-A03-F00001, G18-A03-F00010 | U/N | Tư thế cầm và kiểu thiết bị như này đã chốt rất nhiều lần là phone U rồi |
| G19-A01-F00039, G19-A01-F00052 | N/  | Tay và bàn của targer anchor hoàn toàn clear |
| G21-A01-F00007 | N/P | Tay có thể quan sát rõ là đang cầm vật giống bìa cartoon mà, hay là nó cũng là vật gây nhiễu? |
| G22-A01-F00013-R02 | N/N | Một tay đang khoanh vào, tư thế này giống với crop nào đó ở trên, nhưng mọi thứ hoàn toàn clear, không có gì gây nhầm lẫn cả |
| G27-A01-F00016-R02 | Xem xét | Vẫn là tư thế khoanh tay này, mọi thứ clear, không có vật gì gây nhầm lẫn |
| G27-A02-F00022, G27-A03-F00031 | Xem xét | Crop như này thì làm gì còn người nào khác nữa mà không biết thiết bị của ai? Quy định đó chỉ áp khi mà đưa vào cả một frame gồm nhiều người thôi chứ? Giống với crop nào đó bên trên |