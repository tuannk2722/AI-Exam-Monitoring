# Release V13 — 23/10/2026

**Đã đóng release local `pilot-b-20261023-v13` theo owner approval.** Package: `data/processed/pilot-b/pilot-b-20261023-v13`. Dataset dùng tiếp là V13; V12 và experiment pins lịch sử giữ nguyên.

| Phần | Số crop |
|---|---:|
| Train | 1.119 |
| Validation/development | 185 |
| Test | 0 |
| Tổng ledger/manifest/payload | **1.304** |

Chỉ giữ crop được sử dụng. V6-EX-003 và mọi crop đã loại không có trong payload; dùng đủ 21 ảnh generated owner duyệt, không quarantine. NEW-069 là ảnh calculator thay thế N/N; E004-EX-C184 N/N. Nhãn/geometry theo audit cuối; U giữ null/mask 0. Work context để unknown khi chưa có review riêng, không suy N/N thành confirmed_normal.

## Locator và bằng chứng

- [Package pointer và checksum](package-pointers.json), [owner approval](owner-release-approval.json), [config](../../../configs/datasets/pilot-b-20261023-v13.json).
- [Export/rebuild validation](package-validation.json), [loader và V12 preservation](loader-and-parent-checks.json), [delta so với parent](parent-delta.json).
- [Allocation owner duyệt](../v12-reconcile-20261022/allocation-approved.json), [inventory audit](../v12-reconcile-20261022/candidate-final-audit-r2.json), [nguồn upstream và lineage](../v12-reconcile-20261022/candidate-source-provenance.json), [policy revision](../v12-reconcile-20261022/owner-policy-20261023.md).
- [Source roots phục vụ rebuild](source-roots.json); bundle nguồn crop đã review nằm ở `data/interim/v13-release-preparation-20261023/reviewed-crop-inputs.zip`. Không gọi bundle này là ảnh camera gốc hoặc recipe AI đã xác minh.

## Validation và giới hạn

Exporter chuẩn kiểm strict schema, source/crop pixel parity, exact ID set, SHA và integrity. Accepted rebuild đảo thứ tự records vẫn có cùng checksums. Loader kiểm membership/split/encoding, 1.119 train và 185 val, target/mask shape 1.304 × 2. V12 ledger nguyên pin. Nhánh loader zero-test có regression riêng; guards freeze/preservation cũ giữ nguyên.

Không có nhóm đã xác định nào trộn split. Tuy nhiên 21 ảnh generated chỉ được owner xác nhận nguồn ở cấp cohort, chưa có exact parent ID; không chứng minh độc lập nguồn giữa train/val. Validation là development, **không phải independent holdout**. Năm test lịch sử đã audit chuyển sang val; các test cũ bị loại được ghi trong parent delta. Holdout mới cần nguồn/protocol riêng sau.

Phạm vi quyền: `local_classifier_research`. Không upload hoặc train/inference trong task release. Locator local không chứng minh remote backup. Không sửa release cũ hoặc experiment configs để trỏ ngầm sang V13.
