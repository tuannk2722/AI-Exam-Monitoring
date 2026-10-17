# DATASET-RELEASE-20261017 — Release dataset đã nghiệm thu

- Trạng thái: hoàn tất release, kiểm và cleanup; bàn giao bằng commit Git của task này. Owner đã yêu cầu release, cleanup và commit; không train hoặc test inference.

## Inputs và phạm vi

- Parent E004-c345-development-20261016 và đúng 270 crop đã nghiệm thu (98 + 172).
- Exact allocation được TRAIN-VAL-ACCEPTANCE-20261017 duyệt; không đổi nhãn, crop/geometry hoặc spec. Cách train còn chờ thiết kế mới từ owner.

## Outputs và vòng đời

- Dataset hiện hành: data/processed/pilot-b/pilot-b-20261017-v11; 1.185 train / 266 val / 11 test đóng; 332 review-only và 29 excluded giữ nguyên.
- Pointer, approval, checks và backup/cleanup receipts: artifacts/reports/dataset-release-20261017/README.md.
- Config release: configs/datasets/pilot-b-20261017-v11.json; không có training recipe.
- Backup local có DVC pointer và registry; đã restore đối chiếu đủ 2.906 file. Không upload.
- Đã dọn scratch restore/rebuild và cache theo exact inventory: 6.444 file, 947.564.014 bytes; accepted sources và parent giữ lại.

## Checks và bàn giao

- Codec/exporter, exact allocation, source/crop parity, loader, deterministic rebuild: PASS.
- Bảo toàn 1.553 records parent về nhãn/geometry/rights/source; test 11 giữ nội dung/nhóm, version metadata mới được attest riêng. Parent bytes không đổi.
- Không có group/source SHA/crop SHA cắt qua split; 36 unit tests đúng scope PASS, worksheet Ruff PASS.
- Stage đúng metadata/docs/config/pointer; checker với Git index và diff trước commit, checkout sạch sau commit. Kết quả thao tác Git tra lịch sử commit và bàn giao hội thoại.
- Bước tiếp theo chỉ theo thiết kế train mới của owner; không tự khởi chạy train, smoke hoặc test/holdout.
