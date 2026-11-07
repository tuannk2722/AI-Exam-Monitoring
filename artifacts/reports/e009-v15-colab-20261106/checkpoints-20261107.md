# E009 V15 — Hoàn tất nhận ba run đại diện ngày 07/11/2026

**PASS: đã nhận đủ B0, B448 và C0 theo danh sách audit, kiểm nguyên bytes 48 files và cấu trúc sáu checkpoint best/last.** [Kết quả metadata](results-20261107.md) và findings đã ghi vẫn giữ nguyên; B0 đứng đầu ranking nghiên cứu, chưa Selected/promotion hoặc thay G0 prototype.

Owner cung cấp ba ZIP thư mục run từ Downloads. Đã import **2.613.350.884 bytes** vào [runs local](../../../outputs/E009-V15-Colab-20261106/runs), không sửa metadata hay checksum. Giữ nguyên ba ZIP nguồn, không tạo bản ZIP trùng trong repository. [Receipt](checkpoint-import-20261107.json) ghi SHA/size archive và từng file đích; [script tái lập](import_checkpoints.py) chỉ import/check cấu trúc, không train hoặc inference.

| Run | Best epoch / completed | File local |
|---|---:|---|
| **E009-V15-B0-S20261106** | **10 / 16** | [best.pt](../../../outputs/E009-V15-Colab-20261106/runs/E009-V15-B0-S20261106/best.pt), [last.pt](../../../outputs/E009-V15-Colab-20261106/runs/E009-V15-B0-S20261106/last.pt), metadata |
| E009-V15-B448-S20261110 | 22 / 24 | [best.pt](../../../outputs/E009-V15-Colab-20261106/runs/E009-V15-B448-S20261110/best.pt), [last.pt](../../../outputs/E009-V15-Colab-20261106/runs/E009-V15-B448-S20261110/last.pt), metadata |
| E009-V15-C0-S20261107 | 15 / 21 | [best.pt](../../../outputs/E009-V15-Colab-20261106/runs/E009-V15-C0-S20261107/best.pt), [last.pt](../../../outputs/E009-V15-Colab-20261106/runs/E009-V15-C0-S20261107/last.pt), metadata |

Các kiểm tra đã hoàn tất:

- Ba inventory đúng 16 files/run; path/allowlist/symlink an toàn. CRC được kiểm khi đọc hết từng member, streaming SHA khớp mirror manifest của metadata ZIP đã audit; đọc lại hash file đích sau ghi. Không ghi đè divergent input và không còn `.import-partial`.
- 42 file metadata giống nguyên bytes metadata ZIP trước; cả 48 file khớp manifest, các checksum best/last khớp `checksums.json`, bundle và calibration liên quan.
- Đọc sáu checkpoint bằng `torch.load(weights_only=True, map_location="cpu", mmap=True)`. Identity/config/code/runtime pins, best epoch/completed epoch, history và selection metric khớp metadata. Best epoch đúng quy tắc val macro AP → val BCE → epoch sớm nhất.
- Digest tensor best khớp digest khai báo và `best_model` trong last; tensors model/optimizer đều hữu hạn. Model cấu trúc gốc load strict cả best và final state thành công, không forward ảnh hoặc tạo predictions mới.
- Mỗi model có 181 state keys và 36 optimizer parameter states; optimizer tensor shapes/steps khớp parameter inventory, số epoch và warmup. Global step lần lượt 1.392 / 2.088 / 1.827; sampler permutation/cursor khớp 1.377 ảnh train và history, RNG/sampler state có đủ cấu trúc.
- Với mỗi best/last, **145 backbone tensors phải đóng băng vẫn giống pretrained gốc**, 30 trainable backbone tensors đã thay đổi. Train prevalence trong best khớp đúng known-label counts của V15 train, không lấy val.

Đây là audit integrity/cấu trúc trên Windows, Python 3.11.9 / Torch 2.8.0+cpu; không giả đây là tái chạy CUDA Linux gốc. Evidence inference/reload CUDA vẫn là các lượt Colab trong metadata đã audit; lần kiểm này không mở test hoặc tạo metrics mới. CUDA RNG được đọc cấu trúc, không restore lên GPU local.

Đã đủ bytes của **ba model đại diện** được yêu cầu. Chưa tải toàn bộ best/last của 31 run, 10 head initialization hay recovery tars, nên không kết luận toàn campaign đã được backup local. Giữ campaign/recovery trên private Drive; việc import không cấp quyền xóa nguồn, resume/train thêm hoặc promotion.

Không còn thiếu download trong phạm vi bàn giao ba run. Các quyết định dùng B0/B448, xử lý finding export score và nghiệm thu model là bước riêng theo use scope; không tự thay G0 prototype chỉ vì checkpoint đã load được.
