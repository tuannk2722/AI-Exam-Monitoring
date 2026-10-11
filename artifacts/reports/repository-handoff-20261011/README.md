# Bằng chứng bàn giao repository

Tóm tắt di chuyển từ development guide; không là một lượt kiểm mới. [Quy trình restore](../../../docs/operations.md), [reports index](../README.md).

## 1. Snapshot bàn giao lịch sử — 2026-10-11

Scope lịch sử: owner duyệt cleanup/handoff và backup tại gốc D; không thay scientific decisions hoặc cấp quyền experiment. Nội dung bàn giao đầy đủ ở Git `7d78c79:docs/development.md` §8; sửa whitespace lịch sử tiếp theo ở `a58e797`. Các kết quả dưới đây được giữ từ handoff, không chạy lại trong task refactor spec.

| Bằng chứng của snapshot | Kết quả và giới hạn |
|---|---|
| Kiểm ban đầu | 114 tests PASS (24 classifier; base mô phỏng 90 chạy/24 skipped); package v4–v7 qua checksum/codec, 42 run artifacts E001–E003 khớp, gồm ba best.pt |
| Kiểm bàn giao sau khắc phục | Clean staged checkout: 119 tests, Ruff/checker PASS; strict mypy 32 files PASS; import từ checkout sạch, không dựa dataset/model local |
| Preservation/restore | Ba metadata dependencies v5 restore exact SHA, loader v4/v5/v6 verify; 709 removed tracked paths truy được archive hoặc Git `ab34b32`; restore drill backup v7/E003 PASS, không inference |
| Code/process | Checker kiểm index/registry/pins và CRLF; xử lý type debt 41 lỗi/9 file; reference có mapping reuse, development/operations có lifecycle/restore. Không đổi recipe/model/dataset |
| Backup | `D:/ai-exam-monitoring-backup-20261011`: 1.917 file/2.778.275.362 bytes, copy riêng không hardlink, SHA khớp manifest; Git bundle được bổ sung sau commit theo hồ sơ handoff |

Backup trên cùng ổ D chỉ bảo vệ sửa/xóa nhầm, không chống hỏng ổ hoặc là remote backup. Receipt/inventory ở `backup-manifest.json` trong backup; source Git ở `repository.bundle`. Không suy snapshot này bao gồm release/run được tạo về sau. Original cleanup receipt `outputs/cleanup-20261010.json.gz` nằm trong archive theo docs/operations.md; byte-exact rebuild ở docs/operations.md là evidence của lượt trước, không chạy lại ở handoff.

Khôi phục snapshot này: verify SHA trong manifest trước copy, không overwrite khác content; source dùng `git clone D:/ai-exam-monitoring-backup-20261011/repository.bundle <new-workspace>`. Copy đúng subtrees `data/processed/pilot-b`, `outputs`, `archive` theo nhu cầu, kiểm checksum package/run; raw lịch sử tra inventory và `common.history restore`. `git bundle verify` không thay kiểm binary manifest. Kiểm availability thực tế trước restore; không hứa snapshot có toàn upstream raw.
