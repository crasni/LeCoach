# Local speech and vision runtime setup

The integration-owned optional dependency groups provide the CPU runtimes
requested in [#6](https://github.com/crasni/LeSpeech/issues/6) and
[#15](https://github.com/crasni/LeSpeech/issues/15). They are excluded from the
default core/dev installation. The exact versions and hashes are in `uv.lock`.

```sh
uv sync --frozen --group speech
uv sync --frozen --group vision
uv sync --frozen --group speech --group vision
```

Include both groups on subsequent sync/run commands when both are needed;
`uv sync --frozen` restores the core/dev environment. Packages are downloaded
during setup; weights must be prepared separately in ignored `models/`, outside
sessions. Runtime setup does not establish microphone/camera, model quality,
live app composition or UGen300 compatibility.

## Speech configuration handoff

Integration accepts Lane 2's proposed English analysis baseline for the Stage I
demo. Keep the existing `SpeechConfig` in `lespeech.speech.config`; the composition
root constructs/passes that configuration, with no second definition in shared
contracts. The existing adapter constructor accepts it. This follows the
[speech design](../openspec/changes/archive/2026-10-11-aud-01-live-speech-adapter/design.md)
and preserves the v0 event interface.

| Setting | Baseline |
| --- | --- |
| Analysis language | `en` |
| Trailing metrics window / update hop | 10 s / 1 s |
| Minimum observation / pause minimum | 5 s / 1 s |
| Finalized coverage wait / maximum utterance | 3 s / 8 s |
| Partial transcript interval / capture rate | 1 s / 16,000 Hz |
| Initial model / device / compute type | `base.en` / `cpu` / `int8` |

These are configurable demo heuristics, awaiting actual speech measurements.
Unsupported analysis languages retain null WPM/filler observations. Engagement
pace bands and pause interpretation stay with Lane 4. The proposed 1 s hop is
within the existing engine's 5 s maximum gap; the reported scripted composition
is evidence of interface compatibility, not inference latency. In particular,
the reviewed engine in PR #29 holds pace/filler rules during an active pause and
does not treat silence-filled windows as positive pace evidence.
The current 2 s drain bound remains unchanged pending real finalization evidence.

The `speech` group provides `faster-whisper`, `sounddevice` and `numpy`. Linux
requires the PortAudio system library (on Debian/Ubuntu, `libportaudio2`); see
[sounddevice installation](https://python-sounddevice.readthedocs.io/en/latest/installation.html).
For example, on a Debian/Ubuntu development host with administrator access:

```sh
sudo apt-get install libportaudio2
```

On macOS/Windows, the sounddevice wheels normally bundle PortAudio. Device
permissions and availability must still be checked on the actual rehearsal host.
The production source/VAD/transcriber is delivered by Lane 2 in PR #28; actual
microphone acceptance remains [#13](https://github.com/crasni/LeSpeech/issues/13).
Follow [demo host preparation](DEMO_HOST.md) for explicit model preparation and
`lespeech serve --live`. Model loading finishes before serving; neither package
setup nor serving alone acquires devices. Downloads require the explicit model
preparation command, never a session start.

## Vision runtime handoff

The `vision` group provides MediaPipe's 0.10 Tasks API family and
`opencv-contrib-python`, which includes the `cv2` capture/JPEG/preview APIs.
MediaPipe already depends on this OpenCV distribution. Install a single OpenCV
distribution: the four wheel variants share `cv2` and cannot coexist reliably
([OpenCV installation guidance](https://pypi.org/project/opencv-contrib-python/)).
Do not add `opencv-python` or either headless variant alongside it.

Use the merged vision producer's `build_local_adapter()` public factory, with one
adapter per session, through the delivered opt-in live composition. Its README on main
documents the Pose Landmarker lite asset, ignored model path, camera selection,
probe and approximate facing/activity limitations:
[vision handoff](https://github.com/crasni/LeSpeech/blob/main/src/lespeech/vision/README.md#integration-handoff-lane-1).
Do not open a second camera in the browser.

Stage I vision is [accepted by the owner](https://github.com/crasni/LeSpeech/issues/16#issuecomment-6097454631).
On the Ubuntu demo host, three isolated runs started in 0.20–0.36 s, inferred
about 9.95 frames/s and released the camera in 54–77 ms. The existing 5 s startup
bound is retained. The earlier 5.94 s outlier was on the owner's Mac, not the
Ubuntu demo host. Activity/gesture distinction was measured on Mac only; the
owner accepted that limitation because no engine rule or coaching template uses
activity. Future activity-based behavior needs a host recheck. Concurrent
speech/browser latency and UGen300 performance remain separate measurements.
