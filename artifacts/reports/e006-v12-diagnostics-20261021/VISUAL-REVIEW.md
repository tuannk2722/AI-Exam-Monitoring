# Nhận xét thị giác — Draft ngày 21/10/2026

37/37 mẫu shortlist đã xem source, crop và input; các nhãn accepted V12 giữ nguyên. Đây là mẫu chọn có chủ đích, không ước lượng tỷ lệ sai nhãn toàn dataset. Bốn dòng **owner review** cần quyết định; các dòng giữ là đề xuất không thấy lý do đổi trong phạm vi đã xem.

[Gallery không hiển thị scores/nhãn](../../../data/interim/e006-v12-diagnostics-20261021/index.html). JSON đầy đủ và exact SHA ở [visual-findings.json](visual-findings.json).

| # | ID | V12 phone / looking | Quan sát | Đề xuất Draft |
|---:|---|---|---|---|
| 1 | `V7-A-008` | N/N | Anchor đang dùng laptop; tay và phần bàn/laptop còn thấy ở input. Không thấy bằng chứng mobile rõ. | Không đề xuất đổi N/N; ca âm tính khó khác miền phòng thi. |
| 2 | `V7-C-132` | N/N | Anchor đang viết trên sách; vật chữ nhật/chi tiết trên bàn không đủ để gợi mobile. | Giữ nhãn accepted; không suy phone từ tư thế tay hoặc vật chữ nhật. |
| 3 | `G27-A04-F00043` | N/N | Tay cầm bút viết, tay còn lại trên giấy; crop giữ vùng bằng chứng ở input. | Giữ N/N; ưu tiên hard negative viết bài trong cùng bối cảnh. |
| 4 | `G05-A02-F00092-R02` | N/N | Một tay gần miệng/cằm, tay còn lại trên bàn; cốc và đồ dùng trong context. | Giữ N/N; tư thế tay gần mặt không tự là phone P. |
| 5 | `V6R2-CA-001` | P/N | Vật dạng điện thoại sát tai và tay cầm bút trên giấy; vẫn thấy ở input. | Giữ P/N; ca phone P dạng áp tai, không chỉ nhìn màn hình. |
| 6 | `E004-EX-C008` | P/N | Điện thoại cầm trong tay rõ cả crop và input; đồng thời có bút/giấy. | Giữ P/N; bỏ sót không giải thích được chỉ bằng ảnh quá nhỏ. |
| 7 | `G06-A02-F00012` | P/N | Điện thoại nằm trên bàn cạnh giấy, anchor đang viết; vật vẫn rõ ở input. | Giữ P/N; ví dụ chuẩn semantics hiện hành bao gồm phone trên bàn. |
| 8 | `G12-A01-F00053-R02` | P/N | Vật có màn hình nhỏ và cụm phím vật lý giống calculator; chưa thấy phone khác trong vùng bàn. | **owner review** — đề xuất phone P → N nếu owner xác nhận đây là calculator và vùng quan sát đủ; không sửa V12. |
| 9 | `V7-UNAPPROVED-C-003` | P/N | Anchor cầm điện thoại rõ; còn một thiết bị trên bàn. ID chứa UNAPPROVED là tên lịch sử, không thay trạng thái release. | Giữ P/N; ví dụ phone P rõ. |
| 10 | `V7-B-018-R04` | N/N | Ảnh gốc/crop đã nhòe; vẫn thấy hai tay và giấy trong tư thế viết. | Không loại chỉ vì nhòe hoặc kích thước nhỏ; giữ nhãn accepted. |
| 11 | `SCB-write-010` | N/N | Cúi viết trên bàn; chi tiết mắt yếu từ crop, vùng bài làm còn đủ. | Giữ N/N; không đồng nhất ảnh khó với dữ liệu sai. |
| 12 | `E004-EX-C002-R04` | U/N | Vật đen trong tay nhìn nghiêng, có chi tiết giống phím; không xác minh chắc mobile từ crop. | Giữ phone U; không dùng hình chữ nhật để ép sang P hoặc N. |
| 13 | `G05-A01-F00065-R02` | U/P | Anchor quay đầu sang bạn/người sau; vật ở cạnh vùng tay/bàn không phân biệt chắc loại. | Giữ U/P; ví dụ tách hai target, looking P không biến phone U thành N. |
| 14 | `V7-D-009` | U/N | Anchor cầm điện thoại đen, hình dáng màn hình/thân máy rõ ở crop và input. | **owner review** — đề xuất phone U → P; looking N giữ nguyên. Đây là review mới, không hồi tố metrics. |
| 15 | `V6-EX-036` | N/N | Anchor cúi đầu nhẹ về vùng giấy/bàn; grayscale và ánh sáng làm nét mặt yếu. | Giữ N/N; head angle riêng không đủ suy looking P. |
| 16 | `E004-CN-048` | N/N | Anchor đứng đọc sách, hướng đầu và mắt về sách; input vẫn giữ sách và mắt. | Giữ N/N; standing không đồng nghĩa looking around. |
| 17 | `EXP-SCB-005` | N/N | Đầu xoay nhẹ khi tay đặt trên bàn; crop cao/hẹp làm vùng mắt nhỏ hơn ở 224. | Giữ accepted N/N; dùng làm ca ranh giới nhìn đầu nghiêng so với vùng bài, chưa đủ bằng chứng đổi nhãn. |
| 18 | `EXP-SCB-021` | N/P | Anchor cầm bút, đầu cúi nghiêng gần trang sách; crop 107 × 111 không cho thấy chắc đang nhìn người khác. | **owner review** — Owner chốt looking P có đủ evidence hay phải U/N; đề xuất U nếu không xác định được vùng nhìn, không tự đổi. |
| 19 | `V7-C-075` | U/P | Mặt quay sang bên, mắt gần khép; source/crop không thể hiện rõ vùng bài hay đích nhìn. | **owner review** — đề xuất xem lại looking P → U vì context/đích nhìn không rõ; không lấy góc đầu thay bằng chứng. |
| 20 | `G05-B02-F00015-R02` | N/P | Crop 77 × 85 đã thiếu chi tiết, đầu hướng sang bên; input chỉ phóng lớn dữ liệu gốc. | Giữ N/P; ca khó có hướng đầu, không đề xuất xóa để tăng metric. |
| 21 | `G09-A02-F00043` | N/P | Anchor nhìn sang phía trước/bên ngoài trang sách; bàn và sách còn trong crop. | Giữ N/P theo contract ngoài vùng bài làm; không suy là gian lận hay phân biệt đang nghe giảng. |
| 22 | `E004-EX-C001` | P/P | Mặt/đầu hướng ra ngoài vùng bàn, điện thoại cầm rõ. | Giữ P/P; ví dụ hai target cùng positive. |
| 23 | `G27-B02-F00016` | N/P | Anchor ở xa, đầu hướng lên khỏi vùng bàn; crop 85 × 116 đã thiếu chi tiết mắt. | Giữ N/P; model có TP dù nhỏ, không đặt cutoff kích thước tùy ý. |
| 24 | `E004-EX-C018` | N/N | Góc trên xuống, hai tay và giấy rõ, đầu cúi về bài. | Giữ N/N; ví dụ âm tính có context làm việc. |
| 25 | `V7-B-048` | N/N | Anchor cúi viết, giấy/bút và vùng bàn còn thấy ở input. | Giữ N/N; đối chứng looking TN. |
| 26 | `CB-0428` | P/N | Trên giấy có hai vật dạng thiết bị, điện thoại accepted vẫn thấy ở input. | Giữ P/N; 11 epoch xem riêng chưa thấy erasing xóa hết phone. |
| 27 | `E004-CF-C021-R03` | P/P | Anchor cầm thiết bị rõ và nhìn sang người bên cạnh; các bàn tay người khác cùng context. | Giữ P/P; dùng thảo luận attribution, không gán mọi thiết bị cho anchor. |
| 28 | `NB-0046` | N/N | Anchor cúi sát giấy, hai tay ở vùng bài làm; crop derivative 224 đủ review. | Giữ N/N; không phải recrop mới trong task này. |
| 29 | `G23-B01-F00003` | N/N | Calculator có cụm phím trên bàn; anchor cầm bút viết. | Giữ N/N; ví dụ calculator không tạo phone P. Erasing epoch 9 che một phần vùng đầu. |
| 30 | `CB-0294` | U/N | Vật dài trong tay chỉ thấy cạnh, có calculator trên bàn; không thấy mặt thiết bị để phân loại chắc. | Giữ U/N; không ép U thành N để tăng supervision. |
| 31 | `V7-OE-S044-A01` | U/N | Thiết bị trong hai tay nhìn nghiêng và một phần bị chai che; không thấy đủ mặt thiết bị. | Giữ U/N; cần evidence nhận diện mobile trước khi đổi P. |
| 32 | `V6R2-MP-006` | U/P | Đầu/mắt hướng lên khỏi bàn; vùng trang giấy phía dưới vẫn có context. | Giữ U/P; phone thiếu bằng chứng độc lập. |
| 33 | `EXP-CM-003` | U/P | Anchor hướng đầu lên/bên ngoài vùng giấy; có vật sát tai nhưng phone accepted U. | Giữ U/P; augmentation epoch 6 che vùng miệng/má, làm yếu bằng chứng looking. Chưa suy nguyên nhân metrics. |
| 34 | `G26-B11-F00027` | U/N | Anchor cúi về giấy, vật chữ nhật dưới tay không phân biệt chắc ở input. | Giữ U/N; cần phân biệt mobile/calculator/vật khác trước gán phone. |
| 35 | `NB-0006` | N/N | Anchor cầm calculator có màn hình nhỏ và phím vật lý, hướng về giấy. | Giữ N/N; ví dụ negative dù cầm thiết bị. |
| 36 | `Y01-A12-F00098` | P/U | Đầu gục/cúi sâu, không thấy mặt/hướng nhìn rõ; điện thoại trên bàn còn thấy. | Giữ P/U; ví dụ U looking không làm mất supervision phone. |
| 37 | `NB-0038-R1` | N/U | Đầu nhìn nghiêng, một phần tay/bài làm ở rìa và bị người trước che; khó chốt đích nhìn. | Giữ N/U; ví dụ ranh giới U cần context, không dùng nhãn nguồn thay review. |
