"""Build a pinned, read-only exception gallery from existing runtime evidence."""
from __future__ import annotations

import argparse
import html
import os
from pathlib import Path

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.common.provenance import sha256_file
from ai_exam_monitoring.training.adaptation_config import FilePin
from ai_exam_monitoring.training.artifacts import checksum_artifacts, write_json

from .detector_review import read_object
from .runtime_config import media_deadline


def build_batch(config: Path, workspace: Path, output: Path) -> None:
    workspace, output = workspace.resolve(), output.resolve()
    if output.exists() or not output.is_relative_to(workspace / "outputs"):
        raise DataContractError("Batch requires a new directory under workspace outputs")
    raw = load_yaml(config)
    if raw.get("schema_version") != "runtime-exception-batch-v1":
        raise DataContractError("Unknown batch schema")
    paths = {k: FilePin(**v).verify(workspace) for k, v in raw["pins"].items()}
    session = read_object(paths["run"])
    media_deadline(session)
    checks = read_object(paths["checksums"])
    for key in ("predictions", "run"):
        if checks.get(paths[key].name) != sha256_file(paths[key]):
            raise DataContractError("Batch input checksum mismatch")
    records = read_object(paths["predictions"])["records"]
    rows = {r["anchor_id"]: r for r in records}
    cohort = read_object(paths["cohort"])
    if cohort["media_delete_by"] != session["media_delete_by"]:
        raise DataContractError("Batch deadline differs from source")
    frames = {f["frame_index"]: f for f in cohort["frames"]}
    evidence = []
    sections = []

    def image_link(pin: dict[str, str], caption: str) -> str:
        path = FilePin(**pin).verify(workspace)
        relative = Path(os.path.relpath(path, output)).as_posix()
        return (f'<figure><figcaption>{html.escape(caption)}</figcaption>'
                f'<a href="{html.escape(relative)}">'
                f'<img src="{html.escape(relative)}"></a></figure>')

    for case in raw["cases"]:
        selected = [rows[a] for a in case["anchors"]]
        frame_ids = {r["frame_index"] for r in selected}
        sections.append(f'<section id="{html.escape(case["id"])}"><h2>'
                        f'{html.escape(case["id"])} — {html.escape(case["title"])}</h2>'
                        f'<p>{html.escape(case["draft_observation"])}</p>'
                        f'<p><b>Cần chốt:</b> {html.escape(case["question"])}</p>')
        for idx in sorted(frame_ids):
            sections.append(image_link(frames[idx]["source_png"], f"Nguồn frame {idx}"))
        for row in selected:
            overlay = case.get("overlays", {}).get(str(row["frame_index"]))
            if overlay:
                sections.append(image_link(overlay, "Detector boxes — mã b chỉ trong frame"))
            sections.append(f'<h3>{html.escape(row["anchor_id"])}</h3><p>'
                            f'Person: {row["person_box"]}; context: {row["context_box"]}</p>')
            sections.append(image_link(row["crop"], "Context crop"))
            sections.append(image_link(row["input"], "Model input"))
            sections.append('<details><summary>Xem scores sau review hình ảnh</summary>'
                            f'<p>{row["scores"]}; flags={row["above_threshold"]}</p></details>')
        sections.append('</section>')
        evidence.append({**case, "records": selected, "owner_decision": None,
                         "role": "unknown", "status": "draft"})
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "review.json", {"status": "draft", "config_sha256": sha256_file(config),
               "pins": raw["pins"], "media_delete_by": session["media_delete_by"],
               "cases": evidence})
    (output / "index.html").write_text(
        '<!doctype html><html lang="vi"><meta charset="utf-8">'
        '<title>Review ngoại lệ runtime</title><style>body{font:17px system-ui;margin:28px;'
        'background:#f4f6fa;color:#172439}section{padding:20px;background:white;'
        'margin:24px 0;border:1px solid #ccd}figure{display:inline-block;vertical-align:top;'
        'margin:8px}img{max-width:570px;max-height:350px}figcaption{max-width:570px}'
        'details{padding:12px;background:#eef}a{color:#1257a4}</style>'
        '<h1>Review ngoại lệ runtime — Draft</h1><p>Không inference mới; không tự đổi '
        'winner/nhãn/role. Bấm ảnh để xem kích thước gốc. Phản hồi theo mã case; '
        'unknown được giữ khi chưa rõ. Scores không là ground truth.</p>'
        '<p><a href="review.json">Manifest và pins</a></p>' + ''.join(sections) + '</html>',
        encoding="utf-8")
    checksum_artifacts(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_batch(args.config, args.workspace, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
