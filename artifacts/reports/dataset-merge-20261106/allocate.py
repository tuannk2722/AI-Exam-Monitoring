"""Batch research worksheet: constrained whole-family allocation, no model scores.

SciPy is an already installed local research dependency, not a new runtime dependency.
The selected assignment is explicit metadata consumed by the existing exporter.
"""

import json
from collections import Counter, defaultdict
from importlib.metadata import version
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from ai_exam_monitoring.data.pilot_schema import read_records

ROOT = Path(__file__).resolve().parents[3]
REPORT = Path(__file__).resolve().parent
PARENT = ROOT / "data/processed/pilot-b/pilot-b-20261024-v14"
NAMED_PARENTS = (
    "E004-EX-C001", "E004-EX-C163", "G08-B02-F00001", "G19-A01-F00052",
    "G19-A02-F00056", "SCB-turnhead-016", "V6R2-EX-009", "V7-C-111", "V7-OE-S094-A01-R04",
)
EXCLUDE = {"V6-SB-048-ADD01", "G08-B01-F00001"}


def write(name, value):
    path = REPORT / name
    if path.exists():
        raise RuntimeError(f"Do not overwrite allocation: {path}")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parent = read_records(PARENT / "manifest.jsonl")
    by_id = {r.sample_id: r for r in parent}
    inv = json.loads((REPORT / "inventory.json").read_text(encoding="utf-8"))
    review = json.loads((REPORT / "visual-review.json").read_text(encoding="utf-8"))
    provenance = json.loads((ROOT / "artifacts/reports/v12-reconcile-20261022/candidate-source-provenance.json").read_text(encoding="utf-8"))
    generated = {r["id"] for r in provenance if r.get("owner_provenance_confirmation")}
    generated |= {r.sample_id for r in parent if r.source.source_id == "owner-generated-20261024"}
    assert len(generated) == 74
    group_rows = defaultdict(list)
    rows = []
    states = {"positive": "P", "negative": "N", "unknown": "U"}
    for r in parent:
        if r.sample_id in EXCLUDE:
            continue
        label = states[r.phone_use.state] + states[r.looking_around.state]
        if r.sample_id == "G09-B05-F00043":
            label = "NP"
        rows.append({"id": r.sample_id, "group": r.group.leakage_group_id,
                     "label": label, "parent_split": r.split, "origin": "V14"})
    sources = {r["parent_id"]: r["source_id"] for r in json.loads(
        (ROOT / "artifacts/reports/accepted-frames-crops-20261105/inventory.json").read_text(encoding="utf-8"))}
    families = {s: f"M15-FRAMES-{s}" for s in sources.values()}
    families.update(S01="M15-FAMILY-S01-S07", S07="M15-FAMILY-S01-S07",
                    S02="M15-FAMILY-S02-S06", S06="M15-FAMILY-S02-S06",
                    S09="M15-FAMILY-S09-S10", S10="M15-FAMILY-S09-S10")
    import_names = {r["id"]: r["original_name"] for r in inv["imports"]}
    lineage = []
    for r in review["rows"]:
        sid = r["id"]
        ancestor, src = None, None
        if sid.startswith("S"):
            src = sid[:3]
        else:
            name = import_names[sid]
            for p in NAMED_PARENTS:
                if name.startswith(p + " "):
                    ancestor = p
                    break
            if ancestor is None:
                for vid, source in sources.items():
                    if name.startswith(vid + "_"):
                        src = source
                        break
                if src is None and name.startswith("S"):
                    src = name[:3]
        group = by_id[ancestor].group.leakage_group_id if ancestor else families.get(src, "M15-THEMATIC-UNKNOWN-PARENT")
        assert ancestor or src or import_names.get(sid, "").startswith("generate ")
        rows.append({"id": sid, "group": group, "label": r["final_label"],
                     "parent_split": None, "origin": "new"})
        lineage.append({"id": sid, "source_id": src, "confirmed_ancestor_crop_id": ancestor,
                        "leakage_group_id": group,
                        "relationship": "owner-confirmed named ancestor" if ancestor or src else
                        "owner thematic generation, exact parent unknown"})
    for r in rows:
        group_rows[r["group"]].append(r)
    train_locks = {by_id[s].group.leakage_group_id for s in NAMED_PARENTS}
    train_locks |= {by_id[s].group.leakage_group_id for s in generated}
    train_locks |= {g for g, rs in group_rows.items() if len(rs) > 34}
    train_locks |= {r["group"] for r in rows if r["id"].startswith("M15-")}
    # All descendants of frame sources are training families, including native siblings.
    train_locks |= set(families.values()) - {families["S03"]}
    val_locks = {r["group"] for r in rows if r["parent_split"] == "val"} - train_locks
    val_locks.add(families["S03"])
    assert not train_locks & val_locks
    groups = sorted(group_rows)
    names = ["records", "phone_P", "phone_N", "phone_U", "looking_P", "looking_N", "looking_U",
             "joint_PP", "joint_PN", "joint_NP", "joint_NN"]

    def vector(rs):
        counts = Counter(r["label"] for r in rs)
        return np.array([len(rs)] + [sum(r["label"][t] == s for r in rs) for t in (0, 1) for s in "PNU"]
                        + [counts[s] for s in ("PP", "PN", "NP", "NN")], dtype=float)

    vectors = np.stack([vector(group_rows[g]) for g in groups], axis=1)
    totals = vector(rows)
    n, d = len(groups), len(names)
    target_size = round(len(rows) * .2)
    target = totals * (target_size / len(rows))
    a = np.hstack((vectors, -np.eye(d), np.eye(d)))
    lo = np.zeros(n + 2 * d)
    hi = np.r_[np.ones(n), np.full(2 * d, np.inf)]
    for i, g in enumerate(groups):
        if g in train_locks:
            hi[i] = 0
        if g in val_locks:
            lo[i] = 1
    objective = np.r_[np.zeros(n), 1 / np.maximum(target, 1), 1 / np.maximum(target, 1)]
    constraints = [LinearConstraint(a, target, target)]
    hard = np.zeros((5, n + 2 * d))
    hard[0, :n] = vectors[0]
    hard[1, :n] = vectors[1]
    hard[2, :n] = vectors[2]
    hard[3, :n] = vectors[4]
    hard[4, :n] = vectors[5]
    constraints.append(LinearConstraint(hard, [target_size, 50, 50, 50, 50],
                                        [target_size, np.inf, np.inf, np.inf, np.inf]))
    integrality = np.r_[np.ones(n), np.zeros(2 * d)]
    result = milp(objective, integrality=integrality, bounds=Bounds(lo, hi),
                  constraints=constraints, options={"time_limit": 45, "mip_rel_gap": 0})
    if result.x is None:
        raise RuntimeError(result.message)
    first_objective = float(objective @ result.x)
    # Preserve the primary distribution solution; prefer fewer old-train moves next.
    second = np.zeros(n + 2 * d)
    for i, g in enumerate(groups):
        second[i] = sum(r["parent_split"] == "train" for r in group_rows[g]) + (i + 1) * 1e-7
    constraints.append(LinearConstraint(objective, -np.inf, first_objective + 1e-7))
    result2 = milp(second, integrality=integrality, bounds=Bounds(lo, hi), constraints=constraints,
                   options={"time_limit": 45, "mip_rel_gap": 0})
    selected = result2 if result2.x is not None else result
    selected_val = {g for i, g in enumerate(groups) if selected.x[i] > .5}
    assigned = [{**r, "split": "val" if r["group"] in selected_val else "train"} for r in rows]
    assert len({r["id"] for r in assigned}) == len(rows) == 1721
    assert not selected_val & train_locks and val_locks <= selected_val
    actual = vector([r for r in assigned if r["split"] == "val"])
    assert actual[0] == target_size and min(actual[[1, 2, 4, 5]]) >= 50
    write("group-lineage.json", {
        "rows": lineage, "generated_parent_ids_locked_train": sorted(generated),
        "native_source_families": families,
        "family_basis": {
            "M15-FAMILY-S01-S07": "conservative possible school-family overlap from uniforms and classroom fixtures, not verified same session",
            "M15-FAMILY-S02-S06": "conservative possible school-family overlap from uniform/work setting, not verified same session",
            "M15-FAMILY-S09-S10": "matching school setting/uniforms and derivative families; same-family boundary without claiming same video",
        },
        "identity_claim": "No student identities or unverified session IDs inferred; families are leakage boundaries",
        "train_locked_groups": sorted(train_locks), "fixed_val_groups": sorted(val_locks),
    })
    write("allocation.json", {
        "status": "owner-delegated allocation; implementation follows QA",
        "method": "MILP whole-family stratification on P/N/U and fully-known joint states, never model predictions",
        "libraries": {p: version(p) for p in ("numpy", "scipy")},
        "target_val_fraction": .2, "target_val_records": target_size,
        "minimum_val_P_and_N_per_target": 50, "max_val_group_records": 34,
        "primary_objective": "sum of normalized absolute deviations from proportional P/N/U and joint-state counts",
        "secondary_objective": "minimize old-train records moved, then tiny stable group-order tie break",
        "primary_solver": {"status": int(result.status), "message": result.message,
                           "objective": first_objective, "gap": float(result.mip_gap)},
        "secondary_solver": {"status": int(result2.status), "message": result2.message,
                             "gap": float(result2.mip_gap) if result2.x is not None else None},
        "total_counts": dict(zip(names, totals.astype(int).tolist(), strict=True)),
        "val_counts": dict(zip(names, actual.astype(int).tolist(), strict=True)),
        "train_counts": dict(zip(names, (totals - actual).astype(int).tolist(), strict=True)),
        "groups_by_split": dict(Counter("val" if g in selected_val else "train" for g in groups)),
        "old_val_to_train": sorted(r["id"] for r in assigned if r["parent_split"] == "val" and r["split"] == "train"),
        "old_train_to_val": sorted(r["id"] for r in assigned if r["parent_split"] == "train" and r["split"] == "val"),
        "new_counts": dict(Counter(r["split"] for r in assigned if r["origin"] == "new")),
        "rows": sorted(assigned, key=lambda r: r["id"]),
        "limitations": [
            "Optimality applies only to this declared integer objective if solver status is zero, not future model performance",
            "Validation is development and uses revised membership; old E008 metrics cannot be directly compared",
            "Any future E009 needs fresh approved initialization; E008 or historical checkpoints saw some newly assigned validation crops during training",
            "All imported derivatives and thematic generation stay training-only, including their native/parent siblings",
            "Historical uncertain synthetic parentage is inherited and not disproved by unique hashes",
        ],
    })
    print(json.dumps({"train": len(rows) - target_size, "val": target_size,
                      "val_counts": dict(zip(names, actual.astype(int).tolist(), strict=True)),
                      "new_counts": Counter(r["split"] for r in assigned if r["origin"] == "new"),
                      "old_train_to_val": sum(r["parent_split"] == "train" and r["split"] == "val" for r in assigned),
                      "solver": [int(result.status), int(result2.status)]}, indent=2))


if __name__ == "__main__":
    main()
