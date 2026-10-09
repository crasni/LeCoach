# Spec Delta

## Purpose

Turn local speech and vision observations into simulated audience reactions. The reactions are deterministic, smoothed and evidence-cited, so the live audience and post-rehearsal coaching rely on the same explainable decisions. They never treat missing input as poor delivery.

## ADDED Requirements

### Requirement: Start every session neutral and isolated
On session start the engine SHALL discard all state from any previous session. It SHALL then emit one `NEUTRAL` audience state, with previous state `NEUTRAL`, no reasons, no usable sources, the current shared clock time, and an event ID unique within the session. Events from other sessions SHALL be ignored.

#### Scenario: First audience event
- **WHEN** a session starts
- **THEN** the first engagement event is `NEUTRAL` at the session clock's current time with empty reasons and usable sources

#### Scenario: Restart after a negative state
- **WHEN** a session ends while the audience is `CONFUSED` and a new session starts
- **THEN** the new session begins `NEUTRAL`, no earlier rule remains latched, and observations from the old session have no effect

### Requirement: Use only usable input sources
A source SHALL be usable only when its newest observation reports `available` and its capture window ended within that source's configured stale age. It must also have been captured after the source's latest `unavailable` or `error` status. Vision SHALL additionally require a detected person and pose.

#### Scenario: Camera outage
- **WHEN** a vision `signal.status` reports the camera unavailable after the latest vision observation
- **THEN** vision is excluded from usable sources and its rules stop contributing

#### Scenario: Recovery status without new observations
- **WHEN** a source reports `available` again after an outage but no observation captured after the outage has arrived
- **THEN** the source stays unusable, and its pre-outage observations are not used again

#### Scenario: Observations stop arriving
- **WHEN** no speech observation arrives within the speech stale age
- **THEN** speech is excluded from usable sources, and any speech rule it supported is released

### Requirement: Never let older observations overwrite newer ones
For each source, an observation whose capture window ends at or before the newest accepted observation SHALL be ignored. Late observations SHALL NOT revise reactions already shown.

#### Scenario: Late calmer observation
- **WHEN** a slow-pace observation captured earlier than the newest fast-pace observation arrives late
- **THEN** the audience state is unchanged

### Requirement: Ignore observations that are stale on arrival
An observation whose capture window ended longer ago than its source's stale age when it arrives SHALL be ignored. It SHALL be neither used for decisions nor cited as evidence.

#### Scenario: Very late observation
- **WHEN** a fast-pace observation whose window ended longer ago than the speech stale age arrives just before a fresh fast-pace observation whose window starts within the window gap of it
- **THEN** the late observation neither extends the sustained run nor appears in any reason

### Requirement: Latch negative rules only on sustained evidence
A pace, filler or facing rule SHALL latch only when consecutive triggering observations cover at least that rule's sustain duration. Consecutive means separated by no more than the configured window gap and not interrupted by an outage. The silence rule SHALL latch when a reported active pause reaches the configured duration.

#### Scenario: Brief facing away
- **WHEN** facing stays below the facing-away threshold for less than the sustain duration
- **THEN** no facing rule latches and the audience does not become `BORED` from it

#### Scenario: Sustained fast pace
- **WHEN** consecutive speech windows at or above the high-pace threshold cover the pace sustain duration
- **THEN** the `pace_high` rule latches

#### Scenario: Run interrupted by an outage
- **WHEN** facing-away windows before a camera outage and one facing-away window after it together cover the sustain duration
- **THEN** no facing rule latches, because the run restarts after the outage

#### Scenario: Prolonged silence after speech
- **WHEN** after speech, the speech producer reports an active pause that reaches the prolonged-silence duration
- **THEN** the `silence_prolonged` rule latches

### Requirement: Hold pace and filler rules while the speaker is pausing
While a speech observation reports an active pause at least the configured pause-hold duration long, pace and filler rules SHALL neither latch nor release. That observation SHALL give no positive or negative pace verdict, because the trailing window is filling with silence.

#### Scenario: Speaker stops after fast speech
- **WHEN** `pace_high` is latched and trailing windows with a growing active pause report falling WPM inside the comfortable band
- **THEN** the audience does not become `INTERESTED`, `pace_high` stays latched, and the audience becomes `BORED` when the pause reaches the prolonged-silence duration

