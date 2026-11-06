# Crop từ accepted_frames.zip — 05/11/2026

Owner yêu cầu nghiên cứu khoảng thiếu của dataset/model mới nhất, rồi chỉ xuất crop để review. Nhánh `feat/dataset-crops-20261105`, baseline `b915c08`. **Batch có 390 crop chưa gán nhãn, chưa có P/N/U, chưa chia split, chưa release hoặc train.**

- [Gallery local](../../../data/interim/accepted-frames-crops-20261105/index.html): native, input 336 px, frame gốc và overlay person/context; có toàn bộ 373 frame để owner tìm crop bổ sung.
- [Thư mục PNG native](../../../data/interim/accepted-frames-crops-20261105/crops), [manifest geometry/provenance](../../../data/interim/accepted-frames-crops-20261105/manifest.json).
- [Nghiên cứu và đối chiếu cached evidence](context-audit.json), [input ZIP](intake-checks.json), [inventory 373 frame](inventory.json), [geometry bàn giao](geometry.json).
- [581 đề xuất ban đầu](proposals.json), [các đề xuất bỏ sau hai vòng QA](crop-screening.json). Số trial là locator, không là nhãn hoặc mức chất lượng.

## Dataset và training hiện hành

Đã đọc contracts/data/training/development, reference/decisions; đối chiếu [V14](../dataset-release-20261024-v14/README.md), parent [V13](../dataset-release-20261023-v13/README.md), [đối soát V12](../v12-reconcile-20261022/README.md) và [policy cuối](../v12-reconcile-20261022/owner-policy-20261023.md). Manifest, ledger, release và config V14 local khớp pins trong package-pointers. Counts dưới đây tính lại từ codec đọc manifest, không glob thư mục ảnh.

| Cohort V14 | Crop / nhóm leakage | Phone P / N / U | Looking P / N / U |
|---|---:|---:|---:|
| Train | 1.199 / 245 | 369 / 735 / 95 | 210 / 980 / 9 |
| Val development | 156 / 86 | 44 / 105 / 7 | 29 / 127 / 0 |
| Test | 0 | — | — |

V14 thêm đủ 53 crop generated vào train, giữ nhãn/geometry/bytes của 1.302 crop V13; loại hai crop chất lượng kém và chuyển đủ 27 crop của sáu nhóm liên quan từ val sang train để tránh tách lineage. Không xem synthetic là quan sát độc lập. Nhóm train lớn nhất có 367 crop, tương đương 30,61%; nhóm leakage bảo thủ không đồng nghĩa một video hoặc phòng độc lập. V13 đã có 21 ảnh generated; giới hạn exact upstream provenance trong hồ sơ parent vẫn tồn tại.

Lần train mới nhất là [E008 V14](../e008-v14-colab-20261024/results-20261025.md): 4 smoke + 5 research FINISHED trên A100, G0 thắng G1/A1. Ba seed G0 cùng looking recall 23/29 = 79,31%; precision 79,31% / 82,14% / 76,67%. Không seed nào đạt đồng thời precision và recall 80%. Looking còn thiếu support tối thiểu 30 positive, nên gate chính thức là INCONCLUSIVE, không tự đổi thành FAIL hoặc PASS. Phone qua gate 3/3 seed G0.

Đã kiểm SHA tám metadata/prediction files mỗi seed G0 và đối chiếu lại membership, labels, masks, groups trên đủ 1.199 train / 156 val mỗi run; confusion và giao lỗi ba seed khớp error-cohorts gốc. Không chạy classifier. Không dùng raw metrics E007/V13 so trực tiếp với E008/V14 vì cohort, split và horizon đã đổi. [Quyết định prototype](../e008-v14-colab-20261024/prototype-decision-20261025.md) chỉ chọn G0 seed 20261023 cho prototype, không biến thành model Selected theo gate nghiên cứu.

## Khoảng thiếu có bằng chứng

