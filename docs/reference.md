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

Schema matched-adaptation-v2 thêm provenance random/learned head và diagnostic epoch0/first-epoch steps cho research/smoke. Model chỉ nhận learned FC từ parent checkpoint đã pin, reset backbone/optimizer; diagnostic giữ RNG/modes và không đổi best epoch rule. CLI train/evaluate dispatch cả v1/v2, research v2 không có final-test scope. [E004-RC1 execution](../configs/experiments/E004-RC1-20261014/EXECUTION.md) dẫn tới variables/approval/checks, không là default recipe mới.

Recipe E001–E003 ở [baseline report](../artifacts/reports/baseline-review-20261011/README.md), không là default cho model mới. Biến nằm trong `configs/experiments/E001.yaml`/E002/E003 và smoke tương ứng. `ExperimentConfig` hiện từ chối keys thiếu/lạ, values unresolved/nonfinite, model/device/optimizer/loss/transform khác whitelist; chỉ hỗ trợ `resnet18_frozen_linear` CPU. Đổi tên YAML không triển khai fine-tune hoặc GPU.

Backbone chỉ load weights local đúng SHA; không tự download, random fallback hoặc đổi license. Legacy `best.pt` chứa head/config/identity/epoch và cần pretrained gốc. Schema `matched-adaptation-v1` thêm frozen matched control/layer4 CPU, full backbone+head bundle và atomic epoch-boundary resume; reload bundle không cần pretrained/head initialization bên ngoài. Code ở `adaptation_config/data/model/metrics/train/evaluate.py`; synthetic validation và giới hạn ở [E004 software evidence](../artifacts/reports/E004-software-readiness-20261012/README.md).

`training/data.py::verify_dataset` kiểm payload checksum/inventory, manifest versions/scope/usage, manifest–ledger membership, inline freeze hoặc preservation pointer. V5 cần thêm approval/membership/group/proposal/parent evidence ở original paths; ba metadata dependencies đã khôi phục exact SHA trong task handoff 2026-10-11 và giữ trong Git. Loader v4/v5/v6 đã verify trực tiếp; thiếu file về sau vẫn phải restore đúng pin, không bỏ guard. `select_records` chỉ train/val, test cần explicit final-test access. Không glob toàn crops hoặc đưa review-only/U-U vào supervision.

Evaluator yêu cầu run FINISHED, **code identity giống run**, resolved config và artifact hashes đúng; validation output mới dưới workspace outputs. Test cần protocol riêng pin candidate/checkpoint/config/code/payload/threshold. Legacy guard không có use-once xuyên output. Adaptation evaluator thêm separate holdout package, exact pre-training reservation và `holdout_access.py` keyed payload; reserve trước model/crops, pending/failed/consumed chặn repeat trong cùng workspace. Guard không tự cấp quyền test.

Lệnh mẫu chỉ dùng với **config đã approved và output mới**, không phải lệnh yêu cầu chạy các run cũ lần nữa:

Trainer nhận `--config`, `--output`, `--workspace`; `--resume` chỉ cùng identity; `--interrupt-after` dành cho recovery drill được phép. Kiểm `--help`/source trước chạy, không tự smoke chỉ để thử CLI.

