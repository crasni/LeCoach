# VIS-01 labeled vision fixture (synthetic)

`fixtures/labeled_session.json` is a **synthetic** 40 s keypoint session. No camera,
image or person was used. `make_fixture.py` poses a 640×480 upper-body skeleton
through hand-written segments with seeded jitter at 10 frames/s, and labels each
segment with the observation it should produce:

| Seconds | Scene | Expected window |
| --- | --- | --- |
| 0–8 | facing camera, still | facing ≥ 0.6, activity ≤ 0.2 |
| 8–16 | facing camera, gesturing | facing ≥ 0.6, activity ≥ 0.4 |
| 16–26 | head turned 70°, body 35°, still | facing < 0.4 (sustained looking away) |
| 26–30 | no person detected | `person_present: false`, null scores |
| 30–33 | detector undecided | `person_present: null`, null scores |
| 33–36 | person, keypoints low confidence | `pose_available: false`, null scores |
| 36–40 | facing camera, still | facing ≥ 0.6, activity ≤ 0.2 |

The thresholds match the engine's facing defaults (`engagement/config.py`).
`tests/test_vision.py` checks every window against its label and replays the
fixture through the real adapter, controller and engine.

```sh
python3 checks/vision/make_fixture.py --check   # fixture matches its generator
```

This fixture proves the code paths and contract handling only. Real-camera
behavior is accepted separately with `python -m lecoach.vision.probe` (see
`src/lecoach/vision/README.md` and Issues #15/#16).
