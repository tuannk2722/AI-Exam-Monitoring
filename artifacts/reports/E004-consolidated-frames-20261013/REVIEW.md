# E004 — Nghiệm thu đề xuất từ ZIP 222 frames

Ngày 2026-10-13. **Draft: 33 crop mới, chưa owner nghiệm thu.** Approval 20 crop cũ đã nhập riêng; không áp dụng tự động cho các crop mới này.

[Báo cáo audit](README.md) · [QA cuối](qa-proposals.json) · [Support](support-proposal.json). Mở giao diện local: `data/interim/E004-consolidated-frames-20261013/REVIEW.html` (source + geometry + crop + input 224).

Đề xuất giữ cả family CF-Q072 ở new-development (12 crop); 21 crop còn lại reserve holdout candidate, chưa freeze hoặc dùng test. Không chia các frame/ảnh cùng family sang train. V7 train/val/test giữ nguyên; chưa cần release train mới. Quyền local đã được owner xác nhận, không cần duyệt lại.

Owner chỉ cần chốt batch nhãn/geometry và family/role proposal; có thể ghi ngoại lệ theo ID. P/N/U theo thứ tự phone/looking. Không có scores model trong lựa chọn. Nhãn canonical vẫn Unknown cho tới nghiệm thu.

| Crop | Frame | P/N/U | Family | Vai trò đề xuất | Owner |
|---|---|---|---|---|---|
| E004-CF-C001 | CF-001 | U/N | CF-Q001 | reserved_holdout_candidate | Approve |
| E004-CF-C002 | CF-001 | U/P | CF-Q001 | reserved_holdout_candidate | Approve |
| E004-CF-C003 | CF-019 | U/N | CF-Q009 | reserved_holdout_candidate | Approve |
| E004-CF-C004 | CF-033 | U/N | CF-Q030 | reserved_holdout_candidate | Approve |
| E004-CF-C005 | CF-033 | N/N | CF-Q030 | reserved_holdout_candidate | Approve |
| E004-CF-C006 | CF-064 | N/P | CF-Q061 | reserved_holdout_candidate | Approve |
| E004-CF-C007 | CF-072 | P/N | CF-Q072 | new_development | Approve |
| E004-CF-C008 | CF-091 | N/N | CF-Q072 | new_development | Approve |
| E004-CF-C009 | CF-099 | N/P | CF-Q072 | new_development | Approve |
| E004-CF-C010 | CF-104 | N/N | CF-Q072 | new_development | Approve |
| E004-CF-C011 | CF-109 | N/P | CF-Q072 | new_development | Approve |
| E004-CF-C012 | CF-126 | P/U | CF-Q126 | reserved_holdout_candidate | Approve |
| E004-CF-C013 | CF-128 | P/N | CF-Q126 | reserved_holdout_candidate | Approve |
| E004-CF-C014 | CF-129 | P/P | CF-Q129 | reserved_holdout_candidate | Approve |
| E004-CF-C015 | CF-130 | P/N | CF-Q112 | reserved_holdout_candidate | Approve |
| E004-CF-C016 | CF-135 | P/P | CF-Q072 | new_development | Approve |
| E004-CF-C017 | CF-137 | P/N | CF-Q137 | reserved_holdout_candidate | Approve |
| E004-CF-C018 | CF-143 | P/N | CF-Q072 | new_development | Approve |
| E004-CF-C019 | CF-145 | P/N | CF-Q137 | reserved_holdout_candidate | Approve |
| E004-CF-C020 | CF-149 | P/N | CF-Q149 | reserved_holdout_candidate | Approve |
| E004-CF-C021 | CF-152 | P/P | CF-Q072 | new_development | Approve |
| E004-CF-C022 | CF-153 | P/U | CF-Q153 | reserved_holdout_candidate | Approve |
| E004-CF-C023 | CF-161 | N/N | CF-Q161 | reserved_holdout_candidate | Approve |
| E004-CF-C024 | CF-169 | N/N | CF-Q169 | reserved_holdout_candidate | Approve |
| E004-CF-C025 | CF-172 | U/N | CF-Q172 | reserved_holdout_candidate | Approve |
| E004-CF-C026 | CF-193 | N/P | CF-Q112 | reserved_holdout_candidate | Approve |
| E004-CF-C027 | CF-195 | N/N | CF-Q112 | reserved_holdout_candidate | Approve |
| E004-CF-C028 | CF-202 | N/P | CF-Q072 | new_development | Approve |
| E004-CF-C029 | CF-203 | N/N | CF-Q072 | new_development | Approve |
| E004-CF-C030 | CF-208 | U/P | CF-Q072 | new_development | Approve |
| E004-CF-C031 | CF-209 | U/N | CF-Q072 | new_development | Approve |
| E004-CF-C032 | CF-210 | P/N | CF-Q112 | reserved_holdout_candidate | Approve |
| E004-CF-C033 | CF-217 | P/N | CF-Q126 | reserved_holdout_candidate | Approve |

## Ngoại lệ cần chú ý

- C001, C002, C003, C004, C025, C030, C031 giữ phone U vì vật/tay khuất hoặc evidence nhỏ; không cộng thành N.
- C012 và C022 giữ looking U: phía sau đầu hoặc thiếu vùng bài làm.
- C015/C019/C032 nhìn thiết bị riêng: looking N theo semantics hiện hành; không tự coi phone P là looking P.
- C021 có hai người cầm phone; anchor là người áo caro phía nền, không gán thiết bị gần camera cho anchor.
- C024 hộp bút và C028/C029 calculator là hard negatives; không phải mobile.
- Một family có thể chứa nhiều parent IDs và ảnh tĩnh không parent. Group IDs là ranh giới quarantine bảo thủ dựa vào cảnh/metadata, không video/session đã chứng minh.
