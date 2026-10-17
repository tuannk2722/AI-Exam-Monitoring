import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw

root = Path.cwd()
report = root / "artifacts/reports/frame-crop-audit-20261016"
out = root / "data/interim/frame-crop-owner-review-20261017"
out.mkdir(exist_ok=True)
raw = (report / "README.md").read_bytes()
snapshot = report / "owner-review-input-20261017.md"
if snapshot.exists():
    assert snapshot.read_bytes() == raw, (
        "Owner comments changed; create a new version instead of replacing the snapshot"
    )
else:
    snapshot.write_bytes(raw)
notes = raw.decode("utf-8").split("## Kết quả review của owner")[1]
ids = list(dict.fromkeys(re.findall(r"G\d{2}-A\d{2}-F\d{5}(?:-R\d{2})?", notes)))
rows = json.loads((report / "review-index.json").read_text(encoding="utf-8"))
lookup = {r["candidate_id"]: r for r in rows}
assert set(ids) <= lookup.keys()
json.dump(
    {
        "readme_sha256": hashlib.sha256(raw).hexdigest(),
        "mentioned_ids": ids,
        "default_approved_ids": [r["candidate_id"] for r in rows if r["candidate_id"] not in ids],
    },
    open(report / "owner-review-scope-20261017.json", "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2,
)
for off in range(0, len(ids), 6):
    batch = ids[off : off + 6]
    can = Image.new("RGB", (1500, 760), "#dedede")
    draw = ImageDraw.Draw(can)
    for j, cid in enumerate(batch):
        r = lookup[cid]
        x = j % 3 * 500
        y = j // 3 * 380
        im = Image.open(root / "data/interim/frame-crop-audit-20261016" / r["export_path"])
        im.thumbnail((270, 330))
        can.paste(im, (x, y + 30))
        can.paste(
            Image.open(
                root / "data/interim/frame-crop-audit-20261016/candidates" / cid / "input.png"
            ),
            (x + 274, y + 30),
        )
        draw.text((x + 3, y + 5), cid + " " + "".join(r["draft_states"]), fill="black")
    can.save(out / f"exception-{off // 6 + 1:02}.jpg", quality=96)
print("mentioned", len(ids), "default approved", 100 - len(ids))
print(ids)
