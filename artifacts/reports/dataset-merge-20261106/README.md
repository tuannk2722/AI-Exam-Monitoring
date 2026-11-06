# V15 — Hợp nhất crop và chia train/val ngày 06/11/2026

Đã tạo release local **`pilot-b-20261106-v15`**, gồm **1.721 crop sử dụng: 1.377 train / 344 val development / 0 test**. Owner giao agent rà soát, hợp nhất và chọn allocation; [receipt](owner-direction.json) phân biệt ủy quyền này với việc owner tự duyệt từng box/split tính toán. Không chạy E009 hoặc classifier inference.

- [Gallery 368 crop mới, nhãn cuối và split](../../../data/interim/dataset-merge-20261106/index.html).
- [Bảng toàn bộ 368 crop mới](labels.md), [review gắn SHA và person box](visual-review.json), [inventory và ánh xạ tên file](inventory.json).
- [Package/pins dùng tiếp](package-pointers.json), [config](../../../configs/datasets/pilot-b-20261106-v15.json), [export checks](export-validation.json), [rebuild và bàn giao](handoff-validation.json).

## Tổng hợp và thay đổi nhãn

| Input / quyết định | Kết quả |
|---|---:|
| Batch 390 crop ngày 05/11 | 116 include / 274 exclude theo README và quy tắc mặc định owner |
| Crop owner bổ sung | 252, decode thành công, đưa đủ vào sử dụng |
| Tổng crop mới sử dụng | **368** |
| Parent V14 sử dụng tiếp | 1.353 / 1.355 |
| Crop được sử dụng trong V15 | **1.721** |

README có `S09-F00019-P03` được nhắc hai lần cùng N/N; chỉ tính một mẫu. Không có ID quyết định nằm ngoài batch. Nhãn theo thứ tự **phone / looking**; giữ quyết định owner, ngoại trừ `S06-F00096-P01` được owner đổi từ P/P thành **P/U** sau khi agent báo hướng nhìn chưa đủ rõ. Looking của crop này là null/mask 0, không tham gia loss/metric.

| ID trong V14 | Quyết định trong version mới |
|---|---|
| V6-SB-048-ADD01 | Exclude |
| G08-B01-F00001 | Exclude |
| G09-B05-F00043 | N/P |

V14, source/crop bytes và pins lịch sử giữ nguyên. Hai crop đã bị loại trong V14 tiếp tục excluded. Ledger V15 có 1.999 records, gồm 1.721 sử dụng và 278 excluded; 274 crop mặc định loại không được gán target supervision. N/N không tự thành `confirmed_normal`; context chưa được review riêng giữ unknown.

## Rà trùng, nhãn và geometry

Đã xem đủ 368 crop ở letterbox 336 px với fill `[124,116,104]`, mở native khi cần xác minh thiết bị/hướng đầu, kiểm thêm frame gốc cho ngoại lệ looking. Đã kiểm 252 overlay person box; sửa 77 đề xuất detector bị thiếu tóc, tay/chân nhìn thấy hoặc box chưa bám phần anchor. Đây là sửa **metadata box**, không sửa pixel hay crop lại ảnh owner.

- Không có duplicate bytes hoặc RGB giữa 368 crop mới và 1.355 crop V14.
- Đã xem 50 cặp shortlist bằng dHash ≤ 10 hoặc tương quan RGB 48 × 48 ≥ 0,94; [triage](new-pair-triage.json). Đồng thời xem 5 crop V14 gần nhất cho mỗi crop mới, tổng 1.840 cặp; [ranking](similarity-triage.json). Similarity chỉ phục vụ review, không tự quyết nhãn/nhóm.
- Ảnh gần giống có thay hướng đầu, thay mobile bằng calculator/ví, bỏ mobile hoặc đổi context được giữ cùng family ở train. Ba cặp `M15-N069/N079`, `N074/N081`, `N078/N082` giữ tư thế nhưng thay quyển sách trên bàn: giữ như biến thể context tương quan, không tính là tình huống độc lập.
- Đã mở native các hard negative như `M15-N148`, `N152`, `N158`, `N163`, `N172`, `N174`, `N177`, `N197`, `N205` và `S09-F00018-P03`: calculator/ví không đổi thành phone P. Phone người khác không gán cho anchor. Không thấy lỗi nhãn rõ ràng khác; kết luận này không chứng minh tỷ lệ sai nhãn bằng 0.
- Kiểm **473.688 cặp train–val** bằng dHash sau allocation: chỉ một cặp ≤ 10 (`V6R2-CA-008-ADD02` / `V6-EX-043`, distance 9); đã mở native và xác minh khác người/trang phục/bối cảnh. Không có trùng SHA/RGB hoặc nhóm leakage xuyên split. [Cặp cần xem](cross-split-triage.json).

Ngưỡng similarity là cờ QA của đợt này, không là ngưỡng model hoặc bằng chứng mọi quan hệ tiềm ẩn đã được phát hiện. Không áp cutoff kích thước mới, không làm nét/upscale/inpaint ảnh nhập.

## Lineage và allocation

Owner xác nhận file có tên frame/crop được chỉnh sửa hoặc generate từ **đúng frame/crop đó**. Riêng 28 ảnh `generate 1`…`generate 28` tạo theo lỗi model và không có parent cụ thể. [Lineage](group-lineage.json) giữ quan hệ xác nhận và phần chưa biết; ảnh nhập bảo toàn như delivered blob, không khai recipe generate có thể tái lập.

