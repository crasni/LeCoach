"""VIS-01 vision lane: features, labeled fixture, adapter lifecycle and engine handoff.

Everything here is synthetic (fake camera/pose backends and the generated keypoint
fixture). It does not establish real-camera behavior; see the VIS-01/VIS-02 Issues.
"""

import asyncio
import json
import threading
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase

from lecoach.contracts import parse_event
from lecoach.contracts.interfaces import Components, SessionConfig
from lecoach.engagement.engine import RuleEngine
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.session import SessionController
from lecoach.vision.adapter import LocalVisionAdapter
from lecoach.vision.backend import VisionUnavailable
from lecoach.vision.config import VisionConfig
from lecoach.vision.features import FrameFeatures, Keypoint, PoseFrame, WindowAggregator
from lecoach.vision.local_backend import MediaPipePose

FIXTURE = Path(__file__).parents[1] / "checks/vision/fixtures/labeled_session.json"


def load_fixture():
    data = json.loads(FIXTURE.read_text())
    frames = [
        PoseFrame(f["t"], f["person"], {k: Keypoint(*v) for k, v in f["kp"].items()})
        for f in data["frames"]
    ]
    return data, frames


def frontal(t=0.5, yaw_offset=0.0, **overrides):
    points = {
        "nose": (320 + yaw_offset, 150),
        "left_ear": (280, 155),
        "right_ear": (360, 155),
        "left_shoulder": (240, 250),
        "right_shoulder": (400, 250),
        "left_hip": (265, 430),
        "right_hip": (375, 430),
        "left_wrist": (230, 400),
        "right_wrist": (410, 400),
    }
    points.update(overrides)
    return PoseFrame(
        t, True, {k: Keypoint(x, y, 0.9) for k, (x, y) in points.items() if x is not None}
    )


class FeatureTests(TestCase):
    def setUp(self):
        self.config = VisionConfig()

    def test_facing_cues(self):
        front = FrameFeatures(frontal(), self.config)
        self.assertAlmostEqual(front.head_facing(), 1.0, places=2)
        self.assertGreater(front.facing(), 0.95)  # body cue: front-on shoulders
        half = FrameFeatures(frontal(yaw_offset=20), self.config).facing()
        self.assertAlmostEqual(half, 0.5, places=2)
        profile = frontal(right_ear=(None, None))
        self.assertEqual(FrameFeatures(profile, self.config).facing(), 0.0)
        # Back turned / low confidence: no nose -> unknown, not "away".
        no_nose = frontal(nose=(None, None))
        self.assertIsNone(FrameFeatures(no_nose, self.config).facing())
        # A turned torso caps the head cue.
        narrow = frontal(left_shoulder=(300, 250), right_shoulder=(340, 250))
        self.assertLess(FrameFeatures(narrow, self.config).facing(), 0.2)

    def test_unavailable_windows_have_null_scores(self):
        aggregator = WindowAggregator(self.config)
        empty = aggregator.finish(1.0)
        self.assertEqual(empty[0].availability, "unavailable")
        self.assertIsNone(empty[0].person_present)
        aggregator = WindowAggregator(self.config)
        for i in range(10):
            aggregator.add(PoseFrame(i / 10 + 0.05, False))
        [absent] = aggregator.finish(1.0)
        self.assertEqual(
            (absent.person_present, absent.pose_available, absent.facing_score),
            (False, False, None),
        )
        self.assertIsNone(absent.activity_score)

    def test_trailing_window_clipped_to_capture_end(self):
        aggregator = WindowAggregator(self.config)
        windows = [w for i in range(17) for w in aggregator.add(frontal(i / 10 + 0.01))]
        windows += aggregator.finish(1.7)
        self.assertEqual([(w.window_start_s, w.window_end_s) for w in windows], [(0, 1), (1, 1.7)])
        aggregator = WindowAggregator(self.config)
        aggregator.add(frontal(0.5))
        self.assertEqual(len(aggregator.finish(1.3)), 1)  # 0.3 s tail is dropped

    def test_out_of_order_and_invalid_frames_ignored(self):
        aggregator = WindowAggregator(self.config)
        aggregator.add(frontal(0.5))
        self.assertEqual(aggregator.add(frontal(0.4)), [])
        self.assertEqual(aggregator.add(frontal(float("nan"))), [])
        [window] = aggregator.finish(1.0)
        self.assertEqual(window.frames, 1)

    def test_config_validation(self):
        for bad in (
            {"window_s": 0},
            {"min_final_window_s": 2.0},
            {"activity_noise_floor": 3.0},
            {"min_decision_fraction": 1.5},
            {"shoulder_ratio_side": 1.0},
        ):
            with self.subTest(bad), self.assertRaises(ValueError):
                VisionConfig(**bad)


