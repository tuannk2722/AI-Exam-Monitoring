# Tổng hợp nghiên cứu dữ liệu đến 2026-10-11

Hồ sơ diễn giải chuyển từ data spec trong task tổ chức tài liệu; không phải release mới hoặc lần audit dữ liệu mới. Số đo đến 2026-10-10, mapping/bàn giao đến 2026-10-11. Không sửa evidence đã seal. Giữ snapshot này; kết quả mới thuộc hồ sơ source/release/audit tương ứng, không append mọi task vào đây.

Đọc [data contract](../../../docs/data.md) cho quy định; [reports index](../README.md) cho evidence gốc; [trạng thái](../../../docs/status.md) cho ưu tiên đang có hiệu lực. Các “bước tiếp” dưới đây là kết luận lịch sử, không tự cấp quyền.

Original research ở Git `ab34b32` (đọc bằng `git show <commit>:<path>`): SCB/RF tại `docs/data/candidates/`, FPI/SCB tại `docs/data/fpi-scb-research-20261007.md`, v6 tại `docs/data/pilot-b-v6-source-proposal-20261007.md`, holdout tại `docs/data/E004-public-holdout-research-20261008.md`, v7 tại `docs/data/v7-targeted-review-20261009.md` và `docs/data/v7-audit-r8-20261009.md`. Xem imports/inventory/pins khi tái dùng inputs, không coi toàn upstream raw còn sẵn. Các quyết định nguồn ở đây thuộc scope snapshot; scope mới cần approval riêng.

## 1. Nghiên cứu nguồn đã thực hiện và kết luận sử dụng

Các con số dưới đây là **audit đúng snapshot vào 2026-10-03–10**, không là inventory nhà cung cấp hiện nay hoặc số mẫu canonical. Khi tiếp nhận bản mới phải xác minh version/hash/terms lại; không lặp công việc đã có cho cùng snapshot và cùng scope.

| Nguồn/snapshot | Đã kiểm / phát hiện | Kết luận còn áp dụng |
|---|---|---|
| SCB ba ZIP Head/HRW/Discuss owner cung cấp | 10.138 ảnh, 8.116 SHA unique; 546 label files bị flag, 625 dòng lỗi; 961 nhóm duplicate có thành viên qua train/val nguồn; metadata video/session thiếu | Head/HRW dùng tuyển looking/negative sau relabel; Discuss đã loại theo owner. Không concat giữ split nguồn hoặc tự map TurnHead/read/write. Quyền SCB đã owner xác nhận, không hỏi lại cùng scope |
| Roboflow `Exam cheating` v1, project `exam-cheating-9iz1y-rrfsz` | 3.407 cặp; 35 dòng vượt biên rất nhỏ trong 34 file, không tự clip; 0 exact duplicate nội bộ/cross-SCB trong audit này. Unit box lẫn device/head/person, gồm UI/phụ đề/watermark; phone 120 raw/117 strict annotations không là accepted positives | Owner review queue 74 ảnh, chốt 28 person crops trên 21 ảnh: 24 phone P, 5 looking P, 1 co-occurrence, đa số target còn unknown. V4 dùng 23/28 crop sau group review. Không dùng toàn nguồn hoặc `No cheating` làm normal |
| Classroom Monitoring v2 | Acquisition/audit và owner review phục vụ v5; 24 ledger records được giữ qua các release | Chỉ membership được duyệt, không coi một project là một tập phòng/camera độc lập; lịch sử này tạo additional train, không holdout |
| Classroom Attitude v3, `classroom-attitude` | 3.573 ảnh, 16 lớp trộn object/behavior/person; 1.122 label rỗng, một dòng 9 trường; 39 lineage-name groups qua split; heuristic resize/re-export gần nguồn cũ | Tuyển person/context và hard negatives được review; empty labels không là negative, dòng sai phải quarantine/re-annotate có trace. 16 lớp không trở thành ontology dự án |
| Student Behaviour v6, `student-behaviour-detection-neazg` | 4.065 ảnh nhưng 2.469 filename lineages; blur/noise augmentation nguồn. 12.912 `Using_phone` bbox; bốn mẫu unit chỉ 9×9–36×25 pixel, không bao người. Similarity thấy nội dung SCB được resize/re-export | Dựng lại person crop/attribution. Nhiều bbox/augmentation không là nhiều tình huống độc lập; không nhập Discuss qua project khác hoặc coi tên mới là nguồn mới |
| Exam Cheating v2, `exam_cheating-keaor` | 772 ảnh/4 lớp; 57 nhóm exact/RGB duplicate với RF v1, 2 nhóm exact qua split nội bộ; video/phim/subtitles lặp; upstream test chỉ 3 `Use_phone` bbox | Bổ sung phần mới có giá trị sau group review; không dùng upstream test làm holdout hoặc nhập `Cheat_paper` thành target |
| FPI-Det | Đầu tiên audit metadata/code; sau đó audit ZIP đủ 22.879 ảnh (18.800/1.730/2.349), 460 label rỗng, 62 SHA duplicate groups, 1 qua val/test; 1.357 dòng bị validator từ chối trong 1.261 file, gồm 242 dòng sai field count | Owner chốt **ngoài membership v6 chính**. Còn annotation/person attribution/semantics/rights chưa giải quyết; không tự sửa/tách/clip nhãn hoặc train từ CSV đánh giá |
| COCO train 2017, Open Images train prefix, Commons/public video | Tuyển/review chọn lọc cho v7; lưu creator/title/source/license/changes và source provenance của từng record; không dùng eval pool để bù train | Chỉ accepted subset local; ảnh phụ trợ không thay domain thi hoặc independent holdout. Blocker rights/lineage vẫn ở ngoài supervision |

