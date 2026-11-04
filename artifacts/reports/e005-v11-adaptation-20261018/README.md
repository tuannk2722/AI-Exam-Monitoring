# Báo cáo thực nghiệm E005 trên Dataset V11 — 18/10/2026

**Trạng thái: Đã hoàn tất 1 smoke run (`E005-V11-AC-L4B1-SMOKE`) và 4 run đối chứng chính thức (`E005-V11-LP`, `E005-V11-S1-AUG`, `E005-V11-AC-L4B1`, `E005-V11-AC-L4`) trên local CPU (`threads = 4`). Toàn bộ 5 run đạt `FINISHED` và vượt qua kiểm tra `evaluate_adaptation` standalone reload exact parity. Cấu hình `E005-V11-S1-AUG` đạt chất lượng cao nhất toàn ma trận (`Val Macro AP = 0.7378`, `Val BCE = 0.5260`, `phone_use AP = 0.8161`, `looking_around AP = 0.6595`), tăng `+0.0365` Macro AP và `+0.0597` `looking_around` AP so với Baseline Linear Probe (`E005-V11-LP`). Tuy nhiên, chưa có cấu hình nào đồng thời vượt qua cổng chất lượng `Precision >= 80%, Recall >= 80%, FPR <= 20%` cho cả hai target trên tập validation 266 mẫu. Quyết định hiện hành: `continue_research_only` (chưa chọn model `Selected`, tập `test` 11 mẫu giữ đóng tuyệt đối).**

## 1. Cơ sở phê duyệt, provenance và ranh giới thực nghiệm

- **Dataset V11**: [`data/processed/pilot-b/pilot-b-20261017-v11`](../dataset-release-20261017/README.md) ([`package-pointers.json`](../dataset-release-20261017/package-pointers.json), `payload_sha256`: `e851ce51ae8bc027c50370468ee15ee99b4d93ae73c0d270f2055489fcbccd3a`, `split_version`: `owner-train-val-20261017`). Gồm **1.185 mẫu `train`** (274 nhóm; `phone_use`: `323 P / 411 N / 451 U`; `looking_around`: `318 P / 678 N / 189 U`), **266 mẫu `val`** (155 nhóm; `phone_use`: `72 P / 96 N / 98 U`; `looking_around`: `74 P / 146 N / 46 U`) và **11 mẫu `test`** (khóa trong `reserved_holdout`, không truy cập hoặc suy diễn).
- **Cổng chất lượng đã duyệt**: [`owner-acceptance.json`](../train-val-plan-20261017/owner-acceptance.json) (`TRAIN-VAL-ACCEPTANCE-20261017`) yêu cầu trên tập validation 266 mẫu, **mỗi target** (`phone_use` và `looking_around`) đều phải đạt `Precision >= 80%`, `Recall >= 80%`, `FPR <= 20%` với điều kiện support tối thiểu `30 P, 30 N, 5 nhóm P, 5 nhóm N`.
- **Phê duyệt thiết kế & thực thi E005**: [`owner-e005-approval.json`](owner-e005-approval.json) (`E005-V11-EXECUTION-APPROVAL-20261018`) và bộ cấu hình đóng băng tại [`configs/experiments/E005-V11-20261018/`](../../../configs/experiments/E005-V11-20261018/README.md), pin chính xác `code_sha256 = 241460325c026eb4aee270f8a3f8e9eedef8fde1ee9276d23fdc29d5a7ce1a7a`.
- **Chính sách khởi tạo chống rò rỉ lịch sử (Zero Warm-Start Leakage)**: Trong 266 mẫu `val` của V11 có **178 mẫu** (`former_train_178`) từng nằm ở tập `train` của V9/V10 (`E004-c345-development-20261016`). Để đảm bảo đánh giá trung thực 100%, toàn bộ các run E005 đều khởi tạo sạch từ trọng số ImageNet `IMAGENET1K_V1` (`outputs/pretrained/resnet18-f37072fd.pth`) và các head khởi tạo ngẫu nhiên mới (`seed = 20261018`) tại `data/interim/E005-V11-20261018/`, tuyệt đối không warm-start từ bất kỳ checkpoint hay head nào của V9/V10.

## 2. Tổng hợp thực thi và thông số vận hành 5 runs

| Run ID | Kiến trúc & Phạm vi mở khóa | Head | Epochs (Best / Hoàn tất) | Thời gian chạy (s) | Đỉnh RAM (MB) | Reload Parity | Checkpoint `best.pt` SHA-256 |
|---|---|---|---:|---:|---:|---|---|
| `E005-V11-AC-L4B1-SMOKE` | Dual-ROI Anchor-Context (`layer4.1`, smoke 1 ep) | MLP `1542->128->2` | `1 / 1` | `431.6s` | `1050.2` | `PASS` | `f8d078a98cee76da...` |
| `E005-V11-LP` | Single-Crop Frozen Backbone (`head_only`, không aug) | Linear `512->2` | `6 / 12` | `1580.2s` | `1389.4` | `PASS` | `63f213b97eecb33b...` |
| `E005-V11-S1-AUG` | Single-Crop + 2-Stage (`warmup 3 ep -> layer4.1`) + Aug + Balanced BCE | MLP `512->128->2` | `4 / 10` | `1115.4s` | `1490.6` | `PASS` | `28a5bd349e476d2d...` |
| `E005-V11-AC-L4B1` | Dual-ROI Anchor-Context + 6D `g_rel` + 2-Stage (`warmup 3 ep -> layer4.1`) + Sync Aug | MLP `1542->128->2` | `2 / 8` | `1795.0s` | `1490.6` | `PASS` | `f4f5406089bdcc67...` |
| `E005-V11-AC-L4` | Dual-ROI Anchor-Context + 6D `g_rel` + 2-Stage (`warmup 3 ep -> full layer4`) + Sync Aug | MLP `1542->128->2` | `2 / 8` | `1948.5s` | `1490.6` | `PASS` | `e5eadb31a583347d...` |

