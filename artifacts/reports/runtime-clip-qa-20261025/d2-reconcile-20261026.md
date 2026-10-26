# Đối soát ngoại lệ D2 và readiness — 26/10/2026

## Phản hồi owner đã nhận

**Làm rõ đã hoàn tất:** [review r2](owner-review-20261026-r2.json) supersede phần pending của r1, giữ r1 và batch gốc nguyên vẹn. C01: phone trong crop rộng thuộc người đội mũ bên cạnh; không tự suy mọi nhãn của anchor. C03 cả hai U/N, không xác nhận phone presence. C05 giây 59 có phần đầu nhưng không đủ quan sát hành vi: U/U; không phải case detector false positive. Các nhãn C04, C05 giây 36, C06, C07 và quan hệ C01/C02 giữ nguyên. Unknown hợp lệ vẫn giữ, không ép thành N. Pins 12 crop đã kiểm PASS.

Đã chuẩn bị [thiết kế duplicate draft](../../../configs/runtime/RUNTIME-D2-RECONCILE-20261026/duplicate-design.md): tách same-person matching, chọn crop đúng anchor và bảo toàn người khác bị che; không chọn rule/threshold tùy ý. Phần triển khai số còn cần cohort đối chứng và quyết định variables, không tự chạy inference mới.

[Addendum r1](owner-review-20261026-r1.json) pin exact batch và crop SHA, giữ nguyên draft/output cũ. Owner xác nhận **C01/C02 đều cùng người**; vì vậy D2 còn duplicate đã xác nhận trên cohort, vẫn giữ D2 làm baseline đã chọn, không sửa receipt winner cũ. Phạm vi tiếp theo: **mọi người, diagnostic, runtime role unknown**.

| Case | Nhãn phone / looking ghi nhận | Đối chiếu cached output |
|---|---|---|
| C03 giây 56 | U / N; phone chờ làm rõ | Looking vượt ngưỡng: false positive theo owner review |
| C03 giây 59 | U / N; phone chờ làm rõ | Looking dưới ngưỡng |
| C04 | U / U | Không đánh giá đúng/sai từ unknown |
| C05 giây 36 | N / P; owner ghi chú giám thị | Cờ N/P khớp; role không tự thành runtime filter |
| C05 giây 59 | U / U tạm giữ | Câu mô tả chưa rõ; đã hỏi lại |
| C06 cả hai crop | N / N, anchor áo trắng | Cờ N/N khớp |
| C07 | P / N, phone thuộc anchor | Cờ P/N khớp |

Không tổng hợp accuracy từ shortlist hoặc gọi phone C03 false negative khi chưa rõ presence. Nhận xét looking N của người đội mũ được giữ nguyên, chỉ map tới hai anchor C03 đã xác định; không tự gán xuyên mọi frame thiếu mapping/track. Cụm “điện thoại trong crop rộng” có thể liên quan C01; đã hỏi để phân biệt ownership đó với phone presence C03 ở giây 56/59.

Tiếp theo phần độc lập: chuẩn bị thiết kế xử lý duplicate có kiểm bảo toàn người bị che và giữ evidence thuộc anchor. Không hạ IoU thêm chỉ để loại cặp C01/C02, không chọn box bằng score classifier. Candidate suppression và tiêu chí/variables phải được review trước chạy; không thay D2/G0 hoặc mở tracking/events từ phản hồi nhãn này.

Owner duyệt hướng audit status, yêu cầu triển khai và hỏi khi chưa rõ. Giữ D2 winner; evidence mới ghi riêng, không sửa quyết định/pins cũ.

## Batch và phần còn chờ

[Gallery 7 nhóm ngoại lệ](../../../outputs/runtime-d2-reconcile-20261026/index.html), [manifest draft](../../../outputs/runtime-d2-reconcile-20261026/review.json), [config](../../../configs/runtime/RUNTIME-D2-RECONCILE-20261026/batch.yaml). Source → overlay → crop → input; scores mở riêng, owner decisions null. Không inference mới.

- C01, giây 23: b015/b016 cùng tồn tại, box nhỏ nằm trong box lớn, float IoU 0,28061 < 0,30. Draft cùng người; phone scores 0,174/0,927. Crop rộng chứa vùng người/thiết bị bên cạnh; ownership cần xác nhận.
- C02, giây 36: b014/b015 cùng tồn tại; hai crop đều thấy người áo xanh đang viết giữa-trái. Draft cùng người, chưa chọn box giữ.
- C03, giây 56/59: người đội mũ và vật nhỏ cạnh tay/bàn. Phone score thấp không chứng minh false negative; draft unknown chờ xác nhận vật và ownership.
- C04/C06/C07: crop nhạy, hai crop mới, case đối chiếu; chờ nhãn hai hành vi riêng. C05 tách vai trò/eligibility khỏi nhãn hành vi.

Đã hỏi owner xác nhận C01/C02, scope mọi người diagnostic hay thí sinh được chỉ định, và nhãn P/N/U C03–C07. Approval triển khai không biến draft thành accepted. Không tự chọn suppression, threshold hoặc tracker khi các quyết định còn thiếu.

## Retention và CI

Đã bỏ `now + 7 ngày` khi khởi động/hoàn tất runtime. Run mới cần absolute `media_delete_by`, timezone-aware, còn hạn và không quá 7 ngày. Kiểm trước tạo output/load model, trong decode, trước frame và trước completed; success/failure giữ deadline ban đầu. Hết hạn trước xử lý frame không xuất failed-frame media.

Receipt `runtime-media-approval-v2` hỗ trợ `parent_session` path/SHA, kiểm cùng source và deadline không muộn hơn parent. V1 đọc lịch sử được; run mới thiếu absolute deadline bị chặn, cần receipt mới đúng scope, không sửa receipt đã pin. Đây là thực thi policy hiện có, không tự gia hạn hoặc xóa media.

CI classifier job thêm `test_detector_review.py` và `test_selected_crop_review.py` để không chỉ discover trong job base có thể skip do thiếu Torch. Không đổi dependencies.

## Checks và bàn giao

19 runtime tests, 9 detector-review tests và 3 selected-crop tests PASS; Ruff phần đổi PASS; strict mypy toàn 64 source files PASS. Batch kiểm pins/refs và deadline trước tạo. Phần review nhãn/eligibility vẫn chờ owner; không chạy thêm inference hoặc stage/commit. Không scratch/checkout mới; giữ deadline nguồn.
