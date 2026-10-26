"""Audit all within-frame float box pairs; geometry never assigns person identity."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
from pathlib import Path

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import checksum_artifacts, write_json

from .detector_review import read_object
from .runtime_config import media_deadline


def overlap(a: list[float], b: list[float]) -> dict[str, float]:
    for box in (a, b):
        if (len(box) != 4 or any(not math.isfinite(v) for v in box)
                or box[0] >= box[2] or box[1] >= box[3]):
            raise DataContractError("Invalid float box")
    aa = (a[2] - a[0]) * (a[3] - a[1])
    bb = (b[2] - b[0]) * (b[3] - b[1])
    intersection = (max(0., min(a[2], b[2]) - max(a[0], b[0]))
                    * max(0., min(a[3], b[3]) - max(a[1], b[1])))
    return {"iou": intersection / (aa + bb - intersection),
            "intersection_over_smaller": intersection / min(aa, bb),
            "area_ratio": min(aa, bb) / max(aa, bb)}


def audit(config: Path, workspace: Path, output: Path) -> None:
    if output.exists() or not output.resolve().is_relative_to((workspace / "outputs").resolve()):
        raise DataContractError("Require new audit output under workspace outputs")
    raw = load_yaml(config)
    if raw.get("schema_version") != "pair-geometry-audit-v1":
        raise DataContractError("Unknown pair audit config")
    paths = {k: FilePin(**v).verify(workspace) for k, v in raw["pins"].items()}
    run = read_object(paths["run"])
    media_deadline(run)
    checks = read_object(paths["checksums"])
    if run["status"] != "completed" or any(
        checks.get(paths[k].name) != sha256_file(paths[k]) for k in ("run", "detections")
    ):
        raise DataContractError("Diagnostic evidence mismatch")
    owner = read_object(paths["owner_review"])
    accepted = {frozenset(r["anchors"]): r["relation"] for r in owner["relations"]
                if r["status"] == "owner_confirmed"}
    rows = [json.loads(line) for line in paths["detections"].read_text().splitlines()]
    frames = [r for r in rows if r["arm"] == raw["arm"]]
    cohort = read_object(paths["cohort"])
    if [f["frame_index"] for f in frames] != [f["frame_index"] for f in cohort["frames"]]:
        raise DataContractError("Frame cohort mismatch")
    pairs = []
    for frame in frames:
        for a, b in itertools.combinations(frame["boxes"], 2):
            ids = [f'f{frame["frame_index"]:08d}-{raw["arm"]}-{x["box_id"]}' for x in (a, b)]
            pairs.append({"frame_index": frame["frame_index"], "anchor_a": ids[0],
                          "anchor_b": ids[1], **overlap(a["xyxy_float"], b["xyxy_float"]),
                          "relation": accepted.get(frozenset(ids), "unknown")})
    if not accepted.keys() <= {frozenset((p["anchor_a"], p["anchor_b"])) for p in pairs}:
        raise DataContractError("Reviewed pair missing from audit")
    output.mkdir(parents=True, exist_ok=False)
    with (output / "pairs.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pairs[0]))
        writer.writeheader()
        writer.writerows(pairs)
    write_json(output / "audit.json", {"pins": raw["pins"], "frames": len(frames),
               "pairs": len(pairs), "positive_overlap": sum(p["iou"] > 0 for p in pairs),
               "reviewed_pairs": [p for p in pairs if p["relation"] != "unknown"],
               "media_delete_by": run["media_delete_by"], "suppression_applied": False})
    checksum_artifacts(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.config, args.workspace, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
