"""Resolve reviewed marked slots against actual QA and retained owner decisions."""

import json

from intake import HERE, dump


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def main():
    ledger = {r["id"]: r for r in read("consolidated-ledger.json")}
    qa = {
        r["id"]: r
        for p in sorted(HERE.glob("qa-*.json"))
        for r in read(p.name).get("geometry_qa", [])
    }
    frames = (
        read("additional-slots-y01-part01.json")["frames"]
        + read("additional-slots-part02.json")["frames"]
    )
    replacements = {
        "ADD-Y01-F00099-M01": "ADD-Y01-F00099-M01-R02",
        "ADD-Y01-F00051-M01": "ADD-Y01-F00099-M01-R02",
    }
    explicit = {
        ("Y01-F00045", 0): "ADD-Y01-F00045-M01",
        ("Y01-F00050", 1): "ADD-Y01-F00125-M01",
        ("Y04-F00022", 1): "ADD-Y04-F00022-M01",
        ("Y04-F00030", 0): "ADD-Y04-F00030-M02",
        ("Y06-F00004", 0): "ADD-Y06-F00004-M01",
        ("Y06-F00012", 2): "ADD-Y06-F00012-M03",
        ("Y06-F00095", 2): "ADD-Y06-F00095-M03-R02",
    }
    for frame in frames:
        for index, slot in enumerate(frame["slots"]):
            candidate = explicit.get((frame["frame"], index), slot.get("candidate"))
            if candidate:
                candidate = replacements.get(candidate, candidate)
                verdict = qa[candidate]
                slot["candidate"] = candidate
                slot["action"] = (
                    "propose_candidate"
                    if verdict["result"] == "pass_draft"
                    else "withhold_geometry"
                )
                slot["reason"] = verdict["note"]
                slot["qa_status"] = verdict["result"]
                if (
                    not candidate.startswith("ADD-" + frame["frame"] + "-")
                    and verdict["result"] == "pass_draft"
                ):
                    slot["action"] = "represented_by_candidate"
                    slot["reason"] += (
                        " Chọn đại diện ở frame khác đã so trong audit, không suy danh tính."
                    )
            elif slot.get("existing"):
                retained = ledger[slot["existing"]]
                assert retained["owner_import_status"] == "approved_existing", slot
                assert retained["owner_interpreted_action"] == "keep", slot
                slot["action"] = "covered_existing"
                slot["reason"] = (
                    "Đã có đại diện được owner duyệt; không thêm bản gần trùng."
                )
            assert not slot["action"].startswith("pending"), slot
            slot["audit_complete"] = True
    assert len(frames) == len({r["frame"] for r in frames}) == 41
    expected = {r["id"].removeprefix("ADD-") for r in read("additional-parents.json")}
    assert {r["frame"] for r in frames} == expected
    dump(
        HERE / "additional-final-slots.json",
        {
            "status": "audit_complete_pending_owner_acceptance",
            "scope": "Đối chiếu vị trí và hành vi được đánh dấu; không nhận dạng danh tính.",
            "frame_count": 41,
            "slot_count": sum(len(r["slots"]) for r in frames),
            "frames": frames,
        },
    )


if __name__ == "__main__":
    main()
