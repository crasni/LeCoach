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
  `timestamp_s = window_end_s`. A trailing window shorter than 0.5 s at stop is
  dropped; the last window is clipped to the capture end. Event IDs `vision-<n>`.
* **Frames** are stamped with `context.clock.now()` right after capture. Pose
  inference is throttled to `max_inference_fps` (10/s) to cap CPU load.
* **person_present / pose_available**: majority (≥ 50 %) of frames in the window
  must agree, otherwise `null` (cannot decide). Pose requires both shoulders at
  visibility ≥ 0.5.
* **facing_score** (median of frames, ≥ 3 frames): head cue `1 − |nose − ear
  midpoint| / (half ear span)` (eyes if ears are not both visible; nose plus one ear
  = profile = 0). When both hips are visible, a shoulder-span/torso-length body cue
  can only lower it. No nose → `null`, so a back turned to the camera reads as
  *unknown*, never as "away". It is head/body orientation toward the camera, **not
  eye contact, attention or emotion**.
* **activity_score** (≥ 2 frame pairs): mean elbow/wrist speed in shoulder-widths
  per second, minus a 0.15 noise floor, reaching 1 at 2.0. More movement is not
  better; low movement is never a negative rule on its own.
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
uv pip install opencv-python mediapipe      # inside the project venv
mkdir -p models && curl -L -o models/pose_landmarker_lite.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
uv run python -m lecoach.vision.probe -v --out sessions/vision-probe.json
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

## Known limitations

* Facing is a 2-D geometric heuristic; strong head tilt, glasses, or a camera far
  off-axis bias it. Thresholds are demo heuristics, not validated measures.
* Single person only; the most confident pose is used.
* Not measured on the UGen300 or any target hardware; no accelerator path yet.
* The web app does not compose this adapter yet (integration-owned composition).
