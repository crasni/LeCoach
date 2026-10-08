"""Hardware/model boundary for the vision adapter.

The adapter depends only on these protocols, so a camera, pose model or
accelerator (e.g. a future UGen300 path) can change without touching windowing,
events or lifecycle. Implementations run on the adapter's worker thread.
"""

from collections.abc import Callable
from typing import Any, Protocol

from .features import PoseFrame


class VisionUnavailable(Exception):
    """Expected device/model condition, reported as ``signal.status``, never as behavior.

    ``reason`` is a short snake_case code shown in the UI notice, e.g.
    ``camera_permission_denied``, ``camera_not_found``, ``pose_model_missing``.
    """

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason


class FrameSource(Protocol):
    def open(self) -> None:
        """Acquire the camera; raise ``VisionUnavailable`` on expected failures."""

    def read(self) -> Any | None:
        """Block for the next frame; ``None`` is a transient read failure."""

    def close(self) -> None:
        """Release the camera. Must be idempotent."""


class PoseEstimator(Protocol):
    def open(self) -> None:
        """Load the model; raise ``VisionUnavailable`` if runtime/model is missing."""

    def estimate(self, frame: Any, timestamp_s: float) -> PoseFrame:
        """Return keypoints for one frame in isotropic units, stamped ``timestamp_s``."""

    def close(self) -> None:
        """Release model resources. Must be idempotent."""


# (frame, jpeg_quality) -> JPEG bytes, or None if encoding failed.
JpegEncoder = Callable[[Any, int], bytes | None]
