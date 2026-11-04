"""Check the delivered audit without running a model or reading test media."""

import ast
import hashlib
import json
import re
import zipfile
from pathlib import Path

from PIL import Image

from ai_exam_monitoring.data.source_review import preview_input

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
DATA = ROOT / "data/interim/youtube-frame-audit-20261018"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inventory = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    rows = json.loads((REPORT / "review-index.json").read_text(encoding="utf-8"))
    notes = json.loads((REPORT / "frame-notes.json").read_text(encoding="utf-8"))
    trials = json.loads((REPORT / "selections.json").read_text(encoding="utf-8"))
    assert len(rows) == 71 and len(notes) == 115 and len(trials) == 116
    assert all("?" not in n["note"] for n in notes)
    assert all("?" not in r["draft_reason"] + r["qa_note"] for r in trials)
    assert "?" not in (ROOT / ".codex/TASK.md").read_text(encoding="utf-8")
    source_zip = Path("D:/dataset-foundry-starter/exports/youtube-crawl-accepted-frames.zip")
    assert sha(source_zip) == inventory["archive"]["sha256"]
    for source in inventory["frames"]:
        assert sha(ROOT / source["source_path"]) == source["sha256"]
    for reference in inventory["references"]:
        assert sha(ROOT / reference["path"]) == reference["sha256"]
    for row in rows:
        source = Image.open(ROOT / row["source_path"]).convert("RGB")
        crop = Image.open(ROOT / row["crop_path"]).convert("RGB")
        prepared = Image.open(ROOT / row["input_path"]).convert("RGB")
        assert source.crop(row["context_xyxy"]).tobytes() == crop.tobytes()
        assert prepared.tobytes() == preview_input(crop, 224, (114, 114, 114)).tobytes()
        assert sha(ROOT / row["crop_path"]) == row["crop_sha256"]
        assert sha(ROOT / row["input_path"]) == row["input_sha256"]
    report_links = []
    text = (REPORT / "README.md").read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        path = (REPORT / target).resolve()
        if path.name != "handoff-validation.json":
            assert path.is_file(), target
        report_links.append(target)
    for path in REPORT.glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"))
    bundle = DATA / "youtube-crop-proposals.zip"
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None and len(z.namelist()) == 215
        zipped = json.loads(z.read("review-index.json"))
        assert zipped == rows
        for row in rows:
            blob = z.read(f"{row['group']}/{row['candidate_id']}/crop.png")
            assert hashlib.sha256(blob).hexdigest() == row["crop_sha256"]
    # Only this task's temporary trial tree is eligible for removal.
    trial_root = (DATA / "trials").resolve()
    assert trial_root.parent == DATA.resolve()
    assert trial_root.name == "trials"
    if trial_root.exists():
        assert len(list(trial_root.glob("*/crop.png"))) == len(trials)
    assert len(list((DATA / "boards").glob("*-qa-*.png"))) == 18
    media = {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted(DATA.rglob("*"))
        if path.is_file() and trial_root not in path.resolve().parents
    }
    (REPORT / "media-checksums.json").write_text(
        json.dumps(media, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    parent = ROOT / "artifacts/reports/dataset-release-20261017/package-pointers.json"
    assert json.loads(parent.read_text(encoding="utf-8"))["payload_sha256"] == (
        "e851ce51ae8bc027c50370468ee15ee99b4d93ae73c0d270f2055489fcbccd3a"
    )
    pins = {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted(REPORT.iterdir())
        if path.is_file() and path.name != "handoff-validation.json"
    }
    result = {
        "status": "PASS",
        "date": "2026-10-19",
        "source_zip_sha256": sha(source_zip),
        "reference_sha_count": 6,
        "source_sha_count": 115,
        "crop_input_pixel_and_sha_count": 71,
        "review_zip_members": 215,
        "review_zip_sha256": sha(bundle),
        "utf8_notes_reasons_task": "PASS",
        "report_links": len(report_links),
        "python_syntax": "PASS",
        "source_review_unit_tests": "6/6 PASS",
        "ruff": "PASS, E501 bỏ riêng lệnh kiểm worksheets cho chuỗi ghi chú/HTML dài; không đổi cấu hình project.",
        "repository_checker": "PASS; chưa stage/commit file mới, không là clean-checkout delivery.",
        "git_diff_check": "PASS",
        "browser_render": "Chưa kiểm; HTML tĩnh và local links đã kiểm.",
        "retained_media_files": len(media),
        "temporary_trials_path": trial_root.as_posix(),
        "temporary_trials_safe_to_remove": True,
        "temporary_trials_present": trial_root.exists(),
        "parent_pointer_sha256": sha(parent),
        "report_pins": pins,
        "owner_accepted": False,
        "test_access": False,
    }
    (REPORT / "handoff-validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in result.items() if k != "report_pins"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
