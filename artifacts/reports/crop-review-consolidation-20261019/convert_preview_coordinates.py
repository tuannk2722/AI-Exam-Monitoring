"""Convert manually inspected preview coordinates to immutable native trials."""

import argparse
import json

from intake import HERE, ROOT, dump
from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", default="03", choices=["03", "04", "05", "06", "07", "08"])
    args = parser.parse_args()
    ledger = {
        r["id"]: r for r in json.loads((HERE / "intake-ledger.json").read_text(encoding="utf-8"))
    }
    ledger.update(
        {
            r["id"]: r
            for r in json.loads((HERE / "additional-parents.json").read_text(encoding="utf-8"))
        }
    )
    rows = json.loads(
        (HERE / f"preview-coordinates-owner{args.batch}.json").read_text(encoding="utf-8")
    )
    trials = []
    for parent, candidate, basis, box, states, reason in rows:
        with Image.open(ROOT / ledger[parent]["source_path"]) as im:
            scale = im.width / basis
            xyxy = [round(v * scale) for v in box]
            assert 0 <= xyxy[0] < xyxy[2] <= im.width, candidate
            assert 0 <= xyxy[1] < xyxy[3] <= im.height, candidate
        trials.append(
            {
                "parent": parent,
                "id": candidate,
                "person": xyxy,
                "context": xyxy,
                "states": states,
                "reason": reason,
            }
        )
    dest = HERE / f"geometry-trials-owner-extra{args.batch}.json"
    if dest.exists():
        assert json.loads(dest.read_text(encoding="utf-8")) == trials
    else:
        dump(dest, trials)


if __name__ == "__main__":
    main()