class LabeledFixtureTests(TestCase):
    def test_fixture_is_current(self):
        import runpy

        module = runpy.run_path(str(FIXTURE.parents[1] / "make_fixture.py"))
        self.assertEqual(FIXTURE.read_text(), module["render"](), "rerun make_fixture.py")

    def test_every_window_matches_its_label(self):
        data, frames = load_fixture()
        limits = data["label_thresholds"]
        aggregator = WindowAggregator()
        windows = [w for f in frames for w in aggregator.add(f)]
        windows += aggregator.finish(data["duration_s"])
        self.assertEqual(len(windows), data["duration_s"])
        for window in windows:
            label = next(
                s["label"]
                for s in data["segments"]
                if s["start_s"] <= window.window_start_s < s["end_s"]
            )
            with self.subTest(window=window.window_start_s, label=label):
                parse_event(
                    {
                        "schema_version": 0,
                        "session_id": "fixture",
                        "event_id": f"vision-{window.window_start_s}",
                        "source": "vision",
                        "type": "vision.metrics",
                        "timestamp_s": window.window_end_s,
                        "payload": window.payload(),
                    }
                )
                self.assertEqual(window.availability, "available")
                self.assertEqual(window.person_present, label["person_present"])
                if "pose_available" in label:
                    self.assertEqual(window.pose_available, label["pose_available"])
                facing, activity = window.facing_score, window.activity_score
                if label["facing"] == "toward":
                    self.assertGreaterEqual(facing, limits["toward_facing_at_least"])
                elif label["facing"] == "away":
                    self.assertLess(facing, limits["away_facing_below"])
                else:
                    self.assertIsNone(facing)
                if label["activity"] == "low":
                    self.assertLessEqual(activity, limits["low_activity_at_most"])
                elif label["activity"] == "active":
                    self.assertGreaterEqual(activity, limits["active_activity_at_least"])
                else:
                    self.assertIsNone(activity)


class ReplaySource:
    """Fake camera: each read advances the session FakeClock to the frame's capture time."""

    def __init__(self, clock, frames, fail_open=None, gate=None):
        self.clock, self.frames, self.fail_open, self.gate = clock, list(frames), fail_open, gate
        self.opened = self.closed = 0
        self.position = 0
        self.pace = None  # optional callable(t) that blocks to keep the loop in step
        self.last = None

    def open(self):
        if self.fail_open:
            raise VisionUnavailable(self.fail_open)
        self.opened += 1

    def read(self):
        if self.gate is not None:
            self.gate.wait(1)
        if self.position >= len(self.frames):
            # Exhausted: behave like a frozen camera (same frame, no new capture time).
            threading.Event().wait(0.002)
            return self.last
        frame = self.frames[self.position]
        self.position += 1
        if frame is not None:
            if self.pace is not None:
                self.pace(frame.timestamp_s)
            self.clock.advance_to(max(self.clock.now(), frame.timestamp_s))
            self.last = frame
        return frame

    def close(self):
        self.closed += 1


