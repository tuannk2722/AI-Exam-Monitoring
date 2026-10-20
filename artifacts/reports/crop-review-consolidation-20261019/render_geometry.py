"""Render explicitly reviewed coordinates through the active crop writer."""

import json

from intake import HERE, MEDIA, ROOT, dump, sha
from PIL import Image
from prepare_review import boards

from ai_exam_monitoring.data.pilot_schema import PixelBox
from ai_exam_monitoring.data.source_review import SourceImage, member_key, write_pending_crop


def main():
    queue = {
        r["id"]: r for r in json.loads((HERE / "intake-ledger.json").read_text(encoding="utf-8"))
    }
    additional_path = HERE / "additional-parents.json"
    if additional_path.exists():
        for row in json.loads(additional_path.read_text(encoding="utf-8")):
            assert row["id"] not in queue
            queue[row["id"]] = row
    youtube = {
        r["candidate_id"]: r
        for r in json.loads(
            (HERE.parent / "youtube-frame-audit-20261018" / "review-index.json").read_text(
                encoding="utf-8"
            )
        )
    }
    trials = [
        trial
        for path in sorted(HERE.glob("geometry-trials*.json"))
        for trial in json.loads(path.read_text(encoding="utf-8"))
    ]
    assert len({trial["id"] for trial in trials}) == len(trials)
    previous_path = HERE / "geometry-review.json"
    previous = (
        {r["candidate_id"]: r for r in json.loads(previous_path.read_text(encoding="utf-8"))}
        if previous_path.exists()
        else {}
    )
    rows = []
    for t in trials:
        r = queue[t["parent"]]
        path = ROOT / r["source_path"]
        blob = path.read_bytes()
        expected_sha = (
            r["source_sha256"]
            if r["audit"] in {"legacy836", "additional"}
            else youtube[r["id"]]["source_sha256"]
        )
        assert sha(blob) == expected_sha
        dest = MEDIA / "candidates" / t["id"]
        if dest.exists():
            p = json.loads((dest / "proposal.json").read_text(encoding="utf-8"))
            assert p["context_xyxy"] == t["context"] and p["person_xyxy"] == t["person"]
        else:
            with Image.open(path) as im:
                source = SourceImage(
                    member_key(r["source_path"]),
                    sha(blob),
                    "",
                    "unassigned",
                    blob,
                    im.convert("RGB"),
                    (),
                )
                p = write_pending_crop(
                    source,
                    PixelBox(*t["person"]),
                    PixelBox(*t["context"]),
                    t["id"],
                    MEDIA / "candidates",
                    states=tuple(t["states"]),
                    reason=t["reason"],
                    input_size=224,
                    fill=(114, 114, 114),
                )
        rows.append(
            {
                **p,
                "parent_id": t["parent"],
                "qa_status": previous.get(t["id"], {}).get("qa_status", "pending"),
                "crop_path": str((dest / "crop.png").relative_to(ROOT)),
                "input_path": str((dest / "input.png").relative_to(ROOT)),
            }
        )
    dump(HERE / "geometry-review.json", rows)
    boards(
        [{"id": r["candidate_id"] + " native", "path": r["crop_path"]} for r in rows],
        "geometry-native",
        4,
        512,
        540,
    )
    boards(
        [{"id": r["candidate_id"] + " input224", "path": r["input_path"]} for r in rows],
        "geometry-input",
        4,
        320,
        270,
    )


if __name__ == "__main__":
    main()
