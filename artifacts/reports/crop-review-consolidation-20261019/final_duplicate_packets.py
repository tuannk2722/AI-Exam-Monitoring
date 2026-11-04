"""Build an effective draft cohort and explicit duplicate comparison queue."""

import itertools
import json
from collections import defaultdict

from intake import HERE, MEDIA, ROOT, dump, sha
from PIL import Image, ImageDraw, ImageFont

from ai_exam_monitoring.data.image_similarity import difference_hash
from ai_exam_monitoring.data.source_review import preview_input


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def overlap(a, b):
    area = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return area / max(1e-12, min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1])))


def main(suffix=""):
    ledger = read("resolved-ledger.json")
    changes = read("delta-review.json")
    replaced = {
        r["parent"] for r in changes if r["kind"] == "geometry" and r["relation"] == "replacement"
    }
    removed = {
        r["parent"] for r in changes if r["kind"] in {"source_exclusion", "duplicate_exclusion"}
    }
    cohort = []
    for row in ledger:
        if row["id"] in replaced | removed or row["owner_interpreted_action"] == "exclude":
            continue
        box = row.get("context_xyxy") or list(row["context_box"].values())
        states = row.get("label_resolution", {}).get("states", row["owner_interpreted_states"])
        cohort.append(
            {
                "id": row["id"],
                "parent": row["id"],
                "path": row["crop_path"],
                "source": row["source_path"],
                "box": box,
                "states": states,
                "kind": "existing",
            }
        )
    geometry = {r["candidate_id"]: r for r in read("geometry-review.json")}
    for row in changes:
        if row["kind"] == "geometry":
            cohort.append(
                {
                    "id": row["id"],
                    "parent": row["parent"],
                    "path": row["after"],
                    "source": row["source"],
                    "box": geometry[row["id"]]["context_xyxy"],
                    "states": row["states"],
                    "kind": "proposal",
                }
            )
    by_parent = defaultdict(list)
    for row in cohort:
        with Image.open(ROOT / row["source"]) as source:
            w, h = source.size
            row["normalized_box"] = [v / (w if i % 2 == 0 else h) for i, v in enumerate(row["box"])]
        with Image.open(ROOT / row["path"]) as crop:
            rgb = crop.convert("RGB")
            row["dhash"] = difference_hash(rgb)
            row["rgb_sha"] = sha(str(rgb.size).encode() + rgb.tobytes())
        by_parent[row["parent"]].append(row)
    assert len({r["id"] for r in cohort}) == len(cohort)
    assert all(len(r["states"]) == 2 and r["states"] != ["U", "U"] for r in cohort)
    pairs = {}

    def add(a, b, reason):
        if a["id"] == b["id"]:
            return
        key = tuple(sorted([a["id"], b["id"]]))
        pairs.setdefault(key, {"a": key[0], "b": key[1], "reasons": []})["reasons"].append(reason)

    for a, b in itertools.combinations(cohort, 2):
        if a["rgb_sha"] == b["rgb_sha"] or (a["dhash"] ^ b["dhash"]).bit_count() <= 12:
            add(a, b, "crop_fingerprint")
        if a["source"] == b["source"] and overlap(a["box"], b["box"]) >= 0.25:
            add(a, b, "same_source_overlapping_region")
    source_triage = []
    for index, source_pair in enumerate(read("source-similarity.json")["near_source_pairs"], 1):
        active_a = [r for p in source_pair["a_members"] for r in by_parent[p]]
        active_b = [r for p in source_pair["b_members"] for r in by_parent[p]]
        queued = []
        for a, b in itertools.product(active_a, active_b):
            add(a, b, f"source_pair_{index}")
            queued.append(sorted([a["id"], b["id"]]))
        source_triage.append(
            {
                "source_pair": index,
                "a_members": source_pair["a_members"],
                "b_members": source_pair["b_members"],
                "active_pairs": queued,
                "status": "queued" if queued else "no_two_retained_sides",
            }
        )
    values = [dict(pair, pair_id=f"FD-{i:03}") for i, pair in enumerate(pairs.values(), 1)]
    dump(HERE / f"effective-draft-cohort{suffix}.json", cohort)
    dump(HERE / f"final-duplicate-pairs{suffix}.json", values)
    dump(HERE / f"source-pair-coverage{suffix}.json", source_triage)
    lookup = {r["id"]: r for r in cohort}
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    for start in range(0, len(values), 6):
        canvas = Image.new("RGB", (1000, 810), "white")
        draw = ImageDraw.Draw(canvas)
        for j, pair in enumerate(values[start : start + 6]):
            x, y = (j % 2) * 500, (j // 2) * 270
            draw.text((x + 3, y + 2), pair["pair_id"], fill="black", font=font)
            for side, key in enumerate(("a", "b")):
                row = lookup[pair[key]]
                draw.text((x + side * 248 + 3, y + 20), row["id"], fill="black", font=font)
                with Image.open(ROOT / row["path"]) as crop:
                    canvas.paste(
                        preview_input(crop.convert("RGB"), 224, (114, 114, 114)),
                        (x + side * 248 + 3, y + 42),
                    )
        canvas.save(
            MEDIA / "boards" / f"final-duplicates{suffix}-{start // 6 + 1:03}.jpg", quality=96
        )
    print(
        {
            "cohort": len(cohort),
            "pairs": len(values),
            "boards": (len(values) + 5) // 6,
            "source_pairs": len(source_triage),
        }
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--suffix", default="")
    main(parser.parse_args().suffix)
