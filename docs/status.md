# Trạng thái dự án

Đối chiếu code và hồ sơ bàn giao đến **2026-11-07**. Chỉ giữ trạng thái hiện hành, thay nội dung khi tiến độ đổi; không append nhật ký/metrics/mọi task. Không là approval. [Index](00-INDEX.md) định tuyến contracts; [reports](../artifacts/reports/README.md) giữ lịch sử/evidence.

## Capability

| Phạm vi | Đã có / khoảng thiếu | Nơi kiểm |
|---|---|---|
| Data engineering | V15 local accepted theo ủy quyền: 1.721 crop sử dụng, 1.377 train / 344 val development / 0 test; dùng đủ 368 crop mới sau QA | [V15 release/pointers](../artifacts/reports/dataset-merge-20261106/README.md) |
| Baseline | E001–E003 FINISHED, Continue research; chưa model Selected | Reports → runs/baseline |
| Model improvement | E008 V14: 4 smoke + 5 research FINISHED; audit metadata PASS. G0 thắng, phone qua gate 3/3 seed G0; looking chưa đạt, chưa Selected. Đã nhận đủ best/last ba run G0 và kiểm integrity local | [Kết quả E008](../artifacts/reports/e008-v14-colab-20261024/results-20261025.md), [checkpoint](../artifacts/reports/e008-v14-colab-20261024/checkpoints-20261025.md) |
| Runtime | Đã có CLI recorded-video → person → context crop → G0, pins/rights guards và gallery QA; có full-frame và sampling 1/2 Hz; stage V8S + G0 trên clip hiện tại đã nghiệm thu, chưa nghiệm thu tổng quát | [Reference](reference.md), [system](system.md) |
| Tracking/events/risk/web | C10 và events đã được owner chấp nhận cho prototype trên clip hiện tại. Web Review local đã triển khai với light/dark và SQLite review riêng; risk chưa mở | [Tracking closeout](../artifacts/reports/tracking-cadence-20261027/closeout-20261027.md), [event acceptance](../artifacts/reports/events-prototype-20261027/acceptance-20261027.md), [scope web](../configs/web/README.md) |
| Tooling/storage | Sau E007 đã nghỉ lưu payload lịch sử và bản trùng: 8.971 files, 9,959 GiB logical; giữ V13/nguồn độc nhất, ba best D1 và ba best R0 cùng metadata | [Cleanup/availability 24/10](../artifacts/reports/cleanup-20261024/README.md), [chính sách](storage.md) |

## Ưu tiên hiện hành

Owner đã review batch ngày 05/11 và bổ sung crop có nhãn ngày 06/11/2026. Đã kiểm
368 crop mới, nhập quyết định exclude/relabel và đóng
[V15](../artifacts/reports/dataset-merge-20261106/README.md) theo ủy quyền hợp nhất/chia split.
Val mới có composition khác và gồm 197 crop train lịch sử chuyển sang theo nguyên nhóm;
chỉ là development; E009 đã khởi tạo mới từ pretrained theo recipe/protocol được duyệt riêng.
Owner đã approve [E009](../configs/experiments/E009-V15-20261106/README.md), trần 12 giờ GPU
private Colab/Drive; campaign đã hoàn tất 6 smoke + 25 research sau recovery 45 phút/run, giữ đồng hồ gốc. [Audit E009 ngày 07/11](../artifacts/reports/e009-v15-colab-20261106/results-20261107.md) xác nhận B0 đứng đầu, nhưng có finding score sát ngưỡng và hạn chế looking trên cohort old-train chuyển sang val. [Checkpoint audit](../artifacts/reports/e009-v15-colab-20261106/checkpoints-20261107.md) đã nhận đủ best/last ba run đại diện và kiểm integrity/cấu trúc local. Chưa Selected/promotion hoặc test; không tự train thêm hoặc thay G0. V14 và model prototype hiện hành giữ nguyên. Phần dưới giữ trạng thái
implementation runtime đã có, không là yêu cầu tiếp tục chạy trong task dữ liệu.