Đối chiếu [nghiên cứu E007](../e007-v13-research-20261023/README.md), [kết quả E007](../e007-v13-colab-20261024/README.md), [audit looking 90 crop](../looking-around-audit-20261024/README.md), [diagnostics E006](../e006-v12-diagnostics-20261021/README.md), rồi mở lại native và input 336 của **14 crop khác nhau** trong giao lỗi G0 ba seed. Đây là review có mục tiêu, không ước lượng tỷ lệ sai nhãn toàn dataset hoặc chứng minh nguyên nhân model bằng can thiệp.

| Khoảng thiếu | Evidence / ý nghĩa cho crop mới |
|---|---|
| Quan hệ đầu–thân–bàn và hướng lớp | Looking FP bền vững: E004-EX-C001, G08-B02-F00001, V6R2-EX-009, V7-OE-S094-A01-R04. Audit upstream E007 cho thấy camera bên/profile hoặc hướng phía trước lớp dễ bị nhầm; cần giữ mốc không gian và đối chứng viết/đọc so với quay sang bên/sau. Không đổi nhãn cũ từ lỗi model. |
| Quay đầu ở nhiều kích thước và miền | Looking FN: G19-A01-F00052, G19-A02-F00056, V7-C-111. Có native nhỏ/mờ và ảnh người lớn/phòng họp; không thể kết luận mọi lỗi do thiếu pixel hoặc mọi ảnh nhỏ đều vô ích. Cần QA riêng evidence còn thấy ở input 336. |
| Device và vị trí phone đa dạng | Phone FN: V6-CA-011-R04, V6R2-CA-001, V6R2-EX-009, V7-B-031-R03: mặt lưng/ốp sáng, áp tai, vị trí thấp, cầm dựng. ZIP mới có phone trên bàn/trong tay; chưa có bằng chứng đã phủ đủ mọi dạng áp tai hoặc vị trí thấp. Không tạo thêm ảnh để lấp khoảng này. |
| Vật dễ nhầm và attribution | Phone FP: E004-EX-C163, SCB-turnhead-016, V6R2-CA-008-ADD02, V7-C-081. Giữ sách, calculator, bút, tay gần mặt và thiết bị đúng bàn; không suy phone P từ hình chữ nhật hoặc từ thiết bị người bên cạnh. Crop mới vẫn chưa có nhãn. |
| Geometry chưa thống nhất về mức cô lập anchor | 334/1.199 train và 69/156 val có person box bằng context. Chỉ số này là proxy geometry, không chứng minh ảnh có bao nhiêu người hoặc tự là lỗi bbox. Spatial G1/A1 chưa thắng G0 trong E008; không tự suy crop chặt hơn sẽ giúp model. |
| Đánh giá và lineage | Val là development đã dùng cho selection/calibration/audit; 29 looking P thuộc 19 nhóm vẫn thiếu support. Nhiều crop cùng nguồn không thay nguồn độc lập. Không chuyển một crop hoặc điều chỉnh nhãn chỉ để vượt gate; allocation/holdout cần bước riêng sau review. |

Phone U hiện hành chỉ do vật nhìn thấy còn mơ hồ; khuất tay/bàn không tự khiến U. Looking theo policy quay hẳn bên/sau, hoặc nhìn bài người khác khi hơi chéo; góc camera sau không tự tạo P/U. Các semantics này chỉ định hướng giữ evidence, chưa áp state cho batch mới.

## Nguồn ZIP và crop

ZIP owner cung cấp có 104.524.090 bytes, SHA256 `c836bfb05348ebb814d859c1d260beae5238dc3d94a0c3ee6c5f8a8e74f3d088`. Đủ 373 JPEG / 10 parent video; CRC, decode, byte count, SHA và quyết định accepted tương ứng đều khớp. Manifest nguồn vẫn ghi label/split null; `accepted` là quyết định chọn frame trong Foundry, không là nhãn hoặc dataset acceptance. Không có duplicate byte/RGB giữa 373 frame.

