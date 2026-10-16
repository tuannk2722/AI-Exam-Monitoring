# E004 — Targeted coverage train sau RC1

Ngày 14/10/2026. **Đã lập matrix metadata đủ 716 train/71 selection, xem mới 44 train qua 14 nguồn và đối chiếu 31 selection từ audit thị giác trước. Nhận xét và factors là Draft, chờ owner review batch.** Không train/inference mới, không xem media test/reserve, không sửa nhãn, crop hoặc split.

Kết luận: các tình huống cần học **đã hiện diện trong train**, gồm desk/held/partial phone, calculator, bút và nhìn ngoài vùng bài. Tuy nhiên, chưa có taxonomy thị giác đầy đủ để nói train đã đủ coverage tương ứng selection. W-H vẫn sai một số mẫu train có evidence rõ ở 224; vì vậy chưa đủ cơ sở chỉ quy thất bại cho thiếu số lượng ảnh hoặc chỉ tăng resolution. Ưu tiên tiếp là owner nghiệm thu factors/ngoại lệ trong batch này, rồi chốt hướng bổ sung tình huống sát failure modes hoặc proposal representation riêng dựa trên evidence.

## Mở kết quả và review

- [Gallery local: 44 train và 31 selection](../../../outputs/E004-targeted-coverage-20261014/index.html), có bộ lọc ID/factor/nguồn/cohort, native và input 224; scores ẩn mặc định.
- [Matrix toàn cohort](matrix.json), [summary metadata](summary.json), [shortlist](shortlist.json).
- [Nhận xét từng mẫu](observations.json), [matrix factors thị giác](visual-factor-matrix.json), [bản notes dễ sửa khi review](visual-notes.tsv).
- [Input pins](input-pins.json), [verification](verification.json), [validation bàn giao](validation.json).
- [Rules audit](../../../configs/datasets/E004-targeted-coverage-20261014.yaml), [analysis worksheet](analyze.py), [ghép notes/gallery](assemble.py). Đây là study artifacts dùng codec/preprocess/score validator hiện có, không sửa production source hoặc code identity RC1.

Ngoại lệ cần owner xác định: **V7-OE-S061-A01** có person box gần bao toàn crop nhiều người; [ảnh chỉ box hiện có](../../../outputs/E004-targeted-coverage-20261014/anchor-guide.png). Chưa chắc người nào là anchor nên không đưa mẫu này vào count outside-workarea đã quan sát. Giữ nguyên phone U/looking P accepted; câu trả lời owner ở chat sẽ được ghi thành clarification mới, không sửa release cũ. Các mẫu confidence vừa/thấp được review theo batch; không yêu cầu annotate lại corpus.

## Phạm vi và phương pháp

Inputs đúng experiment package `E004-v9-development-20261013`, payload SHA `df505bf90d85815455ad4fce3d76e5834d55beae1d6bcb89c3f63754a79b4ec9`; scores best checkpoint W-H epoch 1 và LP epoch 10 đã lưu. Membership lấy exact config, không dùng toàn manifest hoặc glob crops. Manifest có diagnostic49 và test11 nhưng chúng không vào matrix, shortlist hoặc media review. Threshold giữ 0,5; unknown luôn masked. Đây là analysis trên development đã dùng, không final evaluation hoặc M4 enrollment.

Shortlist được định trước khi xem ảnh: mỗi source lấy 2; mỗi factor hint lấy 4, riêng calculator-negative lấy hết 3 hints; thêm 3 mỗi target/state P/N/U. Mỗi lượt ưu tiên các family khác nhau, sau đó số lỗi W-H và sample ID; union còn **44 train**. Đó là ngân sách review, không quota dữ liệu. Có bias ưu tiên lỗi; counts/TP/FP trong batch không ước lượng prevalence hay error rate toàn corpus. Các lượt có thể chọn trùng mẫu, family cùng nguồn vẫn không là camera/session độc lập.

Đã xem 8 boards native-fit/224; mở thêm 7 native crops cho các nhận định chi tiết và ngoại lệ anchor. Panels native-fit có thu nhỏ để trình bày; **không** nói đã xem native pixel 1:1 của toàn 44. File PNG 224 lưu riêng bằng preprocessing hiện hành, pixel parity với training letterbox PASS. Nhận xét dựa crop accepted; không restore/xem lại source toàn cảnh trong task này. Không kết luận source → crop mất evidence khi chưa xem source.

