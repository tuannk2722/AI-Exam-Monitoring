# E004 — Software readiness ngày 2026-10-12

Thực hiện I1–I8 theo [thiết kế đã duyệt](../../../configs/experiments/E004-freeze-proposal-20261011.md), tiếp nối [execution companion](../../../configs/experiments/E004-data-execution-20261011.md). Owner yêu cầu tiếp tục phần độc lập tới khi hoàn tất hoặc cần review/decision. Kiểm thử mới chỉ dùng synthetic images/models, không smoke/train/holdout inference trên dữ liệu thật.

## Implementation

| Hạng mục | Kết quả |
|---|---|
| I1 config/approval | `adaptation_config.py`: schema strict, exact owner/config/action approval, matched signature; legacy E001–E003 giữ semantics |
| I2 data/protocol | `adaptation_data.py`: strict package loader, exact record/order pins, usage/mask, whole-family evidence, train/development/holdout reservation leakage guards |
| I3 model | `adaptation_model.py`: local pinned ResNet18/shared head; frozen control hoặc layer4+head autograd; mọi BN eval, explicit optimizer parameter names |
| I4 objective/trainer | Global known-count normalization, uniform permutation/tail, recompute global epoch BCE, raw-min best riêng early-stop reference |
| I5 resume | Atomic epoch-boundary full model/optimizer/RNG/sampler/history; restart epoch chưa commit; config/code/runtime/checksum guards và cumulative wall-time budget |
| I6 bundle/evaluator | Full backbone+head bundle, fresh-process reload không cần pretrained/head gốc; metrics/predictions cùng order, constant từ train prevalence, code/config/runtime identity |
| I7 use-once | Exclusive creation và hash-chain receipt ở `outputs/holdout-access/<payload>.jsonl`; pending/failed/consumed chặn mọi output/model/protocol khác trong workspace; reserve trước mở model/crops |
| I8 uncertainty/benchmark | Whole-group bootstrap 5.000 lần/seed 42, denominator từng metric, slices support-aware; development benchmark B1/4 threads, warm-up 10/measured 500, decode+transform+forward trong timing, hash ngoài timing/startup riêng |

Source ở [training](../../../src/ai_exam_monitoring/training/), fixture [synthetic](../../../tests/fixtures/adaptation_fixture.py), tests [adaptation](../../../tests/test_training_adaptation.py) và [access](../../../tests/test_holdout_access.py). Candidate không có feature-cache path; legacy cache/loss giữ nguyên. CLI train/evaluate dispatch theo schema; `--benchmark` chỉ dành cho adaptation development.

## Validation và giới hạn

[Validation receipt](validation.json) ghi checks và file digests cuối cùng. Tests kiểm loss/gradient với U/tail, freeze/BN/head parity, deterministic resume, fresh-process reload, FPR/null/slices/bootstrap, concurrent use-once và timing boundaries; regression legacy chạy cùng toàn suite. Synthetic benchmark chỉ kiểm semantics, không chứng minh M6 PASS.

Full suite: 151 tests PASS trong workspace và 151 PASS trên source snapshot không media/model local. Final adaptation suite: 15 PASS; Ruff, strict Mypy (42 source files), compile và diff check PASS; 79 historical pins giữ nguyên, 95 local links hợp lệ. Snapshot checker ZIP mode PASS; `--require-git` trên index thật báo 23 required files chưa tracked (gồm các file từ task trước). Chưa stage theo yêu cầu bảo toàn workflow; đây chưa phải committed clean checkout.

Final evaluator yêu cầu protocol riêng đúng candidate/promotion identity và holdout đã reserve trước training; kiểm lại G3 support thực tế và overlap. Registry chỉ bảo vệ một workspace, không distributed/chống người sửa filesystem. Receipt partial/corrupt fail closed; không tự xóa/retry. Model reload yêu cầu original source/environment; không sửa hashes lịch sử để dùng evaluator mới.

Resume hỗ trợ interruption có receipt; kill cứng có thể còn RUNNING và cần recovery review riêng. Deadline kiểm ở ranh giới thao tác, không hard-kill kernel. RSS trên Windows là process peak có thể gồm startup; ngoài Windows báo current RSS, không claim peak. M1–M7 cần evidence/owner acceptance; không auto Selected từ FINISHED.

## Data và bàn giao

56 anchors accepted không chứng minh independence. Chưa có provenance mới; accepted independent groups/test support vẫn 0. Không tạo release mới hoặc train thật khi thiếu inputs. [Readiness cần quyết định](../../../configs/experiments/E004-execution-readiness-20261012.md) ghi evidence còn thiếu và compute đề xuất.

Giữ original review/proposals/receipts và pins của lần nghiệm thu trước. Không stage/commit/upload. Scratch synthetic media/checkpoints, source snapshot và caches dọn sau khi giữ validation metadata; inputs/accepted ledgers/reports được bảo toàn.
