"""Live speech adapter behind the INT-01 `CaptureAdapter` seam.

Threads: the device callback only queues audio. A voice-activity thread segments
it in real time and advances the capture watermark; a transcription thread runs
the shared model, so slow inference never stalls segmentation. All pipeline
state and every `context.emit` call run on the session's event loop, reached
with `call_soon_threadsafe`.

Capture time is the clock reading at start plus elapsed samples, floored to the
millisecond. On the loop it is also capped at the clock (audio clock drift) and,
after stop, at the capture end, so the controller never drops an observation as
being later than capture end.
"""

import asyncio
import queue
import threading
from array import array
from collections.abc import Callable, Sequence

from lecoach.contracts.interfaces import SessionContext

from .config import SpeechConfig
from .emitter import floor_ms
from .pipeline import SpeechPipeline
from .seams import (
    AudioSource,
    Boundary,
    MicrophoneError,
    Segmenter,
    Transcriber,
    Transcription,
)

_STOP = ("stop",)


class SpeechAdapter:
    """One instance per session. The transcriber is preloaded and shared.

    Device and model failures become a speech `signal.status` followed by
    non-available windows (degraded mode), so the session keeps running for
    other inputs. Other start failures propagate to the controller, which
    reports them generically; speech then emits nothing further.
    """

    def __init__(
        self,
        config: SpeechConfig,
        source: AudioSource | None,
        segmenter: Segmenter | None,
        transcriber: Transcriber | None,
        *,
        max_backlog_chunks: int = 200,
        idle_tick_s: float = 0.1,
        lookback_s: float = 1.0,
    ) -> None:
        self.config = config
        self.source, self.segmenter, self.transcriber = source, segmenter, transcriber
        self.max_backlog_chunks = max_backlog_chunks
        self.idle_tick_s = idle_tick_s
        self.lookback_frames = int(lookback_s * config.sample_rate)
        self._max_utterance_frames = round(config.max_utterance_s * config.sample_rate)
        self.errors: list[str] = []  # emission and device-release failures, for diagnostics
        self.analyzed_s = 0.0  # capture time segmented so far; clock minus this is the lag
        # Worker-thread state.
        self._audio: queue.SimpleQueue = queue.SimpleQueue()
        self._jobs: queue.SimpleQueue = queue.SimpleQueue()
        self._abort = threading.Event()
        self._threads: list[threading.Thread] = []
        self._source_lock = threading.Lock()
        self._source_open = False
        self._frames = 0
        self._end_frame: int | None = None
        self._last_ended_seq = 0
        self._partial_pending = False
        self._failure_lock = threading.Lock()
        self._transcription_failed = False
        self._segmented_until_s: float | None = None
        # Event-loop state.
        self._loop: asyncio.AbstractEventLoop | None = None
        self._context: SessionContext | None = None
        self._pipeline: SpeechPipeline | None = None
        self._origin_s = 0.0
        self._capture_end_s: float | None = None
        self._ticker: asyncio.TimerHandle | None = None
        self._unavailable = False
        self._closed = False
        self._started = self._stopped = self._drained = False

    # Session seam ---------------------------------------------------------

    async def start(self, context: SessionContext) -> None:
        if self._started:
            return
        self._started = True
        self._context, self._loop = context, asyncio.get_running_loop()
        self._pipeline = SpeechPipeline(context.session_id, self.config)
        self._segmented, self._transcribed = asyncio.Event(), asyncio.Event()
        now = floor_ms(context.clock.now())
        if self.transcriber is None or not self.transcriber.ready:
            return self._enter_degraded(now, "error", "speech_model_unavailable")
        if self.source is None or self.segmenter is None:
            return self._enter_degraded(now, "unavailable", "microphone_not_found")
        self._origin_s = now
        try:
            with self._source_lock:
                self._source_open = True  # close() then runs once even if open fails partway
                self.source.open(self._on_audio, self._on_device_error)
        except MicrophoneError as error:
            self._release_source()
            return self._enter_degraded(now, error.availability, error.reason)
        except BaseException:
            self._release_source()
            self._pipeline = None  # the controller reports the failure; emit nothing more
            raise
        self._threads = [
            threading.Thread(target=self._segment_loop, name="lecoach-speech-vad", daemon=True),
            threading.Thread(target=self._transcribe_loop, name="lecoach-speech-asr",
                             daemon=True),
        ]
        for thread in self._threads:
            thread.start()

    async def stop_capture(self, capture_end_s: float) -> None:
        if self._stopped:
            return
        end_s = floor_ms(capture_end_s)
        # Set the end frame before releasing the device so queued audio is cut there.
        self._end_frame = max(0, round((end_s - self._origin_s) * self.config.sample_rate))
        self._capture_end_s, self._stopped = end_s, True
        self._release_source()
        if self._threads:
            self._audio.put(_STOP)

    async def drain(self) -> None:
        if self._drained or self._closed or self._pipeline is None:
            self._shutdown()
            return
        if not self._stopped:
            await self.stop_capture(self._context.clock.now())
        try:
            if self._threads:
                await self._segmented.wait()
                await self._transcribed.wait()
            self._apply(self._pipeline.finish, self._capture_end_s)
            self._drained = True
        finally:
            # Also runs on cancellation by the controller's drain deadline.
            self._shutdown()

    # Device thread --------------------------------------------------------

    def _on_audio(self, samples: Sequence[float]) -> None:
        if self._abort.is_set() or self._stopped:
            return
        first = self._frames
        self._frames += len(samples)
        self._audio.put(("audio", first, array("f", samples)))

    def _on_device_error(self, error: MicrophoneError) -> None:
        if not self._stopped and not self._abort.is_set():
            self._audio.put(("lost", error, self._frames))

    # Voice-activity thread ------------------------------------------------

    def _segment_loop(self) -> None:
        sample_rate = self.config.sample_rate
        history, history_start, position = array("f"), 0, 0  # position: frames segmented
        seq = open_seq = open_start = last_partial = 0

        def at(frame: int) -> float:
            return floor_ms(self._origin_s + frame / sample_rate)

        def handle(boundaries: list[Boundary]) -> None:
            nonlocal seq, open_seq, open_start, last_partial
            for boundary in boundaries:
                if boundary.kind == "start" and not open_seq:
                    seq += 1
                    open_seq, open_start, last_partial = seq, boundary.frame, boundary.frame
                    self._post(self._speech_started, seq, at(boundary.frame))
                elif boundary.kind == "end" and open_seq:
                    end = max(boundary.frame, open_start)
                    audio = history[max(0, open_start - history_start):
                                    max(0, end - history_start)]
                    self._post(self._speech_ended, open_seq, at(end))
                    self._last_ended_seq = open_seq
                    self._jobs.put((open_seq, audio, True, at(end)))
                    open_seq = 0

        def stop_at(frame: int, availability: str, reason: str) -> None:
            handle(self.segmenter.flush(frame))
            self._fail(at(frame), availability, reason)

        try:
            while not self._abort.is_set():
                item = self._audio.get()
                if self._abort.is_set():
                    break
                if item[0] == "stop":
                    position = min(self._end_frame, position)
                    handle(self.segmenter.flush(position))
                    self._post(self._advance, at(position))
                    break
                if item[0] == "lost":
                    _, error, frame = item
                    position = min(frame, position)
                    stop_at(position, error.availability, error.reason)
                    break
                if self._transcription_failed:  # the outage begins where segmentation stops
                    stop_at(position, "error", "transcription_failed")
                    break
                _, first, samples = item
                if self._end_frame is not None:
                    samples = samples[:max(0, self._end_frame - first)]
                if not samples:
                    continue
                if self._audio.qsize() > self.max_backlog_chunks:
                    stop_at(position, "error", "audio_queue_overflow")
                    break
                boundaries = self.segmenter.process(samples, first)
                history.extend(samples)
                position = first + len(samples)
                handle(boundaries)
                if open_seq and position - open_start >= self._max_utterance_frames:
                    # Backstop for a segmenter that does not split long speech in time:
                    # bounded segments keep memory and the final transcription bounded.
                    handle([Boundary("end", position), Boundary("start", position)])
                if open_seq and self._partial_due(position - last_partial):
                    self._partial_pending, last_partial = True, position
                    self._jobs.put((open_seq, history[max(0, open_start - history_start):],
                                    False, at(position)))
                keep_from = open_start if open_seq else position - self.lookback_frames
                if keep_from - history_start > sample_rate:
                    del history[:keep_from - history_start]
                    history_start = keep_from
                self._post(self._advance, at(position))
        except Exception:
            if open_seq:  # finalize without words so no utterance stays open
                self._post(self._speech_ended, open_seq, at(max(position, open_start)))
                self._last_ended_seq = open_seq
                self._post(self._pipeline.finalized, open_seq, Transcription(""), False)
            self._fail(at(position), "error", "speech_segmentation_failed")
        finally:
            with self._failure_lock:
                self._segmented_until_s = at(position)
                failed = self._transcription_failed
            if failed:  # transcription failed after segmentation's last check
                self._fail(self._segmented_until_s, "error", "transcription_failed")
            self._jobs.put(_STOP)
            self._post(self._segmented.set)

    def _partial_due(self, frames_since_partial: int) -> bool:
        interval = self.config.partial_interval_s
        return (interval > 0 and not self._partial_pending
                and frames_since_partial >= interval * self.config.sample_rate)

    # Transcription thread -------------------------------------------------

    def _transcribe_loop(self) -> None:
        try:
            while not self._abort.is_set():
                job = self._jobs.get()
                if job is _STOP or self._abort.is_set():
                    break
                seq, audio, final, covered_end_s = job
                if not final:
                    self._partial_pending = False
                    if self._transcription_failed or seq <= self._last_ended_seq:
                        continue
                if self._transcription_failed:
                    self._post(self._pipeline.finalized, seq, Transcription(""), False)
                    continue
                try:
                    result = (self.transcriber.transcribe(audio, self.config.sample_rate, final)
                              if audio else Transcription(""))
                except Exception:
                    self._transcription_failure()
                    if final:  # retract any partial; overlapping windows report null
                        self._post(self._pipeline.finalized, seq, Transcription(""), False)
                    continue
                if final:
                    self._post(self._pipeline.finalized, seq, result)
                else:
                    self._post(self._partial, seq, result.text, covered_end_s)
        finally:
            self._post(self._transcribed.set)

    def _transcription_failure(self) -> None:
        """Stop transcribing. Segmentation reports the outage where it stops, so no
        utterance it already closed is finalized after the outage begins."""
        with self._failure_lock:
            self._transcription_failed = True
            segmented_until_s = self._segmented_until_s
        if segmented_until_s is not None:  # segmentation already finished
            self._fail(segmented_until_s, "error", "transcription_failed")

    # Event loop side ------------------------------------------------------

    def _post(self, function: Callable, *args) -> None:
        try:
            self._loop.call_soon_threadsafe(self._apply, function, *args)
        except RuntimeError:  # loop closed after the session ended
            pass

    def _apply(self, function: Callable, *args) -> None:
        if self._closed:
            return
        for event in function(*args) or ():
            try:
                self._context.emit(event)
            except Exception as error:  # a contract bug; keep the session alive
                self.errors.append(f"{event.get('event_id')}: {error}")

    def _clamp(self, at_s: float) -> float:
        """Never stamp ahead of the shared clock, or after capture end once stopped."""
        if self._capture_end_s is not None:
            return min(at_s, self._capture_end_s)
        return min(at_s, floor_ms(self._context.clock.now()))

    def _speech_started(self, seq: int, at_s: float) -> list[dict]:
        return self._pipeline.speech_started(seq, self._clamp(at_s))

    def _speech_ended(self, seq: int, at_s: float) -> list[dict]:
        return self._pipeline.speech_ended(seq, self._clamp(at_s))

    def _partial(self, seq: int, text: str, covered_end_s: float) -> list[dict]:
        return self._pipeline.partial(seq, text, self._clamp(covered_end_s))

    def _advance(self, at_s: float) -> list[dict]:
        self.analyzed_s = max(self.analyzed_s, self._clamp(at_s))
        return self._pipeline.advance(self.analyzed_s)

    def _fail(self, at_s: float, availability: str, reason: str) -> None:
        """Called from worker threads: stop capture and report non-available input."""
        self._release_source()
        self._post(self._enter_degraded, at_s, availability, reason)

    def _enter_degraded(self, at_s: float, availability: str, reason: str) -> None:
        if self._unavailable or self._closed:
            return
        self._unavailable = True
        self._apply(self._pipeline.unavailable, self._clamp(at_s), availability, reason)
        self._schedule_tick()

    def _schedule_tick(self) -> None:
        if not self._closed and self._capture_end_s is None:
            self._ticker = self._loop.call_later(self.idle_tick_s, self._tick)

    def _tick(self) -> None:
        """Without segmentation, keep emitting non-available windows on the clock."""
        if self._closed or self._capture_end_s is not None:
            return
        self._apply(self._pipeline.advance, floor_ms(self._context.clock.now()))
        self._schedule_tick()

    def _release_source(self) -> None:
        with self._source_lock:
            if not self._source_open:
                return
            self._source_open = False
            try:
                self.source.close()
            except Exception as error:  # the device is gone either way
                self.errors.append(f"microphone close failed: {error}")

    def _shutdown(self) -> None:
        self._closed = True
        self._abort.set()
        if self._ticker is not None:
            self._ticker.cancel()
        self._audio.put(_STOP)
        self._jobs.put(_STOP)
        self._release_source()
