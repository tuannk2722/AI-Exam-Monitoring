# Tracking N0/B0/B1 — Thiết kế đã được duyệt

Ngày 27/10 owner giao agent nghiên cứu và tự quyết định: [selection B0](selection-20261027.json), [research](../../../artifacts/reports/tracking-prototype-20261026/research-20261027/README.md). B0 được chọn làm baseline, chưa được nghiệm thu cho temporal aggregation vì có mixed-person track. Trạng thái pending lựa chọn của bàn giao ngày 26/10 được quyết định mới thay thế; artifacts gốc giữ nguyên.

Owner đã trả lời “approve, hãy thực hiện đi!” cho thiết kế, variables, cài `lap==0.5.12`, implementation, benchmark và tạo batch review. [Authorization](owner-authorization.json) pin README/proposal/preflight nguyên trạng. Chữ Draft trong snapshot đã pin không phản ánh approval mới; không sửa bytes snapshot để thay trạng thái. Chưa có tracker winner hoặc quality acceptance.

## Cách chạy

CLI `ai_exam_monitoring.inference.tracking --authorization configs/tracking/TRACKING-PROTOTYPE-20261026/owner-authorization.json --output <thư mục mới dưới outputs>` replay đúng N0/B0/B1, kiểm pins/rights/deadline trước và sau. Không detector/classifier inference. Mỗi arm giữ config, environment, code provenance, assignments, summary, session outcome và checksums; root có benchmark outcome. Không chạy lại benchmark đã hoàn tất chỉ để kiểm phần mềm.

CLI `ai_exam_monitoring.inference.tracking_review --authorization <authorization.json> --benchmark <benchmark đã completed> --source <clip gốc đúng SHA> --output <thư mục review mới dưới outputs>` decode source frames và tạo gallery offline. Không log đường dẫn clip riêng tư. Deadline kế thừa 01/11/2026 15:55:06 Việt Nam.

Mapping ByteTrack giữ original detection index qua cả hai nhóm high/low; không ghép theo thứ tự kết quả. ID không được xuất vẫn có assignment null với lý do `not_emitted_by_tracker`, không suy nguyên nhân cụ thể khi upstream không trả về. Mỗi arm chạy tuần tự với instance mới vì upstream dùng bộ đếm ID chung; không chạy các instances này đồng thời trong cùng process.

`lap==0.5.12` đã cài vào `.venv`, không đổi các package hiện hành. Guard kiểm exact versions trước import và tắt auto-install/sync. Package này chỉ cần cho tracking; không thêm vào base dependencies hoặc buộc CI base cài ML.

## Kết quả và review

[Report](../../../artifacts/reports/tracking-prototype-20261026/README.md) giữ kết quả benchmark, checks và giới hạn. [Gallery local](../../../outputs/tracking-review-20261026/index.html) cho xem ba arms, chuyển sample, xem nhóm track/gap/unassigned và xuất review JSON. Draft review trong browser không tự thành acceptance hoặc ground truth. Owner review batch/ngoại lệ trước khi chọn arm; metrics identity chỉ tính trong coverage được review rõ.

Gallery dùng localStorage để giữ nháp và có nút xuất JSON; cần xóa nháp/browser site data cùng media theo deadline. File review xuất về máy cũng thuộc scope local owner-only và cùng deadline. Không tự mở events/risk/web.