| Nguồn kỹ thuật | Frame nguồn | Crop bàn giao |
|---|---:|---:|
| S01 | 62 | 51 |
| S02 | 30 | 20 |
| S03 | 28 | 48 |
| S04 | 30 | 56 |
| S05 | 22 | 20 |
| S06 | 22 | 16 |
| S07 | 23 | 23 |
| S08 | 24 | 48 |
| S09 | 99 | 54 |
| S10 | 33 | 54 |
| Tổng | **373** | **390** |

Đã xem đủ 46 board nguồn, rà chuỗi toàn bộ frame và 581 đề xuất, rồi xem lại crop sau chỉnh geometry ở input 336. Tái dùng V8S/policy/weights đã có từ RUNTIME-V8S-20261026 làm trợ giúp geometry; 4.059 detections trên 373 frame không phải số người/anchor đã xác minh hoặc annotation detector. Không train, tune detector hoặc tải weights mới.

Loại đề xuất bắt nhầm tranh trên tường, box chỉ chứa tóc/tay, crop bị nguồn cắt đầu, người bị che/nhòe quá mức, anchor cạnh tranh hoặc tư thế lặp. Context-v1 là khung đề xuất ban đầu; các vùng hai bên đã được thu lại qua QA để giảm người lân cận, giữ person và evidence của anchor. Hình học gốc và mới cùng được lưu. Crop native là PNG lossless từ ROI RGB, không ép vuông, làm nét, inpaint hoặc upscale. Chỉ preview letterbox thay kích thước.

Owner đã chọn **contract dự án và QA từng crop** khi hỏi conflict với tài liệu `QUY_CHUAN_CAT_VA_THAM_DINH_CROP.md`: giữ fill G0 `[124,116,104]`, không áp giới hạn cứng 120 px hoặc 1–4 crop/anchor. Vẫn giảm gần lặp theo nội dung. ID Pxx chỉ định detection/người trong frame, **không xác nhận continuity/danh tính** qua camera cut; không công bố số anchor độc lập từ các ID đó.

Trong ZIP có giờ học, làm nhóm và sinh hoạt lớp; không gọi mọi hướng nhìn ra khỏi sách là looking P. S09/S10 có trang phục/bối cảnh gần nhau, cần review scene-family trước allocation. Không tìm thấy exact video ID của ZIP trong các metadata text đang tra, nhưng điều đó không chứng minh nguồn mới độc lập với toàn bộ lịch sử V14. Chưa đóng audit cross-source lineage/near-duplicate hoặc cấp vai trò holdout.

License nguồn chỉ là `user-specified-source`. Yêu cầu owner cho phép xử lý crop/review local lần này; không suy thành license phân phối, upload hoặc enrollment train/val. Bản gốc chỉ đọc, media không vào Git hoặc dịch vụ ngoài.

## Kiểm và vòng đời

[Worksheet](build_review.py) xuất crop và dựng gallery cho batch này bằng PIL cùng các công cụ sẵn có `read_pinned_zip`, `PixelBox`, `preview_input` và `sha256_file`. Script kiểm nguồn/geometry trước khi tạo output mới, giữ native ROI, không tạo nhãn/mask/split placeholder và không ghi đè batch đã có. Đã bỏ module `data.frame_crops` và test mới riêng cho module theo yêu cầu owner; không thêm API hoặc test thường trực. Dữ liệu và models V14/E008 được bảo toàn.

Kiểm pixel parity toàn bộ 390 PNG với source ROI, SHA/source membership/geometry, preview, duplicate và links ghi tại [validation](validation.json). Receipt này giữ nguyên bằng chứng lần xuất ban đầu, gồm software checks của module/test sau đó đã được bỏ; không mô tả dependencies hiện hành. Kết quả kiểm sau khi thu gọn tooling ở [tooling cleanup](tooling-cleanup-20261105.json). PASS kỹ thuật không thay review crop, nhãn, rights, group, allocation hoặc chất lượng model.

