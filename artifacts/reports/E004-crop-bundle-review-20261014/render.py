"""Render study proposals; source pixels are immutable and every crop is pinned."""

import hashlib
import json
from pathlib import Path

import yaml
from PIL import Image, ImageDraw

from ai_exam_monitoring.data.source_review import preview_input

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "outputs" / HERE.name
DATA = ROOT / "data/interim" / HERE.name
OLD = "E004-crop-bundle-audit-20261014"
config = yaml.safe_load(
    (ROOT / "configs/datasets" / f"{HERE.name}.yaml").read_text(encoding="utf-8")
)
records = {
    r["sample_id"]: r
    for r in json.loads((ROOT / "data/interim" / OLD / "records.json").read_text())
}
geo = json.loads((HERE / "geometry-proposals.json").read_text(encoding="utf-8"))
for folder in [DATA / "crops", OUT / "inputs", OUT / "recrop-boards"]:
    folder.mkdir(parents=True, exist_ok=True)
rows = []
for cid, proposal in geo.items():
    base = records[proposal.get("original_id", proposal.get("source_crop_id"))]
    source = ROOT / base["local_source"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == base["source_sha256"]
    im = Image.open(source).convert("RGB")
    x1, y1, x2, y2 = proposal["context_xyxy"]
    assert 0 <= x1 < x2 <= im.width and 0 <= y1 < y2 <= im.height
    crop = im.crop((x1, y1, x2, y2))
    dest = DATA / "crops" / f"{cid}.png"
    crop.save(dest)
    inp = preview_input(crop, config["preview"]["size"], tuple(config["preview"]["fill"]))
    ip = OUT / "inputs" / f"{cid}.png"
    inp.save(ip)
    rows.append(
        {
            **proposal,
            "candidate_id": cid,
            "source": base["local_source"],
            "source_sha256": base["source_sha256"],
            "parent_id": base["supplied"]["parent_id"],
            "anchor_id": proposal.get("new_anchor_id", base["supplied"]["anchor_id"]),
            "crop": dest.relative_to(ROOT).as_posix(),
            "input": ip.relative_to(ROOT).as_posix(),
            "crop_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
            "input_sha256": hashlib.sha256(ip.read_bytes()).hexdigest(),
            "status": "draft_pending_owner",
            "split": None,
            "training_ready": False,
        }
    )
for offset in range(0, len(rows), 12):
    board = Image.new("RGB", (960, 816), "white")
    draw = ImageDraw.Draw(board)
    for j, row in enumerate(rows[offset : offset + 12]):
        x, y = j % 4 * 240, j // 4 * 272
        draw.text((x + 3, y + 3), row["candidate_id"] + " " + row["draft_labels"], fill="black")
        board.paste(Image.open(ROOT / row["input"]), (x, y + 40))
        row["board"] = f"recrop-boards/{offset // 12 + 1:02}.png"
    board.save(OUT / f"recrop-boards/{offset // 12 + 1:02}.png")
(HERE / "derivatives.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({"derivatives": len(rows), "boards": (len(rows) + 11) // 12}))
