# Spec Delta

## Purpose

Make LeCoach's hardware readiness and inference performance claims reproducible, with clear separation between intended accelerator support and execution observed on an identified host/device.

## ADDED Requirements

### Requirement: Identify each evidence mode
Every evidence record SHALL identify its source revision, observation date, host, input mode, inference backend, and observed versus untested scope. Synthetic fixtures, live CPU processing, vendor references, and measured UGen300 execution SHALL remain distinguishable. A replay check SHALL NOT establish capture, inference, or hardware performance.

#### Scenario: Synthetic validation recorded
- **WHEN** fixture checks or authored replay are run
- **THEN** the record labels the inputs and outputs as synthetic/authored and excludes live capture, model accuracy, and accelerator performance claims

#### Scenario: CPU rehearsal recorded
- **WHEN** real microphone/camera input is processed locally on the host CPU
- **THEN** the record identifies that live CPU path and does not claim UGen300 execution

### Requirement: Preserve an explicit readiness outcome
The hardware record SHALL report observed device/runtime availability and the commands used to inspect it. An absent device or incompatible runtime/model SHALL produce a dated limitation and next action. A maintainer-confirmed team availability constraint SHALL be distinguished from
host inspection. Missing UGen300 SHALL NOT stop Stage I implementation or local CPU
validation; target inference SHALL remain unverified until measured in Stage II.

#### Scenario: Target device absent
- **WHEN** host inspection finds no identifiable UGen300
- **THEN** the record names the inspected host, states target execution is unverified, and permits Stage I implementation and actual local CPU validation to continue without a fabricated accelerator measurement

#### Scenario: Device present but inference cannot start
- **WHEN** driver, firmware, runtime, model, or host compatibility prevents execution
- **THEN** the record captures the failed prerequisite and next action without presenting device detection as successful LeCoach inference

### Requirement: Ground adapter compatibility in official evidence
The hardware record SHALL cite official model/runtime references and pin inspected revisions. Before reporting target execution, it SHALL identify the actual device/interface, driver, firmware, runtime, model version/hash, preprocessing, and postprocessing used. Advertised model availability and non-USB benchmark conditions SHALL NOT substitute for validated USB compatibility.

#### Scenario: Candidate adapter documented
- **WHEN** official sources list a suitable speech or pose model
- **THEN** the candidate remains untested until its actual runtime, data processing, host/interface path, and application integration are verified

### Requirement: Measure delay with defined clocks and samples
Performance records SHALL state exact commands/configuration, clock mapping, units, warm-up, workload, sample count, and failures/dropped observations. They SHALL distinguish input-window duration, capture-to-emission delay, engagement decision/smoothing delay, and UI delivery delay. Reported distributions SHALL use comparable samples; missing instrumentation SHALL remain explicit.

#### Scenario: Windowed speech benchmark
- **WHEN** a speech model processes a multi-second audio window
- **THEN** the report distinguishes that window duration from processing and capture-to-emission delay and identifies the measured timing endpoints

#### Scenario: Only producer timing is available
- **WHEN** the available instrumentation measures capture-to-emission but not browser display
- **THEN** the report labels producer delay, states UI delay is unmeasured, and makes no end-to-end latency claim

### Requirement: Validate concurrent application operation
A claim of integrated accelerator performance SHALL require concurrent speech and vision operation through LeCoach's sole engagement engine and recorder. The record SHALL include repeated-session, shutdown/resource-release, and unavailable-input results alongside timing. Isolated model throughput SHALL NOT establish live audience responsiveness.

#### Scenario: Concurrent rehearsal observed
- **WHEN** the integrated pipeline runs on the identified target configuration
- **THEN** the report records workload, producer delays, audience behavior, supported feedback, resource cleanup, repeat-session isolation, and failures for that configuration

#### Scenario: Only an isolated model runs
- **WHEN** one model executes without the integrated concurrent pipeline
- **THEN** the record identifies isolated inference and leaves concurrent LeCoach compatibility and responsiveness unverified

### Requirement: Reuse owner implementations and local data rules
Hardware validation SHALL use the approved subsystem implementations and canonical clocks/events without creating alternate producers, engagement engines, or loggers. Input, inference, and session processing SHALL stay local. Raw recordings, transcripts, exports, credentials, and weights SHALL remain outside Git; public evidence SHALL contain sanitized observations.

#### Scenario: Benchmark needs an unimplemented adapter
- **WHEN** a target measurement depends on an owner adapter that has not landed
- **THEN** the record exposes that handoff dependency rather than substituting an unreviewed competing implementation or cloud inference

#### Scenario: Run retained for reproduction
- **WHEN** a development run generates private media or session output
- **THEN** those files remain in ignored local storage and the committed summary contains configuration, procedure, aggregate observations, and limitations only

### Requirement: Separate Stage I CPU and Stage II accelerator milestones
Stage I SHALL validate actual local CPU behavior on the confirmed ordinary demo computer without depending on UGen300 access. Eventual target runtime/model/interface compatibility and isolated/concurrent performance SHALL remain Stage II requirements. A missing-device disposition SHALL NOT establish either live CPU acceptance or accelerator execution.

#### Scenario: No accelerator before qualification
- **WHEN** the maintainer confirms no UGen300 will be available before Stage II
- **THEN** Stage I speech/vision/application work proceeds on CPU and hardware-only measurements remain an explicit later milestone
