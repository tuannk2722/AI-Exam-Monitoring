# Kết luận đối chiếu owner review — 17/10/2026

Phạm vi: xử lý 38 ID được nêu trong README; ghi nhận 62 crop còn lại được owner mặc định approve. Đã xem crop native, input 224 và frame cùng thời điểm của các ngoại lệ; đối chiếu 33 ví dụ **train** của V10 cùng hướng xử lý occlusion đã được duyệt. Không mở test/reserve, không chạy model và không mở rộng tìm anchor mới trong lượt này.

## Phương án đề xuất

- **72 ID đã có approval**: 62 mặc định và 10 có nhãn owner chốt rõ. Approval ở đây là review crop/nhãn, không phải enrollment/split.
- **28 ID đã có kết luận đề xuất**, chưa tự ghi thành owner acceptance: 25 giữ khung, 1 recrop, 2 tạm loại.
- Sau khi owner đồng ý phần đề xuất: **98 crop** trong danh sách giữ, gồm **G06-A03-F00012-R02** thay khung cũ. Tạm loại G14-A10-F00018 vì crop còn gây nhiễu anchor/thiết bị và G17-A01-F00012 vì evidence yếu.
- G18-A03-F00001 **U/N**, F00010 **U/P** theo câu trả lời owner trong hội thoại ngày 17/10. Chỉ F00010 looking được làm rõ so với dòng gộp trong README.

[Mở gallery đối chiếu](../../../data/interim/frame-crop-owner-review-20261017/index.html) · [Ledger đủ 100 ID](owner-review-decisions-20261017.json) · [Snapshot nguyên văn nhận xét](owner-review-input-20261017.md) · [33 ví dụ V10 train và SHA](v10-comparison-20261017.json).

## Các điểm cần thống nhất

**Tay khoanh, chống cằm, băng bó:** không phải lý do tự động gán phone U. NB-0013/NB-0015, CB-0055-R1, CB-0742-R1 và NC-009 có negative được duyệt khi phần evidence còn lại đủ rõ. Ngược lại, NBX-004/NBX-005, NC-010 và G4-A03-F105/F125 cho thấy mất evidence quan trọng vẫn có thể U. Đây là đối chiếu từng ảnh, không thay contract thành “tay khuất luôn N”. Băng bó không tự tạo ambiguity về phone; chưa có thử nghiệm để nói các ảnh ấy sẽ làm model nhầm hay cải thiện.

**Mặt lưng thiết bị:** NC-003 U/N và NC-012 N/N của cùng anchor cho thấy phải xét từng frame; không lấy calculator ở frame trước để sửa vật mặt lưng ở frame sau. CB-0024-R1 và CB-0390 cũng giữ U khi camera/loại vật chưa rõ. Đề xuất giữ P cho G05-A01, G18-A01, G20-A03 vì cụm ống kính còn tách được; chuyển các mặt lưng/cạnh thiếu đặc trưng sang U theo bảng. G14-A07 được đề xuất U vì các chấm nhỏ/nhòe chưa đủ chắc; đây là nhận định thị giác cần owner chốt, không phải ngưỡng pixel mới.

**Laptop và looking:** laptop không làm phone_use thành P. Vật trong tay vẫn được xét riêng. G14-A09 không đủ thấy laptop trong crop nên bỏ lý do suy từ frame rộng. Đầu cúi/che mặt hoặc thân nghiêng không tự chứng minh looking P: G14-A02 và G16-A02 đề xuất looking N; G17-A01 tạm loại vì khó phân biệt chắc.

**Thiết bị của ai:** không cần chứng minh quyền sở hữu ngoài đời; cần attribution hành vi/vùng hoạt động cho anchor. Quy tắc này áp dụng cả crop, vì crop bỏ người khác không tạo ra evidence mới rằng vật thuộc anchor. Tuy nhiên, người xem chỉ nhận RGB crop nên không thể dùng lời giải thích dựa trên phần bị cắt mất để cứu một negative gây hiểu nhầm. Vì vậy G06 phải sửa khung. G14-A10 tạm loại vì khung thử vẫn dính thiết bị bên cạnh hoặc cắt sát tay. G27-A02/A03 đề xuất giữ U/P: phone rõ nhưng vùng bàn dùng chung và thiếu tương tác/vùng bài riêng để gán chắc cho anchor; không khẳng định phone thuộc người khác. Owner có thể chốt khác nếu xác nhận evidence không gian trong chính crop đủ — chưa tự nâng thành P.

## Kết luận từng ID được nêu

