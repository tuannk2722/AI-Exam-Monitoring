"""Final local audit checks and current-state pointers for this study."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent

task = """# E004-CROP-BUNDLE-AUDIT-20261014 — Audit toàn bộ crop/frame

- Trạng thái: audit hoàn tất; owner repository-owner; không delegation.
- Scope: user cung cấp 6 ZIP crop và ZIP frame gốc, xác nhận quyền sử dụng, yêu cầu giữ contract hiện tại. Anchor V7-OE-S061-A01 là người áo khoác xanh lá đậm.
- Inputs/version: 7 ZIP pin trong config E004-crop-bundle-audit-20261014; V9, E004 development, contract và helper ở dependency-pins.json. Đã đọc index/status/data/development/reference và coverage/RC1 liên quan.
- Constraints: raw/releases/pins cũ bất biến; nhãn ZIP provisional; không sửa accepted labels/splits, không train/test/upload/commit. Giữ thay đổi uncommitted từ targeted coverage trước.
- Kết quả: kiểm kỹ thuật 765 crop/212 frame; screening 765 crop trên 48 boards và đối chiếu 6 frame nguồn. Giữ đủ inventory, 32 track và 5 batch Draft. Chưa nghiệm thu nhãn/split.
- Outputs: artifacts/reports/E004-crop-bundle-audit-20261014; raw/interim và outputs cùng ID giữ local. Gallery/boards là evidence review đang dùng; không scratch mới cần dọn.
- Checks: 5 unit tests helper PASS; lint/type, links/pins/counts/diff/checker trong validation.json. Không stage để qua checker. Spec không đổi.
- Bước tiếp: chuẩn bị draft annotation/recrop, rà semantics/anchor và lineage; owner nghiệm thu batch/ngoại lệ trước release revision. Audit PASS không là training approval.
"""
(ROOT / ".codex/TASK.md").write_text(task, encoding="utf-8")
status = ROOT / "docs/status.md"
text = status.read_text(encoding="utf-8")
text = text.replace("gallery/factors Draft chờ owner review batch và ngoại lệ anchor V7-OE-S061-A01", "gallery/factors Draft chờ owner review batch; anchor V7-OE-S061-A01 đã được owner xác định là người áo khoác xanh lá đậm")
line = "- [Audit bộ crop/frame mới](../artifacts/reports/E004-crop-bundle-audit-20261014/README.md): kiểm kỹ thuật toàn bộ 765 crop/212 frame và screening đủ 765 crop; giữ contract hiện tại, giữ toàn bộ dữ liệu trong 5 batch review Draft. Cần draft annotation/recrop và kiểm lineage trước nghiệm thu membership/split; chưa release/train mới.\n\n"
if line not in text:
    text = text.replace("Model demo:", line + "Model demo:")
status.write_text(text, encoding="utf-8")
pins = json.loads((REPORT / "dependency-pins.json").read_text())
for path, expected in pins.items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
records = json.loads((ROOT / "data/interim" / REPORT.name / "records.json").read_text())
notes = json.loads((REPORT / "visual-screening.json").read_text(encoding="utf-8"))
assert len(records) == len(notes) == 765
assert {r["sample_id"] for r in records} == {r["sample_id"] for r in notes}
assert all(n["accepted_labels"] is None and n["assigned_split"] is None for n in notes)
assert len(list((ROOT / "outputs" / REPORT.name / "boards").glob("*.png"))) == 48
print("Dependency pins, 765 row join, 48 boards, no acceptance/split: PASS")