Source pin quan trọng của audit đầu: RF v1 ZIP SHA `70060bfe7d65dedcca6a72aaac423c95f402369eec08563b24ae8d962e666eed`; SCB Head `a0fdd6637fb286cbc5d3de83c09f4143686eab0da4d92e4d8007b6b14b3ca828`, HRW `46619af0c0dea011b09b8d50f4c0578420b881b5154e9d11f0447760193a208d`, Discuss `63aa029d04f8e9d5027cc2491aeca10785678750bdae4351835bfceaab95187f`. Không thay ZIP mới cùng tên cho snapshot cũ. Các ZIP đầu do owner cung cấp từ Downloads; archive repo lưu phần input còn giữ, không mặc định có toàn bộ upstream ZIP.

FPI có hai vấn đề cần nhớ khi mở lại: annotation face/phone không cung cấp person bbox/association; CSV 4.079 tên chỉ phủ val/test, 0 tên train. Paper/code nói numeric 0 là phone-use nhưng join CSV/boxes gợi ý chiều ngược; chưa đủ bằng chứng để đảo nhãn. Active-use semantics cũng khác mobile presence đã chốt. MIT repo không tự xác minh rights từng ảnh/DataFountain terms. Không copy benchmark inner-join hoặc rule có face+phone vào production.

Cross-source v6 đã sàng lọc dHash 64 khoảng cách ≤4: 964 Classroom gần RF, 1.359 Student gần SCB, 358 Exam gần RF. Đây là **cờ review**, không số duplicate được xác nhận hoặc threshold independence Accepted. Chín cặp minh họa xác nhận resize/re-export ở những cặp đã xem; không suy mọi cặp ngoài ngưỡng đều độc lập. Các flag liên quan validation/test lịch sử phải quarantine hoặc owner chốt whole-family trước tuyển train.

## 2. Các release đã accepted và vì sao thay đổi

Package nằm dưới `data/processed/pilot-b/`; config tương ứng `configs/datasets/pilot_b_release_v4.yaml` đến `v7.yaml`. Manifest là danh sách supervision; ledger giữ tất cả decisions. Không train bằng cách glob thư mục crops.

| Release | Package suffix | Train / val / test | Manifest | Ledger | Review-only / excluded | Kết quả chính |
|---|---|---|---:|---:|---|---|
| v4 | `pilot-b-20261005-v4` | 60 / 13 / 11 | 84 | 112 | 28 / 0 | RF 28 + SCB84 reviewed; 16 group của used records; 9 normal metadata; local accepted, test freeze |
| v5 | `pilot-b-20261007-v5` | 80 / 13 / 11 | 104 | 208 | 93 / 11 | Train +20 sau review nguồn cũ/Classroom Monitoring; giữ val 13/test 11 và evaluation identity parent |
| v6 | `pilot-b-20261007-v6` | 317 / 50 / 11 | 378 | 498 | 93 / 27 | Nhập subset reviewed SCB/Student/Classroom Attitude/Exam; 471 crop files; bảo toàn 104 used parent và test 11; thêm validation development, không holdout |
| v7 | `pilot-b-20261010-v7` | 689 / 49 / 11 | 749 | 900 | 122 / 29 | 871 crop files; parent corrections +375 new train; whole-family/rights local accepted; không thêm validation mới |

V4/v5/v6 có DVC pointers riêng; v7 giữ local package/release pointer và có snapshot trong archive, chưa có `.dvc` riêng. Chỉ v4 có remote-storage approval/round-trip đã kiểm; không suy quyền remote cho version/model khác. Budget v1 28 RF +84 SCB (28 TurnHead/28 read/28 write) là lựa chọn thiết kế ADR-013 lịch sử, không quota mỗi release.

