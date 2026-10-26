# Audit hình học D2 — 26/10/2026

Owner đã duyệt thực hiện duplicate-design.md trong hội thoại. Approval cho hướng audit/đối chứng; chưa định nghĩa rule số hoặc box giữ. Giữ thiết kế đã pin, D2/G0, nhãn review r2 và mọi người diagnostic với role unknown.

## Kết quả

[Config audit](../../../configs/runtime/RUNTIME-D2-RECONCILE-20261026/pair-audit.yaml) pin detections float, cohort, run/checksums, review r2 và design. [Audit](../../../outputs/runtime-d2-pair-audit-20261026/audit.json) và [2.917 cặp](../../../outputs/runtime-d2-pair-audit-20261026/pairs.csv) gồm toàn bộ cặp trong từng frame của 19 frame D2; 259 cặp giao nhau. Không inference hoặc suppression.

| Cặp owner xác nhận cùng người | IoU | Diện tích giao / box nhỏ |
|---|---:|---:|
| C01, 23 giây, b015/b016 | 0,280610 | 1,000000 |
| C02, 36 giây, b014/b015 | 0,125823 | 0,298399 |

C01 là containment hoàn toàn nhưng C02 không phải. Rule chỉ loại box lồng hoàn toàn không giải quyết cả hai. Có 54 cặp unknown có IoU ít nhất bằng C02: hạ ngưỡng tới mức này tạo nhiều ứng viên cần kiểm, chưa chứng minh chúng khác người hoặc sẽ bị NMS loại thực tế (NMS còn phụ thuộc thứ tự). Không chọn ngưỡng từ hai positive này.

## Batch đối chứng đã được owner review

[Gallery P01–P06](../../../outputs/runtime-d2-pair-controls-20261026/index.html), [config](../../../configs/runtime/RUNTIME-D2-RECONCILE-20261026/controls-batch.yaml). Chọn xác định: 5 cặp unknown có IoU cao nhất và 1 cặp unknown có giao/box nhỏ cao nhất. Đây là shortlist hình học, chưa gọi là negative accepted; không đại diện thống kê toàn video. Gallery liên kết source/overlay/crop/input gốc, không sao chép media; scores ẩn sau details.

Owner đã làm rõ P04/P06 cùng người, P01/P02/P03/P05 khác người. [Receipt review](pair-owner-review-20261026-r1.json) pin exact batch/gallery/config/bảng hình học; sửa cách hiểu P07 trong phản hồi trước thành P06. Gallery và audit gốc giữ nguyên trạng thái lịch sử; receipt này là nguồn quan hệ accepted mới. Không gán thêm nhãn hành vi hoặc box giữ.

| Case | Quan hệ accepted | IoU | Giao / box nhỏ |
|---|---|---:|---:|
| P01 | Khác người | 0,299967 | 0,516861 |
| P02 | Khác người | 0,299949 | 0,712652 |
| P03 | Khác người | 0,299236 | 0,516096 |
| P04 | Cùng người | 0,276874 | 0,572640 |
| P05 | Khác người | 0,275975 | 0,497560 |
| P06 | Cùng người | 0,222368 | 1,000000 |

## Kết luận và bước tiếp theo

Kết hợp C01/C02: 4 cặp cùng người và 4 cặp khác người đã review. Một rule pairwise dạng IoU >= t để bắt cả C02 (0,125823) cũng đánh dấu cả 4 cặp khác người. Tương tự, rule giao/box nhỏ >= t để bắt C02 (0,298399) cũng đánh dấu cả 4 cặp khác người. Đây là kiểm tra khả năng phân biệt của rule pairwise, không phải kết quả chạy NMS hoặc số người thực tế bị mất.

Containment hoàn toàn phù hợp C01/P06 trên shortlist này nhưng bỏ sót C02/P04. Chưa có đối chứng khác người lồng hoàn toàn được review, nên chưa đủ evidence để kết luận rule này an toàn ngoài shortlist. Không khẳng định mọi tổ hợp hình học đều bất khả thi; cũng không fit nhiều điều kiện riêng để vừa 8 cặp.

Đề xuất chuyển bước thiết kế sang xác minh cùng người bằng evidence hình ảnh ở vùng đầu/thân và vị trí anchor, dùng hình học để đề xuất cặp. Cần tách quyết định cùng người khỏi quyết định chọn crop: crop rộng có thể chứa thiết bị của hàng xóm như C01. Mục tiêu của thiết kế tiếp là có điều kiện giữ cả hai khi chưa rõ, kiểm bảo toàn 4 cặp khác người, và QA đầu/tay/bàn cho 4 cặp cùng người. Chưa chọn model/refinement, ngưỡng, nguồn pretrained hoặc thêm inference; các biến này cần proposal cụ thể theo duplicate-design đã duyệt. Chưa áp dụng suppression, đổi D2/G0 hoặc mở tracking/events.


## Kiểm tra và lifecycle

3 unit tests hình học PASS, Ruff phần mới PASS, strict mypy 65 source files PASS. Gallery builder kiểm input pins, source/crop/input/overlay pins và deadline khi tạo. Media giữ deadline nguồn 01/11/2026 15:55 giờ Việt Nam. Không sửa sealed output hoặc stage/commit. Software checks không thay owner acceptance.

Review lần này: kiểm checksum gallery và mapping đủ 6 case PASS; JSON receipt và diff được kiểm. Chỉ metadata/docs, không chạy lại ML tests hoặc inference.

## Bàn giao thiết kế visual refinement

Owner approve tiếp tục; đã chuẩn bị [thiết kế companion](../../../configs/runtime/RUNTIME-D2-RECONCILE-20261026/visual-refinement-design.md) và [gallery crop keeper](../../../outputs/runtime-d2-keeper-review-20261026/index.html), giữ mã C01/C02/P04/P06. Chỉ hỏi lựa chọn crop/evidence, không hỏi lại quan hệ accepted. Code hiện có chưa có head/pose/pair verifier; tài liệu tách rõ human reference và candidate tự động chưa chọn model. Kiểm 4 case/8 anchors, checksum output và tất cả gallery links PASS. Không inference hoặc sửa runtime code.

## Crop keeper đã được owner chốt

[Receipt keeper](keeper-owner-review-20261026-r1.json) pin batch/config và từng crop/input. Owner ghi C04/C06 nhưng exact anchor ID khớp duy nhất P04/P06 trong keeper batch; giữ nguyên lời ghi và mapping, không ảnh hưởng C04/C06 ở exception batch cũ.

| Case chuẩn | Keeper accepted |
|---|---|
| C01 | f00000690-D2-b015 |
| C02 | f00001080-D2-b015 |
| P04 | f00001680-D2-b009 |
| P06 | f00000780-D2-b015 |

Đã đủ reference lựa chọn crop cho 4 cặp same. Đây là lựa chọn trên các cặp cụ thể, không là quy tắc chọn box tổng quát hoặc nghiệm thu classifier attribution. Không áp dụng suppression hoặc đổi nhãn hành vi. Bước còn lại là proposal candidate verifier có model/source/license/variables rõ, abstain khi unknown và đối chứng 4 different cùng các keeper này trước tích hợp. Kiểm checksum batch, mapping duy nhất và 8 hashes crop/input PASS; không inference.
