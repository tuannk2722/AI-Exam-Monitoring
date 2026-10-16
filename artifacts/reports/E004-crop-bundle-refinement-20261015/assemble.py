"""Assemble manual audit decisions; output is review-only, not a training manifest."""

import hashlib
import json
import shutil
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = ROOT / "artifacts/reports/E004-crop-bundle-review-20261014"
OUT = ROOT / "outputs" / HERE.name


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


pins = read(HERE / "input-pins.json")
assert sha(OLD / "README.md") == pins["owner_snapshot_sha256"], "Owner review changed"
for path, expected in pins["files"].items():
    assert sha(ROOT / path) == expected, path
tracks = read(HERE / "track-inventory.json")
decisions = read(HERE / "visual-decisions.json")
rows = []
track_summary = []
phone = {
    "P": "Có mobile gắn với anchor trên tay hoặc bàn riêng.",
    "N": "Tay/bàn đủ quan sát và không thấy mobile; cần owner nghiệm thu absence.",
    "U": "Không đủ chắc về loại vật, attribution hoặc vùng tay/bàn; không suy absence.",
}
looking = {
    "P": "Hướng đầu/nhìn rõ ra ngoài vùng bài riêng với context.",
    ("N"): (
        "Hướng đầu và vùng bài đủ cho thấy đang nhìn vùng riêng; không suy từ tên hành động nguồn."
    ),
    "U": "Hướng đầu hoặc vùng bài không đủ rõ để kết luận.",
}


def finish(r):
    phone_state, looking_state = r["draft_labels"].split("/")
    r.update(
        phone_reason=phone[phone_state],
        looking_reason=looking[looking_state],
        status="draft_review_only",
        assigned_split=None,
        training_ready=False,
        canonical_targets=[None, None],
        canonical_mask=[0, 0],
        evidence_crop_sha256=r["crop_sha256"],
        input_sha256=sha(ROOT / r["input"]),
    )
    return r


for ti, t in enumerate(tracks, 1):
    decision = decisions["tracks"][str(ti)]
    keep_ids = set(decision["keep"])
    assert keep_ids <= {int(r["sample_id"][3:]) for r in t["rows"]}
    for original in t["rows"]:
        r = dict(original)
        num = int(r["sample_id"][3:])
        prior = r["draft_labels"]
        labels = decision["default"] or prior
        for override, ids in decision["overrides"].items():
            if num in ids:
                labels = override
        disposition = "shortlist" if num in keep_ids else "alternative"
        if num in decision.get("withhold", []) or labels == "U/U":
            disposition = "withheld"
        r.update(
            prior_draft_labels=prior,
            draft_labels=labels,
            label_changed=prior != labels,
            disposition=disposition,
            selection_reason=decision["reason"],
            reason=decision["reason"],
            cohort="supplied",
            description=t["anchor_id"],
            original_reason=original["reason"],
            revision_visual_status="viewed",
            comparison="revision_vs_previous_draft",
        )
        rows.append(finish(r))
    t["revision_visual_status"] = "all_effective_inputs_viewed"
    track_summary.append(
        dict(
            anchor_id=t["anchor_id"],
            before=t["count"],
            shortlist=len(keep_ids),
            reason=decision["reason"],
        )
    )

obs = read(HERE / "new-observations.json")["anchors"]
plan = read(HERE / "expansion-plan.json")
new = read(HERE / "expansion-ledger.json")
by_anchor = {a["id"]: a for a in plan["anchors"]}
for r in new:
    a = by_anchor[r["anchor_id"]]
    o = obs[r["anchor_id"]]
    assert len(a["frames"]) == len(o["labels"])
    labels = o["labels"][a["frames"].index(r["frame_num"])]
    disposition = "shortlist" if r["frame_num"] in o["keep"] else "alternative"
    if labels == "U/U":
        disposition = "withheld"
    r.update(
        sample_id=r["candidate_id"],
        draft_labels=labels,
        prior_draft_labels=None,
        label_changed=False,
        disposition=disposition,
        cohort="new",
        selection_reason=o["note"],
        reason=o["note"],
        revision_visual_status="native_and_224_viewed",
    )
    rows.append(finish(r))

