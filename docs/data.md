# Đặc tả dữ liệu

## 1. Phạm vi và thẩm quyền

Quy định unit/semantics, schema và điều kiện nghiệm thu dataset; không chứa inventory nguồn, coverage từng release hoặc backlog. [Reports index](../artifacts/reports/README.md) dẫn tới nghiên cứu/release; [reference](reference.md#data-tools) mô tả công cụ; [status](status.md) chỉ version/proposal đang làm. Approval release đúng scope/version, không tự cấp quyền experiment/upload.

## 2. Unit và semantics đã chốt

ADR-011/012/013/018 Accepted: mỗi mẫu là **một person anchor và context crop đã review**. Thứ tự hai target cố định `[phone_use, looking_around]`; có thể đồng thời positive. Không thêm lớp `normal`, `cheating` hay map tên lớp nguồn thẳng sang target.

| Target/state | Điều kiện review | Trường hợp phải giữ unknown |
|---|---|---|
| Phone positive | Điện thoại **di động** được cầm/tương tác hoặc hiện trên bàn/sách, có evidence gắn đúng anchor | Device quá mờ/che, không phân biệt mobile với vật khác, không biết thuộc người nào |
| Phone negative | Vùng tay/bàn/bằng chứng đủ quan sát và owner xác nhận absence mobile của anchor | Không có source bbox, tay khuất hoặc thiếu annotation không là negative |
| Looking positive | Hướng đầu/nhìn rõ sang người khác hoặc ngoài vùng bài làm, có context để diễn giải | Chỉ lệch đầu, cúi đọc/viết, back view hoặc hướng nhìn/vùng bài không rõ |
| Looking negative | Review xác nhận không có hành vi trên trong vùng quan sát đủ evidence | Không lấy `read/write/normal` nguồn làm ground truth |
| Normal metadata | Cả hai target negative và work context `confirmed_working` | Hai negative nhưng thiếu context vẫn normal unknown; không tạo nhãn thứ ba |

Landline có dây không tạo phone positive. Calculator/book/badge/bút không tự là mobile. Không gán phone gần nhất hoặc device người khác cho anchor. Ảnh tĩnh không chứng minh duration/event. Positive một target không tự xác nhận target kia negative. Có positive hoặc context `confirmed_other` thì `normal_review=not_normal`; đủ hai negative + working mới `confirmed_normal`, còn lại `unknown`.

Person box bao phần nhìn thấy; context có thể thêm vùng bàn/thiết bị liên quan. Không tự ước lượng cơ thể bị che, thêm padding/gaze/visibility threshold chưa duyệt. Geometry/crop policy thuộc release đã nghiệm thu; không sửa geometry cũ cho khớp detector khác. Crop runtime từ video là gate riêng. Classifier crop review không yêu cầu annotate mọi người trong ảnh; nếu train detector cần completeness contract khác.

### Ngoại lệ absence có phạm vi từ 15/10/2026

[E004-PHONE-OCCLUSION-20261015](../artifacts/reports/E004-device-consistency-20261015/owner-direction.md) được owner duyệt cho revision crop bundle này và revision tiếp theo dẫn quyết định: vật bị giấy/vật khác che **hoàn toàn** có thể phone N khi tay và phần quan sát còn lại đủ review, không có phone rõ hoặc thiết bị mơ hồ còn lộ. N ở đây là absence trong vùng nhìn thấy, không chứng minh không có phone sau vật che. Tay mất khỏi crop/dưới bàn, vật còn lộ không phân biệt được hoặc attribution chưa rõ vẫn U nếu không có phone khác rõ. Không hồi tố release/metrics/pins cũ; package mới phải ghi semantics revision/evidence. Các semantics còn lại của bảng trên giữ nguyên.

### Revision đối soát V12 từ 23/10/2026

[V12-RECONCILE-PHONE-20261023](../artifacts/reports/v12-reconcile-20261022/owner-policy-20261023.md) được owner duyệt cho candidate đang đối soát và 156 ảnh bổ sung: tay/bàn bị che hoặc nằm ngoài crop không tự khiến phone U. Không thấy phone hay vật nghi phone trong ảnh thì N; có vật nhìn thấy nhưng chưa phân biệt được phone với vật khác thì U. Không gán thiết bị của người khác cho anchor. Quyết định này supersede riêng điều kiện quan sát tay/bàn của bảng và ngoại lệ 15/10 ở trên trong revision này; giữ nguyên semantics và pins các release đã accepted. Package mới phải dẫn đúng semantics revision và evidence từng crop.

Trong cùng đợt audit, Looking P khi đầu quay hẳn sang bên/sau, hoặc hơi chéo nhưng nhìn bài người khác; đầu thẳng/hơi chéo còn lại N khi đủ evidence. Hướng đầu/đích nhìn không xác định vẫn U. Quy tắc này không tự cấp acceptance nhãn toàn batch, split hoặc release.

## 3. Contract thực thi và trạng thái record

Codec ở `src/ai_exam_monitoring/data/pilot_schema.py`: `schema_version=pilot-b-manifest-v1`, `target_encoding_version=pilot-b-targets-v1`. Dùng `record_from_dict`, `read_records`, `validate_records`, `write_records`; không tạo parser dict permissive song song. Field lạ, derived mask/value sai, version/evidence không hợp lệ phải bị từ chối.

Mở rộng được owner duyệt [E004 crop dẫn xuất ngày 16/10](../artifacts/reports/E004-train-enrollment-20261016/owner-direction.md): `pilot-b-manifest-v2` thêm `crop.derivation` cho crop import đã resize/nén được review; giữ nguyên serialization V1. Derivation phải pin source SHA, RGB SHA ROI native, kích thước/format output, evidence và review đúng crop SHA. Đây là provenance của derivative đã review, không là bằng chứng recipe upstream tái lập được. Export bắt buộc exact crop bytes và kiểm source/ROI/output pins; loader kiểm bytes/dimensions/format. Crop native không có derivation vẫn phải khớp pixel tuyệt đối ROI. Unknown mask, person/context geometry, rights/group/release gates không đổi. Chỉ package mới dùng V2; không sửa hoặc reseal V1.

| State | Value JSON | Mask | Supervision |
|---|---|---:|---|
| positive | 1 | 1 | Có |
| negative | 0 | 1 | Có |
| unknown | null | 0 | Ngoài loss/metric |

Crop U/U không vào manifest supervision. `TargetReview` có state/reason/review; known target phải pin evidence đúng crop SHA. `ContextReview` dùng `confirmed_working/confirmed_other/unknown`. `ReviewEvidence` giữ reviewer, ngày review, evidence ref và crop SHA khi review crop. Chỉ ghi người/role kỹ thuật, không danh tính sinh viên.

| Nhóm fields của `PilotRecord` | Nội dung và ràng buộc |
|---|---|
| Identity/version | `sample_id`, dataset/selection/crop-policy/schema/encoding versions; ID kỹ thuật an toàn cho filename, không tự đổi identity parent |
| Source | `SourceRef`: source ID, archive/image hashes, relative path, dimensions; label hash/line/class/split nguồn nếu có; taxonomy nguồn chỉ provenance |
| Crop | `CropRef`: anchor, person/context `PixelBox`, relative crop path/hash và crop review; XYXY integer, right/bottom exclusive, nằm trong ảnh; context chứa person region |
| Targets/context | Hai `TargetReview`, work-context review; value/mask/normal derive từ state, không fill unknown thành negative |
| Rights | License ID, attribution ref, approved scopes và owner review; scope sử dụng phải thuộc scope đã duyệt |
| Group | Leakage group ID, evidence refs/review, video/session/room/subject khi xác minh được; null không được bịa từ filename |
| Disposition/usage | Disposition `pending/approved/excluded`; usage `review_only/excluded/train/val/test`, assignment/version và lý do không đủ điều kiện |
| Acceptance/freeze | Owner decision, release review, use scope; test có freeze ref; các field này không thay owner approval thật |

`review_only` và `excluded` có split/version null. Review-only cần lý do còn thiếu; excluded cần reason và owner decision. `train/val/test` cần crop/person approved, ít nhất một target known, rights đúng scope, group đã review, release review và usage khớp split; không còn blocker. Known target/context evidence phải khớp crop hiện tại: recrop tạo SHA mới thì review cũ không tự áp dụng.

## 4. Workflow và nghiệm thu release

1. **Chốt mục tiêu hữu hạn:** failure mode/domain/target cần cải thiện, scope local và vai trò train/development/holdout. Dùng hồ sơ nghiên cứu/coverage đúng version từ reports index, không audit lại mọi source hoặc đặt quota tùy ý.
2. **Tìm input hiện có:** xác minh snapshot/hash và phần archive còn giữ; nếu thiếu toàn payload nguồn thì ghi rõ, tiếp nhận/reacquire đúng version/terms khi được phép. Raw bất biến; không chạy code upstream.
3. **Audit cấu trúc:** decode, image/label pairing, geometry/class IDs, duplicates bytes/RGB, lineage/near-duplicate cross-source. Không sửa raw hoặc dùng filename/hash để invent session.
4. **Tự động shortlist và draft review:** đề xuất anchor/person/context, hai state/reasons, rights/provenance/group flags; dùng heuristics/công cụ đã có. Model/pretrained mới cần scope/license decision. Owner nghiệm thu batch và ngoại lệ, không phải tự vẽ mọi bbox.
5. **QA source → crop → model input:** đúng anchor, geometry/attribution, evidence hiển thị còn đủ tại input size, difficult negatives/co-occurrence; U giữ mask 0. Review gắn SHA exact crop.
6. **Group trước split:** cùng image/video/session/augmentation/scene-family cùng ranh giới; thiếu evidence giữ review-only/quarantine. Whole-family không tự chứng minh independent holdout.
7. **Owner chốt membership/rights/assignment:** eligibility đầy đủ mới vào train/val/test. Giữ parent evaluation identity; đổi nhãn/crop/assignment tạo version mới và report delta riêng.
8. **Đóng package mới:** ledger, used manifest, selection/provenance, split assignment, release metadata/card, coverage/leakage/QA reports, approval/config/hash, test freeze và checksums. Exporter `pilot_package.py` và codec là logic tái dùng; không tạo một script cho mỗi vòng review.
9. **Kiểm và bàn giao:** schema/usage/pins, exact inventory/crop bytes, cross-split leakage, parent preservation/test serialization và deterministic rebuild theo scope. Report limitations và quyền storage; không reseal package cũ hoặc tự train sau release.

`train/val/test` assignment phải tường minh/versioned, không chia lại random ratio/seed trong loader. Unknown không tham gia loss/metric, test không dùng cho tuning/quota/selection. Holdout có package/protocol riêng, không nhập vào train.

## 5. Contract holdout

Tiếp nhận holdout: pin source/version/terms/SHA → quarantine lineage/cross-source overlap → crop/two-target QA không cho reviewer xem candidate scores → sampling/protocol chốt trước prediction → package riêng/freeze/access receipt. Không lấy evaluation pool đã dùng, upstream test chưa kiểm provenance hoặc random frame split gọi là independent holdout. Không cân lại/loại mẫu khó sau thấy metrics.
