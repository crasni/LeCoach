"""OpenCV camera + MediaPipe Pose Landmarker backend (CPU, fully local).

Runtime packages are imported lazily so the rest of the lane (and the app) works
without them. Adding them to the shared manifest is an integration decision
(VIS-01 handoff); until then a missing runtime is reported as
``signal.status unavailable/pose_runtime_missing``, never as behavior.

The Pose Landmarker ``.task`` model is downloaded by the user into the ignored
``models/`` directory (see ``src/lecoach/vision/README.md``); it is never committed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .backend import VisionUnavailable
from .features import Keypoint, PoseFrame

DEFAULT_MODEL_PATH = Path("models/pose_landmarker_lite.task")
MODEL_ENV = "LECOACH_POSE_MODEL"
CAMERA_ENV = "LECOACH_CAMERA_INDEX"

# MediaPipe Pose (BlazePose, 33 landmarks) indices for the lane's keypoint subset.
MEDIAPIPE_LANDMARKS = {
    "nose": 0,
    "left_eye": 2,
    "right_eye": 5,
    "left_ear": 7,
    "right_ear": 8,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_hip": 23,
    "right_hip": 24,
}


def _import_cv2():
    try:
        import cv2
    except ImportError as error:
        raise VisionUnavailable("pose_runtime_missing", "OpenCV (cv2) not installed") from error
    return cv2


class OpenCVCamera:
    """Local webcam via OpenCV. Frames are BGR ``numpy`` arrays."""

    def __init__(self, index: int | None = None, width: int = 640, height: int = 480) -> None:
        self.index = int(os.environ.get(CAMERA_ENV, 0)) if index is None else index
        self.width, self.height = width, height
        self._capture = None

    def open(self) -> None:
        cv2 = _import_cv2()
        backend = cv2.CAP_AVFOUNDATION if sys.platform == "darwin" else cv2.CAP_ANY
        capture = cv2.VideoCapture(self.index, backend)
        if not capture.isOpened():
            capture.release()
            # OpenCV cannot tell a denied permission from a missing device.
            raise VisionUnavailable(
                "camera_unavailable", "camera missing, busy or permission denied"
            )
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        ok, _ = capture.read()
        if not ok:
            capture.release()
            raise VisionUnavailable("camera_unavailable", "camera opened but returned no frame")
        self._capture = capture

    def read(self):
        capture = self._capture
        if capture is None:
            return None
        ok, frame = capture.read()
        return frame if ok else None

    def close(self) -> None:
        capture, self._capture = self._capture, None
        if capture is not None:
            capture.release()


def opencv_jpeg(frame, quality: int) -> bytes | None:
    cv2 = _import_cv2()
    ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buffer.tobytes() if ok else None


class MediaPipePose:
    """MediaPipe Tasks Pose Landmarker in VIDEO mode, one person, CPU delegate."""

    def __init__(
        self,
        model_path: str | Path | None = None,
        min_detection_confidence: float = 0.5,
        min_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ) -> None:
        self.model_path = Path(model_path or os.environ.get(MODEL_ENV, DEFAULT_MODEL_PATH))
        self.min_detection_confidence = min_detection_confidence
        self.min_presence_confidence = min_presence_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self._landmarker = None
        self._mp = None
        self._cv2 = None
        self._last_ms = -1

    def open(self) -> None:
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import vision
            from mediapipe.tasks.python.core.base_options import BaseOptions
        except ImportError as error:
            raise VisionUnavailable("pose_runtime_missing", "mediapipe not installed") from error
        self._cv2 = _import_cv2()
        if not self.model_path.is_file():
            raise VisionUnavailable("pose_model_missing", str(self.model_path))
        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(self.model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=self.min_detection_confidence,
            min_pose_presence_confidence=self.min_presence_confidence,
            min_tracking_confidence=self.min_tracking_confidence,
        )
        self._mp = mp
        self._landmarker = vision.PoseLandmarker.create_from_options(options)

    def estimate(self, frame, timestamp_s: float) -> PoseFrame:
        height, width = frame.shape[:2]
        rgb = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        # VIDEO mode requires strictly increasing millisecond timestamps.
        ms = max(int(timestamp_s * 1000), self._last_ms + 1)
        self._last_ms = ms
        result = self._landmarker.detect_for_video(image, ms)
        if not result.pose_landmarks:
            # Below the detector's confidence thresholds: no person observed.
            return PoseFrame(timestamp_s, False)
        landmarks = result.pose_landmarks[0]
        keypoints = {}
        for name, index in MEDIAPIPE_LANDMARKS.items():
            mark = landmarks[index]
            visibility = min(
                getattr(mark, "visibility", None) or 0.0, getattr(mark, "presence", None) or 1.0
            )
            # Pixels keep x and y isotropic for distance ratios.
            keypoints[name] = Keypoint(mark.x * width, mark.y * height, visibility)
        return PoseFrame(timestamp_s, True, keypoints)

    def close(self) -> None:
        landmarker, self._landmarker = self._landmarker, None
        if landmarker is not None:
            landmarker.close()


def build_local_adapter(
    model_path: str | Path | None = None,
    camera_index: int | None = None,
    config=None,
    on_frame=None,
):
    """Composition helper for integration: the default local camera/pose adapter."""
    from .adapter import LocalVisionAdapter

    return LocalVisionAdapter(
        source_factory=lambda: OpenCVCamera(camera_index),
        estimator_factory=lambda: MediaPipePose(model_path),
        encoder=opencv_jpeg,
        config=config,
        on_frame=on_frame,
    )
