# E004 — Nghiệm thu crop và xử lý tồn đọng ngày 2026-10-12

**Đã nhập nghiệm thu đủ 56 active anchors:** 49 crop có ít nhất một target known, 7 U/U auxiliary, 85 target cells known. Cả 16 dòng owner nêu đã được xử lý; 40 anchors còn lại được owner đồng ý trong chat. **Chưa có assignment train/development/test mới hoặc group độc lập đã xác minh.**

Bản này là kết quả hiện hành, supersede trạng thái pending acceptance/counts/pairs của [REVIEW-UPDATE](REVIEW-UPDATE.md), không thay source evidence cũ hoặc numeric gates. REVIEW-UPDATE và các JSON `*-current` đã được pin; giữ nguyên bytes nhận từ owner, tạo companion ngày 12/10 thay vì ghi đè. [Receipt](owner-review-receipt-20261012.json) giữ bảng gốc, lời xác nhận trong chat và pins; [quyết định máy đọc](owner-decisions-20261012.json) bind từng source/crop/input và ledger đầu vào.

## Nghiệm thu đã thực hiện

Owner xác nhận “Đồng ý các crop còn lại”, sau đó “Đồng ý cả 10 ngoại lệ” cho đề xuất đã xem source → native crop → input 224. Thứ tự dưới đây là **phone_use / looking_around**.

| Crop | Quyết định đã nhập | Xử lý và lý do |
|---|---|---|
| CN-004 | U/N | Áp dụng hướng đầu về bài theo owner; phone vẫn U |
| CN-006 | N/P | Áp dụng owner xác nhận nhìn sang trái ngoài bài |
| CN-007 | N/N | Chỉ chếch nhẹ, vẫn hướng bài; bỏ pair dùng looking P cũ |
| CN-010 | N/N | Bỏ mô tả thiếu căn cứ “vật ở tay”; tay/bàn không thấy mobile |
| CN-011 | N/N | Tư thế cầm bút/viết không là mobile; hai tay và mặt bàn được review |
| CN-012 | U/N | Không xác nhận vật; chi tiết tay nhỏ nên giữ U theo ngoại lệ đã chốt |
| CN-019 | N/P | Tay/bút/giấy quan sát được, không mobile; nhìn sang người bên cạnh |
| CN-020 | N/P | Sửa mô tả sai “tay dưới bàn”; một tay gần cổ, tay kia giữ bút trên giấy |
| CN-026 | P/N | Owner xác nhận vật là phone |
| CN-031 | N/N | Giữ geometry: anchor phía trước, người nền là context; owner đã đồng ý |
| CN-034 | N/P | Áp dụng owner; khác source SHA/frame với CN-019/031, cùng ranh giới cảnh |
| CN-036 | N/P | Đứng không thêm class hoặc suy cheating; tay/bàn không mobile, nhìn ra ngoài bài |
| CN-039 | U/P | Một tay/vùng bàn còn khuất; không thấy phone chưa đủ phone N |
| CN-040 | U/N | Đầu hướng vùng bài/thiết bị riêng; vật nhỏ chưa đủ phone category |
| CN-043 | U/N | Hướng đầu/bút/bài đủ looking N; biên crop còn thiếu phone evidence |
| CN-041-R2 | P/P | Owner xác nhận phone và nhìn sang bên, áp dụng đúng SHA của R2 |

CN-019/031/034 là frame khác cùng cảnh, không phải ba independent samples. Có người nền không tự làm crop sai: unit là một anchor được chỉ rõ trong context. Giữ các crop đã nghiệm thu, không recrop để rồi tái sử dụng approval trên SHA mới. CN-002/035/041 originals vẫn superseded; chỉ R2 active.

Mở [REVIEW local mới](../../../data/interim/E004-source-review-20261011/owner-review-20261012/REVIEW.html), [QA](pilot-input224-review-20261012.json), [summary](pilot-summary-20261012.json) và [ledger strict](../../../data/interim/E004-source-review-20261011/owner-review-20261012/accepted/ledger.jsonl). Media/ledger local không thuộc Git.

| Target, trên 56 anchors | P | N | U |
|---|---:|---:|---:|
| Phone | 12 | 26 | 18 |
| Looking | 24 | 23 | 9 |

Ledger dùng `PilotRecord` và codec hiện có: known values/masks đã nhập đúng owner review; U giữ null/mask 0. `disposition=approved` chỉ nghiệm thu crop/labels; `usage=review_only`, split/version null, group ID null, chưa release review. Không tự suy work context/normal từ N/N. Quyền xử lý local hai ZIP đã có được bảo toàn, không hỏi lại hoặc mở scope upload.

| Reserve role, chưa là assignment | Crop có target known | Phone P/N/U | Looking P/N/U |
|---|---:|---|---|
| Holdout candidate — behavie | 33 | 10/19/4 | 19/13/1 |
| New-development quarantine — Student instructional | 12 | 0/7/5 | 3/8/1 |
| Train supplement candidate — Student đã train | 4 | 2/0/2 | 2/2/0 |

[Pairs mới](pilot-pairs-20261012.json) còn 5 cặp hợp lệ theo nhãn đã duyệt: 1 phone và 4 looking. Cặp CN-007/CN-008 bị loại vì cả hai looking N. Đây là same-image/cross-anchor diagnostics; label acceptance không biến chúng thành same-person counterfactual, independent pairs hoặc cohort đã freeze.