#### Scenario: Pausing with no rule latched
- **WHEN** speech is the only source and its window reports a holding pause with a pace inside the comfortable band
- **THEN** the audience does not become `INTERESTED`

#### Scenario: Facing carries a pause
- **WHEN** speech reports a holding pause while facing stays in its positive band
- **THEN** the evaluation stays positive from facing alone and can reach `ENGAGED`, citing only `facing_audience`

#### Scenario: Completed pause
- **WHEN** a speech window reports a completed pause and a pace inside the comfortable band
- **THEN** the pace counts as positive evidence

### Requirement: Map negative rules to audience states
`pace_high` and `fillers_frequent` SHALL indicate `CONFUSED`. `pace_low`, `silence_prolonged` and `facing_away_sustained` SHALL indicate `BORED`. While any negative rule is latched, the most recently latched rule SHALL determine the state, and every latched rule SHALL be cited as a reason.

#### Scenario: Two simultaneous issues
- **WHEN** `pace_high` is latched and `facing_away_sustained` latches later
- **THEN** the audience becomes `BORED` and cites both `pace_high` and `facing_away_sustained`

### Requirement: Release negative rules with hysteresis
A latched rule SHALL be released only when its newest observation crosses that rule's separate clear threshold, or when the observation becomes unknown or its source unusable. Values between the trigger and clear thresholds SHALL keep the rule latched.

#### Scenario: Pace between thresholds
- **WHEN** `pace_high` is latched and pace drops below the trigger but stays above the clear threshold
- **THEN** the rule stays latched and the audience stays `CONFUSED`

#### Scenario: Pace returns to the comfortable band
- **WHEN** a speech window without an active pause reports pace at or below the high-pace clear threshold
- **THEN** `pace_high` is released

### Requirement: Never treat unknown input as negative evidence
Null metrics, unknown pauses, absent persons or poses, outages and low activity SHALL NOT trigger any rule. Zero WPM SHALL be left to the silence rule rather than the slow-pace rule. Only pauses the speech producer reports as active SHALL count as silence. Under the speech contract, silence before the first speech is not a pause.

#### Scenario: Silence before the speaker starts
- **WHEN** speech capture works but the speaker has not started speaking
- **THEN** no negative audience state results

#### Scenario: Person leaves the frame
- **WHEN** vision reports no detected person for longer than the facing sustain duration
- **THEN** no facing rule latches

#### Scenario: Unsupported analysis language
- **WHEN** speech observations report null WPM and filler values
- **THEN** no pace or filler rule latches

### Requirement: Recognize positive delivery
With no negative rule latched, an evaluation SHALL be positive when every usable source with a verdict is in its positive band, and at least one is. Speech is in band with pace between the two clear thresholds and fillers at or below their clear rate. Vision is in band with facing at or above the facing-toward threshold. Null or zero WPM, or a holding pause, gives speech no verdict.

#### Scenario: Delivery improves after a negative state
- **WHEN** a negative rule releases and pace and facing are both in their positive bands
- **THEN** the audience becomes `INTERESTED`

#### Scenario: One source out of band
- **WHEN** facing is in its positive band but pace is above the high-pace clear threshold
- **THEN** the evaluation is not positive

### Requirement: Cite one positive reason per source in band
Each `INTERESTED` or `ENGAGED` transition SHALL cite `pace_steady` for speech and `facing_audience` for vision, each only when that usable source's newest observation is in its positive band. A source without a verdict SHALL contribute no reason.

#### Scenario: Camera unavailable
- **WHEN** only speech is usable and its pace is in the positive band
- **THEN** the positive transition cites only `pace_steady`

### Requirement: Require uninterrupted positive evidence for ENGAGED
The audience SHALL become `ENGAGED` from `INTERESTED` only after every evaluation for the configured engaged duration has been positive. Any evaluation that is not positive SHALL restart that duration.

#### Scenario: Sustained good delivery
- **WHEN** every evaluation has been positive for the engaged duration while the audience is `INTERESTED`
- **THEN** the audience becomes `ENGAGED`

#### Scenario: Intermittent good delivery
- **WHEN** positive and mixed evaluations alternate
- **THEN** the audience never becomes `ENGAGED`