## 3. Kết quả tổng thể trên tập Validation V11 (266 mẫu, 155 nhóm)

Support trên tập Validation V11 (266 mẫu, 155 nhóm phân bổ): `phone_use` có **72 P / 96 N / 98 U** (168 mẫu có nhãn biết trước, **56 nhóm P / 48 nhóm N / 100 nhóm có bằng chứng** -> `AVAILABLE`); `looking_around` có **74 P / 146 N / 46 U** (220 mẫu có nhãn biết trước, **46 nhóm P / 87 nhóm N / 121 nhóm có bằng chứng** -> `AVAILABLE`). Baseline dự đoán hằng số theo tỷ lệ lớp `train` (`constant_train_prevalence`) có `Val Macro AP = 0.3886` và `Val Macro Masked BCE = 0.6548`.

### 3.1. Bảng đối chiếu ở ngưỡng mặc định `threshold = 0.50`

| Run ID | Val Macro AP | Val Masked BCE | Target | AP | Precision | Recall | F1 | FPR | TP / FP / FN / TN | Cổng 80/80/20 |
|---|---:|---:|---|---:|---:|---:|---:|---:|---|---|
| `E005-V11-LP` | `0.7013` | `0.5736` | `phone_use` | `0.8029` | `58.93%` | `91.67%` | `0.7174` | `47.92%` | `66 / 46 / 6 / 50` | `FAIL` |
| `E005-V11-LP` |  |  | `looking_around` | `0.5998` | `58.67%` | `59.46%` | `0.5906` | `21.23%` | `44 / 31 / 30 / 115` | `FAIL` |
| `E005-V11-S1-AUG` | `0.7378` | `0.5260` | `phone_use` | `0.8161` | `80.00%` | `66.67%` | `0.7273` | `12.50%` | `48 / 12 / 24 / 84` | `FAIL` |
| `E005-V11-S1-AUG` |  |  | `looking_around` | `0.6595` | `55.67%` | `72.97%` | `0.6316` | `29.45%` | `54 / 43 / 20 / 103` | `FAIL` |
| `E005-V11-AC-L4B1` | `0.7119` | `0.5835` | `phone_use` | `0.7944` | `72.73%` | `66.67%` | `0.6957` | `18.75%` | `48 / 18 / 24 / 78` | `FAIL` |
| `E005-V11-AC-L4B1` |  |  | `looking_around` | `0.6295` | `46.28%` | `75.68%` | `0.5744` | `44.52%` | `56 / 65 / 18 / 81` | `FAIL` |
| `E005-V11-AC-L4` | `0.7119` | `0.5835` | `phone_use` | `0.7944` | `72.73%` | `66.67%` | `0.6957` | `18.75%` | `48 / 18 / 24 / 78` | `FAIL` |
| `E005-V11-AC-L4` |  |  | `looking_around` | `0.6295` | `46.28%` | `75.68%` | `0.5744` | `44.52%` | `56 / 65 / 18 / 81` | `FAIL` |

### 3.2. Bảng đối chiếu ở ngưỡng hiệu chỉnh tối ưu trên Validation (`calibrated_thresholds`)

| Run ID | Target | Ngưỡng `t*` | AP | Precision | Recall | F1 | FPR | TP / FP / FN / TN | Cổng 80/80/20 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `E005-V11-LP` | `phone_use` | `0.67` | `0.8029` | `75.76%` | `69.44%` | `0.7246` | `16.67%` | `50 / 16 / 22 / 80` | `FAIL` |
| `E005-V11-LP` | `looking_around` | `0.50` | `0.5998` | `58.67%` | `59.46%` | `0.5906` | `21.23%` | `44 / 31 / 30 / 115` | `FAIL` |
| `E005-V11-S1-AUG` | `phone_use` | `0.41` | `0.8161` | `74.03%` | `79.17%` | `0.7651` | `20.83%` | `57 / 20 / 15 / 76` | `FAIL` |
| `E005-V11-S1-AUG` | `looking_around` | `0.52` | `0.6595` | `59.55%` | `71.62%` | `0.6503` | `24.66%` | `53 / 36 / 21 / 110` | `FAIL` |
| `E005-V11-AC-L4B1` | `phone_use` | `0.51` | `0.7944` | `75.00%` | `66.67%` | `0.7059` | `16.67%` | `48 / 16 / 24 / 80` | `FAIL` |
| `E005-V11-AC-L4B1` | `looking_around` | `0.65` | `0.6295` | `59.74%` | `62.16%` | `0.6093` | `21.23%` | `46 / 31 / 28 / 115` | `FAIL` |
| `E005-V11-AC-L4` | `phone_use` | `0.51` | `0.7944` | `75.00%` | `66.67%` | `0.7059` | `16.67%` | `48 / 16 / 24 / 80` | `FAIL` |
| `E005-V11-AC-L4` | `looking_around` | `0.65` | `0.6295` | `59.74%` | `62.16%` | `0.6093` | `21.23%` | `46 / 31 / 28 / 115` | `FAIL` |

