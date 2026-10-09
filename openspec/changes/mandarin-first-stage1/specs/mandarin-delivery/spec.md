# Spec Delta

## Purpose

Support Mandarin rehearsals with local transcription and delivery evidence whose language, units, support and uncertainty remain explicit to all consumers.

## ADDED Requirements

### Requirement: Default to local Mandarin transcription
The product SHALL default to Mandarin rehearsal transcription using a local multilingual model. Partial/final text SHALL follow the existing session clock and revision rules. English-only models and translation into English SHALL NOT stand in for Mandarin recognition.

#### Scenario: Mandarin passage with mixed content
- **WHEN** a user rehearses Mandarin containing Taiwan terminology, numbers and an English product name
- **THEN** the transcript retains the spoken meaning and revision identity without translating the passage into English or double-counting partials

#### Scenario: Local model unavailable
- **WHEN** the Mandarin model cannot be loaded locally
- **THEN** the product reports the input limitation and continues with usable inputs without a remote inference fallback

### Requirement: Represent supported pace with its actual unit
Mandarin pace SHALL have an agreed counting/tokenization method, capture-window denominator, finalized coverage rule and explicit unit before it drives a displayed rate, engine threshold or coaching. Chinese character rates SHALL NOT populate English WPM fields or inherit English pace thresholds.

#### Scenario: Character rate proposed
- **WHEN** an owner proposes Han characters per minute
- **THEN** the producer and consumers agree character inclusion, mixed-script handling, units and thresholds through a linked contract delta before using that rate

#### Scenario: Pace unsupported
- **WHEN** the installed Mandarin pipeline does not support an agreed pace measurement
- **THEN** pace is null/unknown and neither a zero nor an English pace-related audience reason is fabricated

### Requirement: Ground Mandarin fillers in supported detection
Mandarin filler observations SHALL use an agreed language/context method with finalized transcript coverage and revision deduplication. Normal content words and proper names SHALL NOT be treated as fillers solely because they match an English or unreviewed Mandarin lexicon. Unsupported detection SHALL return null.

#### Scenario: Ambiguous filler-like content
- **WHEN** a passage contains "那個部門" or "就是這項功能"
- **THEN** unvalidated substring matching does not fabricate a filler count or coaching criticism

#### Scenario: Filler capability unknown
- **WHEN** no agreed Mandarin filler method is available
- **THEN** count/rate remain null while transcript and independently supported pause/facing evidence remain usable

### Requirement: Keep observation support independent
Unknown pace or fillers SHALL NOT invalidate independently supported transcript, pause or vision observations. Audience/coaching SHALL cite only available supported evidence. Unknown metrics SHALL NOT silently satisfy unmet speech acceptance requirements.

#### Scenario: Mandarin pace unknown with camera evidence
- **WHEN** Mandarin pace/fillers are null and sustained facing-away/recovery observations are available
- **THEN** audience reactions may cite facing evidence but do not infer fast/slow/steady speech or fillers

#### Scenario: Required measurement still unsupported
- **WHEN** final P0 speech acceptance requires a measurement the Mandarin pipeline cannot provide
- **THEN** the limitation and concrete scope trade-off are reported to the maintainer instead of accepting fabricated evidence or silently waiving the requirement

### Requirement: Validate on the confirmed Stage I CPU host
Stage I validation SHALL use real microphone/camera input and local CPU inference on a confirmed ordinary computer, recording model/configuration, measured behavior and lifecycle limitations. UGen300 absence SHALL NOT block that validation; eventual accelerator validation SHALL remain a later milestone.

#### Scenario: Host not yet confirmed
- **WHEN** Lucas is the planned operator but the actual computer is unconfirmed
- **THEN** setup and synthetic checks continue while final live/model validation remains pending

#### Scenario: CPU run accepted
- **WHEN** Mandarin behavior is measured on the confirmed computer
- **THEN** evidence identifies actual input, supported observations, audience/coaching, failures and repeated-session cleanup without claiming accelerator execution
