# E004 — thống nhất phone/calculator sau review 247 crop

Đã kiểm lại **toàn bộ 247 crop** trong batch owner vừa review, gồm cả các dòng không có ghi chú; đối chiếu riêng **35 nhận xét**. Sửa nhãn Draft của **77 crop**: 70 thay đổi phone và 12 thay đổi looking, trong đó 5 crop đổi cả hai. Không sửa ảnh hoặc nhãn accepted cũ.

Mở [gallery trước/sau](../../../outputs/E004-device-consistency-20261015/index.html). Có bộ lọc **Nhãn thay đổi**, **Có nhận xét owner**, P/N/U và nhóm evidence; mỗi crop có input 224, context lấy từ source cùng frame, lý do riêng và link frame gốc. [Đối chiếu từng nhận xét](owner-resolution.md), [rubric](rubric.md), [bảng review mới](owner-review.md), [ledger 247](candidate-ledger.json).

## Quy tắc đã áp dụng

- **Chỉ mặt lưng/cạnh:** không nhận dạng được đặc trưng phân biệt thì U, bất kể đen/trắng/hồng/xanh hoặc cách cầm. Mặt sau có thể P nếu camera/đặc trưng mobile thật sự rõ; trong 33 crop thuộc nhóm BACK ở batch này, chưa có evidence đạt điều đó. Nếu cùng crop có phone khác rõ trên bàn thì vẫn P, nhưng phải chỉ rõ phone nào.
- **Mờ hoặc che một phần:** phần còn lại đủ nhận phone và attribution thì P; đủ nhận calculator/vật khác và review absence còn lại thì N; còn mảnh/vệt không phân biệt được thì U. Không đặt tỷ lệ che hay quy tắc “hơi mờ vẫn P” tùy cảm giác. Không dùng nhãn frame trước/sau để lấp evidence.
- **Calculator rõ không tự thành N:** CB-0604-R1 sửa N/N vì đủ hai tay/bàn; CB-0609-R1 giữ U/P vì tay vươn sang phải bị cắt khỏi crop, dù calculator rõ.
- **Vật che hoàn toàn có thể N:** áp [quyết định owner mới](owner-direction.md) cho CB-0571-R1 và G1-A02-F044. Ngoại lệ không áp cho tay dưới bàn/mất khỏi crop, vật còn lộ mơ hồ hoặc attribution chưa rõ. Không hồi tố V9 hay thay metrics cũ.

Ví dụ đối chiếu quan trọng:

| Crop | Trước → sau | Evidence quyết định |
|---|---|---|
| CB-0008 / CB-0017 / CB-0020-R1 | P → U cho phone | Lưng đen/nâu không có chi tiết nhận dạng; áp cùng chuẩn với lưng trắng |
| CB-0540-R1 | P/U → N/N | Calculator có phím, hai tay ở đầu; hướng đầu vào giấy còn rõ |
| CB-0593-R1 | U/N → U/N | Mảnh thiết bị còn lộ ở biên ảnh, không đủ P; cũng không bỏ qua thành N |
| G1-A01-F001 / F010 / F040 | U/N, U/P, U/P sau kiểm lại | Cả ba có phần thiết bị bị che, không đủ đặc trưng; sửa hai P cũ thay vì nâng U theo suy đoán |
| G1-A04-F042 | U/P → P/P | Mặt kính và viền phone trên giấy vẫn còn đủ rõ dù che một góc |
| G2-A02-F001 / F005 | Giữ U/N, U/P | Lưng trắng trơn; không suy loại từ màu hoặc cách cầm |
| G2-A06-F149 | P/P → U/P | Đốm sáng trên vật nhỏ sát thân không đủ nhận phone ở input |
| G5-A02-F001 / G5-A12-F047 | P/N → U/N | Calculator rõ hơn nhưng phần thiết bị khác chỉ lộ mảnh mờ |
| G4-A06-F105 | N/N → U/N | Có vật đen còn lộ trên sách, không đủ phân loại; không là absence |
| CB-0704 / CB-0710 / CB-0756 / CB-0764 | N → U cho phone | Tay dưới bàn hoặc mất khỏi crop |
| CB-0762 | U/N → N/N | Vật cầm có cấu trúc mềm/nếp, đủ loại phone; tay/bàn còn lại review được |
| CB-NEW-01 | P/P → U/N | Lưng/cạnh vật không đủ phone identity; nhìn vật trong tay ở vùng riêng không tự looking P |

CB-0673 và CB-0718-R1 không được đổi thẳng sang P/N theo một tư thế: hướng/đích nhìn còn mơ hồ nên looking U. Không chắc P không có nghĩa chắc N. Chi tiết và phản hồi đầy đủ trong owner-resolution, không chỉ bảng ví dụ này.

