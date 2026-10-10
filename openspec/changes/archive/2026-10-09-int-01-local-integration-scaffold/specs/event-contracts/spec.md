# Spec Delta

## Purpose

Give independent producers and consumers compatible, validated rehearsal data and evidence references. Field meanings, units, and event shapes remain defined by [ARCHITECTURE.md](../../../../../../docs/ARCHITECTURE.md).

## ADDED Requirements

### Requirement: Validate canonical events
The system SHALL validate every accepted event against the v0 contracts defined in ARCHITECTURE, including identity, source/type compatibility, finite values, capture windows, and explicit unknown values.

#### Scenario: Compatible preparation data
- **WHEN** the reviewed synthetic events are validated
- **THEN** their existing v0 envelopes and payloads are accepted without rewriting their fields

#### Scenario: Invalid observations
- **WHEN** an event contains nonfinite time, mismatched source/type, an invalid window, or a derived vision score without usable person/pose observations
- **THEN** validation rejects it instead of turning unavailable evidence into a numeric score

### Requirement: Validate completed sessions
The system SHALL validate completed-session identity, lifecycle boundaries, duration, unique event IDs, and stable capture-time ordering before passing a completed session to coaching.

#### Scenario: Invalid completed timeline
- **WHEN** a completed timeline includes a foreign session, duplicate ID, observation after capture end, or inconsistent lifecycle duration
- **THEN** validation rejects the timeline

#### Scenario: Equal capture timestamps
- **WHEN** accepted completed events share a capture timestamp
- **THEN** their order uses event ID as the stable tie-breaker

### Requirement: Validate feedback evidence
The system SHALL validate feedback identity, moment bounds, moment count limits, and supporting event references before serving computed feedback. Lifecycle and input-status events SHALL NOT qualify as coaching evidence.

#### Scenario: Unsupported moment
- **WHEN** computed feedback references missing events, another session, only lifecycle/status evidence, or a moment outside the rehearsal
- **THEN** it is rejected and is not served as valid coaching

### Requirement: Keep frontend types aligned
The frontend contract types SHALL be generated from the same exported schema as the backend models, and a reproducible check SHALL detect stale generated schema or types.

#### Scenario: Contract drift
- **WHEN** a backend contract changes without regenerating its exported schema or frontend types
- **THEN** the parity checks report the mismatch