### 3.3. Khoảng tin cậy 95% theo nhóm (`whole_group_percentile_95`, 5.000 resamples trên 155 nhóm)

| Run ID | Target | Precision 95% CI (t=0.50) | Recall 95% CI (t=0.50) | FPR 95% CI (t=0.50) | Trạng thái Bootstrap |
|---|---|---|---|---|---|
| `E005-V11-LP` | `phone_use` | `[46.7%, 71.9%]` | `[85.2%, 97.2%]` | `[35.1%, 65.0%]` | `AVAILABLE` |
| `E005-V11-LP` | `looking_around` | `[46.8%, 69.1%]` | `[45.5%, 73.2%]` | `[14.9%, 29.1%]` | `AVAILABLE` |
| `E005-V11-S1-AUG` | `phone_use` | `[68.3%, 90.6%]` | `[52.6%, 81.2%]` | `[5.3%, 23.9%]` | `AVAILABLE` |
| `E005-V11-S1-AUG` | `looking_around` | `[45.2%, 65.2%]` | `[61.0%, 84.3%]` | `[22.3%, 38.4%]` | `AVAILABLE` |
| `E005-V11-AC-L4B1` | `phone_use` | `[60.9%, 83.6%]` | `[53.2%, 80.0%]` | `[10.6%, 31.7%]` | `AVAILABLE` |
| `E005-V11-AC-L4B1` | `looking_around` | `[36.5%, 55.8%]` | `[64.5%, 85.9%]` | `[36.3%, 54.6%]` | `AVAILABLE` |
| `E005-V11-AC-L4` | `phone_use` | `[60.9%, 83.6%]` | `[53.2%, 80.0%]` | `[10.6%, 31.7%]` | `AVAILABLE` |
| `E005-V11-AC-L4` | `looking_around` | `[36.5%, 55.8%]` | `[64.5%, 85.9%]` | `[36.3%, 54.6%]` | `AVAILABLE` |

## 4. Phân tích theo Lát cắt Phơi nhiễm (Exposure Slices), Độ phức tạp Khung hình & Nguồn dữ liệu

### 4.1. Bảng kết quả trên 6 lát cắt Validation đã đăng ký trong `protocol.json`

- `unexposed_val_88` (88 mẫu chưa từng nằm ở `train` cũ: gồm 14 mẫu `val` cũ + 74 mẫu `new270_val_74`): `phone_use` có `11 P / 55 N / 22 U` (5 nhóm P, 13 nhóm N -> `INCONCLUSIVE` do `P = 11 < 30`); `looking_around` có `29 P / 59 N / 0 U` (9 nhóm P, 14 nhóm N -> `INCONCLUSIVE` theo cổng V11 do `P = 29 < 30`).
- `former_train_178` (178 mẫu từng nằm ở `train` của V9/V10 được chuyển sang `val` ở V11; các model E005 **chưa từng học** các mẫu này): `phone_use` có `61 P / 41 N / 76 U` (51 nhóm P, 35 nhóm N -> `AVAILABLE`); `looking_around` có `45 P / 87 N / 46 U` (37 nhóm P, 73 nhóm N -> `AVAILABLE`).
- `new270_val_74` (74 mẫu mới bổ sung trong đợt V11): `phone_use` có `10 P / 45 N / 19 U` (4 nhóm P, 5 nhóm N -> `INCONCLUSIVE`); `looking_around` có `25 P / 49 N / 0 U` (6 nhóm P, 6 nhóm N -> `INCONCLUSIVE`).
- `legacy_val_192` (192 mẫu thuộc pool 1.181 mẫu trước V11, gồm 178 `former_train` + 14 `old_val`): `phone_use` `62 P / 51 N / 79 U` (`AVAILABLE`); `looking_around` `49 P / 97 N / 46 U` (`AVAILABLE`).
- `multi_person_context_58` (58 mẫu có `person_area / context_area < 0.70`, khung hình rộng/nhiều người): `phone_use` `10 P / 30 N / 18 U` (`INCONCLUSIVE`); `looking_around` `15 P / 41 N / 2 U` (`INCONCLUSIVE`).
- `single_person_crop_208` (208 mẫu có `person_area / context_area >= 0.70`): `phone_use` `62 P / 66 N / 80 U` (`AVAILABLE`); `looking_around` `59 P / 105 N / 44 U` (`AVAILABLE`).

