"""Diagnostic exports preserve the existing generator result and omit transcripts."""

import asyncio
import json
import threading
from unittest.mock import AsyncMock

import pytest

from lespeech.coaching.compose import replay_with_coaching
from lespeech.contracts import CompletedSession, Feedback, parse_event
from lespeech.contracts.interfaces import Components, SessionConfig
from lespeech.runtime.fixtures import FixtureRepository, replay_case
from scripts.live_evidence import EvidenceExports, EvidenceFeedback, evidence_factory, main


async def completed(case_name="weak_to_improved"):
    components = []
    base = replay_with_coaching()

    def factory(config):
        current = base(config)
        components.append(current)
        return current

    result = await replay_case(FixtureRepository().load(case_name), factory=factory)
    feedback = Feedback.model_validate(result["feedback"][0])
    completion = next(e for e in result["delivery_trace"] if e["type"] == "session.completed")
    session = components[0].recorder.complete(**completion["payload"])
    return session, feedback


def test_browser_feedback_identity_and_evidence_chain_are_preserved(tmp_path):
    async def check():
        session, feedback = await completed()
        transcript = parse_event({
            "schema_version": 0, "session_id": session.session_id,
            "event_id": "private-transcript", "source": "speech", "type": "speech.transcript",
            "timestamp_s": 1.0,
            "payload": {"utterance_id": "private", "revision": 0, "is_final": True,
                        "start_s": 0.0, "end_s": 1.0,
                        "text": "PRIVATE TRANSCRIPT MUST NOT BE EXPORTED"},
        })
        session = CompletedSession(
            session_id=session.session_id, duration_s=session.duration_s,
            incomplete_sources=session.incomplete_sources,
            events=sorted([*session.events, transcript], key=lambda e: (e.timestamp_s, e.event_id)),
        )
        generator = AsyncMock()
        generator.generate.return_value = feedback
        exports = EvidenceExports(tmp_path)
        wrapped = EvidenceFeedback(generator, exports, {"input": "synthetic test"})
        assert await wrapped.generate(session) is feedback
        generator.generate.assert_awaited_once_with(session)
        await exports.drain()
        saved = list(tmp_path.glob("*.json"))
        assert len(saved) == 1
        text = saved[0].read_text()
        assert "PRIVATE TRANSCRIPT" not in text
        report = json.loads(text)
        assert report["feedback"] == feedback.model_dump(mode="json")
        assert report["transcript_events_omitted"] > 0
        assert report["unresolved_or_omitted_evidence_ids"] == []
        by_id = {e["event_id"]: e for e in report["supporting_events"]}
        for moment in feedback.moments:
            assert all(eid in by_id for eid in moment.evidence_event_ids)
        assert all(e["session_id"] == session.session_id for e in by_id.values())
        assert all(e["type"] != "speech.transcript" for e in by_id.values())

    asyncio.run(check())


def test_export_io_failure_does_not_fail_feedback(tmp_path, caplog):
    async def check():
        session, feedback = await completed("empty_session")
        blocked = tmp_path / "existing-file"
        blocked.write_text("preserve")
        exports = EvidenceExports(blocked)
        generator = AsyncMock()
        generator.generate.return_value = feedback
        assert await EvidenceFeedback(generator, exports, {}).generate(session) is feedback
        await exports.drain()
        assert blocked.read_text() == "preserve"

    asyncio.run(check())
    assert "browser feedback is unaffected" in caplog.text


def test_existing_exports_are_not_overwritten(tmp_path):
    exports = EvidenceExports(tmp_path)
    exports.write("session", {"value": "original"})
    exports.write("session", {"value": "replacement"})
    assert json.loads(next(tmp_path.glob("*.json")).read_text()) == {"value": "original"}


def test_slow_export_does_not_delay_feedback(tmp_path, monkeypatch):
    async def check():
        session, feedback = await completed("empty_session")
        exports = EvidenceExports(tmp_path)
        started = asyncio.Event()
        release = threading.Event()
        loop = asyncio.get_running_loop()
        original_write = exports.write

        def slow_write(*args):
            loop.call_soon_threadsafe(started.set)
            release.wait(timeout=2)
            original_write(*args)

        monkeypatch.setattr(exports, "write", slow_write)
        generator = AsyncMock()
        generator.generate.return_value = feedback
        try:
            result = await asyncio.wait_for(
                EvidenceFeedback(generator, exports, {}).generate(session), timeout=0.5,
            )
            await asyncio.wait_for(started.wait(), timeout=1)
            assert result is feedback
            assert not list(tmp_path.glob("*.json"))
        finally:
            release.set()
            await exports.drain()
        assert len(list(tmp_path.glob("*.json"))) == 1

    asyncio.run(check())


def test_fixture_mode_and_live_capability_are_preserved(tmp_path):
    generator = AsyncMock()
    exports = EvidenceExports(tmp_path)

    def base(config):
        return Components(feedback=generator)

    base.live_integrated = False
    wrapped = evidence_factory(base, exports, {})
    assert wrapped(SessionConfig()).feedback is generator
    live = wrapped(SessionConfig(mode="live"))
    assert isinstance(live.feedback, EvidenceFeedback)
    assert live.feedback.generator is generator
    assert live.feedback.provenance["session_config"]["mode"] == "live"
    assert wrapped.live_integrated is False
    assert not list(tmp_path.iterdir())


def test_output_outside_ignored_sessions_is_rejected_before_preparation(tmp_path):
    with pytest.raises(SystemExit) as error:
        main(["--out-dir", str(tmp_path)])
    assert error.value.code == 2
