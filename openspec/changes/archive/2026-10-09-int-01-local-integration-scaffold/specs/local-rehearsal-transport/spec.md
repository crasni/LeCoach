# Spec Delta

## Purpose

Expose rehearsal controls and observations to a local browser while keeping capture independent of browser delivery. [ARCHITECTURE.md](../../../../../../docs/ARCHITECTURE.md#int-01-implementation-decisions-and-handoff) defines the routes and transport wrappers.

## ADDED Requirements

### Requirement: Keep rehearsal transport local
The documented backend and development UI SHALL bind to loopback. Browser origins SHALL be restricted to the documented local UI, and the default replay UI SHALL use local assets and APIs without remote runtime services.

#### Scenario: Untrusted browser origin
- **WHEN** a browser outside the allowed local origins requests HTTP or WebSocket access
- **THEN** the transport rejects access

#### Scenario: Default replay network traffic
- **WHEN** the built browser shell runs a synthetic replay
- **THEN** its assets and runtime requests remain on the local host

### Requirement: Subscribe before starting
The API SHALL expose preparation, event subscription, start, stop, snapshot, and feedback operations. Start SHALL require an attached event client; retries SHALL preserve the active session rather than create another capture.

#### Scenario: Start without subscription
- **WHEN** a client tries to start a prepared session before attaching its event stream
- **THEN** the API refuses the start and capture remains unstarted

### Requirement: Resynchronize without restarting capture
An event-stream connection SHALL receive a current snapshot before subsequent canonical events. Reconnection SHALL report current phase, availability, transcript, and latest audience state without starting capture again.

#### Scenario: Browser interruption
- **WHEN** a browser reconnects after losing its event stream during a rehearsal
- **THEN** it receives the current session snapshot and makes no additional start request

### Requirement: Isolate slow browsers
Each browser stream SHALL use bounded delivery buffering independent of producer and recorder delivery. Overflow SHALL close that stream with code 1013 so the client can resynchronize instead of blocking the rehearsal.

#### Scenario: Queue overflow
- **WHEN** a browser cannot consume events before its queue fills
- **THEN** that connection closes with code 1013 while the recorder continues receiving accepted events

### Requirement: Preview without another capture stream
Preview SHALL expose only the vision adapter's latest volatile frame, under configured size/rate bounds. The browser SHALL NOT open another camera for preview. Missing preview SHALL report unavailable explicitly.

#### Scenario: Camera unavailable
- **WHEN** no adapter frame is available
- **THEN** preview reports unavailable and the rest of the session remains inspectable

### Requirement: Expose honest mode and feedback state
Snapshots and the shell SHALL distinguish fixture/live mode and authored/computed outputs. Missing live composition SHALL report unavailable. Feedback SHALL distinguish pending, ready, and unavailable; an early-stopped authored replay SHALL NOT invent a summary.

#### Scenario: Synthetic rehearsal
- **WHEN** the default replay is running
- **THEN** the shell visibly labels it synthetic and presents reactions/coaching as authored examples

#### Scenario: Early stop
- **WHEN** the user stops fixture playback before its authored completion
- **THEN** the session completes with feedback unavailable rather than presenting its full authored summary