P/N/U lần lượt là positive/negative/unknown; thứ tự phone_use / looking_around. U bị mask cho target đó khi và chỉ khi đi qua quy trình enrollment; hồ sơ này chưa tạo canonical labels.

| ID | Cũ → kết luận | Xử lý | Trạng thái | Cơ sở |
|---|---|---|---|---|
| G01-A01-F00001-R02 | U/N → N/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Tay chống cằm và tay còn lại ở vùng viết; không thấy vật cầm mơ hồ. Không tự động U chỉ vì bàn tay bị đầu che một phần. Đối chiếu: CB-0055-R1, CB-0742-R1. |
| G02-A02-F00015 | U/P → N/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Vật trên trang có bố cục màn hình nhỏ và vùng phím; tay còn lại không có vật mơ hồ. Đề xuất calculator → phone N; hướng đầu lệch khỏi vùng bài giữ P. Đối chiếu: CB-0604-R1, CB-0026. |
| G03-A02-F00018 | N/P → N/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Vật cầm có nếp gấp và mép bao mềm, không chỉ là một mặt lưng thiết bị hình chữ nhật. Giữ N/P từ chính crop; không dùng tên hoạt động ở frame khác để suy ra vật. Đối chiếu: NC-009. |
| G04-A02-F00014-R03 | U/N → N/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Cánh tay gập/khoanh trên bàn, phần bị che nằm trong tư thế tay rõ; không có vật mơ hồ. Đủ evidence còn lại để N theo hướng owner đã duyệt cho occlusion, không phải mọi tay khuất đều N. Đối chiếu: NB-0013, NB-0015. |
| G04-A03-F00074-R02 | N/N → U/N | Giữ crop | Owner đã chốt nhãn | Theo owner: chỉ thấy mặt lưng/cạnh vật đang cầm; không truyền nhận diện calculator từ frame khác. Đối chiếu: NC-003, NC-012. |
| G05-A01-F00039 | P/N → P/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Mặt lưng có các vòng ống kính tách biệt trong cụm camera và vòng trên ốp; đặc điểm nhận diện mạnh hơn một chấm tối hoặc cạnh đen. Giữ phone P, nhìn vào vùng thao tác N. Đối chiếu: CB-0024-R1. |
| G06-A03-F00012 | N/N → N/N | Thay bằng R02 | Đề xuất sau đối chiếu — chờ owner chốt | Khung cũ giữ phone ở bàn người bên cạnh nhưng cắt gần hết người đó, khiến RGB input dễ gán nhầm anchor. Đề xuất R02 bỏ vùng bàn bên cạnh, giữ đầu, hai tay và tờ giấy; không chỉ sửa lời giải thích. |
| G08-A01-F00009-R02 | U/P → N/N | Giữ crop | Owner đã chốt nhãn | Theo owner: tay cầm bút, không có vật gây nhiễu; chốt N/N. |
| G08-A01-F00014-R02 | U/N → N/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Một tay khoanh, tay kia cầm bút; phần tay và bàn còn lại đủ rõ, không có thiết bị mơ hồ. Đề xuất phone N. Đối chiếu: NB-0013, NC-009. |
| G09-A02-F00043 | U/P → N/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Băng bó tự nó không phải evidence cho thiết bị hoặc unknown. Tư thế tay và vùng hoạt động còn lại đủ quan sát, không thấy vật mơ hồ; đề xuất phone N, giữ looking P. Không suy luận tác động model khi chưa đo. Đối chiếu: NB-0015. |
| G09-A02-F00105 | U/N → N/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Tương tự F00043 nhưng đánh giá ảnh này độc lập: băng bó không tạo một vật cầm chưa rõ, vùng bài đủ quan sát; đề xuất N/N. Đối chiếu: NB-0015. |
| G10-A01-F00008 | U/N → N/N | Giữ crop | Owner đã chốt nhãn | Theo owner: chống đầu, tay/bàn rõ; chốt N/N. |
| G10-A01-F00013 | U/P → N/P | Giữ crop | Owner đã chốt nhãn | Theo owner: tay/bàn rõ, hướng đầu ra ngoài vùng bài; chốt N/P. |
| G13-A06-F00021 | U/P → N/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Tay chống mặt và phần tay/vùng bàn còn thấy không có vật mơ hồ. Người phía trước che một phần không tự động làm phone U khi evidence còn lại đủ; đề xuất N/P. Đối chiếu: CB-0745-R1, G2-A12-F005. |
| G14-A02-F00047 | P/U → U/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Thiết bị cầm chỉ lộ mặt/cạnh chưa đủ nhận diện. Laptop không thuộc phone_use và không nâng phone lên P. Đầu vẫn hướng vào vùng thao tác/bài của anchor; đề xuất U/N. Đối chiếu: NC-003, CB-0390. |
| G14-A04-F00011 | P/N → U/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Vật cầm có mặt lưng/viền nhưng thiếu camera, màn hình hay phím đủ phân biệt; laptop cạnh đó không giải quyết vật đang cầm. Đề xuất U/N. Đối chiếu: NC-003, CB-0390. |
| G14-A05-F00012 | P/N → U/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Vật cầm chỉ lộ mặt lưng/cạnh; calculator trên bàn không chứng minh vật cầm cũng là calculator hoặc phone. Đề xuất U/N. Đối chiếu: CB-0390. |
| G14-A07-F00018 | P/N → U/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Các chấm tối ở góc thiết bị nhỏ và nhòe trong input 224; chưa tách được đặc điểm camera đủ chắc so với mặt lưng/ốp khác. Đề xuất U/N, không gọi camera chỉ từ vài chấm. Đối chiếu: CB-0024-R1. |
| G14-A09-F00027 | P/N → U/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Mặt lưng vật cầm chưa phân biệt được; phần vật sát mép crop cũng không đủ để khẳng định laptop. Bỏ lý do suy ra laptop từ frame rộng; đề xuất U/N. Đối chiếu: NC-003, CB-0390. |
| G14-A10-F00018 | P/N → U/N | Tạm loại khỏi đợt nhập | Đề xuất sau đối chiếu — chờ owner chốt | Vật anchor cầm là U, đồng thời crop giữ thiết bị/người bên cạnh khá nổi bật. Khung thử hẹp hơn vẫn dính thiết bị và cắt sát tay. Đề xuất tạm loại khỏi đợt nhập này; U/N là nhận xét nếu giữ, không phải crop đã đạt QA. Đối chiếu: NC-003. |
| G16-A02-F00027 | U/P → U/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Đầu cúi trong vùng bài, tay che mặt không phải looking_around P; đề xuất looking N. Phone giữ U vì vật trên bàn chưa đủ rõ để phân biệt. Đối chiếu: CB-0168. |
| G17-A01-F00012 | U/P → U/U | Tạm loại khỏi đợt nhập | Đề xuất sau đối chiếu — chờ owner chốt | Ngồi nghiêng không đủ chứng minh nhìn ngoài vùng bài; ảnh xa/mờ chưa tách chắc hướng đầu. Đề xuất tạm loại vì evidence yếu, không khẳng định ảnh làm giảm kết quả model. U/U chỉ lưu bất định, không phải nhãn để nhập. |
| G18-A01-F00001 | P/N → P/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Mặt lưng có cụm camera lớn với các thành phần tách được, không chỉ bóng đen trên một mặt phẳng. Giữ P/N từ ảnh này, không truyền sang người hoặc frame khác. Đối chiếu: CB-0024-R1. |
| G18-A02-F00007 | P/N → U/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Vật cầm nhỏ chỉ rõ dạng khối/cạnh, chưa có đặc trưng phân biệt phone với thiết bị khác. Đề xuất U/N. Đối chiếu: NC-003. |
| G18-A02-F00010 | P/P → U/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Ảnh này cũng chưa nhận diện được vật cầm; đề xuất phone U. Đầu quay ra ngoài vùng bài rõ hơn F00007, giữ looking P. Đối chiếu: NC-003. |
| G18-A03-F00001 | P/N → U/N | Giữ crop | Owner đã chốt nhãn | Owner chốt trong hội thoại ngày 17/10: F00001 là U/N; không lan nhãn looking từ F00010. Đối chiếu: NC-003. |
| G18-A03-F00010 | P/P → U/P | Giữ crop | Owner đã chốt nhãn | Owner xác nhận ngày 17/10: F00010 là U/P. Thiết bị chưa rõ nhưng đầu quay sang trái, ra khỏi vùng bài/thao tác. Quyết định này làm rõ dòng U/N chung trong README. Đối chiếu: NC-003. |
| G19-A01-F00039 | U/N → N/N | Giữ crop | Owner đã chốt nhãn | Owner chốt phone N vì tay/bàn rõ; looking N không bị nêu sửa nên giữ như bản gốc. |
| G19-A01-F00052 | U/P → N/P | Giữ crop | Owner đã chốt nhãn | Owner chốt phone N vì tay/bàn rõ; looking P không bị nêu sửa nên giữ như bản gốc. |
| G20-A02-F00001 | P/P → U/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Vật cầm ngang tối màu, chi tiết góc nhỏ chưa phân biệt chắc camera hay dấu trên vỏ. Đề xuất phone U; giữ looking P theo đầu quay ra ngoài vùng thao tác. Đối chiếu: CB-0024-R1, NC-003. |
| G20-A02-F00020 | P/N → U/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Mặt lưng tối và chi tiết sáng nhỏ chưa đủ nhận diện độc lập ở input; không lấy kết luận vật từ F00001. Đề xuất U/N. Đối chiếu: CB-0024-R1, NC-003. |
| G20-A03-F00073 | P/N → P/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Các vòng ống kính lớn tách biệt trên mặt lưng sáng vẫn thấy ở input; đủ hơn một mặt lưng trơn hoặc chấm nhòe. Giữ P/N. Đối chiếu: CB-0024-R1. |
| G21-A01-F00007 | U/P → N/P | Giữ crop | Owner đã chốt nhãn | Theo owner chốt N/P. Vật nâu có dạng gấp/mềm, không cần khẳng định chính xác là bìa hay ví để ghi nhận không phải thiết bị gây nhiễu trong crop này. |
| G22-A01-F00013-R02 | U/N → N/N | Giữ crop | Owner đã chốt nhãn | Theo owner: khoanh một tay, phần tay/bàn rõ và không có vật mơ hồ; chốt N/N. |
| G23-A03-F00009 | N/N → N/N | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Quan sát bút, trang/vật liệu giấy và tay, không có mặt thiết bị chưa rõ trong tay anchor. Giữ N/N; không gán unknown chỉ vì có vật đang cầm. Đối chiếu: NC-009. |
| G27-A01-F00016-R02 | U/P → N/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Tay khoanh có hình học rõ, phần bàn/tay còn lại không có vật mơ hồ. Đề xuất phone N; giữ looking P. Không mở rộng thành mọi crop khoanh tay đều N. Đối chiếu: NB-0013, NB-0015. |
| G27-A02-F00022 | U/P → U/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Phone nhìn thấy trên bàn phía sau/bên phải anchor nhưng chưa rõ vùng hoạt động thuộc anchor trong cảnh bàn dùng chung, không có tương tác. Crop chỉ còn một người nổi bật không tạo thêm evidence attribution. Giữ U/P; không khẳng định phone thuộc người khác. |
| G27-A03-F00031 | U/P → U/P | Giữ crop | Đề xuất sau đối chiếu — chờ owner chốt | Phone rõ ở phía trái mặt bàn trước anchor đứng, nhưng bàn dùng chung và không thấy tương tác hoặc vùng bài riêng. Chưa đủ chốt P/N cho anchor; giữ U/P. Không cắt bỏ phone chỉ để biến thành negative. |

