"""Serve the existing live app and export sanitized coaching evidence after stop.

Uses the sole recorder/generator; no new event collector or inference path.
Exports contain feedback, cited metrics, audience decisions and status codes,
never transcript events, raw audio/video or model weights. Devices open only
when the operator starts a browser session. This is a diagnostic launcher, not
a recording tool or a performance benchmark.
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import platform
import subprocess
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from lecoach.api.app import create_app
from lecoach.contracts import CompletedSession, Feedback
from lecoach.contracts.interfaces import FeedbackGenerator, SessionConfig
from lecoach.engagement import DEFAULT_RULES
from lecoach.runtime.live import prepare_live_factory
from lecoach.speech import SpeechConfig
from lecoach.speech.whisper import model_path

ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger(__name__)
SAFE_TYPES = {"speech.metrics", "vision.metrics", "engagement.state", "signal.status"}


def evidence_report(session: CompletedSession, feedback: Feedback, provenance: dict) -> dict:
    """Project existing completed evidence without retaining transcript contents."""
    decisions = [e for e in session.events if e.type == "engagement.state"]
    wanted = {eid for m in feedback.moments for eid in m.evidence_event_ids}
    wanted.update(e.event_id for e in decisions)
    wanted.update(eid for e in decisions for r in e.payload.reasons for eid in r.source_event_ids)
    supporting = [e for e in session.events if e.event_id in wanted and e.type in SAFE_TYPES]
    resolved = {e.event_id for e in supporting}
    return {
        "scope": "pipeline diagnostic evidence; presenter/browser review remains separate",
        "exported_at_utc": datetime.now(UTC).isoformat(),
        "provenance": provenance,
        "feedback": feedback.model_dump(mode="json"),
        "incomplete_sources": session.incomplete_sources,
        "supporting_events": [e.model_dump(mode="json") for e in supporting],
        "input_status_events": [
            e.model_dump(mode="json") for e in session.events if e.type == "signal.status"
        ],
        "unresolved_or_omitted_evidence_ids": sorted(wanted - resolved),
        "transcript_events_omitted": sum(e.type == "speech.transcript" for e in session.events),
    }


class EvidenceExports:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.pending: set[asyncio.Task] = set()

    def schedule(self, session_id: str, report: dict) -> None:
        # File I/O is outside the feedback path and its existing timeout.
        task = asyncio.create_task(asyncio.to_thread(self.write, session_id, report))
        self.pending.add(task)
        task.add_done_callback(self.pending.discard)

    def write(self, session_id: str, report: dict) -> None:
        name = hashlib.sha256(session_id.encode()).hexdigest()
        path = self.directory / f"session-{name}.json"
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as output:
                json.dump(report, output, indent=2)
                output.write("\n")
        except (OSError, UnicodeError):
            log.warning("Evidence export unavailable; browser feedback is unaffected")
        else:
            log.info("Sanitized coaching evidence saved: %s", path)

    async def drain(self) -> None:
        if self.pending:
            await asyncio.gather(*list(self.pending))


class EvidenceFeedback:
    def __init__(self, generator: FeedbackGenerator, exports: EvidenceExports, provenance: dict):
        self.generator, self.exports, self.provenance = generator, exports, provenance

    async def generate(self, session: CompletedSession) -> Feedback:
        feedback = await self.generator.generate(session)
        report = evidence_report(session, feedback, self.provenance)
        self.exports.schedule(session.session_id, report)
        return feedback


def evidence_factory(base, exports: EvidenceExports, provenance: dict):
    def factory(config: SessionConfig):
        components = base(config)
        if config.mode == "live" and components.feedback is not None:
            components.feedback = EvidenceFeedback(
                components.feedback, exports, {**provenance, "session_config": config.model_dump()},
            )
        return components

    factory.live_integrated = getattr(base, "live_integrated", True)
    return factory


def asset_identity(path: Path) -> dict:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as asset:
            while chunk := asset.read(1024 * 1024):
                digest.update(chunk)
        return {"available": True, "sha256": digest.hexdigest()}
    except OSError:
        return {"available": False, "sha256": None}


def provenance(config: SpeechConfig) -> dict:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False,
    )
    dirty = subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=ROOT, check=False)
    pose = Path(os.environ.get("LECOACH_POSE_MODEL", "models/pose_landmarker_lite.task"))
    return {
        "source_revision": revision.stdout.strip() if revision.returncode == 0 else None,
        "tracked_worktree_modified": dirty.returncode != 0,
        "input_mode": "live",
        "inference_backend": "local CPU",
        "host": {"os": platform.system(), "release": platform.release(),
                 "architecture": platform.machine(), "python": platform.python_version()},
        "speech_config": config.model_dump(exclude={"model_dir"}),
        "rule_config": DEFAULT_RULES.model_dump(),
        "microphone_selection": os.environ.get("LECOACH_SPEECH_DEVICE") or "system default",
        "camera_index": os.environ.get("LECOACH_CAMERA_INDEX", "0"),
        "speech_model": asset_identity(model_path(config) / "model.bin"),
        "pose_model": asset_identity(pose),
        "limits": "Model hashes identify prepared assets, not inference accuracy or latency",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--speech-model-dir", type=Path, default=Path("models"))
    parser.add_argument("--out-dir", type=Path, default=ROOT / "sessions/live-evidence")
    args = parser.parse_args(argv)
    directory = args.out_dir.resolve()
    if not directory.is_relative_to((ROOT / "sessions").resolve()):
        parser.error("--out-dir must be inside the repository's ignored sessions/ directory")
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler())
    log.propagate = False
    config = SpeechConfig(model_dir=str(args.speech_model_dir))
    exports = EvidenceExports(directory)
    factory = evidence_factory(
        prepare_live_factory(config, DEFAULT_RULES), exports, provenance(config),
    )
    app = create_app(factory)
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(app):
        try:
            async with original_lifespan(app):
                yield
        finally:
            await exports.drain()

    app.router.lifespan_context = lifespan
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