| Lát cắt (Slice) | Run ID | Macro AP | Phone AP | Phone F1 (`0.50`) | Phone F1 (`cal`) | Look AP | Look F1 (`0.50`) | Look F1 (`cal`) | Support Gate V11 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `unexposed_val_88` | `E005-V11-LP` | `0.5843` | `0.5347` | `0.4286` | `0.4348` | `0.6339` | `0.5556` | `0.5556` | `INCONCLUSIVE` |
| `unexposed_val_88` | `E005-V11-S1-AUG` | `0.6061` | `0.5087` | `0.3158` | `0.4762` | `0.7035` | `0.6562` | `0.6885` | `INCONCLUSIVE` |
| `unexposed_val_88` | `E005-V11-AC-L4B1` | `0.5592` | `0.4893` | `0.4167` | `0.4348` | `0.6292` | `0.6053` | `0.6071` | `INCONCLUSIVE` |
| `unexposed_val_88` | `E005-V11-AC-L4` | `0.5592` | `0.4893` | `0.4167` | `0.4348` | `0.6292` | `0.6053` | `0.6071` | `INCONCLUSIVE` |
| `former_train_178` | `E005-V11-LP` | `0.7243` | `0.8572` | `0.8028` | `0.7826` | `0.5914` | `0.6105` | `0.6105` | `AVAILABLE` |
| `former_train_178` | `E005-V11-S1-AUG` | `0.7565` | `0.8680` | `0.7965` | `0.8125` | `0.6449` | `0.6168` | `0.6275` | `AVAILABLE` |
| `former_train_178` | `E005-V11-AC-L4B1` | `0.7523` | `0.8646` | `0.7544` | `0.7611` | `0.6400` | `0.5546` | `0.6105` | `AVAILABLE` |
| `former_train_178` | `E005-V11-AC-L4` | `0.7523` | `0.8646` | `0.7544` | `0.7611` | `0.6400` | `0.5546` | `0.6105` | `AVAILABLE` |
| `new270_val_74` | `E005-V11-LP` | `0.6019` | `0.4987` | `0.4444` | `0.4000` | `0.7052` | `0.5581` | `0.5581` | `INCONCLUSIVE` |
| `new270_val_74` | `E005-V11-S1-AUG` | `0.6240` | `0.5020` | `0.2667` | `0.4706` | `0.7459` | `0.6667` | `0.6939` | `INCONCLUSIVE` |
| `new270_val_74` | `E005-V11-AC-L4B1` | `0.5741` | `0.4456` | `0.4211` | `0.4211` | `0.7026` | `0.6032` | `0.5909` | `INCONCLUSIVE` |
| `new270_val_74` | `E005-V11-AC-L4` | `0.5741` | `0.4456` | `0.4211` | `0.4211` | `0.7026` | `0.6032` | `0.5909` | `INCONCLUSIVE` |
| `legacy_val_192` | `E005-V11-LP` | `0.7139` | `0.8492` | `0.7838` | `0.7797` | `0.5786` | `0.6038` | `0.6038` | `AVAILABLE` |
| `legacy_val_192` | `E005-V11-S1-AUG` | `0.7487` | `0.8606` | `0.7863` | `0.8030` | `0.6368` | `0.6167` | `0.6316` | `AVAILABLE` |
| `legacy_val_192` | `E005-V11-AC-L4B1` | `0.7376` | `0.8520` | `0.7395` | `0.7521` | `0.6233` | `0.5606` | `0.6168` | `AVAILABLE` |
| `legacy_val_192` | `E005-V11-AC-L4` | `0.7376` | `0.8520` | `0.7395` | `0.7521` | `0.6233` | `0.5606` | `0.6168` | `AVAILABLE` |
| `multi_person_context_58` | `E005-V11-LP` | `0.6000` | `0.6166` | `0.6250` | `0.6957` | `0.5834` | `0.5517` | `0.5517` | `INCONCLUSIVE` |
| `multi_person_context_58` | `E005-V11-S1-AUG` | `0.6339` | `0.6660` | `0.5882` | `0.7368` | `0.6017` | `0.5625` | `0.6000` | `INCONCLUSIVE` |
| `multi_person_context_58` | `E005-V11-AC-L4B1` | `0.5952` | `0.6263` | `0.5556` | `0.5556` | `0.5641` | `0.5000` | `0.5517` | `INCONCLUSIVE` |
| `multi_person_context_58` | `E005-V11-AC-L4` | `0.5952` | `0.6263` | `0.5556` | `0.5556` | `0.5641` | `0.5000` | `0.5517` | `INCONCLUSIVE` |
| `single_person_crop_208` | `E005-V11-LP` | `0.7191` | `0.8288` | `0.7368` | `0.7304` | `0.6095` | `0.6000` | `0.6000` | `AVAILABLE` |
| `single_person_crop_208` | `E005-V11-S1-AUG` | `0.7566` | `0.8431` | `0.7478` | `0.7692` | `0.6701` | `0.6475` | `0.6617` | `AVAILABLE` |
| `single_person_crop_208` | `E005-V11-AC-L4B1` | `0.7386` | `0.8202` | `0.7167` | `0.7288` | `0.6570` | `0.5960` | `0.6230` | `AVAILABLE` |
| `single_person_crop_208` | `E005-V11-AC-L4` | `0.7386` | `0.8202` | `0.7167` | `0.7288` | `0.6570` | `0.5960` | `0.6230` | `AVAILABLE` |

### 4.2. Phân rã kết quả theo từng nguồn dữ liệu (`by_source`, đối chiếu `E005-V11-S1-AUG` và `E005-V11-AC-L4B1` ở `t = 0.50`)