aliases = {
    "g1_new_olive": "G1-A02",
    "g4_new_blue_jacket": "G4-A01",
    "g2_new_striped_green": "G2-A14",
    "g5_new_white_left": "G5-A14",
}
plan["status"] = "visual_qa_complete_draft_pending_owner"
dump(HERE / "expansion-plan.json", plan)
dump(HERE / "expansion-ledger.json", new)
for d in read(OLD / "derivatives.json"):
    if d.get("original_id"):
        continue
    r = dict(d)
    r.update(
        sample_id=r["candidate_id"],
        prior_draft_labels=r["draft_labels"],
        anchor_id=aliases[r["anchor_id"]],
        disposition="alternative" if r["candidate_id"] == "CB-NEW-03" else "shortlist",
        cohort="prior_addition",
        label_changed=False,
        description=r["new_anchor_id"],
        selection_reason=(
            "Giữ cặp tương phản/anchor bổ sung cũ; NEW-03 gần lặp G1-A02 nên làm alternative."
        ),
        revision_visual_status="224_viewed",
        frame_num=int(Path(r["source"]).stem.split("_")[-1]),
    )
    rows.append(finish(r))

for r in rows:
    if r["disposition"] == "alternative":
        # Same-anchor references are alternatives, not an assertion of pixel identity.
        r["representative_candidates"] = [
            x["candidate_id"]
            for x in rows
            if x["anchor_id"] == r["anchor_id"] and x["disposition"] == "shortlist"
        ]
    else:
        r["representative_candidates"] = []

frames = read(OLD / "frame-review-ledger.json")
for f in frames:
    f["refinement_visual_pass"] = (
        "viewed_in_53_overview_boards; native crops and 224 inputs checked"
        " for additions/ambiguities"
    )
    f["new_candidates"] = [r["candidate_id"] for r in new if r["source"] == f["path"]]
dump(HERE / "frame-coverage.json", frames)
dump(HERE / "candidate-ledger.json", rows)
dump(HERE / "track-summary.json", track_summary)
dump(HERE / "track-inventory.json", tracks)
decisions["status"] = "visual_pass_complete_draft_pending_owner"
dump(HERE / "visual-decisions.json", decisions)

selected = [r for r in rows if r["disposition"] == "shortlist"]
counts = dict(
    total=len(rows),
    supplied=765,
    new_crops=len(new),
    prior_additions=5,
    dispositions=dict(Counter(r["disposition"] for r in rows)),
    selected_cohorts=dict(Counter(r["cohort"] for r in selected)),
    selected_labels=dict(Counter(r["draft_labels"] for r in selected)),
    selected_anchors=len({r["anchor_id"] for r in selected}),
    original_anchors=len(tracks),
    parents=len({r["parent_id"] for r in rows}),
    changed_labels=sum(r["label_changed"] for r in rows),
    frames=len(frames),
    max_selected_per_anchor=max(Counter(r["anchor_id"] for r in selected).values()),
)
dump(HERE / "summary.json", counts)

refs = OUT / "references"
refs.mkdir(exist_ok=True)
reference_pins = {}
for name in [
    "frame1.jpg",
    "frame2.jpg",
    "frame3.1.jpg",
    "frame3.2.jpg",
    "frame4.jpg",
    "frame5.jpg",
]:
    source = Path("C:/Users/OS/Downloads/temp") / name
    dest = refs / name
    if dest.exists():
        assert sha(dest) == sha(source)
    else:
        shutil.copyfile(source, dest)
    reference_pins[dest.relative_to(ROOT).as_posix()] = sha(dest)
dump(HERE / "reference-pins.json", reference_pins)

gallery = []
for r in rows:
    item = {
        k: r.get(k)
        for k in [
            "candidate_id",
            "sample_id",
            "anchor_id",
            "description",
            "frame_num",
            "cohort",
            "draft_labels",
            "prior_draft_labels",
            "label_changed",
            "disposition",
            "reason",
            "phone_reason",
            "looking_reason",
            "representative_candidates",
        ]
    }
    for k in ["input", "crop", "source", "overlay"]:
        item[k] = "../../" + r[k] if r.get(k) else None
    item["sha256"] = r["crop_sha256"]
    gallery.append(item)
template = (HERE / "gallery-template.html").read_text(encoding="utf8")
(OUT / "index.html").write_text(
    template.replace("__DATA__", json.dumps(gallery, ensure_ascii=False).replace("</", "<\\/")),
    encoding="utf8",
)
review = [
    "# Batch review đề xuất mới",
    "",
    (
        "Draft; thứ tự nhãn phone/looking. Gallery mặc định chỉ hiện "
        "shortlist. Có thể nghiệm thu theo batch và ghi ngoại lệ; bảng này"
        " không tự tạo acceptance."
    ),
    "",
    "| ID | Draft | Quyết định owner / ngoại lệ |",
    "|---|---|---|",
]
review.extend(f"| {r['candidate_id']} | {r['draft_labels']} | |" for r in selected)
dest = HERE / "owner-review.md"
if not dest.exists():
    dest.write_text("\n".join(review) + "\n", encoding="utf8")
print(json.dumps(counts))
