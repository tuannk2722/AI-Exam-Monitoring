# E007 V13 — chuẩn bị và triển khai Colab

**E007 đã hoàn tất 9 research run trên NVIDIA L4, tổng khoảng 42 phút kể từ launcher. D1 cải thiện rõ trên development V13, nhưng chưa run nào đạt đồng thời hai target.** [Execution companion](../../../configs/experiments/E007-V13-20261024/README.md) giữ variables/authorization; [nghiên cứu gốc](../e007-v13-research-20261023/README.md) giữ rationale. Không final test hoặc promotion.

## Kết quả đã kiểm chứng

Đã import nguyên bản 277 files từ hai archive `runs` và 27 config files, giữ original paths; [receipt import](cloud-import-receipt.json), [campaign](campaign-result.json), [audit số liệu](cloud-results-audit.json). Đối chiếu 221 artifact hashes, config/approval/code/data, labels/masks/groups, chọn best epoch, predictions/metrics reload và recompute calibration từ cached scores đều PASS. Hai cặp smoke có history và tensors last/best khớp chính xác giữa full và resume. Không chạy lại model để kiểm các số liệu này.

| Screening, seed 20261023 | Macro AP | Phone AP | Looking AP | Target qua 80/80/20 |
|---|---:|---:|---:|---|
| R0: ResNet18 224, erasing 0,15 | 0,5436 | 0,7782 | 0,3089 | Không |
| R1: ResNet18 224, bỏ erasing | 0,5386 | 0,7668 | 0,3103 | Không |
| R2: ResNet18 336, bỏ erasing | 0,5324 | 0,7730 | 0,2918 | Không |
| D0: DINOv2 336, frozen | 0,7063 | 0,8202 | 0,5925 | Không |
| D1: DINOv2 336, hai block cuối | **0,8337** | **0,9432** | **0,7241** | Phone |

Xác nhận trên ba seed 20261023/20261024/20261025:

| Chỉ số | R0 | D1 |
|---|---:|---:|
| Mean macro AP ± sample SD | 0,5335 ± 0,0091 | **0,8429 ± 0,0098** |
| Mean phone AP | 0,7727 | **0,9405** |
| Mean looking AP | 0,2942 | **0,7453** |
| Mean raw masked BCE | 0,5007 | **0,2451** |
| Seed qua gate phone | 0/3 | **3/3** |
| Seed qua gate looking | 0/3 | **0/3** |

Delta macro AP D1 − R0 là **+0,30945**, tức **+30,95 điểm phần trăm** trên cùng 185 validation records. Paired bootstrap 2.000 lần trên 92 nhóm, lấy trung bình cùng ba seed cố định, cho percentile CI 95% [0,1790; 0,4191]. Đây là mô tả độ ổn định trên development đã dùng chọn epoch/ngưỡng, không chứng minh generalization hoặc độc lập lineage. Không so trực tiếp con số này với E006 V12 vì nhãn/cohort khác.

| D1 seed | Best epoch | Phone P / R / FPR | Looking P / R / FPR |
|---|---:|---|---|
| 20261023 | 11 | 90,57% / 87,27% / 4,17% | 56,52% / 78,79% / 13,16% |
| 20261024 | 7 | 90,57% / 87,27% / 4,17% | 74,19% / 69,70% / 5,26% |
| 20261025 | 9 | 89,09% / 89,09% / 5,00% | 69,70% / 69,70% / 6,58% |

Các operating points dùng đúng ngưỡng đã ghi trong từng run, không chọn lại để làm đẹp report. Trên cả ba D1 checkpoints, exhaustive score boundaries vẫn **không có** ngưỡng looking đạt 80/80/20: khi recall ≥ 80%, precision tối đa lần lượt 55,10% / 52,94% / 55,77%. Vì vậy đổi threshold đơn thuần không giải quyết được phần còn thiếu.

## Quyết định kỹ thuật và bước tiếp đề xuất

Giữ **D1 làm hướng nghiên cứu chính**. Bỏ erasing hoặc tăng input ResNet18 đơn lẻ không tạo cải thiện trong screening; đổi representation tạo bước tiến, finetune hai block cuối tăng thêm so với frozen DINO. Đây là evidence cho ma trận này, không là kết luận mọi ResNet hoặc resolution đều kém. Không mở toàn backbone hoặc tăng epochs chỉ vì còn budget: best D1 nằm ở epoch 7/9/11, train AP 0,974–0,996 vẫn cao hơn val 0,834–0,853.

Ưu tiên tiếp theo là **looking_around**: có 7 false positives và 5 false negatives lặp ở cả ba seed tại ngưỡng đã freeze. Danh sách ID nằm trong `stable_d1_errors_across_three_seeds` của [audit](cloud-results-audit.json). Nên review hình/cue/head pose/ngữ cảnh của 12 ca này trước khi chốt đối chứng mới; không tự coi lỗi model là lỗi nhãn. Các upstream slices có support nhỏ, không dùng chúng để kết luận nguồn kém. Không chuyển validation sang train hoặc thay nhãn/split V13; bổ sung data/recipe/holdout cần scope mới được owner duyệt.

