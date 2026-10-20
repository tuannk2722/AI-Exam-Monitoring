"""Render the current unresolved queue, without assigning decisions."""

import json

from intake import HERE, MEDIA, ROOT, dump
from PIL import Image
from prepare_review import boards


def main():
    def read(name):
        return json.loads((HERE / name).read_text(encoding="utf-8"))

    ledger = {r["id"]: r for r in read("consolidated-ledger.json")}
    remaining = read("remaining-work.json")
    qa = [
        r
        for p in HERE.glob("qa-*.json")
        for r in json.loads(p.read_text(encoding="utf-8")).get("geometry_qa", [])
    ]
    trials = [
        r
        for p in HERE.glob("geometry-trials*.json")
        for r in json.loads(p.read_text(encoding="utf-8"))
    ]
    for kind in ("recrop_requests", "owner_interpretations"):
        rows = [ledger[i] for i in remaining[kind]]
        boards(
            [{"id": r["id"], "path": r["source_path"]} for r in rows],
            "remaining-" + kind,
            4,
            512,
            540,
        )
        focus_rows = []
        focus_dir = MEDIA / "focus"
        focus_dir.mkdir(exist_ok=True)
        for r in rows:
            box = list(r["context_box"].values())
            with Image.open(ROOT / r["source_path"]) as im:
                dx = max(15, round((box[2] - box[0]) * 0.18))
                dy = max(15, round((box[3] - box[1]) * 0.18))
                roi = [
                    max(0, box[0] - dx),
                    max(0, box[1] - dy),
                    min(im.width, box[2] + dx),
                    min(im.height, box[3] + dy),
                ]
                path = focus_dir / (r["id"] + ".png")
                im.convert("RGB").crop(roi).save(path)
                focus_rows.append(
                    {
                        "id": r["id"] + " " + str(roi),
                        "path": str(path.relative_to(ROOT)),
                        "roi": roi,
                        "source_size": list(im.size),
                    }
                )
        dump(HERE / ("focus-" + kind + ".json"), focus_rows)
        boards(focus_rows, "focus-" + kind, 4, 512, 540)
        packet = []
        for r in rows:
            ts = [t for t in trials if t["parent"] == r["id"]]
            ids = {t["id"] for t in ts}
            packet.append(
                {
                    "id": r["id"],
                    "owner": r["owner_review"],
                    "states": r["owner_interpreted_states"],
                    "person": r.get("person_box"),
                    "context": r.get("context_box"),
                    "trials": ts,
                    "qa": [q for q in qa if q["id"] in ids],
                }
            )
        dump(HERE / ("remaining-" + kind + "-details.json"), packet)


if __name__ == "__main__":
    main()