Owner chuyển đích demo sang **camera trực tiếp (có thể từ điện thoại) và video
upload đang phát có detection**, bbox trên hình + log review gọn. Thiết kế/bộ khung
theo [LIVE-DEMO-FOUNDATION-20261027](live-monitoring.md) đã được owner review và
approve ngày 28/10/2026; [approval](live-monitoring.md#approval-của-owner--28102026).
Owner tiếp tục yêu cầu refactor runtime và triển khai luồng video online.
Baseline Web Review đã commit `996c52c`; branch mới `feat/live-monitoring-demo`.
Đã refactor processor từng frame dùng chung và có runner video online nội bộ:
decode một lượt theo media clock, bounded pending/result, pause/seek/stop/EOF,
epoch reset và loại kết quả muộn; kiểm bằng fixtures và MP4 synthetic. Factory
giữ guards config/pins/receipt/deadline, CPU V8S/G0. Đã nối upload/UI/transport
theo [LIVE-VIDEO-WEB-20261028 được owner duyệt](../configs/web/LIVE-VIDEO-WEB-20261028/README.md):
màn hình giám sát light/dark tại `/`, MJPEG/SSE, điều khiển nguồn server và metadata
phiên riêng; `/review` giữ review offline. Chỉ observations tức thời, chưa temporal
log/review mới hoặc tracking/events online; chưa chạy model thật để đo online.
Owner đã review/chốt giao diện và logic slice web/video; baseline commit `2c9d8fa`.
Có adapter device/batch FP32, timings hữu hạn và CLI probe/profile độc lập theo
[LIVE-COMPUTE-20261028](../configs/runtime/LIVE-COMPUTE-20261028/README.md).
Web vẫn CPU; chưa có model parity trên CUDA hoặc config GPU được chọn. Owner chốt
tải demo dưới 15 người, 5–10 phút; mốc kiểm tải 14 người / 10 phút chưa là SLA.
Owner xác nhận dùng iPhone và laptop mượn đáp ứng trên mức sàn của project, ưu tiên
thiết kế ổn định; chưa có environment đo thực tế để chốt GPU config/SLA. Hướng
USB/Camo nếu máy Windows giữ nguyên, camera backend chưa kiểm. Transport và log revision đã được
duyệt; [numeric timing](../configs/tracking/LIVE-TIMING-20261028/README.md) tiếp tục
được owner duyệt cho implementation/fixtures. Có primitives chọn slot, reset continuity
và candidate tăng dần, chưa nối tracker thật hoặc lưu evidence/review online.
Receipt camera và persistence live cụ thể còn mở. Chưa có camera runtime
hoặc nghiệm thu hiệu năng/chất lượng live trên media thật. API và giới hạn runner
ở [reference](reference.md).

Owner đã chốt C10 prototype, miễn audit toàn clip và [chấp nhận kết quả events](../artifacts/reports/events-prototype-20261027/acceptance-20261027.md). Web Review local đã có sảnh phiên, bàn duyệt light/dark, SQLite review riêng, tổng kết và nhập/xuất. Owner duyệt áp dụng nguyên pipeline cho video mới có receipt riêng theo [scope web](../configs/web/README.md). Giữ giới hạn fragmentation/duplicate/classifier, không biến batch acceptance thành confirmed từng event hoặc metrics độc lập. Risk chưa mở; chưa nghiệm thu chất lượng end-to-end trên clip mới.

Owner đã duyệt [chuyển phase prototype](../artifacts/reports/e008-v14-colab-20261024/prototype-decision-20261025.md), dừng cải thiện classifier E008 và chọn G0 seed 20261023, giữ checkpoint/preprocessing/ngưỡng. 80/80/20 không còn chặn chuyển phase prototype; kết quả nghiên cứu và hạn chế support/validation giữ nguyên. [Đề xuất runtime](../configs/runtime/RUNTIME-PROTOTYPE-20261025/README.md) đã được owner duyệt detector/license/crop/output và implementation; config đã materialize. Owner yêu cầu dọn toàn bộ ba thử nghiệm video và hồ sơ riêng; không giữ các lượt đó làm backlog hoặc nghiệm thu. Giữ implementation/config prototype cho phase runtime tiếp theo; tình trạng dọn ghi ở [cleanup](../artifacts/reports/runtime-prototype-20261025/cleanup-20261025.md). [Bàn giao runtime](../artifacts/reports/runtime-prototype-20261025/README.md); chưa nghiệm thu chất lượng video.

Đối soát cleanup cũ theo [observation](../artifacts/reports/runtime-prototype-20261025/cleanup-observation-20261025.json); settings runtime đã được tạo lại cho lượt mới, không phục hồi thử nghiệm cũ. [QA partial](../artifacts/reports/runtime-clip-qa-20261025/README.md) giữ lượt full-frame đã dừng; [QA 1 Hz](../artifacts/reports/runtime-clip-qa-20261025/qa-1hz.md) hoàn tất 60 frame toàn clip, integrity PASS, batch 400 crops để review. Chưa nghiệm thu chất lượng.

## Stage runtime đã đóng

Owner đã nghiệm thu và đóng stage **V8S → context-v1 → G0** trên clip hiện tại, 1 Hz / 60 samples, theo [quyết định cuối](../artifacts/reports/runtime-clip-qa-20261025/stage-acceptance-20261026.json). [Bàn giao session](../artifacts/reports/runtime-clip-qa-20261025/v8s-session-20261026.md) và [runtime hiện hành](../configs/runtime/RUNTIME-V8S-20261026/README.md) giữ config/evidence. Các lỗi detector đã biết được chấp nhận trong scope prototype; mọi người diagnostic, role unknown. Không còn review hoặc run bắt buộc của stage này.

D2, pose và đối chứng V8S/V10S là hồ sơ lịch sử trong reports, không là backlog. Không suy stage acceptance thành ground truth từng crop, chất lượng video độc lập hoặc real-time SLA. Tracking và events đã chốt prototype theo approval riêng ở trên; Web Review mở theo scope riêng, risk chưa mở. Deadline media giữ 01/11/2026 15:55:06 Việt Nam.

Dataset chuẩn bị cho E009 là [V15 accepted theo ủy quyền](../artifacts/reports/dataset-merge-20261106/README.md): 1.377 train / 344 val development / 0 test. V14 vẫn là input lịch sử của E008 và model prototype; không sửa pins hoặc so trực tiếp metrics khác cohort. V13/E007 và lineage limitations được bảo toàn.

- [E006 V12](../artifacts/reports/e006-v12-20261020/README.md) hoàn tất; SQRT là recipe tham chiếu development, chưa đạt đồng thời cổng chất lượng cho cả hai target. Chưa model Selected. Các test cũ đã được mở visual audit trong scope V13; không phát sinh quyền inference/final-test mới.
- [E007 V13 Colab](../configs/experiments/E007-V13-20261024/README.md) hoàn tất 9 research run trên L4 trong khoảng 42 phút; artifacts cloud đã import và kiểm checksum/reload. D1 là hướng nghiên cứu chính, nhìn quanh là phần còn thiếu; chưa test/promotion. Ma trận đã dùng đủ số run được duyệt, không tự chạy thêm dù còn thời gian. [Evidence](../artifacts/reports/e007-v13-colab-20261024/README.md); proposal 23/10 giữ snapshot gốc.
- [E008 V14 Colab](../configs/experiments/E008-V14-LOOKING-20261024/README.md) đã hoàn tất trên A100: 4 smoke + 5 research, khoảng 37 phút. Audit metadata/checksums/predictions/calibration và reload evidence PASS. G0 thắng screening nên chỉ G0 được confirmation hai seed; không chạy thêm khi còn ngân sách. Looking vừa thiếu support (29 positive), vừa chưa đạt đồng thời precision/recall; Continue research, chưa Selected. Đã import đủ ba thư mục G0, kiểm SHA và cấu trúc sáu checkpoint best/last; [receipt](../artifacts/reports/e008-v14-colab-20261024/checkpoint-import-20261025.json). Không chạy inference mới; giữ campaign/recovery trên Drive. [Kết quả và lỗi bền vững](../artifacts/reports/e008-v14-colab-20261024/results-20261025.md) giữ evidence nghiên cứu; hướng review/cải thiện tiếp trong report không còn là backlog hiện hành sau quyết định chuyển phase. Không so trực tiếp E007/V13 hoặc hạ gate để công bố đạt.
- [Diagnostics V12](../artifacts/reports/e006-v12-diagnostics-20261021/README.md) và [audit](../artifacts/reports/v12-reconcile-20261022/README.md) giữ evidence. Các checkpoint candidate/quarantine cũ đã được thay bằng V13 accepted; không lấy chúng làm backlog.
- [Đối chứng erasing](../configs/experiments/E006-followup-20261021/README.md) chưa run approval. Không tự chuyển configs E005/E006 sang V13 hoặc train lại.
- [Cleanup ngày 23/10](../artifacts/reports/cleanup-20261023/README.md) ghi availability mới cho cache, candidate crops và bản làm việc E004 trùng archive. Giữ metadata/pins, archive, datasets/models và nguồn rebuild V13; [availability 16/10](../artifacts/reports/storage-retention-20261016/availability.json) áp dụng cho phần không được đợt mới cập nhật.
- [Cleanup sau E007 ngày 24/10](../artifacts/reports/cleanup-20261024/README.md) supersede availability cũ cho exact paths được nghỉ lưu. Không giả định checkpoint E001–E006, E007 last/smoke/nonchampion hoặc crops lịch sử còn tại working paths; metadata/pins giữ nguyên. Source và model best D1/R0 hiện hành được bảo toàn.
- Runtime/downstream theo [system gates](system.md#6-điều-kiện-chuyển-bước); G0 seed 20261023 đã được chọn riêng cho prototype theo ngoại lệ mới; chưa model demo Selected theo chất lượng nghiên cứu hoặc quality threshold/SLA toàn video Accepted. Phần độc lập được user yêu cầu vẫn tiếp tục.
