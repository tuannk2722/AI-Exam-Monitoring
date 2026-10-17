"""Kiểm bundle và liên kết local sau khi tạo gallery; không đọc media V10."""

import hashlib
import json
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "artifacts/reports/frame-crop-audit-20261016"
DATA = ROOT / "data/interim/frame-crop-audit-20261016"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.paths.append(value)
            if key == "id":
                self.ids.append(value)


def verify():
    page = Links()
    page.feed((DATA / "index.html").read_text(encoding="utf-8"))
    assert len(page.ids) == len(set(page.ids))
    for link in page.paths:
        url = urlsplit(link)
        assert not url.scheme and not url.netloc, link
        if url.path:
            assert (DATA / unquote(url.path)).resolve().is_file(), link
        elif url.fragment:
            assert url.fragment in page.ids, link
    rows = json.loads((REPORT / "review-index.json").read_text(encoding="utf-8"))
    audit = json.loads((REPORT / "frame-audit.json").read_text(encoding="utf-8"))
    result = json.loads((REPORT / "validation.json").read_text(encoding="utf-8"))
    inv = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    assert len(audit) == len({r["frame_id"] for r in audit}) == 536
    selected = {cid for r in audit for cid in r["selected_candidate_ids"]}
    assert selected == {r["candidate_id"] for r in rows}
    assert result["selected_frames"] == sum(bool(r["selected_candidate_ids"]) for r in audit)
    exports = {p.relative_to(DATA).as_posix() for p in (DATA / "crops").rglob("*.png")}
    assert exports == {r["export_path"] for r in rows}
    for archive in inv["archives"]:
        path = Path("C:/Users/OS/Downloads") / archive["name"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == archive["sha256"]
    with zipfile.ZipFile(DATA / "crops-review.zip") as bundle:
        assert bundle.testzip() is None
        assert len(bundle.namelist()) == len(set(bundle.namelist()))
        assert {n for n in bundle.namelist() if n.endswith(".png")} == exports
        for row in rows:
            assert hashlib.sha256(bundle.read(row["export_path"])).hexdigest() == row["crop_sha256"]
    for source in REPORT.glob("*.py"):
        compile(source.read_text(encoding="utf-8"), str(source), "exec")
    status = {
        "status": "PASS",
        "html_local_references": len(page.paths),
        "html_unique_ids": len(page.ids),
        "selected_crops": len(rows),
        "frame_audit_records": len(audit),
        "archive_source_sha_unchanged": True,
        "crop_package_crc_and_exact_bytes": True,
        "export_folder_exact_membership": True,
        "worksheet_syntax": True,
        "package_sha256": hashlib.sha256((DATA / "crops-review.zip").read_bytes()).hexdigest(),
    }
    (REPORT / "delivery-validation.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(status, ensure_ascii=False))


if __name__ == "__main__":
    verify()
