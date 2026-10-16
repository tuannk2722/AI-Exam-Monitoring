# Đối chiếu review owner và sửa crop E004

Hoàn tất audit và đề xuất Draft ngày **15/10/2026**, giữ ID khởi tạo `E004-crop-bundle-review-20261014`. Đã đối chiếu đủ **765 crop**, xem toàn bộ **212 frame gốc**, tạo và kiểm lại **192 recrop + 5 crop bổ sung**. Shortlist đề xuất gồm **710 mẫu**, giữ 56 mẫu gần trùng làm phương án thay thế và 4 mẫu thiếu bằng chứng ngoài shortlist. **Không xóa crop gốc, không sửa V9, không phân split hoặc train.**

Mở [gallery đối chiếu có tìm kiếm và bộ lọc](../../../outputs/E004-crop-bundle-review-20261014/index.html). Mỗi mục có crop gốc, bản sửa nếu có, frame và khung context, nhãn owner, nhãn Draft riêng cho từng phiên bản, nhận xét và SHA. Khung cam là context gốc; khung xanh là context đề xuất, **không phải person box**. Bấm ảnh để xem kích thước gốc. Gallery hoạt động local, không gọi dịch vụ ngoài.

## Phạm vi và nguồn quyết định

Yêu cầu owner: kiểm kỹ quyết định theo nhóm, được lược mẫu tương tự và bổ sung crop hữu ích từ frame gốc. Owner xác nhận quyền sử dụng bộ dữ liệu và giữ contract hiện tại. Với 7 ID chưa được dòng review bao phủ và dòng CB-0398–0484 thiếu cột nhãn, owner trả lời không có quyết định bổ sung; audit tự đề xuất Draft, không coi im lặng là nghiệm thu.

- [Review nguyên văn đã snapshot](owner-review-original.md), [mapping 46 dòng vào 765 ID](review-input.json). Bản README owner gốc được giữ nguyên.
- [Audit đầu vào trước đó](../E004-crop-bundle-audit-20261014/README.md): pins ZIP, decode, tái tạo crop, tra exact/near overlap với phần dữ liệu được phép xem. Các kết quả đó không chứng minh độc lập nguồn.
- [Contract dữ liệu](../../../docs/data.md), [config study](../../../configs/datasets/E004-crop-bundle-review-20261014.yaml). Thứ tự nhãn là **phone / looking**; U được mask, không thay bằng N.

## Độ phủ kiểm ảnh và giới hạn

Đã xem 48 board của 765 crop, mỗi crop ở kích thước 224; xem 53 board chứa đủ 212 frame ở kích thước tổng quan 960 × 540; phóng lớn các frame/vùng nghi vấn để chỉnh geometry và attribution. Đã xem lại đủ 197 preview derivative ở 224 và 79 cặp gần trùng. [Ledger frame](frame-review-ledger.json) nối mỗi frame với crop gốc và derivative; [ledger crop](crop-review-ledger.json) có một dòng riêng cho mỗi ID.

Đây là audit thị giác thủ công, không phải bằng chứng rằng mọi chi tiết nhỏ trong mọi frame đều xác định được. Không annotate đầy đủ mọi người như một dataset detector. Nơi frame gốc cũng cắt đầu, bàn bị che hoặc thiết bị không phân biệt được tại 224 vẫn giữ U; không nội suy trạng thái từ thời điểm bên cạnh. Recrop giữ pixel gốc, không sinh hoặc phục hồi nội dung bằng AI.

## Các điểm sửa quan trọng

