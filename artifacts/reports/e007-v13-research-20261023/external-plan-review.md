# Đối chiếu kế hoạch đang mở ngoài repository

Đọc `C:/Users/OS/Downloads/Ke-Hoach-Nghien-Cuu-Dot-Pha-E007-V13.md` theo context IDE khi resume. Đây là bản tham khảo, không là approval. Không sửa file gốc hoặc suy nguồn tác giả. Các điểm dưới được đối chiếu với source/config/evidence đang có; [báo cáo chính](README.md) giữ đề xuất cuối.

| Nhận định trong bản kế hoạch | Kết quả đối chiếu |
|---|---|
| V13 counts, SQRT weights và 147/27 looking P→N | Counts đúng; transitions phải ghi denominator cùng ID/cùng role. Không kết luận mọi thay đổi là nhãn cũ sai hoặc V13 đã sạch triệt để |
| E006 AP 0,7289, mean SQRT 0,7204 | Không đúng full V12 validation của runs đã pin. SQRT seed 20261020 = 0,692565; mean ba seed = 0,6823. E005 phone/looking AP cũng bị ghi sai: đúng là 0,8161/0,6595 |
| E001–E003 V1–V6, 723 ảnh, AP micro | Không khớp: E001 V4 60/13, E002 V5 80/13, E003 V6 317/50; AP báo macro. E004 RC1 là V9/cohort 716/71; C345 mới có 1.061 train |
| Gate ở docs/training.md §7.4 | File hiện có §§1–3; numerical gate ở owner acceptance ngày 17/10 và experiment protocol, không phải default global §7.4 |
| 167 crop chung chấm AP looking 0,6501→0,2270 | 167 là ID intersection, chỉ 166 crop SHA giữ nguyên. Chênh AP được xác nhận trên cùng 166 crop; phone 0,7852 là 116 known-ID subset, không full val. Không chứng minh train lại chắc chắn đột phá |
| FPR phải ≤3,95% looking và ≤9,17% phone | Đúng tại TP tối thiểu 27 và 44; không là bound chung. Nếu TP tăng, FP cho phép tăng theo floor(TP/4) |
| Allocation schema/preparer giữ 11 test/source bundle | Ba vấn đề tương thích có thật; loader zero-test đã có. Preparer fail ở reservation ID equality trước khi tới overlap guard. Không bỏ guard chỉ vì đếm test bằng 0; phải bind release approval/protocol mới |
| Mọi nguồn gốc ảnh đã biết đầy đủ | 149 NEW thiếu exact upstream source; 21 generated có xác nhận cấp cohort, chưa exact parent. Không suy source thật từ visual-family reference |
| 31,1% ảnh train có nhiều người | Đúng 348/1.119 có person/context area <0,70; proxy này không xác nhận có nhiều người |
| Dual ROI luôn resize context 224 rồi crop/resize lần hai | `_ensure_cached` lấy anchor từ native context PIL trước letterbox riêng. Report E005 cũng có diễn giải double interpolation quá rộng; không sửa report đã pin, không lặp lại như fact |
| Single-crop không spatial jitter là bug E006 | E006 config box_jitter = 0; nhánh jitter chỉ được thiết kế cho dual. Thêm spatial jitter là biến nghiên cứu, không fix requirement bị vi phạm |
| Erasing xóa tới 25% diện tích | Mỗi cạnh dưới S/4, diện tích tối đa xấp xỉ 6,25%; cue nhỏ vẫn có thể bị che |
| E006 18 epochs, warmup 4, unfreeze epoch 5 | Config thật max 12, warmup 3, unfreeze epoch 4. Best 5–7; không có căn cứ phone best epoch 10–14 từ số liệu đã trích |
| Smoothing phá vỡ FPR; focal làm hard negatives bị phạt mạnh hơn BCE | Smoothing làm thay đổi score scale nhưng không đặt FPR. Focal nhấn tương đối hard negatives bằng giảm đóng góp easy negatives; không bảo đảm phạt tuyệt đối lớn hơn BCE hay improve ranking |
| Ghép head tốt nhất từng epoch là hợp lệ vì output độc lập | Hai outputs độc lập về sigmoid không làm feature extractor độc lập. Nếu backbone khác epoch, head phải đi với backbone tương ứng; nếu dùng hai full models thì cần ensemble identity, cost và evaluation riêng. Không ghép heads âm thầm |
| C1 đo gain thuần dữ liệu; C2/C3/C4 cô lập loss/ROI | C1 đổi nhiều biến cùng lúc; các arm khác đổi weighting, scope, heads, pooling, selection. Không phải single-factor ablations và không tách data effect khi labels/cohort đã đổi |
| YAML mẫu chạy với trainer hiện tại | Không: model/objective/schema mới; pad114, extra transforms, workers2 không phải convention hiện tại; thiếu executable pins/approval/device implementation |
| Smoke 1 epoch/2 batches đủ kiểm pipeline mới | Không kiểm được transition sau warmup, optimizer moments khi unfreeze, interruption/resume và reload. Cần synthetic tests trước, smoke đi qua transition thật sau approval |
| E006 R4 chạy cloud | Evidence E006 là local CPU. GPU cloud là hướng E007 owner mới cho phép cân nhắc, budget 4–8 giờ |

Các ý nên giữ: clean initialization theo V13, provenance sidecar, bounded study, erasing ablation, exact PR breakpoints, quan tâm anchor attribution và ngân sách. Các ý ROI/ASL có giá trị như giả thuyết tiếp theo; không coi là sửa lỗi đã chứng minh hoặc triển khai toàn bộ ngay.
