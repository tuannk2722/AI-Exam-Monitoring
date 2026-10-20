"""Run a pinned local research queue without a chat session or external service."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any

from ai_exam_monitoring.common.provenance import sha256_file

from .adaptation_config import FilePin, local_path
from .artifacts import code_identity, now, write_json


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fmt(value: Any) -> str:
    return "unavailable" if value is None else f"{value:.4f}"


def rank_key(metrics: dict[str, Any]) -> tuple[float, float, float]:
    """Prespecified development rank: gates, AP, then unweighted BCE."""
    return (
        float(metrics["calibrated_evaluation"]["v11_all_targets_pass_gates"]),
        float(metrics["macro_ap"]),
        -float(metrics["macro_masked_bce"]),
    )


def verify_parity(run: Path, evaluation: Path) -> None:
    if read_json(run / "metrics.json")["selection"] != read_json(
        evaluation / "metrics.json"
    )["selection"]:
        raise ValueError("Standalone validation metrics differ")
    if read_json(run / "predictions-selection.json") != read_json(
        evaluation / "predictions-selection.json"
    ):
        raise ValueError("Standalone validation predictions differ")


def report(root: Path, plan: dict[str, Any], state: dict[str, Any]) -> None:
    folder = local_path(root, plan["report_dir"])
    folder.mkdir(parents=True, exist_ok=True)
    rows = state["completed"]
    lines = [
        f"# Bảng số liệu tự động — {plan.get('title', 'Training')}", "",
        "**Chưa phải báo cáo phân tích cuối. Agent phải kiểm evidence và viết README.md.**", "",
        f"Trạng thái: **{state['status']}**. Cập nhật UTC: {now()}.", "",
        "Development validation đã dùng chọn epoch, recipe và ngưỡng; không là holdout độc lập.",
        "Test giữ đóng. Không tự chọn model Selected hoặc nghiệm thu production.", "",
        "| Run | Recipe | Seed | Best epoch | Macro AP | BCE | Qua 80/80/20 | Reload |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        m = row["metrics"]
        lines.append(
            f"| {row['id']} | {row['recipe']} | {row['seed']} | {row['best_epoch']} | "
            f"{m['macro_ap']:.4f} | {m['macro_masked_bce']:.4f} | "
            f"{m['calibrated_evaluation']['v11_all_targets_pass_gates']} | PASS |"
        )
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row["recipe"] != "SMOKE":
            groups.setdefault(row["recipe"], []).append(row)
    summaries = []
    for recipe, members in groups.items():
        aps = [float(r["metrics"]["macro_ap"]) for r in members]
        summaries.append({
            "recipe": recipe, "seeds": len(members), "mean_macro_ap": statistics.mean(aps),
            "std_macro_ap": statistics.stdev(aps) if len(aps) > 1 else None,
            "min_macro_ap": min(aps),
            "mean_bce": statistics.mean(r["metrics"]["macro_masked_bce"] for r in members),
            "gate_pass_runs": sum(bool(r["metrics"]["calibrated_evaluation"][
                "v11_all_targets_pass_gates"]) for r in members),
        })
    confirmed = [r for r in summaries if r["seeds"] == 3]
    confirmed.sort(key=lambda r: (
        -r["gate_pass_runs"], -r["mean_macro_ap"], r["std_macro_ap"], r["mean_bce"],
        r["recipe"],
    ))
    if confirmed:
        lines += ["", "## Độ ổn định trên ba seed", "",
                  "| Recipe | Macro AP trung bình ± SD | AP thấp nhất | Số run qua cổng |",
                  "|---|---:|---:|---:|"]
        for r in confirmed:
            lines.append(f"| {r['recipe']} | {r['mean_macro_ap']:.4f} ± "
                         f"{r['std_macro_ap']:.4f} | {r['min_macro_ap']:.4f} | "
                         f"{r['gate_pass_runs']}/3 |")
        lines += ["", f"Recipe ưu tiên để owner xem xét: **{confirmed[0]['recipe']}**.",
                  "Đây là đề xuất từ development; không phải quyết định promotion."]
    for row in rows:
        if row["recipe"] == "SMOKE":
            continue
        m = row["metrics"]
        lines += ["", f"## {row['id']}", "",
                  "| Target | P / N / U | AP | Ngưỡng | Precision | Recall | FPR |",
                  "|---|---|---:|---:|---:|---:|---:|"]
        for target, t in m["calibrated_evaluation"]["targets"].items():
            support = m["targets"][target]
            lines.append(
                f"| {target} | {support['positive']} / {support['negative']} / "
                f"{support.get('unknown', 'NA')} | {fmt(support['ap'])} | "
                f"{m['calibrated_thresholds'][target]:.4f} | {fmt(t['precision'])} | "
                f"{fmt(t['recall'])} | {fmt(t['fpr'])} |"
            )
        lines += ["", f"Artifacts: `outputs/{row['id']}/`; checkpoint `best.pt`; "
                  "metrics chứa bootstrap theo nhóm, nguồn, lát cắt và danh sách FP/FN."]
        lines += ["", "Ngưỡng cố định 0,50:", "",
                  "| Target | Precision | Recall | FPR | TP / FP / FN / TN |",
                  "|---|---:|---:|---:|---|"]
        for target, t in m["targets"].items():
            lines.append(f"| {target} | {fmt(t['precision'])} | {fmt(t['recall'])} | "
                         f"{fmt(t['fpr'])} | {t['tp']} / {t['fp']} / {t['fn']} / {t['tn']} |")
        lines += ["", "Phân tích theo nguồn (AP; nguồn thiếu P/N là unavailable):", "",
                  "| Nguồn | Số mẫu | Phone AP | Looking AP |",
                  "|---|---:|---:|---:|"]
        for source, s in m.get("by_source", {}).items():
            lines.append(f"| {source} | {s['records']} | "
                         f"{fmt(s['targets']['phone_use']['ap'])} | "
                         f"{fmt(s['targets']['looking_around']['ap'])} |")
        for target, errors in m.get("fp_fn_gallery_calibrated_threshold", {}).items():
            lines += ["", f"Lỗi có margin lớn nhất của {target} (ngưỡng hiệu chỉnh):", "",
                      "| ID | Nguồn | Lỗi | Score | Ngưỡng |",
                      "|---|---|---|---:|---:|"]
            for error in errors[:5]:
                lines.append(f"| {error['sample_id']} | {error['source_id']} | "
                             f"{error['error_type']} | {error['score']:.4f} | "
                             f"{error['threshold']:.4f} |")
    if state.get("error"):
        lines += ["", "## Lỗi cần xử lý", "", state["error"],
                  "Pipeline đã dừng; không đổi batch/config hoặc bỏ integrity guard."]
    lines += ["", "## Giới hạn", "",
              "- Support và khoảng tin cậy theo nhóm nằm trong metrics của từng run.",
              "- Chọn recipe trên seed đầu tạo selection bias; "
              "các seed không là dữ liệu độc lập.",
              "- Không so trực tiếp metrics giữa các release khác ground truth/cohort.",
              "- Snapshot config, protocol, approval và logs được giữ để truy vết.", ""]
    text = "\n".join(lines)
    temp = folder / "machine-summary.md.tmp"
    temp.write_text(text, encoding="utf-8")
    temp.replace(folder / "machine-summary.md")
    write_json(folder / "summary.json", {
        "status": state["status"], "recipes": summaries,
        "recommended_recipe": confirmed[0]["recipe"] if confirmed else None,
        "decision": "owner_review_required" if state["status"] == "FINISHED" else "pending",
        "analysis_status": "pending_agent_review",
        "runs": rows, "error": state.get("error"),
    })


def run_one(
    root: Path, item: dict[str, Any], log_dir: Path, interrupt: bool = False,
) -> dict[str, Any]:
    config_path = FilePin(**item["config"]).verify(root)
    output = local_path(root, f"outputs/{item['id']}")
    evaluation = local_path(root, f"outputs/{item['id']}-val-evaluation")
    if output.exists():
        raise ValueError(f"Refusing existing run output: {output}")
    command = [
        sys.executable, "-X", "utf8", "-m", "ai_exam_monitoring.training.train",
        "--config", str(config_path), "--output", str(output), "--workspace", str(root),
    ]
    with (log_dir / f"{item['id']}.log").open("a", encoding="utf-8") as log:
        if interrupt:
            result = subprocess.run(command + ["--interrupt-after", "1"], cwd=root,
                                    stdout=log, stderr=subprocess.STDOUT, check=False)
            record = read_json(output / "run.json")
            if result.returncode == 0 or record["status"] != "INTERRUPTED":
                raise ValueError("Smoke checkpoint interruption drill failed")
            subprocess.run(command + ["--resume"], cwd=root, stdout=log,
                           stderr=subprocess.STDOUT, check=True)
        else:
            subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
        if read_json(output / "run.json")["status"] != "FINISHED":
            raise ValueError("Trainer did not finish")
        subprocess.run([
            sys.executable, "-X", "utf8", "-m", "ai_exam_monitoring.training.evaluate",
            "--run", str(output), "--output", str(evaluation), "--split", "val",
            "--workspace", str(root),
        ], cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
    verify_parity(output, evaluation)
    record = read_json(output / "run.json")
    return {
        "id": item["id"], "recipe": item["recipe"], "seed": item["seed"],
        "best_epoch": record["best_epoch"], "elapsed_seconds": record["elapsed_seconds"],
        "metrics": read_json(output / "metrics.json")["selection"],
        "checkpoint_sha256": sha256_file(output / "best.pt"), "reload_parity": "PASS",
    }


def execute(plan_path: Path, root: Path) -> None:
    root = root.resolve()
    plan = read_json(plan_path)
    if plan["code_sha256"] != code_identity()["sha256"]:
        raise ValueError("Campaign code changed after freeze")
    for pin in plan["evidence_pins"]:
        FilePin(**pin).verify(root)
    folder = local_path(root, plan["report_dir"])
    folder.mkdir(parents=True, exist_ok=True)
    lock = folder / "campaign.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    state: dict[str, Any] = {"status": "RUNNING", "pid": os.getpid(), "completed": [],
                             "plan_sha256": sha256_file(plan_path), "started_at": now()}
    logs = folder / "logs"
    logs.mkdir(exist_ok=True)
    write_json(folder / "campaign-state.json", state)
    if os.name == "nt":
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:
        if plan.get("verified_smoke"):
            receipt = FilePin(**plan["verified_smoke"]).read_json(root)
            if receipt["status"] != "PASS":
                raise ValueError("Reused smoke is not verified")
            for evidence in receipt["evidence_pins"]:
                FilePin(**evidence).verify(root)
            smoke = receipt["result"]
            verify_parity(root / "outputs" / smoke["id"],
                          root / "outputs" / f"{smoke['id']}-val-evaluation")
        else:
            smoke = run_one(root, plan["smoke"], logs, interrupt=True)
        history = read_json(root / "outputs" / smoke["id"] / "history.json")
        if not {"warmup_head_only", "finetune_layer4_block1"} <= {
            h["stage"] for h in history
        }:
            raise ValueError("Smoke did not exercise warmup and fine-tuning")
        state["completed"].append(smoke)
        # This receipt records an observed check, never grants new owner authorization.
        observed_smoke = {
            "status": "PASS", "run": smoke["id"], "reload_parity": "PASS",
            "checkpoint_resume": "PASS", "stage_transition": "PASS",
        }
        smoke_path = local_path(root, plan["smoke_result"])
        if smoke_path.exists():
            if read_json(smoke_path) != observed_smoke:
                raise ValueError("Existing smoke evidence differs")
        else:
            write_json(smoke_path, observed_smoke)
        for item in plan["screening"]:
            if code_identity()["sha256"] != plan["code_sha256"]:
                raise ValueError("Code changed during campaign")
            state["active"] = item["id"]
            write_json(folder / "campaign-state.json", state)
            state["completed"].append(run_one(root, item, logs))
        candidates = [r for r in state["completed"] if r["recipe"] in plan["repeat_recipes"]]
        candidates.sort(key=lambda r: (*(-v for v in rank_key(r["metrics"])), r["recipe"]))
        selected = [r["recipe"] for r in candidates[:2]]
        write_json(folder / "selection.json", {
            "recipes": selected, "rule": "gate_pass, macro_ap desc, BCE asc, recipe name",
            "selected_at": now(),
        })
        for item in plan["confirmation"]:
            if item["recipe"] not in selected:
                continue
            if code_identity()["sha256"] != plan["code_sha256"]:
                raise ValueError("Code changed during campaign")
            state["active"] = item["id"]
            write_json(folder / "campaign-state.json", state)
            state["completed"].append(run_one(root, item, logs))
        state["status"] = "FINISHED"
    except BaseException as error:
        state["status"] = "FAILED"
        state["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        state["ended_at"] = now()
        write_json(folder / "campaign-state.json", state)
        try:
            report(root, plan, state)
        finally:
            lock.unlink()
            if os.name == "nt":
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    args = parser.parse_args()
    execute(args.plan, args.workspace)


if __name__ == "__main__":
    main()