| Phạm vi | Kết quả đối chiếu |
|---|---|
| Calculator và phone | Vật trắng/đen có bàn phím hoặc calculator xanh/hồng không tự là phone. Nhiều P được xác nhận bởi **mobile riêng trên bàn**, không bởi vật đang cầm. Điều này sửa cách diễn giải chưa chính xác trong audit trước. |
| CB-0063–0087 | Không áp P/N toàn nhóm: có các ảnh quay đầu rõ sang bên; vài ảnh tay che/hướng nhìn chưa chắc giữ U. Danh sách từng ID trong ledger và exceptions. |
| CB-0294–0295, 0303, 0332, 0337 | Đề xuất P/P thay P/N vì hướng đầu ra ngoài vùng bài riêng. Không lấy việc nhìn phone/calculator trong vùng riêng làm looking P. |
| CB-0030, 0055 | Crop gốc mất phần đầu. Bản sửa 0030-R1 đề xuất N/P; 0055-R1 giữ N/U vì hướng nhìn còn chưa chắc. Không chuyển nhãn của frame rộng sang crop cũ đã mất evidence. |
| CB-0018–0025, 0106–0112 | Khung cố định lệch khi camera thay đổi. Recrop làm rõ nữ đeo kính bên phải ở nhóm đầu và nữ áo trắng hàng giữa ở nhóm sau. Nhóm sau vẫn có che khuất bàn nên phone U. |
| CB-0224–0252, 0514–0542 | Recrop tập trung đúng nam áo trắng ở giữa / nam áo be. Attribution còn là đề xuất để owner nghiệm thu, không gán nhãn của người lân cận. |
| CB-0543–0571 | Recrop xuống vùng bàn của nữ áo vàng: 0543–0570 đề xuất P/N nhờ mobile riêng cạnh calculator. 0571 bị giấy che thiết bị nên U/N. |
| CB-0582, 0592–0594 | 0582-R1 phục hồi đầu quay sang người bên cạnh, P/P. 0592–0594-R1 phục hồi đầu nhìn bài nhưng không thấy phone ở thời điểm đó, U/N. |
| CB-0601–0603 | Đầu không nằm trong phần frame gốc khả dụng; recrop không thể cứu looking, vẫn P/U. |
| CB-0626–0627, 0631–0632 | Không đồng nhất nhận xét nhóm: 0626–0627 đề xuất P/U; 0631 là góc quay trái rõ P/P; 0632 chuyển động mờ, P/U. |
| CB-0638–0639 | Recrop phục hồi đầu quay trái, đề xuất P/P. |
| CB-0648 | Metadata `redshirt` nhưng crop chứa người khác. 0648-R1 trả về người áo đỏ. Nữ áo trắng được tạo thành **CB-NEW-04**, nhãn Draft U/N, không chuyển quyết định N/N có điều kiện của owner sang người áo đỏ. |
| CB-0673–0674 | Ngoại lệ trong nhóm owner P/P: đang cúi về trang giấy riêng, đề xuất P/N. Các cảnh quay thân/cầm phone 0694, 0696–0697, 0702 giữ looking U. |
| CB-0715–0748 | Recrop phân biệt vest xanh, vest xám và nữ áo đỏ. CB-0734 không có anchor nữ áo đỏ tại vùng/frame đó, giữ ngoài shortlist; không đổi sang người khác để có nhãn. |
| CB-0762 | Vật nhỏ/mờ trong tay không đủ xác nhận absence mobile; đề xuất U/N thay N/N. |

Có người khác trong context **không tự làm mẫu sai** nếu anchor và bằng chứng vẫn rõ. Đầu/tư thế có thể đủ diễn giải hướng nhìn khi mắt nhỏ, nhưng không thêm quy tắc “80% tư thế”. Tay dưới bàn không tự là phone N. Ảnh tĩnh không chứng minh ý định, thời lượng hay gian lận.

## Đối chiếu owner

| Loại đối chiếu trên đúng crop gốc | Số mẫu |
|---|---:|
| Cùng nhãn cột owner và đề xuất audit | 405 |
| Khác ít nhất một nhãn, giữ Draft | 39 |
| CB-0648: quyết định có điều kiện cho anchor khác | 1 |
| Có nhận xét hoặc dòng thiếu nhãn P/N/U hợp lệ | 320 |
| Tổng | 765 |

320 **không có nghĩa owner chưa review 320 ảnh**: nhiều dòng đã có nhận xét “crop lệch”, “nhiều vấn đề”, hoặc quyết định nằm trong prose. Nguyên văn luôn được giữ để đối chiếu. 405 đồng thuận cũng không tự tạo receipt accepted hay cho phép dùng bản recrop mới. [Bảng 40 ngoại lệ đối với cột nhãn](exceptions.md) và [review derivative](derivative-review.json) tách rõ hai phạm vi.

