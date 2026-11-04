# LIVE-TIMING-20261028 — Đề xuất policy thời gian online

Trạng thái: **Accepted cho implementation và fixtures**. Owner trả lời ngày
28/10/2026: “Duyệt policy để triển khai và kiểm bằng fixtures”, đúng phương án này.
Đây là phần còn mở của LIVE-DEMO-FOUNDATION-20261027, không thay acceptance
C10/offline events trên clip cũ. Scope mới: một camera hoặc file đang phát,
14 người / 10 phút là tải cần kiểm, chưa là SLA.

## Phương án đề nghị

| Phần | Policy đề nghị |
|---|---|
| Detector/tracker | Lịch mục tiêu 10 Hz, slot 100 ms theo source clock |
| Frame cho một slot | Frame đầu tiên tại/sau mốc slot, lệch tối đa 50 ms; mỗi frame chỉ dùng một slot |
| Clock | File giữ PTS gốc; camera dùng monotonic lúc backend nhận frame, không gọi là sensor timestamp |
| Metadata | Giữ cả slot index, mốc slot và timestamp thực; không sửa/làm tròn timestamp thật |
| Slot detector bị thiếu | Không gọi tracker bằng prediction cũ/empty giả; trước mẫu hợp lệ tiếp theo reset tracker và temporal chain, tăng continuity generation |
| Bỏ pending khi quá tải | Đếm slot thiếu, hiện degraded; không xếp hàng vô hạn hoặc che gaps |
| G0 | 1 Hz, chỉ dùng frame detector của mỗi slot thứ 10; snapshot anchors/track tại chính frame đó |
| Slot G0 bị thiếu | Đóng segment hành vi; tracker vẫn tiếp tục nếu detector đủ nhịp |
| Candidate | Ít nhất 3 positives ở các slot G0 liên tiếp và span timestamp thật ≥ 2.000 ms |
| Jitter làm span chưa đủ | Chờ positive tiếp theo; không nới 2.000 ms hoặc nhân đôi prediction |
| Negative/unknown/null track | Đóng segment tương ứng, không bridge hoặc gộp người |
| Pause | Không thêm support; đóng segment và reset continuity khi resume |
| Seek/đổi nguồn/mất nguồn | Epoch mới, loại late results và reset continuity; lịch sử evidence giữ identity cũ |

50 ms là nửa slot detector, đề xuất kỹ thuật ban đầu để dung nạp nguồn 25/30 FPS;
không phải số đã benchmark trên iPhone/Camo. Policy ưu tiên không nối nhầm người
qua khoảng mất mẫu. Đánh đổi: tracker có thể fragment và candidate ít hơn khi
máy không theo kịp; UI phải báo gaps, không tự nới tolerance hoặc giảm cadence.
Nếu phải đổi policy sau đo, tạo version/config mới và review riêng.

## Giữ nguyên thiết kế đã duyệt

- Bbox/nhãn chỉ ghép đúng frame/geometry/epoch. Chưa có label propagation/TTL.
- Quan sát tức thời khác ca cần review; log candidate cập nhật cùng ID khi kéo
  dài, không auto-confirm. Stable ID gồm session/epoch/continuity/track/behavior/
  segment; không coi track ID là danh tính người thật.
- Frame G0 chậm giữ snapshot tracker cũ; không tra track đang hiện hành để gán lại.
  Kết quả quá generation/epoch bị loại, không đảo thứ tự theo arrival time.
- Review giữ evidence revision đã xem. SQLite live/schema/wire/evidence budget
  thuộc slice riêng; approval numeric không tự migrate SQLite legacy.
- Quyền camera/retention riêng phải có trước capture người thật. Policy này chỉ
  mở implementation và synthetic/replay được phép sau duyệt; không cấp media,
  model run, chất lượng/SLA hoặc quyền thu/upload mới.

## Kiểm chứng trước bật log trên UI

Fixtures kiểm boundary 0/50/>50 ms, nguồn 25/30 FPS và timestamp bất quy tắc,
duplicate/out-of-order, skipped slots, chậm G0, pause/resume/seek, epoch/generation
và kết quả về muộn. Parity với offline chỉ trên chuỗi đúng grid 1 Hz, assignment
giống nhau; không dùng parity đó để gọi mọi stream có jitter là C10 Accepted.
Case thực máy không đủ nhịp phải báo degraded và đứt chuỗi đúng policy.

Variables thực thi ở [policy.yaml](policy.yaml). Primitives chỉ có metadata trong
RAM, chưa là schema event persistence hoặc evidence đã lưu. Phần nối camera,
tracker thật, vận chuyển log và SQLite live tiếp tục là slice tích hợp riêng.
