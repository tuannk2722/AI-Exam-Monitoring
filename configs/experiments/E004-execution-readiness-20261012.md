# E004 — Đầu vào cần đóng trước release và chạy thật

Ngày 2026-10-12. Bảng chuẩn bị quyết định, **không phải runnable config hoặc approval**. Thiết kế và 56 anchors đã được owner duyệt; không yêu cầu duyệt lại. [Execution companion](E004-data-execution-20261011.md) giữ lifecycle dữ liệu; [software evidence](../../artifacts/reports/E004-software-readiness-20261012/README.md) giữ kết quả implementation.

## Dữ liệu cần bổ sung

Lượt bổ sung đã được owner approve thực hiện, không yêu cầu tìm đủ 100% trong một lượt: [batch mới 20 crop/24 nguồn](../../artifacts/reports/E004-source-review-20261011/support-expansion-20261012/REVIEW.md) đang chờ nghiệm thu. Đề xuất phone 7 P/9 N/4 U, looking 10 P/10 N; chưa cộng vào accepted support. Chỉ đạo tiến độ một phần không tự thay quyết định giữ support cũ.

Quyết định cuối ngày 12/10 ở mục revision bên dưới: chỉ miễn chứng minh independence; giữ support cũ. Những yêu cầu independence trong bảng mô tả protocol gốc được miễn cho revision mới, không tiếp tục yêu cầu owner cung cấp mapping chỉ để chứng minh independence. Source identity, quyền dùng, membership và kiểm overlap vẫn cần giữ; không tự tạo evidence giả.

| Đối tượng | Hiện có | Điều kiện đóng |
|---|---|---|
| Nhãn/geometry | 56 active anchors accepted, 49 có target known, 7 U/U auxiliary | Đã đóng; giữ review-only tới khi role/group được chốt |
| Provenance | ZIP metadata không có mapping video/session/phòng/camera; scene graph chỉ quarantine | Mapping ZIP member hoặc source SHA → video/session/family/context, kèm evidence gốc và nghiệm thu whole-family |
| New-development | Reserve 12 crops; phone 0 P/7 N/5 U | Bổ sung phone P từ families độc lập với train/holdout; nghiệm thu membership/roles |
| Holdout | Reserve 33 known crops; phone 10 P/19 N/4 U, looking 19 P/13 N/1 U; chưa proven independence | Giữ G3: mỗi target ≥100 P/100 N, ≥10 independent groups, mỗi P/N ≥5 groups, ≥2 verified contexts; accepted new test support hiện 0 |
| Slices | Có thiết kế context slices; chưa exact enrollment/bins | Chốt definitions/membership trước training, không dựa scores hoặc P-only; thiếu 20 P/20 N/3 groups thì INCONCLUSIVE |

Bước tiếp là bổ sung đủ P/N và support theo quyết định đã giữ, ưu tiên dữ liệu local đã có quyền; agent dựng shortlist/crops/QA từ evidence thật để owner nghiệm thu batch/ngoại lệ. Mapping/video gốc nếu có vẫn hữu ích, nhưng chứng minh independence không còn là điều kiện của revision. Không tự điền group/context IDs hoặc nới các support khác.

Không cần tạo release train mới chỉ để đổi trainer. Chỉ tạo derivative/version mới khi có bổ sung train đã nghiệm thu; new-development và holdout là packages độc lập, không mutate V7.

## Compute đã được owner đồng ý

| Action | Trần đề xuất | Điều kiện |
|---|---|---|
| Smoke control và candidate | Mỗi ID 30 phút, 2 epochs, CPU 4 threads/batch 16; recovery drill trong cùng budget | Exact data/config approval; kiểm updates/BN/full checkpoint/reload/resume/time/RSS, không là quality evidence |
| Matched control và candidate | Mỗi ID 8 giờ tích lũy, tối đa 50 epochs theo early stop đã duyệt; tổng trần 16 giờ | Smoke PASS và G0–G3; nếu smoke cho thấy không phù hợp thì đề xuất budget/config identity mới, không tự tăng trần/đổi batch |
| Final test | Chưa xin mở | Một candidate, exact protocol/checkpoint/payload và owner decision riêng |