Adaptation evaluator nhận thêm `--benchmark` trên `--split val`: B1/4 threads, warm-up 10/measured 500, decode+transform+forward; không benchmark holdout. Config/protocol/readiness/approval cần exact pins, xem [readiness E004](../configs/experiments/E004-execution-readiness-20261012.md). Head snapshot dùng `adaptation_model.create_initial_head(path, seed)` ở path mới, cùng file pin cho matched pair.

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
| Pinned ZIP inspection | Active `source_review.PinnedYoloZip/fingerprint/diverse_inspection`, `scripts/prepare_source_review.py` | ZIP/config/source-audit/parent manifest pins → inventory/quarantine/inspection boards; source classes chỉ hints, whole-file YOLO reject, scene rank không là independence proof |
| Pending crop/input review | Active `source_review.write_pending_crop/preview_input`, `scripts/build_source_review_batch.py` | Explicit geometry + exact source/geometry pins → source/native crop/input 224 và proposal null/mask 0; review-only, không tự label/split/accept; pixel parity với training letterbox có test |
| Nhập nghiệm thu crop | Active `review_acceptance.accept_reviews`, `scripts/import_crop_review.py` | Pending ledger strict + owner decisions/pins → ledger mới đã có nhãn/geometry accepted; vẫn review-only/split null, không suy group/context/role/release approval; không overwrite |
| Graph quarantine nguồn | Active `source_lineage.lineage_components` | Inventory + source assessments + non-test parent fingerprints → exact-byte/export-lineage/reviewed-scene components và role conflicts; unknown IDs giữ null, không chứng minh independence |
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

Hai source-review CLI phục vụ preparation đã được giao, không đọc test media hoặc chạy model. `prepare_source_review.py --config <authorized-preparation.yaml> --workspace .` cần output mới trong `data/interim`; adapter này đọc source blobs non-test từ archive history đã pin. `build_source_review_batch.py --config <same.yaml> --geometry <draft.json> --geometry-sha256 <exact SHA> --output data/interim/<new-batch> --workspace .` nhận manual/draft geometry, từ chối overwrite. Annotation/ROI draft không trở thành PilotRecord supervision; owner decision phải qua codec/exporter khi đủ data acceptance. Dùng `--help` trước chạy config version mới, không rebuild lên evidence đã được pin/Accepted.

`import_crop_review.py --ledger <pending.jsonl> --ledger-sha256 <SHA> --decisions <owner-decisions.json> --decisions-sha256 <SHA> --output data/interim/<new-output> --workspace .` kiểm đủ batch membership, order/scope và source/crop/input hashes trước ghi ledger/receipt mới. Dùng codec `read_records/write_records`, chỉ nhận pending review-only records; crop acceptance không cấp quyền train/val/test. Input ledger pin giữ geometry, decision pin giữ lời duyệt; không dùng hash thay owner approval thực tế. Work context chưa duyệt vẫn unknown dù cả hai target N.

Generic CLI `python -m ai_exam_monitoring.data.audit` và `.overlay` bắt buộc `--dataset`, `--images`, `--labels`, `--source-names`; subtrees tồn tại dưới dataset root, không auto-detect. Layout `images/{split}` + `labels/{split}` có thể audit chung; layout `{split}/images` + `{split}/labels` audit từng split rồi đối chiếu duplicate riêng.

Pairing theo relative path bỏ extension, case-sensitive. Same stem khác thư mục là khác key; nhiều extension cùng key ambiguous, không overlay. Images JPG/JPEG/PNG/BMP/WEBP; label TXT trừ `classes.txt`/`README*.txt`. Names JSON ID→name hoặc YAML `names` mapping ID→name; không nhận list để tự gán ID. Không tự chuyển source IDs thành targets.

Audit schema v2 giữ input/layout/names, decode/resolution, missing/orphan/ambiguous, invalid files/lines, empty labels, class counts, normalized bbox stats, exact duplicate SHA và valid samples. Label file lỗi không đóng góp partial statistics; orphan hợp lệ có thể vào class count nhưng pixel stats chỉ dùng unique decoded pairs. Empty/missing annotation không xác nhận negative. Near duplicate/license/semantics/group acceptance cần QA riêng.

Overlay dùng `--output-dir`, `--limit` (font tùy chọn); lấy N valid pairs đầu theo path và ghi manifest/audit, không gọi là mẫu đại diện/phân tầng. Dùng tọa độ pixel gốc, không tự xoay EXIF hoặc repair annotation. Output ngoài nguồn/raw; overlay từ chối directory đã có nội dung. Exit 0 pass checks thực hiện, exit 1 lỗi cấu trúc/không xuất mẫu, exit 2 input/output/arguments không hợp lệ.
