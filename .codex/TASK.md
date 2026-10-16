# E004-TRAIN-ENROLLMENT-20261016

- Trạng thái: hoàn tất phạm vi được owner approve ngày 16/10/2026; Continue research, chưa Selected.
- Scope: chuẩn hóa geometry/lineage/provenance cho 345 accepted crop; giữ crop bytes/nhãn; kiểm leakage; chuẩn bị package train và proposal experiment chỉ thay dữ liệu, giữ selection 71. Owner yêu cầu thực hiện tới hoàn thành, không cần review lại nhãn/crop đã duyệt.
- Inputs: E004-accepted-coverage-20261016/result-pins.json và ledgers upstream; V9 release/development/pins; docs data/training/reference; code schema/exporter/loader hiện hành.
- Outputs dự kiến: artifacts/reports/E004-train-enrollment-20261016; data/interim và outputs cùng ID; config/package mới khi đủ điều kiện. Không sửa snapshots cũ.
- Hiện trạng: owner đã duyệt contract crop dẫn xuất, 345 geometry, quarantine group và thiết kế E004-C345-W-H (CPU tối đa 7.200 giây, smoke trước run). V10 và development package đã đóng, loader PASS, 1.061 train; giữ nội dung 1.208 records parent. Evidence tại E004-train-enrollment-20261016/package-pointers.json.
- Constraints: không invent person boxes/independence, không dùng context làm person; giữ test/reserve đóng, chỉ metadata integrity; không tự đổi schema/labels/split/recipe. Approval mới bao phủ implementation các bước báo cáo, không thay quyết định khoa học còn chưa định nghĩa.
- Checks: upstream pins; ROI/input parity; lineage/overlap; schema/export/loader khi khả thi; focused tests/diff. Không claim 100% nếu còn gate/clarification.
- Kết quả: smoke FINISHED; research FINISHED 11 epochs/best epoch 1 sau recovery orphan process tại epoch 8. Config/checkpoint giữ nguyên; downtime tính bảo thủ vào budget. Run integrity và reload scores/metrics exact parity PASS. Báo cáo/comparison tại E004-train-enrollment-20261016: looking cải thiện nhưng phone FP tăng; M1/M2/M3 chưa đạt trên development, M4 INCONCLUSIVE. Backup local 4.121 files restore byte-exact PASS; cache restore/rebuild đã dọn.
- Bước tiếp: bàn giao kết quả; không tự chạy thêm experiment, đổi recipe/nhãn/threshold hoặc mở test/reserve. Nghiên cứu tiếp cần thiết kế riêng. Git chưa stage/commit.
