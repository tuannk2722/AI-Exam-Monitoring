# CLEANUP-20261023 — Dọn workspace và commit V13

- Trạng thái: hoàn thành cleanup và checks; bàn giao qua commit chứa task này theo yêu cầu owner, không push.

## Yêu cầu và hiện trạng

Đã đọc index/status, storage, development và hồ sơ release V13; đối chiếu Git và dung lượng. Thay đổi chờ commit gồm diagnostics/review, audit và V13.

## Quyết định và inputs

Giữ V13 accepted: 1.304 crop, 1.119 train / 185 val / 0 test. Giữ releases/model được retention bảo vệ, nguồn và evidence độc nhất. Không đổi nhãn/split/pins. Dọn exact manifest sau kiểm SHA và dependencies; không coi DVC hardlink là dung lượng riêng.

## Outputs và vòng đời

Hồ sơ: artifacts/reports/cleanup-20261023/. Candidate crops trùng V13 được nghỉ lưu với locator khôi phục, metadata giữ nguyên. Cache công cụ tái tạo được. Archive và nguồn rebuild V13 giữ lại; scratch kiểm tra dọn sau dùng.

## Contract impact và checks

Không đổi contract do cleanup. Ruff PASS; 200 unit tests PASS; mypy PASS (48 files). Protected bytes trước/sau PASS (12.461 file); checker --require-git PASS trên workspace và clean staged checkout. Staged diff không có binary; giữ nguyên một trailing whitespace trong evidence owner batch 04.

## Checkpoint và bàn giao

Đã dọn 4.690 file, 1.118.246.110 bytes. Exact paths/restore và kết quả ở README, cleanup-manifest.json, cleanup-result.json, protected-before.json và handoff.json trong hồ sơ cleanup. Metadata/pins giữ nguyên; candidate crops và media E004 trong manifest cần restore trước khi dùng lại. Nguồn rebuild V13 và bàn audit mới nhất giữ lại. Bổ sung gitattributes bảo toàn bytes config/input đã pin; không train/upload. Scratch checkout đã dọn sau kiểm.
