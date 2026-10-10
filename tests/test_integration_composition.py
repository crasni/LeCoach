"""Merged producer/engine/recorder composition with synthetic device/model seams.

No microphone, camera, model inference or generated coaching is exercised here.
"""

import asyncio
from unittest import IsolatedAsyncioTestCase

from lecoach.coaching.recorder import InMemorySessionRecorder
from lecoach.contracts.interfaces import Components, SessionConfig
from lecoach.engagement.engine import RuleEngine
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.session import SessionManager
from lecoach.speech import MicrophoneNotFound, SpeechAdapter, SpeechConfig
from lecoach.vision.adapter import LocalVisionAdapter
from tests.speech_doubles import ScriptedSegmenter, ScriptedSource, ScriptedTranscriber
from tests.test_vision import PassThroughPose, ReplaySource, frontal


class MergedCompositionTests(IsolatedAsyncioTestCase):
    async def wait_for(self, predicate):
        async with asyncio.timeout(3.0):
            while not predicate():
                await asyncio.sleep(0.005)

    def compose(self, *, speech_missing=False, vision_missing=False, frames=()):
        clock = FakeClock()
        source = ScriptedSource(MicrophoneNotFound() if speech_missing else None)
        speech = SpeechAdapter(
            SpeechConfig(), source, ScriptedSegmenter([(1.0, 6.0)]),
            ScriptedTranscriber(["um our weekly update is ready"]), idle_tick_s=0.01,
        )
        camera = ReplaySource(clock, frames)
        pose = PassThroughPose("pose_model_missing" if vision_missing else None)
        vision = LocalVisionAdapter(lambda: camera, lambda: pose)
        recorder = InMemorySessionRecorder()
        components = Components(
            speech=speech, vision=vision, engagement=RuleEngine(), recorder=recorder,
        )
        return clock, components, source, camera, pose

    def completed(self, controller):
        result = controller.components.recorder.complete(
            controller.capture_end_s, controller.incomplete_sources,
        )
        self.assertEqual(controller.phase, "completed")
        self.assertEqual(controller.incomplete_sources, [])
        self.assertEqual(controller.feedback_status, "unavailable")
        self.assertTrue(all(e.session_id == controller.session_id for e in result.events))
        self.assertTrue(all(e.timestamp_s <= result.duration_s for e in result.events))
        ids = {e.event_id for e in result.events}
        for event in result.events:
            if event.type == "engagement.state":
                for reason in event.payload.reasons:
                    self.assertTrue(set(reason.source_event_ids) <= ids)
        self.assertEqual(controller.components.speech.errors, [])
        self.assertTrue(controller.components.vision.released)
        return result

    async def test_missing_pose_leaves_speech_and_recording_usable(self):
        clock, components, source, camera, pose = self.compose(vision_missing=True)
        manager = SessionManager(lambda config: components)
        controller = manager.create(SessionConfig(mode="live"), clock=clock)
        try:
            await controller.start()
            for reached in (2.0, 4.0, 6.0, 7.0):
                clock.advance_to(reached)
                source.push(reached)
                await self.wait_for(lambda: components.speech.analyzed_s >= reached)
        finally:
            await manager.shutdown()
        result = self.completed(controller)
        finals = [e for e in result.events
                  if e.type == "speech.transcript" and e.payload.is_final]
        self.assertEqual([e.payload.text for e in finals], ["um our weekly update is ready"])
        self.assertTrue(any(e.type == "speech.metrics" and e.payload.wpm is not None
                            for e in result.events))
        self.assertEqual(controller.input_status["vision"]["reason"], "pose_model_missing")
        self.assertFalse(any(e.type == "vision.metrics" for e in result.events))
        self.assertEqual((source.closed, camera.opened, pose.closed), (1, 0, 1))

    async def test_missing_microphone_leaves_vision_and_recording_usable(self):
        frames = [frontal(i / 10 + 0.05) for i in range(70)]
        clock, components, source, camera, pose = self.compose(
            speech_missing=True, frames=frames,
        )
        manager = SessionManager(lambda config: components)
        controller = manager.create(SessionConfig(mode="live"), clock=clock)
        try:
            await controller.start()
            await self.wait_for(lambda: camera.position == len(frames))
        finally:
            await manager.shutdown()
        result = self.completed(controller)
        self.assertEqual(controller.input_status["speech"]["reason"], "microphone_not_found")
        metrics = [e for e in result.events if e.type == "vision.metrics"]
        self.assertTrue(any(e.payload.facing_score is not None for e in metrics))
        for event in result.events:
            if event.type == "speech.metrics":
                self.assertIsNone(event.payload.wpm)
                self.assertIsNone(event.payload.filler_count)
        self.assertEqual((source.closed, camera.closed, pose.closed), (1, 1, 1))

    async def test_both_missing_stay_neutral_and_repeat_sessions_are_isolated(self):
        instances = []

        def factory(config):
            instance = self.compose(speech_missing=True, vision_missing=True)
            instances.append(instance)
            return instance[1]

        manager = SessionManager(factory)
        results = []
        for _ in range(2):
            controller = manager.create(SessionConfig(mode="live"), clock=FakeClock())
            try:
                await controller.start()
            finally:
                await manager.shutdown()
            result = self.completed(controller)
            results.append(result)
            states = [e for e in result.events if e.type == "engagement.state"]
            self.assertTrue(states)
            self.assertTrue(all(e.payload.state == "NEUTRAL" and not e.payload.reasons
                                for e in states))
            self.assertEqual(controller.input_status["speech"]["reason"],
                             "microphone_not_found")
            self.assertEqual(controller.input_status["vision"]["reason"], "pose_model_missing")
        self.assertNotEqual(results[0].session_id, results[1].session_id)
        self.assertIsNot(instances[0][1].speech, instances[1][1].speech)
        self.assertIsNot(instances[0][1].vision, instances[1][1].vision)
        self.assertIsNot(instances[0][1].recorder, instances[1][1].recorder)
        self.assertFalse(manager.current.emit(results[0].events[0]))
        with self.assertRaises(KeyError):
            manager.get(results[0].session_id)