class PassThroughPose:
    """Fake model: the 'frame' already is a PoseFrame."""

    def __init__(self, fail_open=None):
        self.fail_open, self.closed = fail_open, 0

    def open(self):
        if self.fail_open:
            raise VisionUnavailable(self.fail_open)

    def estimate(self, frame, timestamp_s):
        return frame

    def close(self):
        self.closed += 1


class AdapterTests(IsolatedAsyncioTestCase):
    def build(
        self, frames, fail_camera=None, fail_model=None, encoder=None, config=None, gate=None
    ):
        clock = FakeClock()
        source = ReplaySource(clock, frames, fail_camera, gate)
        model = PassThroughPose(fail_model)
        adapter = LocalVisionAdapter(
            lambda: source, lambda: model, encoder=encoder, config=config or VisionConfig()
        )
        engine = RuleEngine()
        controller = SessionController(
            SessionConfig(mode="live", drain_timeout_s=2.0, startup_timeout_s=2.0),
            Components(vision=adapter, engagement=engine),
            session_id="vision-test",
            clock=clock,
        )
        events = []
        controller.bus.subscribe(events.append)
        return controller, clock, adapter, source, model, events

    async def wait_for(self, predicate, timeout=5.0):
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while not predicate():
            if loop.time() > deadline:
                self.fail("timed out waiting for vision events")
            await asyncio.sleep(0.005)

    async def test_fixture_session_through_controller_and_engine(self):
        data, frames = load_fixture()
        controller, clock, adapter, source, model, events = self.build(frames)

        def pace(t):
            # Keep fake capture within ~1 s of emitted windows, as a real camera
            # would, so the engine does not see artificially stale observations.
            for _ in range(5000):
                if adapter.stats.windows_emitted >= int(t) - 1:
                    return
                threading.Event().wait(0.001)

        source.pace = pace
        await controller.start()
        await self.wait_for(lambda: source.position >= len(frames))
        await self.wait_for(lambda: clock.now() >= 39.95 and adapter.stats.windows_emitted >= 39)
        await controller.stop()

        self.assertTrue(adapter.released)
        self.assertEqual((source.closed, model.closed), (1, 1))
        self.assertEqual(controller.incomplete_sources, [])
        metrics = [e for e in events if e.type == "vision.metrics"]
        self.assertEqual(len(metrics), 40)
        self.assertTrue(all(e.timestamp_s == e.payload.window_end_s for e in metrics))
        self.assertLessEqual(metrics[-1].timestamp_s, controller.capture_end_s)
        statuses = [
            e.payload.reason for e in events if e.type == "signal.status" and e.source == "vision"
        ]
        self.assertEqual(statuses, ["capture_started"])

        # Engine handoff: sustained looking away (16-26 s) is the only negative.
        states = [e for e in events if e.type == "engagement.state"]
        codes = {r.code for e in states for r in e.payload.reasons}
        self.assertIn("facing_away_sustained", codes)
        self.assertIn("facing_audience", codes)
        bored = [e for e in states if e.payload.state == "BORED"]
        self.assertTrue(bored and all(16 + 6 <= e.timestamp_s <= 27 for e in bored))
        for state in states:
            for reason in state.payload.reasons:
                cited = [e for e in metrics if e.event_id in reason.source_event_ids]
                self.assertTrue(cited, reason)
                if reason.code == "facing_away_sustained":
                    self.assertTrue(all(16 <= e.payload.window_start_s < 26 for e in cited))
        # No person / undecided / low confidence never produce a negative state.
        late_negative = [
            e for e in states if e.timestamp_s >= 27 and e.payload.state in ("BORED", "CONFUSED")
        ]
        self.assertEqual(late_negative, [])

    async def test_camera_and_model_failures_are_unavailable_input(self):
        for kwargs, reason in (
            ({"fail_camera": "camera_unavailable"}, "camera_unavailable"),
            ({"fail_model": "pose_model_missing"}, "pose_model_missing"),
        ):
            with self.subTest(reason):
                controller, _, adapter, source, model, events = self.build([], **kwargs)
                await controller.start()
                self.assertEqual(controller.input_status["vision"]["reason"], reason)
                self.assertEqual(controller.input_status["vision"]["availability"], "unavailable")
                snapshot = await controller.stop()
                self.assertTrue(adapter.released)
                self.assertEqual(model.closed, 1)
                self.assertEqual(source.opened, 0)
                self.assertEqual([e for e in events if e.type == "vision.metrics"], [])
                self.assertEqual(snapshot.phase, "completed")

    async def test_repeated_read_failures_report_error_and_release(self):
        config = VisionConfig(max_consecutive_read_failures=3)
        frames = [frontal(0.05), None, None, None, frontal(0.5)]
        controller, _, adapter, source, _, events = self.build(frames, config=config)
        await controller.start()
        await self.wait_for(lambda: source.closed == 1)
        self.assertEqual(controller.input_status["vision"]["reason"], "camera_read_failed")
        self.assertEqual(controller.input_status["vision"]["availability"], "error")
        await controller.stop()
        self.assertTrue(adapter.released)

    async def test_preview_latest_frame_capped_and_cleared(self):
        sizes = iter([10, 600_000, 20] + [30] * 100)

        def encoder(frame, quality):
            return b"x" * next(sizes)

        config = VisionConfig(preview_fps=1000, preview_max_bytes=512_000)
        frames = [frontal(0.05 + i / 100) for i in range(3)]
        gate = threading.Event()
        controller, _, adapter, source, _, _ = self.build(
            frames, encoder=encoder, config=config, gate=gate
        )
        await controller.start()
        self.assertIsNone(adapter.preview_jpeg())
        gate.set()
        await self.wait_for(lambda: source.position >= 3)
        await self.wait_for(lambda: adapter.preview_jpeg() == b"x" * 20)
        await controller.stop()
        self.assertIsNone(adapter.preview_jpeg())

    async def test_stop_and_drain_are_idempotent(self):
        controller, clock, adapter, source, _, events = self.build([frontal(0.05), frontal(0.6)])
        await controller.start()
        await self.wait_for(lambda: source.position >= 2)
        clock.advance_to(1.2)
        await adapter.stop_capture(1.2)
        await adapter.stop_capture(5.0)  # first capture end wins
        await adapter.drain()
        await adapter.drain()
        await controller.stop()
        metrics = [e for e in events if e.type == "vision.metrics"]
        self.assertEqual([e.timestamp_s for e in metrics], [1.0])
        self.assertEqual(source.closed, 1)

    async def test_stop_before_open_finishes_releases_camera(self):
        opened = threading.Event()
        release = threading.Event()
        clock = FakeClock()
        source = ReplaySource(clock, [])

        class SlowPose(PassThroughPose):
            def open(self):
                opened.set()
                release.wait(2)

        model = SlowPose()
        adapter = LocalVisionAdapter(lambda: source, lambda: model)
        from lecoach.contracts.interfaces import SessionContext

        context = SessionContext("s", clock, lambda e: True, SessionConfig(mode="live"))
        start = asyncio.create_task(adapter.start(context))
        await asyncio.to_thread(opened.wait, 2)
        start.cancel()
        stop = asyncio.create_task(adapter.stop_capture(0.0))
        release.set()
        await asyncio.gather(start, return_exceptions=True)
        await stop
        await adapter.drain()
        self.assertTrue(adapter.released)
        self.assertEqual((source.closed, model.closed), (1, 1))


