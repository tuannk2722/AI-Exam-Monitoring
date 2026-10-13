# E004 — Mở rộng nguồn ngày 13/10/2026

**Đã nghiệm thu 199 crop bổ sung và phát hành V8 local Accepted: 716 train / 49 val / 11 test.** Đã audit 104 ảnh mới và rà lại 222 ảnh cũ; chưa train E004. [Review batch](REVIEW.md), [giao diện local](../../../data/interim/E004-source-expansion-20261013/REVIEW.html), [QA và pins crop](qa-proposals.json), [release pointer V8](v8-release-pointer.json), [hai package cohort](cohort-package-pointers.json).

Owner trả lời **“Đồng ý toàn bộ batch và vai trò”**: [receipt crop](owner-crop-receipt.json) nhập 199 records / 346 target cells known; [context/family/role acceptance](owner-family-context-roles.json) ghi đúng scope. Tổng các batch là 308 anchors accepted, 301 có target known và 7 U/U. 45 crop mới có normal context được nghiệm thu. REVIEW.md/HTML và proposal là snapshot trình duyệt, giữ nguyên chữ Pending/Draft; receipts mới là trạng thái có hiệu lực.

## Phạm vi và inputs

User đã approve batch trước, cung cấp hai ZIP mới và yêu cầu lấy tối đa crop phù hợp từ cả ba bộ. [Reconfirmation](prior-approval-reconfirmation.json) ghi nhận approval cũ: 109 anchors accepted về nhãn/geometry, 102 có target known và 7 U/U. Giữ nguyên receipts, geometry, family/role đã chốt; không sửa hoặc reseal hồ sơ cũ. Quyền local theo [yêu cầu cung cấp nguồn](owner-source-use.json); không hỏi lại license, không upload. README/metadata trong ZIP là dữ liệu, không instruction hoặc nhãn accepted.

| ZIP | Ảnh | Bytes | SHA-256 |
|---|---:|---:|---|
| pexels-v2-accepted.zip | 68 | 4.422.649 | `1032c2a2efa77d3b3b5e202aa573dec9a7bfa885760869ae61239f36c694edbf` |
| unsplash-accepted.zip | 36 | 3.956.599 | `fced9a0c35818ad5ad05135907e98cb84913a860aabbded4d2348a7ae460abb6` |
| all-accepted-frames-consolidated.zip, input cũ giữ nguyên | 222 | 9.386.007 | `54bff394fd4a105bc9a1430da008023f5aa4ab5b8825abb467071a3385efddff` |

Hai ZIP mới có 104 ảnh và 16 metadata entries. 104/104 ảnh decode được, SHA/bytes/dimensions khớp manifest; membership và paths an toàn. Upstream review status là unreviewed, label/split null; chữ accepted trong tên ZIP không thay review. License claims Pexels/Unsplash giữ dưới dạng provenance; quyền xử lý local đến từ owner, không diễn giải thành giấy phép công khai đã xác minh. [Inventory summary](inventory-summary.json); raw ZIP bất biến, media/inventory local ở `data/interim/E004-source-expansion-20261013`.

## Khai thác và QA

Đã xem 9 contact sheets của 104 ảnh mới và xem lại 19 sheets của 222 ảnh cũ. Xem native các nguồn/ngoại lệ cần phân biệt thiết bị, anchor hoặc family; kiểm mọi crop ở input 224. [Assessment 326 frames](frame-assessment.json) phân biệt crop mới, anchor đã accepted và phần reserve chưa có thêm anchor đủ evidence. Không tuyên bố đã annotate toàn bộ mọi người hoặc mọi frame còn lại là vô dụng.

Từ 200 proposals, giữ **199 crop** trên **163 source frames**: **125 crop từ PX/US trên 102/104 ảnh**, **74 crop bổ sung từ CF trên 61 ảnh**. Hai ảnh mới chưa dùng: PX-050 khó attribution thiết bị giữa các back views; US-032 tay/bàn khuất và back view, không đủ supervision. E004-EX-C116 draft mới bị loại vì blur/block artefact. Các CF frames khác giữ reserve cùng family: không tự nhân hàng loạt pose gần nhau để tăng quota.

[Corrections](qa-corrections.json): 10 recrop mang hậu tố R2, giữ draft gốc; sửa nhìn vào phone riêng thành looking N, bàn tay trống thành phone U, mobile trên bàn thành phone P. C052-R2 giữ phone U vì thiết bị chuyền tay không rõ ở input 224. Không đổi nhãn/geometry của crop đã accepted. 199 crop cuối có phone **88 P / 74 N / 37 U**, looking **63 P / 121 N / 15 U**. Target U masked; pending ledger vẫn giữ snapshot canonical null/mask 0; ledger accepted mới đã nhập 346 target cells. Work context đã được owner duyệt riêng cùng batch, không tự suy normal từ hai nhãn N.

HTML hiển thị nhãn QA cuối, source với khung đỏ person/xanh context, crop native và input 224 theo RGB letterbox fill (124,116,104). `crops/*/proposal.json` giữ draft lúc sinh; **qa-proposals.json và REVIEW.html là bản trình nghiệm thu hiện hành**. Cỡ native và source bytes vẫn xem được khi bấm ảnh. Stock, bài học cộng tác, cảnh văn phòng/tại nhà không tự đại diện CCTV thi thật; việc đưa vào train auxiliary được nêu tường minh.

