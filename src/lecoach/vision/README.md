# Vision lane (Lane 3): local camera → approximate facing/activity

Owner: @kai-nnnnn. Live status, acceptance and blockers live in Issues
[#15 VIS-01](https://github.com/crasni/LeCoach/issues/15) and
[#16 VIS-02](https://github.com/crasni/LeCoach/issues/16), not here. The event
contract is [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) (`vision.metrics`,
`signal.status`); this file only documents how this implementation fills it.

## Modules

| Module | Role |
| --- | --- |
| `config.py` | Every default and unit (`VisionConfig`). |
| `features.py` | Pure-Python keypoints → per-frame cues → 1 s `vision.metrics` windows. |
| `backend.py` | `FrameSource` / `PoseEstimator` protocols and `VisionUnavailable(reason)`. |
| `adapter.py` | `LocalVisionAdapter`, the `VisionAdapter` seam (lifecycle, worker thread, preview, stats). |
| `local_backend.py` | OpenCV camera + MediaPipe Pose Landmarker (lazy imports); `build_local_adapter()`. |
| `probe.py` | Guided real-camera check that reports acceptance and measurements (no media saved). |
| `viewer.py` | Probe-only preview window: mirrored camera, skeleton and live readout. |

Test evidence: `tests/test_vision.py` and the synthetic labeled fixture in
`checks/vision/` (`python3 checks/vision/make_fixture.py --check`).

## Mapping (approximate; tuned in VIS-02)

* **Windows**: non-overlapping 1 s capture windows on the shared session clock;
  `timestamp_s = window_end_s`. The first window starts when the camera actually
  opened (the startup gap is not reported as unavailable windows) and is extended
  to the next boundary if it would be shorter than 0.5 s. A trailing window
  shorter than 0.5 s at stop is dropped; the last window is clipped to the capture
  end. Event IDs `vision-<n>`, where `n` is the window's slot on the 1 s grid.
* **Frames** are stamped with `context.clock.now()` right after capture. Pose
  inference runs on a fixed-rate schedule capped at `max_inference_fps` (10/s) to
  cap CPU load; every camera frame is still read so timestamps stay fresh.
* **person_present / pose_available**: majority (≥ 50 %) of frames in the window
  must agree, otherwise `null` (cannot decide). Pose requires both shoulders at
  visibility ≥ 0.5.
* **facing_score** (median of frames, ≥ 3 frames): head cue `1 − |nose − ear
  midpoint| / (half ear span)` (eyes if ears are not both visible; nose plus one ear
  = profile = 0). When both hips are visible, a shoulder-span/torso-length body cue
  can only lower it. No nose → `null`, so a back turned to the camera reads as
  *unknown*, never as "away". It is head/body orientation toward the camera, **not
  eye contact, attention or emotion**.
* **activity_score** (≥ 2 frame pairs): mean elbow/wrist speed in body-scale units
  per second, minus a 0.15 noise floor, reaching 1 at 2.0. Body scale is the
  shoulder span, floored by 1.5 × the nose-to-shoulder-midpoint distance, so turning
  sideways (narrower apparent shoulders) does not inflate activity. More movement is
  not better; low movement is never a negative rule on its own.
* **Unavailable input**: no frames in a window → `availability: "unavailable"`.
  No person, undecided detection or unusable pose → available window with `null`
  scores. Device/model problems emit `signal.status` with reasons
  `camera_unavailable`, `pose_model_missing`, `pose_runtime_missing`,
  `camera_start_failed`, `camera_read_failed` (error) or `vision_capture_failed`
  (error); `capture_started` when capture works.

## Lifecycle and privacy

`start` opens the model and camera off the event loop and returns once capture
runs; failures produce a status notice and return normally so speech still works.
One worker thread captures and infers; emissions are posted back to the loop with
`call_soon_threadsafe`. `stop_capture` waits for the worker to release the camera;
`drain` emits the trailing window. Both are idempotent; cancellation during start
still releases anything opened. The preview keeps only the latest JPEG (≤ 512 kB,
≤ 5 fps) and is cleared on stop. Nothing is written to disk.

## Running the real backend (owner's machine)

Runtime packages come from the optional `vision` dependency group proposed by
integration in PR #23 (`docs/LOCAL_RUNTIME.md`): `mediapipe` plus a **single**
OpenCV distribution, `opencv-contrib-python`, which MediaPipe already depends on.
Do not add `opencv-python` (or a headless variant) alongside it; both provide `cv2`.

```sh
mkdir -p models && curl -L -o models/pose_landmarker_lite.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
# Once the vision group is on main:
uv sync --frozen --group vision
uv run python -m lecoach.vision.probe -v --repeat 3 --out sessions/vision-probe.json
# Before that, the same versions for one run (MediaPipe pulls in the contrib OpenCV):
uv run --with "mediapipe==0.10.35" --with "opencv-contrib-python==4.14.0.94" \
  python -m lecoach.vision.probe -v --repeat 3 --out sessions/vision-probe.json
```

`--repeat N` adds N back-to-back 5 s sessions after the guided run, each with a
fresh adapter, and checks that the camera reopens, produces windows and is
released every time.

A preview window opens with the mirrored camera, the detected skeleton (green
lines; orange dot = nose), the current prompt with a countdown, and the latest 1 s
window's `person`/`facing`/`activity`. A 5 s unjudged "get ready" phase comes
first so you can frame your head and shoulders. Press `q`/Esc to abort, or pass
`--no-show` to run without the window. The window is display only and nothing is
saved.

`models/` and `sessions/` are git-ignored. On macOS, grant the terminal camera
access (System Settings → Privacy & Security → Camera) — OpenCV cannot tell a denied
permission from a missing camera, so both report `camera_unavailable`. Override
with `LECOACH_POSE_MODEL` / `LECOACH_CAMERA_INDEX`.

## Integration handoff (Lane 1)

Composition is integration-owned; this lane does not edit `pyproject.toml`,
`uv.lock`, `api/app.py` or `cli.py`.

1. **Dependencies:** the optional `vision` group from PR #23: `mediapipe`
   (Pose Landmarker Tasks API) and `opencv-contrib-python` (capture, JPEG preview,
   probe window; needs the non-headless build for the probe window). Without them
   the adapter still imports and reports `signal.status unavailable/pose_runtime_missing`.
2. **Model asset:** `pose_landmarker_lite.task` (download above) in the ignored
   `models/` directory, or point `LECOACH_POSE_MODEL` at it. A missing file →
   `pose_model_missing`, while speech keeps working.
3. **Compose for live mode** in the session factory passed to `create_app`:

   ```python
   from lecoach.vision.local_backend import build_local_adapter

   def factory(config):
       if config.mode == "live":
           return Components(vision=build_local_adapter(), engagement=..., ...)
   ```

   One adapter instance per session (it is single-use). Building it starts a
   once-per-process background import of OpenCV/MediaPipe (`prewarm()`), and since
   the session factory runs at prepare time, that ~0.6 s+ import is usually done
   before start. Pass `warm=False` to opt out. `GET /api/sessions/{id}/preview`
   then streams `preview_jpeg()`; the browser must not open a second camera stream.
4. **Configuration:** `VisionConfig` (`config.py`) holds every default. The only
   knob integration is likely to need is `max_inference_fps` (CPU cap, default 10).
   On the session side, give live mode a `startup_timeout_s` of ~10 s (see evidence
   below).
   Camera index: `LECOACH_CAMERA_INDEX` (default 0). OpenCV selects cameras by
   index only; on macOS an iPhone (Continuity Camera) can take index 0, so check
   with `python -m lecoach.vision.probe --list-cameras` (or turn Continuity Camera
   off on the phone) and pin the intended webcam's index on the demo host.
5. **Framing:** the presenter's elbows/wrists must be in frame for `activity_score`;
   with a laptop head-and-shoulders crop it is `null` (facing still works).
6. **Status reasons the UI should show:** `capture_started`, `camera_unavailable`
   (missing, busy or permission denied), `pose_model_missing`, `pose_runtime_missing`,
   `camera_start_failed`, `camera_read_failed`, `vision_capture_failed`.

**Measured evidence (not target hardware):** actual camera, MacBook Air (arm64,
macOS 26.6.2), Python 3.12.14, Pose Landmarker lite on CPU, 23 fps webcam, 2026-10-09
(VIS-02 #16, runs 5–6): inference 19.5 ms/frame mean (≤ 31 ms) at 9.99/s; 1 s
windows emitted 67–75 ms after their end on average (max 104–109 ms); camera + model
close 0.19–0.40 s. Startup (model + camera open) was 1.8–2.1 s in five runs but
**5.9 s once**, which is above the default `SessionConfig.startup_timeout_s` of 5 s.
Live mode should allow ~10 s, otherwise such a session runs without vision
(`adapter_start_failed`; the camera is still released). No UGen300 or intended-host
numbers yet; UI responsiveness with vision composed into the app is not measured yet.

## Known limitations

* Facing is a 2-D geometric heuristic; strong head tilt, glasses, or a camera far
  off-axis bias it. Thresholds are demo heuristics, not validated measures.
* Single person only; the most confident pose is used.
* Not measured on the UGen300 or any target hardware; no accelerator path yet.
* The web app does not compose this adapter yet (integration-owned composition).
