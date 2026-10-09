# Proposal

## Why

The maintainer selected Mandarin rehearsals and native Traditional Chinese product
content for Taiwan, with ordinary-computer CPU inference for Stage I. The previous
English analysis decision and English UI/coaching do not meet that direction;
existing owners and implementations must be extended rather than replaced.

## What Changes

- Default spoken rehearsal language to Mandarin and user-facing content to zh-TW.
- Agree local multilingual transcription, Traditional Chinese display, Mandarin
  pace units/tokenization and contextual filler rules before changing producers,
  event/configuration semantics, engine rules or coaching consumers.
- Preserve null for unsupported measurements. Never place Chinese character counts
  or rates in English WPM fields or reuse English filler rules for Mandarin.
- Keep real CPU microphone/camera validation on the confirmed demo computer as the
  Stage I acceptance target. UGen300 access is unavailable before qualification;
  actual accelerator validation remains a Stage II milestone.
- Preserve English competition deliverables where official rules require them;
  show Mandarin rehearsal/zh-TW UI with mainly English explanatory narration and
  explanatory captions. Lucas is the likely operator, not a confirmed recording.
- Add integration-owned synthetic Mandarin examples and behavioral/presentation
  handoff checks, independently of actual speech/model quality validation.

No v0 schema change is approved here. A typed Mandarin pace representation or
new rule codes require affected-owner agreement and a coherent contract delta.

## Capabilities

### New Capabilities

- `mandarin-delivery`: Local Mandarin transcript and delivery observations with
  explicit measurement support, units and evidence limits.
- `zh-tw-experience`: Native Taiwan Traditional Chinese rehearsal and coaching
  presentation, including devices, unknown measurements and example scenarios.

### Modified Capabilities

None. No archived main capability specs exist. The existing INT-03 planning
artifacts are separately reconciled for Stage I CPU evidence and later accelerator
validation, without restarting that change.

## Impact

Integration owns canonical guidance, contracts/dependencies/composition and this
cross-lane agreement. Speech owns its adapter and measurement method; realtime
owns engine/UI; coaching owns feedback and scenarios. Existing Issues #6/#11/#12,
#13/#14, #18/#19 and #20/#21 retain owners/branches/acceptance; #15/#16 retain CPU
vision handoffs and defer hardware-only measurements. No parallel implementation,
cloud inference, default recording or private data publication is introduced.
