# synthetic-replay Specification

## Purpose

Let subsystem owners exercise shared contracts and lifecycle without devices or models, using reproducible synthetic inputs. [STATUS.md](../../../docs/STATUS.md#int-01-local-scaffold-validation) records the fixture provenance and validation evidence.

## Requirements

### Requirement: Preserve fixture delivery semantics
Headless acceptance replay SHALL preserve fixture event IDs, capture timestamps, and delivery order, including late observations. Its fake clock SHALL never move backward. Explicit test delivery schedules SHALL NOT rewrite capture timestamps.

#### Scenario: Late final transcript
- **WHEN** a final transcript is delivered after a newer capture-time event
- **THEN** replay preserves its earlier capture timestamp and dispatches it at its original delivery position

#### Scenario: Delayed delivery schedule
- **WHEN** a test delays an event beyond its capture timestamp
- **THEN** delivery follows the schedule and the shared fake clock remains monotonic

### Requirement: Reuse reviewed cases reproducibly
Replay SHALL reuse the reviewed preparation cases without editing their original contents and SHALL produce identical traces and authored outputs for identical headless input. Only enumerated fixture names SHALL be loadable.

#### Scenario: Repeat acceptance replay
- **WHEN** the same synthetic case is replayed twice
- **THEN** its delivered trace and authored outputs match

#### Scenario: Invalid fixture name
- **WHEN** a caller supplies an unknown name or file path
- **THEN** replay rejects it rather than loading an arbitrary file

### Requirement: Separate authored and computed consumers
Default complete-stream replay SHALL identify audience transitions and feedback as authored. An injected engagement implementation SHALL replace authored reactions, and injected recorder/generator outputs SHALL be validated through the shared contracts. Replay SHALL NOT add a competing production logger or coaching selector.

#### Scenario: Authored example
- **WHEN** a fixture runs without real consumers
- **THEN** the output is identified as an authored example and does not establish algorithm or live-inference correctness

#### Scenario: Injected engagement consumer
- **WHEN** the same producer inputs run through an injected engagement implementation
- **THEN** authored fixture transitions are suppressed so only that implementation determines audience output

### Requirement: Keep replay model-free and local
Core installation and synthetic replay SHALL require no model download or microphone/camera access. Default replay SHALL persist no rehearsal data; explicit development exports SHALL follow the documented ignored-session location.

#### Scenario: Core-only rehearsal
- **WHEN** the locked core environment runs the documented replay command
- **THEN** it produces synthetic output without initializing capture or inference and without an automatic session export

### Requirement: Provide a consumable handoff
The repository SHALL provide locked backend/frontend setup, a headless replay command, a public subscription example, and reproducible contract/lifecycle/transport checks. Subsystems SHALL be consumable through shared boundaries without importing another subsystem's implementation internals.

#### Scenario: Isolated working-tree setup
- **WHEN** a fresh working-tree copy follows the documented setup with the tested dependency caches available
- **THEN** core checks, schema/type parity, frontend build, and the subscription example pass without devices or models
