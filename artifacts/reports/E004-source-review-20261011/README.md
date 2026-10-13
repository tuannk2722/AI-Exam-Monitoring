# E004 — Thẩm định nguồn và contextual-negative pilot, 2026-10-11

Owner đã approve báo cáo/đề xuất trước và yêu cầu thực hiện ưu tiên dữ liệu; [receipt](owner-direction.json) giữ lời duyệt và exact input hashes. Snapshot Draft cũ giữ nguyên bytes. Quyền sử dụng hai ZIP local đã xác nhận. Báo cáo này ghi **kết quả chuẩn bị mới**, chưa là nghiệm thu crop/nhãn/group/assignment hoặc quyền run/final test.

**Kết luận:** đã xem đủ 40 ảnh gốc, mở rộng và xem 120 ảnh, tạo/review 58 crop versions tại input 224. Có 47 đề xuất có ít nhất một target đủ evidence draft để owner review; **0 group độc lập đã xác minh, 0 crop mới đã vào train/development/test**. Hai nguồn hữu ích cho contrasts nhưng chưa đáp ứng G3 hoặc new-development đã freeze. Không thêm frame cùng cảnh để gọi là tăng independence.

## 1. Inputs, phương pháp và evidence

Theo [AGENTS](../../../AGENTS.md), [index](../../../docs/00-INDEX.md), contracts data/training và freeze proposal đã duyệt. ZIP/payload V7/40 IDs giữ pins của audit trước. Config mới: [source review](../../../configs/datasets/e004_source_review_20261011.yaml). Raw ở Downloads bất biến; chỉ derivatives/review media ở `data/interim/E004-source-review-20261011`.

- [Thẩm định từng ảnh gốc 40](shortlist40-assessment.json), [toàn 120](inspection-assessment120.json), [scene/family review](scene-family-review.json), [triage summary](triage-summary.json).
- [Geometry đầu](pilot-geometry.json), [recrop/contrast bổ sung](pilot-geometry-followup.json), [QA exact crop/input 224](pilot-input224-review.json), [summary](pilot-summary.json), [matched pairs](pilot-pairs.json).
- [Validation/pins](validation.json), [freeze và bước thực thi](../../../configs/experiments/E004-data-execution-20261011.md).
- Mở [review batch local](../../../data/interim/E004-source-review-20261011/REVIEW.html): source có khung anchor/context → crop native → input 224, states sau QA và exceptions. Media này không ở Git; giữ local cho owner review.

Inventory mới đọc 3.633 ảnh behavie và 8.949 ảnh Student; toàn file annotation lỗi bị quarantine, Student có 2 file lỗi zero-size như audit trước, behavie 0. Source classes luôn là hints; empty label không là N. Farthest-first trên descriptor RGB 12×8 chọn thêm 8 ảnh cho mỗi hint, deterministic, loại cờ dHash đã biết. Descriptor/dHash/filename chỉ phục vụ tìm ảnh và rank review, không tạo group độc lập.

Đối chiếu 629 unique source images **non-test** V7 trong archive đúng SHA; không đọc media/predictions test 11, không chạy model hoặc dùng candidate scores. Nearest scene comparisons không chứng minh disjointness toàn bộ E001–E004; overlap đã thấy là evidence dương, còn chưa thấy vẫn unknown. Upstream train/valid/test không trở thành E004 roles.

## 2. Kết quả thẩm định 40 và mở rộng

| Evidence | Original 40 | Toàn 120 | Ý nghĩa |
|---|---:|---:|---|
| Raw images đã xem | 40 | 120 | 20 → 60 mỗi nguồn, không phải person crops |
| Cùng cảnh đã dùng train V7 | 12 | 36 | Không đủ điều kiện holdout/new-development độc lập |
| behavie reserve candidate evaluation | 20 | 60 | 6 ranh giới cảnh thận trọng, chưa proven independent |
| Student instructional candidates chưa thấy overlap trong comparisons | 8 | 23 | Quarantine new-development; chưa chứng minh nguồn/video/person/session/room khác |
| Semantic quarantine thêm | 0 | 1 | `STU-X-d83408e7c75e`: box writing ở nền cạnh teacher; không crop/auto label |
| Independent groups đã chứng minh | 0 | 0 | Không lấy visual views/hash/IDs làm session evidence |

12 ảnh Student gốc có hint phone/Using_phone/turn_head thuộc hai cảnh train: tường xám/cửa sổ xanh (`V6-SB-005`, `V6R2-SB-006`) và camera cao/bàn vàng (`V6-SB-012`, `V6R2-SB-011`). Mở rộng xác nhận thêm cảnh giảng đường (`V6-SB-008`, `V6R2-MP-048`); tổng 36 ảnh thuộc ba cảnh đã dùng. Cùng cảnh xác minh bằng bố trí phòng/camera/bàn/window; không suy danh tính người. Đây là overlap scene bị bỏ sót bởi shortlist dHash, không phải exact duplicate bytes.