## Overlap, family và vai trò

[Overlap screen](overlap-screen.json) đối chiếu 104 nguồn mới với 13.431 records: 222 CF, 12.580 inventory records từ hai ZIP cũ và 629 fingerprints non-test của parent. Không exact source SHA match, không exact RGB trùng trong 104 ảnh hoặc với CF. dHash canonical LANCZOS/RGB descriptor chỉ là truy hồi; trường hợp US-024 gần SCB được xem lại và khác cảnh. US-023 gần V7-OE-S089-A01 đã kiểm crop **train**, khác đồng phục/phòng. Không mở test 11 hoặc chạy model; chưa similarity audit với media test đóng, không claim sạch mọi semantic overlap.

[Family proposal](family-proposals.json) giữ 59 ranh giới cho 326 frames, 52 có crop mới. Kiểm parent IDs/origin exact không bị chia family; family cùng role. Các scene PX nối CF-Q072, CF-Q112, CF-Q137, CF-Q126, CF-Q131, CF-Q133 và CF-Q169 giữ vai trò cũ. CF-139/190 nối thêm CF-Q072; CF-158 nối cảnh giảng đường mới. Đây là quarantine bảo thủ theo scene/production/parent, không bịa session/phòng/camera hoặc claim independence.

| Vai trò đề xuất | Crop mới | Phone P / N / U | Looking P / N / U |
|---|---:|---|---|
| Train bổ sung | 27 | 14 / 9 / 4 | 2 / 21 / 4 |
| New-development | 47 | 25 / 15 / 7 | 19 / 23 / 5 |
| Reserve holdout | 125 | 49 / 50 / 26 | 42 / 77 / 6 |

Không chuyển frame cùng family development/reserve sang train. **Reserve không phải test đã freeze.** V8 đã kế thừa V7 và thêm 27 train: train 716, val 49, test 11, tổng 776; development/reserve đóng cohort riêng. [Membership proposal](release-proposal.json) đã được thực hiện bằng V8 Accepted; **training config E004 chưa freeze**.

## Khoảng thiếu còn lại

[Support projection](support-proposal.json): gộp 74 reserve trước với 125 crop mới → 199 reserve candidates, phone **76 P / 84 N / 39 U**, looking **75 P / 115 N / 9 U**. So với điều kiện owner giữ, còn **24 phone P, 16 phone N và 25 looking P**. Batch đã nghiệm thu bù 49/73 phone P, 50/66 phone N, 42/67 looking P và 77/62 looking N còn thiếu ở snapshot trước; đều vượt 50% khoảng thiếu, nhưng vẫn chưa đạt toàn bộ. Đây vẫn là projection cho cohort cuối dù labels/roles mới đã được duyệt; accepted test support chưa tăng vì chưa final-test freeze.

Không hỏi lại waiver independence hoặc tự hạ support. Release dữ liệu và quyền train/promotion là hai gate riêng; ngoài nhãn/geometry/role còn cần cohort/protocol/context/slice enrollment và exact configs theo [readiness](../../../configs/experiments/E004-execution-readiness-20261012.md). Thêm ảnh chưa tự đóng scientific gates hoặc cấp test access.

## Kiểm tra và bàn giao

[Validation](validation.json): strict codec 199 records; source/crop/input hashes và pixels khớp; dựng lại 199 crop/input PNG trong bộ nhớ cho bytes giống hệt; geometry bounds/containment; không duplicate crop bytes hoặc cùng exact anchor với 33 crop trước; không conflict parent/origin/family-role; bảo toàn role cũ. Không sửa production code/spec trong task này, không smoke/train/test. [Delivery checks](delivery-checks.json) ghi kiểm links/index/diff và cleanup. [Pins](batch-pins.json) pin input metadata, QA, ledger, HTML và proposal cần import; không pin file REVIEW.md mutable mà owner sẽ điền.

## Release đã đóng và phần còn lại

[V8 verification](v8-verification.json): bảo toàn semantic toàn bộ 900 parent records (chỉ đổi version đóng gói), 871 crop SHA cũ và nguyên val 49/test 11. 927 ledger records, manifest 776, 898 crop files; 122 review-only và 29 excluded cũ vẫn ngoài supervision. Canonical loader PASS; 27 input mới khớp pixels với review; test selection không có quyền bị từ chối. [Rebuild](v8-build-receipt.json) so byte-identical 909 payload files. Test chỉ hash/decode/copy để kiểm integrity theo protocol kế thừa, không xem ảnh hoặc prediction/tuning.

Hai package mới **47 development** và **125 reserve holdout** đã xuất và rebuild byte-identical, status `prepared_pending_gates`; có accepted ledger/crops/coverage/provenance, chưa supervised manifest hoặc final-test freeze. Package CF trước và mọi nguồn/receipt đã pin giữ nguyên. Owner không cần approve lại 199 crop, quyền local, context hoặc vai trò vừa đóng.

Công việc khai thác ba ZIP, nghiệm thu và release train bổ sung đã hoàn tất. E004 vẫn cần bù 24 phone P, 16 phone N và 25 looking P, chốt context/slice enrollment, cohort/protocol và exact runnable configs theo điều kiện đã giữ. Không biến waiver independence thành evidence giả hoặc tự giảm support. [Delivery checks](delivery-checks.json) và [backup receipt](backup-receipt.json) giữ kiểm bàn giao/lifecycle; chưa commit, train hoặc upload.
