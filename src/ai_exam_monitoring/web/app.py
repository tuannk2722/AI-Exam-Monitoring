"""FastAPI boundary for the local review workbench."""

from __future__ import annotations

import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ai_exam_monitoring.common.config import load_yaml
from ai_exam_monitoring.common.errors import ProjectError

from .catalog import Catalog, read_json
from .monitor import Monitor
from .monitor_routes import install_monitor_routes
from .pipeline import Jobs
from .store import ReviewStore


def create_app(workspace: Path = Path("."), config_path: Path | None = None) -> FastAPI:
    root = workspace.resolve()
    config = load_yaml(config_path or root / "configs/web/review.yaml")
    catalog = Catalog(root)
    store = ReviewStore(catalog.path(config["output_root"]) / "reviews.sqlite3")
    jobs = Jobs(catalog, config)
    monitor_path = root / "configs/web/LIVE-VIDEO-WEB-20261028/monitor.yaml"
    monitor = Monitor(root, monitor_path) if monitor_path.is_file() else None
    execution_lock = threading.Lock()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            from starlette.concurrency import run_in_threadpool
            if monitor is not None:
                await run_in_threadpool(monitor.close)
            await run_in_threadpool(jobs.executor.shutdown, wait=True)

    app = FastAPI(title="Exam Monitor", docs_url=None, redoc_url=None, lifespan=lifespan)
    app.state.catalog, app.state.store, app.state.jobs = catalog, store, jobs
    app.state.monitor = monitor
    assets = Path(__file__).parent / "assets"
    app.mount("/assets", StaticFiles(directory=assets), name="assets")
    templates = Environment(loader=FileSystemLoader(assets), autoescape=select_autoescape())

    @app.middleware("http")
    async def local_boundary(request: Request, call_next: Any) -> Response:
        origin = request.headers.get("origin")
        if (
            request.method not in {"GET", "HEAD"}
            and origin
            and origin != str(request.base_url).rstrip("/")
        ):
            return JSONResponse({"detail": "Chỉ nhận thao tác từ giao diện local"}, status_code=403)
        try:
            response: Response = await call_next(request)
        except Exception:
            return JSONResponse(
                {"detail": "Lỗi server; kiểm tra cấu hình và input của phiên"}, status_code=500
            )
        response.headers["Cache-Control"] = "no-store"
        return response

    async def input_error(_: Request, exc: Exception) -> JSONResponse:
        status = (
            409
            if isinstance(exc, FileExistsError)
            else 410
            if isinstance(exc, PermissionError)
            else 400
        )
        return JSONResponse({"detail": str(exc)}, status_code=status)

    for kind in (ValueError, FileNotFoundError, FileExistsError, PermissionError, ProjectError):
        app.add_exception_handler(kind, input_error)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return templates.get_template("monitor.html" if monitor else "index.html").render()

    @app.get("/review", response_class=HTMLResponse)
    def legacy_review() -> str:
        return templates.get_template("index.html").render()

    @app.get("/api/sessions")
    def sessions() -> list[dict[str, Any]]:
        items = catalog.discover()
        for item in items:
            if item["reviewable"]:
                try:
                    directory = catalog.path(item["id"])
                    provenance = read_json(directory / "provenance.json")
                    checks = read_json(directory / "checksums.json")
                    review = store.get(checks["events.jsonl"])
                    item["source_sha256"] = provenance["source_sha256"]
                    item["reviewed_count"] = sum(
                        d["status"] != "candidate" for d in review["decisions"].values()
                    )
                except (KeyError, ValueError, OSError):
                    item["catalog_warning"] = "Metadata phiên chưa đầy đủ"
        return items

    @app.get("/api/session")
    def session(identity: str) -> dict[str, Any]:
        data = catalog.load(identity)
        return {k: v for k, v in data.items() if k not in {"runtime_dir", "cache_dir"}}

    @app.get("/api/review")
    def review(identity: str) -> dict[str, Any]:
        return store.get(catalog.load(identity)["events_sha256"])

    @app.put("/api/review")
    def save_review(identity: str, value: dict[str, Any]) -> dict[str, Any]:
        data = catalog.load(identity)
        return store.save(
            data["events_sha256"], value, {e["event"]["event_id"] for e in data["events"]}
        )

    @app.get("/api/image")
    def media(identity: str, frame: int, anchor: str | None = None, kind: str = "crop") -> Response:
        return Response(catalog.image(identity, frame, anchor, kind), media_type="image/png")

    @app.post("/api/source")
    def connect(value: dict[str, str]) -> dict[str, bool]:
        catalog.connect_source(value["identity"], Path(value["source"]))
        return {"connected": True}

    @app.post("/api/preflight")
    def preflight(value: dict[str, str]) -> dict[str, Any]:
        return jobs.preflight(value["source"], value["receipt"])

    @app.post("/api/jobs", status_code=202)
    def start_job(value: dict[str, str]) -> dict[str, Any]:
        with execution_lock:
            if monitor is not None and monitor.busy():
                raise FileExistsError("Phiên giám sát đang hoạt động; hãy dừng hoặc xóa phiên")
            return jobs.start(value["source"], value["receipt"])

    @app.get("/api/jobs")
    def job_list() -> list[dict[str, Any]]:
        result = []
        for path in catalog.path(config["output_root"]).glob("job-*/session.json"):
            value = read_json(path)
            runtime = path.parent / "runtime/session.json"
            if runtime.exists():
                value["runtime"] = read_json(runtime)
                predictions = path.parent / "runtime/predictions.jsonl"
                if predictions.exists() and value["status"] == "running":
                    value["runtime_frames_written"] = sum(
                        '"record_type": "frame"' in line
                        for line in predictions.read_text(encoding="utf-8").splitlines()
                    )
            result.append(value)
        return result

    if monitor is not None:
        install_monitor_routes(app, monitor, jobs, execution_lock)
    return app
