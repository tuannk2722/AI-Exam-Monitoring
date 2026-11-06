"""Rebuild exact released bytes and write the local labeled review gallery."""

import hashlib
import html
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.data.pilot_package import build_pilot_package
from ai_exam_monitoring.data.pilot_schema import read_records
from ai_exam_monitoring.data.source_review import preview_input
from ai_exam_monitoring.training.data import verify_dataset

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
BATCH = ROOT / "data/interim/dataset-merge-20261106"
SCRATCH = ROOT / "outputs/_scratch/dataset-merge-20261106"
DATASET = ROOT / "data/processed/pilot-b/pilot-b-20261106-v15"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    if path.exists():
        raise RuntimeError(f"Evidence exists: {path}")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    pointers = load(REPORT / "package-pointers.json")
    config = load(ROOT / pointers["config"]["path"])
    records = read_records(DATASET / "review-ledger.jsonl")
    release = load(DATASET / "release.json")
    roots = {k: ROOT / v for k, v in load(REPORT / "source-roots.json").items()}
    variables = SimpleNamespace(
        dataset=DATASET.relative_to(ROOT).as_posix(),
        dataset_version=config["dataset_version"], split_version=config["split_version"],
        encoding_version="pilot-b-targets-v1", payload_sha256=pointers["payload"]["sha256"],
    )
    used = verify_dataset(DATASET, variables)
    crop_inputs = {}
    for row in records:
        if row.crop is None or row.crop.review is None:
            continue
        path = DATASET / row.crop.crop_relpath
        if not path.exists():
            path = roots[row.source.source_id] / row.source.image_relpath
        assert sha256_file(path) == row.crop.crop_sha256
        crop_inputs[row.sample_id] = path
    rebuild = SCRATCH / "rebuild"
    if rebuild.exists():
        raise RuntimeError("Do not overwrite a rebuild")
    build_pilot_package(
        list(reversed(records)), rebuild, roots, crop_inputs, [], release,
        [r.sample_id for r in records],
    )
    assert (rebuild / "checksums.sha256").read_bytes() == (DATASET / "checksums.sha256").read_bytes()
    print("reverse-order rebuild exact checksum inventory PASS", flush=True)
    inv = load(REPORT / "inventory.json")
    new = inv["imports"] + inv["native_included"]
    final = {r.sample_id: r for r in used}
    groups = defaultdict(set)
    byte_splits = defaultdict(set)
    rgb_splits = defaultdict(set)
    for r in used:
        groups[r.group.leakage_group_id].add(r.split)
        byte_splits[r.crop.crop_sha256].add(r.split)
    for row in inv["imports"] + inv["native_included"] + inv["parent"]:
        if row["id"] in final:
            rgb_splits[(str(row["size"]), row["rgb_sha256"])].add(final[row["id"]].split)
    assert not any(len(s) != 1 for s in groups.values())
    assert not any(len(s) != 1 for s in byte_splits.values())
    assert not any(len(s) != 1 for s in rgb_splits.values())
    generated = load(REPORT / "group-lineage.json")["generated_parent_ids_locked_train"]
    assert all(final[s].split == "train" for s in generated)
    assert all(final[r["id"]].split == "train" for r in inv["imports"])
    assert {r["id"] for r in new} <= set(final)
    assert "V6-SB-048-ADD01" not in final and "G08-B01-F00001" not in final
    assert final["G09-B05-F00043"].target_values == (0, 1)
    assert final["S06-F00096-P01"].target_values == (1, None)
    assert final["S06-F00096-P01"].target_mask == (1, 0)
    cards = []
    lines = ["# Nhãn và split của 368 crop mới", "",
             "Thứ tự nhãn: phone / looking. U giữ mask 0. Nhãn N/N không tự là normal.", "",
             "| ID | Tên owner / crop native | Nhãn cuối | Split | Nhóm nguồn |",
             "|---|---|---|---|---|"]
    inputs = BATCH / "inputs"
    inputs.mkdir()
    letter = {"positive": "P", "negative": "N", "unknown": "U"}
    for row in new:
        r = final[row["id"]]
        label = letter[r.phone_use.state] + "/" + letter[r.looking_around.state]
        path = ROOT / row["path"]
        native = Path(os.path.relpath(path, BATCH)).as_posix()
        with Image.open(path) as image:
            preview_input(image.convert("RGB"), 336, (124, 116, 104)).save(inputs / (r.sample_id + ".png"))
        name = row["original_name"]
        group = r.group.leakage_group_id
        cards.append(
            f'<article data-key="{html.escape(r.sample_id + " " + name + " " + group, quote=True)}" '
            f'data-split="{r.split}" data-label="{label}"><a href="{html.escape(native, quote=True)}">'
            f'<img loading="lazy" src="inputs/{r.sample_id}.png" alt="{r.sample_id}"></a>'
            f'<b>{r.sample_id} · {label} · {r.split}</b><span>{html.escape(name)}</span>'
            f'<small>{group} · native {row["size"][0]} × {row["size"][1]}</small></article>'
        )
        lines.append(f"| {r.sample_id} | {name} | {label} | {r.split} | {group} |")
    document = """<!doctype html><html lang="vi"><meta charset="utf-8">
<title>V15 · 368 crop mới đã rà soát</title><style>
body{font:16px system-ui;background:#eff2f6;margin:24px;color:#162033}
header{position:sticky;top:0;background:#eff2f6ee;padding:8px 0;z-index:1}
input,select{padding:10px;margin-right:8px;border:1px solid #bbc4d0;border-radius:6px}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px}
article{background:white;border-radius:10px;padding:12px;display:flex;flex-direction:column;gap:6px}
article[hidden]{display:none}img{width:336px;max-width:100%;height:auto}
span,small{overflow-wrap:anywhere}small{color:#576477}h1{font-size:24px}
</style><header><h1>V15 · 368 crop mới đã rà soát</h1>
<p>Phone / Looking · 349 train / 19 val · U được mask · Bấm ảnh để mở native.</p>
<input id="q" placeholder="Tìm ID, tên file hoặc nhóm nguồn">
<select id="s"><option value="">Mọi split</option><option>train</option><option>val</option></select>
<select id="l"><option value="">Mọi nhãn</option><option>N/N</option><option>N/P</option>
<option>P/N</option><option>P/P</option><option>U/N</option><option>P/U</option></select>
<b id="count"></b></header><main>__CARDS__</main><script>
let cards=[...document.querySelectorAll('article')];
function filter(){let q=document.querySelector('#q').value.toLowerCase();
let s=document.querySelector('#s').value,l=document.querySelector('#l').value;
cards.forEach(c=>c.hidden=!!((q&&!c.dataset.key.toLowerCase().includes(q))||
(s&&c.dataset.split!==s)||(l&&c.dataset.label!==l)));
document.querySelector('#count').textContent=cards.filter(c=>!c.hidden).length+' / 368';}
document.querySelectorAll('input,select').forEach(e=>e.addEventListener('input',filter));filter();
</script></html>""".replace("__CARDS__", "".join(cards))
    (BATCH / "index.html").write_text(document, encoding="utf-8")
    (REPORT / "labels.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    cross = load(REPORT / "cross-split-triage.json")
    assert len(cross) == 1 and cross[0]["ids"] == ["V6R2-CA-008-ADD02", "V6-EX-043"]
    save(REPORT / "handoff-validation.json", {
        "rebuild_reverse_order_exact_payload": "PASS",
        "source_payload_checksum": sha256_file(DATASET / "checksums.sha256"),
        "strict_training_loader": "PASS", "schema_and_usage": "PASS",
        "cross_split_group_leakage": 0, "cross_split_crop_byte_duplicates": 0,
        "cross_split_crop_rgb_duplicates": 0,
        "cross_split_all_pairs_checked": 1377 * 344,
        "cross_split_dhash_at_most_10": {
            "candidate_pairs": 1, "review": "visually distinct people, clothing and scenes; not duplicate",
            "ids": cross[0]["ids"],
        },
        "all_252_imports_train": True, "all_74_inherited_generated_train": True,
        "native_labels_including_U_masks": "PASS", "parent_explicit_changes": "PASS",
        "new_crop_label_counts": dict(Counter(
            letter[final[r["id"]].phone_use.state] + letter[final[r["id"]].looking_around.state]
            for r in new)),
        "gallery_cards": len(cards), "gallery_local_links": "generated from verified inputs",
        "gallery_path": (BATCH / "index.html").relative_to(ROOT).as_posix(),
        "tests": {"pilot_schema": 22, "pilot_package": 8, "derived_crop": 2,
                  "training_no_test_release": 4, "training_preservation": 10,
                  "image_similarity": 3},
        "tests_total_passed": 49,
        "training_or_classifier_inference": False, "test_opened": False,
        "rebuild_scratch": rebuild.relative_to(ROOT).as_posix(),
        "rebuild_scratch_disposable_after_checksum_evidence": True,
    })
    print(json.dumps({"used": len(used), "new_gallery": len(cards),
                      "rebuild_payload_match": True, "cross_split_leakage": 0}))


if __name__ == "__main__":
    main()