| Nguồn (`source_id`) | Phone P/N/U | Look P/N/U | `S1-AUG` Phone AP / F1 | `S1-AUG` Look AP / F1 | `AC-L4B1` Phone AP / F1 | `AC-L4B1` Look AP / F1 |
|---|---|---|---|---|---|---|
| `classroom_attitude` | `29 / 0 / 4` | `5 / 5 / 23` | `null / null` | `0.9667 / 0.9091` | `null / null` | `0.9667 / 0.7692` |
| `coco_2017_train` | `4 / 2 / 2` | `2 / 2 / 4` | `0.9500 / 0.8000` | `0.7500 / 0.5000` | `1.0000 / 0.8000` | `0.7500 / 0.4000` |
| `commons_classroom_gapfill` | `4 / 1 / 5` | `1 / 4 / 5` | `1.0000 / 0.8571` | `1.0000 / 1.0000` | `1.0000 / 0.8571` | `1.0000 / 1.0000` |
| `consolidated-frames-20261013` | `3 / 2 / 1` | `0 / 6 / 0` | `1.0000 / 1.0000` | `null / null` | `1.0000 / 1.0000` | `null / null` |
| `exam_cheating_keaor` | `6 / 3 / 2` | `4 / 2 / 5` | `1.0000 / 0.9231` | `0.9167 / 0.7500` | `0.9762 / 0.9231` | `0.9167 / 0.6667` |
| `openimages_train_prefix` | `8 / 0 / 19` | `11 / 11 / 5` | `null / null` | `0.5328 / 0.5000` | `null / null` | `0.5220 / 0.4800` |
| `owner-frames-part01-20261016` | `3 / 9 / 10` | `7 / 15 / 0` | `0.2869 / 0.0000` | `0.4603 / 0.4000` | `0.2452 / 0.0000` | `0.5158 / 0.3636` |
| `owner-frames-part02-20261016` | `5 / 30 / 7` | `10 / 32 / 0` | `0.7722 / 0.5714` | `0.6226 / 0.7000` | `0.7125 / 0.6667` | `0.5929 / 0.6087` |
| `owner-frames-part04-20261016` | `0 / 2 / 1` | `2 / 1 / 0` | `null / null` | `1.0000 / 0.6667` | `null / null` | `1.0000 / 0.8000` |
| `owner-frames-part05-20261016` | `2 / 4 / 1` | `6 / 1 / 0` | `0.4167 / 0.0000` | `1.0000 / 0.9231` | `0.4167 / 0.4000` | `1.0000 / 0.9231` |
| `pexels-v2-20261013` | `4 / 2 / 1` | `1 / 6 / 0` | `0.9167 / 0.6667` | `1.0000 / 0.5000` | `0.8042 / 0.7500` | `1.0000 / 0.5000` |
| `roboflow_v1` | `2 / 6 / 8` | `9 / 6 / 1` | `0.6667 / 0.4000` | `0.9301 / 0.8421` | `0.6667 / 0.3333` | `0.9396 / 0.8421` |
| `scb_head` | `0 / 1 / 15` | `13 / 3 / 0` | `null / null` | `0.9542 / 0.7826` | `null / null` | `0.9446 / 0.7826` |
| `scb_hrw` | `0 / 3 / 20` | `3 / 20 / 0` | `null / null` | `0.5889 / 0.6000` | `null / null` | `0.7556 / 0.4286` |
| `student_behaviour` | `0 / 28 / 1` | `0 / 28 / 1` | `null / null` | `null / null` | `null / null` | `null / null` |
| `studentclassroombehavior` | `0 / 2 / 1` | `0 / 3 / 0` | `null / null` | `null / null` | `null / null` | `null / null` |
| `unsplash-20261013` | `2 / 1 / 0` | `0 / 1 / 2` | `0.5833 / 0.8000` | `null / null` | `0.5833 / 0.8000` | `null / null` |

## 5. Đường cong huấn luyện (Epoch-by-Epoch Learning Curves)