31 selection dùng lại observations Draft của [visual audit](../E004-visual-audit-20261014/README.md), join đúng ID/crop SHA; mapping factors được ghi tường minh trong worksheet. Không gọi đây là 31 mẫu xem mới hoặc owner acceptance. [Root-cause](../E004-root-cause-20261014/README.md), [RC1](../E004-RC1-execution-20261014/README.md) và [coverage V7 lịch sử](../E004-post-v7-audit-20261011/README.md) là context; không lấy blocker/quota cũ làm gate mới sau waiver.

## Coverage nào đã đo được?

| Metadata toàn cohort | Train 716 | Selection 71 |
|---|---:|---:|
| Source IDs | 14 | 3 |
| Registered family IDs | 397 | 10 |
| Work context unknown | 605 | 24 |
| Native crop cạnh dài ≤224 | 222 | 7 |
| Không có factor hint theo rules hiện tại | 99 | 22 |

Family IDs là ranh giới quarantine/lineage, **không** số camera/session độc lập. Kích thước crop chỉ là geometry; không đo kích thước phone, độ rõ mắt hay quality. 222 crop ≤224 không có nghĩa 222 crop không dùng được. Work context unknown không có nghĩa ngoài domain hoặc nhãn sai.

| Factor | Metadata hints train / selection | Quan sát Draft trong 44 train / 31 selection | Family chạm tới train / selection |
|---|---:|---:|---:|
| Phone trên bàn | 100 / 0 | 3 / 6 | 3 / 2 |
| Phone cầm tay | 123 / 4 | 13 / 2 | 10 / 1 |
| Phone partial/tối | 11 / 1 | 5 / 2 | 5 / 2 |
| Calculator, phone N | 3 / 2 | 2 / 2 | 2 / 1 |
| Bút, phone N | 62 / 4 | 13 / 6 | 13 / 3 |
| Nhìn ngoài vùng bài | 178 / 9 | 12 / 14 | 12 / 5 |
| Own-workarea/đọc/viết | 290 / 38 | 18 / 15 | 17 / 10 |
| Context nhiều người | 96 / 3 | 28 / 11 | 21 / 6 |

Hai cột đầu có **định nghĩa và denominator khác nhau**, không tính precision/recall của hint bằng bảng này. Hints tìm literal trong reasons, có state filter nhưng chưa xử lý phủ định/“hoặc”. Ví dụ selection có 0 desk hints nhưng audit cũ thấy 6 desk-phone; train V7-OE-S112-A01 có chữ calculator trong câu **không calculator**, thực tế là sách. V6R2-MP-010 có desk hint nhưng ảnh là held-phone. Không hint nghĩa chưa đánh giá, không nghĩa absent. Không cộng các factors chồng nhau.

Observed own-workarea mô tả vùng thao tác thấy trong crop; 2/18 train vẫn looking U theo accepted, không chuyển thành N. Phone/looking metrics vẫn chỉ dùng known. Các counts quan sát là support đã tìm thấy trong batch có chủ đích, không tổng support train; chưa thể chốt quota hoặc “đã đủ/thiếu chính xác bao nhiêu”.

## Đối chiếu failure modes với W-H

Các số dưới là cached W-H **best epoch 1**, không phải predictions train cuối epoch 11; không mâu thuẫn với train loss cuối run rất thấp. Chọn mẫu có ưu tiên lỗi nên không so train/selection error percentages để ước lượng generalization.

| Tình huống đã quan sát | Train trong batch | Selection trong batch | Ý nghĩa |
|---|---|---|---|
| Desk-phone | 3 P, 0 TP/3 FN | 6 P, 2 TP/4 FN | Có supervision tương ứng nhưng không đảm bảo hình dạng/góc/camera đủ đa dạng |
| Held-phone | 13 P, 7 TP/6 FN | 2 P, 1 TP/1 FN | Lỗi tồn tại cả khi vật không nằm riêng trên bàn |
| Partial-phone | 5 P, 3 TP/2 FN | 2 P, 1 TP/1 FN | Che khuất không luôn dẫn tới FN; tách khỏi resolution |
| Calculator negative | 2 N, 1 FP/1 TN | 2 N, 1 FP/1 TN | Có hard negative nhưng support quan sát nhỏ và selection cùng một family |
| Looking ngoài vùng bài | 12 P, 6 TP/6 FN | 14 P, 3 TP/11 FN | Hướng đầu/vùng bài vẫn là khoảng yếu; không tự chứng minh attribution là nguyên nhân |
| Own-workarea | 16 N + 2 U, 7 FP/9 TN | 15 N, 2 FP/13 TN | Giữ U; cần đối chứng cùng pose, tránh gọi cúi đầu luôn negative |

