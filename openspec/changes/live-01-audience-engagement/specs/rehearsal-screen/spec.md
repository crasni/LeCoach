# Spec Delta

## Purpose

Give the speaker a rehearsal screen where a simulated audience visibly reacts to delivery. Each reaction is explained in plain language, and input availability and data provenance stay honest. The screen does not distract from presenting.

## ADDED Requirements

### Requirement: Render only the engine's audience decisions
The screen SHALL derive the audience state solely from received `engagement.state` events and snapshots. It SHALL NOT compute audience rules of its own. Before any engagement event arrives, the audience SHALL appear `NEUTRAL`.

#### Scenario: Engine transition received
- **WHEN** an `engagement.state` event for the active session reports `BORED`
- **THEN** the displayed state becomes `BORED` with its plain-language label

#### Scenario: Event from another session
- **WHEN** an event for a session other than the active one is received
- **THEN** the displayed audience, inputs and transcript are unchanged

### Requirement: Show a visible but calm audience reaction
The audience SHALL be shown as several simple 2D listeners whose pose and expression differ per state. Listeners SHALL adopt a new state one after another rather than all at once. During negative states some listeners SHALL stay neutral. Continuous motion SHALL stop when the viewer prefers reduced motion.

#### Scenario: State change ripple
- **WHEN** the audience changes from `NEUTRAL` to `CONFUSED`
- **THEN** listeners update in sequence and not every listener shows confusion

#### Scenario: Reduced motion preference
- **WHEN** the browser reports a reduced-motion preference
- **THEN** nodding, floating and pose-transition animations are disabled

### Requirement: Explain the current reaction in plain language
The screen SHALL describe each reason the current state cites in plain language. If no reason applies and no input is currently available during a running session, it SHALL say it is waiting for usable speech or camera input. It SHALL state that reactions are simulated from rules, not measured emotions or judgments.

#### Scenario: Negative reaction with reasons
- **WHEN** the current state cites `pace_high` and `facing_away_sustained`
- **THEN** the screen shows that pace has stayed fast and that the speaker turned away from the audience for a while

#### Scenario: No usable input
- **WHEN** a running session has no input source currently available
- **THEN** the screen says it is waiting for usable speech or camera input instead of showing a delivery reason

#### Scenario: Input arrives without a new transition
- **WHEN** speech becomes available while the audience stays `NEUTRAL`
- **THEN** the waiting message is replaced by the neutral description

### Requirement: Show the audience timeline
The screen SHALL list every audience transition it received for the active session, in order, each with its time, plain-language state label and reasons. It SHALL draw a bar whose segment widths are proportional to the time spent in each state. Duplicate deliveries and reconnection snapshots SHALL NOT duplicate entries.

#### Scenario: Completed weak-to-improved replay
- **WHEN** the `weak_to_improved` replay completes
- **THEN** the timeline lists the confused, bored, recovering and engaged transitions with their reasons

#### Scenario: Reconnection
- **WHEN** the event connection is interrupted and restored during a session
- **THEN** the timeline keeps one entry per received transition

### Requirement: Show input status in plain language
The screen SHALL show microphone and camera status in plain language, including the adapters' documented status reasons. Each source's status SHALL follow its newest status or metrics event by capture time, with a status event winning a tie. A later unavailable metrics window SHALL keep the status's specific reason.

#### Scenario: Missing pose runtime
- **WHEN** the camera reports `pose_runtime_missing`
- **THEN** the camera status says the pose software is not installed

#### Scenario: Late observation after an outage
- **WHEN** a speech metrics event captured before a newer microphone outage arrives late
- **THEN** the microphone status still shows the outage

#### Scenario: Unavailable windows after an outage
- **WHEN** the microphone reports a disconnection and later speech windows report it unavailable
- **THEN** the status keeps saying the microphone is disconnected

### Requirement: Never show stale or unknown values as current
The screen SHALL show pace, filler rate, approximate facing and an active pause only from an available observation captured after that source's latest status event. Otherwise, and for unknown values, it SHALL show them as unavailable, never as zero or a pre-outage value.

#### Scenario: Microphone drops mid-session
- **WHEN** the microphone reports an error after speech metrics showed a pace
- **THEN** the pace is shown as unavailable instead of the last value

#### Scenario: Recovery status before new observations
- **WHEN** the microphone reports available again after an outage but no new speech window has arrived
- **THEN** the pace stays unavailable until a window captured after the recovery arrives

#### Scenario: Unknown pace
- **WHEN** the latest speech metrics report null WPM
- **THEN** pace is shown as unavailable rather than 0 WPM

### Requirement: Show the live transcript with revisions
The screen SHALL show utterances in capture order, including when they arrive out of order. A newer revision of an utterance SHALL replace its partial text until the final arrives, and nothing SHALL change the utterance after its final. Partial text SHALL be visually distinguishable from final text.

#### Scenario: Delayed final and duplicates
- **WHEN** a partial, a late final and a duplicate final for one utterance arrive
- **THEN** the transcript shows the final text once

#### Scenario: Utterances out of order
- **WHEN** a later utterance arrives before an earlier one
- **THEN** the transcript reads in capture order

### Requirement: Label mode and provenance
In synthetic replay the screen SHALL state that the observations are authored examples, that the audience is computed by the engine, that the coaching is an authored example, and that the microphone and camera are off. The live option SHALL be unavailable while the backend reports live input as not integrated.

#### Scenario: Default replay
- **WHEN** a synthetic example is started
- **THEN** the synthetic replay label and the authored-coaching label are visible

#### Scenario: Live not integrated
- **WHEN** the backend health reports live input as not integrated
- **THEN** the live option is shown as not connected yet and cannot be selected

### Requirement: Show the camera preview from the backend
While a live session runs and the camera is available, the screen SHALL display the backend's preview stream once a frame arrives and SHALL NOT open its own camera stream. Otherwise it SHALL show a plain message, retrying periodically while the camera is available. It SHALL state that no video is recorded.

#### Scenario: Camera still opening
- **WHEN** the first preview request fails because the camera is still starting
- **THEN** the screen shows that the preview is unavailable without an empty preview box, then retries and displays the preview once frames exist

#### Scenario: Camera fails mid-session
- **WHEN** the camera reports an error while its preview is shown
- **THEN** the preview is removed and the screen says it is unavailable, instead of showing a frozen frame

### Requirement: Present the post-rehearsal summary
When feedback is ready, the screen SHALL show each moment with its time, kind, observation and suggestion, plus any limitations. With no moments, it SHALL say none are supported. A replay stopped early SHALL show that the authored summary is unavailable.

#### Scenario: Stop early in replay
- **WHEN** a synthetic replay is stopped before it completes
- **THEN** the screen says the authored example summary is unavailable

### Requirement: Fit narrow screens
The rehearsal screen SHALL remain usable at a 390-pixel viewport width without horizontal page scrolling.

#### Scenario: Phone-width layout
- **WHEN** the screen is displayed 390 pixels wide
- **THEN** the page has no horizontal scroll and the audience, controls and timeline remain visible
