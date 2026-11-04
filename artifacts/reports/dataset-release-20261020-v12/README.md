# Release V12 — 20/10/2026

Package: `data/processed/pilot-b/pilot-b-20261020-v12`.
Owner đã chốt review và duyệt phân bổ mới. Release hoàn tất: exporter, loader và rebuild PASS;
kết quả ở `package-validation.json`. Không chạy lại worksheet vào package đã tồn tại.

## Phạm vi đã chốt

Chuỗi quyết định: audit legacy R1 → R2 và review 836 crop → audit YouTube 71 crop
→ hợp nhất/recrop/loại trùng và 41 ảnh bổ sung → review cuối của owner → V12.
R1 đã được R2 thay thế trong phạm vi audit; quyết định cuối ưu tiên review owner mới nhất.
Các báo cáo cũ và snapshot giữ nguyên để truy vết, không sửa trạng thái lịch sử thành approval mới.

- `owner-final-review.md`: snapshot 15 dòng ngoại lệ; crop không nhắc đến mặc định approved.
- `OWNER-DECISIONS.md`: yêu cầu release, xác nhận chỉ giữ EX027 và duyệt phân bổ cụ thể.
- `owner-crop-acceptance.json`: nhận xét được áp dụng đúng ID và crop SHA.
- `accepted-audit-cohort.json`: 681 crop đã chốt, gồm 591 crop từ cohort legacy và 90 crop YouTube.
- `allocation-proposal.json`: bảng assignment đã được owner duyệt qua receipt
  `owner-release-approval.json`; giữ nguyên bytes và chữ proposed của snapshot.

Giữ `V6-EX-027 N/P`; loại `V6-EX-022` và `V6R2-EX-010-R06`.
Ba đề xuất `V7-OE-S042-A01-R03`, `V7-PF-C-003-R03`, `V7-OE-S023-A01-R03`
bị owner loại, không đưa crop parent đã cần sửa trở lại supervision.
Các nhãn ngoại lệ mới được áp dụng theo review cuối, gồm N/U và P/P; U giữ null/mask 0.

## Thành phần

| Vai trò | Records | Ghi chú |
|---|---:|---|
| Train | 1.092 | 1.002 kế thừa sau audit + 90 YouTube mới |
| Validation | 204 | Giữ role parent của các mẫu còn lại |
| Test | 11 | Bảo toàn nội dung/evidence, không visual review hoặc inference |
| Review-only | 332 | Giữ ngoài supervision như V11 |
| Excluded | 418 | Gồm parent bị rút/thay thế; lưu lineage trong ledger |

Ledger 2.057 records; manifest supervision 1.307 records.
Không dùng glob thư mục crops làm train. Consumer phải đọc manifest, lọc role và giữ masks.
987 records ngoài cohort legacy được bảo toàn, ngoại trừ các trường version của package.
Recrop có ID/SHA và evidence mới; bản cũ bị thay thế được đánh dấu excluded, không xóa khỏi lịch sử.

## Split, lineage và mức hỗ trợ

Giữ split V11 cho mẫu kế thừa; không chia random lại sau sửa nhãn.
90 crop YouTube vào train, cùng video không đi qua train/validation.
Y03/Y05 được gom nhóm bảo thủ cùng cờ scene-family G17; G17 không có record trong V11.
Đã sàng lọc nguồn mới với nguồn V11 ngoài test và xem 18 cặp gần nhất đại diện;
khác scene trong các cặp đã xem. Similarity chỉ hỗ trợ review, không chứng minh độc lập.

Validation có phone P/N/U = **35/94/75**, looking P/N/U = **65/139/0**.
Positive phone thuộc 25 groups, positive looking thuộc 40 groups:
đủ mức support tối thiểu đã chốt cho development validation.
Đây không phải bằng chứng model đạt precision/recall/FPR.

## Kiểm tra và bảo toàn

`package-validation.json` và `package-pointers.json` là kết quả kiểm package và checksum.
Exporter kiểm source/crop pixels, SHA, schema, masks, assignment và leakage;
loader kiểm inventory/payload/freeze. Rebuild phải có checksum byte-identical.
Test giữ source/crop/labels/masks/group/evidence/freeze reference; chỉ trường version thay đổi,
nên không gọi serialization test mới là byte-identical với V11.

V11, config/receipts và E005 giữ nguyên. Metrics E005 thuộc nhãn V11 cũ, không coi chênh lệch
trên V12 là gain trên cùng ground truth. Validation có lịch sử exposure từ model cũ,
không là holdout độc lập.

Nguồn cần recrop/export giữ tại `data/interim/dataset-release-20261020-v12/sources`;
`source-roots.json` là locator local, `source-restore.json` dẫn archive gốc đúng SHA.
Các package/source/evidence hiện hành được bảo toàn; chỉ dọn rebuild/cache tạm sau checks.
Không train/smoke/test inference/upload/commit trong task này.

## Bàn giao

- [Package pointers](package-pointers.json), [kiểm package](package-validation.json),
  [kiểm bàn giao](handoff-checks.json).
- [Bản lưu local](backup-receipt.json): 3.725 file đã restore và kiểm byte-exact PASS.
  Archive giữ snapshot tại thời điểm đóng gói; receipt và cập nhật bàn giao sau đó ở hồ sơ này.
  Bản lưu cùng ổ D, không phải backup ngoài thiết bị; không upload.
- 30 tests package/schema PASS; Ruff PASS; repository checker PASS trên Git index hiện có.
  Files mới chưa stage/commit; checker không chứng minh các files untracked đã được Git lưu.
- Scratch rebuild/restore được dọn sau xác minh; nguồn, package và evidence được giữ lại.