### Requirement: Return to NEUTRAL without inventing reactions
With no usable source, the audience SHALL return to `NEUTRAL` immediately, with no reasons and no usable sources. With usable sources but neither a latched negative rule nor a positive evaluation, it SHALL return to `NEUTRAL` with no reasons after the configured neutral duration.

#### Scenario: Every input lost
- **WHEN** both sources become unusable while the audience is `CONFUSED`
- **THEN** the audience becomes `NEUTRAL` with empty reasons and usable sources at the next evaluation

#### Scenario: Mixed observations
- **WHEN** no rule is latched but one usable source is outside its positive band for the neutral duration
- **THEN** the audience returns to `NEUTRAL` without reasons

### Requirement: Hold each reaction for a minimum dwell
Apart from the no-usable-input reset, the audience SHALL NOT change state again until the current state has been shown for the configured minimum dwell. Rapid metric jitter SHALL NOT make the audience flicker.

#### Scenario: Metrics alternating across thresholds
- **WHEN** pace and facing alternate between triggering and positive values every second for one minute
- **THEN** no negative state latches, the audience never becomes `ENGAGED`, and no two transitions are closer than the minimum dwell

### Requirement: Emit timestamped transitions
Each transition SHALL use the shared clock time of the decision, name the previous state, and list the usable sources. No state SHALL be emitted when unchanged.

#### Scenario: Unchanged state
- **WHEN** a new observation keeps the audience in its current state
- **THEN** no engagement event is emitted

### Requirement: Cite the observations that latched or sustain each rule
Each reason SHALL cite one or more, and at most the configured number of, speech or vision event IDs captured no later than the decision. A negative reason SHALL cite the run that latched its rule, plus later observations that still meet its trigger. A positive reason SHALL cite the current positive run. Observations inside a hysteresis band SHALL NOT be cited.

#### Scenario: Reason evidence
- **WHEN** the audience becomes `CONFUSED` because of `pace_high`
- **THEN** the reason cites speech metric event IDs whose capture times are no later than the transition timestamp

#### Scenario: Held rule cited again later
- **WHEN** `pace_high` is held by observations between its trigger and clear thresholds, and a facing rule later changes the state
- **THEN** the `pace_high` reason cites only observations at or above the high-pace trigger, even if they are older than the speech stale age

### Requirement: Behave deterministically and without models
For the same event stream, delivery timing and configuration, the engine SHALL produce identical transitions. No model, LLM or remote service SHALL participate in audience decisions.

#### Scenario: Repeated replay
- **WHEN** the same synthetic case is replayed twice with the same configuration
- **THEN** both runs emit identical engagement events

### Requirement: Re-evaluate periodically during live sessions
In live mode the engine SHALL re-evaluate on the configured interval, so stale input is released without waiting for a new event.

#### Scenario: Speech-only input stalls
- **WHEN** speech is the only usable source and stops arriving during a live session while the audience is `CONFUSED`
- **THEN** a later periodic evaluation returns the audience to `NEUTRAL` without a new input event

### Requirement: Emit nothing after stop
After the engine is stopped, it SHALL emit no further engagement events in either replay or live mode, whether observations or periodic evaluations follow.

#### Scenario: Stopped engine
- **WHEN** the engine is stopped and observations or ticks would follow
- **THEN** no further engagement events are emitted

### Requirement: Keep rule defaults in one validated configuration
All thresholds, durations, stale ages, dwell times, evidence limits and the per-source history bound SHALL be declared with their units in one configuration. Inverted pace, filler or facing thresholds, and a pause hold longer than the prolonged-silence duration, SHALL be rejected. Defaults SHALL be documented as demo heuristics, not validated measures.

#### Scenario: Inverted thresholds
- **WHEN** a configuration sets the high-pace trigger below its clear threshold, the filler clear rate at or above its trigger, or the facing-away threshold above the facing-toward threshold
- **THEN** the configuration is rejected

### Requirement: Expose the per-source stale ages to consumers
The engine's per-source stale ages SHALL be readable from its configuration. Downstream consumers, such as coaching, can then apply the same freshness limits the engine applied.

#### Scenario: Coaching composition
- **WHEN** a consumer is composed with the engine's configuration
- **THEN** it reads the speech and vision stale ages from that configuration rather than defining its own
