# E004 — Thực thi ưu tiên dữ liệu sau owner approval

Ngày 2026-10-11, owner approve báo cáo và đề xuất đã review, yêu cầu thực hiện theo thứ tự data. [Receipt/pins thiết kế](../../artifacts/reports/E004-source-review-20261011/owner-direction.json) giữ approval đó; ngày 2026-10-12 owner đã nghiệm thu 56 active anchors theo [receipt crop](../../artifacts/reports/E004-source-review-20261011/owner-review-receipt-20261012.json). [Kết quả hiện hành](../../artifacts/reports/E004-source-review-20261011/REVIEW-OWNER-20261012.md) và [batch QA](../../artifacts/reports/E004-source-review-20261011/pilot-input224-review-20261012.json) giữ evidence. [Freeze proposal](E004-freeze-proposal-20261011.md) và [proposal gốc](E004-proposal.md) là snapshots đã duyệt, giữ chữ Draft/hashes lịch sử, không sửa chúng để cập nhật lifecycle.

## Quyết định có hiệu lực và các đối tượng chưa freeze

Cập nhật quyết định 12/10: owner đã đồng ý compute, yêu cầu giữ promotion, chỉ miễn independence và giữ support cũ. [Revision readiness](E004-execution-readiness-20261012.md) ghi exact scope/gaps; các mô tả independence bên dưới thuộc thiết kế gốc, không được dùng để phủ nhận waiver mới. Chưa có runnable protocol revision hoặc cohort đủ support; không đánh dấu independence đã verified khi không có evidence.

Approval thiết kế/đề xuất và quyền thực hiện preparation có hiệu lực; tiếp tục recommended new-development whole-family cho selection, comparator48/full val49 diagnostic, matched frozen control/layer4 recipe và test/reproducibility plan đã trình bày. Numeric G3/M1–M7 giữ exact values trong snapshot; không tự revise gate. Nghiệm thu nhãn/geometry 56 anchors đã đóng riêng ngày 12/10; exact groups/roles/test package và wall-time budget/config hash cho hai run thật vẫn chưa đóng.

| Gate/mốc | Sau lần xử lý này |
|---|---|
| G0 / F0 | Design đã owner approve; exact runnable configs/cohort/protocol/data identities và wall-time budget cần đóng trước training. Không coi approval mới không tồn tại chỉ vì snapshot cũ ghi Draft |
| G1 / F1 | V7 local Accepted; 56 active anchors đã nghiệm thu nhãn/geometry, 49 có target known; ledger mới review-only. New-development/holdout package chưa Accepted |
| G2 | 0 new independent groups proven. Đã xem 136 nguồn; 52 Student sources cùng cảnh train. Graph quarantine/metadata chưa đủ xác minh independence |
| G3 | Ngưỡng không đổi: mỗi target ≥100 P/100 N; ≥10 independent groups, P/N mỗi loại ≥5 groups; ≥2 verified camera/room contexts. Accepted new test support vẫn 0; báo gap, không hạ số |
| G4 / F2–F3 | I1–I8 đã triển khai và kiểm synthetic/regression theo [software evidence](../../artifacts/reports/E004-software-readiness-20261012/README.md); chưa smoke/run thật. [Readiness](E004-execution-readiness-20261012.md) ghi inputs và compute cần chốt |
| G5 / F4–F5 | Chưa candidate/holdout payload/access receipt đã freeze, chưa final evaluation. Giữ use-once registry và một candidate theo thiết kế |
| M1–M7 | Numeric/protocol proposals đã được duyệt để thực hiện; chưa có model evidence để PASS. Không đổi ngưỡng hoặc dùng macro che target yếu |

## Freeze dữ liệu tiếp theo

1. **Đã đóng batch label/geometry:** 56 active anchors được owner nghiệm thu, 49 có ít nhất một target known và 7 U/U auxiliary; 3 original crop versions superseded, chỉ R2 active. Ledger strict đã nhập values/masks nhưng giữ review-only/split null. Quyền nguồn local đã xác nhận, không hỏi lại.
2. Giữ 6 behavie scene boundaries reserve holdout candidate; Student instructional quarantine new-development; ba cảnh Student đã train chỉ train-supplement candidates. Role này là reserve proposal, chưa canonical assignment. Không chia cùng family vào cả hai cohort.
3. Graph provenance/overlap local đã dựng từ exact source SHA, lineage hints cùng export và reviewed scenes: 33 thành phần quarantine liên quan tới 193 members, không có reserve-role conflict quan sát được. Metadata ZIP chưa có video/session/phòng/camera mapping; unknown IDs giữ null. Visual scene IDs không là independent groups. Cần evidence bổ sung trước group/split acceptance.
4. Bổ sung phone P ở new-development từ families chưa dùng; 16 ảnh phone/Using_phone vừa xem thêm đều thuộc hai cảnh train, không bù gap. Giữ phone P/N và looking P/N/group coverage phù hợp, không bù bằng upstream split hoặc train positives. Chỉ freeze cohort roles/sampling mixture/package khi group và assignment có evidence/acceptance.
5. Dùng strict PilotRecord codec và exporter active để đóng ledger/manifest/package/approval/protocol mới sau nghiệm thu. Comparator48, val49 bijection và historical parent preservation theo exact pins đã duyệt, không sửa V7 hay lịch sử.
6. I1–I8 software đã có synthetic validation; real smoke/run chỉ sau exact data/config/compute/readiness scope. Không bỏ G1–G3 để chạy promotion experiment; dùng [readiness companion](E004-execution-readiness-20261012.md) để đóng các đầu vào còn thiếu.

Taxonomy V7 Unknown là conditional queue sau bổ sung train và xác định gap cụ thể; không thêm classes hoặc relabel 256 cells từ tên lớp nguồn. Chưa có supervised train mới Accepted nên chưa claim train đã đủ/thiếu từ model outcomes. Trạng thái lifecycle này không thay hashes/approval contracts lịch sử.
