# E004 — Audit thị giác và lựa chọn ablation

Ngày 14/10/2026. Hoàn thành bước audit tiếp theo [root-cause](../E004-root-cause-20261014/README.md) theo yêu cầu user. **31 crop thuộc đủ 10 family của selection đã được xem; nhận xét Draft, không sửa nhãn hoặc nghiệm thu lại dataset.** Không inference/train mới, không xem test/reserve, không upload.

**Kết luận thực dụng:** ưu tiên ablation recipe trước. Có lỗi với evidence vẫn rõ ở input 224, gồm cả TP của LP bị L4 làm mất; tăng resolution đơn thuần không giải thích hoặc sửa được mọi lỗi. Phone nhỏ trên bàn, che khuất và thiếu chi tiết nguồn là nhánh thứ hai cần giữ. Chưa có kết luận nhân quả rằng head initialization hoặc LR cụ thể là nguyên nhân chính.

## Mở evidence

- [Trang review local — 31 mẫu](../../../outputs/E004-visual-audit-20261014/index.html): exact input 224 và nhận xét, mỗi mẫu có link source/crop/input board.
- [Observations từng crop](observations.json): nhận xét, mức chắc chắn và hành động; chưa là accepted annotation.
- [Inputs và shortlist](review-inputs.json): hashes, lý do chọn, nhãn accepted, LP/L4 outcomes và archive locator.
- [Verification](verification.json): parity, coverage, media hashes và scope.
- [Proposal E004-RC1](../../../configs/experiments/E004-RC1-20261014/README.md): matrix initialization × LR, variables, checks, budget và điểm dừng, chờ duyệt.

Media chỉ local trong outputs; JSON/Markdown giữ evidence nhỏ trong repository. Không vẽ/sinh ảnh hoặc làm sắc nét thay evidence. Bảng source/crop có thu nhỏ để trình bày; exact input lưu riêng 224×224. Đã xem thêm native crop C195/C199/C054/CF-C029 và exact input C009/C029/C044/C195 để kiểm các nhận định chính.

## Phương pháp và coverage

Chỉ dùng cached predictions-selection LP/L4, threshold 0,5. Với family có ≤4 crop lấy toàn bộ; family lớn lấy mỗi target một L4 FN/FP/TP/TN tự tin nhất nếu có, cộng một trường hợp LP đúng/L4 sai nếu có; ties theo sample ID. Sau dedup còn 31 crop. Quy tắc chọn ghi trong inputs, trước khi xem ảnh. Đây là purposive diagnostic sample có bias theo scores, không mẫu đại diện hoặc M4 slice enrollment; không suy tỷ lệ lỗi toàn selection/dataset từ bảng này.

| Scope đã xem | Phone FN / FP | Looking FN / FP |
|---|---:|---:|
| LP trên 31 crop shortlist | 4 / 4 | 9 / 2 |
| L4 trên cùng shortlist | 6 / 2 | 13 / 1 |

Có 8 phone U và 2 looking U, không đánh giá đúng/sai các cells này. 11 crop được ghi nhóm correct-control và một crop hard-negative được L4 sửa đúng; có các target đúng khác trong những crop lỗi. Coverage 31/71 không là audit mọi FN hoặc mọi ảnh V9.

## Phát hiện làm thay đổi ưu tiên

