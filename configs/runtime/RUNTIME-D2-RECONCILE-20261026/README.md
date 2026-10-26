# Đối soát ngoại lệ D2 — 26/10/2026

Owner đồng ý hướng review D2/attribution, sửa retention/CI, rồi mới tích hợp video/tracking/events theo scope được chốt. Giữ D2/G0 và threshold hiện hành.

[Batch config](batch.yaml) pin predictions/run/checksums/cohort và overlay của C01–C07. [Gallery local](../../../outputs/runtime-d2-reconcile-20261026/index.html), [manifest draft](../../../outputs/runtime-d2-reconcile-20261026/review.json) chỉ dùng evidence đã có, không inference. Owner decisions null; role unknown. Scores đặt trong mục mở rộng để review hình ảnh trước. Đây là shortlist có mục tiêu, không dùng để tính accuracy toàn clip.

Draft C01/C02 cùng người, chưa chọn box giữ; C03 cần xác minh thiết bị/ownership; C04/C06/C07 cần phone/looking P/N/U theo anchor; C05 cần scope eligibility. Owner review batch và ngoại lệ, không annotate từ đầu. Không sửa winner receipt hoặc unknown lịch sử.

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.inference.review_batch --config configs/runtime/RUNTIME-D2-RECONCILE-20261026/batch.yaml --output outputs/runtime-d2-reconcile-20261026
```

Output đã tồn tại, không ghi đè. Deadline media 01/11/2026 lúc 15:55 Việt Nam; gallery link input, không copy/upload. Sau phản hồi owner, ghi addendum mới; không mutate pins cũ. Nếu xác nhận duplicate, chuẩn bị đối chứng suppression bảo toàn người bị che; không tự hạ IoU hoặc chọn largest/highest-score. Chưa chạy video mới khi kết luận/variables còn chưa rõ.
