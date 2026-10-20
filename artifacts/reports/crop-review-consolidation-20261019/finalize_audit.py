"""Close the audit evidence; this does not accept or enroll a dataset release."""

import json
from collections import Counter

from intake import HERE, MEDIA, ROOT, dump, sha


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def main():
    ledger = read("resolved-ledger.json")
    delta = read("delta-review.json")
    cohort = read("effective-draft-cohort-post.json")
    slots = read("additional-final-slots.json")
    remaining = read("remaining-work.json")
    for key in ("recrop_requests", "owner_interpretations", "label_geometry_followup"):
        assert not remaining[key], key
    assert len(ledger) == len({r["id"] for r in ledger}) == 907
    assert len(delta) == len({r["id"] for r in delta})
    assert len(slots["frames"]) == 41
    assert all(s["audit_complete"] for f in slots["frames"] for s in f["slots"])
    members = {r["id"]: r for r in cohort}
    assert len(members) == len(cohort)
    assert len({r["rgb_sha"] for r in cohort}) == len(cohort), "Exact RGB duplicate"
    for pin in read("input-pins.json"):
        assert sha((ROOT / pin["source"]).read_bytes()) == pin["sha256"]
        if "snapshot" in pin:
            assert sha((ROOT / pin["snapshot"]).read_bytes()) == pin["sha256"]
    youtube_pins = {
        r["candidate_id"]: r
        for r in json.loads(
            (HERE.parent / "youtube-frame-audit-20261018" / "review-index.json").read_text(
                encoding="utf-8"
            )
        )
    }
    verified_sources = set()
    for row in ledger + read("additional-parents.json"):
        if row["source_path"] not in verified_sources:
            expected_source = row.get("source_sha256") or youtube_pins[row["id"]]["source_sha256"]
            assert sha((ROOT / row["source_path"]).read_bytes()) == expected_source, row["id"]
            verified_sources.add(row["source_path"])
        expected = row.get("crop_sha256", row.get("reference_sha256"))
        assert sha((ROOT / row["crop_path"]).read_bytes()) == expected, row["id"]
    reviewed = read("final-duplicate-review.json")
    assert len(reviewed["pairs"]) == 331 and reviewed["status"] == "complete"
    post = read("final-duplicate-review-post.json")
    queued = read("final-duplicate-pairs-post.json")

    def key(pair):
        return tuple(sorted((pair["a"], pair["b"])))

    assert {key(p) for p in post["pairs"]} == {key(p) for p in queued}
    assert all(p["status"] == "retain_distinct" for p in post["pairs"])
    coverage = read("source-pair-coverage-post.json")
    pair_keys = {key(p) for p in post["pairs"]}
    assert len(coverage) == 244
    for row in coverage:
        assert all(tuple(sorted(p)) in pair_keys for p in row["active_pairs"])
        row["status"] = "reviewed_distinct" if row["active_pairs"] else "no_two_retained_sides"
    dump(HERE / "source-pair-final-coverage.json", coverage)
    for frame in slots["frames"]:
        for slot in frame["slots"]:
            if slot["action"] in {"propose_candidate", "represented_by_candidate"}:
                assert slot["candidate"] in members, slot
            if slot["action"] == "covered_existing":
                assert slot["existing"] in members, slot
    for row in delta:
        if row["kind"] == "duplicate_exclusion":
            assert row["retained_candidate"] in members, row
            assert row["id"] not in members
    label_changes = {r["id"] for r in delta if r["kind"] == "label_change"}
    for row in cohort:
        assert len(row["states"]) == 2 and set(row["states"]) <= {"P", "N", "U"}
        assert row["states"] != ["U", "U"]
        row["acceptance"] = (
            "pending_owner_review"
            if row["kind"] == "proposal" or row["id"] in label_changes
            else "owner_approved_existing"
        )
    dump(HERE / "final-draft-cohort.json", cohort)
    dispositions = []
    for row in ledger:
        changes = [d for d in delta if d["parent"] == row["id"]]
        outputs = [r["id"] for r in cohort if r["parent"] == row["id"]]
        if any(d["kind"] == "duplicate_exclusion" for d in changes):
            disposition = "proposed_duplicate_exclusion"
        elif any(d["kind"] == "source_exclusion" for d in changes):
            disposition = "proposed_source_exclusion"
        elif any(d.get("relation") == "replacement" for d in changes):
            disposition = "proposed_replacement"
        elif row["owner_interpreted_action"] == "exclude":
            assert not outputs
            disposition = "owner_excluded"
        else:
            assert row["id"] in members, row["id"]
            disposition = "retained_existing"
        dispositions.append(
            {
                "id": row["id"],
                "disposition": disposition,
                "outputs": outputs,
                "review_ids": [d["id"] for d in changes],
            }
        )
    dump(HERE / "final-dispositions.json", dispositions)
    summary = read("progress-summary.json")
    summary.update(
        status="audit_complete_pending_owner_review",
        audit_complete=True,
        additional_crop_proposals_complete=True,
        all_recrops_complete=True,
        all_duplicates_complete=True,
        final_draft_members=len(cohort),
        reviewed_duplicate_pairs=331 + post["new_pairs_reviewed"],
        source_pairs_closed=len(coverage),
        marked_slots=slots["slot_count"],
        source_files_verified=len(verified_sources),
        delta_by_kind=dict(Counter(r["kind"] for r in delta)),
        dispositions=dict(Counter(r["disposition"] for r in dispositions)),
        draft_states=dict(Counter("/".join(r["states"]) for r in cohort)),
    )
    dump(HERE / "progress-summary.json", summary)
    page = MEDIA / "index.html"
    content = page.read_text(encoding="utf-8")
    content = content.replace(
        "Hợp nhất audit crop — đang xử lý", "Hợp nhất audit crop — chờ review thay đổi"
    )
    start = content.index('<p class="notice">')
    end = content.index("</p>", start) + 4
    notice = (
        f'<p class="notice">Audit hoàn tất: {len(delta)} mục cần review — '
        "168 crop mới/sửa, 3 nhãn, 20 đề xuất loại trùng và 82 đề xuất rút crop. "
        "Đã xử lý 907 crop và 83 vùng đánh dấu trong 41 ảnh bổ sung. "
        "Crop approved không đổi được ẩn. Đây là bản Draft chờ bạn duyệt thay đổi; "
        "accepted V11 chưa thay đổi. Thứ tự nhãn: phone / looking.</p>"
    )
    content = content[:start] + notice + content[end:]
    content = content.replace("img{max-width:440px;", "img{max-width:min(440px,100%);")
    page.write_text(content, encoding="utf-8")
    report = f"""# Hợp nhất audit crop — hoàn tất, chờ review thay đổi

Đã xử lý 836 crop legacy, 71 crop YouTube và 83 vùng được đánh dấu trong 41 ảnh `additional.zip`.
Hai file review của owner và ZIP vẫn khớp SHA ban đầu; crop không nhận xét được giữ approved
theo chỉ dẫn.

[Mở gallery hợp nhất](../../../data/interim/crop-review-consolidation-20261019/index.html).
Bạn chỉ cần review **{len(delta)} mục thay đổi**, gồm:

- **168 crop mới hoặc cắt lại**, trong đó 19 crop từ ảnh bổ sung.
- **3 thay đổi nhãn** cần xác nhận; 20 trường hợp nhãn đã được đối chiếu riêng với nhận xét/source.
- **20 đề xuất loại trùng**, mỗi mục hiển thị crop bỏ và bản giữ lại.
- **82 đề xuất rút crop** vì không tìm được khung thay thế đáp ứng tiêu chí; lý do từng mục có
trong gallery.

Các crop approved giữ nguyên không nằm trong danh sách review. Quyết định owner đã exclude cũng
không bị hỏi lại.
Nhãn theo thứ tự **phone / looking**; U được giữ khi bằng chứng không đủ, không biến tay khuất
thành N.
Xác nhận phone của owner cho CA001/S023 đã được áp dụng đúng phạm vi, không suy thành nghiệm thu
crop mới.

## Kết quả và kiểm tra

- 324 phương án cắt đã được xem xét; 168 bản được chọn sau QA native/input 224 và loại trùng.
- 338 cặp đã được đối chiếu trực quan: 331 cặp ban đầu và 7 cặp phát sinh sau hợp nhất.
  244 cặp nguồn tương đồng đã có kết quả; cohort Draft cuối gồm **{len(cohort)} crop**, không
còn cặp trùng pixel.
  Tương đồng không tự quyết định loại; giữ những khác biệt về vùng người, hướng đầu hoặc thao tác.
- Cả 41 ảnh bổ sung có quyết định từng vùng: đề xuất, được đại diện bởi crop có sẵn, hoặc không
đạt geometry.
  Người được đánh dấu không bắt buộc có crop.
- Hàng đợi recrop, diễn giải nhận xét và nhãn/geometry đều bằng 0. 907 records có disposition và
liên kết outputs.
- Đã kiểm SHA nguồn/crop đầu vào; bản crop được chọn khớp từng pixel với vùng nguồn và input 224
khớp pipeline.

## Hồ sơ để kiểm tra lại

- `delta-review.json`, `final-dispositions.json`, `final-draft-cohort.json`: thay đổi và trạng
thái cuối từng crop.
- `additional-final-slots.json`: đủ 83 vùng/41 ảnh, lý do và đại diện.
- `final-duplicate-review.json`, `final-duplicate-review-post.json`, `duplicate-decisions.json`:
đối chiếu trùng.
- `source-pair-final-coverage.json`, `geometry-review.json`, `qa-*.json`: nguồn và QA từng
phương án.
- `progress-summary.json`, `checkpoint-validation.json`: số lượng và kiểm tra tự động.
- `input-pins.json`, `owner-inputs/`: review gốc và provenance.

Đây là **hoàn tất audit**, chưa là nghiệm thu dataset mới. Crop/nhãn mới và đề xuất rút vẫn chờ
owner duyệt.
Các trial bị thay thế hoặc không chọn được giữ làm bằng chứng, không nằm trong cohort cuối.
Accepted V11, splits, model và E005 không thay đổi; không train, test, upload hoặc commit.
Y05 vẫn giữ lưu ý lineage của audit YouTube; chưa gán split hoặc xác nhận là nguồn độc lập.
"""
    (HERE / "README.md").write_text(report, encoding="utf-8")
    evidence = {
        name: sha((HERE / name).read_bytes())
        for name in (
            "delta-review.json",
            "resolved-ledger.json",
            "geometry-review.json",
            "final-draft-cohort.json",
            "final-dispositions.json",
            "additional-final-slots.json",
            "final-duplicate-review.json",
            "final-duplicate-review-post.json",
            "source-pair-final-coverage.json",
            "input-pins.json",
        )
    }
    dump(
        HERE / "audit-completion.json",
        {
            "status": "audit_complete_pending_owner_review",
            "evidence_sha256": evidence,
            "gallery_sha256": sha(page.read_bytes()),
            "accepted_release_modified": False,
        },
    )
    print(
        json.dumps(
            {k: v for k, v in summary.items() if k != "pixel_and_hash_verified_ids"},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
