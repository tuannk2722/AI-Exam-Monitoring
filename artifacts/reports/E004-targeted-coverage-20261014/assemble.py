"""Join recorded visual notes to the audit worksheet and render local review."""

from __future__ import annotations

import csv
import html
import json
from collections import Counter
from pathlib import Path

from ai_exam_monitoring.training.error_audit import support

root = Path(__file__).resolve().parents[3]
report = Path(__file__).parent
out = root / "outputs/E004-targeted-coverage-20261014"


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf8")


matrix = read(report / "matrix.json")["rows"]
by_id = {r["sample_id"]: r for r in matrix}
shortlist = read(report / "shortlist.json")
with (report / "visual-notes.tsv").open(encoding="utf8", newline="") as f:
    notes = list(csv.DictReader(f, delimiter="\t"))
assert len(notes) == len({r["sample_id"] for r in notes})
assert {r["sample_id"] for r in notes} == set(shortlist["train_ids"])
native_full = {
    "EXP-CM-008",
    "V7-A-001",
    "V7-A-004",
    "V7-B-041",
    "V7-OE-S114-A01",
    "V7-OE-S112-A01",
    "V7-OE-S061-A01",
}
observations = []
for note in notes:
    sid = note["sample_id"]
    observations.append(
        {
            **note,
            "cohort": "train",
            "factors": note["factors"].split(","),
            "basis": "new_visual_review_native_fit_and_input224",
            "native_full_opened": sid in native_full,
            "crop_sha256": by_id[sid]["crop_sha256"],
            "status": "draft_pending_owner_review",
        }
    )

# These are explicit mappings of prior written observations, not fresh visual review.
selection_factors = {
    "E004-CF-C021": ["held_phone", "outside_workarea", "multi_person_context"],
    "E004-CF-C029": ["calculator_negative", "own_workarea"],
    "E004-CF-C031": ["own_workarea"],
    "E004-EX-C009": ["desk_phone", "own_workarea"],
    "E004-EX-C027": ["outside_workarea"],
    "E004-EX-C029": ["calculator_negative", "outside_workarea"],
    "E004-EX-C051": ["own_workarea", "multi_person_context"],
    "E004-EX-C120": ["held_phone", "partial_phone"],
    "E004-EX-C122": ["outside_workarea", "multi_person_context"],
    "E004-EX-C042": ["desk_phone", "partial_phone", "outside_workarea", "multi_person_context"],
    "E004-EX-C054": ["outside_workarea"],
    "E004-EX-C055": ["desk_phone", "outside_workarea"],
    "E004-EX-C056": ["desk_phone", "outside_workarea"],
    "E004-EX-C195": ["desk_phone", "own_workarea"],
    "E004-EX-C199": ["desk_phone", "outside_workarea"],
    "E004-EX-C044": ["outside_workarea"],
    "E004-EX-C045": ["pen_negative", "own_workarea"],
    "E004-EX-C193": ["pen_negative", "own_workarea"],
    "E004-EX-C194": ["pen_negative", "outside_workarea"],
    "E004-CN-042": ["outside_workarea"],
    "E004-CN-043": ["own_workarea"],
    "E004-CN-044": ["outside_workarea", "multi_person_context"],
    "E004-CN-045": ["outside_workarea", "multi_person_context"],
    "E004-CN-056": ["own_workarea", "multi_person_context"],
    "E004-CN-046": ["own_workarea"],
    "E004-CN-047": ["own_workarea", "multi_person_context"],
    "E004-CN-048": ["own_workarea"],
    "E004-CN-050": ["own_workarea"],
    "E004-CN-052": ["pen_negative", "multi_person_context"],
    "E004-CN-053": ["pen_negative", "own_workarea", "multi_person_context"],
    "E004-CN-055": ["pen_negative", "own_workarea", "multi_person_context"],
}
assert set(selection_factors) == set(shortlist["selection_ids"])
for sid, factors in selection_factors.items():
    old = by_id[sid]["prior_draft_observation"]
    observations.append(
        dict(
            sample_id=sid,
            cohort="selection",
            factors=factors,
            evidence_224="see_prior_observation",
            confidence=old["confidence"],
            observation=old["observation"],
            basis="mapped_from_prior_draft_not_new_review",
            crop_sha256=by_id[sid]["crop_sha256"],
            status="draft_pending_owner_review",
        )
    )
write(
    report / "observations.json",
    dict(status="draft_pending_owner_review", labels_changed=False, observations=observations),
)
factor_summary = {}
for factor in sorted({v for r in observations for v in r["factors"]}):
    factor_summary[factor] = {}
    for cohort in ("train", "selection"):
        selected = [
            by_id[r["sample_id"]]
            for r in observations
            if factor in r["factors"] and r["cohort"] == cohort
        ]
        model_support = {}
        for model in ("WH", "LP"):
            predictions = [
                dict(
                    scores=r["scores"][model],
                    targets=r["labels"],
                    mask=[int(v is not None) for v in r["labels"]],
                )
                for r in selected
            ]
            model_support[model] = support(predictions, 0.5)
        factor_summary[factor][cohort] = dict(
            reviewed_count=len(selected),
            families=len({r["family"] for r in selected}),
            sources=dict(Counter(r["source"] for r in selected)),
            sample_ids=[r["sample_id"] for r in selected],
            support=model_support,
        )
