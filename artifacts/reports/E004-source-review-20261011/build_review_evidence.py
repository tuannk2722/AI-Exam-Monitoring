"""Serialize human visual triage and explicit draft geometry; never release acceptance."""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path("data/interim/E004-source-review-20261011")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


def build(output):
    sources = {
        s: json.loads((ROOT / (s + "-inspection.json")).read_text(encoding="utf-8"))
        for s in ("behavie", "studentclassroombehavior")
    }
    families = {
        "BEH-bright-worktables": (
            "Phòng sáng, bàn gỗ rộng, cửa sổ bên phải; lớp nguồn phone có box vùng đầu/thân.",
            "holdout_candidate_reserve",
        ),
        "BEH-blue-cctv": (
            "Ghế/bàn xanh, camera góc cao; timestamp cùng ngày 2016 trong các frame đã xem.",
            "holdout_candidate_reserve",
        ),
        "BEH-rear-cctv": (
            "Camera phía sau lớp đông, bàn gỗ; thiết bị rất nhỏ, nhiều anchor.",
            "holdout_candidate_reserve",
        ),
        "BEH-chair-staging": (
            "Ghế gỗ có bàn viết, cảnh diễn người lớn; gom thận trọng các góc/sàn khác nhau, chưa xác minh phòng/session.",
            "holdout_candidate_reserve",
        ),
        "BEH-yellow-flags": (
            "Tường vàng, cờ dây, bàn gỗ nhỏ, cửa chớp; nhiều tư thế viết/ngẩng/nhìn ngang.",
            "holdout_candidate_reserve",
        ),
        "BEH-worn-benches": (
            "Tường vàng cũ, bàn ghế dài; gom thận trọng các bố trí/nhóm người/góc quay có quan hệ chưa rõ.",
            "holdout_candidate_reserve",
        ),
        "STU-gray-train": (
            "Cảnh tường xám, cửa sổ xanh bên phải, bàn gỗ; đã đối chiếu cùng cảnh train V7.",
            "train_supplement_candidate",
        ),
        "STU-overhead-train": (
            "Cảnh camera cao, bàn vàng, cửa sổ xanh; đã đối chiếu cùng cảnh train V7.",
            "train_supplement_candidate",
        ),
        "STU-theater-train": (
            "Dãy ghế gỗ dạng giảng đường; ảnh mở rộng đã đối chiếu cùng cảnh train V7.",
            "train_supplement_candidate",
        ),
    }
    beh = [
        "BEH-bright-worktables",
        "BEH-blue-cctv",
        "BEH-rear-cctv",
        "BEH-chair-staging",
        "BEH-yellow-flags",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-yellow-flags",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-yellow-flags",
        "BEH-yellow-flags",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-worn-benches",
    ]
    beh += ["BEH-chair-staging"] * 7 + ["BEH-blue-cctv"]
    beh += (
        ["BEH-worn-benches", "BEH-blue-cctv", "BEH-worn-benches"]
        + ["BEH-blue-cctv"] * 4
        + ["BEH-worn-benches"]
    )
    beh += ["BEH-worn-benches"] * 14 + ["BEH-yellow-flags", "BEH-worn-benches"]
    beh += ["BEH-worn-benches"] * 3 + [
        "BEH-yellow-flags",
        "BEH-worn-benches",
        "BEH-worn-benches",
        "BEH-yellow-flags",
        "BEH-worn-benches",
    ]
    assert len(beh) == 60
    stu = []
    for i in range(60):
        if i in [0, 2, 3, 5, 6, 20, 22, 29, 30, 37]:
            stu.append("STU-gray-train")
        elif i in [
            1,
            4,
            7,
            8,
            9,
            10,
            11,
            21,
            23,
            24,
            25,
            26,
            27,
            31,
            32,
            33,
            34,
            35,
            36,
            38,
            39,
            40,
            41,
            42,
            43,
        ]:
            stu.append("STU-overhead-train")
        elif i == 28:
            stu.append("STU-theater-train")
        else:
            # A view identifier is not a verified distinct video/person/session/room.
            stu.append(f"STU-instructional-view-{i:02d}")
            families[stu[-1]] = (
                "Video lớp học hướng dẫn, cảnh riêng trong lượt xem; quan hệ giữa video/room/session chưa xác minh.",
                "new_development_candidate_quarantine",
            )
    parents = {
        "STU-gray-train": ["V6-SB-005", "V6R2-SB-006"],
        "STU-overhead-train": ["V6-SB-012", "V6R2-SB-011"],
        "STU-theater-train": ["V6-SB-008", "V6R2-MP-048"],
    }
    old = [
        json.loads(x)
        for x in Path("data/processed/pilot-b/pilot-b-20261010-v7/manifest.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    parent_by_id = {x["sample_id"]: x for x in old}
    assessments = []
    for s, tags in (("behavie", beh), ("studentclassroombehavior", stu)):
        for index, (row, family) in enumerate(zip(sources[s], tags, strict=True)):
            description, role = families[family]
            hint = row["priority_hint"]
            if s == "behavie" and hint == "phone":
                feasibility = "Cần vẽ person/context ngoài box thiết bị/đầu nguồn; có cơ hội phone P, phải xác nhận mobile và ownership tại crop/input 224."
            elif s == "behavie" and hint == "Normal":
                feasibility = "Nhãn Normal không xác nhận N: một số anchor đang cầm vật dạng thiết bị; review riêng mobile/hand/workarea/gaze."
            elif hint in {"Hand Under Table", "Bend Over The Desk"}:
                feasibility = "Có giá trị posture/occlusion contrast; tay dưới bàn giữ phone U, không dùng absence annotation làm N."
            elif hint in {"Look Around", "turn_head"}:
                feasibility = "Tìm anchor nhìn ngang và anchor viết cùng cảnh; chỉ đầu nghiêng hoặc source head box chưa đủ looking P."
            else:
                feasibility = "Book/pen/hand-to-face có ích cho contextual negative; reading/writing chỉ hint, back view hoặc thiếu vùng tay giữ U."
            quality = []
            if s == "studentclassroombehavior" and index >= 12:
                quality += ["upstream_export_quality_and_video_overlay_review"]
            if s == "studentclassroombehavior" and index in [18, 49]:
                quality += ["prominent_player_or_watermark_overlay"]
            if s == "studentclassroombehavior" and index == 55:
                quality += ["source_writing_box_on_background_semantic_error"]
                role = "semantic_quarantine_no_crop_selected"
            assessments.append(
                {
                    **{
                        k: row[k]
                        for k in (
                            "review_id",
                            "source_id",
                            "source_sha256",
                            "member_sha256",
                            "label_sha256",
                            "archive_sha256",
                            "original_split",
                            "priority_hint",
                            "selection",
                            "size",
                            "source_class_hints",
                        )
                    },
                    "review_index": index,
                    "visual_review": "completed_by_agent_no_candidate_scores",
                    "observed_scene_description": description,
                    "draft_scene_boundary": family,
                    "draft_role": role,
                    "crop_feasibility": feasibility,
                    "quality_flags": quality,
                    "confirmed_parent_scene_overlap": family in parents,
                    "parent_scene_evidence": [
                        {
                            "sample_id": p,
                            "source_sha256": parent_by_id[p]["source"]["image_sha256"],
                            "usage": parent_by_id[p]["usage"],
                        }
                        for p in parents.get(family, [])
                    ],
                    "scope_of_overlap_evidence": "shared_scene_visual_evidence_not_identity_inference"
                    if family in parents
                    else "nearest_non_test_comparisons_not_exhaustive_disjointness_proof",
                    "original_shortlist40": index < 20,
                    "canonical_targets": [None, None],
                    "canonical_mask": [0, 0],
                    "video_id": None,
                    "session_id": None,
                    "room_id": None,
                    "subject_id": None,
                    "independence_proven": False,
                    "owner_batch_accepted": False,
                    "test_candidate_eligibility": "ineligible_known_train_scene"
                    if family in parents
                    else "pending_provenance_crop_qa_and_owner_assignment",
                }
            )
    write(output / "inspection-assessment120.json", assessments)
    write(
        output / "shortlist40-assessment.json",
        [x for x in assessments if x["original_shortlist40"]],
    )
    family_summary = []
    for family, (description, role) in families.items():
        rows = [x for x in assessments if x["draft_scene_boundary"] == family]
        family_summary.append(
            {
                "draft_boundary": family,
                "description": description,
                "role_proposal": role,
                "image_count": len(rows),
                "original40_count": sum(x["original_shortlist40"] for x in rows),
                "review_ids": [x["review_id"] for x in rows],
                "confirmed_train_overlap": family in parents,
                "evidenced_independent_groups": 0,
                "owner_accepted": False,
            }
        )
    write(output / "scene-family-review.json", family_summary)

    # Boxes were drawn from visual coordinate grids; normalized values are authoring units, not thresholds.
    # Person rectangles cover visible anchor regions, context adds observed desks/devices/neighbours.
    specs = []

    def add(s, i, person, context, states, phenotype, reason):
        row = sources[s][i]
        family = (beh if s == "behavie" else stu)[i]
        w, h = row["size"]

        def pixels(box):
            return [round(v * (w if j % 2 == 0 else h) / 1000) for j, v in enumerate(box)]

        specs.append(
            {
                "candidate_id": f"E004-CN-{len(specs) + 1:03d}",
                "source_id": s,
                "review_id": row["review_id"],
                "source_sha256": row["source_sha256"],
                "member_sha256": row["member_sha256"],
                "person_xyxy": pixels(person),
                "context_xyxy": pixels(context),
                "draft_states": list(states),
                "phenotype": phenotype,
                "reason": reason,
                "draft_scene_boundary": family,
                "role_proposal": families[family][1],
                "owner_approved": False,
            }
        )

    b = "behavie"
    t = "studentclassroombehavior"
    own = "Tay và vùng bài riêng có thể quan sát, đang viết/đọc; đề xuất N/N phải owner xác nhận absence mobile và gaze tại exact crop."
    side = "Đầu hướng về anchor/bên cạnh, context giữ vùng bài riêng; phone chưa đủ evidence thì U."
    device = "Thiết bị dạng mobile gắn với tay/bàn của anchor; kiểm lại phân biệt mobile và ownership tại 224."
    add(
        b,
        0,
        [435, 440, 505, 665],
        [415, 420, 545, 700],
        ("U", "N"),
        "small_device_or_book",
        "Vật nhỏ ở tay/bàn chưa phân biệt chắc mobile; không map phone nguồn sang P.",
    )
    add(
        b,
        0,
        [540, 445, 620, 665],
        [510, 425, 655, 700],
        ("U", "U"),
        "crowded_shared_worktable",
        "Thiếu evidence absence mobile và gaze so vùng bài; giữ U/U làm review phụ.",
    )
    add(b, 3, [388, 5, 710, 985], [365, 0, 735, 1000], ("P", "N"), "handheld_phone_control", device)
    add(b, 4, [300, 405, 415, 1000], [250, 375, 460, 1000], ("U", "P"), "side_gaze_workarea", side)
    add(b, 4, [420, 385, 565, 965], [390, 350, 600, 980], ("N", "N"), "own_paper_pen", own)
    add(b, 4, [650, 465, 800, 1000], [600, 430, 850, 1000], ("N", "N"), "own_paper_pen", own)
    add(
        b,
        5,
        [145, 415, 330, 975],
        [125, 380, 415, 1000],
        ("N", "P"),
        "side_gaze_versus_writing",
        side + " Hai tay/vùng giấy nhìn thấy.",
    )
    add(b, 5, [570, 405, 735, 930], [535, 370, 790, 975], ("N", "N"), "own_paper_pen", own)
    add(b, 5, [250, 320, 385, 515], [225, 285, 435, 560], ("N", "N"), "own_paper_pen", own)
    add(
        b,
        8,
        [240, 485, 375, 905],
        [205, 450, 420, 965],
        ("U", "U"),
        "hand_to_chin_and_small_object",
        "Một tay chống cằm, tay kia giữ vật nhỏ; vật/gaze chưa chắc, không nhận Normal là N.",
    )
    add(
        b,
        8,
        [550, 460, 695, 905],
        [505, 435, 750, 965],
        ("U", "N"),
        "hands_on_small_object",
        "Hai tay gần vật nhỏ trên bàn; mobile chưa rõ, looking về vùng tay đề xuất N.",
    )
    add(
        b,
        8,
        [415, 310, 515, 490],
        [380, 280, 555, 535],
        ("U", "N"),
        "far_anchor_workarea",
        "Anchor xa, tay/vật nhỏ chưa đủ phone evidence.",
    )
    add(b, 10, [425, 385, 560, 965], [390, 350, 600, 990], ("N", "N"), "own_paper_pen", own)
    add(b, 10, [650, 475, 800, 1000], [600, 440, 850, 1000], ("N", "N"), "own_paper_pen", own)
    add(
        b,
        10,
        [160, 275, 285, 755],
        [125, 245, 335, 795],
        ("U", "P"),
        "peer_gaze_and_occluded_hand",
        side,
    )
    add(b, 12, [395, 380, 500, 555], [350, 355, 555, 615], ("N", "N"), "bent_writing_negative", own)
    add(
        b,
        13,
        [440, 470, 510, 610],
        [410, 445, 555, 650],
        ("U", "N"),
        "far_bent_anchor",
        "Anchor xa/desk che phần tay; không source phone box không là N.",
    )
    add(
        b,
        13,
        [550, 475, 645, 625],
        [525, 450, 680, 665],
        ("U", "N"),
        "far_bent_anchor",
        "Nhìn xuống vùng bài, phone absence không quan sát đủ.",
    )
    add(
        b,
        16,
        [160, 400, 335, 970],
        [120, 370, 425, 1000],
        ("U", "P"),
        "peer_gaze_and_hand_occlusion",
        side,
    )
    add(
        b,
        16,
        [590, 395, 740, 960],
        [545, 355, 790, 990],
        ("U", "P"),
        "hand_under_table",
        "Tay dưới bàn và đầu hướng sang bên; phone giữ U.",
    )
    add(b, 16, [270, 350, 390, 555], [230, 310, 445, 595], ("N", "N"), "own_paper_pen", own)
    add(
        b,
        20,
        [355, 260, 605, 1000],
        [315, 230, 645, 1000],
        ("P", "P"),
        "phone_and_peer_gaze",
        device + " Đầu quay sang người bên cạnh.",
    )
    add(
        b,
        20,
        [650, 280, 1000, 1000],
        [610, 255, 1000, 1000],
        ("P", "P"),
        "phone_and_peer_gaze",
        device + " Đầu quay sang người bên cạnh.",
    )
    add(
        b,
        20,
        [25, 245, 275, 1000],
        [0, 220, 315, 1000],
        ("P", "U"),
        "handheld_phone_back_view",
        device + " Back view không đủ gaze.",
    )
    add(
        b,
        21,
        [320, 430, 645, 1000],
        [290, 355, 875, 1000],
        ("N", "N"),
        "foreign_mobile_ownership_negative",
        own + " Context có mobile của hàng ghế phía sau; không gán cho foreground anchor.",
    )
    add(
        b,
        21,
        [265, 115, 490, 565],
        [235, 90, 535, 630],
        ("P", "N"),
        "handheld_phone_control",
        device,
    )
    add(
        b,
        21,
        [600, 205, 825, 665],
        [560, 175, 855, 710],
        ("P", "N"),
        "handheld_phone_control",
        device,
    )
    add(b, 22, [320, 115, 605, 925], [285, 90, 655, 950], ("P", "N"), "desk_phone_control", device)
    add(b, 22, [0, 250, 270, 1000], [0, 220, 325, 1000], ("P", "N"), "desk_phone_control", device)
    add(
        b,
        22,
        [720, 200, 1000, 940],
        [690, 175, 1000, 965],
        ("P", "N"),
        "desk_phone_control",
        device,
    )
    add(
        b, 37, [135, 405, 320, 1000], [105, 375, 400, 1000], ("N", "N"), "writing_hand_visible", own
    )
    add(b, 37, [575, 340, 735, 970], [530, 315, 790, 1000], ("N", "N"), "writing_hand_visible", own)
    add(
        b,
        44,
        [575, 520, 735, 930],
        [530, 460, 790, 980],
        ("U", "U"),
        "head_down_occlusion",
        "Đầu và vùng tay bị che bởi tư thế cúi; U/U auxiliary, không supervision.",
    )
    add(b, 44, [145, 415, 335, 1000], [115, 380, 405, 1000], ("N", "N"), "own_paper_pen", own)
    add(
        b,
        50,
        [290, 400, 410, 1000],
        [250, 365, 465, 1000],
        ("N", "P"),
        "peer_gaze_contrast",
        side + " Tay/vùng giấy đủ review draft N.",
    )
    add(b, 50, [645, 345, 810, 1000], [595, 315, 855, 1000], ("U", "P"), "upright_peer_gaze", side)
    add(b, 50, [155, 275, 290, 750], [120, 245, 340, 795], ("N", "N"), "own_paper_pen", own)
    add(
        t,
        0,
        [450, 665, 610, 1000],
        [425, 630, 655, 1000],
        ("P", "N"),
        "handheld_phone_control",
        device,
    )
    add(
        t,
        0,
        [160, 590, 310, 1000],
        [115, 565, 355, 1000],
        ("U", "P"),
        "hand_to_chin_peer_gaze",
        side,
    )
    add(
        t,
        1,
        [675, 685, 790, 870],
        [625, 650, 835, 935],
        ("P", "N"),
        "small_desk_phone_control",
        device,
    )
    add(
        t,
        1,
        [310, 565, 450, 800],
        [285, 535, 495, 850],
        ("N", "N"),
        "foreign_mobile_crowded_workarea",
        own + " Crop chứa lân cận: ownership không theo nearest phone.",
    )
    add(
        t,
        12,
        [290, 485, 415, 760],
        [265, 450, 465, 825],
        ("U", "P"),
        "hand_raise_forward_gaze",
        side + " Nhìn về người ở phía trước, source writing không quyết định target.",
    )
    add(
        t,
        12,
        [40, 745, 245, 1000],
        [20, 710, 310, 1000],
        ("U", "N"),
        "book_writing_occlusion",
        "Vùng bài riêng rõ, tay/desk một phần bị che; phone U.",
    )
    add(
        t,
        13,
        [280, 435, 520, 1000],
        [250, 405, 600, 1000],
        ("U", "P"),
        "hand_to_face_peer_gaze",
        side,
    )
    add(t, 13, [500, 435, 725, 1000], [465, 405, 830, 1000], ("N", "N"), "book_pen_negative", own)
    add(
        t,
        16,
        [590, 785, 790, 1000],
        [540, 740, 855, 1000],
        ("U", "N"),
        "book_negative_occluded_hands",
        "Đang đọc sách; không coi sách/reading là phone N khi thiếu tay.",
    )
    add(t, 16, [575, 545, 695, 745], [525, 505, 750, 820], ("U", "P"), "peer_teacher_gaze", side)
    add(
        t,
        44,
        [490, 50, 800, 1000],
        [450, 20, 835, 1000],
        ("N", "N"),
        "book_held_in_both_hands",
        own,
    )
    add(
        t,
        44,
        [115, 625, 310, 1000],
        [85, 585, 355, 1000],
        ("U", "N"),
        "book_negative_partial_workarea",
        "Cúi đọc/viết, phần bàn bị crop biên nên phone U.",
    )
    add(
        t,
        53,
        [55, 485, 360, 1000],
        [35, 450, 405, 1000],
        ("N", "N"),
        "pen_pencilcase_negative",
        own,
    )
    add(
        t,
        53,
        [425, 515, 660, 890],
        [375, 465, 735, 980],
        ("N", "N"),
        "pen_pencilcase_negative",
        own,
    )
    add(
        t,
        54,
        [450, 65, 1000, 1000],
        [410, 40, 1000, 1000],
        ("N", "U"),
        "writing_face_occluded",
        "Bút/giấy/tay của anchor rõ; tóc che hướng nhìn nên looking U.",
    )
    add(t, 54, [350, 300, 705, 830], [315, 265, 740, 900], ("N", "N"), "pen_negative", own)
    add(
        t,
        59,
        [210, 460, 815, 1000],
        [175, 430, 850, 1000],
        ("U", "U"),
        "extreme_head_down_occlusion",
        "Đầu/vùng tay crop biên che evidence; không ép writing sang N/N.",
    )
    add(t, 59, [280, 155, 540, 575], [245, 115, 590, 645], ("N", "N"), "crowded_own_paper", own)
    write(
        output / "pilot-geometry.json",
        {
            "status": "draft_pending_exact_crop_input_review_and_owner_acceptance",
            "target_order": ["phone_use", "looking_around"],
            "input_size": 224,
            "fill": [124, 116, 104],
            "source_inventory_root": str(ROOT).replace("\\", "/"),
            "candidates": specs,
        },
    )
    write(
        output / "triage-summary.json",
        {
            "inspected_sources": len(assessments),
            "original_shortlist_sources": 40,
            "expanded_sources": 80,
            "confirmed_train_scene_sources": sum(
                x["confirmed_parent_scene_overlap"] for x in assessments
            ),
            "confirmed_train_scene_original40": sum(
                x["confirmed_parent_scene_overlap"] and x["original_shortlist40"]
                for x in assessments
            ),
            "role_proposals": dict(Counter(x["draft_role"] for x in assessments)),
            "draft_crop_count": len(specs),
            "proven_independent_groups": 0,
            "accepted_new_train": 0,
            "accepted_new_development": 0,
            "accepted_new_holdout": 0,
            "all_canonical_targets_null_mask_zero": True,
        },
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/reports/E004-source-review-20261011")
    )
    build(parser.parse_args().output)
