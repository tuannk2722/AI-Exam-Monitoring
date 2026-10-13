# E004 — Hợp nhất V9 sau review owner

**V9 local Accepted**, đã dựng và tái lập byte-identical tại `data/processed/pilot-b/pilot-b-20261013-v9`. Đã nhập toàn bộ review mới và nghiệm thu 16 ngoại lệ/7 recrop. [Owner direction và waiver](owner-direction.json), [nghiệm thu ngoại lệ](owner-exception-approval.json), [review](REVIEW.md), [membership](membership-lineage.json), [config](../../../configs/datasets/pilot_b_release_v9.yaml).

## Membership đã hợp nhất

Master ledger có **1.208 records**: **716 train / 49 val / 11 test / 403 review-only / 29 excluded**. Kế thừa 927 records V8, bổ sung 281 records chưa có trong V8 từ các đợt CN/SX/CF/EX. Tổng 308 anchors của các đợt review được đại diện đúng một lần; 27 đã nằm trong V8 không cộng lại. Không gộp ngẫu nhiên các version/split cũ.

Trong 403 review-only: 122 inherited từ parent; 71 development; 199 reserve holdout; 4 train candidates cũ chưa có assignment/group/context acceptance đầy đủ; 7 U/U auxiliary. Những mẫu chưa đủ evidence giữ review-only, không biến unknown thành negative hoặc tự gán train/test. [Vai trò và family](role-membership.json), [coverage theo vai trò](coverage-by-reserved-role.json).

| Cohort reservation | Crop | Phone P / N / U | Looking P / N / U |
|---|---:|---|---|
| Development | 71 | 27 / 33 / 11 | 28 / 38 / 5 |
| Reserve holdout | 199 | 78 / 88 / 33 | 75 / 116 / 8 |
| Train candidates chưa assignment | 4 | 2 / 0 / 2 | 2 / 2 / 0 |
| Auxiliary U/U | 7 | 0 / 0 / 7 | 0 / 0 / 7 |

## Review và bảo toàn

170 Approve và 13 cặp nhãn rõ đã nhập bằng strict importer; 16 ngoại lệ gồm C096 và 7 recrop đã được owner nghiệm thu tiếp. Toàn bộ 199 records EX có phiên bản nhãn mới nhất. Geometry revision dùng source bất biến, kiểm exact crop/input 224, có SHA riêng; originals và receipts cũ giữ nguyên. [Validation](validation.json), [183 quyết định rõ](owner-explicit-decisions.json), [16 quyết định ngoại lệ](owner-exception-decisions.json).

Parent V8 chỉ sửa nhãn train **E004-EX-C089: N/N → N/P** và evidence tương ứng trong V9. 926 parent records còn lại giữ semantic, chỉ đổi identity đóng gói. Toàn bộ source/crop hashes parent, val 49 và test 11 giữ nguyên. [Parent preservation](parent-preservation.json). Không xem ảnh test hoặc chạy inference; test chỉ hash/decode/copy theo protocol kế thừa.

## Quyết định và giới hạn

Owner đã miễn thiếu hụt so với quota support cũ. Điều kiện phải bù đủ 100 P/100 N của revision trước được thay ở phạm vi này; không dùng snapshot readiness cũ để tiếp tục chặn vì quota. Waiver không chứng minh independence, chất lượng model hoặc tính đại diện CCTV thi thật.

Development/reserve được hợp nhất trong release để quản lý, nhưng chưa là supervised val/test mới: role reservations và records review-only được giữ nguyên. Release không tự đóng protocol final-test/context/slices hoặc exact config E004; chưa train/smoke/test inference, upload, stage/commit. 4 train candidates cũ chưa đủ acceptance không được tự thăng thành train.

## Kiểm và vòng đời

Exporter chuẩn kiểm codec/source/crop pixels/rights/usage/serialization PASS; rebuild byte-identical 1.191 files, gồm 1.179 crop. Canonical loader PASS: 716 train / 49 val, chặn test thiếu protocol; V8 payload integrity PASS. [Build receipt](v9-build-receipt.json), [loader verification](loader-verification.json), [release pointer](v9-release-pointer.json). Backup/restore và cleanup được ghi bằng receipt riêng sau snapshot. Cùng ổ D không là off-device backup. Không thay production code/schema/spec trong task này.

Backup đã verify toàn bộ 2.988 paths và restore byte-identical 1.191 package files: [receipt](backup-receipt.json). Raw cache cần rebuild nằm trong archive, prefix ghi trong receipt. [Audit trùng](consolidation-overlap.json): không exact crop duplicate hoặc source SHA xung đột vai trò.

Bàn giao hoàn tất: scratch restore/rebuild/source cache đã xóa sau backup; giữ ảnh review và recrop là evidence. DVC local pointer đã tạo, không remote upload. Checker thường và diff whitespace PASS; strict Git delivery còn các files chưa stage của workspace, không stage/commit trong task này. [Delivery checks](delivery-checks.json).
