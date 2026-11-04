# Chốt audit V12 và ảnh bổ sung — 23/10/2026

**Đã áp quyết định cuối và hoàn thành snapshot audit. Chưa phát hành dataset mới.** Owner duyệt phần còn lại của README sau hai chỉnh nhãn và bảy quyết định loại. Approval này chốt nội dung audit đã trình bày; không tự cấp split, quyền nguồn chưa xác minh hoặc nghiệm thu package release.

## Kết quả hiện hành

| Hạng mục | Kết quả |
|---|---:|
| Crop cũ giữ sau audit | 1.156 |
| Ảnh mới giữ, gồm NEW-069 thay thế | 149 |
| Tổng crop đã chốt nhãn | **1.305** |
| Nhóm liên quan sau lọc membership | 331 |
| Crop cũ bị loại trong cohort 1.639 | 483 |
| Ảnh mới bị loại trong 156 ID | 7 |
| Trùng bytes / pixel RGB trong candidate | 0 / 0 |

G11-B09-F00008 và G5-A11-F047 chốt **U/N**. Loại EXP-SCB-030, V6-CA-034, V6R2-MP-017, G2-A09-F001, SCB-write-015, V6-EX-038, V7-C-001-R03. Mọi quyết định batch 01–04 và xác nhận chat còn lại đã hợp nhất. E004-EX-C184 là N/N, không có ngoại lệ. NEW-069 dùng ảnh calculator thay thế, N/N; ảnh phone cũ không là candidate. NEW-070 vẫn P/N.

“121 crop” trong bảng policy cũ là số crop đã rà, không phải số crop đều đổi sang N. Các snapshot ban đầu và checkpoint cũ không còn là nguồn trạng thái hiện hành.

## Artifact dùng tiếp

- [Inventory audit hợp nhất](candidate-final-audit.json): ID, crop SHA/path, kích thước, person/context box, nhãn, value/mask, nhóm và blocker. Đây là inventory audit, **không phải PilotRecord hoặc manifest release**; chưa gán split.
- [Quyết định cohort cũ](reconciled-review-final.json), [nhãn ảnh mới](additional-annotations-r7.json), [geometry ảnh mới](additional-geometry-r6.json), [geometry 53 recrop](old-recrop-geometry-draft-r2.json). Snapshot dự thảo giữ nguyên tên/bytes; approval cuối của owner áp trong snapshot hợp nhất, không sửa ngược bằng chứng đã review.
- [Nhóm audit](leakage-groups-final-audit.json), [lineage thị giác](additional-lineage-r3.json). Các ID bị loại chỉ có thể còn trong quan hệ nguồn; không còn là thành viên candidate. Cùng họ cảnh/biến thể phải cùng ranh giới split.
- [Checks cuối](final-audit-checks.json), [pins tiếp nhận](inputs.json), [policy áp dụng](owner-policy-20261023.md).
- [Kế hoạch chuẩn bị release](release-preparation-plan.md).

## QA và phạm vi kết luận

Đã kiểm 1.305 crop khớp SHA/decode, bounds person/context hợp lệ, mỗi ID thuộc đúng một nhóm và masks đúng P/N/U; không trùng bytes/RGB. Ledger accepted V12 giữ nguyên pin. 53 recrop đã kiểm pixel ROI ở vòng trước; 12 khung người đã chỉnh sau đổi tọa độ và được xem lại. Ảnh thay NEW-069 đã kiểm native/input 224.

Kiểm gần trùng đã xem 91 cặp ban đầu, 153 cặp mở rộng, các cặp chi tiết và tám nearest của ảnh thay thế. Đã áp lựa chọn giữ/loại owner chốt, gồm giữ NEW-012/056 thay crop cũ tương ứng và giữ CB-0405 thay NEW-052. Không coi hash hay shortlist là chứng minh tuyệt đối rằng không còn mọi dạng ảnh tương tự.

## Giới hạn cần xử lý trong bước release

- **21 ảnh đang giữ thuộc 8 họ cảnh chưa xác minh crop nguồn cũ.** Con số 22 trong lineage là toàn bộ 156 ID, gồm NEW-150 đã loại. Không bịa parent/recipe. Theo data contract, chưa đủ evidence thì quarantine ngoài train/val/test cho đến khi xác minh; owner chốt nhãn không tự khép provenance.
- **V6-EX-003 U/U** không có target dùng cho supervision. Giữ nhãn owner đã duyệt trong hồ sơ audit; không đưa vào used manifest, không tự đổi U thành N.
- Còn **1.283 crop không có hai blocker trên**; đây chưa là số release được duyệt vì còn mapping quyền sử dụng, record schema và allocation.
- 11 test cũ đã được mở visual audit trong đợt này; SCB-write-015 bị owner loại. Release mới cần report delta, không gọi tập còn lại là holdout độc lập hoặc tái sử dụng protocol test cũ mà không có quyết định.

Không train, inference, upload, commit hoặc sửa release V12. Crop bị loại không đưa vào payload release mới; hồ sơ audit và inputs đang làm bằng chứng được giữ local.
