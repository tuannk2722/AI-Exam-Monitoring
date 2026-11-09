# Đặc tả dữ liệu

## 1. Phạm vi và thẩm quyền

Quy định unit/semantics, schema và điều kiện nghiệm thu dataset; không chứa inventory nguồn, coverage từng release hoặc backlog. [Reports index](../artifacts/reports/README.md) dẫn tới nghiên cứu/release; [reference](reference.md#data-tools) mô tả công cụ; [status](status.md) chỉ version/proposal đang làm. Approval release đúng scope/version, không tự cấp quyền experiment/upload.

## 2. Unit và semantics đã chốt

Mỗi mẫu là **một person anchor và context crop đã review**. Contract mở rộng được owner duyệt tại [LABEL-CONTRACT-20261109](decisions.md) có thứ tự `[phone_use, looking_around, sleeping, hand_raising, standing_up]`; áp dụng mọi person anchor, không phân biệt thí sinh/giám thị. Nhiều target có thể cùng positive; không thêm lớp `normal`, `cheating` hoặc map tên lớp nguồn thẳng sang target. `standing_up` là tư thế đang đứng, không phải chuyển động đứng dậy.

P/N/U tương ứng positive/negative/unknown, xét evidence thuộc đúng anchor trên crop. Bảng dưới hợp nhất tiêu chí hiện hành; hai nhãn cũ kế thừa [semantics đối soát đã duyệt](../artifacts/reports/v12-reconcile-20261022/owner-policy-20261023.md):

| Target | P | N | U |
|---|---|---|---|
| `phone_use` | Điện thoại **di động** được cầm/tương tác hoặc hiện trên bàn/sách, gắn đúng anchor | Không thấy phone hoặc vật nghi phone; khuất tay/bàn không tự khiến U. Landline, calculator/book/badge/bút không tự là phone | Vật nhìn thấy chưa phân biệt được với phone hoặc attribution chưa rõ |
| `looking_around` | Đầu quay hẳn sang bên/sau, hoặc hơi chéo nhưng nhìn bài người khác | Đầu thẳng/hơi chéo còn lại khi đủ evidence; cúi đọc/viết; `sleeping=P` | Hướng đầu/đích nhìn không xác định; không lấy `read/write/normal` nguồn làm N |
| `sleeping` | **Gục/ngủ biểu kiến:** đầu nằm đè lên bàn/giấy hoặc cánh tay nằm trên bàn; gồm úp trán và áp má nghiêng trái/phải | Cúi sát đọc/viết nhưng đầu chưa nằm xuống; chống cằm/trán bằng cẳng tay dựng đứng giữ đầu xa bàn; ngả lưng/ngửa cổ/gục cằm trên ghế dù nhắm mắt | Đầu thấp bị che, thiếu evidence phân biệt cúi viết với gục trên bàn/tay |
| `hand_raising` | Tay vươn cao qua đầu hoặc giơ chếch ngang đầu, khuỷu rời bàn, tay tách đầu–mặt–gáy; cả bắp tay và cẳng tay duỗi vượt đỉnh đầu đủ rõ vẫn P khi bàn tay bị cắt ở mép crop | Tì khuỷu lên bàn dù bàn tay ngang tai; gãi đầu/vuốt tóc/ôm gáy/chỉnh kính; đan hai tay vươn vai. Anchor ngồi làm bài có hai vai xuôi rõ là N dù tay khuất dưới bàn hoặc tay người khác giơ cạnh đầu | Bàn tay ngang tai nhưng khuỷu/bàn bị che, không phân biệt đang tì hay nhấc khỏi bàn; không xác định được tay thuộc anchor |
| `standing_up` | Đang đứng/đi trong lối đi, kể cả giám thị; nhổm hẳn mông khỏi ghế dù khom chống tay lên bàn; chân bị che vẫn P nếu context đủ xác nhận | Hông/mông còn trên ghế dù người cao, ngồi thẳng hoặc rướn với đồ; ngồi thấy toàn thân/chân gập. Chỉ lộ đầu/vai nhưng tương quan dãy bàn xác nhận chắc chắn ngồi vẫn N | Chỉ có mặt/cổ, thiếu mốc không gian hoặc evidence chưa phân biệt đứng/ngồi; có thể loại crop không đủ điều kiện |

**Ràng buộc ground truth/QA:** `sleeping=P` buộc `looking_around=N`, kể cả mặt xoay ngang khi nằm gục. Ca đầu thấp khuất sau người phía trước, thiếu context như rubric, giữ U cho cả hai. Ràng buộc này không tự ép nhãn hiển thị hoặc sửa scores model; xung đột nhãn phải review trước acceptance. Ngoài ngoại lệ này, P của một target không tự xác nhận target khác N. Ảnh tĩnh không chứng minh đang ngủ thật hoặc duration/event; không áp ngưỡng thời gian của pipeline cũ vào rubric.

`normal_review` chỉ là metadata trong phạm vi tập target/version: có P hoặc context `confirmed_other` thì `not_normal`; mọi target N và context `confirmed_working` mới `confirmed_normal`, còn lại `unknown`. Normal hai target cũ không tự là normal năm target. Target mới chưa review không được suy N; các khoảng số mẫu trong input thu thập chỉ là mục tiêu coverage, không là gate release hoặc bảo đảm chất lượng model.

Person box bao phần nhìn thấy; context giữ đủ cue của từng nhãn và đúng attribution, không gán phone/tay người bên cạnh cho anchor. Không tự ước lượng cơ thể bị che hoặc đặt padding/gaze/visibility threshold mới. Geometry đã accepted không sửa để khớp detector khác; recrop cần review mới. Classifier chỉ cần review anchor, không annotate mọi người trong ảnh; crop runtime/video và completeness khi train detector có gate riêng.

Thay đổi trên supersede riêng giới hạn hai target và quy tắc không suy chéo ở cấp contract mới; giữ ADR-011/012/013/018 về person unit, multi-label, mask và mobile. Semantics lịch sử, gồm [ngoại lệ absence 15/10](../artifacts/reports/E004-device-consistency-20261015/owner-direction.md), giữ đúng release/scope gốc; không relabel/reseal V15 hoặc hồi tố metrics.

## 3. Contract thực thi và trạng thái record

Codec `data/pilot_schema.py` giữ V1/V2 (`pilot-b-manifest-v1/v2`, `pilot-b-targets-v1`) cho hai target cũ. V3 (`pilot-b-manifest-v3`, `pilot-b-targets-v2`, `semantics_version=LABEL-CONTRACT-20261109`) dùng `targets` theo tên cho năm nhãn, mỗi entry là `TargetReview`. Cùng `PilotRecord` và API `record_from_dict/read_records/validate_records/write_records`; không đổi bytes/ý nghĩa version hoặc `TARGET_ORDER` cũ. V3 từ chối field/target lạ, JSON key trùng, derived values/masks/normal/order sai và xung đột sleeping/looking.

JSONL là **ledger nội bộ của workflow audit**, không phải định dạng bên thu thập phải bàn giao trước. Dữ liệu ngoài vẫn qua kiểm ảnh/nguồn, anchor/crop, review nhãn và QA/group/split/release ở §4. V3 dùng cùng states/gates bên dưới; có thể bắt đầu từ source chưa có crop, mọi target U, rights/group/review còn pending. Nhãn nguồn chỉ là hints; không đòi dữ liệu đã được nghiệm thu trước khi audit.

Mở rộng được owner duyệt [E004 crop dẫn xuất ngày 16/10](../artifacts/reports/E004-train-enrollment-20261016/owner-direction.md): `pilot-b-manifest-v2` thêm `crop.derivation` cho crop import đã resize/nén được review; giữ nguyên serialization V1. Derivation phải pin source SHA, RGB SHA ROI native, kích thước/format output, evidence và review đúng crop SHA. Đây là provenance của derivative đã review, không là bằng chứng recipe upstream tái lập được. Export bắt buộc exact crop bytes và kiểm source/ROI/output pins; loader kiểm bytes/dimensions/format. Crop native không có derivation vẫn phải khớp pixel tuyệt đối ROI. Unknown mask, person/context geometry, rights/group/release gates không đổi. Chỉ package mới dùng V2; không sửa hoặc reseal V1.

| State | Value JSON | Mask | Supervision |
|---|---|---:|---|
| positive | 1 | 1 | Có |
| negative | 0 | 1 | Có |
| unknown | null | 0 | Ngoài loss/metric |

Crop có mọi target U không vào manifest supervision. `TargetReview` có state/reason/review; known target phải pin evidence đúng crop SHA. `ContextReview` dùng `confirmed_working/confirmed_other/unknown`. `ReviewEvidence` giữ reviewer, ngày review, evidence ref và crop SHA khi review crop. Chỉ ghi người/role kỹ thuật, không danh tính sinh viên.

| Nhóm fields của `PilotRecord` | Nội dung và ràng buộc |
|---|---|
| Identity/version | `sample_id`, dataset/selection/crop-policy/schema/encoding versions; ID kỹ thuật an toàn cho filename, không tự đổi identity parent |
| Source | `SourceRef`: source ID, archive/image hashes, relative path, dimensions; label hash/line/class/split nguồn nếu có; taxonomy nguồn chỉ provenance |
| Crop | `CropRef`: anchor, person/context `PixelBox`, relative crop path/hash và crop review; XYXY integer, right/bottom exclusive, nằm trong ảnh; context chứa person region |
| Targets/context | V1/V2 giữ hai field review; V3 có `targets` đủ năm tên chuẩn. Work-context review và value/mask/normal theo target version; không fill unknown thành negative |
| Rights | License ID, attribution ref, approved scopes và owner review; scope sử dụng phải thuộc scope đã duyệt |
| Group | Leakage group ID, evidence refs/review, video/session/room/subject khi xác minh được; null không được bịa từ filename |
| Disposition/usage | Disposition `pending/approved/excluded`; usage `review_only/excluded/train/val/test`, assignment/version và lý do không đủ điều kiện |
| Acceptance/freeze | Owner decision, release review, use scope; test có freeze ref; các field này không thay owner approval thật |

`review_only` và `excluded` có split/version null. Review-only cần lý do còn thiếu; excluded cần reason và owner decision. `train/val/test` cần crop/person approved, ít nhất một target known, rights đúng scope, group đã review, release review và usage khớp split; không còn blocker. Known target/context evidence phải khớp crop hiện tại: recrop tạo SHA mới thì review cũ không tự áp dụng.

## 4. Workflow và nghiệm thu release

1. **Chốt mục tiêu hữu hạn:** failure mode/domain/target cần cải thiện, scope local và vai trò train/development/holdout. Dùng hồ sơ nghiên cứu/coverage đúng version từ reports index, không audit lại mọi source hoặc đặt quota tùy ý.
2. **Tìm input hiện có:** xác minh snapshot/hash và phần archive còn giữ; nếu thiếu toàn payload nguồn thì ghi rõ, tiếp nhận/reacquire đúng version/terms khi được phép. Raw bất biến; không chạy code upstream.
3. **Audit cấu trúc:** decode, image/label pairing, geometry/class IDs, duplicates bytes/RGB, lineage/near-duplicate cross-source. Không sửa raw hoặc dùng filename/hash để invent session.
4. **Tự động shortlist và draft review:** đề xuất anchor/person/context, states/reasons theo tập target của version, rights/provenance/group flags; dùng heuristics/công cụ đã có. Model/pretrained mới cần scope/license decision. Owner nghiệm thu batch và ngoại lệ, không phải tự vẽ mọi bbox.
5. **QA source → crop → model input:** đúng anchor, geometry/attribution, evidence hiển thị còn đủ tại input size, difficult negatives/co-occurrence; U giữ mask 0. Review gắn SHA exact crop.
6. **Group trước split:** cùng image/video/session/augmentation/scene-family cùng ranh giới; thiếu evidence giữ review-only/quarantine. Whole-family không tự chứng minh independent holdout.
7. **Owner chốt membership/rights/assignment:** eligibility đầy đủ mới vào train/val/test. Giữ parent evaluation identity; đổi nhãn/crop/assignment tạo version mới và report delta riêng.
8. **Đóng package mới:** ledger, used manifest, selection/provenance, split assignment, release metadata/card, coverage/leakage/QA reports, approval/config/hash, test freeze và checksums. Exporter `pilot_package.py` và codec là logic tái dùng; không tạo một script cho mỗi vòng review.
9. **Kiểm và bàn giao:** schema/usage/pins, exact inventory/crop bytes, cross-split leakage, parent preservation/test serialization và deterministic rebuild theo scope. Report limitations và quyền storage; không reseal package cũ hoặc tự train sau release.

`train/val/test` assignment phải tường minh/versioned, không chia lại random ratio/seed trong loader. Unknown không tham gia loss/metric, test không dùng cho tuning/quota/selection. Holdout có package/protocol riêng, không nhập vào train.

## 5. Contract holdout

Tiếp nhận holdout: pin source/version/terms/SHA → quarantine lineage/cross-source overlap → crop/target QA theo đúng contract, không cho reviewer xem candidate scores → sampling/protocol chốt trước prediction → package riêng/freeze/access receipt. Không lấy evaluation pool đã dùng, upstream test chưa kiểm provenance hoặc random frame split gọi là independent holdout. Không cân lại/loại mẫu khó sau thấy metrics.
