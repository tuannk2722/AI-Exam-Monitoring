# Nghiên cứu chọn tracker — 27/10/2026

## Quyết định

**Chọn B0 làm baseline tracking của prototype hiện tại. Không chọn B1 làm mặc định. Chưa nghiệm thu B0 hoặc B1 cho việc cộng dồn hành vi theo ID.** Quyết định kỹ thuật do agent thực hiện theo yêu cầu owner tự nghiên cứu và quyết định ngày 27/10/2026; không ghi thành owner xác nhận mọi track đúng.

B0 giữ được nhiều observations hữu ích hơn trong clip đã biết. B1 có một số đoạn liên kết tốt hơn, nhưng không chứng minh được lợi ích đủ lớn để đổi lấy những người bị bỏ trống kéo dài. Cả hai có lỗi chuyển ID giữa hai người tại 8 → 9 giây. Vì vậy, baseline selection đã hoàn tất; quality gate cho downstream vẫn chưa đạt. Không mở events/risk/web hoặc tự đóng stage bằng số lượng assignment.

[Decision có pins](../../../../configs/tracking/TRACKING-PROTOTYPE-20261026/selection-20261027.json), [phân tích cached](cached-analysis.json), [visual audit](visual-audit.json). Giữ nguyên mọi output/config/receipt của benchmark ngày 26/10.

## 1. Câu hỏi và phương pháp

Owner thấy B1 nhiều khung đỏ và giao agent tự chọn phương án. Khung đỏ có dấu `?` nghĩa là observation chưa được tracker xuất ID, không phải nhãn hành vi hoặc kết luận detection sai. Màu track khác trong gallery chỉ giúp phân biệt ID.

Nghiên cứu gồm ba lớp: đọc paper và source chính thức; phân tích toàn bộ 60 samples/1.162 observations đã pin; visual audit có chủ đích trên những nhóm làm thay đổi quyết định. Không chạy lại tracker/model, không thay threshold sau khi xem kết quả. Phân tích dùng person box/detector confidence/assignment, không dùng behavior flags để tune tracker.

Tất cả links giữa observations dùng khóa `(sample index, anchor_id)`, không so trực tiếp số ID giữa hai arm. Tập liên kết liền kề của một arm gồm hai anchors cùng track ở hai samples kế tiếp. Phân hoạch toàn clip gồm các cặp anchors cùng track ở bất kỳ hai samples nào. Chỉ so phân hoạch trên 894 anchors mà cả hai arm đều gán. Những đại lượng này mô tả agreement, không phải ground-truth accuracy.

Visual audit chọn bốn mẫu phân bố trong mỗi nhóm của 12 B0 tracks có nhiều B0-only observations nhất; xem toàn bộ 11 B1-only observations; xem các đoạn gây split/merge khác nhau trên phần coverage chung; xem các chuyển động tâm box lớn nhất để tìm phản ví dụ. Đây là mẫu diagnostic có chủ đích, không mẫu ngẫu nhiên và không đánh giá exhaustive mọi identity transition. Không tạo HOTA/IDF1/IDSW toàn clip khi chưa có identity ground truth đầy đủ.

## 2. Kết quả cached, đối soát hai chiều

| Đại lượng | Kết quả |
|---|---:|
| Cả B0 và B1 gán cùng observation | 894 |
| Chỉ B0 gán | 209 |
| Chỉ B1 gán | 11 |
| Cả hai bỏ trống | 48 |
| Coverage B0 | 1.103 / 1.162 = 94,92% |
| Coverage B1 | 905 / 1.162 = 77,88% |
| Chênh lệch coverage | 198 observations; 17,04 điểm phần trăm |

Trong 209 B0-only observations, 184 có detector confidence dưới 0,50 và 25 từ 0,50 trở lên. Toàn bộ 11 B1-only observations dưới 0,50. Như vậy, việc B1 bỏ trống không chỉ là phép lọc trực tiếp confidence; lịch sử khởi tạo/xác nhận/mất track cũng tác động.

B0 có 1.041 liên kết giữa samples liền kề, B1 có 861; 845 liên kết giống nhau. Khi cả hai đầu của một liên kết đều được cả hai arm gán, không có bất đồng nối người trong các cặp liền kề này. **Điều đó không chứng minh liên kết đúng:** hai arm có thể cùng sai.

Xét mọi khoảng thời gian, trên 894 anchors chung có 20.394 cặp cùng-track chung, 378 cặp chỉ B0 nối và 555 cặp chỉ B1 nối. Các cặp tương quan mạnh, không phải 933 lỗi độc lập. Khác biệt tập trung ở năm nhóm: B0 T3 và T7 được B1 chia thành hai ID; B1 T6/T9/T33 tương ứng nhiều ID B0. Vì vậy, phát biểu “hai arm tracking giống hệt nhau” cũng không đúng.

## 3. Visual evidence thay đổi quyết định như thế nào

