"""Publish only manually checked changes, clearly keeping the audit in progress."""

import html
import json
import os
from collections import Counter

from intake import HERE, MEDIA, ROOT, dump, sha
from PIL import Image

from ai_exam_monitoring.data.source_review import preview_input


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def link(path):
    return html.escape(os.path.relpath(ROOT / path, MEDIA).replace("\\", "/"), quote=True)


def browser_source(path):
    original = ROOT / path
    if original.suffix != ".bin":
        return path
    blob = original.read_bytes()
    with Image.open(original) as image:
        extension = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}[image.format]
    directory = MEDIA / "source-views"
    directory.mkdir(exist_ok=True)
    target = directory / (sha(blob) + extension)
    if not target.exists():
        target.write_bytes(blob)
    assert target.read_bytes() == blob
    return str(target.relative_to(ROOT))


def main():
    ledger = read("consolidated-ledger.json")
    parents = {r["id"]: r for r in ledger}
    if (HERE / "additional-parents.json").exists():
        for row in read("additional-parents.json"):
            assert row["id"] not in parents
            parents[row["id"]] = row
    qa = {}
    for name in [p.name for p in sorted(HERE.glob("qa-*.json"))]:
        for row in read(name).get("geometry_qa", []):
            qa[row["id"]] = row
    geometries = read("geometry-review.json")
    relation_overrides = (
        read("geometry-relations.json") if (HERE / "geometry-relations.json").exists() else {}
    )
    assert set(relation_overrides.values()) <= {"replacement", "additional_anchor"}
    changes = []
    checks = []
    label_resolutions = (
        read("manual-label-resolutions.json")
        if (HERE / "manual-label-resolutions.json").exists()
        else []
    )
    assert len({r["id"] for r in label_resolutions}) == len(label_resolutions)
    for resolution in label_resolutions:
        parent = parents[resolution["id"]]
        assert sha((ROOT / parent["crop_path"]).read_bytes()) == parent["crop_sha256"]
        parent["label_resolution"] = {
            **resolution,
            "crop_sha256": parent["crop_sha256"],
            "source_sha256": sha((ROOT / parent["source_path"]).read_bytes()),
            "geometry_acceptance_inferred": False,
        }
        if resolution["needs_review"]:
            changes.append(
                {
                    "id": resolution["id"],
                    "parent": resolution["id"],
                    "kind": "label_change",
                    "states": resolution["states"],
                    "note": resolution["note"],
                    "before": parent["crop_path"],
                    "before_caption": "Nhãn trước: " + "/".join(parent["parent_states"]),
                    "after": parent["crop_path"],
                    "input": str(
                        (MEDIA / "label-inputs" / (resolution["id"] + ".png")).relative_to(ROOT)
                    ),
                    "source": parent["source_path"],
                    "owner_approved": False,
                }
            )
    for row in geometries:
        verdict = qa.get(row["candidate_id"], {"result": "pending"})
        row["qa_status"] = verdict["result"]
        row["qa_note"] = verdict.get("note", "")
        row["qa_states"] = verdict.get("states")
        if verdict["result"] != "pass_draft":
            continue
        parent = parents[row["parent_id"]]
        with Image.open(ROOT / parent["source_path"]) as source:
            expected = source.convert("RGB").crop(row["context_xyxy"])
        with Image.open(ROOT / row["crop_path"]) as crop:
            assert (
                crop.size == expected.size and crop.convert("RGB").tobytes() == expected.tobytes()
            )
        assert sha((ROOT / row["crop_path"]).read_bytes()) == row["crop_sha256"]
        assert sha((ROOT / row["input_path"]).read_bytes()) == row["input_sha256"]
        with Image.open(ROOT / row["input_path"]) as input_image:
            expected_input = preview_input(expected, 224, (114, 114, 114))
            assert input_image.convert("RGB").tobytes() == expected_input.tobytes()
        assert row["canonical_mask"] == [0, 0]
        checks.append(row["candidate_id"])
        changes.append(
            {
                "id": row["candidate_id"],
                "parent": row["parent_id"],
                "kind": "geometry",
                "relation": relation_overrides.get(
                    row["candidate_id"],
                    (
                        "additional_anchor"
                        if "-ADD" in row["candidate_id"] or parent["audit"] == "additional"
                        else "replacement"
                    ),
                ),
                "states": verdict["states"],
                "note": verdict["note"],
                "before": parent["crop_path"],
                "before_caption": ("Ảnh đánh dấu" if parent["audit"] == "additional" else "Trước"),
                "after": row["crop_path"],
                "input": row["input_path"],
                "source": parent["source_path"],
                "qa_status": "pass_draft",
                "owner_approved": False,
            }
        )
    replacements = {
        row["parent"]: row
        for row in changes
        if row["kind"] == "geometry" and row["relation"] == "replacement"
    }
    for row in read("duplicate-decisions.json")["decisions"]:
        if not row["action"].startswith("exclude"):
            continue
        retained = parents[row["retain"]]
        assert retained.get("owner_interpreted_action") != "exclude", row["retain"]
        replacement = replacements.get(row["retain"])
        changes.append(
            {
                "id": row["remove"],
                "parent": row["remove"],
                "kind": "duplicate_exclusion",
                "states": [],
                "retain": row["retain"],
                "note": row["reason"],
                "before": parents[row["remove"]]["crop_path"],
                "after": replacement["after"] if replacement else retained["crop_path"],
                "retained_candidate": replacement["id"] if replacement else row["retain"],
                "source": parents[row["remove"]]["source_path"],
                "owner_approved": False,
            }
        )
    dispositions = (
        read("source-dispositions.json") if (HERE / "source-dispositions.json").exists() else []
    )
    for disposition_path in sorted(HERE.glob("closeout-source-decisions*.json")):
        dispositions += [
            {**row, "action": "propose_exclusion"} for row in read(disposition_path.name)
        ]
    assert len({r["id"] for r in dispositions}) == len(dispositions)
    for disposition in dispositions:
        assert disposition["action"] == "propose_exclusion"
        parent = parents[disposition["id"]]
        assert disposition["id"] not in replacements
        assert sha((ROOT / parent["crop_path"]).read_bytes()) == parent["crop_sha256"]
        parent["source_disposition"] = {
            **disposition,
            "owner_approved": False,
            "crop_sha256": parent["crop_sha256"],
        }
        changes.append(
            {
                "id": disposition["id"],
                "parent": disposition["id"],
                "kind": "source_exclusion",
                "states": [],
                "note": disposition["reason"],
                "before": parent["crop_path"],
                "after": parent["source_path"],
                "after_caption": "Ảnh nguồn — đề xuất rút crop",
                "source": parent["source_path"],
                "owner_approved": False,
            }
        )
    dump(HERE / "geometry-review.json", geometries)
    dump(HERE / "resolved-ledger.json", ledger)
    dump(HERE / "delta-review.json", changes)
    passed_parents = set(replacements)
    owner_resolutions = (
        read("owner-request-resolutions.json")
        if (HERE / "owner-request-resolutions.json").exists()
        else []
    )
    passed_ids = {r["id"] for r in changes if r["kind"] == "geometry"}
    assert len({r["id"] for r in owner_resolutions}) == len(owner_resolutions)
    for resolution in owner_resolutions:
        assert resolution["complete"] is True
        assert set(resolution["outputs"]) <= passed_ids, resolution["id"]
        for existing in resolution.get("covered_existing", []):
            assert parents[existing]["owner_interpreted_action"] != "exclude", existing
        parents[resolution["id"]]["owner_request_resolution"] = resolution
    closed_owner_requests = {r["id"] for r in owner_resolutions}
    dump(HERE / "resolved-ledger.json", ledger)
    removed_parents = {
        r["parent"] for r in changes if r["kind"] in {"duplicate_exclusion", "source_exclusion"}
    }
    resolved_labels = {r["id"] for r in label_resolutions if not r.get("geometry_followup")}
    remaining = {
        "note": (
            "Hàng đợi theo parent; trial thất bại đã có bản pass không tính lại. "
            "Không thay nghiệm thu."
        ),
        "recrop_requests": [
            r["id"]
            for r in ledger
            if r["owner_import_status"] == "approved_recrop_request"
            and r["id"] not in passed_parents | removed_parents
        ],
        "owner_interpretations": [
            r["id"]
            for r in ledger
            if r["owner_import_status"] in {"needs_interpretation", "owner_reinclude_needs_qa"}
            and r["id"]
            not in passed_parents | removed_parents | resolved_labels | closed_owner_requests
        ],
        "label_geometry_followup": [
            r["id"]
            for r in label_resolutions
            if r.get("geometry_followup") and r["id"] not in passed_parents | removed_parents
        ],
    }
    dump(HERE / "remaining-work.json", remaining)
    summary = {
        "status": "in_progress",
        "input_records": len(ledger),
        "broad_scan_records": 907,
        "new_geometry_trials": len(geometries),
        "geometry_qa": dict(Counter(r["qa_status"] for r in geometries)),
        "delta_rows": len(changes),
        "manual_label_resolutions": len(label_resolutions),
        "new_label_review_rows": sum(r["kind"] == "label_change" for r in changes),
        "pixel_and_hash_verified_ids": checks,
        "additional_marked_images": 41,
        "additional_crop_proposals_complete": False,
        "all_recrops_complete": False,
        "all_duplicates_complete": False,
        "accepted_release_modified": False,
    }
    dump(HERE / "progress-summary.json", summary)
    cards = []
    for row in changes:
        display_source = browser_source(row["source"])
        display_after = browser_source(row["after"])
        title = html.escape(row["id"])
        label = "/".join(row["states"]) or (
            "Đề xuất rút crop" if row["kind"] == "source_exclusion" else "Đề xuất loại trùng"
        )
        note = html.escape(row["note"])
        after_caption = html.escape(
            row.get(
                "after_caption", row.get("retained_candidate", row.get("retain", "Đề xuất mới"))
            )
        )
        extra = (
            f'<figure><img src="{link(row["input"])}"><figcaption>Input 224</figcaption></figure>'
            if row.get("input")
            else ""
        )
        cards.append(f'''<article data-kind="{row["kind"]}"><h2>{title} · {label}</h2>
<p>{note}</p><div class="images">
<figure><img src="{link(row["before"])}">
<figcaption>{html.escape(row.get("before_caption", "Trước"))}</figcaption></figure>
<figure><img src="{link(display_after)}">
<figcaption>{after_caption}</figcaption></figure>
{extra}</div><a href="{link(display_source)}">Ảnh nguồn</a></article>''')
    page = (
        """<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hợp nhất audit crop — đang xử lý</title>
<style>body{font:16px system-ui;margin:24px;background:#f3f5f8;color:#172033}
article{background:white;padding:20px;margin:20px 0;border:1px solid #ccd3dd;border-radius:10px}
h2{font-size:18px}.images{display:flex;gap:18px;flex-wrap:wrap}figure{margin:0}
img{max-width:440px;max-height:420px;object-fit:contain}figcaption{padding:8px}
.notice{background:#fff0c2;padding:16px}button{padding:10px;margin:8px}</style>
<h1>Hợp nhất review 836 crop và YouTube</h1>
<p class="notice">Đang xử lý. Đây là phần thay đổi đã kiểm tra đến checkpoint hiện tại,
chưa phải batch hoàn tất. Chưa xử lý xong toàn bộ recrop, duplicate và additional.zip.
Các crop approved không thay đổi không xuất hiện ở đây. Accepted V11 giữ nguyên.</p>
<button onclick="filter('all')">Tất cả thay đổi</button>
<button onclick="filter('geometry')">Crop mới / sửa</button>
<button onclick="filter('label_change')">Thay đổi nhãn</button>
<button onclick="filter('duplicate_exclusion')">Đề xuất loại trùng</button>
<button onclick="filter('source_exclusion')">Không tìm được crop thay thế đạt</button>
"""
        + "\n".join(cards)
        + """<script>function filter(k){document.querySelectorAll('article').forEach(
e=>e.hidden=k!=='all'&&e.dataset.kind!==k)}</script></html>"""
    )
    (MEDIA / "index.html").write_text(page, encoding="utf-8")
    report = f"""# Hợp nhất audit crop — đang xử lý

Inputs: 836 crop legacy, 71 crop YouTube và 41 ảnh marked trong additional.zip.
Owner mặc định approved nếu không nhận xét; snapshots và SHA ở `owner-inputs/` và `input-pins.json`.

- Đã rà tổng thể 907 crop; chưa coi là hoàn tất QA chi tiết.
- Đã tạo {len(geometries)} phương án geometry; {len(checks)} bản qua QA Draft và kiểm pixel/hash.
- Gallery hiện có {len(changes)} thay đổi, bao gồm đề xuất loại trùng;
  không đưa approved không đổi vào review.
- Đã đối chiếu thêm {len(label_resolutions)} nhận xét nhãn với source/native/input;
  `resolved-ledger.json` giữ kết quả gắn đúng crop SHA, không tự nghiệm thu geometry mới.
- Chưa hoàn tất toàn bộ recrop, duplicate, nhãn và người marked bổ sung. Không có release mới.

[Mở gallery đang xử lý](../../../data/interim/crop-review-consolidation-20261019/index.html).
Chi tiết: `delta-review.json`, `geometry-review.json`, `duplicate-decisions.json`,
`qa-checkpoint.json`, các file `qa-*.json` và `progress-summary.json`.

Nguồn gốc được kiểm SHA; crop mới được đối chiếu từng pixel với vùng cắt nguồn,
input được kiểm SHA. Canonical targets vẫn pending, mask 0; không enroll train/val/test.
Gallery này chưa là yêu cầu nghiệm thu cuối cùng.
"""
    (HERE / "README.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