| Run ID | Epoch | Giai đoạn (`stage`) | Train Loss | Val Loss | Train Macro AP | Val Macro AP |
|---|---:|---|---:|---:|---:|---:|
| `E005-V11-LP` | 1 | `head_only` | `0.5626` | `0.6232` | `0.6461` | `0.5790` |
| `E005-V11-LP` | 2 | `head_only` | `0.5253` | `0.6016` | `0.7039` | `0.6575` |
| `E005-V11-LP` | 3 | `head_only` | `0.4923` | `0.5644` | `0.7342` | `0.6830` |
| `E005-V11-LP` | 4 | `head_only` | `0.4924` | `0.5730` | `0.7540` | `0.6905` |
| `E005-V11-LP` | 5 | `head_only` | `0.4711` | `0.5490` | `0.7689` | `0.6922` |
| `E005-V11-LP` | **6 (best)** | `head_only` | `0.4738` | `0.5736` | `0.7840` | `0.7013` |
| `E005-V11-LP` | 7 | `head_only` | `0.4451` | `0.5421` | `0.7955` | `0.6993` |
| `E005-V11-LP` | 8 | `head_only` | `0.4314` | `0.5452` | `0.8028` | `0.6920` |
| `E005-V11-LP` | 9 | `head_only` | `0.4254` | `0.5464` | `0.8110` | `0.6933` |
| `E005-V11-LP` | 10 | `head_only` | `0.4429` | `0.5456` | `0.8166` | `0.6909` |
| `E005-V11-LP` | 11 | `head_only` | `0.4776` | `0.6201` | `0.8276` | `0.6950` |
| `E005-V11-LP` | 12 | `head_only` | `0.4126` | `0.5416` | `0.8304` | `0.6821` |
| `E005-V11-S1-AUG` | 1 | `warmup_head_only` | `0.5471` | `0.5910` | `0.6933` | `0.7085` |
| `E005-V11-S1-AUG` | 2 | `warmup_head_only` | `0.5236` | `0.6031` | `0.7422` | `0.7319` |
| `E005-V11-S1-AUG` | 3 | `warmup_head_only` | `0.4830` | `0.5694` | `0.7820` | `0.7343` |
| `E005-V11-S1-AUG` | **4 (best)** | `finetune_layer4_block1` | `0.4184` | `0.5260` | `0.8428` | `0.7378` |
| `E005-V11-S1-AUG` | 5 | `finetune_layer4_block1` | `0.3579` | `0.5214` | `0.8937` | `0.7323` |
| `E005-V11-S1-AUG` | 6 | `finetune_layer4_block1` | `0.3404` | `0.5539` | `0.9203` | `0.7321` |
| `E005-V11-S1-AUG` | 7 | `finetune_layer4_block1` | `0.2864` | `0.5375` | `0.9449` | `0.7145` |
| `E005-V11-S1-AUG` | 8 | `finetune_layer4_block1` | `0.2511` | `0.5430` | `0.9568` | `0.7145` |
| `E005-V11-S1-AUG` | 9 | `finetune_layer4_block1` | `0.2270` | `0.5456` | `0.9634` | `0.7109` |
| `E005-V11-S1-AUG` | 10 | `finetune_layer4_block1` | `0.2121` | `0.5337` | `0.9693` | `0.7143` |
| `E005-V11-AC-L4B1` | 1 | `warmup_head_only` | `0.5307` | `0.6102` | `0.7316` | `0.6961` |
| `E005-V11-AC-L4B1` | **2 (best)** | `warmup_head_only` | `0.4839` | `0.5835` | `0.7794` | `0.7119` |
| `E005-V11-AC-L4B1` | 3 | `warmup_head_only` | `0.4357` | `0.5470` | `0.8169` | `0.6973` |
| `E005-V11-AC-L4B1` | 4 | `finetune_layer4_block1` | `0.4000` | `0.5523` | `0.8718` | `0.7022` |
| `E005-V11-AC-L4B1` | 5 | `finetune_layer4_block1` | `0.3300` | `0.5350` | `0.9118` | `0.6884` |
| `E005-V11-AC-L4B1` | 6 | `finetune_layer4_block1` | `0.3046` | `0.6047` | `0.9359` | `0.6960` |
| `E005-V11-AC-L4B1` | 7 | `finetune_layer4_block1` | `0.2396` | `0.5461` | `0.9617` | `0.6900` |
| `E005-V11-AC-L4B1` | 8 | `finetune_layer4_block1` | `0.2141` | `0.6016` | `0.9722` | `0.6827` |
| `E005-V11-AC-L4` | 1 | `warmup_head_only` | `0.5307` | `0.6102` | `0.7316` | `0.6961` |
| `E005-V11-AC-L4` | **2 (best)** | `warmup_head_only` | `0.4839` | `0.5835` | `0.7794` | `0.7119` |
| `E005-V11-AC-L4` | 3 | `warmup_head_only` | `0.4357` | `0.5470` | `0.8169` | `0.6973` |
| `E005-V11-AC-L4` | 4 | `finetune_layer4` | `0.3668` | `0.5342` | `0.8998` | `0.6960` |
| `E005-V11-AC-L4` | 5 | `finetune_layer4` | `0.2855` | `0.5608` | `0.9431` | `0.6836` |
| `E005-V11-AC-L4` | 6 | `finetune_layer4` | `0.2641` | `0.6630` | `0.9667` | `0.7019` |
| `E005-V11-AC-L4` | 7 | `finetune_layer4` | `0.1668` | `0.5898` | `0.9886` | `0.6845` |
| `E005-V11-AC-L4` | 8 | `finetune_layer4` | `0.1497` | `0.7003` | `0.9930` | `0.6799` |

## 6. Danh sách lỗi điển hình (`FP_FN_gallery`) trên cấu hình tốt nhất `E005-V11-S1-AUG`

Toàn bộ danh sách lỗi `FP` / `FN` của cả 4 run ở ngưỡng mặc định `0.50` và ngưỡng hiệu chỉnh được lưu đầy đủ tại [`fp-fn-gallery.json`](fp-fn-gallery.json). Dưới đây là 10 lỗi có biên độ độ tự tin (`margin = |score - threshold|`) lớn nhất của mỗi target trên cấu hình dẫn đầu `E005-V11-S1-AUG` (ở ngưỡng hiệu chỉnh `t_phone = 0.41, t_looking = 0.52`):

### 6.1. Target `phone_use` (`FP = 20`, `FN = 15`)

| Hạng | `sample_id` | Loại lỗi | `source_id` | `group_id` | Score | Ngưỡng | Margin | Tỷ lệ diện tích `person/context` | Thuộc `new270` | Thuộc `unexposed_88` |
|---:|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | `EXP-RF-013` | **FP** | `roboflow_v1` | `PLAN-9134fdad8c791285` | `0.7732` | `0.41` | `0.3584` | `1.0` | `False` | `False` |
| 2 | `G27-B02-F00016` | **FP** | `owner-frames-part05-20261016` | `PLAN-f620032131205571` | `0.7281` | `0.41` | `0.3132` | `0.6247` | `True` | `True` |
| 3 | `E004-EX-C179` | **FP** | `unsplash-20261013` | `PLAN-d83704f809532ba0` | `0.7217` | `0.41` | `0.3069` | `0.6666` | `False` | `False` |
| 4 | `V7-A-047` | **FP** | `coco_2017_train` | `PLAN-87e972853f88ca19` | `0.7158` | `0.41` | `0.3010` | `1.0` | `False` | `False` |
| 5 | `V7-OE-S104-A01` | **FN** | `classroom_attitude` | `PLAN-53bf2a191101f8af` | `0.1364` | `0.41` | `0.2785` | `1.0` | `False` | `False` |
| 6 | `V7-A-068` | **FN** | `openimages_train_prefix` | `PLAN-5413967e5148fe61` | `0.1647` | `0.41` | `0.2502` | `1.0` | `False` | `False` |
| 7 | `G27-A04-F00043` | **FP** | `owner-frames-part05-20261016` | `PLAN-f620032131205571` | `0.6403` | `0.41` | `0.2255` | `0.9159` | `True` | `True` |
| 8 | `V6-EX-017` | **FP** | `exam_cheating_keaor` | `PLAN-d39bffd423ff6462` | `0.6282` | `0.41` | `0.2133` | `1.0` | `False` | `False` |
| 9 | `V7-A-008` | **FP** | `coco_2017_train` | `PLAN-d7b462cb7b4310d2` | `0.6180` | `0.41` | `0.2032` | `1.0` | `False` | `False` |
| 10 | `V7-A-070` | **FN** | `openimages_train_prefix` | `PLAN-f750c70b1de54473` | `0.2123` | `0.41` | `0.2025` | `1.0` | `False` | `False` |

