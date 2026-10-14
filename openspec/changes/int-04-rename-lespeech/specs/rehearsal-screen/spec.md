# Spec Delta

## ADDED Requirements

### Requirement: Name audience states in everyday words
The screen SHALL label the audience states with everyday words a first-time viewer understands without explanation: `ENGAGED` as Engaged, `INTERESTED` as Interested, `NEUTRAL` as Listening, `CONFUSED` as Confused and `BORED` as Bored. Reason phrases and coaching sentences SHALL use short, plain sentences.

#### Scenario: Confused audience
- **WHEN** an `engagement.state` event reports `CONFUSED`
- **THEN** the displayed label reads "Confused"
