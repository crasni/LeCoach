"""Local debug view for the probe: mirrored camera, detected skeleton and live readout.

Display only — nothing is saved. OpenCV windows must be driven from the main
thread, so the capture worker only hands over its latest frame/pose and the
probe's main-thread loop calls ``show``. Not used by the web app.
"""

from __future__ import annotations

import os
import sys
import threading

from .config import VisionConfig
from .features import FrameFeatures, PoseFrame

BONES = (
    ("left_ear", "left_eye"),
    ("left_eye", "nose"),
    ("nose", "right_eye"),
    ("right_eye", "right_ear"),
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
)
WINDOW = "LeCoach vision probe (q to quit)"


def display_available() -> bool:
    """OpenCV aborts the process (not an exception) when no display exists on Linux."""
    if sys.platform.startswith("linux"):
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    return True


def _fmt(value) -> str:
    return "--" if value is None else f"{value:.2f}"


class ProbeViewer:
    def __init__(self, config: VisionConfig | None = None) -> None:
        import cv2  # only needed when the window is enabled

        self.cv2 = cv2
        self.config = config or VisionConfig()
        self._lock = threading.Lock()
        self._latest: tuple[object, PoseFrame] | None = None
        self.enabled = display_available()
        if not self.enabled:
            print("(no display; running without preview window)", flush=True)

    def on_frame(self, frame, pose: PoseFrame) -> None:
        """Worker-thread hook: keep only the newest frame and its pose."""
        with self._lock:
            self._latest = (frame, pose)

    def compose(self, frame, pose: PoseFrame, lines: list[str]):
        """Return a mirrored copy of ``frame`` with skeleton and text drawn on it."""
        cv2 = self.cv2
        image = frame.copy()
        features = FrameFeatures(pose, self.config)
        points = {
            name: (int(p.x), int(p.y))
            for name in pose.keypoints
            if (p := features.visible(name)) is not None
        }
        for a, b in BONES:
            if a in points and b in points:
                cv2.line(image, points[a], points[b], (80, 220, 80), 2, cv2.LINE_AA)
        for name, xy in points.items():
            colour = (0, 200, 255) if name == "nose" else (255, 255, 255)
            cv2.circle(image, xy, 4, colour, -1, cv2.LINE_AA)
        image = cv2.flip(image, 1)  # mirror so moving left looks like left
        frame_facing = features.facing()
        lines = lines + [
            f"person={pose.person_present}  frame facing={_fmt(frame_facing)}",
        ]
        # One white text pass on a translucent dark panel: an outline drawn as a
        # second, thicker pass read as two overlapping copies on scaled displays.
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = max(0.5, image.shape[1] / 1100)
        thickness = 1 if scale < 0.9 else 2
        sizes = [cv2.getTextSize(text, font, scale, thickness) for text in lines]
        line_h = max(h + base for (_, h), base in sizes) + 8
        pad = 10
        width = min(image.shape[1], max(w for (w, _), _ in sizes) + 2 * pad)
        height = min(image.shape[0], line_h * len(lines) + pad)
        panel = image[:height, :width]
        panel[:] = (panel * 0.35).astype(panel.dtype)
        y = pad
        for text, ((_, h), _) in zip(lines, sizes):
            y += h
            cv2.putText(image, text, (pad, y), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)
            y += line_h - h
        return image

    def show(self, lines: list[str]) -> bool:
        """Draw the newest frame; returns False if the user pressed q/Esc."""
        if not self.enabled:
            return True
        with self._lock:
            latest = self._latest
        cv2 = self.cv2
        try:
            if latest is not None:
                cv2.imshow(WINDOW, self.compose(latest[0], latest[1], lines))
            key = cv2.waitKey(1) & 0xFF
        except cv2.error:
            self.enabled = False  # no display available: keep running headless
            print("(preview window unavailable; continuing without it)", flush=True)
            return True
        return key not in (ord("q"), 27)

    def close(self) -> None:
        if not self.enabled:
            return
        try:
            self.cv2.destroyAllWindows()
            self.cv2.waitKey(1)
        except self.cv2.error:
            pass