| Case | Quan sát trên các source crops đã xem | Ý nghĩa |
|---|---|---|
| B0 T13/T30 | Người ngồi áo trắng ở cùng vùng bàn xuất hiện rõ tại các mẫu 0/5/11/16 và 18/32/46/59 giây; B1 null tại các anchors này | 59 B0-only assignments thuộc hai tracklets; không thể coi tất cả box đỏ là background |
| B0 T14 | Người áo sáng cạnh tường vẫn thấy tại 0/12/25/37 giây; B1 null ở những anchors đã xem | 38 B0-only assignments; B1 mất coverage kéo dài, không chỉ một frame |
| B0 T58 | Người đội mũ gần cửa sổ vẫn thấy tại 36/43/52/59 giây | 22 B0-only assignments; còn là người nhìn thấy |
| B0 T55 | Crop hẹp trỏ vào vùng người cũng nằm trong B0 T7 / B1 T28 | Có lợi ích lọc duplicate từ B1; không gọi mọi B0-only assignment là một người bổ sung |
| Năm nhóm split/merge | Các mẫu trước/sau nhìn tương thích với cùng người ở cùng vùng; mỗi arm có những đoạn chia ID khác nhau | B1 cũng có lợi ích continuity cục bộ; không kết luận B0 thắng mọi loại lỗi |
| Cả hai T10, 8 → 9 giây | `f00000240-a004`: người ngồi áo xanh/đội mũ; `f00000270-a000`: người áo trắng đi qua. Cả hai vẫn ID 10 | **Mixed-person track quan sát rõ; chặn dùng ID thô để cộng dồn hành vi** |
| B0 T57 / B1 T37, 36 → 39 giây | Full body → phần đầu ở gần mép camera; context không đủ để chứng minh continuity chỉ từ hai crops | Giữ uncertain, không ép thành một nhãn đúng/sai |

Các số 59/38/22 là độ dài nhóm cached, không phải toàn bộ số ảnh đã được gán nhãn thủ công. Đối soát geometry cho B0 T30 cho thấy không có box B1 assigned nào giao với box của nhóm đó trong 42 B0-only observations; vì vậy không thể giải thích riêng nhóm này là B1 đã giữ một duplicate trùng vị trí. Những kiểm tra overlap khác chỉ là diagnostic, không thay identity matching.

Board [extra-0](../../../../outputs/tracking-research-20261027/extra-0.jpg), [extra-1](../../../../outputs/tracking-research-20261027/extra-1.jpg), [partition](../../../../outputs/tracking-research-20261027/partition-cases.jpg), [B1-only](../../../../outputs/tracking-research-20261027/B1-only.jpg), [largest-jumps](../../../../outputs/tracking-research-20261027/largest-jumps.jpg). Tất cả là derivative local từ gallery đã pin, cùng deadline media; không có tên thật, không upload.

## 4. Giải thích bằng paper và source đúng version