behavie có cảnh bàn rộng/cửa sổ sáng, CCTV ghế xanh, CCTV phía sau lớp, ghế có bàn viết kiểu diễn, lớp tường vàng/cờ dây và lớp bàn ghế dài/tường cũ. Các bố trí/nhóm người/góc quay trong nhóm bàn ghế cũ và ghế kiểu diễn được gom thận trọng khi quan hệ chưa rõ; không đếm chúng như phòng/session khác. Timestamp ghế xanh giúp liên kết frame cùng footage, không chứng minh độc lập với lịch sử.

Student instructional có nhiều cảnh trẻ em đọc/viết, nhưng nguồn video gốc và liên kết với SCB/RF/HRW lịch sử còn unknown. Reading có ảnh giơ tay; writing có teacher/background; một số ảnh có player UI, watermark lớn, back view hoặc low detail. Chỉ giữ ảnh/crop có evidence từng target, không map class name. Đã xem native/crop bổ sung cho các trường hợp QA mơ hồ.

## 3. Pilot cụ thể và giá trị bổ sung

58 crop artifacts gồm 55 draft đầu và 3 follow-up; hai original `CN-002`/`CN-041` bị supersede bởi R2. Còn **56 anchor candidates từ 24 ảnh**, không đếm hai crop versions của cùng anchor thành hai mẫu. `CN-041` đầu bị mất head; R2 khôi phục anchor và đổi phone proposal sau visual QA. Giữ originals để trace.

| QA draft sau review | Số |
|---|---:|
| Có ít nhất một target được đề nghị known | 47 |
| U/U auxiliary, ngoài supervision | 9 |
| Phone P / N / U trên 56 active anchors | 11 / 24 / 21 |
| Looking P / N / U trên 56 active anchors | 21 / 23 / 12 |
| Fully known NN / NP / PN / PP | 15 / 8 / 2 / 7 |
| Partial NU / PU / UN / UP | 1 / 2 / 6 / 6 |

Đây là **proposed label counts**, không accepted actual-train counts; canonical values vẫn `[null,null]`, masks `[0,0]`, usage review_only/split null. Owner chỉ cần nghiệm thu batch và ngoại lệ, không phải annotate lại mọi ảnh. Known proposals pin exact crop SHA/input SHA; nếu recrop phải review lại evidence.

| Role reserve của 47 đề xuất | Crops | Phone P/N/U | Looking P/N/U | Giới hạn |
|---|---:|---|---|---|
| Holdout candidate — behavie | 33 | 9/16/8 | 17/15/1 | 4 ranh giới cảnh trong crop batch; phone P mới quan sát ở 2 ranh giới. Independent evidence 0 |
| New-development quarantine — Student instructional | 11 | 0/8/3 | 3/7/1 | 7 view IDs chỉ phục vụ review, không 7 groups độc lập; **thiếu phone P** |
| Train supplement candidate — Student cảnh train | 3 | 2/0/1 | 1/1/1 | Marginal independence bằng 0; không đưa vào evaluation mới |

Pilot bao gồm pen/book/pencilcase, tay chống mặt, gaze sang peer so với giấy riêng, desk/handheld mobile, crowded ownership và co-occurrence. QA không giữ N từ posture/head-down khi gaze bị che, cũng không giữ phone N khi tay dưới bàn. `CN-025` native không đang viết như draft ban đầu: tay dưới bàn, U/U. `CN-026` device category mobile/tablet chưa chắc: phone U. Các ngoại lệ đều nằm trong QA companion và REVIEW.html.

8 matched-pair proposals: 1 phone ownership contrast và 7 looking contrasts, cùng source image nhưng khác anchor/vị trí. Chất lượng scene matching tốt hơn cặp khác phòng; vẫn còn identity/position confounding, không là same-person counterfactual hoặc independent pairs. `CN-001`/`CN-002-R2` giữ mobile của anchor bên cạnh trong context; Student `CN-044`/`CN-056` đối chiếu chống mặt/gaze ngoài bài với viết giấy riêng. Không tự biến “không có box phone” thành negative.

## 4. Khả thi G3 và new-development

**G3 chưa đủ evidence.** Dùng ngưỡng đã đề xuất/owner duyệt để tiếp tục thực hiện, giữ nguyên số; không nới để pass. Hiện chưa có accepted independent test package nên support thực tế mới là 0 P/0 N cho mỗi target, 0 independent groups và 0 accepted verified contexts. Khoảng thiếu vẫn là 100 P + 100 N mỗi target, 10 groups tổng, P/N mỗi loại 5 groups, 2 contexts xác minh.

Nếu **chỉ giả định** 33 nhãn holdout draft được nghiệm thu, phone còn thiếu 91 P/84 N và looking còn thiếu 83 P/85 N để tới count gate. Đây không là tiến độ G3 đã đạt: labels, assignment và independence còn chưa Accepted. Raw annotation count lớn hoặc nhiều frame không thay được gap group/provenance. Cảnh train Student không được bù test support.

