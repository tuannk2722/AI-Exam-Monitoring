# Release dataset V11 — 17/10/2026

**Package mới: `data/processed/pilot-b/pilot-b-20261017-v11`.** Đây là release từ phân bổ và 270 crop đã được owner nghiệm thu; không phải một thiết kế hoặc lần chạy train. Việc đóng gói bắt đầu ngày 17/10 và kiểm bàn giao hoàn tất sau nửa đêm 18/10; identity release giữ ngày bắt đầu.

## Thành phần và quyền sử dụng

| Vai trò | Số crop | Nhóm | Ghi chú |
|---|---:|---:|---|
| Train | 1.185 | 274 | 196 crop mới |
| Validation | 266 | 155 | 74 crop mới; development validation |
| Test cũ | 11 | 3 | Giữ đóng; không inference hoặc tuning |
| Review-only | 332 | — | Ngoài manifest supervision |
| Excluded | 29 | — | Ngoài manifest supervision |

Ledger có **1.823 records**; manifest có **1.462 records**, gồm train/val/test. Thư mục crops giữ 1.794 ảnh đã review, bao gồm review-only; **không đọc cả thư mục crops làm tập train**. Consumer phải đọc manifest và lọc role tường minh. Nhãn `[phone_use, looking_around]`, unknown giữ null/mask 0.

Parent là `E004-c345-development-20261016` (1.181 train/val), cộng đúng 98 + 172 crop. Không cộng trùng V10 canonical. Nhãn, geometry, crop bytes và rights của parent giữ nguyên; train/val/group đổi đúng [allocation đã nghiệm thu](../train-val-plan-20261017/owner-acceptance.json). 270 ảnh mới giữ exact crop bytes và nhãn owner đã chốt, gồm G06 R02, G23 U/N và hai crop G27 P/P.

[Approval release](owner-release-approval.json) ghi scope yêu cầu release, cleanup và commit của owner, nối tới các receipt crop và allocation. Snapshot allocation và receipt cũ giữ nguyên bytes, kể cả trạng thái Draft/chưa materialize tại thời điểm lịch sử. Release này thực hiện phần đã được duyệt, không sửa các snapshot đó.

## Bằng chứng và cách dùng cho agent tiếp theo

- [Pointer và SHA payload](package-pointers.json): vị trí package, dataset/split version, counts và SHA của `checksums.sha256`.
- [Config release](../../../configs/datasets/pilot-b-20261017-v11.json): chỉ variables đóng gói; không chứa recipe, initialization, checkpoint selection hoặc prediction threshold.
- [Kiểm package](package-validation.json): codec/exporter, loader, bảo toàn và deterministic rebuild. Chi tiết coverage/leakage/QA ở `reports/` trong package.
- [Provenance 270 crop](new-crop-provenance.json), [restore nguồn](source-restore-receipt.json): trace nguồn/crop tới receipt. Source member trong ZIP và ảnh local được đối chiếu bằng inventory đã pin ở hồ sơ audit. Trường `geometry_sha256` trong bảng provenance là SHA của crop được review với geometry đó, không phải hash riêng của tọa độ; tọa độ chính xác nằm trong ledger package.
- [Backup local](backup-receipt.json): snapshot release, nguồn mới và sources của 345 crop parent; nguồn cũ còn phụ thuộc archive V9 được giữ đúng SHA. Có kiểm byte-exact restore; cùng ổ D, không remote upload.
- [Cleanup](cleanup-receipt.json) và [checks bàn giao](handoff-checks.json): chỉ dọn scratch/cache đã kiểm, không retire parent hoặc accepted sources.

`assemble.py` và `backup.py` là worksheet thực hiện release một lần qua API core hiện có, không phải pipeline train. Không chạy lại vào output đã tồn tại hoặc reseal artifact; khi cần restore dùng archive/pins và hướng dẫn operations.

## Phạm vi bảo toàn và giới hạn

Test giữ nguyên ID, nguồn, crop, labels/masks, group, evidence và freeze reference của record; các trường dataset/selection/crop-policy/split version đổi để thuộc package mới. Vì vậy không gọi serialization record test V11 là byte-identical với parent. Parent package bất biến; attestation mới pin serialization mới và chỉ cho phép integrity decode/copy, không có visual review hoặc prediction trên test.

Validation có **178 mẫu từng ở train cũ**. Model được đánh giá sau này phải khai báo lịch sử tiếp xúc dữ liệu; đây không phải holdout độc lập. Nhóm bảo thủ không chứng minh đã xác minh lớp/buổi học/người độc lập; 27 video chưa có mapping lớp/buổi do owner cung cấp. Holdout tiếp tục để sau.

[Mức đạt đã nghiệm thu](../train-val-plan-20261017/README.md) giữ hiệu lực: từng target precision/recall ≥ 80%, FPR ≤ 20%, với support và báo cáo đúng receipt. Prediction threshold, kiến trúc và cách train chưa được chốt. Không train, smoke, inference model hoặc so sánh model trong task release.
