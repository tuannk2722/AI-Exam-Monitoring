"""Validate audit evidence and delta membership without claiming audit completion."""

import json
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import unquote

from intake import HERE, MEDIA, ROOT, dump, sha
from PIL import Image

from ai_exam_monitoring.data.source_review import preview_input


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"src", "href"} and value:
                self.targets.append(value)


def main():
    ledger = read("resolved-ledger.json")
    assert len(ledger) == len({r["id"] for r in ledger}) == 907
    parents = {r["id"]: r for r in ledger + read("additional-parents.json")}
    geometries = {r["candidate_id"]: r for r in read("geometry-review.json")}
    delta = read("delta-review.json")
    assert len(delta) == len({r["id"] for r in delta})
    for row in delta:
        assert row["parent"] in parents and row["owner_approved"] is False
        assert row["states"] != ["U", "U"]
        for key in ("before", "after", "source", "input"):
            if key in row:
                assert (ROOT / row[key]).is_file(), (row["id"], key)
        if row["kind"] == "geometry":
            assert geometries[row["id"]]["qa_status"] == "pass_draft"
        if row["kind"] == "label_change":
            with Image.open(ROOT / row["after"]) as crop:
                expected = preview_input(crop.convert("RGB"), 224, (114, 114, 114))
            with Image.open(ROOT / row["input"]) as actual:
                assert actual.size == expected.size
                assert actual.convert("RGB").tobytes() == expected.tobytes()
        if row["kind"] == "duplicate_exclusion":
            assert row["retain"] in parents
            assert parents[row["retain"]].get("owner_interpreted_action") != "exclude"
    slots = read("additional-final-slots.json")["frames"]
    expected_frames = {r["id"].removeprefix("ADD-") for r in read("additional-parents.json")}
    assert len(slots) == len({r["frame"] for r in slots}) == 41
    assert {r["frame"] for r in slots} == expected_frames
    for frame in slots:
        for slot in frame["slots"]:
            assert slot["audit_complete"] is True
            if "existing" in slot:
                assert slot["existing"] in parents, slot
            if "candidate" in slot:
                assert slot["candidate"] in geometries, slot
    parser = Links()
    page = MEDIA / "index.html"
    parser.feed(page.read_text(encoding="utf-8"))
    for target in parser.targets:
        assert (MEDIA / unquote(target)).resolve().is_file(), target
    completion = read("audit-completion.json")
    for name, expected in completion["evidence_sha256"].items():
        assert sha((HERE / name).read_bytes()) == expected, name
    assert sha(page.read_bytes()) == completion["gallery_sha256"]
    browser_path = HERE / "browser-validation.json"
    browser = read(browser_path.name) if browser_path.exists() else {}
    browser_checked = browser.get("status") == "pass" and browser.get("gallery_sha256") == sha(
        page.read_bytes()
    )
    result = {
        "status": "audit_checks_pass",
        "audit_complete": True,
        "ledger_records": len(ledger),
        "delta_by_kind": dict(Counter(r["kind"] for r in delta)),
        "marked_frames_with_slot_records": len(slots),
        "slot_decisions_complete": True,
        "html_local_links_checked": len(parser.targets),
        "html_sha256": sha(page.read_bytes()),
        "browser_render_checked": browser_checked,
        "note": "Audit hoàn tất; kiểm tra kỹ thuật không thay owner nghiệm thu thay đổi.",
    }
    dump(HERE / "checkpoint-validation.json", result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
