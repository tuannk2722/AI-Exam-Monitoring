"""HTTP transport for the approved local monitor, with bounded request bodies."""

from __future__ import annotations

import asyncio
import hashlib
import json
import threading
from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse
from starlette.concurrency import run_in_threadpool

from .monitor import Monitor
from .pipeline import Jobs


async def object_body(request: Request, limit: int) -> dict[str, Any]:
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > limit:
            raise ValueError("Yêu cầu vượt giới hạn dung lượng")
        body.extend(chunk)
    value = json.loads(body)
    if not isinstance(value, dict):
        raise ValueError("Yêu cầu phải là JSON object")
    return value


def install_monitor_routes(app: FastAPI, monitor: Monitor, jobs: Jobs,
                           execution_lock: threading.Lock) -> None:
    interval = monitor.config["transport_interval_ms"] / 1000

    @app.get("/api/monitor/state")
    def state() -> dict[str, Any]:
        return monitor.state()

    @app.post("/api/monitor/uploads", status_code=201)
    async def create(request: Request) -> dict[str, Any]:
        value = await object_body(request, monitor.config["max_receipt_bytes"] + 1024)

        def prepare() -> dict[str, Any]:
            with execution_lock:
                with jobs.lock:
                    if any(s["status"] in {"queued", "running"} for s in jobs.active.values()):
                        raise FileExistsError("Job offline đang chạy; hãy đợi hoàn tất")
                if not isinstance(value.get("receipt"), dict):
                    raise ValueError("Thiếu receipt JSON")
                size = value.get("size")
                if type(size) is not int:
                    raise ValueError("Thiếu dung lượng video nguyên")
                return monitor.create(value["receipt"], size, value.get("model_id"))

        return await run_in_threadpool(prepare)

    @app.put("/api/monitor/uploads/{identity}")
    async def upload(identity: str, request: Request) -> dict[str, Any]:
        handle = await run_in_threadpool(monitor.begin_upload, identity)
        digest = hashlib.sha256()
        try:
            async for chunk in request.stream():
                await run_in_threadpool(monitor.write_chunk, identity, handle, chunk)
                digest.update(chunk)
            await run_in_threadpool(handle.close)
            return await run_in_threadpool(monitor.finish_upload, identity, digest.hexdigest())
        except BaseException as exc:
            handle.close()
            # Cancellation must release the file and partial payload too.
            monitor.abort_upload(identity, type(exc).__name__)
            raise

    @app.post("/api/monitor/sessions/{identity}/start")
    def start(identity: str) -> dict[str, Any]:
        with execution_lock:
            return monitor.start(identity)

    @app.post("/api/monitor/sessions/{identity}/command")
    async def command(identity: str, request: Request) -> dict[str, Any]:
        value = await object_body(request, 1024)
        return await run_in_threadpool(monitor.command, identity, value)

    @app.delete("/api/monitor/sessions/{identity}", status_code=204)
    def delete(identity: str) -> Response:
        monitor.delete(identity)
        return Response(status_code=204)

    @app.get("/api/monitor/sessions/{identity}/preview")
    def preview(identity: str, epoch: int) -> StreamingResponse:
        current = monitor.state()["session"]
        if not current or current["id"] != identity or current["epoch"] != epoch:
            raise FileExistsError("Preview thuộc phiên hoặc epoch cũ")
        buffer = monitor.preview
        assert buffer is not None

        async def images() -> AsyncIterator[bytes]:
            revision = -1
            while True:
                state = await run_in_threadpool(monitor.state)
                session = state["session"]
                snapshot = buffer.snapshot()
                if (not session or session["id"] != identity or session["epoch"] != epoch
                        or snapshot.closed or snapshot.epoch != epoch):
                    return
                if snapshot.jpeg is not None and snapshot.revision != revision:
                    revision = snapshot.revision
                    yield (b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                           + str(len(snapshot.jpeg)).encode() + b"\r\n\r\n"
                           + snapshot.jpeg + b"\r\n")
                if session["status"] in {"completed", "stopped", "failed"}:
                    return
                await asyncio.sleep(interval)

        return StreamingResponse(images(), media_type="multipart/x-mixed-replace; boundary=frame")

    @app.get("/api/monitor/sessions/{identity}/events")
    def events(identity: str) -> StreamingResponse:
        current = monitor.state()["session"]
        if not current or current["id"] != identity:
            raise FileNotFoundError("Phiên không còn hiện hành")

        async def snapshots() -> AsyncIterator[str]:
            sequence = 0
            while True:
                value = await run_in_threadpool(monitor.state)
                sequence += 1
                # Full snapshots deliberately replace replay; reconnect starts from current state.
                yield (f"id: {identity}:{sequence}\nevent: snapshot\ndata: "
                       + json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n\n")
                if (not value["session"] or value["session"]["id"] != identity
                        or value["session"]["status"] in {"completed", "stopped", "failed"}):
                    return
                await asyncio.sleep(interval)

        return StreamingResponse(snapshots(), media_type="text/event-stream",
                                 headers={"X-Accel-Buffering": "no"})
