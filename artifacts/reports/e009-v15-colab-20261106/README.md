# E009 V15 — Kết quả và hồ sơ bàn giao

**Campaign FINISHED: 6 smoke + 25 research run trên A100 80 GB.** [Kết quả audit ngày 07/11](results-20261107.md) và [receipt metadata](results-audit-20261107.json) xác nhận thứ hạng B0 → B448 → C0, nhưng có findings về score sát ngưỡng và hạn chế looking theo cohort. [Audit checkpoint local](checkpoints-20261107.md) đã nhận đủ ba run đại diện, 48 files và cả sáu best/last PASS integrity/cấu trúc. Chưa Selected hoặc thay model prototype; không còn thiếu download trong phạm vi ba run.

Notebook/bundle bên dưới giữ cơ chế đã dùng để tái lập; **không Run all lại campaign FINISHED**. [Authorization recovery](../../../configs/experiments/E009-V15-20261106/recovery-authorization-20261107.json) đã cho phép cap 45 phút/run, giữ tổng 12 giờ/pool research 500 phút và timestamp gốc, xác minh lại sáu smoke không train lại. Proposal/design/bundle/source tạo checkpoints giữ nguyên. Phần implementation/software evidence bên dưới là hồ sơ bàn giao trước run; kết quả model chỉ đọc ở report audit phía trên.

Đã sửa lỗi bootstrap của lần recovery 02:40–02:42: proxy `subprocess` thiếu `STDOUT`, làm dừng trước nvidia-smi/venv setup, chưa tiến thêm research. Proxy hiện giữ đầy đủ API; output con được stream vào cell để hiện traceback gốc. Đã tái hiện lỗi và kiểm lại bootstrap qua launcher gốc không GPU; không đổi extension/authorization/model/bundle hoặc ngân sách đã duyệt.

| File dùng tiếp | Vai trò |
|---|---|
| [Checkpoint audit](checkpoints-20261107.md), [receipt](checkpoint-import-20261107.json) | SHA/structure best/last B0, B448, C0 đã nhập local; không inference hoặc promotion |
| [E009-V15-Colab.ipynb](../../../notebooks/E009-V15-Colab.ipynb) | Notebook mỏng, một code cell; mount Drive, verify archive, gọi launcher và unassign |
| [e009-colab-execution-bundle.zip](../../../outputs/E009-V15-Colab-20261106/e009-colab-execution-bundle.zip) | Input hiện hành, 1.273.068.741 bytes, 1.854 members đã verify; upload vào My Drive/E009, giữ nguyên tên/private |
| [Handoff/pins ban đầu](handoff.json) | SHA notebook/archive/code/design và source checkout ở thời điểm bàn giao; trạng thái cloud trong snapshot không thay kết quả audit |
| [Software checks](software-checks.json) | Checks cuối cùng và giới hạn Git index |
| [Portable preflight](portable-preflight.json) | Verify từ ZIP extract trong workspace riêng, import source riêng và kiểm loader/approval/gates |

Execution bundle SHA256: `8125a39ba893624730193a219a4b3ab340592eb66e2f687f3bc1b55b3f7b95b1`.

Owner đã tự upload/chạy; agent hỗ trợ sửa notebook và đọc metadata qua Chrome theo yêu cầu. Cơ chế đã dùng: kernel 3.13 mount Drive, uv 0.9.7 cài CPython 3.12.12 riêng cho launcher/train; không giả `sys.version_info`. Setup/recovery giữ journal và timestamp gốc. ZIP input/metadata/model trên Drive giữ private; chưa có quyền test/promotion hoặc thay runtime model.

## Implementation đã kiểm

- Schema `dinov2-adaptation-v6`: S/B, global CLS + mean patch, suffix hai/bốn block và final norm; prefix/tokenization frozen no-grad. V1–V5 giữ behavior/guards, model prototype hiện hành không đổi.
- Preparer dùng exact V15: 1.377 train / 344 val / 0 test, đúng masks/rights/group/pins; sidecars chỉ ánh xạ metadata, không sửa package. Hai screening seed; top hai recipe + C0 được xác nhận đủ năm seed, dedup control và cap 25/19 research run.
- Runner chọn profile từ VRAM trước score; six-run full/interruption/resume smoke, shape/finite/gradient/VRAM/time/reload gates. Không có CPU fallback hoặc đổi biến ngầm khi OOM/budget fail.
- Incremental sync verify hash; giữ phiên bản trước của file thay đổi để manifest đã commit vẫn recover được khi ngắt giữa publication. Epoch snapshot atomic, continuation kiểm config/code/GPU/runtime, giữ timestamp/cap gốc và không chạy lại run FINISHED đã verify.
- Báo từng seed/mean/sample SD, fixed/calibrated threshold, paired group bootstrap giữ threshold và nhóm chung; checkpoint handoff có SHA best/config/calibration/bundle của một seed đại diện cho cả hai target. Không tự test, refit train+val hoặc thay runtime model.

