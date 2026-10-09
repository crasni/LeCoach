"""Local camera → pose → ``vision.metrics`` producer implementing ``VisionAdapter``.

Lifecycle (ARCHITECTURE "capture adapter protocol"):

* ``start`` opens the model and camera off the event loop and returns once capture
  is running. Expected device/model failures emit ``signal.status`` (unavailable)
  and return normally so the speech pipeline stays usable.
* Capture and inference run on one worker thread. Frames are stamped with the
  shared session clock immediately after capture; emissions are marshalled back
  onto the event loop with ``call_soon_threadsafe``.
* ``stop_capture`` stops acquisition and waits for the worker to release the
  camera; ``drain`` closes the trailing window at the capture end. Both are
  idempotent and cancellation-safe: the worker owns and always closes its devices.

No frames or keypoints are persisted. The preview keeps only the latest JPEG.
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from collections.abc import Callable
from concurrent.futures import Future

from lecoach.contracts.interfaces import SessionContext

from .backend import FrameSource, JpegEncoder, PoseEstimator, VisionUnavailable
from .config import VisionConfig
from .features import PoseFrame, WindowAggregator, WindowSummary

log = logging.getLogger(__name__)


class VisionStats:
    """Counters for VIS-02 throughput/latency evidence (no image data)."""

    def __init__(self) -> None:
        self.frames_read = 0
        self.read_failures = 0
        self.frames_inferred = 0
        self.inference_errors = 0
        self.inference_s_total = 0.0
        self.inference_s_max = 0.0
        self.windows_emitted = 0
        # Shared-clock delay between a window's end and its emission.
        self.emit_lag_s_total = 0.0
        self.emit_lag_s_max = 0.0
        self.capture_started_s: float | None = None
        self.capture_stopped_s: float | None = None
        # Wall time spent releasing camera + model (macOS AVFoundation varies).
        self.camera_close_s: float | None = None

    def as_dict(self) -> dict:
        inferred = max(self.frames_inferred, 1)
        windows = max(self.windows_emitted, 1)
        span = None
        if self.capture_started_s is not None and self.capture_stopped_s is not None:
            span = self.capture_stopped_s - self.capture_started_s
        return {
            "frames_read": self.frames_read,
            "read_failures": self.read_failures,
            "frames_inferred": self.frames_inferred,
            "inference_errors": self.inference_errors,
            "inference_ms_mean": round(1000 * self.inference_s_total / inferred, 2),
            "inference_ms_max": round(1000 * self.inference_s_max, 2),
            "capture_fps": round(self.frames_read / span, 2) if span else None,
            "inference_fps": round(self.frames_inferred / span, 2) if span else None,
            "windows_emitted": self.windows_emitted,
            "emit_lag_ms_mean": round(1000 * self.emit_lag_s_total / windows, 2),
            "emit_lag_ms_max": round(1000 * self.emit_lag_s_max, 2),
            "camera_close_ms": (
                round(1000 * self.camera_close_s, 2) if self.camera_close_s is not None else None
            ),
        }


class LocalVisionAdapter:
    def __init__(
        self,
        source_factory: Callable[[], FrameSource],
        estimator_factory: Callable[[], PoseEstimator],
        encoder: JpegEncoder | None = None,
        config: VisionConfig | None = None,
        on_window: Callable[[WindowSummary], None] | None = None,
        on_frame: Callable[[object, PoseFrame], None] | None = None,
    ) -> None:
        self.config = config or VisionConfig()
        self._source_factory = source_factory
        self._estimator_factory = estimator_factory
        self._encoder = encoder
        self._on_window = on_window
        # Local debug view only (probe window); called on the worker thread.
        self._on_frame = on_frame
        self.stats = VisionStats()
        self._context: SessionContext | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._opening: asyncio.Future | None = None
        self._worker: threading.Thread | None = None
        self._worker_done: Future | None = None
        self._aggregator = WindowAggregator(self.config)
        self._capture_end_s: float | None = None
        self._preview: bytes | None = None
        self._started = self._drained = False
        self._devices_claimed = False  # opened devices owned by the worker or released
        self._status_count = 0
        self.released = True  # no device held until start opens one

    # ------------------------------------------------------------------ protocol
    async def start(self, context: SessionContext) -> None:
        if self._started:
            return
        self._started = True
        self._context = context
        self._loop = asyncio.get_running_loop()
        self._opening = self._loop.run_in_executor(None, self._open_devices)
        try:
            devices = await asyncio.shield(self._opening)
        except VisionUnavailable as error:
            self._status("unavailable", error.reason)
            return
        except asyncio.CancelledError:
            # Opening may still finish in its thread: release whatever it returns.
            self._stop.set()
            self._opening.add_done_callback(self._discard_opened)
            raise
        if devices is None:  # stop requested while opening
            return
        if self._stop.is_set() or self._devices_claimed:
            self._discard(devices)
            return
        self._devices_claimed = True
        self.stats.capture_started_s = context.clock.now()
        # Windows before the camera opened are startup, not missing input.
        self._aggregator.begin(self.stats.capture_started_s)
        self._status("available", "capture_started")
        self._worker_done = Future()
        self._worker = threading.Thread(
            target=self._run, args=devices, name="lecoach-vision", daemon=True
        )
        self._worker.start()

    async def stop_capture(self, capture_end_s: float) -> None:
        with self._lock:
            if self._capture_end_s is None:
                self._capture_end_s = capture_end_s
            self._stop.set()
        if self._opening is not None:
            [devices] = await asyncio.gather(asyncio.shield(self._opening), return_exceptions=True)
            if isinstance(devices, tuple) and not self._devices_claimed:
                self._discard(devices)
        if self._worker_done is not None:
            await asyncio.wrap_future(self._worker_done)

    async def drain(self) -> None:
        if self._drained:
            return
        try:
            if self._worker_done is not None:
                await asyncio.wrap_future(self._worker_done)
            self._drained = True
            # Normally already closed by the worker; covers a worker that ended on a
            # camera failure before stop_capture supplied the capture end.
            if self._worker is not None and self._capture_end_s is not None:
                for summary in self._aggregator.finish(self._capture_end_s):
                    self._emit_window(summary)
        finally:
            self._preview = None

    def preview_jpeg(self) -> bytes | None:
        return self._preview

    # ---------------------------------------------------------------- internals
    def _open_devices(self) -> tuple[FrameSource, PoseEstimator] | None:
        """Runs in an executor thread. Opens the model first (cheap failure)."""
        estimator = source = None
        try:
            estimator = self._estimator_factory()
            estimator.open()
            source = self._source_factory()
            self.released = False
            source.open()
        except VisionUnavailable:
            self._close(source, estimator)
            raise
        except Exception as error:  # unexpected backend failure: still a device notice
            self._close(source, estimator)
            log.exception("vision backend failed to open")
            raise VisionUnavailable("camera_start_failed", type(error).__name__) from error
        if self._stop.is_set():
            self._close(source, estimator)
            return None
        return source, estimator

    def _discard(self, devices: tuple[FrameSource, PoseEstimator]) -> None:
        """Release devices that were opened but never handed to a worker (loop thread)."""
        if self._devices_claimed:
            return
        self._devices_claimed = True
        self._close(*devices)

    def _discard_opened(self, opening: asyncio.Future) -> None:
        if opening.cancelled() or opening.exception() is not None:
            return
        if isinstance(devices := opening.result(), tuple):
            self._discard(devices)

    def _close(self, source: FrameSource | None, estimator: PoseEstimator | None) -> None:
        for resource in (source, estimator):
            if resource is None:
                continue
            try:
                resource.close()
            except Exception:
                log.exception("vision resource close failed")
        self.released = True

    def _run(self, source: FrameSource, estimator: PoseEstimator) -> None:
        clock, config = self._context.clock, self.config
        failures = 0
        last_preview = float("-inf")
        interval = 1 / config.max_inference_fps
        next_inference = float("-inf")
        try:
            while not self._stop.is_set():
                frame = source.read()
                now = clock.now()
                end = self._capture_end_s
                if end is not None and now > end:
                    break
                if frame is None:
                    failures += 1
                    self.stats.read_failures += 1
                    if failures >= config.max_consecutive_read_failures:
                        self._post(self._status, "error", "camera_read_failed")
                        break
                    continue
                failures = 0
                self.stats.frames_read += 1
                if self._encoder is not None and now - last_preview >= 1 / config.preview_fps:
                    last_preview = now
                    self._update_preview(frame)
                # Fixed-rate schedule: measuring from the last processed frame would
                # undershoot (a 23 fps camera gave ~7.7/s at a 10/s cap). 5 ms slack
                # keeps frames exactly one interval apart.
                if now < next_inference - 0.005:
                    continue
                if now - next_inference < interval:
                    next_inference += interval
                else:  # first frame or after a stall: restart the schedule
                    next_inference = now + interval
                pose = self._estimate(estimator, frame, now)
                if self._on_frame is not None:
                    try:
                        self._on_frame(frame, pose)
                    except Exception:
                        log.debug("on_frame hook failed", exc_info=True)
                for summary in self._aggregator.add(pose):
                    self._post(self._emit_window, summary)
        except Exception:
            log.exception("vision capture loop failed")
            self._post(self._status, "error", "vision_capture_failed")
        finally:
            self.stats.capture_stopped_s = clock.now()
            with self._lock:
                end = self._capture_end_s
            if end is not None:
                # Close the trailing window now, not after the (slow) camera release
                # in drain(): it was the remaining max emit lag on real hardware.
                try:
                    for summary in self._aggregator.finish(end):
                        self._post(self._emit_window, summary)
                except Exception:
                    log.exception("vision trailing window failed")
            started = time.perf_counter()
            self._close(source, estimator)
            self.stats.camera_close_s = time.perf_counter() - started
            self._preview = None
            self._worker_done.set_result(None)

    def _estimate(self, estimator: PoseEstimator, frame, now: float) -> PoseFrame:
        started = time.perf_counter()
        try:
            pose = estimator.estimate(frame, now)
        except Exception:
            # One failed inference is an undecided frame, never "no person".
            self.stats.inference_errors += 1
            log.debug("pose inference failed", exc_info=True)
            return PoseFrame(now, None)
        finally:
            elapsed = time.perf_counter() - started
            self.stats.frames_inferred += 1
            self.stats.inference_s_total += elapsed
            self.stats.inference_s_max = max(self.stats.inference_s_max, elapsed)
        if pose.timestamp_s != now:  # capture time is authoritative
            pose = PoseFrame(now, pose.person_present, pose.keypoints)
        return pose

    def _update_preview(self, frame) -> None:
        try:
            jpeg = self._encoder(frame, self.config.preview_jpeg_quality)
        except Exception:
            log.debug("preview encoding failed", exc_info=True)
            return
        if jpeg and len(jpeg) <= self.config.preview_max_bytes:
            self._preview = jpeg

    def _post(self, callback, *args) -> None:
        try:
            self._loop.call_soon_threadsafe(callback, *args)
        except RuntimeError:  # loop already closed: session is gone
            pass

    def _emit(self, value: dict) -> None:
        try:
            self._context.emit(value)
        except Exception:
            log.exception("vision event rejected by the session")

    def _emit_window(self, summary: WindowSummary) -> None:
        context = self._context
        lag = max(0.0, context.clock.now() - summary.window_end_s)
        self.stats.windows_emitted += 1
        self.stats.emit_lag_s_total += lag
        self.stats.emit_lag_s_max = max(self.stats.emit_lag_s_max, lag)
        index = summary.index
        self._emit(
            {
                "schema_version": 0,
                "session_id": context.session_id,
                "event_id": f"vision-{index}",
                "source": "vision",
                "type": "vision.metrics",
                "timestamp_s": summary.window_end_s,
                "payload": summary.payload(),
            }
        )
        if self._on_window is not None:
            self._on_window(summary)

    def _status(self, availability: str, reason: str) -> None:
        context = self._context
        self._status_count += 1
        self._emit(
            {
                "schema_version": 0,
                "session_id": context.session_id,
                "event_id": f"vision-status-{self._status_count}",
                "source": "vision",
                "type": "signal.status",
                "timestamp_s": context.clock.now(),
                "payload": {"availability": availability, "reason": reason},
            }
        )
