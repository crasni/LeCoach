# Spec Delta

## Purpose

Present the complete LeCoach rehearsal and coaching experience in natural Traditional Chinese for Mandarin-speaking users in Taiwan, with honest observations and actionable advice.

## ADDED Requirements

### Requirement: Present all product surfaces in native zh-TW
Navigation, controls, onboarding, device/input status, errors, audience labels/reasons, metric explanations, timelines, feedback, empty states and default example scenarios SHALL use native Taiwan Traditional Chinese. The product name SHALL remain LeCoach. Internal identifiers, API fields and developer documents need not be translated.

#### Scenario: Start and finish a rehearsal
- **WHEN** a user prepares, starts, stops and reviews a Mandarin rehearsal
- **THEN** every product-authored instruction, notice and feedback sentence is natural zh-TW and supports the intended rehearsal task

#### Scenario: Example selected
- **WHEN** a user selects a default example
- **THEN** its title, scenario passage, explanation and authored feedback are zh-TW, and synthetic input/authored output remain visibly distinguished

### Requirement: Explain unavailable measurements and devices
Unsupported measurements SHALL appear as unknown with a useful zh-TW explanation, without zero values, misleading pace units or blame. Device/model failures and unknown reason codes SHALL have understandable zh-TW fallback notices rather than raw technical identifiers.

#### Scenario: Mandarin pace not supported
- **WHEN** the session has no supported Mandarin pace measurement
- **THEN** the UI explains that speaking rate is not yet available and displays no fabricated zero, WPM or character-rate label

#### Scenario: Camera cannot start
- **WHEN** camera availability, permission or local runtime prevents startup
- **THEN** the user sees a clear zh-TW notice and practical next action while any usable speech path remains available

### Requirement: Write evidence-based coaching naturally
Coaching SHALL give a timestamped observation and practical action in natural Taiwan Mandarin, using only the sole engine's supported citations. It SHALL NOT turn missing input, unknown Mandarin measurement, facing approximation or simulated audience reactions into claims of speaker quality, eye contact or emotion.

#### Scenario: Supported facing moment
- **WHEN** sustained facing-away evidence supports an improvement moment
- **THEN** coaching suggests a concrete rehearsal action such as moving notes near the camera and looking up for the next key sentence, without claiming eye tracking

#### Scenario: Insufficient evidence
- **WHEN** a short or unavailable-input session lacks supported moments
- **THEN** the summary explains the limitation in zh-TW and does not invent strengths, criticism or a score

### Requirement: Preserve language and evidence distinctions
Product UI/rehearsal language SHALL remain Mandarin/zh-TW even when competition material requires English explanation. Competition narration/captions SHALL explain demonstrated behavior without translating the product into an English default or concealing synthetic/CPU modes.

#### Scenario: Stage I video planned
- **WHEN** current rules require mainly English video explanation
- **THEN** the plan retains Mandarin rehearsal and zh-TW UI, using mainly English narration with explanatory captions for judges

### Requirement: Check actual Traditional Chinese presentation
Acceptance SHALL include a reviewed Mandarin example, localized happy/failure/empty states, readable Chinese fonts and wrapping at desktop/narrow widths, and correct metric units. Synthetic copy checks SHALL remain distinct from browser presentation and actual microphone recognition checks.

#### Scenario: Only fixture copy was checked
- **WHEN** synthetic transcripts and proposed zh-TW copy pass conformance checks
- **THEN** the evidence records fixture coverage and leaves actual UI rendering and Mandarin recognition unverified
