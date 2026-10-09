# Local speech and vision runtime setup

The integration-owned optional dependency groups provide the CPU runtimes
requested in [#6](https://github.com/crasni/LeCoach/issues/6) and
[#15](https://github.com/crasni/LeCoach/issues/15). They are excluded from the
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

The maintainer's 2026-10-09 Mandarin-first decision supersedes the English
baseline recorded in `929f727`. Product rehearsal language is Mandarin; product
presentation is native Taiwan Traditional Chinese (`zh-TW`). Keep the existing
speech-owned configuration and optional packages, but do not interpret a language
flag change as completed Mandarin support.

Speech/integration/realtime/coaching must agree transcription, pace units/counting,
contextual fillers, coverage/revisions and coaching in [#6](https://github.com/crasni/LeCoach/issues/6)
and the [proposed delta](../openspec/changes/mandarin-first-stage1/proposal.md).
Use a multilingual local model; `base.en` is an English-only regression baseline,
not the Mandarin demo model. Multilingual `base` on CPU/int8 is a candidate pending
actual host recognition/performance checks. Traditional script handling also needs
owner review. Unsupported pace/fillers remain null; Chinese character rates cannot
populate v0 English WPM. Existing timing knobs are preserved for testing, not
validated Mandarin settings. No engine thresholds or 2 s drain bound change here.

The owner [speech design](https://github.com/crasni/LeCoach/blob/agent/audio-streaming/openspec/changes/aud-01-live-speech-adapter/design.md)
requires a follow-up reconciliation on that owner's branch. Do not create another
config or producer. The existing active-pause/`pace_steady` finding remains #18's
handoff; it cannot establish a supported Mandarin pace observation.

The `speech` group provides `faster-whisper`, `sounddevice` and `numpy`. Linux
requires the PortAudio system library (on Debian/Ubuntu, `libportaudio2`); see
[sounddevice installation](https://python-sounddevice.readthedocs.io/en/latest/installation.html).
For example, on a Debian/Ubuntu development host with administrator access:

```sh
sudo apt-get install libportaudio2
```

On macOS/Windows, the sounddevice wheels normally bundle PortAudio. Device
permissions and availability must still be checked on the actual rehearsal host.
The production source/VAD/transcriber remains Lane 2's work in
[#13](https://github.com/crasni/LeCoach/issues/13). Model download/loading must
finish before session start; no setup command here starts capture or downloads weights.

## Vision runtime handoff

The `vision` group provides MediaPipe's 0.10 Tasks API family and
`opencv-contrib-python`, which includes the `cv2` capture/JPEG/preview APIs.
MediaPipe already depends on this OpenCV distribution. Install a single OpenCV
distribution: the four wheel variants share `cv2` and cannot coexist reliably
([OpenCV installation guidance](https://pypi.org/project/opencv-contrib-python/)).
Do not add `opencv-python` or either headless variant alongside it.

Use the merged vision producer's `build_local_adapter()` public factory, with one
adapter per session, after the composition handoff is agreed. Its README on main
documents the Pose Landmarker lite asset, ignored model path, camera selection,
probe and approximate facing/activity limitations:
[vision handoff](https://github.com/crasni/LeCoach/blob/main/src/lecoach/vision/README.md#integration-handoff-lane-1).
Do not open a second camera in the browser.

Actual-camera CPU measurements in #16 include one 5.94 s startup, above the
shared default 5 s bound. A proposed 10 s live-mode bound requires composition
review; this dependency increment does not change that default. In-app UI
responsiveness can be measured only once vision is composed into the app; that
measurement remains part of #16 and joint #11/#19 acceptance. Final acceptance
must not prevent independent composition preparation.
