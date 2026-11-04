# Allocation A — owner đã duyệt

Owner chọn trực tiếp trong hội thoại: **A: 1.119 train / 185 val / 0 test; holdout riêng sau**. Membership là 1.304 crop, đã loại V6-EX-003, dùng đủ 21 ảnh owner xác nhận generate từ cohort audit. Không giữ 21 ảnh ở quarantine.

Phạm vi: chuẩn bị dataset local và allocation development. Năm test lịch sử chuyển sang val theo cả nhóm. Không gọi validation hiện tại là holdout độc lập; chưa xác minh exact parent của 21 ảnh nên không chứng minh được độc lập giữa train và val ở mức nguồn sinh ảnh. Không inference, training, upload hoặc đổi package accepted V12.

Nguồn nhập package candidate là các crop bytes đã được review, có bundle SHA riêng để kiểm tái lập. Các nguồn upstream V12, lineage thị giác và xác nhận generated được giữ trong provenance sidecar; bundle crop không được mô tả là ảnh camera gốc hoặc recipe AI đã xác minh. Context/normal chưa được chốt lại riêng để unknown, không suy tự động từ N/N.

Candidate chuẩn bị dùng identity `pilot-b-20261023-v13-candidate`; chưa là release accepted hoặc pointer hiện hành. Bước cuối cần nghiệm thu package cụ thể sau schema/export/checks; approval này không giả lập bước đó.
