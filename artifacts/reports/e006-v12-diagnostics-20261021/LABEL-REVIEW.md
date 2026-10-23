# Bộ ví dụ nhãn và ngoại lệ cần chốt

**Draft minh họa contract hiện hành, chưa là approval nhãn mới.** Nhãn tham chiếu lấy từ accepted V12, không dùng tên lớp nguồn hoặc score model làm ground truth. Thứ tự `phone_use / looking_around`; P = positive, N = negative, U = unknown. U có mask 0 cho đúng target, không phải N.

Mở [gallery](../../../data/interim/e006-v12-diagnostics-20261021/index.html) trước; gallery cố ý không hiển thị nhãn/scores. Sau khi xem ảnh, dùng bảng này để đối chiếu. Mọi card có số thứ tự cố định, source/anchor/context, crop và input 224; đề xuất sửa phải gắn crop SHA ở [selection](review-selection.json).

## 1. Ví dụ chuẩn đề xuất giữ

| Khái niệm | Card / ID | Nhãn V12 | Cách áp dụng |
|---|---|---|---|
| Phone cầm rõ | 09 `V7-UNAPPROVED-C-003` | P/N | Có thiết bị rõ gắn đúng anchor; tên ID lịch sử không là trạng thái approval |
| Phone trên bàn | 07 `G06-A02-F00012` | P/N | Người đang viết vẫn phone P khi mobile trên bàn thuộc anchor; không yêu cầu đang chạm máy |
| Phone áp tai | 05 `V6R2-CA-001` | P/N | Tư thế sát tai chỉ có ý nghĩa khi nhìn thấy đúng thiết bị |
| Calculator trên bàn | 29 `G23-B01-F00003` | N/N | Phím/màn hình calculator không là mobile |
| Calculator cầm tay | 35 `NB-0006` | N/N | Cầm vật điện tử không tự tạo phone P |
| Laptop | 01 `V7-A-008` | N/N | Laptop không thuộc phone; cần đủ vùng quan sát để xác nhận N |
| Vật chưa phân loại được | 12 `E004-EX-C002-R04`, 30 `CB-0294` | U/N | Chỉ thấy cạnh/chi tiết mơ hồ: giữ U, không đoán từ dáng vật |
| Looking rõ ngoài vùng làm việc | 22 `E004-EX-C001` | P/P | Đầu/mắt và context cùng hỗ trợ; hai target có thể đồng thời P |
| Đọc sách dù đang đứng | 16 `E004-CN-048` | N/N | Tư thế đứng không là looking P; xét vùng đọc thực tế |
| Viết bài | 24 `E004-EX-C018`, 25 `V7-B-048` | N/N | Có context giấy/bút và hướng đầu phù hợp |
| Hướng nhìn không đủ quan sát | 36 `Y01-A12-F00098` | P/U | Đầu gục/che mặt; phone vẫn được supervision độc lập |
| Context hướng nhìn chưa rõ | 37 `NB-0038-R1` | N/U | Đầu nghiêng không đủ xác nhận đích nhìn |

Đây là ví dụ để thống nhất cách áp dụng, không là mẫu đại diện thống kê. Không suy score cao ở các controls là lý do giữ nhãn. Với ca hoàn toàn bị vật khác che, áp đúng ngoại lệ absence đã duyệt tại [data contract](../../../docs/data.md), không mở rộng thành mọi tay khuất đều N.

## 2. Bốn ngoại lệ cần owner trả lời

| Card / ID | Nhãn hiện tại | Đề xuất và câu hỏi cụ thể |
|---|---|---|
| 08 `G12-A01-F00053-R02` | P/N | Vật có phím vật lý giống calculator. Nếu owner xác nhận không có mobile khác và đủ vùng quan sát, đề xuất **N/N**; nếu không phân biệt chắc thì **U/N** |
| 14 `V7-D-009` | U/N | Điện thoại đen cầm rõ: đề xuất **P/N** |
| 18 `EXP-SCB-021` | N/P | Đích nhìn gần trang sách chưa rõ: đề xuất **N/U** nếu không đủ evidence; giữ N/P nếu owner chỉ ra evidence nhìn ngoài vùng bài; N/N chỉ khi đủ xác nhận đang nhìn bài |
| 19 `V7-C-075` | U/P | Thiếu context bài/đích nhìn, mắt gần khép: đề xuất **U/U**; nếu được chốt U/U thì ngoài supervision trong release mới, không xóa raw |

Có thể trả lời một batch: “Giữ bộ ví dụ; 08 = ..., 14 = ..., 18 = ..., 19 = ...”, kèm lý do cho khác đề xuất. Các dòng khác trong [visual review](VISUAL-REVIEW.md) đề xuất giữ accepted label. Chưa tạo receipt approval hoặc thay package trước câu trả lời.

## 3. Quy tắc chất lượng cần giữ khi review

- File/crop sai là lỗi dữ liệu; ảnh khó nhưng đủ evidence là dữ liệu cần giữ.
- Tách từng target: N/U hoặc P/U vẫn có supervision, U/U thì không.
- Review source → crop → input. Source rõ nhưng input mất cue là vấn đề biểu diễn cần ghi riêng, không tự biến P thành N.
- Phone của người bên cạnh không gán cho anchor. Unknown attribution giữ U.
- Nhìn ra phía trước/giáo viên ngoài vùng bài làm vẫn cần áp contract đang có; không suy sự gian lận từ P. Nếu muốn loại hành vi nghe giảng khỏi target thì đó là thay semantics cần quyết định riêng.
- Không dùng model disagreement để tự sửa nhãn; không lọc validation theo việc model đoán đúng/sai. Threshold và metrics hiện tại vẫn thuộc nhãn V12.
