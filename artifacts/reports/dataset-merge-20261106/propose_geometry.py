"""Propose visible-person boxes with the existing pinned V8S, for visual QA only."""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.source_review import preview_input
from ai_exam_monitoring.inference.person import PersonDetector
from ai_exam_monitoring.inference.runtime_config import RuntimeConfig
from ai_exam_monitoring.common.config import load_yaml

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
SCRATCH = ROOT / "outputs/_scratch/dataset-merge-20261106"


def main():
    output = REPORT / "geometry-proposals.json"
    if output.exists():
        raise RuntimeError("Do not overwrite proposals")
    path = ROOT / "configs/runtime/RUNTIME-V8S-20261026/runtime.yaml"
    config = RuntimeConfig(load_yaml(path), ROOT)
    detector = PersonDetector(config)
    inv = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    proposals = []
    for row in inv["imports"]:
        with Image.open(ROOT / row["path"]) as source:
            im = source.convert("RGB")
        w, h = im.size
        assert sha256_file(ROOT / row["path"]) == row["sha256"]
        detections = detector.predict(im)
        rank = sorted(detections, key=lambda d: (
            (d.xyxy[2] - d.xyxy[0]) * (d.xyxy[3] - d.xyxy[1])
            * (1 if d.xyxy[0] <= w / 2 <= d.xyxy[2] else .2)), reverse=True)
        box = None
        if rank:
            x1, y1, x2, y2 = rank[0].xyxy
            box = [max(0, math.floor(x1)), max(0, math.floor(y1)),
                   min(w, math.ceil(x2)), min(h, math.ceil(y2))]
        proposals.append({"id": row["id"], "crop_sha256": row["sha256"],
                          "person_box": box, "size": [w, h],
                          "detections": [{"xyxy": list(d.xyxy), "confidence": d.confidence}
                                         for d in detections]})
        if len(proposals) % 24 == 0:
            print(f"geometry {len(proposals)}/252", flush=True)
    output.write_text(json.dumps({
        "status": "draft_visual_review_required", "weights": config.raw["pins"]["detector_weights"],
        "policy": config.raw["detector"], "rows": proposals,
    }, indent=2) + "\n", encoding="utf-8")
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 16)
    for start in range(0, len(proposals), 12):
        sheet = Image.new("RGB", (1408, 1176), "#eee")
        draw = ImageDraw.Draw(sheet)
        for i, proposal in enumerate(proposals[start:start + 12]):
            row = inv["imports"][start + i]
            with Image.open(ROOT / row["path"]) as image:
                im = image.convert("RGB")
            if proposal["person_box"]:
                ImageDraw.Draw(im).rectangle(proposal["person_box"], outline="#ff2020", width=max(2, im.width // 100))
            x, y = (i % 4) * 352, (i // 4) * 392
            sheet.paste(preview_input(im, 336, (124, 116, 104)), (x + 8, y))
            draw.text((x + 8, y + 340), row["id"] + " " + str(proposal["person_box"]), fill="black", font=font)
        sheet.save(SCRATCH / f"geometry-{start // 12 + 1:02d}.jpg", quality=95)


if __name__ == "__main__":
    main()