Toàn bộ 252 crop nhập ở train; native siblings cùng video và nhóm parent đi cùng ranh giới. Giữ 74 ảnh generated kế thừa V13/V14 cùng family ở train. Thematic mới có một ranh giới bảo thủ ở train. S01/S07, S02/S06 và S09/S10 được xử lý bảo thủ theo khả năng liên hệ school/scene-family; không tuyên bố cùng session hoặc nhận diện học sinh. Chỉ S03 trong native mới đưa trọn vào val: 19 crop, gồm 6 looking P và 13 N.

[Allocation tường minh](allocation.json) dùng MILP trên **nguyên nhóm**, không random frame/crop split. Ràng buộc: gần 80/20 theo số crop (344 val), mỗi target ở val có ít nhất 50 P và 50 N, không nhóm val quá 34 crop, giữ nhóm val cũ còn hợp lệ; family có derivative/synthetic và nhóm lớn ở train. Mục tiêu chính giảm lệch tỷ lệ P/N/U và bốn joint states fully known; mục tiêu phụ giảm số crop train cũ phải chuyển. Không dùng predictions/metrics để chọn phương án. Hai lượt solver tìm nghiệm tối ưu trong ràng buộc đã khai; điều đó **không bảo đảm E009 đạt kết quả tối ưu**.

| Cohort | Crop / nhóm leakage | Phone P / N / U | Looking P / N / U | P/P |
|---|---:|---:|---:|---:|
| Train | 1.377 / 219 | 397 / 896 / 84 | 323 / 1.046 / 8 | 54 |
| Val development | 344 / 119 | 100 / 223 / 21 | 81 / 261 / 2 | 14 |
| Test | 0 | — | — | — |

Crop mới: 349 train / 19 val. Chuyển **26 crop thuộc 7 nhóm val cũ → train** sau khi hai crop user exclude rời membership; chuyển **197 crop train cũ → val** theo nguyên nhóm để tăng support và cân bằng. Danh sách đầy đủ ở allocation, không thay assignment trong loader. Nhóm val lớn nhất 32/344 crop; nhóm train lớn nhất 367/1.377. Nhóm leakage bảo thủ không đồng nghĩa số video/session/tình huống độc lập.

Giữ val cũ sau gom derivative và relabel `G09-B05-F00043` chỉ còn 128 crop / 21 looking P; thêm riêng S03 cũng chỉ lên 27 looking P. Split mới tăng support cho cả hai target, giữ nguồn liên quan cùng phía và dùng đủ crop mới owner chọn. Nguyên tắc nguyên nhóm và giới hạn cân bằng tham khảo [StratifiedGroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html); solver dùng [SciPy MILP](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.milp.html). Các con số/ràng buộc là thiết kế allocation theo ủy quyền cho V15, không đổi quality gates experiment.

**Val này là development mới, không phải independent holdout.** E008 và checkpoint lịch sử đã thấy một phần crop vừa chuyển sang val trong training. E009 cần khởi tạo mới từ pretrained được duyệt theo config/protocol riêng; warm-start từ checkpoint lịch sử đó làm evaluation trên val này bị nhiễm. Không so trực tiếp metrics E008/V14 với E009/V15 để tuyên bố tác động dữ liệu. Giới hạn exact parent của generated cũ và quan hệ nguồn tiềm ẩn giữ nguyên; khác SHA không chứng minh độc lập.

## Kiểm, bảo toàn và vòng đời

Tái dùng codec/exporter/integrity/training loader hiện hành; không sửa src, schema, spec, recipe hoặc experiment config. PASS source/crop SHA, pixel parity native, mask/usage/membership, inventory payload, group/cross-split, parent delta đúng ba quyết định, 49 regression tests và rebuild đảo thứ tự records cho checksum inventory giống hoàn toàn. [Export](export-validation.json) và [handoff](handoff-validation.json) giữ evidence. Software PASS không chứng minh model quality.

Input owner snapshot bất biến tại `data/raw/owner-crops-20261106/imports.zip`; bản nhập/sources/ledger/gallery tại `data/interim/dataset-merge-20261106`. ZIP frame gốc chỉ đọc. [Input pins](input-pins.json) và [source roots](source-roots.json) phục vụ traceability/rebuild local, không là remote backup. Quyền là `local_classifier_research`, không suy license phân phối hoặc quyền upload.

Worksheet giữ code **đúng bytes đã thực thi**, được pin trong release; không là API production mới hoặc lệnh chạy lại lên output hiện có. [Software checks ban đầu](software-checks.json) ghi syntax/links, các style findings riêng của snapshot worksheet và trạng thái Git trước khi owner yêu cầu commit. Kết quả kiểm cho bàn giao Git và cleanup hiện tại ở [receipt](cleanup-commit-validation.json); không sửa snapshot hoặc pins để qua lint.

Đã lập [manifest dọn scratch](scratch-cleanup-manifest.json) sau bảo toàn evidence và kiểm exact absolute path/dependencies. [Receipt ban đầu](scratch-cleanup-result.json) ghi lần xóa bị automatic approval review chặn với lý do `blocked by policy`. Khi owner yêu cầu cleanup và commit, kiểm thực tế thấy thư mục scratch này đã không còn; không có thao tác xóa scratch trong task bàn giao và không xác định tác nhân đã xóa. Giữ receipt lịch sử, không ghi đè bằng suy đoán.

Cleanup bàn giao đã lập [manifest riêng](cleanup-commit-manifest.json) cho 172 file cache Python/Ruff/Mypy / 49.219.300 bytes. Lệnh PowerShell xóa đúng các thư mục cache bị automatic approval review chặn với lý do `blocked by policy`; cache còn nguyên, không thử phương thức khác để vượt chặn. Giữ nguyên raw, crop/frame, gallery, source roots, dataset/model và evidence đã pin. Git chỉ giao source/docs/config/metadata; media vẫn local theo chính sách lưu trữ. Không push hoặc train E009 trong task này.