Scope accepted v7 là `local_classifier_research`; không cấp quyền train experiment, inference test mới, upload/redistribution hoặc remote DVC. Approval experiment nằm trong proposal E004 ở configs/experiments/E004-proposal.md/config/receipt đúng identity. Không nguồn nào trong snapshot này đã cung cấp holdout phòng thi độc lập được nghiệm thu; trạng thái nghiên cứu holdout ở mục holdout bên dưới.

V7 xuất phát từ 498 parent records và pool 402 crop bổ sung. Final pool: 375 new train, 21 U/U review-only, 5 blocker review-only, 1 evaluation-family excluded. Bản preparation 694 train là upper bound cũ; accepted đúng **689**, không lấy proposal làm canonical.

Owner đã review đủ 12 cell được audit E003 nêu. Trong v7: `V6-CA-041` phone U và rời val; `EXP-SCB-002` looking N; `EXP-RF-014` excluded vì crop/text conflict; `EXP-SCB-032` và `SCB-turnhead-023` U; `SCB-turnhead-020` N; các `SCB-turnhead-007/009/012/019/021` và `V6R2-MP-059` giữ P theo review. Tổng 49 parent reviews dẫn tới 9 record changes: 6 target corrections, 2 domain notes, 1 exclusion. V6 trên đĩa giữ nguyên; correction chỉ trong v7, không mở lại nhãn đã được chốt thiếu bằng chứng mới.

Bốn rights blockers `V7-OE-S005-A01/S020-A01/S027-A01/S034-A01` vẫn review-only do landing/metadata license chưa đủ ở thời điểm chốt; `V7-OE-S080-A01` còn boundary liên quan parent val. Crop/label approved không xóa blocker quyền/group. Source reserve ngoài pool giữ lý do, không tự tuyển lại để bù quota.

## 3. Coverage v7 và giới hạn đánh giá — snapshot 2026-10-10

P/N/U = positive/negative/unknown. Các số dưới đây tính từ accepted v7 manifest, không cả ledger/crop folder. Đây là version được phân tích trong snapshot này, không default dataset cho mọi task. Hồ sơ này giữ snapshot v7; release tiếp theo có hồ sơ riêng, không nối coverage mới vào đây.

| Split | Phone P / N / U | Looking P / N / U | Fully-known | Registered groups |
|---|---|---|---:|---:|
| Train 689 | 233 / 184 / 272 | 210 / 277 / 202 | 215 | 375 |
| Val 49 | 16 / 20 / 13 | 17 / 12 / 20 | 16 | 14 |
| Test 11 | 2 / 2 / 7 | 2 / 7 / 2 | 2 | 3 |

Toàn ledger 900 thuộc 449 conservative components; manifest 749 có 392 groups. Exact image/crop/group không qua nhiều split đã được kiểm. **Không có proof independence mới** theo person/session/room; group IDs và SHA unique không chứng minh độc lập. Metadata subject/session/room/video của train/val còn null.

Train v6→v7: 317→689; fully-known 96→215 (30,3%→31,2%), 474/689 vẫn chỉ known một target. Bốn tổ hợp fully-known PP/PN/NP/NN từ 16/3/23/54 thành 36/16/32/131. Largest group Student 91 giữ nguyên, tỷ trọng giảm 28,7%→13,2%; không phải 91 tình huống mới.

Source confounding còn: train v7 SCB Head looking 53 P/12 N; HRW 3 P/81 N; Classroom Attitude phone 83 P/16 N; Student phone 42 P/35 N, looking 44 P/38 N. Cân bằng P/N toàn tập không loại lệch trong từng nguồn. Đây là rủi ro distribution, chưa phải kết luận causal model học shortcut.

375 new train gồm 196 `classroom_or_exam_context`,127 `auxiliary_out_of_exam`,52 context khác/pending; tag classroom không chứng minh CCTV/phòng thi/session mới. Có 22 raw P/N pairs trên 19 exact-source images (phone 5/5 images; looking 17/16 images), không 22 independent sessions. Trong 162 pair R5 lịch sử chỉ 138 vẫn đúng P/N và cả hai train: 132 source-context, 5 same-image, 1 same-scene; không cộng các bảng pair có overlap.

QA input 224/pixel equality đã PASS; không đồng nghĩa phone nhỏ nhìn rõ hoặc model đã học. 119 finding lịch sử chỉ 104 khớp current train crop SHA (94 clear/10 ambiguous); recrop SHA khác không kế thừa review 224 cũ. Chưa có taxonomy đo/pin đầy đủ phone context/visibility/own-workarea/domain/camera-session cho toàn 375 new train.

