"""Root composition checks with synthetic capture, real engine/recorder/coach."""

from unittest import IsolatedAsyncioTestCase, TestCase, mock

from fastapi.testclient import TestClient

from lecoach.api.app import create_app
from lecoach.cli import main
from lecoach.contracts.interfaces import SessionConfig
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.fixtures import FixtureRepository, remap
from lecoach.runtime.live import prepare_live_factory
from lecoach.runtime.session import SessionManager
from lecoach.speech.whisper import ModelUnavailable
from tests.helpers import Capture


class LiveFactoryTests(IsolatedAsyncioTestCase):
    async def test_shutdown_of_prepared_session_never_opens_devices(self):
        speech, vision = Capture(), Capture()
        with (
            mock.patch("lecoach.runtime.live.warm_up", return_value=object()),
            mock.patch("lecoach.runtime.live.prewarm"),
            mock.patch("lecoach.runtime.live.build_speech_adapter", return_value=speech),
            mock.patch("lecoach.runtime.live.build_vision_adapter", return_value=vision),
        ):
            manager = SessionManager(prepare_live_factory())
            controller = manager.create(SessionConfig(mode="live"), clock=FakeClock())
            await manager.shutdown()
            self.assertEqual(
                (speech.starts, vision.starts, speech.stops, vision.stops), (0, 0, 0, 0)
            )
            self.assertEqual(controller.phase, "completed")
            self.assertEqual(controller.feedback_status, "ready")
            self.assertEqual(controller.feedback.moments, [])
            self.assertEqual(controller.feedback.duration_s, 0.0)

    async def test_repeated_sessions_compute_feedback_with_fresh_components(self):
        speech, vision = [Capture(), Capture()], [Capture(), Capture()]
        model = object()
        with (
            mock.patch("lecoach.runtime.live.warm_up", return_value=model) as warm,
            mock.patch("lecoach.runtime.live.prewarm"),
            mock.patch("lecoach.runtime.live.build_speech_adapter", side_effect=speech) as build,
            mock.patch("lecoach.runtime.live.build_vision_adapter", side_effect=vision),
        ):
            factory = prepare_live_factory()
            fixture = factory(SessionConfig())
            self.assertIsNone(fixture.speech)
            self.assertIsNone(fixture.recorder)
            self.assertIsNone(fixture.feedback)
            self.assertEqual(build.call_count, 1)
            self.assertTrue(all(adapter.starts == 0 for adapter in speech + vision))
            manager = SessionManager(factory)
            completed = []
            for _ in range(2):
                clock = FakeClock()
                controller = manager.create(SessionConfig(mode="live"), clock=clock)
                try:
                    await controller.start()
                    case = FixtureRepository().load("weak_to_improved")
                    for event in case.events:
                        if event.source in ("speech", "vision"):
                            clock.advance_to(max(clock.now(), event.timestamp_s))
                            self.assertTrue(
                                controller.emit(
                                    remap(event, event.session_id, controller.session_id),
                                )
                            )
                    clock.advance_to(50.0)
                finally:
                    await manager.shutdown()
                self.assertEqual(controller.feedback_status, "ready")
                self.assertEqual(
                    [m.timestamp_s for m in controller.feedback.moments], [10.0, 25.0, 40.0]
                )
                self.assertEqual(controller.feedback.limitations, [])
                self.assertEqual(controller.snapshot().output_provenance, "computed")
                completed.append(controller)
            self.assertNotEqual(completed[0].session_id, completed[1].session_id)
            self.assertIsNot(completed[0].components.recorder, completed[1].components.recorder)
            self.assertEqual(warm.call_count, 1)
            self.assertEqual(build.call_count, 2)
            self.assertTrue(
                all(call.kwargs["transcriber"] is model for call in build.call_args_list)
            )
            self.assertTrue(
                all(
                    adapter.starts == 1 and adapter.stops == 1 and adapter.released
                    for adapter in speech + vision
                )
            )


class LiveApiTests(TestCase):
    def test_failed_inputs_return_generated_limitations_and_release(self):
        speech, vision = Capture(fail=True), Capture(fail=True)
        with (
            mock.patch("lecoach.runtime.live.warm_up", side_effect=ModelUnavailable("missing")),
            mock.patch("lecoach.runtime.live.prewarm"),
            mock.patch("lecoach.runtime.live.build_speech_adapter", return_value=speech) as build,
            mock.patch("lecoach.runtime.live.build_vision_adapter", return_value=vision),
        ):
            factory = prepare_live_factory()
            self.assertIsNone(build.call_args.kwargs["transcriber"])
            with TestClient(create_app(factory)) as client:
                self.assertTrue(client.get("/api/health").json()["live_integrated"])
                session_id = client.post("/api/sessions", json={"mode": "live"}).json()[
                    "session_id"
                ]
                self.assertEqual((speech.starts, vision.starts), (0, 0))
                with client.websocket_connect(f"/api/sessions/{session_id}/events") as ws:
                    ws.receive_json()
                    self.assertEqual(
                        client.post(f"/api/sessions/{session_id}/start").status_code, 200
                    )
                    stopped = client.post(f"/api/sessions/{session_id}/stop").json()
                self.assertEqual(stopped["feedback_status"], "ready")
                self.assertEqual(stopped["incomplete_sources"], [])
                self.assertEqual(
                    stopped["latest_events"]["engagement.state"]["payload"]["state"], "NEUTRAL"
                )
                feedback = client.get(f"/api/sessions/{session_id}/feedback").json()
                self.assertEqual(feedback["moments"], [])
                self.assertTrue(
                    any("speech" in limitation.lower() for limitation in feedback["limitations"])
                )
                self.assertTrue(
                    any("camera" in limitation.lower() for limitation in feedback["limitations"])
                )
                self.assertTrue(speech.released and vision.released)

    def test_cli_live_is_opt_in_and_prepares_before_serving(self):
        with mock.patch("sys.argv", ["lecoach", "serve"]), mock.patch("uvicorn.run") as run:
            main()
            run.assert_called_once_with("lecoach.api.app:app", host="127.0.0.1", port=8000)
        with (
            mock.patch(
                "sys.argv", ["lecoach", "serve", "--live", "--speech-model-dir", "/tmp/models"]
            ),
            mock.patch("lecoach.runtime.live.prepare_live_factory") as prepare,
            mock.patch("lecoach.api.app.create_app") as create,
            mock.patch("uvicorn.run") as run,
        ):
            main()
            self.assertEqual(prepare.call_args.args[0].model_dir, "/tmp/models")
            create.assert_called_once_with(prepare.return_value)
            run.assert_called_once_with(create.return_value, host="127.0.0.1", port=8000)