Run seed 20261024 có macro AP cao nhất 0,8532, có thể dùng làm điểm bắt đầu review artifacts; không tự chọn nó làm model Selected. Giữ nguyên cả ba checkpoint D1 để đánh giá độ ổn định, không ghép hai target từ các seed. Campaign đã dùng đủ 9 research run được duyệt; không tiêu tiếp phần 8 giờ còn dư bằng các lượt ngoài protocol.

## Tài nguyên và khả năng khôi phục

Actual GPU **NVIDIA L4**, FP32, TF32 tắt; Python 3.11.17, Torch 2.8.0+cu128, torchvision 0.23.0+cu128. Smoke 489,54 giây; campaign 2.517,69 giây, gồm setup và các bước của runner trước sync cuối. Không có phép đo CU billing thực tế hoặc thời gian cấp GPU trước launcher. Không suy A100/H100 hoặc lượng CU tiêu thụ từ tên Google AI Pro.

Full best/last checkpoints, resolved configs, code provenance, logs và predictions đã được khôi phục local; cloud giữ private. Các file head initialization riêng **không nằm trong archive runs/configs**; file/tensor hashes còn trong initialization receipts. Không tuyên bố các file đó đã backup hoặc tự tái tạo bytes để lấp pin. Full-model standalone reload trên môi trường gốc đã PASS và không cần external initial head/pretrained; DINO vẫn cần pinned source archive. Handoff checks trước cloud là snapshot lịch sử, không sửa trạng thái NOT RUN trong file đó.

## Thay đổi có tác dụng tới E007

- Schema V4 thêm CUDA FP32 thật, RNG CUDA và runtime identity cho resume; legacy giữ semantics cũ.
- DINOv2-S dùng source revision và weights chính thức đã pin; lấy normalized CLS nối mean normalized patch tokens, head 768 → 128 → 2, đúng freeze/finetune hai block cuối. [License/source/weights receipt](dinov2-pretrained.json).
- Calibration exact một lần trên validation, dùng lại cùng threshold cho mọi cohort/slice/reload; precision không xác định vẫn null. Không còn fit threshold riêng trên train trong V4.
- Preparer kiểm release V13 zero-test, allocation, membership và provenance sidecar. Giữ unresolved upstream, không suy parent của 21 generated ảnh. Cache input được phân biệt theo kích thước/transform/model.
- Runner thực thi smoke trước research, giới hạn thời gian/số run, exact reload parity và checkpoint epoch sang persistent storage. Notebook chỉ mount/setup/verify/launch/unassign; không chứa thuật toán training.

## Kiểm chứng local

| Kiểm | Kết quả |
|---|---|
| Full unit suite | 210 tests PASS, 188,912 giây |
| V4 focused tests | 10 tests PASS: calibration, endpoints/nulls, support-aware ranking, recovery, device, cache, DINO freeze/gradients, resume và reload |
| Ruff `src tests scripts` | PASS |
| Strict mypy source + checker | PASS, 55 source files |
| Compileall | PASS |
| Official DINO source + pretrained trên tensor tổng hợp 336 | PASS state load, exact features parity với upstream, frozen prefix/last-two gradients; CPU, không dùng ảnh V13 |
| Smoke config/data preflight | PASS, đủ 1.119 train / 185 selection; [receipt](local-preflight.json) |
| GPU smoke / research / upload | CUDA smoke PASS; 9/9 research FINISHED và reload PASS; artifacts đã có trên private Drive và import local |

Preflight đầu bị chặn đúng bởi code-identity guard khi source đang được sửa đồng thời; lần kiểm cuối chạy sau khi code ổn định đã PASS. Không sửa approval/pin để bỏ guard. `check_repo.py` PASS trên Git index hiện có; source mới chưa stage vì owner chưa yêu cầu commit, nên không gọi đó là clean-checkout/index validation cho files mới.

## Truy cập cloud và nguồn kỹ thuật

Browser CUA cũ trả `helper_sandbox_lock_failed` sau full access. Khi resume, Chrome DevTools mới kết nối được và thấy campaign đã FINISHED. Đã tải artifacts qua giao diện Drive, không đọc cookies/credentials hoặc chạy thêm GPU. [Cloud folder](https://drive.google.com/drive/u/0/folders/1eud7CyzWnAV9s9vANJ0ERpDH2DMaoVoL) là locator private, không thay quyền chia sẻ.

PyTorch 2.8.0/torchvision 0.23.0 CUDA 12.8 theo [hướng dẫn chính thức](https://pytorch.org/get-started/previous-versions/). `requirements/classifier-colab.txt` là setup recipe, không phải closure lock đã đo trên Linux; actual `pip freeze`/GPU được ghi trước smoke. Ngắt runtime dùng [API Colab chính thức](https://github.com/googlecolab/colabtools/blob/main/google/colab/runtime.py).

Scratch preflight được giữ tạm ở `outputs/_scratch/e007-config-preflight` và `outputs/_scratch/e007-final-preflight`: automatic approval review chặn lệnh cleanup với “blocked by policy”. Đây là derivatives/fixture configs, không phải accepted inputs hoặc results. Không stage media/weights/bundle/checkpoint.
