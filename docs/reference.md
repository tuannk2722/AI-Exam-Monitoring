# Reference implementation và công cụ

Đối chiếu code/handoff đến 2026-10-11; cập nhật khi API, module hoặc giới hạn thực tế thay đổi, không thêm lịch sử task. Contract có thẩm quyền ở [system](system.md), [data](data.md), [training](training.md). Có module/schema không chứng minh pipeline đã nghiệm thu; tiến độ ở [status](status.md).

Hardware tham chiếu lịch sử: local i7-1255U, RAM 8/16 GB, Intel UHD; không bảo đảm hiệu năng, không thay environment của run/benchmark cụ thể. Chưa có benchmark chứng minh B tốt hơn A; lựa chọn B là decision kiến trúc, không là kết quả so sánh thực nghiệm.

## Module map

| Vị trí code | Trách nhiệm / giới hạn |
|---|---|
| `src/ai_exam_monitoring/data/` | Audit nguồn YOLO, overlay, similarity, codec `PilotRecord`, package và integrity; builder v7 historical có self-SHA pin |
| `src/ai_exam_monitoring/training/` | Config/approval, loader/freeze, RGB letterbox, frozen encoder/cache, head training/resume, metrics và evaluator |
| `src/ai_exam_monitoring/inference/` | Adapter generic đọc checkpoint có sẵn và xuất prediction theo taxonomy checkpoint; chưa lọc person hoặc suy luận classifier B |
| `src/ai_exam_monitoring/contracts/` | Dataclass producer/consumer dùng chung; không phụ thuộc web framework |
| `src/ai_exam_monitoring/common/` | Config/error/provenance và truy/khôi phục lịch sử theo SHA |
| `configs/` | Biến dataset/experiment có version; phân biệt proposal với config thực thi được duyệt theo training spec |



## Adapter và giới hạn integration

`Prediction` hiện biểu diễn một label/score/bbox. Adapter classifier B chưa có: khi nối hai score với person/crop/frame phải thiết kế producer/consumer tường minh và review nếu mở schema; không nhét dict tùy ý hoặc coi detection class ID là target order. `PilotRecord` là contract dataset riêng, được mô tả đầy đủ trong data spec.

Adapter hiện yêu cầu source/checkpoint tồn tại, output mới và FPS dương/hữu hạn trước predict; không tạo timestamp 0 để che metadata thiếu. JSONL mở đầu bằng metadata source/checkpoint SHA và FPS, tiếp theo là predictions. CLI confidence mặc định 0.25 là giá trị của adapter generic, không phải threshold hành vi hoặc risk được owner duyệt. Không có classifier video integration/session status persistence ở đường này.



<a id="training-code"></a>

## Trainer/evaluator hiện có

Recipe E001–E003 ở [baseline report](../artifacts/reports/baseline-review-20261011/README.md), không là default cho model mới. Biến nằm trong `configs/experiments/E001.yaml`/E002/E003 và smoke tương ứng. `ExperimentConfig` hiện từ chối keys thiếu/lạ, values unresolved/nonfinite, model/device/optimizer/loss/transform khác whitelist; chỉ hỗ trợ `resnet18_frozen_linear` CPU. Đổi tên YAML không triển khai fine-tune hoặc GPU.

Backbone chỉ load weights local đúng SHA; không tự download, random fallback hoặc đổi license. `best.pt` hiện chứa head/config/identity/epoch, không standalone backbone. Dùng lại model phải có đúng pretrained + preprocess/target order/threshold; model bundle tự chứa đủ backbone là việc chưa hoàn tất cho deployment/promotion.

`training/data.py::verify_dataset` kiểm payload checksum/inventory, manifest versions/scope/usage, manifest–ledger membership, inline freeze hoặc preservation pointer. V5 cần thêm approval/membership/group/proposal/parent evidence ở original paths; ba metadata dependencies đã khôi phục exact SHA trong task handoff 2026-10-11 và giữ trong Git. Loader v4/v5/v6 đã verify trực tiếp; thiếu file về sau vẫn phải restore đúng pin, không bỏ guard. `select_records` chỉ train/val, test cần explicit final-test access. Không glob toàn crops hoặc đưa review-only/U-U vào supervision.

Evaluator hiện yêu cầu run FINISHED, **code identity giống run**, resolved config và mọi artifact hash đúng; validation output mới dưới workspace outputs. Test cần protocol riêng pin một experiment/checkpoint/config/code/payload/threshold/best epoch. Guard hiện chưa quản lý holdout độc lập và use-once xuyên output, vì vậy không đủ để tự cấp quyền test mới.

Lệnh mẫu chỉ dùng với **config đã approved và output mới**, không phải lệnh yêu cầu chạy các run cũ lần nữa:

Trainer nhận `--config`, `--output`, `--workspace`; `--resume` chỉ cùng identity; `--interrupt-after` dành cho recovery drill được phép. Kiểm `--help`/source trước chạy, không tự smoke chỉ để thử CLI.

```powershell
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.training.train --config configs/experiments/<approved-id>.yaml --output outputs/<new-id> --workspace .
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.training.evaluate --run outputs/<new-id> --output outputs/<new-id>-val-evaluation --split val --workspace .
```

Giới hạn evaluator hiện hành: `code_identity` hash toàn Python package (UTF-8 LF), nên retire modules/đổi imports cũng đổi identity. Model run lịch sử cần exact source/commit và environment theo [operations](operations.md), không nới evaluator hoặc sửa hash cũ. Cải tiến cơ chế identity trong tương lai cần contract/version riêng và bảo toàn tái lập lịch sử.

<a id="data-tools"></a>

## Công cụ dữ liệu và cách tái dùng

### Đường thực thi cho expansion/release mới