Owner trả lời “Đồng ý các trần đề xuất” ngày 2026-10-12: smoke 30 phút/model, 2 epochs; matched runs 8 giờ/model, tối đa 50 epochs, tổng 16 giờ; CPU 4 threads/batch 16. Đây là approval budget, chưa phải exact config/data/test approval hoặc runtime đã đo. Run budget tính cả preparation/reporting; deadline kiểm giữa các bước, không hard-kill kernel đang chạy. Recipe khác giữ nguyên thiết kế đã duyệt: seed 42, FP32, ảnh 224, AdamW head LR 0.001/layer4 LR 0.0001, weight decay 0.0001; BN eval; patience 10/min_delta 0.0001/threshold 0.5.

## Quyết định revision promotion ngày 2026-10-12

Owner đã trả lời: “giữ hướng promotion, không cần độc lập gì cả.” Đây là quyết định miễn yêu cầu chứng minh independence cho revision mới; không phải evidence rằng dữ liệu độc lập. Không tiếp tục hướng exploratory đã đề xuất. Budget đã approved giữ nguyên.

Owner đã chốt câu hỏi tiếp theo: **“Chỉ miễn independence, giữ support cũ”**. Vì vậy không dùng val 49 cho phương án promotion nội bộ thay cohort đủ support; mỗi target vẫn cần ≥100 P và ≥100 N. Không tự miễn số nhóm/context, slice support hoặc M1–M7 khác từ quyết định miễn independence. Test cũ tiếp tục đóng; không dùng dữ liệu train để bù support đánh giá.

Riêng reserve holdout hiện có, ngay cả nếu cả 33 crops được chốt role, phone còn thiếu ít nhất 90 P và 81 N; looking còn thiếu ít nhất 81 P và 87 N. Đây là thiếu hụt theo từng target, không cộng thành số ảnh vì một ảnh có thể phục vụ cả hai target; Unknown không tính thành N. Accepted new test support hiện vẫn 0 do chưa freeze package/membership. Cần bổ sung và nghiệm thu trước promotion run theo kế hoạch đã giữ.

Implementation hiện giữ guards của protocol gốc; khi đủ dữ liệu sẽ tạo revision config/protocol thể hiện waiver tường minh, giữ nguyên support và snapshots lịch sử. Không dùng flag independence=true giả hoặc reseal approval cũ để vượt guard.

## Hồ sơ sẽ tạo sau khi đủ evidence

1. Packages/manifest/ledger/splits/rights/QA và acceptance receipts có version.
2. `matched-protocol-v1`: exact cohort IDs/order/record digest, family assignments/evidence, reserved holdout payload/source SHA/family IDs và slice enrollment. New-development selection; comparator 48/full val 49 diagnostic.
3. `adaptation-readiness-v1`: scope smoke hoặc promotion, protocol/cohort/evidence pins và G0 hoặc G0–G3 theo action. Không đánh dấu true khi thiếu evidence.
4. Hai configs `matched-adaptation-v1` với exact pins/budget/owner và approval digest từng ID. Cùng head snapshot tạo bằng `adaptation_model.create_initial_head`; `verify_matched_configs` kiểm recipe/init/cohorts. Smoke có identity riêng.
5. Smoke → matched pair → development benchmark bằng canonical `training.evaluate --split val --benchmark` → quyết định candidate → final protocol riêng. FINISHED không tự Selected; M1–M7 vẫn cần evidence/owner acceptance.

Chưa tạo YAML runnable vì package/protocol pins chưa tồn tại; không dùng SHA giả. Thiết kế approved không thay thông tin nguồn hoặc acceptance của dữ liệu chưa có.
