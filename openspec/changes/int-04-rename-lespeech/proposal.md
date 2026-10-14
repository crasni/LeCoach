# Proposal

## Why

"LeCoach" is already the name of an existing AI coaching product. On 2026-10-14 the team chose **LeSpeech** as the product name, ahead of the extended Stage I deadline (2026-10-28 17:00 Asia/Taipei). The maintainer also found the audience-state labels ("Perking up", "Losing the thread") and the coaching sentences too literary for a first-time viewer or a judge watching a three-minute demo.

## What Changes

- Product name `LeCoach` → `LeSpeech` in the UI, documentation, OpenSpec (archived changes included) and repository links (`crasni/LeCoach` → `crasni/LeSpeech`).
- **BREAKING (tooling):** Python package and CLI `lecoach` → `lespeech` (`uv run lespeech serve`); environment variables `LECOACH_*` → `LESPEECH_*`; frontend package `lecoach-frontend` → `lespeech-frontend`. Run `uv sync` after pulling.
- Audience-state labels use everyday words: Engaged, Interested, Listening, Confused, Bored. Their one-line descriptions, the reason phrases and the review-screen headings are shortened in the same spirit.
- Coaching sentences (live templates, limitations and the authored replay example) say what happened and what to try in short, plain sentences, keeping the hedges ("about", "seemed") and making no causal claim.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rehearsal-screen`: audience states are named with everyday words.

## Impact

Event contracts, `engagement.state` values, engine thresholds, coaching selection and the JSON schema are unchanged. Every lane's commands and environment variables change name; owners are tagged in the coordination Issue. The superseded `docs/submission/proposal.{fodp,pdf}` pair keeps its historical name because its PDF cannot be regenerated without LibreOffice; the Stage I deck is delivered outside the repository.