Có 19 crop có cạnh ngắn native dưới 120 px; đây là thông tin để review kỹ, không là cutoff loại tự động theo lựa chọn owner. Gallery giữ kích thước native khi ảnh nhỏ và cho mở PNG gốc; input 336 là preview riêng. Đã kiểm render Chromium, lọc S06 trả đúng 16 crop / 22 frame, tìm exact ID và đủ 2.697 liên kết ảnh/file local.

Batch ở `data/interim/accepted-frames-crops-20261105` là output review cần giữ cho vòng owner review. Giữ ZIP tại đường dẫn owner cung cấp. Đã bảo toàn output/metadata trước khi dọn scratch; lệnh PowerShell xóa `outputs/_scratch/accepted-frames-crops-20261105` bị bộ duyệt tự động chặn với lý do `blocked by policy`, nên scratch vẫn còn. Không thử cách khác để vượt chặn. Sau khi owner chốt membership và các recrop mới tiến tới annotation/P/N/U; training/config/release cần task tiếp theo.

## Kết quả review của onwer

| ID | Kết quả |
|---|---|
| S01-F00006-P15, S01-F00006-P05, S01-F00009-P02, S01-F00013-P12, S02-F00004-P04, S02-F00038-P11, S02-F00051-P10, S03-F00005-P01, S03-F00005-P02, S03-F00012-P02, S03-F00012-P03, S03-F00015-P01, S03-F00018-P01, S03-F00037-P02, S03-F00047-P01, S03-F00059-P02, S03-F00059-P03, S03-F00063-P02, S03-F00068-P02, S03-F00071-P01, S07-F00001-P03, S07-F00001-P01, S08-F00028-P06, S08-F00041-P01, S08-F00060-P04, S08-F00117-P04, S09-F00018-P03, S09-F00019-P03, S09-F00019-P03, S09-F00071-P01, S10-F00004-P01, S10-F00005-P02, S10-F00006-P03, S10-F00007-P01, S10-F00007-P03, S10-F00008-P02, S10-F00009-P02, S10-F00020-P01, S10-F00032-P03,  | include N/N |
| S01-F00034-P01, S01-F00045-P01, S02-F00012-P11, S02-F00054-P02, S03-F00022-P01, S03-F00063-P05, S03-F00065-P02, S03-F00066-P02, S03-F00072-P01, S03-F00088-P02, S06-F00020-P01, S07-F00012-P14, S08-F00027-P11, S08-F00047-P02, S08-F00057-P01, S08-F00058-P02, S08-F00062-P02, S08-F00069-P02, S08-F00114-P03, S08-F00114-P04, S10-F00019-P01, S10-F00042-P01, S10-F00057-P01,  | include N/P |
| S04-F00004-P01, S04-F00019-P01, S04-F00019-P04, S04-F00084-P02, S04-F00085-P02, S04-F00126-P04, S04-F00148-P02, S04-F00140-P01, S06-F00086-P01, S06-F00095-P01, S06-F00104-P02, S09-F00004-P01, S09-F00009-P02, S09-F00012-P02, S09-F00015-P01, S09-F00015-P03, S09-F00019-P02, S09-F00016-P07, S09-F00021-P05, S09-F00022-P01, S09-F00023-P02, S09-F00025-P02, S09-F00025-P03, S09-F00030-P02, S09-F00036-P02, S09-F00036-P03, S09-F00039-P01, S09-F00041-P01, S09-F00042-P02, S09-F00042-P01, S09-F00045-P01, S09-F00049-P01, S09-F00058-P01, S09-F00064-P01, S09-F00064-P04, S09-F00066-P02, S09-F00069-P02 , S09-F00073-P05, S09-F00076-P02, S09-F00077-P03, S09-F00084-P02, S09-F00086-P02, S09-F00095-P02, S09-F00136-P01, S10-F00011-P01, S10-F00015-P02, S10-F00031-P02 ,  | include P/N |
| S04-F00039-P02, S04-F00045-P04, S04-F00141-P03, S06-F00087-P01, S06-F00096-P01,  | include P/P |
| S04-F00124-P03, S04-F00126-P03, S04-F00129-P05 | include U/N |
