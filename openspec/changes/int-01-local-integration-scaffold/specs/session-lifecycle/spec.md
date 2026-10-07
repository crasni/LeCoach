# Spec Delta

## Purpose

Let independently implemented rehearsal components share one session identity and capture clock, with predictable startup, routing, and shutdown. [ARCHITECTURE.md](../../../../../docs/ARCHITECTURE.md#session-lifecycle) defines the shared lifecycle contract.

## ADDED Requirements

### Requirement: Prepare before capture
Preparing a session SHALL allocate its identity without starting capture. Starting SHALL attach consumers before producers, use one shared monotonic clock, and emit the start boundary at capture time zero. Repeated start requests SHALL NOT reopen capture.

#### Scenario: Prepared session and retry
- **WHEN** a prepared session is started and the start request is retried
- **THEN** capture starts once, after consumers are attached, using the same session identity and clock

### Requirement: Route supporting evidence before resulting reactions
Event delivery SHALL preserve arrival order for subscribers. Events emitted during a subscriber callback SHALL reach subscribers after the supporting event finishes delivery.

#### Scenario: Reaction emitted during metric handling
- **WHEN** a consumer emits an audience transition while handling a speech metric
- **THEN** every subscriber receives the speech metric before that resulting transition

### Requirement: Isolate sessions and deduplicate retries
The system SHALL reject foreign-session events, conflicting retries of stable event IDs, and callbacks after completion. Replacing a completed session SHALL clear its retained transport/display state and make the old session unavailable through the active-session API.

#### Scenario: Foreign and repeated events
- **WHEN** an adapter emits another session's event or retries an identical accepted event
- **THEN** neither emission adds another observation to the current session

#### Scenario: Consecutive sessions
- **WHEN** a new session replaces a completed one and an old callback arrives
- **THEN** the new session's transcript, input status, and audience state remain isolated from the old session

### Requirement: Handle producer startup failures independently
Producer startup SHALL have a configurable deadline and cleanup. Failure of one producer SHALL expose its unavailable/error status while allowing another usable producer to continue.

#### Scenario: Camera fails while speech starts
- **WHEN** vision startup fails or exceeds its deadline while speech initializes successfully
- **THEN** the session reports the vision failure and remains usable for speech

### Requirement: Stop capture before bounded draining
Stopping SHALL freeze capture end, stop live reactions, stop acquisition before draining producers, and emit completion after drain or timeout. Stop/drain SHALL share a configurable bounded deadline. Timed-out sources SHALL be listed as incomplete; repeated stops SHALL NOT duplicate lifecycle boundaries.

#### Scenario: Pending final transcript
- **WHEN** stopping flushes a final transcript captured before capture end
- **THEN** it can reach the recorder before completion without changing reactions already displayed

#### Scenario: Drain timeout and repeated stop
- **WHEN** a producer exceeds the stop/drain deadline and stop is retried
- **THEN** cleanup completes, the source is listed as incomplete, and the completed boundary appears once at capture end

### Requirement: Preserve newer display observations
Older delivered observations SHALL NOT overwrite newer input/display state. A final transcript revision SHALL freeze that utterance's display against older or partial revisions.

#### Scenario: Late observations
- **WHEN** an older metric/status or partial transcript arrives after a newer metric or final transcript
- **THEN** the newer display state is retained while eligible evidence can still reach the recorder before completion

### Requirement: Bound consumer failures
Consumer failure SHALL trigger session cleanup. Computed completion/feedback SHALL be validated and feedback generation SHALL have a configurable timeout; failure SHALL surface an explicit error/unavailable result.

#### Scenario: Invalid or stalled feedback
- **WHEN** a generator returns mismatched evidence or exceeds its deadline
- **THEN** the API does not expose that result as valid completed coaching
