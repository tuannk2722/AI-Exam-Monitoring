# E004 — Kết quả hiện hành sau QA native bổ sung

Đây là **bản hiện hành để owner review batch**. [README đầu](README.md), QA/summary/pairs đầu và [validation đầu](validation.json) giữ nguyên vì đã được audit pin. Bản này supersede **counts và label/geometry proposals ở §§3–4 của README đầu**, không thay source/lineage analysis, approval hoặc numeric gates. [Delta QA](qa-update-decisions.json) ghi từng thay đổi và lý do.

**Đã hoàn thành phần thẩm định/chuẩn bị dữ liệu:** xem đủ 40 ảnh shortlist gốc, mở rộng và xem 120 ảnh; tạo và QA 59 crop versions ở native/input 224. Có **47 proposals** từ 56 active anchors/24 ảnh, 9 U/U auxiliary và 3 versions superseded. **Independent group evidence vẫn bằng 0; chưa có crop mới Accepted vào train/development/test.**

## Kết quả source và tính khả thi

[Từng ảnh gốc 40](shortlist40-assessment.json), [toàn 120](inspection-assessment120.json) và [family evidence](scene-family-review.json) giữ exact ZIP/member/source/label pins, mô tả cảnh, overlap/provenance flags và crop feasibility. Hai ZIP được kiểm toàn file YOLO, quarantine 2 Student label files lỗi; không map source classes thành targets. Không đọc media/predictions test 11 hoặc candidate scores.

36 Student sources cùng ba cảnh train V7, gồm 12 original shortlist; không đủ điều kiện independent holdout/new-development. Các nearest comparisons non-test không thấy trùng **không** chứng minh disjointness. 60 behavie images đang reserve candidate holdout; 23 Student instructional images quarantine candidate development; 1 semantic-error image không chọn crop. IDs/phòng/session/person/video chưa chứng minh giữ null.

G3 vẫn cần 100 known P + 100 N mỗi target, ≥10 independent groups, P/N mỗi loại ở ≥5 groups, ≥2 verified camera/room contexts. Accepted new test support hiện 0 nên gap thực tế vẫn toàn bộ ngưỡng trên. Hai ZIP có giá trị crop/contrasts nhưng lượt xem này chưa chứng minh khả năng đóng G3; các phần ngoài 120 inspected images vẫn unknown coverage.

## Batch sau native follow-up

Mở [REVIEW.html local](../../../data/interim/E004-source-review-20261011/REVIEW.html), [QA hiện hành](pilot-input224-review-current.json), [summary](pilot-summary-current.json) và [pairs](pilot-pairs-current.json). Các thẻ hiển thị source/anchor/context → crop native → input 224, state proposals, reasons và hashes; bấm ảnh để xem native.

| Active QA proposals | Phone | Looking |
|---|---:|---:|
| P | 11 | 23 |
| N | 22 | 19 |
| U | 23 | 14 |

Trong 47 proposals có ít nhất một target được đề nghị known: PP 7, PN 2, PU 2, NP 9, NN 10, NU 3, UP 7, UN 7. **Canonical values vẫn null/mask 0 và review_only/split null**, vì chưa có owner acceptance cho batch mới. Không cộng Draft counts vào actual-train V7.

| Reserve role | Proposals | Phone P/N/U | Looking P/N/U | Independent evidence |
|---|---:|---|---|---:|
| Holdout candidate — behavie | 33 | 9/15/9 | 19/11/3 | 0 |
| New-development quarantine — Student instructional | 11 | 0/7/4 | 3/7/1 | 0 |
| Train supplement candidate — cảnh Student đã train | 3 | 2/0/1 | 1/1/1 | 0 |

`CN-002`, `CN-041`, `CN-035` originals bị supersede; dùng R2. `CN-035-R2` mở rộng vùng trái để giữ cả bàn tay cầm bút, không apply QA crop cũ lên SHA mới. Native review sửa phone N của `CN-032` vì tay dưới bàn; sửa gaze của `CN-005`/`CN-013` nhìn ngoài giấy; giữ gaze U khi tóc che ở `CN-006`/`CN-034`, phone U ở `CN-050`. Các thay đổi này giảm known support thay vì giữ N để đạt số.

Còn 6 matched-pair proposals hợp lệ với QA hiện hành: 1 phone ownership contrast và 5 looking contrasts. Cùng source image nhưng khác anchor/vị trí, **không** same-person counterfactual hoặc independent pairs. Hai pair dùng looking N cũ của CN-005/CN-013 đã bị loại. CN-035 pair dùng R2 với exact crop SHA mới.

Nếu chỉ **giả định** 33 draft labels reserve holdout được nghiệm thu, count shortfall sẽ là phone 91 P/85 N, looking 81 P/89 N. Chưa thể công nhận tiến độ G3 vì group/assignment/independence chưa Accepted. Phone P trong crop batch này ở 2 ranh giới cảnh quan sát; không phải ≥5 independent phone-P groups. New-development thiếu phone P; tăng thêm writing frames để vượt 40 không giải quyết gap đó.

