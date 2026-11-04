# Audit ZIP sáu lớp học — 18–19/10/2026

Đã xem **115/115 frame**, kiểm source/native/input 224 cho **116 geometry**, giữ **71 crop đề xuất**, không chọn **45 khung thử**. Batch **Draft, review-only**, chưa owner nghiệm thu crop/nhãn/membership. Đây không phải số người độc lập hoặc annotation detector đầy đủ.

**[Mở gallery](../../../data/interim/youtube-frame-audit-20261018/index.html)** · [ZIP crop/input/metadata](../../../data/interim/youtube-frame-audit-20261018/youtube-crop-proposals.zip) · [Ledger 71 crop](review-index.json) · [Validation](validation.json)

## Inputs và phạm vi

Owner yêu cầu audit local trong khi review riêng 836 crop R2, xác nhận toàn quyền sử dụng 6 video và gửi 6 ảnh đánh dấu. Scope là audit/crop local, chưa enrollment/split/train/upload. ZIP `youtube-crawl-accepted-frames.zip`: 6.654.750 bytes, SHA-256 `50156f90e3c7eefff8bdd5bc081a5781921fe76400ea2a7966442d3f09f56a62`; có 115 JPG và 8 metadata files. Manifest/hash/dimensions/CRC khớp, không exact-byte/RGB duplicate nội bộ.

“Accepted” trong ZIP là chọn frame nguồn, không phải crop/nhãn nghiệm thu. Summary upstream đề cập 646 frame, nhưng chỉ 115 có payload thuộc scope. Nguồn rộng 480–640 px; ảnh đánh dấu dùng ghép cảnh/vị trí, không làm pixel crop hoặc khôi phục chi tiết. Không tăng nét AI/inpaint. Raw ZIP, accepted V11, R1/R2 và E005 không sửa; test 11 không mở.

## Ghép folder và kết quả

Tham chiếu là hậu tố `-1.png` đến `-6.png` của tên file owner gửi, không phải thứ tự attachment trong chat.

| Nhóm | Folder nguồn | Tham chiếu | Frame | Crop |
|---|---|---:|---:|---:|
| Y01 | `95223b0df46c027a0dc4` | 1 — lớp rèm xanh, bốn góc | 44 | 26 |
| Y02 | `79e76713ba8a3a894dce` | 4 — hai dãy đối diện | 15 | 6 |
| Y03 | `30b8ff52d298e941f61a` | 5 — giáo viên áo caro | 11 | 15 |
| Y04 | `2227112d45d10d7e91b3` | 3 — nguồn 480 px | 14 | 9 |
| Y05 | `1f11900c922a248ef051` | 6 — áo khoác xanh | 16 | 8 |
| Y06 | `8648d6fd214427e930d6` | 2 — người đọc sách xanh | 15 | 7 |

[Mapping](reference-mapping.json) ghi vị trí và crop chọn/không chọn; gallery kèm ảnh đánh dấu gốc. ID A là vị trí review theo bàn/bố cục/trang phục cục bộ, **không phải nhận diện khuôn mặt hoặc track danh tính**. Đổi góc/che không chắc thì ghi giới hạn. Vị trí quay lưng tiền cảnh Y06 có dấu nhưng không có crop đạt; thiếu hướng mặt/tay/bàn, mapping sau pan chưa chắc.

[Ghi chú 115 frame](frame-notes.json) ghi tình huống, đổi tư thế và ca ngoài khung/che. Boards giữ nguồn ở kích thước native. Đây là ghi chú audit từng frame, **không phải ma trận tracking từng người ở mọi frame**. Vị trí ngoài dấu vẫn được xét, ví dụ Y01-A16. Marked không buộc có crop: vị trí giữa Y02 lẫn hai người; nhiều hàng xa Y04/Y05 không đủ rõ hướng.

## Tiêu chí và mức bù đắp dataset

Cơ sở đã đối chiếu: [data](../../../docs/data.md), [system](../../../docs/system.md), [rubric phone](../E004-device-consistency-20261015/rubric.md), [ngoại lệ occlusion](../E004-device-consistency-20261015/owner-direction.md), [98 crop đã chốt](../frame-crop-audit-20261016/OWNER-ACCEPTED-20261017.md), [172 crop đã chốt](../frame-crop-additional-20261017/README.md), [rubric R2](../v11-legacy-crop-audit-20261018/r2/RUBRIC.md), [E005](../e005-v11-adaptation-20261018/README.md), [coverage](../E004-targeted-coverage-20261014/README.md).

