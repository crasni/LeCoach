"""Guided live speech check for AUD-01 acceptance and AUD-02 measurements.

Runs the production speech adapter through the real session controller, outside
the web app: the shared Whisper model, the microphone (or a WAV replay), and
Silero segmentation. It prompts the speaker through scripted parts, prints
transcripts and metrics as they arrive, and reports startup, latency, and drain
timing. No audio is written. `--out` saves the event stream, which includes
transcripts, as a JSON array for `checks/speech/check_speech.py --stream`, plus
a `.summary.json` beside it; keep both in the ignored `sessions/` directory.

    python -m lecoach.speech.probe --list-devices
    python -m lecoach.speech.probe --out sessions/speech-probe.json
    python -m lecoach.speech.probe --wav take.wav --out sessions/speech-replay.json
    python3 checks/speech/check_speech.py --stream sessions/speech-probe.json
"""

import argparse
import asyncio
import json
import os
import platform
import statistics
import sys
import time
import wave
from pathlib import Path

from lecoach.contracts.interfaces import Components, SessionConfig
from lecoach.runtime.clock import MonotonicClock
from lecoach.runtime.session import SessionController

from .config import SpeechConfig
from .local import build_local_adapter
from .whisper import ModelUnavailable, warm_up

PASSAGE = ("Thank you all for coming today. I want to show you how our team built a faster "
           "way to practice presentations. First, we listen to your voice and count your "
           "words. Then a small audience reacts to your pace, your pauses, and your "
           "posture, so you can see the effect while you speak.")

PARTS = (
    ("normal", 25, "Read this aloud at your normal pace:\n\n  " + PASSAGE),
    ("fast", 15, "Read the same passage again, as fast as you clearly can."),
    ("fillers", 15, "Talk about your weekend and use fillers on purpose: um, uh, like, you know."),
    ("silence", 10, "Stay completely silent."),
    ("stop_while_speaking", 6, "Start talking now and keep talking until the stop."),
)


def summarize(values: list[float]) -> dict | None:
    if not values:
        return None
    ordered = sorted(values)
    p95 = ordered[min(len(ordered) - 1, round(0.95 * (len(ordered) - 1)))]
    return {"count": len(values), "median_s": round(statistics.median(values), 3),
            "p95_s": round(p95, 3), "max_s": round(ordered[-1], 3)}


def describe(event) -> str | None:
    payload = event.payload
    if event.type == "speech.transcript" and payload.is_final:
        return f"final {payload.utterance_id} [{payload.start_s:.1f}-{payload.end_s:.1f} s]: " \
               f"{payload.text or '(empty)'}"
    if event.type == "speech.metrics":
        pause = payload.pause
        pause_text = f", pause {pause.state} {pause.duration_s or 0:.1f} s" \
            if pause.state in ("active", "completed") else ""
        return f"window ..{payload.window_end_s:.1f} s: {payload.availability}, " \
               f"WPM {payload.wpm}, fillers {payload.filler_count}{pause_text}"
    if event.type == "signal.status":
        return f"status: {payload.availability} / {payload.reason}"
    return None


async def run(args: argparse.Namespace) -> int:
    config = SpeechConfig(**{key: value for key, value in
                             {"model": args.model, "model_dir": args.model_dir}.items() if value})
    print(f"Loading {config.model} on {config.device}/{config.compute_type} ...", flush=True)
    started = time.perf_counter()
    try:
        transcriber = warm_up(config)
    except ModelUnavailable as error:
        print(error, file=sys.stderr)
        return 2
    load_s = time.perf_counter() - started
    adapter = build_local_adapter(config, transcriber=transcriber, device=args.device,
                                  wav=args.wav)
    controller = SessionController(
        SessionConfig(mode="live", drain_timeout_s=args.drain_timeout),
        Components(speech=adapter), session_id=f"speech-probe-{int(time.time())}",
        clock=MonotonicClock())
    arrivals: list[tuple[float, object]] = []

    def on_event(event) -> None:
        arrivals.append((controller.clock.now(), event))
        line = describe(event) if event.source == "speech" else None
        if line:
            print(f"  [{controller.clock.now():6.1f} s] {line}", flush=True)

    controller.bus.subscribe(on_event)
    started = time.perf_counter()
    await controller.start()
    start_s = time.perf_counter() - started
    print(f"Model ready in {load_s:.1f} s; session started in {start_s:.2f} s.", flush=True)
    boundaries = []
    if args.wav:
        with wave.open(str(args.wav), "rb") as file:
            duration = file.getnframes() / file.getframerate()
        print(f"Replaying {args.wav} ({duration:.1f} s) ...", flush=True)
        await asyncio.sleep(duration + 1.0)
        boundaries.append(("wav", 0.0, controller.clock.now()))
    else:
        for name, seconds, prompt in PARTS:
            print(f"\n=== {name} ({seconds} s) ===\n{prompt}\n", flush=True)
            begin = controller.clock.now()
            await asyncio.sleep(seconds)
            boundaries.append((name, begin, controller.clock.now()))
    started = time.perf_counter()
    await controller.stop()
    stop_s = time.perf_counter() - started
    summary = report(config, args, adapter, controller, arrivals, boundaries, load_s, start_s,
                     stop_s)
    print("\n" + json.dumps(summary, indent=2))
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        stream = [event.model_dump(mode="json") for _, event in arrivals]
        out.write_text(json.dumps(stream, indent=1) + "\n", encoding="utf-8")
        out.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n",
                                                   encoding="utf-8")
        print(f"\nSaved {out} and {out.with_suffix('.summary.json')}; check with:\n"
              f"  python3 checks/speech/check_speech.py --stream {out}")
    return 0


