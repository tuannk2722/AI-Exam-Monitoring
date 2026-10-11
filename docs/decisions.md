# Registry quyết định và phạm vi

Tóm tắt decision IDs từ hồ sơ đã có, chuyển khỏi system spec ngày 2026-10-11. Không approval mới. Contract Accepted được thể hiện trong spec; bảng này phân biệt scope lịch sử/proposal. Khi cần đổi quyết định, đọc original để lấy đầy đủ bối cảnh/lý do, không tự suy rationale từ implementation.

Original ADR ở Git `ab34b32:docs/decisions/<filename>`; tra tên bằng `git ls-tree -r --name-only ab34b32 -- docs/decisions`. Archive locator/restore theo [operations](operations.md). Approval run hiện có qua [configs index](../configs/experiments/README.md); proposal E004 dùng bản active được link bên dưới, YAML đã pin giữ nguyên.

| ID | Trạng thái / nội dung và phạm vi áp dụng | Nơi giữ nội dung |
|---|---|---|
| ADR-001 | Accepted: research/demo recorded, một camera, human review; ngoài scope identity/production | System §1, §5 |
| ADR-002 | Superseded phần formulation/normal bởi 011/012; không là lựa chọn A/B đang mở | System §1; Data semantics |
| ADR-003 | Accepted cho candidate SCB/RF; Discuss loại, nhãn nguồn không tự accepted | [Nghiên cứu nguồn](../artifacts/reports/data-research-20261011/README.md) |
| ADR-004 | Accepted local + Colab, canonical modules, checkpoint/resume/sync; CPU E001–E003 là ngoại lệ | System §5; Development môi trường |
| ADR-005 | Accepted Git metadata/DVC binary/Drive restricted; push đúng quyền trước publish remote pointer | Development storage |
| ADR-006 | Accepted config/run/Git/DVC/metrics canonical; W&B optional disabled, không tự host MLflow | Training provenance |
| ADR-007 | Accepted bỏ Django/Cloudinary prototype, hoãn web; stack local FastAPI/`Jinja2`/JS/SQLite | System §3, §5 |
| ADR-008 | Proposed ByteTrack, phải benchmark; chưa threshold/tracker Accepted | System FR-TRK-01 |
| ADR-009 | Proposed temporal events/risk framework, chưa numerical rules/formula | System FR-EVT/RSK |
| ADR-010 | Accepted privacy gate; retention cụ thể chưa được duyệt | System §5 |
| ADR-011 | Accepted person unit/phone attribution; review evidence, không nearest-device labels | Data semantics/QA |
| ADR-012 | Accepted B, multi-label, normal metadata, unknown mask; không tự dataset/model approval | Data schema; Training loss |
| ADR-013 | Accepted thiết kế reviewed-crop pilot/masked supervision/group gates; budget v1 không quota release mới | [Data workflow](data.md); [release history](../artifacts/reports/data-research-20261011/README.md) |
| ADR-014 | Approval lịch sử Accepted riêng E001 CPU frozen probe v4 và final protocol; không cấp quyền run mới | [Reports/approvals](../artifacts/reports/README.md) |
| ADR-015 | Approval lịch sử Accepted riêng E002 train expansion v5, bảo toàn val/test; không test mới/promotion | [Reports/approvals](../artifacts/reports/README.md) |
| ADR-016 | Approval lịch sử Accepted riêng E003 v6/protocol/CPU/smoke/resume; không holdout/promotion | [Reports/approvals](../artifacts/reports/README.md) |
| ADR-017 | Proposal; trạng thái và scope hiện hành duy trì ở hồ sơ E004 | [Training gates](../configs/experiments/E004-proposal.md#e004-promotion-gates) |
| ADR-018 | Accepted phone chỉ mobile; landline không positive, không relabel hàng loạt thiếu review | [Data semantics](data.md); corrections trong release report |



Quyết định quan trọng mới giữ ID/date/owner/scope, context, lựa chọn và rationale, consequences, approval locator. Có thể ghi trong hồ sơ proposal liên quan; chỉ tạo ADR riêng khi quyết định có phạm vi kiến trúc độc lập. Registry thêm locator và trạng thái, không chép lại toàn văn. Khi thay thế, ghi Superseded/by và phần bị thay; giữ original/pins, cập nhật contract Accepted tương ứng. Accepted lịch sử không cấp quyền run mới. Không tạo ADR cho bug fix hoặc đổi implementation giữ nguyên contract.
