# E004 V9 — Kết quả matched development

**Hai run FINISHED; khuyến nghị Continue research, chưa promotion/Selected.** Layer4 không cải thiện trên selection 71 dù diagnostic cũ tốt hơn. Final test và reserve 199 vẫn đóng. Đây là khuyến nghị từ development, không phải quyết định nghiệm thu model của owner.

## Phạm vi đã duyệt

[Owner approval](owner-execution-approval.json) chốt 716 train, 71 selection, diagnostic 49/comparator 48/added 35 và reserve 199; đã nghiệm thu family boundaries còn thiếu. Independence và thiếu hụt support được miễn; không tuyên bố các family độc lập. Selection có 10 boundaries, 45/71 crop thuộc CF-Q072. Diagnostic subsets chồng nhau, không cộng thành mẫu độc lập. [Membership](cohort-membership.json), [support](cohort-support.json), [family](family-enrollment.json).

Package experiment mới chuyển đúng 71 crop sang val, giữ V9 Accepted bất biến. Có 716 train/120 val/11 test cũ; test không được inference. [Package](experiment-package.json), [rebuild 1.191 files byte-exact](package-rebuild.json). [Protocol v2](../../../configs/experiments/E004-v9-execution-20261013/protocol.json) ghi waiver rõ; M4 INCONCLUSIVE. Không sửa nhãn, thresholds hay pins để qua gate.

## Kết quả chính

| Chỉ số trên selection 71 | Frozen control LP | Layer4 L4 |
|---|---:|---:|
| Epoch hoàn tất / best | 20 / 10 | 11 / 1 |
| Thời gian train | 1.679,97 giây | 1.146,33 giây |
| Macro masked BCE (thấp tốt) | 0,67785 | 0,70932 |
| Macro AP (cao tốt) | 0,57537 | 0,54123 |
| Phone precision / recall | 58,8% / 37,0% | 45,5% / 18,5% |
| Looking precision / recall | 60,0% / 32,1% | 33,3% / 7,1% |
| Phone / looking FPR | 21,2% / 15,8% | 18,2% / 10,5% |

Threshold giữ 0,5. Phone có 27 P/33 N/11 U; looking 28 P/38 N/5 U, unknown masked. Control bỏ sót 17 phone P và 19 looking P; layer4 bỏ sót 22 và 26. Layer4 giảm FP nhưng giảm mạnh recall. Constant train-prevalence BCE là 0,69739: control chỉ cải thiện khoảng 2,8%, layer4 kém hơn constant. Các giá trị development chưa đạt mục tiêu chất lượng M1–M3; không gọi đây là final-test gate result.

| Cohort diagnostic | LP BCE / macro AP | L4 BCE / macro AP |
|---|---:|---:|
| Val 49 | 0,62270 / 0,75955 | 0,57700 / 0,82472 |
| Comparator 48 | 0,63469 / 0,76302 | 0,58881 / 0,82555 |
| Added 35 | 0,70065 / 0,67659 | 0,63959 / 0,70896 |

Không chọn candidate theo diagnostic khi selection đã cho kết quả ngược lại. [Metrics đầy đủ](matched-results.json), [deltas](matched-deltas.json), [lỗi theo crop](development-errors.json), [lỗi theo family](development-group-errors.json). Phân tích family là diagnostic hậu nghiệm, không thay M4 slices đã thiếu enrollment. Bootstrap 5.000 lần theo quarantine family trong outputs chỉ là độ nhạy theo grouping; selection đã dùng chọn epoch và không có independence claim.

## Xác minh kỹ thuật

- [Software revision](software-revision-validation.json): 16 tests, Ruff/mypy PASS; giữ guards v1 và final-test guards.
- [Smoke pair](smoke-pair-acceptance.json): 2 epochs mỗi model, interrupt/resume, shared head/order và frozen prefix/BN PASS.
- [Matched preflight](matched-preflight.json), [run integrity](run-integrity.json): exact code/config/checksums, best epoch là minimum BCE, sampler khớp trên các epochs chung. Hai run kết thúc trong budget 50 epochs/8 giờ mỗi model.
- [Evaluation verification](evaluation-verification.json): reload predictions khớp hoàn toàn (max absolute delta 0) trên cả 4 development cohorts, masks/decisions/metrics khớp; checksums PASS.
- Benchmark CPU 4 threads, batch 1, 10 warmup + 500 lần decode/letterbox/normalize/forward: p95 LP 124,88 ms; L4 124,22 ms; peak RSS 551.059.456 bytes. Đạt giới hạn benchmark 200 ms/1 GiB ở scope này; không phải SLA toàn video. Startup riêng 2,96/3,38 giây.

Exact configs: [LP](../../../configs/experiments/E004-v9-execution-20261013/E004-V9-LP.yaml), [L4](../../../configs/experiments/E004-v9-execution-20261013/E004-V9-L4.yaml). Canonical checkpoints/history/predictions ở outputs/E004-V9-LP và outputs/E004-V9-L4; evaluations ở các thư mục cùng tên nối -development-evaluation. Code identity cdb20fb051b46d3a0a88cf422a004d490c4dc92b8d13a0a7e86bdaae1c842cfb; không dùng source khác để reseal run.

## Bàn giao và hướng tiếp

Đề xuất giữ cả hai model ở hướng nghiên cứu, không mở final test cho layer4 hiện tại. Trước run mới, cần một hypothesis/config identity mới dựa trên các false negatives và chênh lệch cohort; không tự tăng epochs, đổi threshold hoặc dùng reserve để tuning. Waiver support không miễn chất lượng model. Owner chưa nghiệm thu model Selected.

[Backup local và restore PASS](backup-receipt.json): 1.389 paths, restore 1.225 files byte-exact, DVC pointer đã đăng ký; chứa package, configs, source snapshot, pretrained và run/evaluation artifacts. Source cache rebuild gốc đã có trong archive V9 (locator ở báo cáo consolidation). Đã dọn scratch sau verify/restore; 1.616 source cache files đã đối chiếu SHA với archive V9. Backup cùng ổ chưa bảo vệ hỏng ổ; không upload hoặc commit.
