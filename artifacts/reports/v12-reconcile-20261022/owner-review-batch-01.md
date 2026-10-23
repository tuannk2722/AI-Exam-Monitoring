# Batch 01 — Các ca cần đối chiếu với owner

Đây là đề xuất sau kiểm ảnh, chưa là quyết định thay nhãn. Thứ tự nhãn **Phone / Looking**.
Viền cam ở ảnh đối chiếu chỉ anchor hiện hành; ảnh gốc không có viền.
Trả lời theo Q01–Q09, ví dụ `Q01: đồng ý N/N`; nếu giữ nhãn hiện tại, ghi cue giúp phân biệt.

## Nhãn: ảnh đối chiếu 01

![Bốn crop và nhãn hiện hành](../../../data/interim/v12-reconcile-20261022/boards/questions-01.png)

| Câu | ID | Hiện hành sau merge | Quan sát và đề xuất cần chốt | Kết quả review của owner |
|---|---|---|---|---|
| Q01 | E004-CF-C011 | N/P, kế thừa | Anchor cúi viết, hướng về trang giấy; tôi chưa thấy quay sang người khác. Đề xuất **N/N**. | Crop này có khiến AI nhầm lẫn không? Vì đó thực ra là đang quay đầu về sau nhưng do quá nhiều tóc dẫn đến việc không thấy được đầu hay mặt đâu. Cái này cần xem xét nếu đưa vào có gây hại không, nếu có thì loại giúp tôi (ảnh tôi sẽ gửi ở khung chat) |
| Q02 | EXP-SCB-045 | U/N, Looking do owner đổi | Đầu có vẻ quay ngang về phía sau ghế trong khi thân hướng bàn. Đề xuất **U/P**; ảnh tối nên cần anh xác nhận hướng quay. | Loại crop này đi giúp tôi |
| Q03 | EXP-SCB-021 | N/P, kế thừa | Anchor cúi viết trên bài trước mặt; khác frame V7-C-007-R03 quay sang bên. Đề xuất **N/N**. | Không phải đang cúi viết mà là quay sang bên tay phải của target anchor. Nhưng nếu cái này cũng gây ảnh hưởng sấu thì loại đi giúp tôi |
| Q04 | V7-OE-S106-A01 | P/N, owner đổi | Vật ngang có vẻ là tablet, lớn so với bàn tay. Contract hiện hành chỉ mobile phone. Đề xuất **U/N** nếu chưa xác định thiết bị; **N/N** nếu anh xác nhận tablet và không có phone khác. Anh nhận diện vật này là gì? | N/N |

## Thiết bị và một cặp trùng: ảnh đối chiếu 02

![Thiết bị và cặp cùng anchor](../../../data/interim/v12-reconcile-20261022/boards/questions-02.png)

| Câu | ID | Hiện hành | Quan sát và đề xuất cần chốt | Kết quả review của owner |
|---|---|---|---|---|
| Q05 | NB-0003 | N/N, owner đổi | Mặt sau vật trắng không có cue phone đủ rõ; có thể là nắp/máy tính. Tôi chưa xác nhận được N chỉ từ ảnh này. Đề xuất **U/N**, hoặc giữ N/N nếu anh nhận diện được máy tính và chỉ rõ cue. | đằng sau phẳng và mượt như vậy chỉ có thể là calculator thôi, phone thì phải có lỗ camera. Vậy nên hãy dựa theo định nghĩa này mà phân tích các crop tương tự để đồng bộ và chuẩn xác nhất |
| Q06 | NB-0007 | N/N, owner đổi | Vật hồng nhìn chủ yếu từ cạnh/mặt sau, chưa đủ phân biệt phone và máy tính. Đề xuất **U/N**, hoặc giữ N/N nếu anh xác nhận được máy tính. |tôi dựa vào phần cạnh trên của calculator, bạn hãy nghiên cứu kỹ |
| Q07 | P019-person-01 và V6-EX-011 | P/N và P/U | Cùng ảnh/cùng người, khác biên crop và nén; source SHA và leakage group hiện khác nhau. Đề xuất **giữ P019-person-01 P/N, loại V6-EX-011 khỏi release mới**, giữ mapping trùng trong evidence. Cần thống nhất lineage trước split, không chỉ xóa một file. | Approve |

**Kết luận chung của owner**: nếu như Q05 và Q06 tôi đang nhận diện quá theo hướng mắt người và khinh nghiệm quan sát từ đó dẫn tới model bị kém thì hãy sửa lại sao cho phù hợp nhất. cái tôi cần nhất vẫn là khi đưa vào train thì những crop đó phải phù hợp chứ không phải theo mắt nhìn của tôi. **nên bạn hãy nghiên cứu thật kỹ 2 crop này, tôi nhớ là có khá nhiều crop tương tự như vậy nên một khi đã chốt được hai cái này rồi thì toàn bộ những crop tương tự phải tuân theo (đây là phần cực kỳ quan trọng)**

## Hai cặp gần trùng: ảnh đối chiếu 03

![Hai cặp gần trùng](../../../data/interim/v12-reconcile-20261022/boards/questions-03.png)

| Câu | ID | Hiện hành | Quan sát và đề xuất cần chốt | Kết quả review của owner |
|---|---|---|---|---|
| Q08 | V6R2-MP-006 và V6R2-MP-054 | U/N và U/U | Cùng cảnh/cùng anchor, hầu như cùng pose; khác crop/nén, đang có leakage group khác nhau. Đề xuất **giữ MP-006 U/N, loại MP-054 khỏi release mới** và nối lineage; không tuyên bố byte-identical. | Approve |
| Q09 | V6R2-CA-016 và V6-CA-044 | P/N và P/U | Cùng anchor/cảnh, pose và bằng chứng phone trên sách gần như lặp lại. Đề xuất **giữ V6R2-CA-016 P/N, loại V6-CA-044 khỏi release mới**. | Approve |

V12 gốc giữ nguyên. Chỉ loại khỏi membership/payload của bản tương lai sau chốt;
evidence mapping vẫn cần để không nhập lại bản lặp hoặc tách family khi chia tập.
Batch này không đại diện kết luận audit toàn bộ; phần còn lại chưa hoàn tất.
