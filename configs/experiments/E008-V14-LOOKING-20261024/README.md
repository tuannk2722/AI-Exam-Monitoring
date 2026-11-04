# E008 V14 — Training trên Colab Pro

**Owner đã chạy xong: 4 smoke + 5 research FINISHED; G0 thắng screening, looking chưa đạt, chưa Selected.** [Kết quả và audit metadata ngày 25/10](../../../artifacts/reports/e008-v14-colab-20261024/results-20261025.md). [Ba run G0 đã import đủ best/last và kiểm checksum local](../../../artifacts/reports/e008-v14-colab-20261024/checkpoints-20261025.md); tiếp tục bảo toàn bản Drive. [Handoff và checksum lịch sử](../../../artifacts/reports/e008-v14-colab-20261024/handoff.json) giữ nguyên. Hướng dẫn bên dưới là launcher gốc, không phải yêu cầu chạy lại campaign.

Owner đã đồng ý [thiết kế E008 gốc](../E008-V13-LOOKING-20261024/README.md), sau đó yêu cầu cập nhật dataset và dùng đủ 53 crop mới trước training. [Receipt](../../../artifacts/reports/dataset-release-20261024-v14/owner-direction.json) ghi authorization. Proposal V13 và pins gốc giữ nguyên như snapshot đã review; companion này có identity mới vì dataset/split đã đổi.

Đầu vào hiện hành: [V14 accepted](../../../artifacts/reports/dataset-release-20261024-v14/README.md), 1.199 train / 156 val / 0 test. [Data input](data-input.json) pin payload, split, encoding và counts. [SQRT weights từ train](../../../artifacts/reports/dataset-release-20261024-v14/train-class-weights.json) được tính lại từ known labels; không giữ weights V13 khi materialize config V14.

Thiết kế được owner đồng ý vẫn là G0 global pooling, G1 context 2 × 2, A1 person-box 2 × 2. Owner yêu cầu tiếp tục train bằng Colab Pro và cho phép tăng thời lượng trong ngân sách cũ; [authorization hiện hành](owner-authorization.json), [proposal V14](proposal.yaml), [design/pins](design.json). Cap tăng từ 12 lên **24 epoch**, patience 6 và warmup 3 giữ nguyên; cả ba arm dùng cùng horizon cosine mới. D1 E007 có best epoch 11/7/9 trong cap 12; cap mới tạo thêm cơ hội hội tụ, không bảo đảm cải thiện và không yêu cầu dùng hết 24 epoch.

Giữ FP32/TF32 tắt, batch 16, 336 px, workers 0, hai block cuối + final norm, loss/smoothing/augmentation/selection/calibration và gates đã duyệt. G1/A1 dùng chung initialization head 1.920 chiều theo seed, G0 head 768 chiều. Schema `spatial-representation-v5` dùng geometry continuous sau rounded letterbox và hflip, không thêm bbox hoặc padding. 69/156 crop val có person box bằng context; ở các crop đó G1/A1 có cùng vùng pooling.

Val đã mất 27 crop do chuyển cả nhóm nguồn sang train và 2 crop bị exclude. Do đó phải chạy lại G0 trên cùng V14 để đối chứng G1/A1; E007/V13 chỉ giữ tham chiếu lịch sử. Giữ `warm_start_research_checkpoint: false`; dùng lại pretrained gốc theo thiết kế, không warm-start D1 E007 đã được chọn theo val cũ. Không gọi V14 là holdout độc lập hoặc dùng cải thiện raw metrics qua hai dataset làm bằng chứng riêng cho spatial pooling.

## Cách chạy

1. Upload [e008-colab-bundle.zip](../../../outputs/E008-V14-Colab-20261024/e008-colab-bundle.zip) vào **My Drive/E008/**, giữ private. Bundle khoảng 489 MB; upload trước khi kết nối GPU.
2. Mở [E008-V14-Colab.ipynb](../../../notebooks/E008-V14-Colab.ipynb) bằng **Colab → File → Upload notebook**. Dùng runtime Python 3.11 hoặc 3.12 theo điều kiện notebook và `requires-python` của project; không chỉ nới câu `if` để chạy Python 3.13. Chọn GPU mạnh nhất khả dụng; High RAM nếu cần/có. Colab Pro không bảo đảm một loại GPU hoặc tài nguyên vô hạn; xem [FAQ chính thức](https://research.google.com/colaboratory/faq.html).
3. Bấm **Run all**, mount Drive đúng tài khoản. Notebook kiểm SHA bundle/từng file, cài environment riêng, rồi chạy canonical campaign; không cần sửa variables hoặc chạy từng arm thủ công.
4. Kết quả tại **My Drive/E008/E008-V14-COLAB-20261024/**. Tải **My Drive/E008/E008-V14-results-metadata.zip** về sau khi chạy để audit. Checkpoints/model vẫn ở thư mục campaign; ZIP nhỏ này chỉ chứa JSON/YAML/logs.

## Gate và ngân sách

Trần **4 giờ từ cell launcher**, gồm setup/chờ/sync. GPU có thể tiêu CU từ lúc kết nối trước cell: kết nối rồi chạy ngay. Không mua thêm credits. Smoke G0 và A1 gồm full 5 epoch, interrupt tại epoch 3 rồi resume, kiểm last/best/history/stage transition và standalone reload. Smoke tối đa 30 phút và phải đạt dự báo thời gian trước research.

Screening G0/G1/A1 ở seed 20261023; champion + G0 ở 20261024/20261025. Tối đa **7 research run**, còn 5 nếu G0 thắng; không tự chạy thêm khi còn giờ. Mỗi run + reload tối đa 25 phút, reserve 35 phút. Runner dừng khi hết cap, OOM hoặc sai parity, không tự giảm batch/resolution hay bật AMP. Config/approval cụ thể được materialize và bind code/runtime theo phase; [smoke configs đã kiểm local](materialized/smoke/plan.json) không phải receipt GPU PASS.

V14 chỉ có **29 looking-positive**, dưới support tối thiểu 30: không hạ gate hoặc đổi split để công bố đạt. Kết quả dùng nghiên cứu/development, không independent holdout, Selected, final test hoặc promotion.

Mỗi epoch có snapshot đồng bộ và atomic replace vào Drive `recovery/`; runtime tự ngắt khi hoàn tất hoặc lỗi. Nếu bị ngắt, giữ folder/log/receipt và đối chiếu trạng thái trước khi resume cùng identity. Không chạy lại toàn notebook khi campaign folder đã tồn tại. Nếu runtime chết trước khi tạo ZIP metadata, lấy metadata từ folder campaign; không mất quyền truy cập checkpoints đã sync.