Mỗi release mới cần task có mục tiêu/failure mode và parent version tường minh, rồi lập bảng inputs → công cụ → outputs → checks theo bảng sau. Không suy quyền tạo release từ số version kế tiếp hoặc chạy config lịch sử với tên mới. Các module/commit cụ thể trong bảng là mapping implementation để tái dùng, không khóa workflow vào một release.

| Bước | Công cụ / nơi tái dùng | Input → output và kiểm bắt buộc |
|---|---|---|
| Audit nguồn | Active `data.audit`, `data.validate_labels`, `data.overlay` | Snapshot đã pin → audit/overlay; kiểm decode, pairing, bbox, taxonomy; không tự repair raw |
| Fingerprints/triage | Active `image_similarity.difference_hash`, `nearest_by_split` | Image metadata → nearest candidates; kết quả chỉ là cờ review, không auto group |
| Shortlist/anchor/context | Git `ab34b32`, `pilot_selection.inventory_anchors/select_round_robin`, `pilot_source_candidates.context_proposal/build_candidates` | Source audit + scope/budget được duyệt → candidates có provenance; kiểm anchor/device attribution, không auto label |
| Targeted screening | Git `ab34b32`, `pilot_targeted_expansion.collect/build_screening` | Cached parent/evaluation fingerprints + source pins → screening; `validate_fingerprints` chặn thiếu evaluation evidence; không đọc test predictions |
| Batch review | Git `ab34b32`, `targeted_review_package.build/check_pairs` | Draft selection → crop/contact sheet/review metadata; code lịch sử có ID/bucket v7 cố định, chỉ dùng tham khảo hoặc chạy đúng phiên bản gốc |
| Owner groups | Git `ab34b32`, `pilot_owner_groups.import_group_decisions/ingest_owner_groups` | Explicit reviewed group decisions → records; không dùng proximity/filename để tự xác nhận independence |
| Canonical records | Active `pilot_schema.record_from_dict/read_records/validate_records` | Decisions có reviewer/scope/crop SHA → strict `PilotRecord`; U giữ mask 0, blockers ngoài supervision |
| Export | Active `pilot_package.build_pilot_package` | Records + source roots + crop inputs + selection + metadata + exact expected IDs → package mới; hàm không tự cấp approval hoặc chọn split |
| Nghiệm thu | Active `integrity.verify_payload`, schema, parent/evaluation comparisons và owner receipt của version mới | Exact inventory/checksums, coverage, delta, leakage, parent preservation → quyết định release; không sửa receipt cũ |

Các module lịch sử được xác định ở Git commit trên, không cam kết tất cả đều nằm trong ZIP. Dùng `git show ab34b32:src/ai_exam_monitoring/data/<module>.py` để đọc đúng file, xem imports trước tái dùng. Không import code trực tiếp từ archive trong production. Nếu cần chức năng cho version mới: chuyển phần tổng quát vào module theo trách nhiệm (`selection`, `review`, `groups` khi thực sự cần), truyền variables bằng config và đưa regression fixtures liên quan trở lại; bỏ hard-code ID/quota của v7 chỉ trong implementation mới. Không khôi phục cả cây công cụ chỉ để có nhiều CLI, không sao chép module thành `v8_r1/v8_r2`.

Exporter nhận `records`, `output_dir`, `source_roots`, `crop_inputs`, `selection_rows`, `metadata`, `expected_sample_ids`; schema và fixtures ở `tests/test_pilot_package.py` là mẫu thực thi. Output phải mới; source/crop SHA phải đúng review. Acceptance layer của release mới là công việc của task release, cần explicit approval/config, parent delta và test-preservation checks; exporter PASS chưa là owner acceptance. Builder `v7_release_acceptance` giữ vai trò lịch sử, không là acceptance layer chung.

Trước coding, TASK ghi bước dùng active API hoặc cần thích nghi, regression và outputs. Kết quả thuộc hồ sơ source/release/audit, không thêm vào spec; lifecycle theo development guide.

Generic CLI `python -m ai_exam_monitoring.data.audit` và `.overlay` bắt buộc `--dataset`, `--images`, `--labels`, `--source-names`; subtrees tồn tại dưới dataset root, không auto-detect. Layout `images/{split}` + `labels/{split}` có thể audit chung; layout `{split}/images` + `{split}/labels` audit từng split rồi đối chiếu duplicate riêng.

Pairing theo relative path bỏ extension, case-sensitive. Same stem khác thư mục là khác key; nhiều extension cùng key ambiguous, không overlay. Images JPG/JPEG/PNG/BMP/WEBP; label TXT trừ `classes.txt`/`README*.txt`. Names JSON ID→name hoặc YAML `names` mapping ID→name; không nhận list để tự gán ID. Không tự chuyển source IDs thành targets.

Audit schema v2 giữ input/layout/names, decode/resolution, missing/orphan/ambiguous, invalid files/lines, empty labels, class counts, normalized bbox stats, exact duplicate SHA và valid samples. Label file lỗi không đóng góp partial statistics; orphan hợp lệ có thể vào class count nhưng pixel stats chỉ dùng unique decoded pairs. Empty/missing annotation không xác nhận negative. Near duplicate/license/semantics/group acceptance cần QA riêng.

Overlay dùng `--output-dir`, `--limit` (font tùy chọn); lấy N valid pairs đầu theo path và ghi manifest/audit, không gọi là mẫu đại diện/phân tầng. Dùng tọa độ pixel gốc, không tự xoay EXIF hoặc repair annotation. Output ngoài nguồn/raw; overlay từ chối directory đã có nội dung. Exit 0 pass checks thực hiện, exit 1 lỗi cấu trúc/không xuất mẫu, exit 2 input/output/arguments không hợp lệ.