Hai ZIP đủ để tiếp tục xây candidate crops, chưa đủ để khẳng định có ≥10 independent groups hay ≥5 phone-P groups. New-development draft 11 crops chỉ có phone N/U; mở thêm writing crops cùng video để vượt 40 không giải quyết phone P hoặc independence. Không freeze cohort chọn epoch với coverage này. Không thể kết luận cả ZIP vĩnh viễn không có cảnh khác từ lượt xem 120; inventory còn là unknown coverage ngoài phần đã review.

Ưu tiên bổ sung theo marginal evidence, chưa dự báo numerical model gain:

| Ưu tiên | Việc cụ thể | Expected marginal value / acceptance |
|---|---|---|
| 1 | Đối chiếu nguồn video/room/camera/session và graph overlap của 6 behavie boundaries + Student instructional; giữ whole-family reserve | Có thể chuyển candidate thành evidenced group; 1 group thật có ích hơn nhiều frame cùng scene. Nếu không xác minh được, giữ quarantine và tìm nguồn mới |
| 2 | Phone P **và** contextual N ở families chưa dùng cho new-development; thêm các phone-P families độc lập còn thiếu của holdout | Giải quyết thiếu phone P ở cohort chọn model và target/group diversity. Không lấy phone families train Student hoặc reserve holdout để bù development |
| 3 | Owner review 47 exact crop/state proposals, 9 U/U và 2 superseded exceptions | Đóng label/geometry QA đã chuẩn bị; chưa tự đóng provenance/split. Không cần owner vẽ lại tất cả bbox |
| 4 | Sau khi group/role rõ, thêm anchors đối kháng trong cùng family đã chọn, ưu tiên mobile thuộc peer, book/pen/chin và side-vs-writing | Tăng contrast evidence và usable known cells; marginal independent groups bằng 0 nếu thêm frame/anchor cùng family |
| 5 | Chỉ mở targeted V7 Unknown re-review khi supplementary train đã Accepted và gap cụ thể vẫn còn | Có thể thêm supervision cho target chưa review; không sửa accepted V7 in place, không cải thiện independent holdout support |

## 5. Unknown taxonomy — điều kiện, không relabel hàng loạt

375 new-train V7 có 256 unknown **target cells**: phone 141 + looking 115, nằm trên 256 partial-known crops; 119 crops fully known. Không có tiêu chí Accepted rằng số train lớn/đủ 375 thì model đạt, cũng chưa có train mới Accepted. Vì vậy chưa kích hoạt sửa 256 cells; masked training vẫn sử dụng các known targets hợp lệ. Gap độc lập không thể đóng bằng relabel train cũ.

[Queue conditional](unknown-review-queue.json) chọn 32 target cells cho lượt QA hữu hạn nếu cần, đa dạng conservative groups/source, ưu tiên input224 chưa có evidence hoặc recrop mismatch. Đây là queue, không phenotype labels hoặc giải phóng U. Evidence taxonomy đề nghị: `not_reviewed_target`, `device_category_unresolved`, `ownership_unresolved`, `hands_or_workarea_occluded`, `gaze_or_workarea_unresolved`, `input224_information_lost`, `intrinsic_static_image_ambiguity`; có nhiều nguyên nhân cùng lúc, cause chưa xem ảnh giữ null. Tách phone geometry/ownership, gaze-to-own-workarea, pen/book/chin/posture/crowding/domain và input224 QA khỏi P/N.

Chỉ đổi U sang P/N sau source → exact crop → input224 có evidence và owner nghiệm thu batch; recrop tạo version/SHA mới, parent/test preservation giữ nguyên. Tạo derivative/release mới nếu thay labels, không mutate V7. Không thêm lớp normal/cheating hoặc giữ N để cân số.

## 6. Thực thi và bàn giao

Đã triển khai reader ZIP pinned, strict full-file YOLO checks, diverse inspection và writer source/crop/input pending trong `src/data/source_review.py`, cùng hai CLI chung. Không sao chép builder v7/trainer E003 hoặc import code từ archive. Test preprocessing so pixel bytes với training consumer; source/pins/duplicate/path/unknown/non-overwrite checks có fixtures. Kết quả checks và exact metadata/payload pins ở validation; software PASS không thay data/model acceptance.

Design/model plan đã owner duyệt; ghi trạng thái hiện hành trong companion execution proposal và decision locator. Bước data F1 chưa đóng; full fine-tune trainer/run/final-test access vẫn theo mốc đã duyệt. Chuẩn bị này chưa tạo experiment execution config khi new-development/holdout và compute wall-time budget chưa pin. Không tự dùng historical val thay new-development, không đổi comparator48/map/added subset hoặc numeric gates.

Review artifacts/media được giữ local để owner nghiệm thu, scratch phụ được dọn sau bảo toàn evidence. Source/ZIP/V7 và tài liệu owner đã approve giữ nguyên hashes. Không commit/stage/upload dữ liệu hoặc mở test.
