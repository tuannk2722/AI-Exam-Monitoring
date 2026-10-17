"""Deterministic group allocation proposal, never modifies a canonical package."""

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path.cwd()
P = ROOT / "artifacts/reports/train-val-plan-20261017"
OUT = P
rows = json.loads((P / "pool-inventory.json").read_text(encoding="utf-8"))
parents = {r["id"]: r["id"] for r in rows}


def find(x):
    while parents[x] != x:
        parents[x] = parents[parents[x]]
        x = parents[x]
    return x


def union(a, b):
    a, b = find(a), find(b)
    if a != b:
        parents[max(a, b)] = min(a, b)


for field in ["group", "source_sha", "crop_sha", "rgb_sha"]:
    seen = {}
    for r in rows:
        value = r[field]
        if value in seen:
            union(r["id"], seen[value])
        else:
            seen[value] = r["id"]
seen = {}
for r in rows:
    if not r["video"]:
        continue
    key = (r["source_id"], r["video"])
    if key in seen:
        union(r["id"], seen[key])
    else:
        seen[key] = r["id"]
links = [
    {
        "groups": ["NEW-G01", "NEW-G08", "NEW-G10", "NEW-G19"],
        "reason": "Cùng bố cục phòng, rèm và camera; gom cảnh bảo thủ, không suy danh tính.",
    },
    {
        "groups": [
            "NEW-G03",
            "NEW-G07",
            "NEW-G13",
            "NEW-G14",
            "NEW-G21",
            "NEW-G22",
            "NEW-G23",
            "NEW-G26",
        ],
        "reason": "Cụm video đồng phục/cảnh liên quan có khả năng cùng trường/lớp; gộp bảo thủ khi chưa có mapping buổi. Không khẳng định cùng người.",
    },
    {
        "groups": [
            "E004-CROP-TRAIN-Q001",
            "NEW-G02",
            "NEW-G04",
            "NEW-G11",
            "NEW-G16",
            "NEW-G18",
            "NEW-G20",
            "NEW-G24",
            "NEW-G25",
        ],
        "reason": "Giữ quarantine 345 nguyên khối và gom các cảnh phòng vàng/cửa xanh mới còn nghi quan hệ nguồn; đề xuất bảo thủ, không xác nhận độc lập bằng dHash.",
    },
]
for link in links:
    ids = [r["id"] for r in rows if r["group"] in link["groups"]]
    for ident in ids[1:]:
        union(ids[0], ident)
groups = defaultdict(list)
for r in rows:
    groups[find(r["id"])].append(r)
keys = sorted(groups)
sources = sorted({r["source_id"] for r in rows})


def vector(rr):
    values = [len(rr)]
    for t in [0, 1]:
        values.extend(sum(r["states"][t] == s for r in rr) for s in ["P", "N", "U"])
    values.extend(sum(r["source_id"] == s for r in rr) for s in sources)
    return np.asarray(values, dtype=float)


matrix = np.array([vector(groups[k]) for k in keys])
total = matrix.sum(0)
target = total * 0.2
scale = np.maximum(target, 5)
weights = np.asarray([5] + [1] * 6 + [0.25] * len(sources))


def score(v):
    return float(np.sum(weights * ((v - target) / scale) ** 2))


# Keep uncertain large classroom clusters together on train side; no weight reuse.
locked = {
    i
    for i, k in enumerate(keys)
    if any(r["group"] in ["E004-CROP-TRAIN-Q001", "NEW-G03"] for r in groups[k])
}
best = None
for seed in range(64):
    rng = random.Random(42 + seed)
    order = [i for i in range(len(keys)) if i not in locked]
    rng.shuffle(order)
    chosen = set()
    v = np.zeros_like(total)
    for _ in range(5):
        changed = False
        for i in order:
            nv = v - matrix[i] if i in chosen else v + matrix[i]
            if score(nv) + 1e-12 < score(v):
                if i in chosen:
                    chosen.remove(i)
                else:
                    chosen.add(i)
                v = nv
                changed = True
        if not changed:
            break
    candidate = (score(v), sorted(chosen), v)
    if best is None or (candidate[0], candidate[1]) < (best[0], best[1]):
        best = candidate
selected = set(best[1])
group_rows = []
assignments = []
for i, k in enumerate(keys):
    rr = groups[k]
    gid = "PLAN-" + hashlib.sha256("|".join(sorted(r["id"] for r in rr)).encode()).hexdigest()[:16]
    role = "val" if i in selected else "train"
    group_rows.append(
        {
            "group_id": gid,
            "role": role,
            "count": len(rr),
            "parent_groups": sorted({r["group"] for r in rr}),
            "locked_train_due_to_uncertainty": i in locked,
            "phone": dict(Counter(r["states"][0] for r in rr)),
            "looking": dict(Counter(r["states"][1] for r in rr)),
        }
    )
    for r in rr:
        assignments.append(
            {
                "sample_id": r["id"],
                "origin": r["origin"],
                "proposed_role": role,
                "proposed_group": gid,
                "prior_usage": r["prior_usage"],
                "states": r["states"],
                "crop_sha256": r["crop_sha"],
                "source_sha256": r["source_sha"],
            }
        )
assignments.sort(key=lambda r: r["sample_id"])
summary = {}
for role in ["train", "val"]:
    aa = [a for a in assignments if a["proposed_role"] == role]
    ids = {a["sample_id"] for a in aa}
    rr = [r for r in rows if r["id"] in ids]
    summary[role] = {
        "count": len(aa),
        "groups": len({a["proposed_group"] for a in aa}),
        "new270": sum(a["origin"] == "new270" for a in aa),
        "phone": dict(Counter(a["states"][0] for a in aa)),
        "looking": dict(Counter(a["states"][1] for a in aa)),
        "source_counts": dict(Counter(r["source_id"] for r in rr)),
        "supporting_groups": {
            f"{t}_{s}": len({a["proposed_group"] for a in aa if a["states"][ti] == s})
            for ti, t in enumerate(["phone", "looking"])
            for s in ["P", "N"]
        },
    }
for field in ["group", "source_sha", "crop_sha", "rgb_sha"]:
    rolemap = defaultdict(set)
    roles = {a["sample_id"]: a["proposed_role"] for a in assignments}
    for r in rows:
        rolemap[r[field]].add(roles[r["id"]])
    assert all(len(x) == 1 for x in rolemap.values())
assert sum(v["count"] for v in summary.values()) == 1451
result = {
    "status": "DRAFT_not_applied",
    "seed_search": list(range(42, 106)),
    "objective": "20% total and label support, softly balance source datasets; no scores/model outputs used",
    "visual_group_proposals": links,
    "locked_train_policy": "Quarantine group and uncertain blue-uniform cluster retained as units on train side; not independent source claims",
    "summary": summary,
    "groups": group_rows,
    "assignments": assignments,
    "safety": {
        "labels_unchanged": True,
        "test_reserve_pixels_opened": False,
        "canonical_packages_mutated": False,
        "train_started": False,
        "all_parent_groups_source_crop_rgb_keys_single_role": True,
    },
}
expected_text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
accepted_path = OUT / "allocation.json"
validation = json.loads((P / "validation.json").read_text(encoding="utf-8"))
assert hashlib.sha256(accepted_path.read_bytes()).hexdigest() == validation["allocation_sha256"]
assert accepted_path.read_text(encoding="utf-8") == expected_text, (
    "Accepted allocation must not be overwritten"
)
print(json.dumps(summary, indent=2))
print("groups", len(groups), "score", best[0])
