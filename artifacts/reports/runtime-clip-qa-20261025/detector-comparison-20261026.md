# Đối chứng D2 / V8S / V10S — 26/10/2026

## Trạng thái

Run completed đủ 38/38 frame forwards, không rerun/sweep, classifier inference hoặc đổi variables. Owner đã duyệt variables và scope, rồi xác nhận census đủ/đúng sau bốn sửa đổi. [Authorization](../../../configs/runtime/RUNTIME-DETECTOR-COMPARISON-20261026/authorization.json), [census acceptance](../../../configs/runtime/RUNTIME-DETECTOR-COMPARISON-20261026/census-acceptance.json), [accepted census](../../../configs/runtime/RUNTIME-DETECTOR-COMPARISON-20261026/accepted-census.json) bảo toàn approval exact snapshots.

Census có 334 person-frame groups trong 19 frame, không 334 danh tính. 342 D2 anchors được gộp theo 8 same pairs, không false boxes/missing people theo owner acceptance. D2 do đó có 8 duplicate extras trên cohort này; không tự suy chất lượng crop/behavior toàn clip. Bốn same mới ở 0/33/39/43 giây chưa có keeper riêng accepted; không cần tự chọn để đánh giá số duplicate. Giữ bốn keeper trước.

## Execution và outputs

[Run/gallery](../../../outputs/runtime-detector-comparison-20261026/index.html), [run record](../../../outputs/runtime-detector-comparison-20261026/run.json), [acquisition](../../../configs/runtime/RUNTIME-DETECTOR-COMPARISON-20261026/acquisition.json). V8S và V10S load/taxonomy/end2end preflight PASS, không predict thêm ngoài 38 frame. CPU FP32, 4 threads, seed 20261026, 640/conf 0,25; V8S IoU 0,30, V10S end2end không thêm NMS. D2 cached. Khoảng 23,33 giây đoạn run sau environment capture, không benchmark/SLA.

| Arm | Tổng boxes / 19 frame | Quality acceptance |
|---|---:|---|
| D2 | 342 | Census accepted; 8 duplicate extras |
| V8S | 364 | Matching/crop pending |
| V10S | 340 | Matching/crop pending |

Không chọn winner theo tổng box. Hai model mới vẫn có thể vừa miss vừa duplicate hoặc box giả.

## Matching cần review

[Gallery matching và context crops](../../../outputs/runtime-detector-matching-review-20261026/index.html), [manifest draft](../../../outputs/runtime-detector-matching-review-20261026/matching-draft.json), [config pins](../../../configs/runtime/RUNTIME-DETECTOR-COMPARISON-20261026/matching-review.yaml). Mỗi frame/arm có source, census overlay và candidate overlay b → p, cùng context crops. Ranking bằng max IoU với các box của một census group chỉ hỗ trợ shortlist; accepted_person_id=null cho cả 704 boxes. Tất cả candidates có giao nhau được lưu, không threshold identity mới và không tự nhận nearest/max-IoU là người đúng.

Draft không có box đề xuất tới 3 person-frame groups ở V8S và 32 ở V10S. Đây chưa là miss metrics: mapping sai có thể làm tăng/giảm số này. V8S shortlist: 0 giây p009, 56/59 giây p017. Owner cần nghiệm thu mapping/ngoại lệ và crop evidence trước báo duplicate/miss/false/quality của hai candidates. Đã xem mẫu overlay V10S 36 giây và V8S 0 giây; không biến visual observation của agent thành acceptance.

Owner có thể xác nhận batch đúng và chỉ sửa ngoại lệ theo model/giây/b/p; không yêu cầu annotate từng ảnh lại. Sau review tạo receipt mới, tổng hợp metrics theo census, giữ unresolved riêng. Nếu không arm nào đạt mục tiêu development thì không chọn winner, không tự tuning hoặc mở confirmation/video/tracking.

## Checks và lifecycle

4 tests census gate, 2 tests ranking PASS. Ruff phần mới và strict mypy 69 source files PASS. CI bổ sung cả hai suites. Run checksums 100 files, matching checksums 782 files và toàn bộ links PASS; 38 records/704 draft assignments giữ unknown acceptance. Context crop mới là derivative để review, không có G0 score. Giữ deadline nguồn 01/11/2026 15:55 Việt Nam, không upload, stage/commit hoặc sửa outputs đã pin. Không scratch checkout cần dọn; weights/overlays/crops là evidence hiện hành.

## Owner chấp nhận V8S có giới hạn

[Review V8S r1](v8s-owner-review-20261026-r1.json) ghi acceptance prototype thực dụng: owner chấp nhận chất lượng hiện tại, không cần tuyệt đối. Điều này thay yêu cầu zero-error cho acceptance cụ thể này; không tự khai quality gate cũ PASS hoặc yêu cầu owner review V10S để được dùng V8S.

Owner báo miss ở giây0 p009/p015, giây56 p017, giây59 p017; duplicate giây33 b009/b012 → p006, giây36 b017/b018 → p015, giây52 b019/b017 → p008. Mã bị che giây36 được resolve từ exact manifest. Đây là các lỗi owner đã nêu, không tự khẳng định danh sách lỗi exhaustive hoặc lấy 364 boxes trừ census để suy metrics.

Có conflict reference mới ở giây0: b011 của V8S bắt người đội mũ phía xa, mapping draft gán p015 nhưng p015 census là người áo xanh cúi ở hàng trước. Đã xem overlay/source và hỏi owner bổ sung nhóm người đội mũ vào census; không sửa accepted census/pins hoặc coi box đó false positive. Acceptance V8S vẫn được giữ riêng với chất lượng census/mapping. Không tính aggregate precision/recall khi conflict này chưa resolve.

Runtime loader hiện v3 còn khóa winner D2; chưa thay guard/config hoặc chạy G0/video trong bước ghi nhận review. Tiếp theo sửa reference bằng addendum theo phản hồi, rồi chuẩn bị revision V8S và crop/G0 QA có scope rõ; không tiếp tục săn zero-error hoặc sweep detector.

## Correction accepted: thêm người đội mũ giây 0

Owner xác nhận cần bổ sung người đội mũ. [Census r2](../../../configs/runtime/RUNTIME-DETECTOR-COMPARISON-20261026/accepted-census-r2.json) và [decision correction](../../../configs/runtime/RUNTIME-DETECTOR-COMPARISON-20261026/census-correction-20261026-r2.json) supersede riêng frame0 của census trước, giữ nguyên các files đã pin. Người mới là p019, không có D2 anchor; V8S f00000000-V8S-b011 → p019 được xác nhận, thay draft p015. Location box lấy từ V8S chỉ là locator, không bbox ground truth được owner vẽ/nghiệm thu. Giữ p009/p015 là hai miss V8S owner đã báo ở frame0.

Census hiện có 335 person-frame groups, 342 D2 anchors; D2 có 1 miss đã xác nhận và 8 duplicate extras trên reference đã sửa, thay kết luận trước đó không có miss. Không tự suy người mới xuyên các frame khác. [V8S review r2](v8s-owner-review-20261026-r2.json) giải quyết pending này, giữ acceptance prototype có lỗi; không tự biến toàn bộ 364 mappings thành accepted hoặc tính aggregate precision/recall. V10S chưa nghiệm thu.

Checks: thêm đúng 1 group ở frame0, giữ nguyên 18 frame khác và 342 D2 anchor references; JSON/pins/diff PASS. Không inference hoặc chỉnh runtime trong correction này. Bước tiếp theo là revision runtime V8S và crop/G0 QA với acceptance thực dụng đã được owner xác nhận; không tiếp tục tối ưu zero-error.
