"""Verify the actual audit handoff, its coverage, local links and preserved pixels."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess

from deep_review import HERE, PACKAGE, ROOT
from package_review import REVIEW
from PIL import Image

from ai_exam_monitoring.common.provenance import sha256_file


def read(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def main() -> None:
    (HERE / "validation.json").write_text('{"status": "RUNNING"}\n', encoding="utf-8")
    cohort = read("cohort.json")
    decisions = read("decisions.json")
    summary = read("summary.json")
    assert len(cohort) == len(decisions) == 836
    assert {r["sample_id"] for r in cohort} == {r["sample_id"] for r in decisions}
    by_id = {r["sample_id"]: r for r in cohort}
    html = (REVIEW / "index.html").read_text(encoding="utf-8")
    script = re.search(r"<script>(.*?)</script>", html, re.S)[1]
    gallery = json.loads(re.search(r"const rows=(.*?);\nconst \$=", script, re.S)[1])
    assert len(gallery) == 836
    script_path = REVIEW / "gallery-check.js"
    script_path.write_text(script, encoding="utf-8")
    try:
        subprocess.run(["node", "--check", str(script_path)], check=True, cwd=ROOT)
    finally:
        script_path.unlink(missing_ok=True)
    for row in gallery:
        sid = row["sample_id"]
        assert row["status"] == "Draft"
        assert (REVIEW / row["native"]).resolve() == (
            PACKAGE / by_id[sid]["crop"]["crop_relpath"]
        ).resolve()
        assert (REVIEW / row["native"]).is_file()
        assert sha256_file(REVIEW / row["native"]) == row["crop_sha256"]
        with Image.open(REVIEW / "input" / f"{sid}.png") as image:
            assert image.size == (224, 224) and image.mode == "RGB"
            assert hashlib.sha256(image.tobytes()).hexdigest() == row["input_rgb_sha256"]
        assert (REVIEW / "source" / f"{sid}.jpg").is_file()
        for ref in [row["first_pass_evidence"], row["deep_evidence"], row["confirmation_evidence"]]:
            if ref:
                assert (REVIEW / "boards" / ref["board"]).is_file()
    for path, digest in read("input-pins.json")["files"].items():
        assert sha256_file(ROOT / path) == digest, path
    assert sum(summary["actions"].values()) == 836
    assert summary["kept_label_delta"] + summary["kept_no_label_delta"] == 707
    assert all(
        d["proposed_states"] != ["unknown", "unknown"] for d in decisions if d["action"] == "keep"
    )
    table_ids = [
        line.split("|")[1].strip()
        for line in (HERE / "DECISIONS.md").read_text(encoding="utf-8").splitlines()
        if line.startswith("| ") and line.split("|")[1].strip() in by_id
    ]
    assert len(table_ids) == 836 and set(table_ids) == set(by_id)
    media = sorted(p for p in REVIEW.rglob("*") if p.suffix in {".png", ".jpg"})
    checksums = "".join(
        f"{sha256_file(path)}  {path.relative_to(REVIEW).as_posix()}\n" for path in media
    )
    (HERE / "media-checksums.sha256").write_text(checksums, encoding="utf-8")
    checked_links = 0
    for path in HERE.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            assert (path.parent / target.split("#")[0]).is_file(), (path, target)
            checked_links += 1
    result = {
        "status": "PASS",
        "review_rows": len(decisions),
        "input_png_pixel_checks": 836,
        "native_crop_sha_checks": 836,
        "media_checksum_count": len(media),
        "local_markdown_links_checked": checked_links,
        "javascript_syntax": "PASS",
        "gallery_browser_render": (
            "Not exercised; links, embedded data, pixels and JS syntax checked"
        ),
        "accepted_input_pins_unchanged": True,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    (HERE / "validation.json").write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