Ví dụ rõ: **V7-A-001** phone tím trên giấy vẫn thấy ở 224 nhưng phone FN; **E004-EX-C002** phone cầm trước laptop vẫn thấy nhưng FN; **EXP-RF-019/V6-CA-028** quay khỏi trang rõ nhưng looking FN; **V7-B-040** viết vào own paper rõ nhưng FP cả hai; **V7-OE-S114-A01** calculator có phím vẫn bị phone FP. Những mẫu này bác bỏ cách giải thích mọi lỗi chỉ do evidence biến mất sau resize, không chứng minh một nguyên nhân thay thế duy nhất.

Đối chiếu selection: EX-C009/C195 là desk-phone; EX-C029/C044 là looking ngoài trang; CF-C029 là calculator. Chúng tương ứng về factor nhưng chưa là matched pairs kiểm nhân quả hoặc cùng góc nhìn/kích thước vật. Không chuyển selection sang train.

## Native/224 và hướng quyết định

Trong 44 notes, mô tả mức evidence chính: **23 clear, 17 limited-native, 3 uncertain, 1 reduced-at-224**. Đây là đánh giá Draft ở cấp crop/tình huống đang mô tả, không rating độc lập từng target, không accepted taxonomy hoặc tỷ lệ toàn train. Limited-native dựa quan sát blur/compression/chi tiết nhỏ, không chỉ dùng ngưỡng kích thước. Trường hợp reduced V7-B-041 phone nhỏ hơn ở 224 nhưng W-H vẫn TP; không chứng minh tăng resolution cứu FN. Không có case mới đủ để quy chắc lỗi cho riêng resize.

1. **Nghiệm thu batch và ngoại lệ anchor trước.** Xác nhận factors/nhận xét hoặc nêu IDs cần sửa. Đây là review audit; không đồng thời nghiệm thu data revision/run mới.
2. **Nếu chọn bổ sung train:** thiết kế scope hữu hạn tập trung phone nhỏ tại cạnh bàn/partial và calculator/bút cùng pose, looking ngoài vùng bài so own-workarea; ưu tiên khác family/camera có provenance. Matrix hiện tại giúp chọn mục tiêu, chưa đủ chốt nguồn, số lượng hay quota. Không loại cảnh khó hoặc kéo selection/reserve vào train.
3. **Nếu chọn input/representation:** chuẩn bị proposal anchor/context cho các lỗi evidence rõ và context nhiều người, với matched control và budget riêng. Audit chưa chứng minh train đã đủ coverage hoặc representation chắc chắn là nguyên nhân; chưa triển khai đổi architecture. Resolution chỉ theo nhánh có evidence native đủ nhưng mất tại input, hiện chưa đủ evidence để ưu tiên blanket increase.

Không chạy confirmation seeds/arms mới. Bước RC1 follow-up về matrix/shortlist đã có đầu ra để owner review; câu hỏi nguồn/recipe mới chỉ đặt sau khi chọn nhánh cụ thể.

## Kiểm và bảo toàn

Kiểm config/prediction SHA theo run checksums, payload-list/manifest pins, exact cohort IDs, labels/masks/groups/sources và quyền local research; 44 crops mới render đúng SHA/geometry, 44 PNG pixel parity PASS. Bàn giao kiểm lại crop/input của cả 75 entries, liên kết local, JSON/YAML, matrix/notes membership, source/config pins và diff. [Validation](validation.json) ghi kết quả thật của checks.

Validation cuối: **787 crop SHA, 75 input parity, 375 liên kết gallery, 15 input pins, syntax và git diff --check PASS; Ruff cho các worksheets PASS.** `check_repo.py --require-git` báo đúng một lỗi: audit YAML mới chưa trong Git index. User chưa yêu cầu commit nên không stage để làm checker PASS; đây là trạng thái delivery, không lỗi data/model và không gọi toàn bộ checker PASS. Không chạy lại ML suite vì production source/recipe không đổi.

Không sửa production source, run/config/release đã pin hoặc spec; index/status/TASK chỉ dẫn tới kết quả mới. Media/HTML local trong outputs có checksums; ảnh gốc đã có trong package và audit trước. Study worksheets + config + notes tái tạo evidence; không tạo scratch checkout/env mới. Không backup off-device/upload hoặc commit; files mới chưa stage, checker không thay Git delivery.
