from pathlib import Path

from choices import CHOICES
from PIL import Image, ImageDraw

from ai_exam_monitoring.data.source_review import preview_input

R = Path.cwd()
OUTPUT = R / "data/interim/frame-crop-additional-20261017"
(OUTPUT / "qa").mkdir(exist_ok=True)
(OUTPUT / "previews").mkdir(exist_ok=True)
rows = []
for g, a, f, p, c, s, _reason in CHOICES:
    cid = f"{g}-{a}-F{f:05}"
    source = R / f"data/interim/frame-crop-audit-20261016/frames/{g}/frame_{f:05}.jpg"
    im = Image.open(source).convert("RGB")
    assert 0 <= c[0] < c[2] <= im.width and 0 <= c[1] < c[3] <= im.height, (cid, c)
    assert c[0] <= p[0] < p[2] <= c[2] and c[1] <= p[1] < p[3] <= c[3], cid
    crop = im.crop(c)
    crop.save(OUTPUT / "previews" / f"{cid}.png")
    rows.append((cid, crop, preview_input(crop, 224, (114, 114, 114)), s))
for group in sorted(set(x[0] for x in CHOICES)):
    batch = [r for r in rows if r[0].startswith(group)]
    for off in range(0, len(batch), 6):
        part = batch[off : off + 6]
        can = Image.new("RGB", (1500, 400 * ((len(part) + 2) // 3)), "#ddd")
        d = ImageDraw.Draw(can)
        for j, (cid, crop, inp, s) in enumerate(part):
            x = j % 3 * 500
            y = j // 3 * 400
            im = crop.copy()
            im.thumbnail((265, 350))
            can.paste(im, (x, y + 30))
            can.paste(inp, (x + 270, y + 30))
            d.text((x + 3, y + 5), cid + " " + s, fill="black")
        can.save(OUTPUT / "qa" / f"{group}-{off // 6 + 1:02}.jpg", quality=97)
print("preview count", len(rows))
