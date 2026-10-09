"""Guided real-camera check for VIS-01 acceptance and VIS-02 measurements.

Runs the production ``LocalVisionAdapter`` with the local OpenCV/MediaPipe backend
outside the web app, prompts the presenter through scripted segments, validates
every emitted event against the v0 contract and reports per-segment results plus
throughput/latency. No frames, JPEGs or keypoints are written anywhere; the
optional ``--out`` summary contains only window metrics and counters.

    python -m lecoach.vision.probe --model models/pose_landmarker_lite.task
    python -m lecoach.vision.probe --segment-s 8 --out sessions/vision-probe.json

A preview window (mirrored camera + detected skeleton + prompt/countdown + latest
window metrics) opens by default; ``--no-show`` disables it. Press q/Esc to abort.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import sys
import time
from pathlib import Path
from statistics import mean

from lecoach.contracts import parse_event
from lecoach.contracts.interfaces import SessionConfig, SessionContext
from lecoach.runtime.clock import MonotonicClock

from .config import VisionConfig
from .features import ARM_JOINTS, FrameFeatures
from .local_backend import DEFAULT_MODEL_PATH, MODEL_ENV, build_local_adapter

SCRIPT = (
    ("toward_still", "Face the camera and stay still."),
    ("toward_active", "Keep facing the camera and gesture with both hands."),
    ("away", "Turn your head (and shoulders) clearly away and hold it."),
    ("toward_still_2", "Face the camera again, still."),
    ("no_person", "Step out of the frame."),
)
# Seconds ignored after each prompt while the presenter changes position.
SETTLE_S = 2.0
# Unjudged lead-in so the presenter can frame themselves in the preview.
READY_S = 5.0
DISPLAY_INTERVAL_S = 1 / 30


def _fmt(value) -> str:
    return "--" if value is None else f"{value:.2f}"


def frame_diagnostics(frames: list[tuple[float, bool, int]]) -> dict:
    """How often a pose and at least two elbow/wrist joints were visible."""
    n = len(frames)
    return {
        "inferred": n,
        "pose_usable_fraction": round(sum(f[1] for f in frames) / n, 3) if n else None,
        "arms_visible_fraction": round(sum(f[2] >= 2 for f in frames) / n, 3) if n else None,
    }


def judge(name: str, windows: list[dict]) -> dict:
    facing = [w["facing_score"] for w in windows if w["facing_score"] is not None]
    activity = [w["activity_score"] for w in windows if w["activity_score"] is not None]
    present = [w["person_present"] for w in windows]
    result = {
        "windows": len(windows),
        "facing_mean": round(mean(facing), 3) if facing else None,
        "activity_mean": round(mean(activity), 3) if activity else None,
        "person_present": {str(v): present.count(v) for v in set(present)},
    }
    if not windows:
        result["pass"] = False
    elif name.startswith("toward"):
        result["pass"] = bool(facing) and result["facing_mean"] >= 0.6
        if name == "toward_active":
            result["pass"] = result["pass"] and bool(activity) and result["activity_mean"] >= 0.4
        elif activity:
            result["pass"] = result["pass"] and result["activity_mean"] <= 0.2
    elif name == "away":
        # Unknown (null) facing while turned away is acceptable, never a high score.
        result["pass"] = not facing or result["facing_mean"] < 0.4
    else:
        result["pass"] = (
            all(w["facing_score"] is None for w in windows)
            and present.count(True) <= len(windows) // 4
        )
    return result


async def run(args) -> dict:
    windows: list[dict] = []
    statuses: list[dict] = []
    marks: list[tuple[str, float, float]] = []
    clock = MonotonicClock()

    def emit(value):
        event = parse_event(value)  # contract check on every emission
        if event.type == "signal.status":
            statuses.append({"t": round(event.timestamp_s, 3), **event.payload.model_dump()})
            print(
                f"[{event.timestamp_s:6.2f}] status {event.payload.availability}: "
                f"{event.payload.reason}",
                flush=True,
            )
        else:
            p = event.payload
            windows.append({"event_id": event.event_id, **p.model_dump()})
            if args.verbose:
                print(
                    f"[{p.window_end_s:6.2f}] person={p.person_present} pose={p.pose_available}"
                    f" facing={p.facing_score} activity={p.activity_score}",
                    flush=True,
                )
        return True

    config = VisionConfig(max_inference_fps=args.max_fps)
    viewer = None
    if args.show:
        try:
            from .viewer import ProbeViewer

            viewer = ProbeViewer(config)
        except ImportError:
            print("(opencv not importable; running without preview window)", flush=True)
    # Per-inferred-frame diagnostics (worker thread appends; no image data):
    # (capture time, pose usable, number of visible elbow/wrist joints).
    frame_log: list[tuple[float, bool, int]] = []

    def on_frame(frame, pose) -> None:
        features = FrameFeatures(pose, config)
        arms = sum(features.visible(joint) is not None for joint in ARM_JOINTS)
        frame_log.append((pose.timestamp_s, features.pose_usable, arms))
        if viewer is not None:
            viewer.on_frame(frame, pose)

    adapter = build_local_adapter(args.model, args.camera, config, on_frame=on_frame)
    context = SessionContext("vision-probe", clock, emit, SessionConfig(mode="live"))
    # Session time 0 = start of capture, as in the app (the controller resets its
    # clock at session start). Otherwise import/model-build time inflates every
    # timestamp and makes capture_started look later than in a real session.
    clock.reset()
    started = time.perf_counter()
    await adapter.start(context)
    startup_s = time.perf_counter() - started
    if adapter.stats.capture_started_s is None:
        await adapter.stop_capture(clock.now())
        await adapter.drain()
        return {"ok": False, "statuses": statuses, "startup_s": round(startup_s, 3)}
    aborted = False

    async def hold(prompt: str, seconds: float) -> bool:
        """Wait ``seconds`` while refreshing the preview; False if the user quit."""
        ends = clock.now() + seconds
        while (left := ends - clock.now()) > 0:
            if viewer is not None:
                last = windows[-1] if windows else {}
                lines = [
                    f"{prompt}  ({left:4.1f} s)",
                    f"last 1 s: person={last.get('person_present')}  "
                    f"facing={_fmt(last.get('facing_score'))}  "
                    f"activity={_fmt(last.get('activity_score'))}",
                ]
                if frame_log:
                    arms = frame_log[-1][2]
                    hint = "" if arms >= 2 else "  <- move back: show elbows/wrists"
                    lines.append(f"arm joints visible: {arms}/4{hint}")
                if not viewer.show(lines):
                    return False
            await asyncio.sleep(DISPLAY_INTERVAL_S if viewer else min(left, 0.5))
        return True

    try:
        print(f"\n>>> Get ready: frame your head and shoulders ({READY_S:.0f} s)", flush=True)
        aborted = not await hold("Get ready: head + shoulders in frame", READY_S)
        for name, prompt in SCRIPT:
            if aborted:
                break
            print(f"\n>>> {prompt} ({args.segment_s:.0f} s)", flush=True)
            begin = clock.now()
            aborted = not await hold(prompt, args.segment_s)
            if not aborted:
                marks.append((name, begin + SETTLE_S, clock.now()))
    finally:
        if viewer is not None:
            viewer.close()
        end = clock.now()
        stop_started = time.perf_counter()
        await adapter.stop_capture(end)
        release_s = time.perf_counter() - stop_started
        await adapter.drain()
    segments = {}
    for name, lo, hi in marks:
        result = judge(
            name, [w for w in windows if lo <= w["window_start_s"] and w["window_end_s"] <= hi]
        )
        result["frames"] = frame_diagnostics([f for f in frame_log if lo <= f[0] <= hi])
        if name == "toward_active" and not result["pass"]:
            if (result["frames"]["arms_visible_fraction"] or 0) < 0.5:
                result["note"] = "elbows/wrists mostly not visible; sit back so arms are in frame"
        segments[name] = result
    return {
        "ok": not aborted and all(s["pass"] for s in segments.values()),
        "aborted": aborted,
        "synthetic": False,
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "model": str(args.model or os.environ.get(MODEL_ENV) or DEFAULT_MODEL_PATH),
        "config": {"window_s": config.window_s, "max_inference_fps": config.max_inference_fps},
        "startup_s": round(startup_s, 3),
        "camera_release_s": round(release_s, 3),
        "camera_released": adapter.released,
        "stats": adapter.stats.as_dict(),
        "statuses": statuses,
        "segments": segments,
        "windows": windows if args.out else len(windows),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", default=None, help="Pose Landmarker .task path")
    parser.add_argument("--camera", type=int, default=None, help="camera index (default 0)")
    parser.add_argument("--segment-s", type=float, default=10.0)
    parser.add_argument("--max-fps", type=float, default=VisionConfig.max_inference_fps)
    parser.add_argument("--out", type=Path, help="write the metrics-only summary JSON here")
    parser.add_argument("-v", "--verbose", action="store_true", help="print every window")
    parser.add_argument(
        "--no-show", dest="show", action="store_false", help="do not open the preview window"
    )
    args = parser.parse_args(argv)
    summary = asyncio.run(run(args))
    text = json.dumps(summary, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")
    print("\n" + json.dumps({k: v for k, v in summary.items() if k != "windows"}, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
