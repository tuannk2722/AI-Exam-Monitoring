# E004 — Audit toàn bộ ZIP 222 frames

Ngày 2026-10-13. **Đã nghiệm thu thêm 33 crop và đóng hai package chuẩn bị; chưa phát hành dataset Accepted mới.** Đã xem đủ 222 ảnh trên 19 contact sheets, kiểm native các nguồn được chọn và QA 33 crop qua input 224. [Batch đã được owner nghiệm thu](REVIEW.md), [QA cuối](qa-proposals.json), [assessment từng ảnh](frame-assessment.json), [support đề xuất](support-proposal.json).

## Đầu vào và quyền

ZIP owner cung cấp: `all-accepted-frames-consolidated.zip`, 9.386.007 bytes, SHA `54bff394fd4a105bc9a1430da008023f5aa4ab5b8825abb467071a3385efddff`. Raw không sửa. 222 JPG và 3 metadata files; tên “accepted” không được dùng làm approval nhãn/geometry. Owner xác nhận toàn quyền sử dụng ngày 13/10 và yêu cầu không hỏi lại; [receipt quyền local](owner-rights.json) áp dụng ZIP này. Các license claims upstream giữ nguyên dưới dạng provenance, không đổi thành giấy phép đã xác minh. Không upload.

## Kết quả kiểm

- 222/222 decode, SHA/bytes/kích thước khớp manifest; membership ZIP an toàn, không thiếu ảnh. 222 SHA và 222 RGB hashes khác nhau: không trùng byte/pixel trong ZIP.
- Metadata có 35 parent IDs không null, 49 ảnh không parent; không coi đó là số nhóm độc lập. Từ toàn bộ ảnh và parent linkage, đề xuất **27 ranh giới family bảo thủ**. Các video/ảnh khác parent nhưng cùng production được gộp. Scene-family vẫn là proposal, không bịa video/session/phòng/camera.
- 71 frame CCTV từ 4 cảnh chính; 151 ảnh/frame còn lại chủ yếu stock/dàn dựng, có ảnh thư viện, nhóm đứng hoặc không thấy vùng bài. Metadata “clean/watermark-free” không đúng cho toàn bộ ảnh: CF-030–060 có logo ALTIMA; một số cảnh CCTV có timestamp/camera overlay. Không xóa watermark để thay đổi raw.
- [Overlap screen](overlap-screen.json): đối chiếu 12.580 inventory records từ hai ZIP trước và 629 fingerprints non-test của parent; không exact source SHA match, không dHash distance ≤ 8. RGB descriptor nearest neighbors chỉ hỗ trợ truy hồi, không chứng minh không overlap hoặc independence. Không mở media test 11 hoặc chạy inference. Chưa kiểm image similarity với media test đóng.
- Không có bbox/target upstream dùng được; `label=null`, `split=null`. Có MIME video kế thừa từ parent dù payload là JPEG. Không dùng metadata này làm supervision.

## 33 crop đã chuẩn bị

31 source frames, 14 family proposals. Owner đã nghiệm thu phone **14 P / 12 N / 7 U**; looking **10 P / 21 N / 2 U**. Pending ledger giữ null/mask 0; ledger accepted mới đã nhập đúng 57 known target cells qua strict importer. [Receipt](owner-crop-receipt.json) và [family/role acceptance](owner-family-roles.json) giữ approval mới; snapshot QA/REVIEW giữ nguyên để truy vết. HTML local có nguồn đầy đủ, person/context boxes, crop và input 224; technical IDs không có danh tính.

Owner đã đồng ý giữ **12 crop family CF-Q072 ở new-development**: phone 4 P / 6 N / 2 U; looking 6 P / 6 N. Nhóm này bù đúng phone P còn thiếu ở development, nhưng tập trung một production nên không claim độ đa dạng độc lập. **21 crop còn lại reserve holdout candidate**: phone 10 P / 6 N / 5 U; looking 4 P / 15 N / 2 U. Không chia các frame cùng family sang train. Reserve còn lại được ghi theo từng frame trong assessment, không gọi là đã crop/annotate hết mọi người.

Chọn batch hữu hạn để ưu tiên missing phone P, co-occurrence, calculator/hộp bút và context CCTV/stock. Không nhân hàng loạt frame gần nhau để đạt quota. Những ảnh không chọn vẫn đã kiểm thị giác; để reserve cùng family hoặc auxiliary, không tự gán negative. Có thể khai thác thêm anchor sau khi nghiệm thu batch và vai trò, nhưng không cam kết đủ 100 P/100 N từ ZIP này.

