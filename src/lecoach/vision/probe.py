"""Guided real-camera check for VIS-01 acceptance and VIS-02 measurements.

Runs the production ``LocalVisionAdapter`` with the local OpenCV/MediaPipe backend
outside the web app, prompts the presenter through scripted segments, validates
every emitted event against the v0 contract and reports per-segment results plus
throughput/latency. No frames, JPEGs or keypoints are written anywhere; the
optional ``--out`` summary contains only window metrics and counters.

    python -m lecoach.vision.probe --model models/pose_landmarker_lite.task
    python -m lecoach.vision.probe --segment-s 8 --out sessions/vision-probe.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import platform
import sys
import time
from pathlib import Path
from statistics import mean

from lecoach.contracts import parse_event
from lecoach.contracts.interfaces import SessionConfig, SessionContext
from lecoach.runtime.clock import MonotonicClock

from .config import VisionConfig
from .local_backend import build_local_adapter

SCRIPT = (
    ("toward_still", "Face the camera and stay still."),
    ("toward_active", "Keep facing the camera and gesture with both hands."),
    ("away", "Turn your head (and shoulders) clearly away and hold it."),
    ("toward_still_2", "Face the camera again, still."),
    ("no_person", "Step out of the frame."),
)
# Seconds ignored after each prompt while the presenter changes position.
SETTLE_S = 2.0


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
    adapter = build_local_adapter(args.model, args.camera, config)
    context = SessionContext("vision-probe", clock, emit, SessionConfig(mode="live"))
    started = time.perf_counter()
    await adapter.start(context)
    startup_s = time.perf_counter() - started
    if adapter.stats.capture_started_s is None:
        await adapter.stop_capture(clock.now())
        await adapter.drain()
        return {"ok": False, "statuses": statuses, "startup_s": round(startup_s, 3)}
    try:
        for name, prompt in SCRIPT:
            print(f"\n>>> {prompt} ({args.segment_s:.0f} s)", flush=True)
            begin = clock.now()
            await asyncio.sleep(args.segment_s)
            marks.append((name, begin + SETTLE_S, clock.now()))
    finally:
        end = clock.now()
        stop_started = time.perf_counter()
        await adapter.stop_capture(end)
        release_s = time.perf_counter() - stop_started
        await adapter.drain()
    segments = {
        name: judge(
            name, [w for w in windows if lo <= w["window_start_s"] and w["window_end_s"] <= hi]
        )
        for name, lo, hi in marks
    }
    return {
        "ok": all(s["pass"] for s in segments.values()),
        "synthetic": False,
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "model": str(args.model),
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