**ByteTrack không quy định một threshold tối ưu cho mọi camera.** Paper dùng detections điểm thấp để nối tiếp track và khởi tạo track mới từ detections điểm cao; còn thảo luận failure của motion cues trong dữ liệu camera chuyển động/FPS thấp. Kết quả MOT17 không chứng minh chất lượng trên lớp học này. [Paper ByteTrack, thuật toán và ablation](https://arxiv.org/html/2110.06864v3).

**Trong bản 8.3.221 đang cài**, nhánh điểm thấp chỉ cập nhật các tracks còn trạng thái Tracked, không tự khởi tạo và không dùng để phục hồi Lost trong bước đó. B1 đưa detections 0,25–0,50 vào nhánh này; người có confidence thấp kéo dài có thể không khởi tạo hoặc không phục hồi được. B0 cho phép dải đó vào association chính/khởi tạo. Track xuất hiện muộn còn cần xác nhận. Đây là lý do cơ chế, không là truy vết chính xác nguyên nhân từng null. [Source BYTETracker 8.3.221](https://github.com/ultralytics/ultralytics/blob/v8.3.221/ultralytics/trackers/byte_tracker.py).

**Matching không chỉ là high threshold.** Source `fuse_score` dùng cost `1 - IoU × confidence`; `match_thresh=0,80` áp dụng trên cost này. Nhánh phụ dùng IoU cost và giới hạn 0,50. Vì vậy, với confidence 0,30, association chính cần IoU khoảng 0,667, còn nhánh phụ có thể chấp nhận khoảng 0,50 khi có track phù hợp. Đây giải thích vì sao B1 vẫn giữ được 11 observations mà B0 không giữ; không kết luận low-threshold luôn tốt hơn. [Source matching](https://github.com/ultralytics/ultralytics/blob/v8.3.221/ultralytics/trackers/utils/matching.py).

B0 dùng high/new 0,25 theo [default config của đúng version](https://github.com/ultralytics/ultralytics/blob/v8.3.221/ultralytics/cfg/trackers/bytetrack.yaml), nhưng buffer/clock đã điều chỉnh theo proposal. Default chỉ là điểm xuất phát; lý do chọn ở đây là evidence local. Input đã cắt dưới 0,25 nên low stage của B0 không có dữ liệu để sử dụng. Không gọi đây là đánh giá đầy đủ lợi ích low-score ByteTrack.

**1 Hz là giới hạn riêng.** Nghiên cứu ColTrack cho thấy khoảng cách lớn giữa frames làm motion/appearance biến đổi và gây suy giảm tracking. Đổi `frame_rate` trong constructor hiện tại chỉ ảnh hưởng tuổi lost track; không tạo lại 29 frames trung gian. Không chuyển kết quả trên benchmark khác thành đảm bảo cho clip này. [ColTrack, ICCV 2023](https://arxiv.org/abs/2308.05911).

**Đánh giá cần tách detection và association.** HOTA được xây dựng để cân bằng cả hai, thay vì tối ưu một số đếm duy nhất. Muốn báo metric chuẩn cần ground truth thích hợp; assignment coverage, track count và agreement B0/B1 không thay được nó. [HOTA](https://arxiv.org/abs/2009.07736), [TrackEval chính thức](https://github.com/JonathonLuiten/TrackEval).

## 5. Đối chiếu các phương án ngoài B0/B1

| Phương án | Kết quả nghiên cứu liên quan | Quyết định cho task này |
|---|---|---|
| N0 | Không nối thời gian, mỗi anchor một ID | Chỉ baseline đo lường; không giải quyết tracking |
| B0 | Coverage local tốt hơn, giữ người confidence thấp; vẫn mixed-person/fragmentation/duplicate | Chọn baseline prototype, không chất lượng downstream |
| B1 | Nhánh low-score và một số đoạn continuity tốt hơn; bỏ trống kéo dài | Không chọn mặc định; giữ comparator |
| OC-SORT | Sửa tích lũy sai số Kalman qua occlusion bằng observations, hợp lý để nghiên cứu motion khó | Chưa benchmark local, không thay bằng tuyên bố paper. [Paper](https://arxiv.org/html/2203.14360v2) |
| BoT-SORT / ReID | Kết hợp motion, appearance và camera compensation | Camera clip này cố định; ReID cần weights/compute và kiểm domain. Chưa có evidence local rằng tốt hơn. [Paper](https://arxiv.org/abs/2206.14651) |
| DeepSORT | Appearance metric hỗ trợ association qua occlusion | Không tự tải model mới; áo đồng dạng/occlusion cần kiểm thực tế. [Paper](https://arxiv.org/abs/1703.07402) |
| ColTrack | Thiết kế riêng cho robustness theo frame rate | Đổi lớn sang mô hình end-to-end, chưa phù hợp scope reuse V8S/G0 hiện tại. [Paper](https://arxiv.org/abs/2308.05911) |

Không chọn tracker mới chỉ vì leaderboard cao. Các kết quả bên ngoài giải thích cơ chế/rủi ro, còn quyết định giữa B0/B1 phải dựa vào input và lỗi local. Không mua compute, cài thêm package hoặc thay pretrained/license trong task research này.

## 6. Hành động đã chốt và giới hạn tiếp tục

1. Ghi selection B0 theo ủy quyền mới; giữ nguyên variables/version/pins, B1 và N0 làm evidence đối chứng. Owner không phải tự chọn lại arm.
2. Không merge/sửa ID đã lưu để che lỗi T10. Không đổi role unknown hoặc loại người đang di chuyển bằng quy tắc vai trò tự suy.
3. Không dùng ID thô hiện tại để tính duration/risk/event history. Case 8 → 9 giây phải được xử lý và có kiểm chứng trước slice đó.
4. Hướng kỹ thuật tiếp theo đáng ưu tiên là kiểm chứng cadence detector/tracker dày hơn trong khi classifier có thể giữ 1 Hz, hoặc association có hỗ trợ appearance nếu motion vẫn thất bại. Đây là hướng thiết kế, chưa có run/config/quality approval mới và chưa được triển khai. Không bảo đảm tăng FPS tự sửa được lỗi.

Task nghiên cứu/chọn baseline hoàn tất. Nghiệm thu tracking end-to-end vẫn mở vì có lỗi cụ thể, không phải vì owner chưa biết chọn thuật toán. Không yêu cầu owner annotate từng ảnh. Literature review không thay ground truth; agent visual findings là evidence diagnostic với scope đã nêu.

## 7. Kiểm tra và bảo toàn

Kiểm checksums benchmark/gallery và exact input pins trước phân tích; kiểm tổng 894 + 209 + 11 + 48 = 1.162, projection về counts B0/B1, và agreement hai chiều. Không code production change, không ML suite/inference lại. Kiểm JSON/links/diff và repository structure theo scope tài liệu/metadata.

Media research và review giữ local owner-only đến **01/11/2026 15:55:06 Việt Nam**, không gia hạn. Source/settings/models/parent outputs bất biến. Script đọc và tạo board không download/upload clip. Snapshot research không ghi credentials hoặc đường dẫn source có tên riêng tư. Artifact hashes và audit coverage ở visual-audit.json; không gọi contact sheets là dataset release.