class LocalBackendTests(TestCase):
    def test_missing_model_is_reported_not_raised_as_crash(self):
        model = MediaPipePose("models/definitely-missing.task")
        with self.assertRaises(VisionUnavailable) as caught:
            model.open()
        self.assertIn(caught.exception.reason, ("pose_model_missing", "pose_runtime_missing"))


class ProbeJudgeTests(TestCase):
    def test_segment_verdicts(self):
        from lecoach.vision.probe import judge

        def w(facing, activity, person=True):
            return {"facing_score": facing, "activity_score": activity, "person_present": person}

        self.assertTrue(judge("toward_still", [w(0.9, 0.05)] * 5)["pass"])
        self.assertFalse(judge("toward_still", [w(0.9, 0.7)] * 5)["pass"])
        self.assertTrue(judge("toward_active", [w(0.8, 0.6)] * 5)["pass"])
        self.assertTrue(judge("away", [w(0.1, 0.0)] * 5)["pass"])
        self.assertTrue(judge("away", [w(None, None)] * 5)["pass"])  # unknown is not "toward"
        self.assertFalse(judge("away", [w(0.8, 0.0)] * 5)["pass"])
        self.assertTrue(judge("no_person", [w(None, None, False)] * 5)["pass"])
        self.assertFalse(judge("no_person", [])["pass"])


