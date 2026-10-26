# Stage A detector — triển khai ngày 26/10/2026

## D2 winner và bước crop/G0 hoàn tất

Sau review toàn bộ frame, owner xác nhận D2 không làm mất người, không crop trùng và chốt D2 winner. [Decision mới](../../../configs/runtime/RUNTIME-DETECTOR-REVIEW-20261025/d2-winner-decision-20261026.md) và [receipt](../../../configs/runtime/RUNTIME-D2-20261026/winner.json) supersede trạng thái chưa chọn winner dưới đây; output diagnostic và matching unknown lịch sử giữ nguyên. Đây là nghiệm thu visual trên 19 frame, không tự tạo bảng ground truth hoặc metrics định lượng.

[Revision runtime D2](../../../configs/runtime/RUNTIME-D2-20261026/README.md) đã materialize: NMS IoU 0,30, conf 0,25, còn lại giữ G0/context-v1/calibration và detector weights. Config v3 bắt buộc receipt selection D2 khớp weights/policy; v1/v2 vẫn giữ IoU 0,70. Đã load config thật PASS. Không đổi config cũ hoặc chạy lại toàn video.

Đã thực hiện bước crop/G0 sau detector theo [config và approval mới](../../../configs/runtime/RUNTIME-D2-20261026/crop-review.yaml). Trong 342 anchors D2, 340 anchors giữ exact geometry/confidence và crop/input pixels; tái dùng cached score có source/prediction/crop/input pins. Chỉ 2 crop mới ở frame 1080/1170 cần G0 forwards. Run completed, CLI exit 0, 340 cached + 2 new, 03:37:12–03:37:42 ngày 26/10 giờ Việt Nam. Không gọi đây là full-video inference hoặc 342 lượt inference mới.

| Frame / thời gian | Phone score | Looking score | Cờ theo calibration giữ nguyên |
|---|---:|---:|---|
| 1080 / 36 giây | 0,03364 | 0,14626 | Cả hai dưới ngưỡng |
| 1170 / 39 giây | 0,03811 | 0,13971 | Cả hai dưới ngưỡng |

Ngưỡng giữ 0,5 / 0,3914746344089508. Hai crop mới đã xem trực quan: có anchor đang viết và người khác ở phần dưới context; score thấp không tự nghiệm thu attribution hoặc chứng minh absence hành vi. Detector winner không tự giải quyết khả năng classifier lấy bằng chứng từ người bên cạnh.

- [Gallery 342 crop/input D2 và scores](../../../outputs/runtime-d2-crop-review-20261026/index.html).
- Hai crop mới: [36 giây](../../../outputs/runtime-d2-crop-review-20261026/f00001080-D2-b004-crop.png), [39 giây](../../../outputs/runtime-d2-crop-review-20261026/f00001170-D2-b005-crop.png).
- [Run outcome](../../../outputs/runtime-d2-crop-review-20261026/run.json), [predictions có nguồn cached/new](../../../outputs/runtime-d2-crop-review-20261026/predictions.json), [checksums](../../../outputs/runtime-d2-crop-review-20261026/checksums.json).

Integrity PASS: 11 output files và 684 references crop/input khớp SHA; 340 cached crop/input đã kiểm pixel trước reuse. Checks: 3 tests crop-review, 16 runtime tests (thêm guard v3/selection và bảo toàn v1), 9 detector-review tests PASS; Ruff phần thay đổi, strict mypy toàn 63 source files PASS. Không train/test/tracking/events; không upload hoặc commit. Deadline media kế thừa 01/11/2026 lúc 15:55 giờ Việt Nam.

Scope chọn D2 và kiểm crop/G0 đã hoàn tất. Runtime D2 sẵn dùng; nghiệm thu chất lượng hành vi/attribution và downstream là scope tiếp theo, không tự suy từ quyết định detector.

## Kết quả diagnostic đã được duyệt riêng

Owner trả lời **“Chạy diagnostic, giữ unknown; chưa chọn winner”**. [Decision ngoại lệ](../../../configs/runtime/RUNTIME-DETECTOR-REVIEW-20261025/diagnostic-decision-20261026.md), [config mới](../../../configs/runtime/RUNTIME-DETECTOR-REVIEW-20261025/diagnostic.yaml) và [receipt mới](../../../configs/runtime/RUNTIME-DETECTOR-REVIEW-20261025/diagnostic-authorization.json) cho phép chạy trước census accepted trong scope diagnostic; không thay approval/pins cũ hoặc nghiệm thu nhãn.

Run `RUNTIME-DETECTOR-DIAGNOSTIC-20261026` completed, CLI exit 0, 57/57 forwards (19 mỗi arm). Từ 03:06:10 đến 03:06:31 ngày 26/10/2026 giờ Việt Nam, khoảng 21,12 giây theo timestamps run; không coi đây là SLA hoặc benchmark warmed-up. **D0 khớp exact integer boxes/context/confidence/order của baseline trên đủ 19 frame.** Kiểm SHA-256 đủ 66 files trong manifest output PASS; matching của 1.098 boxes giữ unknown, không có winner hoặc quality metrics.

| Arm | NMS IoU | Tổng box trên 19 frame | Min–max box/frame |
|---|---:|---:|---:|
| D0 | 0,70 | 400 | 19–25 |
| D1 | 0,50 | 356 | 16–21 |
| D2 | 0,30 | 342 | 16–20 |

D1 ít hơn D0 44 boxes; D2 ít hơn D0 58 boxes. Đây chỉ là số detection, **không là số duplicate loại đúng hoặc số người duy nhất**. Chưa xác nhận bảo toàn người bị che, chưa chọn winner, không đổi cấu hình prototype hoặc G0. Kiểm trực quan ba overlay frame 0 cho thấy các box chồng giảm, nhưng quan sát này không thay census/matching hoặc acceptance toàn cohort.