def report(config, args, adapter, controller, arrivals, boundaries, load_s, start_s,
           stop_s) -> dict:
    speech = [(at, event) for at, event in arrivals if event.source == "speech"]
    finals = [(at, event) for at, event in speech
              if event.type == "speech.transcript" and event.payload.is_final]
    windows = [(at, event) for at, event in speech if event.type == "speech.metrics"]
    parts = {}
    for name, begin, end in boundaries:
        inside = [event.payload for _, event in windows
                  if begin < event.payload.window_end_s <= end]
        parts[name] = {
            "wpm": [payload.wpm for payload in inside],
            "fillers": [payload.filler_count for payload in inside],
            "pauses": sorted({payload.pause.state for payload in inside}),
            "finals": [event.payload.text for _, event in finals
                       if begin < event.payload.end_s <= end],
        }
    return {
        "host": {"platform": platform.platform(), "python": platform.python_version(),
                 "cpus": os.cpu_count()},
        "input": {"source": adapter.source.__class__.__name__,
                  "device": getattr(adapter.source, "device_name", None),
                  "device_rate": getattr(adapter.source, "device_rate", None),
                  "overflows": getattr(adapter.source, "overflows", None)},
        "config": config.model_dump(),
        "model_load_and_warm_up_s": round(load_s, 2),
        "session_start_s": round(start_s, 3),
        "stop_and_drain_s": round(stop_s, 3),
        "drain_timeout_s": args.drain_timeout,
        "incomplete_sources": controller.incomplete_sources,
        "statuses": [(event.payload.availability, event.payload.reason)
                     for _, event in speech if event.type == "signal.status"],
        "final_delay_after_speech_end": summarize(
            [at - event.payload.end_s for at, event in finals]),
        "window_delay_after_window_end": summarize(
            [at - event.payload.window_end_s for at, event in windows]),
        "segmentation_lag_s": round(controller.capture_end_s - adapter.analyzed_s, 3)
        if controller.capture_end_s is not None else None,
        "adapter_errors": adapter.errors,
        "parts": parts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m lecoach.speech.probe",
                                     description="Guided live speech check.")
    parser.add_argument("--list-devices", action="store_true", help="list audio devices")
    parser.add_argument("--device", help="input device index or name (default: system)")
    parser.add_argument("--wav", help="replay a 16-bit PCM WAV instead of the microphone")
    parser.add_argument("--out", help="save the event stream (JSON array) to this path")
    parser.add_argument("--model", help="model name (default: SpeechConfig.model)")
    parser.add_argument("--model-dir", help="model directory (default: models)")
    parser.add_argument("--drain-timeout", type=float, default=2.0,
                        help="stop/drain bound in seconds (session default: 2)")
    args = parser.parse_args(argv)
    if args.device is not None and args.device.isdigit():
        args.device = int(args.device)
    if args.list_devices:
        try:
            import sounddevice
        except (ImportError, OSError) as error:
            print(f"audio backend unavailable: {error}", file=sys.stderr)
            return 2
        print(sounddevice.query_devices())
        return 0
    return asyncio.run(run(args))


if __name__ == "__main__":
    sys.exit(main())
