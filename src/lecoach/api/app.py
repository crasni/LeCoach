"""Loopback transport. Default composition is an explicitly synthetic playback."""

import asyncio
from collections.abc import Callable
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from lecoach.contracts import Event
from lecoach.contracts.interfaces import Components, RuntimeSettings, SessionConfig
from lecoach.runtime.fixtures import FixtureRepository, play_browser, remap
from lecoach.runtime.session import SessionConflict, SessionController, SessionManager

ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
}


class ClientSubscription:
    def __init__(self, size: int) -> None:
        self.queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=size)
        self.overflow = False
        self.replaced = False

    def on_event(self, event: Event) -> None:
        if self.overflow or self.replaced:
            return
        try:
            self.queue.put_nowait(event)
        except asyncio.QueueFull:
            self.overflow = True


def create_app(
    factory: Callable[[SessionConfig], Components] | None = None,
    settings: RuntimeSettings | None = None,
) -> FastAPI:
    settings = settings or RuntimeSettings()
    manager = SessionManager(factory)
    fixtures = FixtureRepository()
    clients: dict[str, set[ClientSubscription]] = {}

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await manager.shutdown()

    app = FastAPI(title="LeCoach", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"]
    )
    app.state.manager = manager
    app.state.fixtures = fixtures

    @app.middleware("http")
    async def local_origin(request: Request, call_next):
        origin = request.headers.get("origin")
        if origin and origin not in ALLOWED_ORIGINS:
            return JSONResponse({"detail": "origin_not_allowed"}, status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    def session(session_id: str) -> SessionController:
        try:
            return manager.get(session_id)
        except KeyError:
            raise HTTPException(404, "session_not_found") from None

    @app.get("/api/health")
    async def health():
        return {
            "status": "ready",
            "default_mode": "fixture",
            "schema_version": 0,
            "live_integrated": factory is not None,
        }

    @app.get("/api/fixtures")
    async def list_fixtures():
        return fixtures.describe()

    @app.post("/api/sessions", status_code=201)
    async def prepare(config: SessionConfig):
        try:
            if config.mode == "fixture":
                case = fixtures.load(config.fixture_case)
                if len(case.session_ids) != 1:
                    raise HTTPException(422, "multi_session_case_requires_headless_replay")
            previous = manager.current
            controller = manager.create(config)
            if previous:
                for client in clients.get(previous.session_id, set()):
                    client.replaced = True
                previous.latest.clear()
                previous.transcript.clear()
                previous._seen.clear()
                previous.feedback = None
            return controller.snapshot()
        except SessionConflict as error:
            code = 503 if str(error).startswith("live_not_integrated") else 409
            raise HTTPException(code, str(error)) from None
        except ValueError as error:
            raise HTTPException(422, str(error)) from None

    @app.get("/api/sessions/{session_id}")
    async def current(session_id: str):
        return session(session_id).snapshot()

    @app.post("/api/sessions/{session_id}/start")
    async def start(session_id: str):
        controller = session(session_id)
        if not clients.get(session_id):
            raise HTTPException(409, "subscribe_to_events_before_start")
        try:
            if controller.config.mode == "fixture":
                case = fixtures.load(controller.config.fixture_case)
                started = next(e for e in case.events if e.type == "session.started")
                await controller.start(remap(started, started.session_id, controller.session_id))
                if controller.playback is None:
                    controller.playback = asyncio.create_task(play_browser(controller, case))
            else:
                await controller.start()
            return controller.snapshot()
        except SessionConflict as error:
            raise HTTPException(409, str(error)) from None

    @app.post("/api/sessions/{session_id}/stop")
    async def stop(session_id: str):
        return await session(session_id).stop()

    @app.get("/api/sessions/{session_id}/feedback")
    async def feedback(session_id: str):
        controller = session(session_id)
        if controller.feedback is not None:
            return controller.feedback
        raise HTTPException(409, f"feedback_{controller.feedback_status}")

    @app.get("/api/sessions/{session_id}/preview")
    async def preview(session_id: str):
        controller = session(session_id)
        adapter = controller.components.vision
        if adapter is None or controller.phase != "running":
            raise HTTPException(503, "preview_unavailable")
        first = adapter.preview_jpeg()
        if not first or len(first) > settings.preview_max_bytes:
            raise HTTPException(503, "preview_unavailable")

        async def frames():
            while controller.phase == "running":
                frame = adapter.preview_jpeg()
                if frame and len(frame) <= settings.preview_max_bytes:
                    yield (
                        b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                        + str(len(frame)).encode()
                        + b"\r\n\r\n"
                        + frame
                        + b"\r\n"
                    )
                await asyncio.sleep(settings.preview_interval_s)

        return StreamingResponse(frames(), media_type="multipart/x-mixed-replace; boundary=frame")

    @app.websocket("/api/sessions/{session_id}/events")
    async def events(websocket: WebSocket, session_id: str):
        origin = websocket.headers.get("origin")
        if origin and origin not in ALLOWED_ORIGINS:
            await websocket.close(code=1008)
            return
        try:
            controller = manager.get(session_id)
        except KeyError:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        client = ClientSubscription(settings.client_queue_size)
        clients.setdefault(session_id, set()).add(client)
        unsubscribe = controller.bus.subscribe(client.on_event)

        async def send():
            snapshot = controller.snapshot()
            await websocket.send_json({"kind": "snapshot", "snapshot": snapshot.model_dump()})
            state = (snapshot.phase, snapshot.feedback_status, snapshot.error)
            while True:
                if client.replaced or client.overflow:
                    await websocket.close(
                        code=1000 if client.replaced else 1013,
                        reason="session_replaced"
                        if client.replaced
                        else "resynchronize_from_snapshot",
                    )
                    return
                try:
                    event = await asyncio.wait_for(client.queue.get(), timeout=0.1)
                except TimeoutError:
                    event = None
                if event:
                    await websocket.send_json({"kind": "event", "event": event.model_dump()})
                snapshot = controller.snapshot()
                current_state = (snapshot.phase, snapshot.feedback_status, snapshot.error)
                if state != current_state:
                    await websocket.send_json(
                        {"kind": "snapshot", "snapshot": snapshot.model_dump()}
                    )
                    state = current_state

        async def receive():
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                pass

        tasks = [asyncio.create_task(send()), asyncio.create_task(receive())]
        try:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        finally:
            unsubscribe()
            clients[session_id].discard(client)
            if not clients[session_id]:
                del clients[session_id]
            for task in tasks:
                task.cancel()
            for task in tasks:
                with suppress(asyncio.CancelledError, WebSocketDisconnect, RuntimeError):
                    await task

    frontend = Path(__file__).resolve().parents[3] / "frontend" / "dist"
    if frontend.is_dir():
        app.mount("/", StaticFiles(directory=frontend, html=True), name="frontend")
    else:

        @app.get("/")
        def setup_notice():
            return {
                "message": "Build the local frontend with npm run build in frontend/.",
                "health": "/api/health",
            }

    return app


app = create_app()