## Kết quả và phạm vi thực sự đã xem

| Target phone | P | N | U |
|---|---:|---:|---:|
| Trước | 130 | 27 | 90 |
| Sau | 78 | 30 | 139 |

Phone delta: **52 P → U**, 1 P → N, 9 U → N, 7 N → U, 1 U → P. Không ép số P tăng; đây là sửa evidence/annotation, chưa có accuracy model mới.

Nhãn sau: P/N 69, P/P 9, N/N 22, N/P 8, U/N 92, U/P 42, U/U 5. Giữ **242 ứng viên shortlist Draft**, đưa **5 U/U** sang withheld: CB-0601-R1, CB-0673, CB-0702, CB-0718-R1, G3-A05-F003. Vẫn thấy cả 247 trong gallery để không mất đối chiếu; tất cả hiện là review-only, chưa manifest supervision.

- Xem đủ 247 input tại 224 × 224 qua 16 bảng. Các crop này tham chiếu **123 frame nguồn khác nhau**, không phải 247 frame độc lập.
- Mở chi tiết context từ source cùng frame cho **145 crop** qua các bảng detail; xem toàn frame gốc thêm cho CB-0762/CB-0765 để kiểm vật dụng và attribution. Không tuyên bố đã mở toàn bộ 212 frame ở độ phân giải gốc trong vòng này.
- Kiểm chéo các nhóm P và N sau lượt đầu; phát hiện thêm CB-0294 chỉ lộ cạnh và CB-0653 chỉ lộ mảnh dưới tay, chuyển về U trước bàn giao. Ghi chú từng crop trong [manual-review](manual-review.txt); input/detail boards được liên kết trong ledger.
- Review toàn bộ 765 crop/212 frame của lượt trước vẫn là evidence lịch sử. **658 alternatives/withheld ngoài batch 247 chưa được xét lại bằng rubric mới**; không dùng nhãn cũ của chúng để bổ sung train. Nếu lấy lại phải review theo cùng tiêu chí.
- G5-A05-F109 và G5-A06-F099 có nhiều người nổi bật; xác định đúng anchor khi review, giữ cờ kiểm geometry trước package. Không coi phone U là đã giải quyết giới hạn classifier RGB không nhận anchor box.

## Tác động contract/codebase

Đã đối chiếu `AdaptationModel` (ResNet18, head hai output), loader letterbox và unknown mask. U không là lớp thứ ba; current classifier không xuất calculator và không tự có cơ chế phân biệt vật bị che. Audit này không sửa production code/model/input size/threshold, không train hoặc mở final test.

Chỉ bổ sung ngoại lệ absence mà owner vừa duyệt vào [data contract](../../../docs/data.md) và [decision registry](../../../docs/decisions.md), có scope forward revision. Phần phone mobile, attribution, looking và encoding giữ nguyên. Accepted releases, 11 pins kết quả refinement, ảnh gốc/crop/input giữ bytes; source review mới không tự làm release accepted.

## Kiểm tra và bàn giao

[Validation](validation.json) PASS: 247 ID duy nhất, 741 phép đối chiếu SHA source/crop/input, 247 input đúng kích thước, 11 pins upstream nguyên vẹn, đủ labels/reasons, U/U withheld, canonical targets null/mask 0 và split null. [Software validation](software-validation.json) ghi lint, AST, bộ lọc/tìm kiếm/phân trang JS, link checks, repo checker và render Chrome. Kiểm kỹ thuật không chứng minh nhãn là ground truth hoặc thay owner acceptance.

[Input pins](input-pins.json) pin ledger và snapshot review owner; [result pins](result-pins.json) pin revision. File owner-review.md mới được để ngoài pins để owner ghi chú; file owner đã viết ở revision trước được giữ nguyên. [Handoff pins](handoff-pins.json) bổ sung report/worksheet/evidence cuối. Media local ngoài Git, không upload/commit. Profile trình duyệt và Python cache tạm được dọn sau QA.

Worksheet `audit.py` chỉ vật hóa quyết định thủ công của batch này; không là annotator cho ảnh khác. `prepare`/`assemble` dành cho revision chưa pin, không chạy lại để ghi đè bản đã bàn giao hoặc review owner mới. `validate` kiểm integrity của phiên bản hiện tại. Mọi điều chỉnh nhãn sau pin phải tạo revision mới.

Phần audit được yêu cầu đã hoàn tất. Trước package train vẫn cần nghiệm thu batch/ngoại lệ, crop/person/context, lineage/membership và split đúng scope; không cần annotate lại 247 crop từ đầu. Gallery có lọc 77 thay đổi để đối chiếu tập trung.