## Evidence local

| Check | Kết quả |
|---|---|
| Full suite | 399 tests, OK; 2 browser opt-in skipped |
| Ruff `src tests scripts` | PASS |
| Strict Mypy source + checker | PASS, 96 source files |
| Official DINO S/B | Strict pretrained load; exact upstream features 336/448, frozen/trainable gradients trên tensor tổng hợp CPU PASS |
| C0 V5/V6 | Exact logits và optimizer update parity trong fixture; schema, four-block resume và standalone reload PASS |
| Campaign/recovery | Hai-seed → finalists/năm-seed queue, run caps, fixed thresholds, copy/restore/tamper và interrupted-publication recovery PASS |
| Bootstrap | Nạp trực tiếp từ ZIP không cần ML trong host; allowlist/path/SHA/divergent overwrite và metadata export guards PASS |
| Portable ZIP | Tất cả 1.854 member SHA khớp; extracted source identity đúng; hai profile loader 1.377/344 và research bị chặn khi chưa có actual smoke |
| GPU smoke/research/model quality | Đã hoàn tất 6 smoke + 25 research; audit metadata có findings, xem report ngày 07/11; chưa checkpoint acceptance/promotion |

[Official model checks](official-model-checks.json), [local input preflight ban đầu](local-preflight.json) và portable receipt phân biệt source snapshots đã kiểm; portable receipt dùng đúng code SHA của bundle cuối. Software PASS không thay nghiệm thu dữ liệu/model hoặc chứng minh kết quả trên holdout độc lập.

Tại thời điểm bàn giao ban đầu, `check_repo.py --require-git` trên index thật báo 19 delivery files mới chưa tracked. Chưa có yêu cầu stage/commit; không stage chỉ để PASS. Source được giao bằng exact private bundle, Git baseline `79c04ce` và dirty source snapshot trong manifest; đây không phải clean Git checkout hoặc CI từ xa.

## Bảo toàn và correction

[Execution design](../../../configs/experiments/E009-V15-20261106/execution-design.json) supersede design ban đầu **chỉ ở sidecar origin tags**: 26 crop parent val đã chuyển sang train được sửa thành `old_val_moved_to_train`. [Receipt đối soát](sidecar-revision.json) giữ originals và thay đổi; train origins là 1.002 old-train kept / 26 old-val moved / 349 new; val là 197 old-train moved / 128 old-val kept / 19 new native S03. Nhãn, split, nhóm và bytes V15 không đổi.

Archive ban đầu `e009-colab-bundle.zip` chưa upload, giữ local như snapshot đã superseded; notebook chỉ nhận **execution bundle** có SHA ở trên. Không reseal archive/design/receipt cũ để che correction. [Pretrained B receipt](pretrained.json) pin official weights, source revision và Apache-2.0 basis; không dùng E008 checkpoint đã thấy val mới.

Hai workspace preflight tạm và toàn bộ synthetic fixtures đã được dọn sau khi giữ receipts; DINO source cache/weights và dataset/model hiện hành được giữ làm dependencies. Raw/source galleries/pins V15/E007/E008 không sửa. Bàn giao ban đầu chưa commit hoặc push.

## Cleanup và Git ngày 07/11/2026

Theo yêu cầu owner, gom implementation, notebook, configs và hồ sơ audit E009 vào một commit trước khi tích hợp web. Không còn scratch E009 cần giữ trong `outputs/_scratch`; không đưa media/model/ZIP/env/cache vào Git. Source package vẫn có identity `68802787f7ee3d892073ff46e6657d45f0d74d283fab5a8ad3582f0795876c29`, đúng snapshot đã train; không refactor hoặc sửa trainer lịch sử sau audit. Ruff và strict Mypy PASS; 9 recovery tests PASS. Full suite 399 tests của snapshot này đã có evidence ở trên, không chạy lại training/smoke để cleanup. Quyết định dùng model trên web được ghi riêng sau commit này, không hồi tố thành quyền trong authorization training ban đầu.
