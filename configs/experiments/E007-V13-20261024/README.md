# E007 V13 — thực thi Google Colab

Owner đã duyệt thiết kế [proposal 23/10](../E007-V13-20261023/proposal.yaml), chọn Colab mạnh nhất khả dụng và cho phép upload dữ liệu lên cloud. [Authorization](owner-authorization.json) ghi scope mới; snapshot proposal và release V13 giữ nguyên bytes. **Campaign đã FINISHED trên NVIDIA L4: 9 research run, khoảng 42 phút, reload PASS. D1 thắng screening và cải thiện ổn định qua ba seed; phone qua gate 3/3, looking chưa qua.** [Kết quả đã kiểm](../../../artifacts/reports/e007-v13-colab-20261024/README.md). Không chạy lại các lệnh dưới đây vào identity đã hoàn tất.

## Cấu hình được triển khai

| Arm | Encoder / input | Phần cập nhật sau 3 epoch đầu | Random erasing |
|---|---|---|---|
| R0 | ResNet18 ImageNet, 224 | Head + layer4.1 | 0,15 |
| R1 | ResNet18 ImageNet, 224 | Head + layer4.1 | 0 |
| R2 | ResNet18 ImageNet, 336 | Head + layer4.1 | 0 |
| D0 | DINOv2 ViT-S/14, 336 | Chỉ head | 0 |
| D1 | DINOv2 ViT-S/14, 336 | Head + block 10/11 và final norm | 0 |

Batch 16, FP32, tối đa 12 epoch, patience 6, SQRT weights tính từ train V13, seed screening 20261023. Xác nhận champion và R0 với seed 20261024/20261025, deduplicate nếu champion là R0; tối đa 9 research run. Head khởi tạo chung trong cùng encoder/seed. Không warm-start giữa các arm hoặc từ E006. Chi tiết variables trong snapshot proposal; [design.json](design.json) khóa inputs/pretrained/source/license/template và đường dẫn thực thi.

GPU smoke gồm hai cặp R0 và D1, mỗi cặp full 5 epoch và ngắt sau epoch 3 rồi resume. Chỉ sau parity history/last/best và standalone reload đạt trên GPU, cùng môi trường, mới tạo research configs. Smoke tối đa 45 phút; mỗi research run gồm reload tối đa 40 phút, tổng 8 giờ kể từ launcher. GPU allocation trước khi chạy launcher không đo được từ notebook: kết nối rồi chạy ngay.

Checkpoint chọn theo val macro AP, tie raw BCE rồi epoch sớm. Sau đó fit một cặp threshold trên validation theo exact score breakpoints; dùng lại cho train, val, slices và reload. Support và quality gates giữ nguyên. `group_bootstrap` hiện báo ở ngưỡng mặc định 0,5; không nhầm với CI của ngưỡng calibrated. Provenance upstream là slices riêng; `by_source` giữ source canonical của manifest V13.

## Chạy trên Colab

1. Upload `outputs/E007-V13-Colab-20261024/e007-colab-bundle.zip` vào **My Drive/E007/** của tài khoản AI Pro. Giữ private, không share link public.
2. Mở [notebook launcher](../../../notebooks/E007-V13-Colab.ipynb) bằng Colab. Chọn GPU mạnh nhất đang được cấp và High RAM nếu có, rồi **Run all**. Mount Drive đúng tài khoản khi Google yêu cầu.
3. Launcher kiểm checksum bundle và từng file, tạo môi trường Python 3.11/3.12 riêng, cài recipe [CUDA 12.8](../../../requirements/classifier-colab.txt), lưu `pip freeze`, chạy canonical campaign. Actual GPU/môi trường bị khóa từ smoke; không tự fallback CPU, đổi batch, AMP hoặc model.
4. Kết quả ở **My Drive/E007/E007-V13-COLAB-20261024/**: `runs/campaign.json`, từng run/reload/log, `configs/`, smoke receipt và `recovery/`. Runtime tự ngắt khi hoàn tất hoặc lỗi. Đọc trạng thái trên Drive trước khi quyết định tiếp.

Không coi tên gói AI Pro là bằng chứng GPU/CU thực tế. Google nêu quyền truy cập phụ thuộc tài nguyên khả dụng và hạn mức tài khoản: [Colab FAQ](https://research.google.com/colaboratory/faq.html). Browser CUA cũ lỗi sandbox; Chrome DevTools mới đã đọc được private Drive khi resume. Bundle và campaign đã có trên cloud, artifacts đã import local; chưa có số liệu CU billing.

## Khôi phục và bảo toàn

Mỗi epoch có snapshot tar được ghi đồng bộ rồi atomic replace sang Drive. Snapshot giữ last/optimizer/RNG/config/code/environment/checksums và trạng thái recovery riêng; không thay record của live run. Chỉ dùng `training.recovery.restore_epoch` khi process gốc đã dừng, vào output mới rồi chạy trainer `--resume` với nguyên config/code/runtime. Checkpoint đã FINISHED giữ trong `runs/`; không resume từ snapshot cũ để tạo run bổ sung. Campaign tự dừng khi lỗi và không tự thử lại hoặc tiếp tục queue; cần đối chiếu budget đã dùng và evidence trước recovery. Không chạy lại toàn notebook khi folder campaign đã tồn tại.

Preparer materialize exact YAML/approval trên môi trường Colab trước từng phase, bind code digest; research phase yêu cầu smoke receipt thật. Có thể materialize configs của các confirmation candidate, nhưng runner chỉ thực thi champion và R0 theo budget. Mọi run ghi ID/config/code/data/split/weights/seed/environment/checksums; standalone reload không cần external pretrained nhưng DINO vẫn cần pinned source archive. Không test/promotion; validation V13 là development có giới hạn lineage.

[Evidence và checks](../../../artifacts/reports/e007-v13-colab-20261024/README.md).
