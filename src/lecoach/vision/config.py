"""Every vision-lane default and unit in one place (Lane 3, VIS-01).

These are demo heuristics on top of an approximate pose model, not validated
measures. Facing approximates head/body orientation toward the camera; it is not
eye contact, attention or emotion. VIS-02 measures and tunes them on real capture.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VisionConfig:
    # --- windowing (seconds, shared session clock) -------------------------------
    # Non-overlapping metric windows. The engine's vision_stale_s (6 s) and
    # max_window_gap_s (5 s) both assume roughly 1 s cadence.
    window_s: float = 1.0
    # A trailing window shorter than this at stop is dropped rather than emitted.
    min_final_window_s: float = 0.5

    # --- per-frame keypoint usability --------------------------------------------
    # Keypoints below this visibility/presence are treated as not observed.
    min_keypoint_visibility: float = 0.5

    # --- window decisions ----------------------------------------------------------
    # Fraction of frames in a window that must agree before person_present/pose
    # become True/False; otherwise the window reports null ("cannot decide").
    min_decision_fraction: float = 0.5
    # Frames with a computable facing value needed before facing_score is reported.
    min_facing_frames: int = 3
    # Consecutive frame pairs with comparable arm keypoints needed for activity.
    min_activity_pairs: int = 2

    # --- facing mapping ------------------------------------------------------------
    # Head yaw cue: nose offset from the ear (or eye) midpoint as a fraction of half
    # the ear (eye) span. 0 → centred (facing camera); >= head_yaw_full → profile.
    head_yaw_full: float = 1.0
    # Body cue: shoulder span / torso length. Front-on ~= shoulder_ratio_front;
    # sideways shrinks toward 0. Only used when both hips are visible.
    shoulder_ratio_front: float = 0.9
    shoulder_ratio_side: float = 0.25

    # --- activity mapping ----------------------------------------------------------
    # Mean wrist/elbow speed in body-scale units per second. Speeds below the noise
    # floor count as still (keypoint jitter); activity reaches 1 at activity_full.
    activity_noise_floor: float = 0.15
    activity_full: float = 2.0
    # Body scale for activity = max(shoulder span, neck_scale_ratio x nose-to-shoulder
    # midpoint distance). Shoulder span alone shrinks when the presenter turns
    # sideways (~30 % in profile), which inflated activity while turned away; the
    # neck length barely changes with yaw. Front-on, shoulder span still dominates.
    neck_scale_ratio: float = 1.5

    # --- capture / load caps ---------------------------------------------------------
    # Pose inference is throttled to this rate so the audience UI stays responsive.
    max_inference_fps: float = 10.0
    # Latest-frame JPEG preview (ARCHITECTURE: 512 kB, 5 frames/s by default).
    preview_fps: float = 5.0
    preview_max_bytes: int = 512_000
    preview_jpeg_quality: int = 70
    # Consecutive camera read failures before capture is declared failed.
    max_consecutive_read_failures: int = 15

    def __post_init__(self) -> None:
        positive = (
            "window_s",
            "min_final_window_s",
            "head_yaw_full",
            "activity_full",
            "neck_scale_ratio",
            "max_inference_fps",
            "preview_fps",
        )
        for name in positive:
            value = getattr(self, name)
            if not (value > 0 and value < float("inf")):
                raise ValueError(f"{name} must be positive and finite")
        if self.min_final_window_s > self.window_s:
            raise ValueError("min_final_window_s cannot exceed window_s")
        for name in ("min_keypoint_visibility", "min_decision_fraction"):
            if not 0 <= getattr(self, name) <= 1:
                raise ValueError(f"{name} must be within [0, 1]")
        if not 0 <= self.activity_noise_floor < self.activity_full:
            raise ValueError("activity noise floor must be below activity_full")
        if not 0 <= self.shoulder_ratio_side < self.shoulder_ratio_front:
            raise ValueError("side shoulder ratio must be below the front ratio")
        if min(self.min_facing_frames, self.min_activity_pairs) < 1:
            raise ValueError("minimum frame counts must be at least 1")
        if self.preview_max_bytes < 1 or not 1 <= self.preview_jpeg_quality <= 100:
            raise ValueError("invalid preview limits")
        if self.max_consecutive_read_failures < 1:
            raise ValueError("max_consecutive_read_failures must be at least 1")
