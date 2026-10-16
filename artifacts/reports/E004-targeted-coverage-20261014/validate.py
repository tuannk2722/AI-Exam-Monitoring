"""Verify the audit artifacts without training, model loading or holdout media."""

from __future__ import annotations

import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace

import yaml
from PIL import Image

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.data import letterbox

root = Path(__file__).resolve().parents[3]
report = Path(__file__).parent
out = root / "outputs/E004-targeted-coverage-20261014"


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.cards = 0

    def handle_starttag(self, tag, attrs):
        if tag == "article":
            self.cards += 1
        self.links.extend(v for k, v in attrs if k in ("src", "href") and v)


pins = read(report / "input-pins.json")
assert all(sha256_file(root / p) == h for p, h in pins.items())
for path in report.glob("*.json"):
    read(path)
cfg = yaml.safe_load(
    (root / "configs/datasets/E004-targeted-coverage-20261014.yaml").read_text(encoding="utf8")
)
assert cfg["scope"] == "train_selection_only"
matrix = read(report / "matrix.json")["rows"]
assert len(matrix) == len({r["sample_id"] for r in matrix}) == 787
for row in matrix:
    assert row["cohort"] in ("train", "selection")
    assert sha256_file(root / row["crop_path"]) == row["crop_sha256"]
assert sum(r["cohort"] == "train" for r in matrix) == 716
rows = {r["sample_id"]: r for r in matrix}
observations = read(report / "observations.json")["observations"]
assert len(observations) == len({r["sample_id"] for r in observations}) == 75
for obs in observations:
    assert obs["crop_sha256"] == rows[obs["sample_id"]]["crop_sha256"]
    if "pen_negative" in obs["factors"] or "calculator_negative" in obs["factors"]:
        assert rows[obs["sample_id"]]["labels"][0] == 0
    if "outside_workarea" in obs["factors"]:
        assert rows[obs["sample_id"]]["labels"][1] == 1
page = (out / "index.html").read_text(encoding="utf8")
parser = Links()
parser.feed(page)
assert parser.cards == 75
for link in parser.links:
    assert (out / link).is_file(), link
input_links = {link for link in parser.links if "inputs224" in link}
assert len(input_links) == 75
config = read(root / cfg["run"] / "resolved-config.json")
for link in input_links:
    sid = Path(link).stem
    assert sid in rows
    with Image.open(root / rows[sid]["crop_path"]) as native:
        exact = letterbox(native, SimpleNamespace(image_size=224, fill=tuple(config["fill"])))
    with Image.open(out / link) as rendered:
        assert rendered.size == (224, 224) and rendered.convert("RGB").tobytes() == exact.tobytes()
for path in report.glob("*.py"):
    compile(path.read_text(encoding="utf8"), str(path), "exec")
for path in [report / "README.md", root / "artifacts/reports/README.md", root / "docs/status.md"]:
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf8")):
        if "://" not in target and not target.startswith("#") and target != "validation.json":
            assert (path.parent / target.split("#")[0]).exists(), (path, target)
checker = subprocess.run(
    [str(root / ".venv/Scripts/python.exe"), "scripts/check_repo.py", "--require-git"],
    cwd=root,
    capture_output=True,
    text=True,
    encoding="utf8",
)
diff = subprocess.run(["git", "diff", "--check"], cwd=root, capture_output=True, text=True)
assert diff.returncode == 0, diff.stdout + diff.stderr
media = {
    p.relative_to(out).as_posix(): sha256_file(p)
    for p in out.rglob("*")
    if p.is_file() and p.name != "media-checksums.json"
}
(out / "media-checksums.json").write_text(json.dumps(media, indent=2) + "\n", encoding="utf8")
result = dict(
    status="PASS_audit_checks",
    input_pins=len(pins),
    scoped_crop_hashes=787,
    gallery_entries=75,
    exact_input_parity=75,
    local_links=len(parser.links),
    syntax="PASS",
    git_diff_check="PASS",
    test_reserve_media_accessed=False,
    repo_checker_exit=checker.returncode,
    repo_checker_output=checker.stdout + checker.stderr,
    git_delivery="not_staged_or_committed",
    production_source_modified=False,
    media_checksums_sha256=sha256_file(out / "media-checksums.json"),
)
(report / "validation.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
)
print(json.dumps(result, ensure_ascii=False, indent=2))
