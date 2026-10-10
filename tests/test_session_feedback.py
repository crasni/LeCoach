import asyncio
import json

import pytest

from checks.coaching.feedback_replay import evaluate
from checks.coaching.session_feedback import main
from lecoach.contracts import Feedback
from lecoach.engagement import RuleConfig
from tests.test_feedback import completed, speech, transition


def save(tmp_path, session):
    path = tmp_path / "completed.json"
    path.write_text(session.model_dump_json(), encoding="utf-8")
    return str(path)


def test_saved_record_uses_existing_canonical_feedback_and_explicit_citations(tmp_path, capsys):
    sessions, expected, _ = asyncio.run(evaluate("weak_to_improved"))
    assert main([save(tmp_path, sessions[0]), "--format", "json"]) == 0
    report = Feedback.model_validate_json(capsys.readouterr().out)
    assert report == expected[0]
    assert [m.timestamp_s for m in report.moments] == [10.0, 25.0, 40.0]


def test_text_timeline_excludes_private_transcript_text(tmp_path, capsys):
    sessions, _, _ = asyncio.run(evaluate("late_final_and_duplicates"))
    value = sessions[0].model_dump()
    for e in value["events"]:
        if e["type"] == "speech.transcript":
            e["payload"]["text"] = "PRIVATE TRANSCRIPT DO NOT DISPLAY"
    path = tmp_path / "private.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    main([str(path), "--timeline"])
    output = capsys.readouterr().out
    assert "PRIVATE TRANSCRIPT" not in output
    assert "speech.transcript" in output
    assert "session.completed" in output
    assert "not enough reliable information" in output
    assert sorted(p.name for p in tmp_path.iterdir()) == ["private.json"]


def test_empty_and_repeated_sessions_remain_separate(tmp_path, capsys):
    for case in ["empty_session", "repeated_sessions"]:
        sessions, reports, _ = asyncio.run(evaluate(case))
        for session, expected in zip(sessions, reports, strict=True):
            main([save(tmp_path, session), "--format", "json"])
            actual = Feedback.model_validate_json(capsys.readouterr().out)
            assert actual == expected
            assert actual.moments == []


def test_drain_timeout_is_preserved(tmp_path, capsys):
    sessions, reports, _ = asyncio.run(evaluate("drain_timeout"))
    main([save(tmp_path, sessions[0]), "--format", "json"])
    assert Feedback.model_validate_json(capsys.readouterr().out) == reports[0]
    assert any("did not finish" in text for text in reports[0].limitations)


def test_actual_engine_freshness_config_is_used(tmp_path, capsys):
    session = completed(speech(), transition(at=12.0))
    rules = tmp_path / "rules.json"
    rules.write_text(RuleConfig(speech_stale_s=1.0).model_dump_json(), encoding="utf-8")
    main([save(tmp_path, session), "--rules", str(rules), "--format", "json"])
    report = Feedback.model_validate_json(capsys.readouterr().out)
    assert report.moments == []
    assert any("left out" in text for text in report.limitations)


def test_invalid_foreign_or_unfinished_log_fails_without_echoing_input(tmp_path, capsys):
    session = completed(speech(), transition()).model_dump()
    foreign = json.loads(json.dumps(session))
    foreign["events"][1]["session_id"] = "PRIVATE CONTENT"
    unfinished = json.loads(json.dumps(session))
    unfinished["events"] = [e for e in unfinished["events"] if e["type"] != "session.completed"]
    path = tmp_path / "bad.json"
    for value in [foreign, unfinished, {"PRIVATE CONTENT": "INVALID"}]:
        path.write_text(json.dumps(value), encoding="utf-8")
        with pytest.raises(SystemExit) as error:
            main([str(path)])
        assert error.value.code == 2
        output = capsys.readouterr()
        assert output.out == ""
        assert "PRIVATE CONTENT" not in output.err
        assert "valid canonical CompletedSession" in output.err


def test_invalid_rules_and_mixed_output_fail_explicitly(tmp_path, capsys):
    path = save(tmp_path, completed())
    rules = tmp_path / "rules.json"
    rules.write_text('{"speech_stale_s": -1}', encoding="utf-8")
    for args in [[path, "--rules", str(rules)], [path, "--format", "json", "--timeline"]]:
        with pytest.raises(SystemExit) as error:
            main(args)
        assert error.value.code == 2
        assert capsys.readouterr().out == ""
