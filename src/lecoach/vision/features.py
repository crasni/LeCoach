"""Pose keypoints → approximate facing/activity → canonical ``vision.metrics`` windows.

Pure Python, no model/runtime dependency, so it is deterministic and testable
without a camera. Keypoint internals stay inside the vision lane (ARCHITECTURE:
"Pose/keypoint internals can stay in the adapter").

Coordinates must be isotropic (e.g. pixels, or normalised x multiplied by the
frame aspect ratio) so distances are comparable across axes; only ratios are used.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from statistics import median

from .config import VisionConfig

# The subset of body landmarks the lane uses. Backends map their model to these.
KEYPOINTS = (
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
)
ARM_JOINTS = ("left_elbow", "right_elbow", "left_wrist", "right_wrist")
# Frame pairs further apart than this (capture stall) do not measure movement.
MAX_PAIR_GAP_S = 0.5


@dataclass(frozen=True)
class Keypoint:
    x: float
    y: float
    visibility: float  # model confidence that the point is visible, in [0, 1]


@dataclass(frozen=True)
class PoseFrame:
    """One captured frame, stamped with the shared session clock at capture.

    ``person_present`` is None when the detector could not decide (low confidence).
    ``keypoints`` is empty when no pose was produced.
    """

    timestamp_s: float
    person_present: bool | None
    keypoints: Mapping[str, Keypoint] = field(default_factory=dict)


def _clamp(value: float) -> float:
    return min(1.0, max(0.0, value))


def _dist(a: Keypoint, b: Keypoint) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


class FrameFeatures:
    """Per-frame cues for one ``PoseFrame`` under a ``VisionConfig``."""

    def __init__(self, frame: PoseFrame, config: VisionConfig) -> None:
        self.frame = frame
        self.config = config

    def visible(self, name: str) -> Keypoint | None:
        point = self.frame.keypoints.get(name)
        if point is None or not point.visibility >= self.config.min_keypoint_visibility:
            return None
        if not (math.isfinite(point.x) and math.isfinite(point.y)):
            return None
        return point

    def shoulder_width(self) -> float | None:
        left, right = self.visible("left_shoulder"), self.visible("right_shoulder")
        if left is None or right is None:
            return None
        width = _dist(left, right)
        return width if width > 1e-6 else None

    @property
    def pose_usable(self) -> bool:
        """A person was detected and the upper body is measurable."""
        return self.frame.person_present is True and self.shoulder_width() is not None

    def head_facing(self) -> float | None:
        """1 = nose centred between ears/eyes (toward camera), 0 = profile."""
        nose = self.visible("nose")
        if nose is None:
            # Back turned and low confidence look identical here: report unknown,
            # never a negative observation.
            return None
        for left_name, right_name in (("left_ear", "right_ear"), ("left_eye", "right_eye")):
            left, right = self.visible(left_name), self.visible(right_name)
            if left is not None and right is not None:
                half_span = abs(left.x - right.x) / 2
                if half_span <= 1e-6:
                    return None
                offset = abs(nose.x - (left.x + right.x) / 2) / half_span
                return _clamp(1 - offset / self.config.head_yaw_full)
        left_ear, right_ear = self.visible("left_ear"), self.visible("right_ear")
        if (left_ear is None) != (right_ear is None):
            return 0.0  # nose plus exactly one ear: head in profile
        return None

    def body_facing(self) -> float | None:
        """Shoulder span relative to torso length; only with both hips visible."""
        width = self.shoulder_width()
        hips = self.visible("left_hip"), self.visible("right_hip")
        if width is None or None in hips:
            return None
        left_s, right_s = self.visible("left_shoulder"), self.visible("right_shoulder")
        shoulder_mid = ((left_s.x + right_s.x) / 2, (left_s.y + right_s.y) / 2)
        hip_mid = ((hips[0].x + hips[1].x) / 2, (hips[0].y + hips[1].y) / 2)
        torso = math.hypot(shoulder_mid[0] - hip_mid[0], shoulder_mid[1] - hip_mid[1])
        if torso <= 1e-6:
            return None
        side, front = self.config.shoulder_ratio_side, self.config.shoulder_ratio_front
        return _clamp((width / torso - side) / (front - side))

    def facing(self) -> float | None:
        """Head cue is required; the body cue can only lower it (turned torso)."""
        if not self.pose_usable:
            return None
        head = self.head_facing()
        if head is None:
            return None
        body = self.body_facing()
        return head if body is None else min(head, body)


def arm_speed(previous: FrameFeatures, current: FrameFeatures) -> float | None:
    """Mean elbow/wrist speed in shoulder-widths per second between two frames."""
    dt = current.frame.timestamp_s - previous.frame.timestamp_s
    if not 0 < dt <= MAX_PAIR_GAP_S or not (previous.pose_usable and current.pose_usable):
        return None
    scale = (previous.shoulder_width() + current.shoulder_width()) / 2
    speeds = [
        _dist(a, b) / scale / dt
        for name in ARM_JOINTS
        if (a := previous.visible(name)) is not None and (b := current.visible(name)) is not None
    ]
    return sum(speeds) / len(speeds) if speeds else None


@dataclass(frozen=True)
class WindowSummary:
    """Canonical ``vision.metrics`` payload fields for one capture window."""

    window_start_s: float
    window_end_s: float
    availability: str
    person_present: bool | None
    pose_available: bool | None
    facing_score: float | None
    activity_score: float | None
    frames: int
    index: int = -1  # window number on the session clock grid (stable event ID)

    def payload(self) -> dict:
        return {
            "window_start_s": self.window_start_s,
            "window_end_s": self.window_end_s,
            "availability": self.availability,
            "person_present": self.person_present,
            "pose_available": self.pose_available,
            "facing_score": self.facing_score,
            "activity_score": self.activity_score,
        }


def summarize(
    start_s: float,
    end_s: float,
    frames: list[FrameFeatures],
    speeds: list[float],
    config: VisionConfig,
) -> WindowSummary:
    """Aggregate one window. Missing/undecided input yields nulls, never low scores."""
    n = len(frames)
    if n == 0:
        # Camera produced nothing in this window (stall/failure): input unavailable.
        return WindowSummary(start_s, end_s, "unavailable", None, None, None, None, 0)
    need = config.min_decision_fraction
    present = sum(f.frame.person_present is True for f in frames)
    absent = sum(f.frame.person_present is False for f in frames)
    if present >= need * n and present > 0:
        person: bool | None = True
    elif absent >= need * n and absent > 0:
        person = False
    else:
        person = None

    if person is True:
        posed = [f for f in frames if f.pose_usable]
        pose: bool | None = len(posed) >= need * present
    elif person is False:
        posed, pose = [], False
    else:
        posed, pose = [], None

    facing = activity = None
    if pose is True:
        values = [v for f in posed if (v := f.facing()) is not None]
        if len(values) >= config.min_facing_frames:
            facing = round(median(values), 4)
        if len(speeds) >= config.min_activity_pairs:
            mean = sum(speeds) / len(speeds)
            span = config.activity_full - config.activity_noise_floor
            activity = round(_clamp((mean - config.activity_noise_floor) / span), 4)
    return WindowSummary(start_s, end_s, "available", person, pose, facing, activity, n)


class WindowAggregator:
    """Groups capture-stamped frames into fixed, non-overlapping windows.

    ``begin`` (optional) sets when capture actually started, so the startup gap
    before the camera opened is not reported as unavailable windows. ``add`` returns
    the windows a newer frame has completed (including empty, unavailable windows if
    capture stalled); ``finish`` closes the trailing window at the capture end.
    Frames must arrive in capture order; older frames are ignored.
    """

    def __init__(self, config: VisionConfig | None = None) -> None:
        self.config = config or VisionConfig()
        self._index = 0
        self._frames: list[FrameFeatures] = []
        self._speeds: list[float] = []
        self._previous: FrameFeatures | None = None
        self._closed = False
        self._first: tuple[int, float] | None = None  # (index, clipped start)

    def begin(self, capture_start_s: float) -> None:
        """Start the first window at ``capture_start_s`` instead of session time 0.

        The first window is clipped to start there; if that would leave less than
        ``min_final_window_s`` before the next grid boundary, it extends to the
        following boundary instead. Must be called before the first frame.
        """
        if self._frames or self._previous is not None or self._closed:
            raise RuntimeError("begin must precede the first frame")
        if not (math.isfinite(capture_start_s) and capture_start_s >= 0):
            raise ValueError("capture start must be finite and non-negative")
        w = self.config.window_s
        index = int(capture_start_s // w)
        if (index + 1) * w - capture_start_s < self.config.min_final_window_s:
            index += 1
        self._index = index
        self._first = (index, capture_start_s)

    def _bounds(self, index: int) -> tuple[float, float]:
        w = self.config.window_s
        start = round(index * w, 6)
        if self._first is not None and index == self._first[0]:
            start = self._first[1]
        return start, round((index + 1) * w, 6)

    def _close_current(self, end_s: float | None = None) -> WindowSummary:
        start, natural_end = self._bounds(self._index)
        summary = summarize(
            start,
            natural_end if end_s is None else end_s,
            self._frames,
            self._speeds,
            self.config,
        )
        summary = replace(summary, index=self._index)
        self._index += 1
        self._frames, self._speeds = [], []
        return summary

    def add(self, frame: PoseFrame) -> list[WindowSummary]:
        if self._closed or not (math.isfinite(frame.timestamp_s) and frame.timestamp_s >= 0):
            return []
        if self._previous is not None and frame.timestamp_s <= self._previous.frame.timestamp_s:
            return []
        done = []
        target = int(frame.timestamp_s // self.config.window_s)
        while self._index < target:
            done.append(self._close_current())
        features = FrameFeatures(frame, self.config)
        if (
            self._previous is not None
            and (speed := arm_speed(self._previous, features)) is not None
        ):
            self._speeds.append(speed)
        self._frames.append(features)
        self._previous = features
        return done

    def finish(self, capture_end_s: float) -> list[WindowSummary]:
        """Close every window up to ``capture_end_s``; drop a too-short trailing one."""
        if self._closed:
            return []
        self._closed = True
        done = []
        while True:
            start, end = self._bounds(self._index)
            if end <= capture_end_s:
                done.append(self._close_current())
                continue
            if capture_end_s - start >= self.config.min_final_window_s:
                # Exact capture end: rounding up could land after it and be rejected.
                done.append(self._close_current(capture_end_s))
            return done