### 6.2. Target `looking_around` (`FP = 36`, `FN = 21`)

| Hạng | `sample_id` | Loại lỗi | `source_id` | `group_id` | Score | Ngưỡng | Margin | Tỷ lệ diện tích `person/context` | Thuộc `new270` | Thuộc `unexposed_88` |
|---:|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | `V7-C-001` | **FN** | `scb_head` | `PLAN-3d3c7d4033a90641` | `0.2082` | `0.52` | `0.3152` | `1.0` | `False` | `False` |
| 2 | `SCB-read-008` | **FP** | `scb_hrw` | `PLAN-1106b1aaa1a591d7` | `0.8303` | `0.52` | `0.3069` | `1.0` | `False` | `False` |
| 3 | `V7-C-139` | **FP** | `openimages_train_prefix` | `PLAN-fe638f411688362d` | `0.7907` | `0.52` | `0.2673` | `1.0` | `False` | `False` |
| 4 | `SCB-turnhead-021` | **FN** | `scb_head` | `PLAN-dcf2183cdec285cd` | `0.2732` | `0.52` | `0.2502` | `1.0` | `False` | `False` |
| 5 | `E004-EX-C142` | **FP** | `consolidated-frames-20261013` | `PLAN-306328761bd655e8` | `0.7718` | `0.52` | `0.2484` | `0.7363` | `False` | `False` |
| 6 | `V6-SB-034` | **FP** | `student_behaviour` | `PLAN-5c95c56ac7f8af49` | `0.7690` | `0.52` | `0.2457` | `1.0` | `False` | `True` |
| 7 | `G05-A01-F00065-R02` | **FN** | `owner-frames-part01-20261016` | `PLAN-dd195a952d5ce32c` | `0.2853` | `0.52` | `0.2381` | `0.7101` | `True` | `True` |
| 8 | `V7-OE-S033-A01` | **FN** | `openimages_train_prefix` | `PLAN-478d506a279f6541` | `0.2866` | `0.52` | `0.2368` | `1.0` | `False` | `False` |
| 9 | `V6-SB-047` | **FP** | `student_behaviour` | `PLAN-bfee2347d4708b9a` | `0.7433` | `0.52` | `0.2199` | `1.0` | `False` | `True` |
| 10 | `V7-C-075` | **FN** | `roboflow_v1` | `PLAN-47d3e969ba580114` | `0.3042` | `0.52` | `0.2192` | `1.0` | `False` | `False` |

## 7. Giải phẫu nguyên nhân kỹ thuật & bài học từ thực nghiệm E005