write(
    report / "visual-factor-matrix.json",
    dict(
        status="draft_purposive_review_not_population_coverage",
        denominator={"train": 44, "selection": 31},
        factors=factor_summary,
        evidence_train=dict(
            Counter(r["evidence_224"] for r in observations if r["cohort"] == "train")
        ),
    ),
)

cards = []
for index, obs in enumerate(observations):
    row = by_id[obs["sample_id"]]
    sid = row["sample_id"]
    if obs["cohort"] == "train":
        input_url = f"inputs224/{sid}.png"
        board = f"boards/{index // 6 + 1:02}.jpg"
    else:
        input_url = f"../E004-visual-audit-20261014/inputs224/{sid}.png"
        # Resolve actual prior input naming without guessing it exists.
        candidates = list((root / "outputs/E004-visual-audit-20261014").rglob(f"{sid}*.png"))
        if not (out / input_url).exists():
            from PIL import Image

            exact = []
            for p in candidates:
                with Image.open(p) as im:
                    if im.size == (224, 224):
                        exact.append(p)
            assert len(exact) == 1, (sid, exact)
            input_url = (
                "../E004-visual-audit-20261014/"
                + exact[0].relative_to(root / "outputs/E004-visual-audit-20261014").as_posix()
            )
        board = "../E004-visual-audit-20261014/index.html"
    assert (out / input_url).exists()
    native_url = "../../" + row["crop_path"]
    search = html.escape(" ".join([sid, obs["cohort"], *obs["factors"], row["source"]]), quote=True)
    cards.append(f'''<article data-search="{search}"><h3>{sid} · {obs["cohort"]}</h3>
<p>{html.escape(row["source"])} · {html.escape(row["family"])} · native {row["native_size"]}</p>
<div class="images"><a href="{native_url}"><img src="{native_url}" alt="Native crop {sid}"></a>
<a href="{input_url}"><img class="exact" src="{input_url}" alt="Input 224 {sid}"></a></div>
<p>Trái: native thu vừa khung, bấm để xem gốc. Phải: input 224.</p>
<p><b>{html.escape(", ".join(obs["factors"]))}</b>
· {obs["evidence_224"]} · chắc chắn {obs["confidence"]}</p>
<p>{html.escape(obs["observation"])}</p>
<details><summary>Nhãn accepted, scores và lý do chọn</summary>
<p>Nhãn phone/looking: {row["labels"]}; W-H: {row["outcomes"]["WH"]};
LP: {row["outcomes"]["LP"]}.</p>
<p>Scores W-H: {row["scores"]["WH"]}; LP: {row["scores"]["LP"]}.</p>
<p>{html.escape(" | ".join(row["reasons"]))}</p>
<p>{html.escape(str(row["review_reasons"]))}</p></details>
<a href="{board}">Bảng đối chiếu</a></article>''')
page = (
    """<!doctype html><html lang="vi"><meta charset="utf-8"><title>E004 — Coverage review</title>
<style>body{font:16px system-ui;max-width:1250px;margin:32px auto;
padding:0 20px;background:#f4f6f8;color:#192b3c}
article{background:white;border:1px solid #ccd5dd;border-radius:10px;padding:20px;margin:20px 0}
.images{display:flex;gap:28px;align-items:center;flex-wrap:wrap}
.images img{max-width:360px;max-height:320px;object-fit:contain}
.images img.exact{width:224px;height:224px}input{padding:12px;width:90%;font:inherit}
summary{cursor:pointer}
a{color:#1465a3}h1{font-size:28px}</style>
<h1>E004 — Batch coverage train / selection</h1>
<p><b>Draft, chờ owner review.</b> 44 train mới xem; 31 selection dùng observations của audit trước.
Không đại diện toàn corpus; factors có thể chồng nhau. Không thay nhãn/split hoặc mở test.</p>
<p>Native-fit không phải pixel 1:1; bấm ảnh trái để xem file gốc. Input 224 bên phải chưa normalize.
Scores được giấu mặc định để owner có thể xem evidence trước.</p>
<p>Ngoại lệ: V7-OE-S061-A01 cần chỉ rõ anchor; V7-OE-S112-A01 là sách, không calculator.
Các nhận xét limited_native/uncertain cần review theo batch, không phải annotate lại corpus.</p>
<input id="filter" aria-label="Lọc mẫu" placeholder="Lọc ID, factor, nguồn hoặc train / selection">
<p id="count"></p>"""
    + "\n".join(cards)
    + """
<script>const f=document.querySelector('#filter');function filter(){let n=0;
document.querySelectorAll('article').forEach(a=>{
a.hidden=!a.dataset.search.toLowerCase().includes(f.value.toLowerCase());
if(!a.hidden)n++});
document.querySelector('#count').textContent=n+' mẫu hiển thị'}
f.addEventListener('input',filter);filter()</script></html>"""
)
(out / "index.html").write_text(page, encoding="utf8")
print(
    json.dumps(
        {
            f: {c: (v["reviewed_count"], v["families"]) for c, v in cells.items()}
            for f, cells in factor_summary.items()
        },
        ensure_ascii=False,
        indent=2,
    )
)