## Geometry mới và mẫu bổ sung

192 recrop thay thế các crop có vấn đề trong **đề xuất shortlist**, không ghi đè crop gốc. Mỗi derivative có source SHA, context XYXY, crop native PNG, preview 224 RGB letterbox bilinear với fill `[124, 116, 104]`, hash và nhãn Draft riêng. [Geometry đề xuất](geometry-proposals.json), [derivative pins](derivatives.json). Context box của study chưa phải bộ annotation `PilotRecord` accepted; person box, work-context và evidence receipt cần hoàn thiện trong bước đóng gói sau nghiệm thu, không suy từ box context thành person box.

| Mẫu mới | Giá trị bổ sung | Draft |
|---|---|---|
| CB-NEW-01 | Nữ áo sọc xanh cầm mobile, quay sang người bên cạnh | P/P |
| CB-NEW-02 | Cùng anchor ở frame khác nhìn vùng riêng; cặp tương phản với NEW-01 | P/N |
| CB-NEW-03 | Nam áo olive nhìn bài; thiết bị chưa chắc tại 224, phone masked | U/N |
| CB-NEW-04 | Tách nữ áo trắng khỏi crop sai anchor CB-0648 | U/N |
| CB-NEW-05 | Nữ áo khoác xanh nhạt, mobile trên sách, nhìn ngoài bài | P/P |

5 mẫu mới thuộc 4 anchor được đề xuất; không phải 5 nguồn độc lập mới.

## Giảm tương tự và khả năng bù thiếu hụt

Bộ lọc gợi ý 79 cặp có dHash ≤ 5 trong **cùng parent, anchor, cặp nhãn Draft và loại review**. Đã kiểm từng cặp; giữ lại 23 mẫu có khác biệt về che khuất, tư thế hoặc thiết bị, chỉ đề xuất 56 mẫu làm phương án thay thế. Đây là ngưỡng screening đã dùng ở audit trước, không phải tiêu chuẩn acceptance hoặc chứng minh hai ảnh giống hệt. Không dùng quan hệ bắc cầu để gom khác anchor/khác nhãn. [Quyết định từng cặp](redundancy-visual-review.json), [shortlist](shortlist-proposal.json).

Sau thay 192 bản gốc bằng bản recrop và thêm 5 mẫu, có 770 ứng viên hiệu lực: **710 shortlist + 56 alternatives + 4 withheld**. Bốn withheld là CB-0090, CB-0097, CB-0615-R1 và CB-0734; đều không có target đủ chắc để đề xuất supervision. Toàn bộ 962 file crop gốc và derivative vẫn được giữ local.

| Nhãn Draft | Shortlist |
|---|---:|
| P/N | 508 |
| P/P | 36 |
| N/N | 60 |
| N/P | 10 |
| P/U | 34 |
| U/N | 40 |
| U/P | 21 |
| N/U | 1 |

Bộ này bổ sung evidence mobile trên bàn, calculator dễ nhầm, góc quay đầu, cảnh nhiều người và các mức che khuất. Tuy nhiên 508/710 vẫn là P/N, chỉ có 5 parent video và nhiều ảnh gần nhau cùng người/phòng. **Không kết luận đã bù đủ coverage hay có thêm 710 quan sát độc lập.** Parent khác hash/URL không bảo đảm khác recording/session; cần kiểm lineage theo family trước assignment. Không mở ảnh test/reserve hay chạy model để chọn mẫu trong task này.

## Kiểm tra và tái lập

