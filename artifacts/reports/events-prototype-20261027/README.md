# Temporal event candidates — 27/10/2026

Đã thực hiện đúng [proposal owner duyệt](../../../configs/events/EVENTS-PROTOTYPE-20261027/execution.md): implementation, synthetic tests và **một cached replay**, outcome completed. Không audit lại toàn clip tracking, không model inference mới, không export media.

| Hành vi | Candidates | Dương có ID | Support candidates | Support chuỗi ngắn | Âm có ID | Null track |
|---|---:|---:|---:|---:|---:|---:|
| phone_use | 20 | 293 | 202 | 91 | 859 | 10 |
| looking_around | 35 | 252 | 132 | 120 | 900 | 10 |

Tổng **55 candidates**, 169 chuỗi dương chưa đủ điều kiện; 0 unknown trong input hiện tại. Mỗi nhãn đối soát đủ 1.162 observations: dương + âm + unknown + null. Mỗi observation dương có ID được phân vào support candidate hoặc chuỗi ngắn, không đếm lặp trong cùng nhãn. Hai hành vi độc lập nên cùng anchor có thể hỗ trợ cả hai nhãn.

Rule đã pin: ít nhất 3 observations dương liên tiếp tại 1 Hz, spacing đúng 1 giây, span tối thiểu 2 giây. Âm/unknown/null/missing/ID change cắt chuỗi; không bridge/merge ID hoặc suppress duplicate. Ngưỡng G0 giữ 0,5 cho phone_use và 0,3914746344089508 cho looking_around. Mean score không phải xác suất đúng của event; span không chứng minh hành vi liên tục giữa frames.

[Danh sách candidates](candidates.md) giúp đọc track/nhãn/mốc thời gian và mean score; [events JSONL đầy đủ](../../../outputs/events-prototype-20261027/events.jsonl) giữ exact anchor/frame/time/score/threshold/person box, references namespaced theo parent session SHA, source/model/tracker/rule pins. [Accounting](../../../outputs/events-prototype-20261027/accounting.json) giữ cả chuỗi ngắn. [Session](../../../outputs/events-prototype-20261027/session.json) và [verification](verification.json) ghi outcome/checksums.

## Kiểm chứng và giới hạn

- 10 event tests PASS: boundary, EOF, hai nhãn, mean/span, negative/unknown/null/missing/ID change, absent track, duplicate/off-grid/geometry/score/flag, accounting/input immutability, expiry, success/failed outcome, mutation và output reuse guard.
- 22 tracking regression tests PASS; Ruff PASS; strict mypy PASS 73 source files. Dataclass BehaviorEvent không đổi.
- Kiểm độc lập toàn bộ 334 support references với predictions G0/C10, timestamps/span và không dùng lại cùng anchor trong cùng nhãn; accounting PASS. Manifest 7 files khớp SHA; approval/input pins kiểm trước/sau replay.
- Không có GT event hoặc visual acceptance mới. 55 candidates không phải 55 hành vi đúng, 55 người hay số vi phạm. Fragmentation/duplicate và classifier errors tiếp tục ảnh hưởng kết quả; không cộng các tracks thành identity hoặc risk.

Implementation và replay đã hoàn tất. Bước tiếp là review/acceptance riêng cho event candidates và các ngoại lệ, trước thiết kế risk hoặc web; không tự mở downstream từ software PASS. Chưa commit. Dữ liệu local owner-only, deadline giữ **01/11/2026 15:55:06 Việt Nam**, không gia hạn; các bảng chứa references kỹ thuật, không danh tính thật.