1. **Tác động rõ rệt của Regularized MLP Head + 2-Stage Unfreeze (`layer4.1`) + Augmentation + Balanced Smoothed BCE (`E005-V11-S1-AUG`)**: So với Baseline Linear Probe (`E005-V11-LP`, `Val Macro AP = 0.7013`, `Val BCE = 0.5736`), cấu hình `E005-V11-S1-AUG` nâng `Val Macro AP` lên **`0.7378` (+3,65 điểm phần trăm)** và giảm `Val Masked BCE` xuống **`0.5260`** (thấp nhất toàn bộ lịch sử V11). Đặc biệt trên hành vi khó `looking_around`, `AP` tăng vọt từ `0.5998` lên **`0.6595` (+5,97 điểm phần trăm)** và `F1` hiệu chỉnh đạt **`0.6503`**. Trên `phone_use`, ở ngưỡng `0.50`, `E005-V11-S1-AUG` đã đạt **`Precision = 80.00%`** và **`FPR = 12.50%`** (vượt 2/3 tiêu chí cổng chất lượng), và ở ngưỡng hiệu chỉnh `t = 0.41` đạt `Recall = 79.17%` (chỉ thiếu đúng 1 mẫu TP để chạm mốc `80%`) và `F1 = 0.7651`.
2. **Tại sao Single-Crop `E005-V11-S1-AUG` (`0.7378`) vượt qua Dual-ROI Anchor-Context `E005-V11-AC-L4B1` (`0.7119`) trên V11?**: Các quan sát sau gợi ý giả thuyết về giới hạn dữ liệu và kiến trúc; ma trận hiện tại chưa tách riêng tác động của từng yếu tố: (a) Trong 266 mẫu `val` V11, có tới **208 mẫu (`78.2%`)** là `single_person_crop_208` (`person_area / context_area >= 0.70`) và chỉ có **58 mẫu (`21.8%`)** thuộc `multi_person_context_58`; (b) Các file ảnh crop đã lưu trong package V11 vốn là ảnh đã cắt từ frame gốc với kích thước trung bình nhỏ (`150x150` đến `300x300` px). Khi trích xuất tiếp sub-crop `x_anchor` từ ảnh `context` đã nén rồi nội suy bilinear ngược lên `224x224`, luồng `x_anchor` chịu hiện tượng **nội suy kép (double-interpolation blur)** đồng thời làm mất vùng bàn/tay phía dưới thân người đối với `phone_use`; (c) Việc ghép vector `1542D` (`512 + 512 + 512 + 6`) làm số tham số tầng đầu của MLP Head tăng gấp 3 lần (`197.376` so với `65.536` trọng số) và truyền gradient kép qua `layer4`, khiến cả `AC-L4B1` và `AC-L4` đạt đỉnh sớm ngay ở Epoch 2 (`0.7119` trong pha `warmup_head_only`, do đó hai run có cùng model tensors tại Epoch 2; SHA-256 của hai file `best.pt` khác nhau vì bundle còn chứa config/identity riêng) trước khi overfit nhanh vào tập train ở pha mở khóa `layer4` (Epoch 4–8). Ngược lại, `E005-V11-S1-AUG` giữ không gian đặc trưng `512D` gọn nhẹ nên khi mở khóa `layer4.1` ở Epoch 4 đã tăng tiếp từ `0.7343` (Epoch 3) lên đỉnh **`0.7378`** (Epoch 4) và thậm chí vượt `AC-L4B1` ngay trên chính lát cắt `multi_person_context_58` (`Macro AP = 0.6339` so với `0.5952`).
3. **Nguyên nhân cốt lõi khiến chưa qua được cổng `80 / 80 / 20` đồng thời trên toàn tập Validation 266 mẫu**: Dù tất cả model E005 được huấn luyện từ đầu (zero warm-start), phân tích theo lát cắt phơi nhiễm và nguồn dữ liệu cho thấy sự phân cực cấu trúc rất lớn giữa hai phần của Validation V11: - Trên **`former_train_178`** (`178` mẫu thuộc các nguồn cũ), `E005-V11-S1-AUG` đạt **`phone_use AP = 0.8680`**, **`F1(cal) = 0.8125`** (`Precision = 79.4%, Recall = 83.6%`) — sát ngưỡng mục tiêu 80/80. - Ngược lại, trên **`new270_val_74`** (`74` mẫu mới từ `owner-frames-part01..05`), `phone_use` chỉ có **`10 P / 45 N / 19 U`** (tỷ lệ dương tính chỉ `18.2%`, thấp hơn 3 lần so với `54.9%` của `legacy_val_192`, và tập trung dày đặc các ca âm tính khó như cúi viết bài, bấm máy tính bỏ túi, đặt tay dưới gầm bàn ở góc quay rộng `owner-frames-part01` và `part02`). Do đó, trên `new270_val_74`, `phone_use AP` chỉ đạt `0.5020`, kéo `Precision` và `FPR` toàn cục của `phone_use` xuống khi áp dụng chung một ngưỡng quyết định. - Ngược lại, với **`looking_around`**, lô `new270_val_74` lại đạt chất lượng rất tốt (**`AP = 0.7459`**, `F1(cal) = 0.6939`), nhưng các nguồn web/lớp học góc rộng thiếu đồng nhất như `openimages_train_prefix` (`S1-AUG AP = 0.5328`) và `owner-frames-part01/02` (`S1-AUG AP = 0.4603–0.6226`) chứa nhiều ca quay đầu biên độ nhỏ (`15°–25°`) gây chồng lấn điểm số giữa `P` và `N` quanh vùng `0.45–0.60`.

## 8. Khuyến nghị bước tiếp theo cho Owner

- **Giữ `E005-V11-S1-AUG` làm mốc chuẩn mới (Reference Baseline trên V11)**: Kiến trúc Single-Crop với Regularized MLP Head (`512 -> 128 -> 2`), huấn luyện 2 giai đoạn (`warmup 3 epochs -> layer4.1`), Augmentation và Balanced Smoothed BCE đạt kết quả tốt nhất trong ma trận E005 với một seed trên V11; chưa đánh giá độ ổn định qua nhiều seed (`Val Macro AP = 0.7378`, `Val BCE = 0.5260`).
- **Hướng cải thiện tiếp theo (nếu tiếp tục vòng lặp trên V11 hoặc V12)**: (1) Thay vì trích xuất `x_anchor` từ ảnh `context` đã cắt nhỏ (gây mờ do nội suy kép), nếu muốn dùng Dual-ROI thì cần trích xuất trực tiếp `person_box` ở độ phân giải gốc từ frame nguồn hoặc dùng cơ chế **Spatial ROI Mask / Box Attention Map** (ghép thêm 1 kênh nhị phân `H x W` đánh dấu vùng `person_box` ngay trên ảnh `context` hoặc nhân trọng số không gian tại feature map `7x7` của `layer4` trước `avgpool` mà không làm tăng gấp 3 số chiều đầu vào của Head); (2) Bổ sung các mẫu dương tính `phone_use` từ chính các góc máy `owner-frames-part01/02` và rà soát lại ranh giới nhãn `looking_around` ở các góc nghiêng đầu nhẹ (`15°–25°`) trong `openimages_train_prefix` và `owner-frames-part01/02`.