## Bảo toàn và bước tiếp theo

README có nhận xét, 100 crop gốc, metadata batch và V10 được giữ nguyên. Revision G06 dùng ROI nguồn nguyên pixel, không chỉnh nội dung ảnh; proposal mới còn review_only, owner_approved false, canonical masks [0, 0], split null. Khung người chỉ bao phần cơ thể nhìn thấy; không bắt buộc lấy phần chân đã bị bàn che. Gallery giữ thứ tự video/anchor và cho xem khung cũ cạnh R02.

28 kết luận đề xuất cần owner nghiệm thu theo quy trình của repo; không yêu cầu duyệt lại 72 ID đã chốt. Chưa đóng nguồn video là “đã lấy đủ crop”: đợt bổ sung chờ danh sách owner gửi sau. Mapping lớp/buổi vẫn chưa có, giữ nhóm theo video. Near-duplicate/family và enrollment là bước riêng, không được coi exact SHA khác nhau là bằng chứng độc lập.

Kiểm tra kỹ thuật được lưu tại [validation](owner-review-validation-20261017.json): coverage 100 ID; SHA crop/input/source gốc; snapshot README; nhãn và split train của 33 comparator; ROI/input parity của G06 R02; tham chiếu HTML local. Kiểm tra phần mềm không thay owner acceptance.

Worksheet tạo companion: `finalize_owner_review.py`; `review_owner.py` chỉ dựng scope/board từ snapshot và dừng nếu README đã đổi. Không chạy lại worksheet batch gốc để áp dụng nhãn mới. Các khung thử không được chọn chỉ là evidence thử geometry, không thuộc 98 crop đề xuất.
