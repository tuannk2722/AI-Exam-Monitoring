# Chuẩn bị đối chứng detector trực tiếp — 26/10/2026

Owner duyệt hướng sau nghiên cứu: census trước, D2 baseline + V8S capacity control + V10S end2end, sau đó crop QA và confirmation riêng. [Proposal/variables](../../../configs/runtime/RUNTIME-DETECTOR-COMPARISON-20261026/README.md) giữ thiết kế, chưa run approval số.

[Gallery census](../../../outputs/runtime-d2-census-review-20261026/index.html) có 19 frame, 342 anchors, 338 nhóm draft sau 4 exact same accepted; giữ 4 different/keeper. Không có nhãn completeness tự động, không 338 người accepted. Nguồn D2 và receipts mới thay việc tái dùng census D0 draft sai namespace. Bộ review cũ và pins nguyên vẹn.

Module census_review reusable, tests kiểm chỉ merge same accepted, different/unknown giữ riêng, conflict/cross-frame/transitive overlap bị chặn. 4 tests PASS, Ruff/mypy 67 files PASS. Kiểm checksum toàn gallery, links, 342 anchor coverage/4 keeper PASS; đã xem overlay frame1080. CI thêm test_census_review.py. Chưa tải checkpoint hoặc inference.

Đã hỏi owner nghiệm thu census theo batch/ngoại lệ và chốt variables/scope 38 frame forwards ở proposal. Hai quyết định độc lập; approval variables không biến census thành accepted. Sau nhận đủ tạo receipts/revision mới, triển khai và run đúng scope. Không có phép đo quality mới trong bước chuẩn bị này. Giữ deadline media nguồn 01/11/2026 15:55 Việt Nam; không upload hoặc copy ảnh nguồn, chỉ sinh overlays cần cho review. Không scratch/checkout hoặc stage/commit.