Val 49 không có mẫu mới: từ val 50 E003 sau correction/exclusion, 14 group, hai group 21+10 crop chiếm 63,3%. Phone 16 P chỉ 4 groups, looking 17 P chỉ 6 groups. Test 11 đã dùng E001, support nhỏ và không quyền inference mới. Không chuyển train sang val/test để vá thiếu đánh giá nếu chưa có policy/version approval.

## 4. Holdout research đã làm và việc còn mở

Ngày 2026-10-08 đã thẩm định metadata nguồn công khai theo yêu cầu owner; chưa có holdout payload/package Accepted. Kết quả này là snapshot nghiên cứu, phải kiểm availability/terms/version khi tiếp nhận thực tế.

| Nguồn | Đã biết | Kết luận/bước tiếp |
|---|---|---|
| CDED-7 / classroom-distraction-tracker | Tác giả mô tả 7 original videos; derived labels Focused/Distracted không trùng targets. Terms nghiên cứu giới hạn, không surveillance/profiling/redistribution raw tùy ý; raw chưa ở local | Ưu tiên thẩm định acquisition/use scope benchmark, original videos/provenance/phone support; không map Distracted→looking hoặc gọi 7 video là 7 independent groups |
| POCO | Công bố 1.903 images/137.960 instances/10 classes; link sample, quyền research riêng, không chia sẻ dataset | Dự phòng có điều kiện; cần đủ payload/terms/two-target evidence và lineage |
| Exam cheat detection ECD | Provider metadata 3.119 images/7 classes/CC BY 4.0, chưa raw/version/source provenance được xác minh | Kiểm re-export/overlap với nguồn đã dùng trước chọn holdout |
| Hashemite paper-based exam actions | Bài báo mô tả 8 actors/cảnh phòng thi; chưa payload/version/license dataset usable | Tiếp tục availability nếu cần; license paper không thay dataset permission |
| MSU OEP | Remote-exam webcam/wearcam/audio/phone, camera khác phòng thi nhiều người | Có thể challenge phone phụ, chưa primary holdout hai target |
| BNU SCB / EduNet / Invigilo | Chưa có raw release/terms/lineage đủ kiểm ở thời điểm nghiên cứu; EduNet cần form, có nguồn YouTube và tự quay | Không coi public repo/code/paper là public usable dataset; không gửi form/email thay owner nếu chưa được yêu cầu |

Tiếp nhận holdout: pin source/version/terms/SHA → quarantine lineage/cross-source overlap → crop/two-target QA không cho reviewer xem candidate scores → sampling/protocol chốt trước prediction → package riêng/freeze/access receipt. Không lấy test 11, val 49/50, upstream test hoặc random frame split gọi là independent holdout. Không cân lại/loại mẫu khó sau thấy metrics.

Ưu tiên được ghi tại thời điểm snapshot: (1) đo targeted matrix thật cho 375 new train và phân biệt primary/auxiliary/parent variants; (2) đề xuất policy new-development whole-groups + holdout độc lập với đủ rights/provenance/P/N support; (3) freeze comparator/recipe/metric theo proposal E004 ở configs/experiments/E004-proposal.md. Owner chốt high-level; không tự hạ gate hoặc ép thêm crop cho đẹp số.

## 5. Vị trí bằng chứng khi cần kiểm/tái lập

Số liệu accepted lấy từ `data/processed/pilot-b/<package>/manifest.jsonl`, `review-ledger.jsonl`, `reports/coverage.json`, `release.json`, `checksums.sha256`; acceptance/provenance ở `artifacts/reports/pilot-b-...release.../`. Audit hiện hành v7/E004 ở `artifacts/reports/E004-v7-fit-audit-20261010/` có measured audit, pair/comparator proposals và cached-score illustration. Agent chỉ mở đúng JSON khi task cần IDs/pins/chi tiết máy đọc.

Nghiên cứu SCB/RF/FPI/v6/v7 gốc còn trong snapshot history hoặc Git `ab34b32`; kết luận cần dùng đã được tích hợp phía trên. Một số report R7/R8/source-funnel có mismatch seal lịch sử, không được reseal hoặc lấy yield/proposal đó thay accepted v7; kiểm exact input khi tái sử dụng. Truy/restore theo docs/operations.md, không bắt agent đọc archive để hiểu domain. Bytes raw/upstream đã bị xóa ở cleanup đầu không tự trở lại bằng Git; kiểm inventory thực tế trước hứa reuse/rebuild nguồn. Config/receipt/sealed originals không sửa để hợp thức hóa tài liệu mới.
