# E008 V14 — Hoàn tất nhận model G0 ngày 25/10/2026

**PASS: đã nhận đủ ba thư mục run G0, kiểm checksum và cấu trúc cả sáu checkpoint best/last.** Phần bàn giao model local đã hoàn tất. Kết luận nghiên cứu vẫn là Continue, chưa Selected; xem [kết quả](results-20261025.md).

Owner cung cấp ba ZIP thư mục run từ Colab. Đã import nguyên bytes 45 files, tổng 889.651.608 bytes, vào [thư mục runs local](../../../outputs/E008-V14-Colab-20261024/runs). Không ghi đè metadata audit hoặc sửa checksum gốc. ZIP nguồn trong Downloads được giữ nguyên; không tạo thêm bản ZIP trùng trong repository.

| Run | Best epoch / completed | Artifacts local |
|---|---:|---|
| E008-V14-G0-S20261023 | 8 / 14 | [best.pt](../../../outputs/E008-V14-Colab-20261024/runs/E008-V14-G0-S20261023/best.pt), [last.pt](../../../outputs/E008-V14-Colab-20261024/runs/E008-V14-G0-S20261023/last.pt), metadata và learning curve |
| E008-V14-G0-S20261024 | 8 / 14 | [best.pt](../../../outputs/E008-V14-Colab-20261024/runs/E008-V14-G0-S20261024/best.pt), [last.pt](../../../outputs/E008-V14-Colab-20261024/runs/E008-V14-G0-S20261024/last.pt), metadata và learning curve |
| E008-V14-G0-S20261025 | 10 / 16 | [best.pt](../../../outputs/E008-V14-Colab-20261024/runs/E008-V14-G0-S20261025/best.pt), [last.pt](../../../outputs/E008-V14-Colab-20261024/runs/E008-V14-G0-S20261025/last.pt), metadata và learning curve |

[Receipt](checkpoint-import-20261025.json) ghi SHA256/size ZIP nguồn, toàn bộ files đích và tensor digest. Kiểm tra đã thực hiện:

- Inventory chính xác, path an toàn, ZIP CRC; 42 artifacts khớp checksum đã nhận trước, ba `checksums.json` giống nguyên bytes bản đã audit.
- Tất cả metadata trùng với ZIP metadata trước; đọc lại SHA file đích sau ghi.
- Đọc sáu checkpoint bằng `torch.load(weights_only=True, map_location="cpu")`; best config/identity/epoch khớp run/bundle, last history/completed epoch khớp metadata.
- Digest tensor best khớp digest được khai báo và `best_model` trong last; tensor model best/last hữu hạn.

Đây là kiểm tra integrity và cấu trúc local, không phải lượt inference mới. Evidence standalone CUDA reload vẫn là lượt Colab đã audit; không đổi môi trường/config để giả lập parity, không train hoặc mở test. Các checkpoint smoke/G1/A1 chưa được tải về, nhưng không còn thiếu bytes của ba model G0 được yêu cầu bàn giao. Không kết luận toàn campaign đã được backup local.

Giữ bản campaign/recovery trên private Drive. Việc xác minh local không xác minh lại trạng thái backup Drive và không cho phép xóa bản cloud. Model vẫn cần code/config/runtime và dependencies đúng pins khi sử dụng; import thư mục run không tự cấp quyền resume hay promotion.