class ProbeViewerTests(TestCase):
    def setUp(self):
        try:
            import numpy  # noqa: F401

            from lecoach.vision.viewer import ProbeViewer
        except ImportError:
            self.skipTest("opencv/numpy not installed")
        self.viewer = ProbeViewer()

    def test_compose_draws_mirrored_overlay_without_mutating_frame(self):
        import numpy as np

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        image = self.viewer.compose(frame, frontal(), ["prompt", "metrics"])
        self.assertEqual(image.shape, frame.shape)
        self.assertEqual(int(frame.sum()), 0)  # caller's frame untouched
        self.assertGreater(int(image.sum()), 0)
        # Nose at x=320 stays centred; the left shoulder (x=240) is drawn mirrored at 399.
        self.assertGreater(int(image[250, 395:405].sum()), 0)

    def test_show_without_display_degrades_to_headless(self):
        import numpy as np

        self.viewer.on_frame(np.zeros((48, 64, 3), dtype=np.uint8), frontal())
        self.assertTrue(self.viewer.show(["x"]))  # never aborts the probe
        self.viewer.close()


class ProbeRunTests(TestCase):
    def test_probe_runs_scripted_segments_and_releases_camera(self):
        from unittest import mock

        from lecoach.vision import probe

        frames = [frontal(i / 10 + 0.05) for i in range(10_000)]

        class WallSource(ReplaySource):
            def read(self):
                threading.Event().wait(0.02)
                return frames[0]

        made = {}

        def fake_build(model, camera, config, on_frame=None):
            made["source"] = WallSource(FakeClock(), [])
            made["adapter"] = LocalVisionAdapter(
                lambda: made["source"], PassThroughPose, config=config, on_frame=on_frame
            )
            return made["adapter"]

        with (
            mock.patch.object(probe, "build_local_adapter", fake_build),
            mock.patch.object(probe, "READY_S", 0.1),
            mock.patch.object(probe, "SETTLE_S", 0.0),
        ):
            summary = asyncio.run(probe.run(probe_args(segment_s=2.1)))
        self.assertFalse(summary["aborted"])
        self.assertEqual(list(summary["segments"]), [name for name, _ in probe.SCRIPT])
        self.assertTrue(summary["camera_released"])
        self.assertEqual(made["source"].closed, 1)
        self.assertGreater(summary["stats"]["frames_inferred"], 0)
        # A still frontal pose passes the "toward" segments it fully covers.
        self.assertTrue(summary["segments"]["toward_still"]["pass"])
        self.assertFalse(summary["segments"]["no_person"]["pass"])


def probe_args(**overrides):
    import argparse

    values = dict(
        model=None, camera=None, segment_s=10.0, max_fps=10.0, out=None, verbose=False, show=False
    )
    values.update(overrides)
    return argparse.Namespace(**values)
