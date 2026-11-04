# Ngoại lệ diagnostic stage A — 26/10/2026

Owner trả lời câu hỏi scope: **“Chạy diagnostic, giữ unknown; chưa chọn winner”**.

Cho phép chạy đúng D0/D1/D2 trên 19 frame đã pin, tổng 57 detector forwards, để xem output khi census còn draft. Ngoại lệ thay điều kiện census accepted trước inference của stage A, chỉ trong run `RUNTIME-DETECTOR-DIAGNOSTIC-20261026`. Không nghiệm thu nhóm người, không tính precision/recall/miss/duplicate extras từ draft, không chọn winner hoặc đổi runtime prototype.

Giữ ma trận conf/NMS, detector weights/package, CPU FP32, crop geometry, nguồn/media rights/deadline và D0 parity. Không classifier rerun, training, test, tracking/events, upload hoặc tải model khác. D0 parity không đạt thì dừng candidates và giải thích drift, không sửa pins hoặc nới phép so để chạy tiếp.

Config và receipt diagnostic mới dẫn decision này. Proposal, stage-a.yaml, approval cũ và census draft giữ nguyên. Output mới giữ mọi assignment unknown và quality not evaluated, có provenance/checksums/gallery để xem lại.
