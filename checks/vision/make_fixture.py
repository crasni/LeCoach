"""Generate the labeled, fully synthetic VIS-01 keypoint fixture.

No camera, image or person was used. A 640x480 upper-body skeleton is posed by
hand-written segments (head/body yaw, arm oscillation, detector outcomes) with
seeded jitter, then sampled at 10 frames/s. Labels are the intended observation
per 1 s window; ``test_vision.py`` checks the vision lane reproduces them.

    python3 checks/vision/make_fixture.py          # rewrite the fixture
    python3 checks/vision/make_fixture.py --check  # fail if it is out of date
"""

import json
import math
import random
import sys
from pathlib import Path

OUT = Path(__file__).with_name("fixtures") / "labeled_session.json"
FPS = 10
HEAD_R = 40.0  # head radius (px) in a top-down view
SHOULDER_HALF = 80.0
HIP_HALF = 55.0

# (start_s, end_s, scene, label). Scene keys: person (True/False/None), head_yaw,
# body_yaw (degrees), gesture (wrist amplitude px), vis (keypoint visibility).
SEGMENTS = [
    (
        0,
        8,
        {"head_yaw": 5, "body_yaw": 0, "gesture": 0},
        {"person_present": True, "facing": "toward", "activity": "low"},
    ),
    (
        8,
        16,
        {"head_yaw": -8, "body_yaw": 0, "gesture": 60},
        {"person_present": True, "facing": "toward", "activity": "active"},
    ),
    (
        16,
        26,
        {"head_yaw": 70, "body_yaw": 35, "gesture": 0},
        {"person_present": True, "facing": "away", "activity": "low"},
    ),
    (26, 30, {"person": False}, {"person_present": False, "facing": None, "activity": None}),
    (30, 33, {"person": None}, {"person_present": None, "facing": None, "activity": None}),
    (
        33,
        36,
        {"head_yaw": 0, "body_yaw": 0, "gesture": 0, "vis": 0.2},
        {"person_present": True, "pose_available": False, "facing": None, "activity": None},
    ),
    (
        36,
        40,
        {"head_yaw": 0, "body_yaw": 0, "gesture": 0},
        {"person_present": True, "facing": "toward", "activity": "low"},
    ),
]


def pose(t: float, scene: dict, rng: random.Random) -> dict:
    head, body = math.radians(scene["head_yaw"]), math.radians(scene["body_yaw"])
    vis = scene.get("vis", 0.95)
    cx = 320.0

    def jitter():
        return rng.gauss(0, 1.0)

    def point(x, y, visible=True):
        return [round(x + jitter(), 1), round(y + jitter(), 1), vis if visible else 0.1]

    # Head points on a circle; an ear rotated behind the head is hidden.
    nose = point(cx + HEAD_R * math.sin(head), 150)
    left_ear_depth, right_ear_depth = math.sin(head), -math.sin(head)
    points = {
        "nose": nose,
        "left_eye": point(cx + 0.5 * HEAD_R * math.sin(head - 0.6), 140),
        "right_eye": point(cx + 0.5 * HEAD_R * math.sin(head + 0.6), 140),
        "left_ear": point(cx - HEAD_R * math.cos(head), 155, left_ear_depth > -0.5),
        "right_ear": point(cx + HEAD_R * math.cos(head), 155, right_ear_depth > -0.5),
    }
    shoulder = SHOULDER_HALF * math.cos(body)
    hip = HIP_HALF * math.cos(body)
    phase = 2 * math.pi * 1.5 * t
    wrist = scene["gesture"] * math.sin(phase)
    elbow = 0.4 * scene["gesture"] * math.sin(phase)
    points.update(
        {
            "left_shoulder": point(cx - shoulder, 250),
            "right_shoulder": point(cx + shoulder, 250),
            "left_elbow": point(cx - shoulder - 15, 330 - elbow),
            "right_elbow": point(cx + shoulder + 15, 330 + elbow),
            "left_wrist": point(cx - shoulder - 10, 400 - wrist),
            "right_wrist": point(cx + shoulder + 10, 400 + wrist),
            "left_hip": point(cx - hip, 430),
            "right_hip": point(cx + hip, 430),
        }
    )
    return points


def build() -> dict:
    rng = random.Random(20261009)
    frames = []
    for start, end, scene, _ in SEGMENTS:
        for i in range(start * FPS, end * FPS):
            t = round(i / FPS + 0.05, 3)  # mid-frame stamps, never on a window edge
            person = scene.get("person", True)
            frames.append({"t": t, "person": person, "kp": pose(t, scene, rng) if person else {}})
    return {
        "description": "Synthetic labeled keypoints for VIS-01; no camera or person was used.",
        "synthetic": True,
        "units": "pixels in a 640x480 frame; visibility in [0, 1]",
        "fps": FPS,
        "duration_s": SEGMENTS[-1][1],
        "label_thresholds": {
            "toward_facing_at_least": 0.6,
            "away_facing_below": 0.4,
            "low_activity_at_most": 0.2,
            "active_activity_at_least": 0.4,
        },
        "segments": [{"start_s": s, "end_s": e, "label": label} for s, e, _, label in SEGMENTS],
        "frames": frames,
    }


def render() -> str:
    data = build()
    frames = data.pop("frames")
    head = json.dumps(data, indent=2)[:-2]
    lines = ",\n".join("    " + json.dumps(f, separators=(",", ":")) for f in frames)
    return f'{head},\n  "frames": [\n{lines}\n  ]\n}}\n'


if __name__ == "__main__":
    text = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text() != text:
            sys.exit(f"{OUT} is out of date; run make_fixture.py")
        print("fixture up to date")
    else:
        OUT.write_text(text)
        print(f"wrote {OUT} ({len(text)} bytes)")
