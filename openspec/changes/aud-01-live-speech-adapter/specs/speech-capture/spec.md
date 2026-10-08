# Spec Delta

## Purpose

Turn the rehearsal microphone into a local, timestamped speech input that starts, fails, and stops predictably within the shared session lifecycle, so missing audio is reported honestly instead of becoming poor-delivery evidence.

## ADDED Requirements

### Requirement: Start capture within the startup bound
Starting the speech adapter SHALL open the microphone and begin capture within the session startup bound. It SHALL NOT download or load transcription models during start. If transcription resources are not ready, start SHALL report speech as unavailable instead of waiting past the bound.

#### Scenario: Prepared model and microphone
- **WHEN** a live session starts with a loaded transcription model and an available microphone
- **THEN** speech capture begins before the startup bound expires and no model download occurs during start

#### Scenario: Model not ready
- **WHEN** a live session starts before transcription resources are loaded
- **THEN** speech reports an unavailable or error status with a model-related reason and the session remains usable for other inputs

### Requirement: Stamp observations with capture time
Every speech observation SHALL carry timestamps derived from audio sample positions mapped onto the shared session clock at capture start. Timestamps SHALL NOT use inference completion time or an independent zero point.

#### Scenario: Delayed transcription
- **WHEN** an utterance that ended at capture time 12.4 s is transcribed 2 s later
- **THEN** its final transcript and any window counting its words use capture times, ending at 12.4 s

### Requirement: Report unavailable speech input explicitly
The adapter SHALL report microphone permission denial, a missing or disconnected device, and transcription failure as a speech `signal.status` with availability `unavailable` or `error` and a specific reason. Later windows SHALL report that availability with null measurements and an unknown pause.

#### Scenario: Permission denied at start
- **WHEN** microphone access is denied when the session starts
- **THEN** a speech status reports the denial and subsequent speech windows contain no numeric WPM, filler, or pause values

#### Scenario: Device lost mid-utterance
- **WHEN** the microphone disconnects while the speaker is talking
- **THEN** the interrupted utterance is finalized at the disconnect capture time, an error status is reported, and later windows report the error with null measurements

### Requirement: Stop acquisition and drain within the session bound
Stopping SHALL end acquisition at the supplied capture end. Draining SHALL finalize speech captured at or before capture end and emit a final metrics window, within the shared stop/drain bound. No observation after capture end, or after session completion, SHALL be emitted.

#### Scenario: Speaking when the session stops
- **WHEN** the session stops while an utterance is in progress
- **THEN** the utterance is finalized with an end time no later than capture end and a final window ending at capture end is emitted during drain

#### Scenario: Transcription exceeds the drain bound
- **WHEN** finalizing pending speech takes longer than the remaining stop/drain bound
- **THEN** draining stops without emitting late observations, so the controller can list speech as incomplete

### Requirement: Release capture resources
The microphone and transcription workers SHALL be released after stop, start failure, drain timeout, and cancellation. Repeated stop or drain calls SHALL be safe and SHALL NOT reopen capture or duplicate observations.

#### Scenario: Repeated stop and cancellation
- **WHEN** stop or drain is called again, or drain is cancelled by the controller's deadline
- **THEN** the microphone is released once, capture does not restart, and no observation is emitted twice

### Requirement: Process speech locally without persistence
Audio capture, voice activity detection, transcription, and metric computation SHALL run on the local machine without remote inference services. Raw audio and transcripts SHALL NOT be written to persistent storage by default.

#### Scenario: Offline rehearsal
- **WHEN** a rehearsal runs with the transcription model already present locally and no network connection
- **THEN** speech observations are produced and no audio or transcript file is created by the adapter