## Ưu tiên và Unknown taxonomy

Ưu tiên tiếp theo: xác minh provenance/overlap cho whole-family reserves; tìm phone P và contextual N ở families chưa dùng cho new-development và các phone-P groups còn thiếu của holdout; owner nghiệm thu batch/exceptions; sau group/role acceptance mới bổ sung contrasts trong family được chọn. Một evidenced group mới cải thiện support độc lập; thêm nhiều frames cùng scene có marginal independent-group value bằng 0. Chưa dự báo model gain bằng phần trăm.

V7 vẫn có 256 unknown target cells, phone 141 + looking 115; chưa có supplementary train Accepted hoặc outcome để kết luận train đã đủ/thiếu. [Queue 32 cells conditional](unknown-review-queue.json) và taxonomy đề nghị trong README đầu chưa activated; cause chưa xem ảnh giữ null. Chỉ review target còn thiếu bằng source/crop/input224, không đổi class formulation hoặc auto gỡ U từ read/write/normal. Nếu đổi labels/crop cần derivative/version mới và owner review, giữ V7/parent/test bytes.

## Approval, software và reproducibility

[Owner direction](owner-direction.json) đã approve các báo cáo/đề xuất trước và preparation scope, quyền nguồn local có hiệu lực. [Execution companion](../../../configs/experiments/E004-data-execution-20261011.md) ghi design approval theo đúng scope; vẫn cần nghiệm thu **batch mới**, group/roles/cohorts và exact runnable config/compute budget trước các mốc tiếp theo. Numeric G0–G5/M1–M7 không đổi, không claim model gates PASS.

Source-review module và 2 CLI đã triển khai; 6 review tests, 30 pilot tests PASS; Ruff/compile và strict mypy gồm package/checker/2 CLI (35 files) PASS. Pixels của 59 crop/input versions tái tạo đúng từ original source bytes; 3 follow-up crops rebuild bằng CLI mới cùng hashes, 80-image expansion order rebuild đúng từ inventory. Exact builder snapshots và parent comparison boards được giữ local, scratch phụ đã dọn. [Checks](software-checks.json), [validation hiện hành/pins](validation-current.json).

`check_repo.py --require-git` báo 7 delivery files chưa nằm trong Git index, gồm 6 file mới của preparation/execution và freeze proposal đã có từ task trước. Chưa stage/commit vì user chưa yêu cầu; Git delivery gate chưa PASS. Điều này không thay kết quả pixel/data/software checks hoặc data/model acceptance. Không sửa report/config đã pin để qua checker/gates.

Phần yêu cầu thẩm định, feasibility, conditional taxonomy và pilot đã có concrete review package. Đóng new-development/holdout vẫn phụ thuộc evidence đang thiếu, không thể tự cấp independence. Full fine-tune trainer/smoke/run/final evaluation là các mốc tiếp theo của plan đã duyệt, chưa được thực hiện trong preparation này.

## Ý kiến và Nghiệm thu của Owner (2026-10-12)

| ID | Ý kiến nghiệm thu của onwer | Phân tích của onwer |
|---|---|---|
| E004-CN-004 | U/N | Hướng đầu về bài làm nhưng có hơi cúi xuống dưới bàn |
| E004-CN-006 | N/P | Với tư thế như vậy thì chắc chắn là đang nhìn sang bên trái rồi |
| E004-CN-007 | N/N | Đầu vẫn đang hướng vào bài làm, chỉ có hơi chếch nhẹ sang bên thôi |
| E004-CN-010 | Bạn xem xét lại | Tôi không thấy vật gì ở tay hay trên bàn cả |
| E004-CN-011 | Bạn xem xét lại | Một tay có tư thế đang cầm gì đó để vẽ/viết, chứ tôi cũng không thấy có vật gì gần tay cả |
| E004-CN-012 | Bạn xem xét lại | Khi zoom thì tôi thấy ko có vật gì cả, hoặc khó phân biệt như vậy thì để unknown |
| E004-CN-019 | Bạn xem xét lại | Không hề có dấu hiệu phone, 2 tay đặt trên bàn |
| E004-CN-020 | Bạn xem xét lại | Không hề có dấu hiệu phone, 2 tay đặt trên bàn |
| E004-CN-026 | P/N | Vật là phone |
| E004-CN-031 | Crop đang bị có 2 người | Kiểm tra lại xem vì bên trên đã có crop từng người trong này rồi |
| E004-CN-034 | N/P | Crop này hình như đã có rồi mà |
| E004-CN-036 | Xem xét lại | Người đang đứng thì xử lý như nào? |
| E004-CN-039 | Xem xét lại | Trông không hề có tư thế hay gì đó liên quan đến việc sử dụng phone thì xử lý sao? |
| E004-CN-040 | Xem xét lại | Hướng nhìn như vậy thì chắc chắn là không looking_around rồi |
| E004-CN-043 | Xem xét lại | Hướng đầu và writing mà không tình N được hả? |
| E004-CN-041-R2 | P/P | Hướng nhìn sang bên cạnh |