[Validation](validation.json) ghi hash, geometry, pixel parity, đầy đủ ledger/frame, phân hoạch shortlist và 3.272 liên kết ảnh PASS. [Kiểm phần mềm](software-validation.json): lint/compile, JavaScript gallery (bộ lọc, tìm kiếm, phân trang), repo checker và diff PASS; chưa kiểm layout trong trình duyệt. Worksheet chỉ ghép các quan sát thủ công đã ghi; không phải model tự gán nhãn. Các file thực hiện: `prepare.py`, `decisions.py`, `render.py`, `assemble.py`, `validate.py`; template HTML ở `gallery-template.html`. Dùng `.venv/Scripts/python.exe` từ root. `prepare.py` giữ snapshot owner đã tồn tại; không dùng nó để thay snapshot bằng bản owner mới. Input hoặc quyết định thay đổi sau khi nghiệm thu phải tạo revision mới.

Study hiện chưa seal. Không cần train/smoke/full ML tests vì không sửa production loader/trainer/schema. Media và output nằm ngoài Git; metadata/pins/report đủ dẫn tới inputs local. Không upload/commit/push. Bản copy trên cùng ổ không là backup ngoài thiết bị.

Bước tiếp theo là owner nghiệm thu **batch cụ thể trong gallery**, ưu tiên 40 ngoại lệ, 197 derivative và attribution ở các nhóm đã nêu. Sau đó mới hoàn thiện person boxes/context review/lineage và đề xuất membership/split theo contract. Task hiện hoàn tất ở phạm vi audit + đề xuất review, chưa là release Accepted.

## Kết quả review của onwer

| ID | Kết quả | Lý do |
|---|---|---|
| CB-00001 -> CB-0025-R1 | Nhiều vấn đề | Gán P,N,U đang bị không nhất quán, nhiều crops anchor cầm vật màu đen thì để là P/N nhưng có crops lại là U/N. Ví dụ CB-0009 CB-0012 ... vật bị che nhưng vẫn P/N; CB-0014 CB-0017 khá rõ ràng nhưng lại U, CB-0016 gần tương tự CB-0014 nhưng lại P/N; CB-0024-R1 CB-0025-R1 vật màu trằng mà anchor đang cầm là calculator nhưng chỉ với crop như vậy thì không thể suy ra dựa theo nhìn nhận thực tế của tôi được nên hãy cân nhắc để U chứ cũng làm sao chắc chắn đó là phone được |
| CB-0043, CB-0044, CB-0045, CB-0046, CB-0052 | Xém xét lại | Vật bị tay anchor che phần lớn thì có nên để phone là N không mặc dù đó là calculator và mặt trước có thể nhìn một ít nút bấm mà chỉ có ở calculator |
| CB-0046, CB-0048, CB-0049, CB-0050, CB-0051, CB-0054, CB-0056 | Xem xét | Vật bị tay anchor che nhưng chỉ bị che một nửa nên vẫn có thể thây rõ những nút bấm chỉ có ở cal nên N/N chắc cũng hợp lý đúng không? |
| CB-0055-R1 | N/N | Hướng mắt và tư thế vẫn đang chỉ vào own-paper |
| CB-0057, CB-0059, CB-0060, CB-0062 | Xem xét | Crop như này thì làm sao chắc chắn được calculator? Trông rất giống phone nhưng nếu suy ra từ các khung hình trước đó thì mới có thể suy ra được đó là calculator |
| CB-0065, CB-0066, CB-0067 | P/N | Tư thế và hướng nhìn rất rõ ràng là đang làm bài, trong khi các crops khác của người này cũng có tư thế tương tự lại đề là P/N, wtf??? |
| CB-0074, CB-0075, CB-0076, CB-0078, CB-0079, CB-0080, CB-0081, CB-0082, CB-0087 | P/N | Đầu không hề quay đi đâu cả vẫn đang nhìn vào own-paper, chỉ là tay che đầu thôi nhưng tư thế như vậy rất rõ ràng là đang làm bài rồi |
| CB-0097 | U/N | Tư thế và hướng nhìn là own-paper |
| CB-0098, CB-0102, CB-0103, CB-0104, CB-0105,  | U/N | Mobile đâu? vẫn là cái màu hồng đó mà. |
| CB-0111-R1 | Loại | Crop này targeted anchor bị núp sau người ngồi phía trước thì bỏ đi chứ thêm vào làm gì? Hay nó có tác dụng gì à? |