## Nghiệm thu 20 crop cũ

Owner approve toàn bộ batch support-expansion ngày 13/10. [Receipt hiện hành](../E004-source-review-20261011/support-expansion-20261012/owner-receipt-20261013-r2.json) nhập 20 records, 36 known target cells; phone 7 P / 9 N / 4 U, looking 10 P / 10 N. Tổng hai batch cũ: **76 anchors accepted về nhãn/geometry, 69 có target known và 7 U/U**; ledger vẫn review-only, chưa role/release acceptance.

Receipt `r2` thay bản import đầu ngày 13/10 **chỉ sửa original_split của C005 và C013–C016 thành valid** theo selection nguồn; nhãn, crop và input hashes không đổi. Giữ receipt/ledger đầu để truy vết, không reseal. `REVIEW.md` ngày 12/10 chứa edits approval của owner nên khác hash trước review là có chủ đích; không sửa pin lịch sử để che khác biệt.

## Release và E004

Chưa tạo V8: không có train addition mới đã nghiệm thu; V7 train/val/test được bảo toàn. New-development và holdout có package/role riêng theo readiness hiện hành. Owner đã nghiệm thu **33 crop mới và family/role proposal**, đồng thời xác nhận quyền nguồn. Không cần duyệt lại những phần này. Đã reserve 206 frames thuộc các families liên quan để tránh đưa các frame còn lại cùng cảnh sang train. Cần đóng cohort/protocol cuối và context/slice enrollment; reservation không tự là test freeze. Release dữ liệu và đủ support chạy promotion là hai gate khác nhau.

Nếu cả reserve cũ 53 crop và 21 crop mới được chốt holdout, tổng đề xuất là 74 crop: phone 27 P / 34 N / 13 U, looking 33 P / 38 N / 3 U. So với điều kiện đã giữ 100 P/100 N, còn thiếu phone 73 P/66 N và looking 67 P/62 N. Đây là projection, accepted test support hiện vẫn 0. Independence đã được miễn; không yêu cầu bổ sung mapping chỉ để chứng minh independence. Giữ số nhóm/context/slices và support khác theo quyết định hiện hành.

## Artifact và kiểm tra

Local payload: `data/interim/E004-consolidated-frames-20261013/` gồm nguyên metadata ZIP, frames, inventory, boards, crops, `pending-ledger.jsonl`, `REVIEW.html`. Không commit media. [Validation](validation.json) giữ schema, pins, QA bytes và kiểm metadata import. Sửa một câu card trong `pilot_package.py` để bỏ khẳng định hardcoded Roboflow không đúng với nguồn mới; giữ nguyên schema và gates. Không sửa spec, không chạy smoke/train/test. Giữ previews là evidence review còn cần dùng; không có checkout/scratch tạm cần giữ. Scratch rebuild và cache mới sinh được dọn sau checks.

## Package hiện hành sau approval

[Hai pointers r2](package-pointers-r2.json): development 12 crop và holdout reserve 21 crop, đã có ledger accepted về nhãn/geometry/group reservation, crop bytes, provenance/selection, coverage, QA, card và checksums. Status exporter là **prepared_pending_gates**, không có supervised manifest hoặc assignment train/val/test. Hai bản rebuild độc lập cho kết quả byte giống nhau. Bản đầu được giữ vì đã pin; r2 chỉ sửa câu mô tả nguồn trong card, không đổi nhãn/geometry/membership.

Đây chưa phải V8 hoặc runnable cohort. Exporter Accepted hiện yêu cầu training records và package freeze đầy đủ; batch được duyệt là development/reserve, không phải quyền chuyển nó thành train hoặc test đã freeze. Không nới gate hoặc thêm training records giả để export. Khi đóng cohort cuối sẽ cần export scope development/holdout đúng contract; support E004 vẫn còn thiếu như trên. Tổng nghiệm thu nhãn/geometry qua ba batch hiện là **109 anchors, 102 có target known, 7 U/U**. Phần audit toàn ZIP và nhập các approval hiện có đã hoàn tất.

Validation cuối: [checks](validation-final.json). REVIEW và HTML là snapshot tại lúc trình duyệt nên còn chữ Pending; receipts mới là bằng chứng nghiệm thu, không sửa snapshot đã pin.
