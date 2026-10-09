# Spec Delta

## Purpose

Produce canonical transcript revisions and approximate pace, filler, and pause observations from local transcription. Audience and coaching consumers can then rely on them without stitching model output or mistaking unknown values for poor delivery.

## ADDED Requirements

### Requirement: Publish one canonical utterance per speech segment
Each voice-activity segment SHALL be published as one utterance. Partial revisions SHALL increase monotonically, and a single final revision SHALL freeze the utterance and carry its capture start and end. Finals SHALL NOT overlap; overlapping audio chunks SHALL be reconciled before publication.

#### Scenario: Partial corrected by its final
- **WHEN** a partial revision contains a misrecognized word that the final transcription corrects
- **THEN** the final replaces the partial and no later revision of that utterance is published

#### Scenario: Overlapping transcription chunks
- **WHEN** consecutive transcription chunks cover overlapping audio
- **THEN** the published finals do not overlap in capture time and no word is published in two finals

### Requirement: Retract non-speech segments
A segment whose transcription is empty or rejected as non-speech SHALL be finalized with empty text, so any displayed partial is retracted. It SHALL contribute no words or fillers.

#### Scenario: Hallucinated partial on noise
- **WHEN** a cough triggers voice activity and a partial shows text that the final transcription rejects
- **THEN** the utterance is finalized with empty text and no metric counts its words

### Requirement: Count finalized words only
WPM and filler counts SHALL count finalized words only, attributed to windows by word capture time. The denominator SHALL be the window duration including silence. Filler rate SHALL equal the filler count per window minute. Retried or duplicate finals SHALL NOT be counted twice.

#### Scenario: Partial text and retries
- **WHEN** partial revisions and an identical retried final are published for an utterance inside a window
- **THEN** the window counts that utterance's finalized words and fillers exactly once

### Requirement: Report unknown measurements as null
WPM and filler fields SHALL be null for windows shorter than the configured minimum observation, windows whose overlapping speech is not finalized within the configured coverage wait, unsupported analysis languages, and unavailable input. A zero SHALL mean analyzed silence.

#### Scenario: Analyzed silence
- **WHEN** capture works and nobody speaks during a full window
- **THEN** the window reports zero WPM and zero fillers rather than null

#### Scenario: Unsupported language
- **WHEN** the speaker uses a language outside the configured analysis language
- **THEN** transcripts and pauses are still published while WPM and filler fields are null

#### Scenario: Transcription falls behind
- **WHEN** finals for speech overlapping a window are not available within the configured coverage wait
- **THEN** that window reports null WPM and filler values instead of an undercount

### Requirement: Emit windows without waiting for unfinished speech
Periodic metrics SHALL cover a trailing configured window at the configured hop. If an utterance is still in progress at the hop time, the window SHALL end where that utterance began. A window that would not advance past the previous one SHALL be skipped. A final window SHALL be emitted at capture end.

#### Scenario: Speaking at the hop time
- **WHEN** a periodic window is due while the speaker is mid-utterance
- **THEN** the window ends at that utterance's capture start and counts only speech finalized before it

### Requirement: Report pauses after speech begins
Silence of at least the configured pause minimum after the first speech SHALL be reported as an active pause with elapsed duration while it continues. When speech resumes, it SHALL be reported exactly once as a completed pause, in a window ending at the resume time. Silence before the first speech SHALL NOT be a pause.

#### Scenario: Prolonged silence
- **WHEN** the speaker stops for 10 s and then resumes
- **THEN** windows during the silence report an active pause with growing duration and one window reports the completed pause when speech resumes

#### Scenario: Leading silence
- **WHEN** the session starts and the speaker has not yet spoken
- **THEN** windows report no pause and, once long enough, zero WPM

### Requirement: Take analysis parameters from one speech configuration
Analysis language, window, hop, minimum observation, pause minimum, coverage wait, and maximum utterance length SHALL come from one speech configuration with documented defaults. Measurements SHALL follow the supplied values; changing a value SHALL NOT require code changes.

#### Scenario: Agreed defaults change
- **WHEN** the team changes the pause minimum from 1.0 s to 1.5 s in the speech configuration
- **THEN** pauses shorter than 1.5 s are no longer reported, without modifying adapter code

### Requirement: Satisfy shared contracts and producer checks
Every emitted speech event SHALL validate against the executable v0 event contracts. A recorded stream of speech and lifecycle events SHALL pass the shared speech producer checks when run with the configured minimum observation and pause minimum.

#### Scenario: Recorded rehearsal check
- **WHEN** a recorded live speech stream is checked with the shared speech checker using the configured values
- **THEN** it reports no violations
