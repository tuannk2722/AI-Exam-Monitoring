# Hướng dẫn coding agent

## Bắt đầu và quyết định

- Đọc `docs/00-INDEX.md`, `docs/status.md` và `.codex/TASK.md`; đối chiếu Git/files/code trước sửa. Index định tuyến contract/reference/hồ sơ đúng task; không đọc cả archive hoặc mọi report.
- Spec giữ requirements/contracts, không giữ mọi kết quả task. Status chỉ hiện trạng; reports/source/release/run có version giữ evidence; proposal/config đúng ID giữ thiết kế/variables. Không lấy ID lớn nhất hoặc “next” của report lịch sử làm scope hiện hành.
- Owner approval đúng scope/version có hiệu lực; Draft/TBD không là approval. Registry `docs/decisions.md` dẫn tới quyết định; configs/receipts/pins và code là bằng chứng. Có conflict: báo rõ, không tự đổi labels/splits/metrics/scope hoặc sửa pins để qua gate.
- Tạo/cập nhật TASK trước sửa theo `docs/templates/task-template.md`: một task, inputs/version, constraints, progress/checks và bước tiếp. Không chứa media/credentials/danh tính, không thay approval hoặc làm WORKLOG.

## Thực hiện

- Đối chiếu gate theo hành động ở system/training: implementation, smoke, run, final test và nghiệm thu có scope riêng. Không train lại/smoke lại/mở downstream chỉ vì refactor/docs; phần độc lập được user yêu cầu vẫn tiếp tục.
- Không tự chốt class/formulation, sources/splits, pretrained/license, training variables, thresholds/metrics, risk/evidence/review hoặc test access. Thiếu decision: đề xuất owner/lý do/evidence/acceptance, hỏi đúng phần. Authorization đúng scope giữ qua turns/resume; không hỏi lại phần đã duyệt.
- Tự động shortlist/draft annotation/group/QA bằng công cụ hiện có; owner nghiệm thu batch và ngoại lệ, không phải annotate từng ảnh. Solo owner tự review, không yêu cầu người thứ hai.
- Logic tái dùng trong src; YAML chứa variables; notebook exploration/launcher; core không import web. Không fake predictions/metrics/model trong production. Kiểm conventions/imports và producer/consumer trước đổi.
- Công cụ/reuse ở `docs/reference.md`, restore ở `docs/operations.md`, lifecycle ở development. Không copy script theo v/r1/r2; chỉ thích nghi phần tái dùng có tests, TASK ghi output tạm/evidence giữ lại.

## Bảo toàn

- Retention hiện hành theo [chính sách lưu trữ](docs/storage.md), owner duyệt 16/10/2026: bảo vệ dataset/model/metadata hiện hành, không bắt buộc giữ mọi payload lịch sử. Tra availability trước restore; receipt/pins cũ không chứng minh bytes còn tồn tại. Không tạo lại dữ liệu hoặc sửa pins để lấp payload đã retire.

- Raw bất biến; derivative/version mới ở interim/processed. Không mutate/reseal accepted releases, config/receipt hoặc artifact đã pin (kể cả Draft đã được audit pin). Bất biến nghĩa là không sửa bytes/pins, không bắt buộc giữ payload vĩnh viễn. Nghỉ lưu chỉ theo scope/manifest đã duyệt; thiếu input xử lý theo chính sách retention, không bỏ integrity guards.
- Git không media/model/checkpoint/env/cache/credentials. Không real identity trong filenames/manifests; không upload người thật/W&B/API thiếu consent/use scope. DVC pointer không là remote backup; push chỉ scope được duyệt.
- Run có ID/hypothesis/owner/code/config/data/split/encoding/seed/environment/status/metrics/checksums/decision. Đổi variables tạo identity mới; OOM/interruption không silent đổi config. Unknown masked; test không tuning hoặc mở lại thiếu protocol/approval.
- Chỉ tái lập run/model cũ khi task cần và đủ input, bằng original code/pins/environment; không sửa hash cũ hoặc nới evaluator sau refactor. Restore workspace tạm dọn sau dùng.

## Bàn giao

- Inspect diff, chạy checks đúng scope theo development. Docs-only không full ML/data hashes; software PASS không thay data/model acceptance.
- **Không sửa spec nếu contract không đổi.** Results ở hồ sơ source/release/run trong artifacts/reports và outputs/data đúng loại; proposal ở configs; cập nhật index/status chỉ khi liên quan. Không append mọi task vào report tổng hợp hoặc status.
- Thay contract quan trọng cần decision đúng scope và traceability; giữ originals, quan hệ Superseded rõ. Không tạo card/ADR/report cho mọi chỉnh sửa nhỏ; dùng hồ sơ hiện có nếu chưa seal và đủ trách nhiệm.
- Khi user yêu cầu commit: stage đúng source/docs/config/metadata, checker `--require-git` kiểm index/registry, inspect staged diff và clean checkout khi đổi cấu trúc rộng; không force-add binary hoặc stage chỉ để checker PASS.
- Tài liệu tiếng Việt, đặc biết chú ý khi viết tài liệu phải dấu cách đầy đủ giữa các chữ/số với nhau; **dọn preview/cache/checkout/tooling sau bảo toàn inputs/evidence/results**. Backup cùng ổ không chống hỏng ổ.

Dừng phần liên quan khi data/license/path/version không rõ, label/split conflict, thiếu protocol test/config experiment hoặc có nguy cơ lộ data/credentials; tiếp tục phần độc lập.
