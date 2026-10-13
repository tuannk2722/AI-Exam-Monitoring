"""Exact-crop blinded visual QA companion; initial drafts remain available."""

import argparse
import json
from collections import Counter
from pathlib import Path

from ai_exam_monitoring.common.provenance import sha256_file

ROOT = Path("data/interim/E004-source-review-20261011")
REPORT = Path("artifacts/reports/E004-source-review-20261011")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def finalize(output):
    batches = [("pilot", json.loads((ROOT / "pilot/batch.json").read_text(encoding="utf-8"))),
               ("pilot-followup", json.loads((ROOT / "pilot-followup/batch.json").read_text(encoding="utf-8")))]
    changes = {
        1: ("PP", "Mobile trên bàn dưới tay anchor nhìn rõ; đầu quay sang bên ngoài vùng bài."),
        3: ("PP", "Mobile ở tay rõ, gaze hướng bên trái ngoài bàn riêng; bỏ looking N ban đầu."),
        10: ("UN", "Mắt hướng xuống vật ở tay/bàn riêng; vật nhỏ chưa phân biệt chắc mobile."),
        14: ("NP", "Cả hai tay/vùng giấy quan sát được; đầu hướng sang bên, không giữ looking N."),
        17: ("UU", "Tay dưới bàn, thiếu bài/đích nhìn và gaze cụ thể; không chỉ từ cúi đầu suy N."),
        18: ("UU", "Desk che tay/đích nhìn, hướng đầu đơn thuần chưa đủ looking state."),
        25: ("UU", "Native cho thấy tay nằm dưới bàn, không đang viết như draft; phone U, gaze/workarea thiếu."),
        26: ("UN", "Thiết bị có thể mobile/tablet, chưa chốt category từ ảnh; mắt về thiết bị riêng."),
        28: ("PP", "Mobile trên bàn riêng rõ; đầu/gaze sang bên, không nhìn vùng bài riêng."),
        29: ("PP", "Mobile ở tay/bàn riêng; đầu/gaze hướng sang bên ngoài vùng bài."),
        30: ("PP", "Mobile dưới tay anchor rõ; đầu quay sang bên ngoài vùng bài."),
        32: ("NP", "Hai tay/vùng giấy quan sát được; đầu sang bên, không phải looking N."),
        36: ("NP", "Hai tay trên giấy/bàn rõ; đầu quay sang bên ngoài giấy riêng."),
        40: ("UU", "Mobile nhỏ/partial không đủ phân biệt tại 224; tóc che gaze, không tự lấy posture làm N."),
        43: ("UU", "Back/side view tóc che mắt; vùng tay/bài bị biên crop, không ép writing thành N."),
        44: ("NP", "Tay chống mặt và tay giữ bút/giấy rõ; head/gaze sang ngoài vùng bài riêng."),
        45: ("NP", "Hai tay/vùng bài đủ phone draft N; head hướng phía trước/ngoài bài, không giữ looking N."),
        47: ("UN", "Native/crop là anchor đọc sách giơ trước mặt; không phải nhìn sang teacher như draft."),
        49: ("UU", "Crop biên thiếu tay/bài; không giữ looking N chỉ từ cúi đầu."),
        51: ("UU", "Pencilcase/tư thế che tay và gaze, low-detail tại 224; giữ U/U."),
    }
    rows = []
    for directory, batch in batches:
        for original in batch["candidates"]:
            row = dict(original)
            ident = row["candidate_id"]
            old = "".join(row["draft_states"])
            reviewed, reason = old, row["draft_reason"]
            status = "proposed_for_owner_batch_acceptance"
            geometry = "anchor_and_context_reviewed"
            if ident in {"E004-CN-002", "E004-CN-041"}:
                status = "superseded_use_R2_only"
                if ident.endswith("041"):
                    geometry = "rejected_anchor_head_missing"
                reviewed = "UU"
                reason = "Giữ original để trace QA; chỉ review revision R2, không đếm hai lần."
            elif ident == "E004-CN-002-R2":
                reviewed, reason = "NP", "Hai tay/bàn riêng rõ; mobile phía trái gắn với anchor khác. Gaze ngoài bàn riêng."
            elif ident == "E004-CN-041-R2":
                reviewed, reason = "PU", "Mobile đen trên giấy/bàn riêng nhìn thấy, cạnh chai hồng; tóc che gaze tại 224 nên looking U."
            elif ident == "E004-CN-056":
                reviewed, reason = "NN", "Bút/giấy và hai tay anchor rõ, head/face nhìn về giấy; contrast với foreground nhìn ra ngoài bài."
            else:
                number = int(ident.rsplit("-", 1)[-1])
                if number in changes:
                    reviewed, reason = changes[number]
            if reviewed == "UU" and not status.startswith("superseded"):
                status = "auxiliary_unknown_not_supervision"
            row.update({"reviewed_draft_states": list(reviewed), "input224_qa": "completed_blinded_visual_review",
                        "geometry_qa": geometry, "qa_reason": reason, "qa_reviewer": "agent-draft-review",
                        "qa_date": "2026-10-11", "decision_proposal": status, "media_directory": str(ROOT / directory / ident).replace("\\", "/"),
                        "changed_since_initial_state": old != reviewed, "canonical_targets": [None,None], "canonical_mask": [0,0],
                        "owner_approved": False, "split": None, "independence_proven": False,
                        "source_to_native_crop_to_input224_reviewed": True})
            folder = ROOT / directory / ident
            assert sha256_file(folder / "crop.png") == row["crop_sha256"]
            assert sha256_file(folder / "input.png") == row["input_sha256"]
            rows.append(row)
    active = [r for r in rows if not r["decision_proposal"].startswith("superseded")]
    proposed = [r for r in active if r["decision_proposal"] == "proposed_for_owner_batch_acceptance"]
    write(output / "pilot-input224-review.json", rows)
    summary = {"artifact_crop_versions": len(rows), "active_anchor_candidates": len(active),
               "source_images": len({r["source_sha256"] for r in active}),
               "reviewed_at_224": len(rows), "proposed_at_least_one_known_target": len(proposed),
               "active_UU_auxiliary": len(active)-len(proposed), "superseded_versions": len(rows)-len(active),
               "proposed_state_combinations": dict(Counter("".join(r["reviewed_draft_states"]) for r in proposed)),
               "active_phone_PNU": dict(Counter(r["reviewed_draft_states"][0] for r in active)),
               "active_looking_PNU": dict(Counter(r["reviewed_draft_states"][1] for r in active)),
               "proposed_role_counts": dict(Counter(r["role_proposal"] for r in proposed)),
               "accepted_supervised_crops": 0, "accepted_independent_groups": 0,
               "canonical_null_mask_zero_for_all": True, "candidate_model_scores_used": False}
    write(output / "pilot-summary.json", summary)
    pair_specs = [("phone", "E004-CN-001", "E004-CN-002-R2", "same_image_cross_anchor_ownership"),
                  ("looking", "E004-CN-007", "E004-CN-008", "same_image_cross_anchor_side_vs_own_paper"),
                  ("looking", "E004-CN-004", "E004-CN-005", "same_image_cross_anchor_side_vs_own_paper"),
                  ("looking", "E004-CN-014", "E004-CN-013", "same_image_cross_anchor_side_vs_own_paper"),
                  ("looking", "E004-CN-032", "E004-CN-031", "same_image_cross_anchor_side_vs_own_paper"),
                  ("looking", "E004-CN-035", "E004-CN-037", "same_image_cross_anchor_side_vs_own_paper"),
                  ("looking", "E004-CN-044", "E004-CN-056", "same_image_cross_anchor_hand_to_face_vs_writing"),
                  ("looking", "E004-CN-045", "E004-CN-056", "same_image_cross_anchor_forward_vs_writing")]
    byid = {r["candidate_id"]:r for r in rows}
    pairs = []
    for target, a, b, quality in pair_specs:
        first, second = byid[a], byid[b]; axis = 0 if target == "phone" else 1
        assert first["source_sha256"] == second["source_sha256"]
        assert first["reviewed_draft_states"][axis] == "P" and second["reviewed_draft_states"][axis] == "N"
        pairs.append({"target":target, "positive_id":a, "negative_id":b, "quality":quality,
                      "source_sha256":first["source_sha256"], "positive_crop_sha256":first["crop_sha256"],
                      "negative_crop_sha256":second["crop_sha256"], "owner_accepted":False,
                      "same_person_counterfactual":False, "independent_pair":False,
                      "limitation":"Giữ scene nhưng khác anchor/vị trí, không suy causal effect hoặc independent samples."})
    write(output / "pilot-pairs.json", pairs)
    # Review entry reflects final companion states, not stale draft cards.
    import html
    parts = ['<!doctype html><meta charset="utf-8"><title>E004 final draft QA</title>',
             '<style>body{font:16px system-ui;margin:24px}article{padding:15px;border-top:1px solid #bbb}img{max-height:320px;max-width:500px;margin:4px;vertical-align:top}code{font-size:13px}</style>',
             '<h1>E004 — Kết quả QA draft để owner review batch</h1><p>Tất cả canonical targets null/mask 0, chưa split hoặc supervision. States sau QA và exceptions là đề xuất. Không cần annotate lại từng ảnh; review batch/ngoại lệ và whole-family trước acceptance.</p>']
    for r in rows:
        folder = Path(r["media_directory"]); relative = folder.relative_to(ROOT).as_posix()
        parts.append(f'<article id="{r["candidate_id"]}"><h2>{r["candidate_id"]}: {"/".join(r["reviewed_draft_states"])} — {r["decision_proposal"]}</h2><p>{html.escape(r["draft_scene_boundary"])} · {html.escape(r["role_proposal"])}</p><a href="{relative}/source.png"><img src="{relative}/source-overlay.png"></a><a href="{relative}/crop.png"><img src="{relative}/crop.png"></a><img width="224" height="224" src="{relative}/input.png"><p>{html.escape(r["qa_reason"])}</p><code>crop SHA {r["crop_sha256"]}<br>input SHA {r["input_sha256"]}</code></article>')
    (ROOT / "REVIEW.html").write_text("\n".join(parts),encoding="utf-8")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPORT)
    finalize(parser.parse_args().output)
