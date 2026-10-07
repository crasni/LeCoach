from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from lecoach.api.app import ClientSubscription, create_app
from lecoach.contracts.interfaces import Components, RuntimeSettings
from tests.helpers import Capture, Recorder, event


def test_health_live_unavailable_and_invalid_cases():
    with TestClient(create_app()) as client:
        assert client.get("/api/health").json()["live_integrated"] is False
        assert client.post("/api/sessions", json={"mode": "live"}).status_code == 503
        assert client.post("/api/sessions", json={"fixture_case": "../secret"}).status_code == 422
        assert (
            client.post("/api/sessions", json={"fixture_case": "repeated_sessions"}).status_code
            == 422
        )
        assert client.get("/api/sessions/unknown").status_code == 404


def test_subscribe_start_complete_and_feedback():
    with TestClient(create_app()) as client:
        prepared = client.post("/api/sessions", json={"fixture_case": "empty_session"}).json()
        session_id = prepared["session_id"]
        assert prepared["phase"] == "prepared"
        assert client.post(f"/api/sessions/{session_id}/start").status_code == 409
        assert client.post("/api/sessions", json={}).status_code == 409
        with client.websocket_connect(f"/api/sessions/{session_id}/events") as websocket:
            assert websocket.receive_json()["snapshot"]["phase"] == "prepared"
            assert client.post(f"/api/sessions/{session_id}/start").status_code == 200
            for _ in range(12):
                message = websocket.receive_json()
                if (
                    message["kind"] == "snapshot"
                    and message["snapshot"]["feedback_status"] == "ready"
                ):
                    break
            else:
                raise AssertionError("completion snapshot missing")
        response = client.get(f"/api/sessions/{session_id}/feedback").json()
        assert response["session_id"] == session_id
        assert response["moments"] == []
        assert client.post(f"/api/sessions/{session_id}/stop").json()["phase"] == "completed"
        assert client.get(f"/api/sessions/{session_id}/preview").status_code == 503


def test_reconnect_does_not_restart_and_early_stop_has_no_authored_feedback():
    with TestClient(create_app()) as client:
        session_id = client.post("/api/sessions", json={}).json()["session_id"]
        with client.websocket_connect(f"/api/sessions/{session_id}/events") as websocket:
            websocket.receive_json()
            client.post(f"/api/sessions/{session_id}/start")
            websocket.receive_json()
        with client.websocket_connect(f"/api/sessions/{session_id}/events") as websocket:
            snapshot = websocket.receive_json()["snapshot"]
            assert snapshot["phase"] == "running"
            assert snapshot["session_id"] == session_id
            assert client.post(f"/api/sessions/{session_id}/start").status_code == 200
            stopped = client.post(f"/api/sessions/{session_id}/stop").json()
            assert stopped["phase"] == "completed"
            assert stopped["feedback_status"] == "unavailable"
            assert client.get(f"/api/sessions/{session_id}/feedback").status_code == 409
        new = client.post("/api/sessions", json={}).json()
        assert new["session_id"] != session_id
        assert client.get(f"/api/sessions/{session_id}").status_code == 404
        assert new["transcript"] == []


def test_untrusted_browser_origin_is_rejected():
    with TestClient(create_app()) as client:
        assert (
            client.post(
                "/api/sessions", json={}, headers={"origin": "https://example.com"}
            ).status_code
            == 403
        )


def test_slow_client_queue_never_blocks_other_subscribers():
    slow = ClientSubscription(1)
    healthy = ClientSubscription(4)
    for name in ("first", "second", "third"):
        current = event(event_id=name)
        slow.on_event(current)
        healthy.on_event(current)
    assert slow.overflow
    assert slow.queue.qsize() == 1
    assert healthy.queue.qsize() == 3


def test_overflow_closes_browser_without_losing_recorder_events():
    recorder = Recorder()

    class Burst(Capture):
        async def start(self, context):
            await super().start(context)
            for index in range(20):
                context.emit(event(context.session_id, f"burst-{index}", 0.0))

    app = create_app(
        lambda config: Components(speech=Burst(), recorder=recorder),
        RuntimeSettings(client_queue_size=1),
    )
    with TestClient(app) as client:
        session_id = client.post("/api/sessions", json={"mode": "live"}).json()["session_id"]
        with client.websocket_connect(f"/api/sessions/{session_id}/events") as websocket:
            websocket.receive_json()
            client.post(f"/api/sessions/{session_id}/start")
            try:
                while True:
                    websocket.receive_json()
            except WebSocketDisconnect as error:
                assert error.code == 1013
        assert sum(e.event_id.startswith("burst-") for e in recorder.events) == 20
        assert client.post(f"/api/sessions/{session_id}/stop").json()["phase"] == "completed"