| Bằng chứng trực quan | Ví dụ | Ý nghĩa / giới hạn |
|---|---|---|
| Phone vẫn thấy ở 224 nhưng L4 mất TP của LP | EX-C009: điện thoại cạnh hộp bút/bài làm | Đủ lý do thử recipe; không quy toàn bộ phone FN cho downsample |
| Hướng nhìn ngoài bài vẫn thấy nhưng cả hai FN | EX-C029, EX-C044 | Khoảng thiếu phân biệt ngay trên ảnh rõ; cơ chế cần ablation |
| L4 mất looking TP trong nhiều context | EX-C027, C042, C054, C056 | Hỗ trợ kiểm adaptation; chưa chứng minh riêng LR hoặc initialization |
| Calculator/bút là hard negatives | CF-C029, CN-052 | Phân biệt vật/pose; không đổi mọi vật chữ nhật thành phone positive |
| Phone nhỏ sát mép bàn, một số source vốn nhỏ | EX-C055, C195, C199 | C195 bị thu nhỏ; C055/C199 dưới 224 và được upscale. Tăng input không tạo chi tiết nguồn mới |
| Phone tối/che khuất | EX-C120 | Resolution chưa chắc giải quyết contrast/occlusion |
| Context nhiều người có cả mẫu đúng lẫn sai | CN-044/045 so CN-053/055; EX-C051 | Crowding là factor quan sát, chưa chứng minh attribution sai |
| Adaptation cũng sửa FP | CN-048: LP FP cả hai → L4 TN cả hai; EX-C194 phone FP → TN | Không kết luận L4 làm mọi tình huống xấu đi |

Các ID trong bảng đều có prefix E004-. Cặp EX-ROUND-DESK hữu ích: C044/C194 looking positive bị bỏ sót, C045/C193 looking negative được nhận đúng trong cùng family/cảnh gần nhau. Tương tự CN-044/CN-045 so CN-056. Đối chứng này gợi ý khả năng phân biệt hướng nhìn/vùng bài còn yếu; không chứng minh model đang dùng shortcut nào khi chưa có intervention.

Không đề xuất đổi nhãn trong audit này. C054 trông giống vật cầm tay nhỏ đã có owner giải thích là tài liệu; CF-C029 là calculator; CN-047 là đọc sách. Đã đối chiếu lý do accepted thay vì dùng prediction để phán nhãn sai. Với quan sát không chắc, confidence giữ vừa và không phát sinh nhãn mới.

## Hướng nghiên cứu đề xuất

**Đợt kế tiếp: 4 runs trong matrix 2×2.** Head random/LP đã học × LR layer4 1e-4/1e-5; còn lại giữ E004. Đo epoch0 và steps15/30 của epoch1 dạng diagnostic; không đổi selection rule best checkpoint. [Plan](../../../configs/experiments/E004-RC1-20261014/plan.yaml) có parent/head pins và trần training 8,5 giờ CPU, gồm tối đa 8 giờ main và 30 phút smoke/recovery, không tự chạy thêm.

Resolution/dữ liệu mới chưa chọn cho đợt này. Không review lại corpus, thay class/semantics, tăng epochs hoặc mở holdout. Không có gain development nhất quán thì dừng nhánh recipe, dùng factors audit để chốt data/input. Gain một seed chưa chứng minh ổn định hoặc đủ promotion.

## Checks và lifecycle

- Cached prediction/config hashes khớp checksums; hai model cùng selection membership, labels/masks; shortlist thuộc val experiment V9.
- Restore chỉ source paths được chọn từ archive V9 đúng container SHA; history.restore verify manifest/blobs trước copy. Không decode test/reserve để review.
- 31 crop/source hashes khớp manifest; crop bằng source context-box từng pixel.
- 31 input panels bằng training.data.letterbox từng pixel, lưu PNG 224 riêng; preview khớp preprocess trước normalize.
- Observations phủ đúng 31 IDs, không thừa/trùng; gallery 31 entries, tám boards. Scientific observations chưa được owner nghiệm thu.
- Không sửa source/trainer/config E004 đã pin; không cần chạy lại ML suite cho evidence/docs/proposal. Kiểm JSON/YAML/links/pins/diff/checker ở bàn giao; checker không thay Git delivery của untracked files.

Giữ gallery/boards/inputs224 để owner review local và metadata hashes/observations để trace. Scratch source restore được dọn sau verify archive/boards; source_original_archive_path trong inputs là locator tái lập, source_path là scratch lúc render. Accepted crop và archive không thay đổi. Không commit/upload. Owner duyệt plan mới là bước còn lại trước implementation/run.