- [Gallery so sánh D0/D1/D2 theo từng frame](../../../outputs/runtime-detector-diagnostic-review-20261026/index.html), [audit kỹ thuật và counts từng frame](../../../outputs/runtime-detector-diagnostic-review-20261026/audit.json).
- [Run outcome](../../../outputs/runtime-detector-diagnostic-20261026/run.json), [checksums](../../../outputs/runtime-detector-diagnostic-20261026/checksums.json), [matching unknown](../../../outputs/runtime-detector-diagnostic-20261026/matching-draft.json). Output run giữ nguyên; gallery companion chỉ link ảnh, không copy media.
- 9 tests detector-review PASS, Ruff/strict mypy phần source mới PASS. Guard v1 vẫn yêu cầu census accepted; v2 cần approval diagnostic riêng, exact draft pin và decision pin. Test xác nhận unknown giữ nguyên và winner null. Không chạy thêm classifier, train hoặc test; không stage/commit.

Scope diagnostic đã hoàn tất. Nếu tiến tới đánh giá chất lượng/chọn arm, bước tiếp là review census và matching; không tự chạy thêm inference. Deadline media giữ 01/11/2026 lúc 15:55 giờ Việt Nam.

## Hồ sơ triển khai trước ngoại lệ diagnostic

Owner duyệt proposal đang mở bằng “approve, hãy thực hiện tiếp đi!”. Approval được materialize riêng ở [receipt](../../../configs/runtime/RUNTIME-DETECTOR-REVIEW-20261025/stage-a-authorization.json) và [config](../../../configs/runtime/RUNTIME-DETECTOR-REVIEW-20261025/stage-a.yaml), giữ nguyên snapshot proposal. Scope: D0/D1/D2, review theo người/frame, giảm duplicate extras không mất người baseline, role unknown diagnostic. Không đổi classifier, train, restore A1/Dual ROI hoặc mở tracking/events.

## Implementation và inputs

CLI `ai_exam_monitoring.inference.detector_review` tái dùng person adapter/crop geometry, không nới loader prototype. Kiểm config approval, proposal/cohort/session/rights/checksums/PNG/cached predictions; kế thừa deadline media 01/11/2026 lúc 15:55 giờ Việt Nam. Preflight local đã PASS, chưa gọi detector/classifier.

Run yêu cầu census được owner nghiệm thu trước load detector. D0 chạy trước toàn bộ candidates; phải trùng exact integer person/context boxes, confidence và thứ tự của cached baseline. Không có float boxes lịch sử để khẳng định float parity; kết quả mới giữ float trước rounding. Drift làm run failed và dừng trước D1/D2. Mỗi arm gọi detector lại trên PNG nguồn, không NMS lần hai trên cached output. Giữ CPU FP32 và số threads baseline.

Output mới chứa config/approval/review/code/environment, detections JSONL, overlay, matching draft, run outcome và checksums; không overwrite. Không chọn winner từ số detection. Candidate matching sau run vẫn phải review trên census trước tính miss/duplicate extras hoặc chốt winner; công cụ này chưa tự nghiệm thu chất lượng.

## Cohort review còn thiếu

[Batch đã có](../../../outputs/runtime-detector-review-20261025/index.html) giữ 19 frames và 12 cặp candidate. [Census draft](../../../outputs/runtime-detector-review-20261025/person-review-draft-20261026.json) được tự điền từ baseline; chỉ gộp nhóm theo các quan hệ `same_person_candidate` đã có. Không tự đặt threshold hình học hoặc dùng score classifier để quyết định cùng người. Các nhóm còn có thể trùng/sai/thiếu; chưa kiểm được toàn bộ người baseline bỏ sót. Role và identity không suy từ hình ảnh.

Owner review batch và ngoại lệ: xác nhận/sửa nhóm cùng người, box giả, bổ sung người có trong source nhưng baseline bỏ sót. Agent cập nhật bản census mới từ phản hồi; không sửa cohort gốc. Census accepted cần đủ 19 frame theo đúng thứ tự, mỗi người có mã local và mô tả vị trí, mỗi anchor baseline map tới mã người hoặc null cho box giả đã xác nhận, không còn unknown. `complete_visible_person_census=true` chỉ sau review đủ toàn frame; status/reviewer/decision_ref ghi đúng bằng chứng owner. Không đổi draft thành accepted chỉ vì approval thiết kế.

Ở thời điểm bàn giao implementation ban đầu, chưa chạy 57 detector forwards vì proposal yêu cầu “Sau owner chốt A và cohort review”. Ngoại lệ diagnostic và kết quả mới ở đầu hồ sơ này thay trạng thái chờ run; census vẫn chưa accepted.

## Commands

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.inference.detector_review --config configs/runtime/RUNTIME-DETECTOR-REVIEW-20261025/stage-a.yaml --preflight-only
```

Sau có census accepted mới, truyền `--review <đường dẫn census accepted>` và `--output outputs/runtime-detector-a-20261026` thay cho `--preflight-only`. Nếu đường dẫn output đã tồn tại, phải xem trạng thái cũ trước quyết định run identity tiếp theo; không xóa để chạy lại. Census là dữ liệu local và không chứa danh tính thật.

## Checks

Synthetic tests kiểm hình học float/integer, parity drift, no-overwrite, draft/unknown/incomplete review bị chặn trước detector, mỗi arm gọi detector thật qua adapter được inject trong fixture, completed/failed/checksums/retention, và draft grouping không mutate input. Runtime regression dùng fixtures, không inference media thật. Lint và strict typing phần source mới PASS. Không commit/stage; bảo toàn các thay đổi có sẵn trong workspace. Software PASS không là chất lượng detector PASS.