## Tồn đọng đã xử lý thêm

1. **Nhập nghiệm thu có thể tái lập.** Thêm importer chung `review_acceptance.accept_reviews` và CLI `import_crop_review.py`, dùng strict codec, kiểm membership/target order/scope/ledger/source/crop/input pins; từ chối stale crop, sai scope, duplicate IDs và overwrite. Không sửa builder đã pin hoặc copy script theo vòng review.
2. **Graph overlap/quarantine.** [Graph](source-lineage-20261012.json) quét 12.580 inventory rows hợp lệ, 136 source rows đã xem và 629 source fingerprints non-test của parent. Exact bytes, lineage hints trong cùng export và các scene đã review nối thành 33 thành phần liên quan, bao phủ 193 archive members; 3 thành phần có train-scene overlap, 0 xung đột reserve role quan sát được. Không tìm thấy exact-byte parent overlap trong các thành phần này; đó không là bằng chứng disjointness. 33 components không phải 33 independent groups. Filename hint chỉ là cạnh quarantine thận trọng, không video/session ID.
3. **Kiểm metadata provenance.** Đã hash/đọc data.yaml và hai README của mỗi ZIP. [Kết quả](source-provenance-20261012.json): có export/project/version/license/preprocess, không có mapping từng ảnh tới video/session/phòng/camera. Owner cho phép tự xử lý hợp lý nhưng chưa cung cấp mapping; các ID chưa xác minh giữ null. Không tạo thông tin nguồn để đạt gate.
4. **Tìm thêm phone P ngoài 120 ảnh.** Dùng helper farthest-first hiện có, 8 ảnh mỗi hint phone/Using_phone, source SHA chưa xem và không có cached-overlap flag. [16 ảnh bổ sung](phone-gap-assessment-20261012.json): 13 thuộc cảnh camera cao/bàn vàng, 3 thuộc cảnh tường xám/cửa sổ xanh đã dùng train. Tổng đã xem 136 nguồn; 52 Student sources cùng ba cảnh train. Lượt này không tìm được family phone P mới phù hợp new-development. Đây là lượt triage hữu hạn, không kết luận toàn ZIP không còn family mới; không crop thêm cùng cảnh chỉ để tăng số.

## Phần còn mở và điều kiện tiếp tục

- **G1 đóng phần label/geometry của batch; chưa đóng release/cohort.** Group evidence và role/split membership vẫn cần bằng chứng và nghiệm thu đúng scope. Không tự chuyển 4 supplement candidates vào train hoặc 33 reserve crops thành test.
- **G2/G3:** 0 independent groups proven và 0 accepted new-test support. Giữ ngưỡng 100 P + 100 N mỗi target, ≥10 independent groups, P/N mỗi loại ≥5 groups và ≥2 verified camera/room contexts. Nếu chỉ xét 33 nhãn reserve đã duyệt, count gap là phone 90 P/81 N, looking 81 P/87 N; đây chưa là G3 progress vì assignment/independence chưa đủ.
- **New-development:** vẫn thiếu phone P ngoài train/reserve families. Input cần tiếp là mapping nguồn có thể kiểm hoặc nguồn mới có provenance/quyền phù hợp; source hint và upstream split không đủ. Không lấy các frame cùng cảnh vừa tìm được bù gap.
- **V7 Unknown:** queue 32 cells vẫn conditional; supplementary train chưa Accepted và chưa có outcome/gap mới để kích hoạt. Không relabel hoặc mutate 256 Unknown cells/parent/test.
- **E004 model I1–I8, smoke/run/final test:** importer/graph ở đây là data tooling, không claim đã triển khai fine-tune trainer. Design approval vẫn có hiệu lực; exact data/cohort/config/compute budget và readiness còn thiếu. Không chạy model, mở test 11 hoặc đổi gate để báo hoàn thành hệ thống.

Đã xử lý 16/16 dòng review và đóng vòng kiểm nhãn/geometry/pairs; đã thực hiện graph, metadata provenance và lượt tìm phone bổ sung. Không quy đổi số việc này thành “% hệ thống đạt yêu cầu”, vì các scientific gates còn thiếu evidence thực tế.

## Kiểm tra và bảo toàn

9 source/lineage tests + 6 acceptance tests + 30 pilot tests PASS; Ruff toàn src/tests/scripts, strict mypy 38 files và compile phần mới PASS. 56 active source → crop → input versions tái tạo đúng pixels/hashes; ledger roundtrip strict, deterministic reimport và scope guards được kiểm. [Validation/checks/pins](validation-20261012.json) ghi evidence và limitations.

Giữ V7, ZIP, proposals, QA/summary/pairs/validation cũ, builder snapshots và REVIEW.html cũ. REVIEW-UPDATE có hash khác pin lịch sử do owner đã thêm bảng trước task; receipt ghi rõ mismatch đó và lưu nguyên bản nhận được, không sửa pin cũ. Source/report pins khác vẫn nguyên. Review mới và source triage media được giữ local làm evidence; scratch, staging và caches phát sinh được dọn sau kiểm. Không stage/commit/upload. Git delivery checker vẫn báo files chưa trong index; không stage chỉ để PASS.
