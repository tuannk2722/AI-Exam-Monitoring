# DOC-BOUNDARIES-20261011 — Tách contract, trạng thái và hồ sơ

- Trạng thái: hoàn thành; owner: chủ repository; không delegation.

## Yêu cầu và quyết định
Owner duyệt tổ chức lại tài liệu: spec giữ requirements/contracts; research/results/proposal về đúng hồ sơ; agent tra theo task. Không đổi scientific scope, recipe, labels/splits, quyền train/test/promotion hoặc upload. Giữ thay đổi working tree trước task.

## Đã đọc và inputs
AGENTS/index/TASK/Git/checker, bốn tài liệu cũ, templates/CI, card/pointer/report v7, E003 run/summary, audit E004, archive registry và original Git locators. Proposal YAML E004 đã pin dù Draft nên giữ bytes.

## Outputs và contract impact
System/data/training còn contract; development là guide. Docs status/reference/operations/decisions có vai trò riêng. Reports index dẫn tới releases/runs/originals; ba bản tổng hợp data/baseline/handoff di chuyển khỏi spec là snapshot lịch sử, không append task tương lai. E004 proposal cạnh configs, YAML/approval gốc không đổi. AGENTS/README/index/TASK/issue/PR templates định tuyến đọc/ghi và cho phép không sửa spec khi contract không đổi.

## Checks thực hiện
PASS: 105 config/report/approval có sẵn giữ SHA trước/sau; card v7 khớp pin; 16 bảng data/training cùng entity table và FR IDs được bảo toàn; 132 Markdown links/anchors hợp lệ và tài liệu mới đều reachable từ index; issue YAML parse; original research Git locators tồn tại. Inspect diff và git diff --check PASS.
Checker --require-git PASS (0 failures) trong delivery snapshot Git độc lập 209 files không cần binary data/model; staged whitespace PASS sau dùng core.autocrlf=true giống repo thật. Index thật giữ nguyên, chưa stage/commit; strict checker với index thật vẫn yêu cầu stage các file mới khi owner yêu cầu commit. Không chạy ML suite/train/inference hoặc full media hashing vì docs/templates-only.

## Vòng đời và bàn giao
Script/bản trước task/checkouts kiểm ở outputs/_scratch/doc-boundaries là tạm; kết quả giữ trong checkpoint này, nội dung chuyển nằm ở canonical docs/reports/proposal và originals vẫn nguyên. Dọn toàn scratch sau verification; không tạo thêm report cho chính task tổ chức docs. Task mới thay TASK này, bắt đầu từ docs/00-INDEX.md và docs/status.md; không kế thừa quyền scientific từ task docs.
