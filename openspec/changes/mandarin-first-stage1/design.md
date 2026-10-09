# Design

## Context

See [proposal.md](proposal.md) and both capability deltas. Integration is at
`929f727`; public PR #26 has a model-free speech adapter with English-only
tokenization, `base.en` and null metrics for unsupported languages. PR #24 has
English templates and a synthetic English narration draft. Main contains the
CPU vision adapter; frontend copy is English in `copy.ts` and `main.tsx`, with
additional English API messages and authored example feedback. Existing v0
speech metrics contain `wpm`, filler observations and pause state, not a typed
Mandarin pace observation. No archived main capability specs exist.

## Goals / Non-Goals

**Goals:** Extend the existing lane implementations, preserve honest unknowns,
agree unit-aware Mandarin observations and create a complete zh-TW experience
with reproducible ordinary-computer setup and evidence.

**Non-Goals:** A second engine/recorder, cloud fallback, unvalidated Chinese WPM,
content translation into English, immediate accelerator development, P1 LLM/TTS,
recording/publication or a silent P0 acceptance exception.

## Decisions

### Keep recognition, measurement and presentation separate

Recognition language is Mandarin (`zh` where the model uses that code); display
locale is `zh-TW`. Speech owns a multilingual CPU Whisper path and its Traditional
script handling. Integration retains the optional runtime groups and constructs
the speech-owned configuration. A multilingual `base` CPU/int8 model is a
candidate, not a measured quality/performance decision; `base.en` is unsuitable.
Evaluate Taiwan terms, names, code-switching, numbers, fillers and silence. Local
script conversion, if used, must be documented/reviewed for names/meaning; it is
not transcription or a translation from English. No weights load/download during
session start. Alternatives: retain English-only model or translate Mandarin to
English—rejected because they fail the product direction.

### Agree measurement before enabling rules

Use v0 null WPM/fillers for the independent Mandarin fallback fixtures. Supported
capture/pause/facing semantics remain unchanged. Before enabling a Mandarin rate,
speech proposes the counting unit and timestamp/window coverage; realtime and
coaching agree its meaning; integration publishes the typed contract/schema
delta. A candidate is Han characters/minute with punctuation/whitespace excluded
and explicit mixed-script/number rules, but it is not an approved field or band.
Fillers need finalized coverage, deduplication and a conservative contextual
method; phrases such as "那個部門" are ambiguous content, not automatic fillers.
No English lexicon or WPM bands are reused. The #6 decision record owns agreement;
silence-positive reactions remain #18's existing behavior handoff. Alternatives:
relabel WPM as Chinese rate or count every filler-looking substring—rejected.

Unknowns let other work proceed; they do not complete unverified P0 pace/filler
acceptance. If a supported method cannot meet the Stage I timeline, owners must
bring the maintainer a concrete capability/scope trade-off.

### Localize the whole experience in the owning lanes

Realtime owns frontend copy/control/status/reason/timeline presentation and
desktop/narrow browser checks. Coaching owns native zh-TW observation/action and
limitation templates, preserving citations/quotas. Integration audits transport
fallbacks and launch guidance; it does not rewrite lane internals. Unknown reason
codes use useful localized fallbacks. User-spoken content is not translated for
UI consistency. Existing English fixtures remain developer regression evidence;
the default user examples must be Mandarin/zh-TW and label synthetic/authored
outputs. Alternatives: translate `copy.ts` only or localize UI while backend
feedback/errors remain English—rejected as incomplete.

### Separate Stage I CPU acceptance from Stage II hardware validation

The maintainer states no UGen300 is available before qualification. Stage I
uses actual local CPU microphone/camera on the confirmed demo computer; CPU
vision/speech responsiveness, shutdown/drain/restart and unavailable-input checks
remain required. Move only target-device validation to the retained Stage II
milestone in #12/#14/#16. Keep accelerator boundary/candidates; eventual validation
still requires actual runtime/model/interface and concurrent application evidence.
Lucas is likely operator, not confirmed narrator/recording permission. Require
OS/CPU/architecture/RAM/devices, model/setup hashes and exact launch before final
CPU acceptance. Proposed startup bounds await actual host measurements.

### Keep competition deliverables compliant

Official rules content was re-fetched on 2026-10-09 (CONTEST/SOURCES): English
deck, mainly English video explanation, ordinary Stage I host permitted. Retain
Mandarin rehearsal and zh-TW UI in the footage; Lane 5 supplies mainly English
explanation and explanatory captions. Final edit timing and requirements are
rechecked before submission. Existing English draft is historical preparation,
not final Mandarin demo acceptance.

## Risks / Trade-offs

- [ASR drops fillers or changes script/names] → actual Taiwan Mandarin evaluation;
  null detection when unsupported, and scoped script normalization review.
- [Mandarin counting unit/threshold differs from English] → owner agreement and
  typed contract delta before consumers change; no rate masquerading as WPM.
- [Slow CPU partial/final recognition] → measure on confirmed host, choose a
  practical multilingual model and report lifecycle bounds; no cloud fallback.
- [Localized strings overflow or technical codes leak] → complete inventory and
  browser happy/failure/empty/narrow checks in the UI lane.
- [Unknown fallback is mistaken for completed P0] → keep Issue acceptance open;
  escalate real unsupported capability/time trade-offs to the maintainer.

## Migration Plan

Preserve branches/assignments and prior English regression evidence. Publish
policy/guidance, these planning artifacts and integration-owned synthetic
Mandarin fixtures. Collect affected-owner agreement in #6/#18/#20 and reconcile
the existing speech change on its owner's branch. Then owners extend their lanes;
integration regenerates any agreed contract and composes accepted public seams.
Run fixture checks and zh-TW browser review, followed by actual microphone/camera
validation on the confirmed CPU host. Keep Stage II accelerator evidence pending.
Rollback, if needed, preserves null measurements and uses scoped reviewed commits;
it must not silently restore the superseded English product default.

## Open Questions

The actual demo host and recording arrangement remain unconfirmed; neither
prevents synthetic checks or owner design review. Model size and runtime bounds
will be selected from host measurements within the agreed local CPU approach.
