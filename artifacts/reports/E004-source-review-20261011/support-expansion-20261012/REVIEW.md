# E004 — Batch bổ sung support, ngày 2026-10-12

Đã rà **24 nguồn mới** (tổng 160 nguồn đã xem), dựng và kiểm **20 crop từ 10 nguồn**, thuộc 5 ranh giới cảnh đã biết. Đây là lượt bổ sung hữu hạn theo chỉ đạo owner: không bắt buộc tìm đủ 100% trong lượt này; không tự đổi support gates. Không dùng model scores, không mở test 11.

**Mở [trang review sau QA](../../../../data/interim/E004-source-review-20261011/support-expansion-20261012/REVIEW.html).** Thứ tự ảnh: source/anchor/context → native crop → input 224. Chỉ review 20 crop mới; 56 anchors đã accepted giữ nguyên. Bảng dưới là đề xuất, cần owner nghiệm thu nhãn và geometry; chưa phải canonical ground truth, release hoặc split assignment.

## Đề xuất để owner review

Thứ tự `phone_use / looking_around`; P = positive, N = negative, U = unknown. Có thể đồng ý cả batch và chỉ ghi ngoại lệ theo ID. C008 là ngoại lệ sau input QA: hạ phone từ P xuống U; trang review mới và `qa-proposals.json` là đề xuất hiện hành, builder preview giữ trạng thái trước QA.

| ID | Đề xuất | Điểm cần kiểm | Quyết định owner |
|---|---|---|---|
| C001 | P/P | Áo xám kính, cầm mobile và quay đầu ra ngoài bàn | Approve |
| C002 | N/P | Áo cam, tay/bàn không mobile, nhìn ngoài vùng bàn | Approve |
| C003 | P/N | Hoodie giữa, mobile có cụm camera gần túi, đầu cúi | Approve |
| C004 | P/N | Áo khoác phải, cầm mobile và nhìn xuống thiết bị | Approve |
| C005 | P/N | Áo tím, hai tay với mobile, cúi nhìn vùng riêng | Approve |
| C006 | P/N | Bàn giữa trái, mobile giữa hai tay | Approve |
| C007 | P/N | Bàn giữa phải, mobile giữa hai tay | Approve |
| C008 | U/P | Nhổm dậy; vật trên tay ghế bị che/nhỏ ở input 224 | Approve |
| C009 | P/P | Mobile dưới tay trên tay ghế, đầu nhìn sang ngoài bàn | Approve |
| C010 | N/N | Nữ bàn trước trái đọc sách; tay/bàn đủ quan sát | Approve |
| C011 | N/P | Nam bàn trước phải, quay sang người phía sau/trái | Approve |
| C012 | U/P | Nam phía sau nhìn sang bên; tay/bàn nhỏ, phone U | Approve |
| C013 | N/N | Áo trắng ở giữa, tay trên bàn và nhìn xuống bàn | Approve |
| C014 | N/P | Đứng bên phải, tay trên bàn, đầu quay ngang | Approve |
| C015 | N/P | Áo xanh hàng sau trái, cầm giấy nhưng nhìn ra ngoài | Approve |
| C016 | N/P | Áo xanh trước trái, tay trên bàn và đầu quay trái | Approve |
| C017 | N/N | Calculator ở mép bàn không là phone; đầu cúi | Approve |
| C018 | N/N | Tay trên bàn trống, đầu cúi về bàn riêng | Approve |
| C019 | U/N | Một tay dưới bàn nên phone U; nhìn vùng riêng | Approve |
| C020 | U/P | Áo sáng hàng giữa quay sang người bên cạnh, phone khuất | Approve |

ID đầy đủ có prefix `E004-SX-`. Geometry, source/crop/input hashes và lý do ở [geometry](geometry.json), [QA sau input](qa-proposals.json). Không recrop các anchors cũ hoặc tái sử dụng approval cũ cho crop mới. Nhóm ghế gỗ có nhiều frame cùng người/cảnh: variation không đồng nghĩa số người hoặc nhóm độc lập mới.

## Đóng góp và giới hạn

| Target | Draft P | Draft N | Draft U |
|---|---:|---:|---:|
| Phone | 7 | 9 | 4 |
| Looking | 10 | 10 | 0 |

Nếu cả batch được nghiệm thu và sau đó chốt role reserve holdout, pool nhãn candidate 33 + 20 sẽ có phone 17 P/28 N/8 U, looking 29 P/23 N/1 U. Khoảng cách tới 100 P/100 N còn phone 83 P/72 N và looking 71 P/77 N. **Đây là kịch bản sau nghiệm thu, chưa phải support accepted**; không cộng các thiếu hụt thành số ảnh vì targets có thể đồng thời known.

8 ảnh Student mới đều thuộc cảnh train đã biết: 7 overhead/bàn vàng, 1 tường xám/cửa sổ xanh. Không tạo crop evaluation từ nhóm này. Development phone P chưa được bù. 6 nguồn behavie còn lại chỉ triage, không crop ở lượt hữu hạn này; không kết luận chúng không có mẫu hữu ích. [Assessment 24 nguồn](source-assessment.json) và [selection receipt](selection-receipt.json) giữ exact locators/hints.

Ranh giới cảnh draft được đối chiếu tên cũ trong QA: chair-staging, bright-worktables, worn-benches, yellow-flags, blue-cctv. Tên mô tả trong geometry ban đầu được map rõ trong QA; không phải video/session/group IDs mới. Miễn independence theo owner không có nghĩa bỏ duplicate/known-train overlap hoặc tự gán group. Rights local hai ZIP đã có; không xin lại, không upload.

## Kiểm tra và bàn giao

[Validation](validation.json) giữ kết quả pins/containment/pixel reconstruction/null masks/duplicates và bảo toàn historical inputs. Reuse source reader, farthest-first và crop builder hiện có; không đổi production code hoặc spec, không chạy lại ML suite chỉ cho artifacts. Native images, contact sheets và crops giữ local làm evidence review, không đưa media vào Git. Caches phát sinh được dọn sau kiểm; accepted ledgers/releases/configs cũ giữ nguyên.

Bước tiếp: owner nghiệm thu nhãn/geometry batch này, agent nhập bằng importer hiện có theo exact hashes; sau đó tiếp tục bổ sung hữu hạn hoặc chốt membership khi đủ điều kiện. Chưa release/train/final-test từ batch Draft.