- Một anchor chính trội, đủ đầu/tay/vùng bài cần diễn giải target. Phần người khác ở mép/nền không được cạnh tranh attribution. Thu hẹp mất evidence thì U hoặc không chọn.
- Phone P cần đặc trưng mobile trong chính crop/input, đúng bàn/tay. N cần đủ absence theo semantics đã duyệt; tay mất/vật mơ hồ không thành N. Không truyền nhãn từ frame khác.
- Looking dựa hướng đầu/vùng bài; nghiêng nhẹ không tự P, cầm bút không tự N. Thiếu đích/context giữ U. Nhìn người nói trong lớp có thể P theo semantics, không là kết luận gian lận.
- Phân bố: **18 U/N, 7 P/N, 11 N/N, 9 N/P, 1 P/U, 1 P/P, 24 U/P**. Canonical targets toàn batch vẫn null/mask 0.
- **9 phone P đều ở Y01**, chủ yếu trên bàn; A10/A21 có cấu trúc mặt sau/camera. Đã xem riêng input phone P; A18 chuyển U vì vật tối không đủ đặc trưng.
- Batch thêm đối chứng nhìn bài/ngoài bài và absence/occlusion. **Chưa chứng minh bù đủ điểm yếu E005**, chưa có phone P đa dạng ở lớp quay cao hoặc calculator negative rõ để tuyên bố giải quyết nhầm thiết bị. Không đo gain model/đặt quota mới.

## Lineage và giới hạn

[Lineage](lineage-review.json): không exact SHA/RGB trùng với 536 frame audit ngày 16/10. Đã xem `P03-G17-F00012` và Y05: phòng/góc máy/cửa sổ/rèm/bàn giáo viên rất gần. Cần quarantine scene-family tiềm năng trước split, không coi 6 folder là 6 nguồn độc lập. Y03/Y05 có cờ tương đồng bố cục cần kiểm thêm. Chưa kiểm toàn bộ lịch sử nguồn V11 hoặc chứng minh independent holdout.

Crop nhỏ có thể đủ hướng đầu/bài nhưng không đủ nhận vật nên phone U nhiều. State trong [khung không chọn](withheld.json) là giả thuyết trước QA, không là nhãn được giữ. Hai khung đứng Y01 thiếu work context bị bỏ; người đọc Y06 F1 dùng R02 bỏ chữ sát mép. Nhận xét Draft cần owner nghiệm thu batch/ngoại lệ.

## Kiểm tra và vòng đời

- [Inventory](inventory.json): CRC/membership 115 manifest/JPG, source SHA, decode/dimensions PASS; pin 6 ảnh tham chiếu.
- [Validation](validation.json): 115 notes / 116 trials / 71 đề xuất; bounds/containment, source/crop/input parity, SHA, unique crop hash, không U/U, canonical null/mask 0, 768 links và ZIP CRC/membership PASS.
- Tái dùng `source_review.write_pending_crop/preview_input`; **6/6 tests source_review PASS**. Worksheets không sửa production source/contract. Checks/pins cuối: [handoff](handoff-validation.json).
- HTML tĩnh/links đã kiểm, chưa kiểm browser render. Không model inference/training/test access.
- Giữ frames/references/candidates/boards làm evidence local. Dọn `trials` rời sau bảo toàn; dựng lại từ selections bằng render_trials. Media không Git/upload; chưa commit/push.
- Worksheets prepare/render_trials/finalize_observations/export_review điều phối inventory/quan sát/xuất gói; không chạy lại lên artifact đã accepted/pin ở revision sau.

Bước tiếp: owner review 71 crop/ngoại lệ; enrollment và assignment cần scope riêng.

## Kết quả review của owner

| ID | Kết quả | Chú thích |
|---|---|---|
| Y01-A09-F00037 | P/N | Điều chỉnh lại crop vì ở góc bàn có vật màu đen giống với phone, nên hãy cân nhắc xem crop có thể kéo tới đó không? và vật như vậy có gán phone P được không |
| Y01-A15-F00003 | P/P | Vật như vậy có thể coi là phone P được rồi |
| Y01-A18-F00043 | P/N | Vật như vậy có thể coi là phone P được rồi |
| Y01-A02-F00188 | N/P | Không bị che hay có vật gây nhiễu gì |
| Y03-A01-F00001 | N/P | Tay và bàn có thể quán sát rõ |
| Y03-A02-F00001 | N/N | Tay có thể quan sát rõ |
| Y03-A03-F00001 | N/N | Ảnh mờ nhưng vẫn quan sát được |
| Y03-A05-F00001 | U/N | Không quan sát được hết tay |
| Y03-A05-F00045 | U/P | Tay vẫn bị che |
| Y03-A06-F00001, Y03-A07-F00001, Y03-A08-F00001, Y03-A09-F00001, Y03-A13-F00001, Y03-A15-F00001, Y04-A02-F00022, Y04-A14-F00001 | N/N | Có thể quan sát rõ tay |
| Y03-A08-F00042, Y03-A09-F00024, Y04-A02-F00001, Y04-A10-F00001, Y05-A03-F00001, Y05-A07-F00001, | N/P | Có thể quan sát rõ tay |
| Y05-A07-F00033 | N/Xem xét | Đang nhìn vào tay ở trước mặt |
| Y06-A02-F00064 | N/N | Tay rõ ràng |
