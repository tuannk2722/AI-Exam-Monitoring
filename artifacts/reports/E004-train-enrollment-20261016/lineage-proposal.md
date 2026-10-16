# Lineage và membership đề xuất

Trạng thái: đề xuất để owner nghiệm thu cùng geometry; không chứng minh độc lập.

- Membership mới: đúng 345 IDs trong accepted-ledger của E004-accepted-coverage-20261016, cùng vai trò train; không crop mới vào val/test/reserve.
- Đề xuất một quarantine group chung `E004-CROP-TRAIN-Q001` cho cả 345 crop. Giữ 7 parent video IDs làm provenance, không suy từ ID rằng khác phòng/người/session. Group chung bảo thủ tránh khẳng định các video mới độc lập; không dùng nó làm 345 hoặc 7 đơn vị độc lập trong bootstrap.
- Anchor identity canonical đề xuất chỉ trong một source frame; ID crop kỹ thuật không là subject identity xuyên frame. Khi cùng frame/cùng người có hai crop, phải hợp nhất identity/loại bản thừa trước enrollment; bảng geometry hiện chỉ là Draft. Không dùng nhãn anchor từ ZIP như căn cước người.
- Đã xem 7 representative parent scenes và toàn bộ 71 selection crops: chưa quan sát thấy scene trùng. Đã tính nearest dHash cho 345 crop với 836 non-test train/val crops trong development package: khoảng cách nhỏ nhất train 12, val 13; không cặp nào ≤ 6. Ngưỡng này chỉ là triage, không là acceptance threshold hoặc chứng minh không leakage.
- Exact SHA source/crop không trùng canonical/development V9 theo báo cáo coverage đã pin. Không mở ảnh test/reserve, không extract features từ các tập đó. Không kết luận protected lineage sạch bằng việc không tìm thấy exact SHA.
- Các giới hạn này phải xuất hiện trong release/protocol research. Nếu yêu cầu chứng minh independence với protected pool trước research, cần protocol audit riêng; không tự mở pool. Không viện waiver của experiment cũ thành approval cho experiment mới.

Evidence: `nearest-development-crops.json`, các board `outputs/E004-train-enrollment-20261016/parent-scenes.jpg`, `selection-1.jpg` đến `selection-3.jpg`, và report coverage upstream. Tất cả là nghiên cứu local, không upload media.
