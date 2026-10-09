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

Runtime packages are **not** in the shared manifest yet — that is an integration
decision requested in #15. Until then, install them locally without editing
`pyproject.toml`/`uv.lock`:

```sh
mkdir -p models && curl -L -o models/pose_landmarker_lite.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
# --with adds the packages for this run only (a later `uv sync` would remove a
# `uv pip install`); without uv: a venv with pydantic, opencv-python, mediapipe
# and `PYTHONPATH=src python -m lecoach.vision.probe ...`.
uv run --with opencv-python --with mediapipe \
  python -m lecoach.vision.probe -v --out sessions/vision-probe.json
```

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

1. **Dependencies (proposed, not added):** `opencv-python` (capture, JPEG preview)
   and `mediapipe` (Pose Landmarker), e.g. as an optional `vision` group. Both were
   exercised with Python 3.12.14 on macOS arm64. Without them the adapter still
   imports and reports `signal.status unavailable/pose_runtime_missing`.
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

   One adapter instance per session (it is single-use). `GET /api/sessions/{id}/preview`
   then streams `preview_jpeg()`; the browser must not open a second camera stream.
4. **Configuration:** `VisionConfig` (`config.py`) holds every default. The only
   knob integration is likely to need is `max_inference_fps` (CPU cap, default 10).
   Camera index: `LECOACH_CAMERA_INDEX` (default 0).
5. **Framing:** the presenter's elbows/wrists must be in frame for `activity_score`;
   with a laptop head-and-shoulders crop it is `null` (facing still works).
6. **Status reasons the UI should show:** `capture_started`, `camera_unavailable`
   (missing, busy or permission denied), `pose_model_missing`, `pose_runtime_missing`,
   `camera_start_failed`, `camera_read_failed`, `vision_capture_failed`.

**Measured evidence (not target hardware):** actual camera, MacBook Air (arm64,
macOS 26.6.2), Python 3.12.14, Pose Landmarker lite on CPU, 23 fps webcam, 2026-10-09
(VIS-02 #16, run 4): inference 19.5 ms/frame mean (28 ms max) at 9.99/s, 1 s windows
emitted 79 ms after their end on average, startup 1.8 s, camera release 0.15–0.42 s.
No UGen300 or intended-host numbers yet; UI responsiveness with vision composed
into the app is not measured yet.

## Known limitations

* Facing is a 2-D geometric heuristic; strong head tilt, glasses, or a camera far
  off-axis bias it. Thresholds are demo heuristics, not validated measures.
* Single person only; the most confident pose is used.
* Not measured on the UGen300 or any target hardware; no accelerator path yet.
* The web app does not compose this adapter yet (integration-owned composition).
