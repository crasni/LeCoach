# Coaching consumer handoff review — 2026-10-10

This is dated Lane 5 compatibility evidence, not a task board or acceptance of
the integrated live product. Current acceptance lives in
[#20](https://github.com/crasni/LeCoach/issues/20),
[#21](https://github.com/crasni/LeCoach/issues/21) and
[#18](https://github.com/crasni/LeCoach/issues/18).

## Reviewed sources and boundary

- Coaching preparation at `9850ae0` was independently approved by integration in
  [PR #24's review](https://github.com/crasni/LeCoach/pull/24#pullrequestreview-5468827739).
- Main source snapshot: `e5c083837a06ae4e3c8edd4fd9b8e0281dbb8ca0`, including
  speech core and vision producer continuations. No runtime dependencies were
  installed and no live adapters were started for this review.
- Proposed engine snapshot: `d76d37375cfd7870dad6d97d0e9b22c355626b59` in
  [PR #29](https://github.com/crasni/LeCoach/pull/29), with its linked
  [`live-01-audience-engagement` specification](https://github.com/crasni/LeCoach/tree/d76d37375cfd7870dad6d97d0e9b22c355626b59/openspec/changes/live-01-audience-engagement).
  This review confirms coaching compatibility; integration owns shared behavior
  acceptance and merge. No feature branch was merged for these checks.

The seven existing reason codes, explicit cited event IDs and capture/decision
times fit the canonical `CompletedSession` / `Feedback` consumer. Freshness still
comes from the public `RuleConfig.speech_stale_s` and `vision_stale_s`, never a
second coaching rule config. New `pause_hold_s` and `history_limit` stay engine-owned.

## Consumer conclusions

| Engine handoff | Coaching behavior |
| --- | --- |
| `ENGAGED` needs uninterrupted positive evaluations | Select a strength only from emitted, cited `ENGAGED`; do not infer sustain from elapsed time in `INTERESTED` |
| Active pause holds pace/filler rules and gives speech no pace verdict | Use emitted reasons; do not label silence-filled WPM as a steady pace or recompute speech rules |
| Facing can carry positive evaluation during a pause | A facing-only strength describes approximate facing; it has no pace claim or uncited speech evidence |
| Recovery status cannot revive pre-outage windows | Reject all cited measurements and newest source observations captured at/before the latest outage, including capture-time ties |
| A held negative rule can re-cite old trigger windows | Omit a reason once its newest cited window or current source observation exceeds the supplied stale age; retain the earlier fresh incident |
| Explicit evidence retains capture timestamps | Baseline feedback remains 10/25/40 s; strength cites `vision-35`, not same-time uncited `vision-40` |

The outage check is conservative over recorded capture time, as the canonical
completed log does not retain delivery order. It does not reinterpret a recovery
status as a measurement. Unknown/missing/insufficient evidence produces limitations.

## Reproducible checks and results

macOS arm64, pinned CPython 3.12.14, existing frozen core/dev environment. Two
temporary source snapshots were created with `git archive`, outside the working
tree; no branch/ref merge, dependency update or live composition was performed:

1. Export main `e5c0838`; overlay this increment's `src/lecoach/coaching/`,
   `checks/coaching/`, `tests/test_coaching.py`, `tests/test_feedback.py` and
   `tests/test_session_feedback.py`. From that snapshot:
   `PYTHONPATH=src <project-venv>/bin/python -m pytest -q`.
   **216 tests / 376 subtests passed; 2 optional cv2 tests skipped.**
2. Copy that snapshot; overlay only PR #29's `src/lecoach/engagement/` and
   `tests/test_engagement.py`. From this separate snapshot:
   `PYTHONPATH=src <project-venv>/bin/python -m pytest -q tests/test_coaching.py tests/test_feedback.py tests/test_session_feedback.py tests/test_engagement.py`.
   **72 tests / 75 subtests passed.**

The existing Starlette/httpx warning is unchanged. These results concern the
described source overlays, not a merged revision or accepted live run. The
feedback tests replay every synthetic coaching case twice and check the original
computed baseline. New consumer regressions cover both source modalities,
unavailable/error status, recovery, capture-time ties and mixed old/new citations.
The local checker tests canonical JSON parity, timeline privacy, empty/repeated
sessions, drain limits, actual freshness config and malformed/unfinished/foreign logs.

On the assigned coaching branch itself, the full suite passed **157 tests /
112 subtests**. Ruff, canonical schema parity, fixture validation and whitespace
checks passed; computed-coaching and recorder replay each passed **9 cases /
10 sessions**. The checker was also invoked as a subprocess on a synthetic
completed record: JSON matches the generated canonical Feedback, text includes
the timeline and no output file is created. The four revised handoff documents
have **14 valid local file/anchor references**. These checks do not require
merging main or another role branch into this branch.

Four additional synthetic sequences were driven through the existing
`SessionController`, engine, recorder and generator in the PR #29 snapshot:

| Input sequence | Recorded result |
| --- | --- |
| Facing 0.8 at 1 s cadence, but 0.5 every fourth window through 19 s | NEUTRAL 0 s → INTERESTED 3 s; no ENGAGED or strength |
| Speech 144 WPM with 1.5 s active pauses and facing 0.8 at 2–12 s | INTERESTED 3 s → ENGAGED 7 s; strength anchored at cited facing capture 6 s, no WPM claim or speech citation |
| Speech 200 WPM at 10–25 s, then 10 s trailing windows with falling WPM and active silence through 33 s | CONFUSED 15 s → BORED 32 s; two supported improvements, no false recovery/strength; pause intent remains unknown |
| Facing-away windows at 1–4 s, outage 4.5 s, available 5 s, late old window and one fresh window at 9 s | NEUTRAL only; no invented moment or revived pre-outage sustain |

These are scripted normalized observations, not microphone capture, camera
inference, browser E2E, narration timing or hardware performance. The proposed
engine's own checked-in tests cover these rule boundaries; coaching consumes their
transitions and never implements another engine.

## Published seam for downstream use

Integration composes the existing recorder and generator through `Components`;
the generator receives the same engine stale ages. UI consumes canonical
`Feedback` plus `CompletedSession.events`; it can show the complete recorded
timeline even after a websocket reconnect missed transitions. The independent
[completed-session checker](../../src/lecoach/coaching/README.md#inspect-a-completed-session-locally)
reads the same canonical data and emits canonical Feedback or a text timeline
without transcript contents. It neither captures nor persists input.

Stage I narration now targets the ordinary CPU host; hardware validation remains
Stage II after qualification. The [revised script](demo/narration.md) has 316 words
in the existing 175 s shot plan, estimated 140.4 s reading at 135 WPM and 34.6 s
holds. Actual read-through/edit duration and the accepted real-input run remain
required before final demo claims change. Raw recording remains off by default;
recording/media publication/competition delivery retain separate authorization.

## Plain advice and delivered CPU script checks — 2026-10-10

Base source: merged main `b419a617c96ac6e8a28bdc6767ffb905e522d933`, safely
fast-forwarded into the existing assigned role branch. The preceding `03028dd`
continuation received integration approval and merged in PR #24 (`5000c23`).
PR #23 delivers the public local CPU composition. #17 is accepted (no rollback;
abandoned scratch branch retained). Historical observations above retain their
original revision/host attribution; live acceptance belongs to Issues.

The maintainer's [requested advice refinement](https://github.com/crasni/LeCoach/issues/20#issuecomment-6095551081)
is implemented as plain observations plus one concrete practice action. User copy
no longer exposes cited-window terminology or normalized facing scores. The
selector/recorder/engine, quotas, capture anchors and canonical citations are
unchanged. Active pauses report the longest supported elapsed duration as a
lower bound with unknown intent. Camera-only strengths make no pace claim.
Filler observations are attributed to the transcript; no measured filler recall
or filler-driven demo story is claimed.

Local macOS arm64 / CPython 3.12.14, existing core/dev environment:

```sh
env -u DISPLAY -u WAYLAND_DISPLAY .venv/bin/python -m pytest -q
# 258 passed / 392 subtests; 12 optional-runtime tests skipped
.venv/bin/python -m pytest -q tests/test_feedback.py tests/test_session_feedback.py tests/test_live_composition.py
# 32 passed / 43 subtests
.venv/bin/ruff check src scripts tests examples checks/coaching/feedback_replay.py checks/coaching/session_feedback.py
.venv/bin/python checks/coaching/feedback_replay.py --show-feedback
.venv/bin/python checks/coaching/record_replay.py
.venv/bin/python scripts/export_schema.py --check
.venv/bin/python scripts/validate_fixtures.py
git diff --check
```

All pass; the existing Starlette/httpx deprecation warning remains. Ten speech
runtime tests and two optional OpenCV tests skip because this environment has
no corresponding optional runtime stack/assets. No model/package installation,
real-device capture, inference performance, browser E2E or recording is claimed.
Both replay paths pass nine synthetic cases / ten sessions. All transition and
moment time/kind/ID baselines are unchanged; only a plain unfinished-results
limitation phrase changes in the computed oracle. The new active-pause regression
checks that advice does not invent a final duration or an intentional pause.

[The revised narration](demo/narration.md) contains six blocks
`[35, 32, 90, 76, 43, 33]`, **309 words**: estimated 137.3 s at 135 WPM plus
37.7 s holds within 175 s, with each slot fitting that assumed pace. These are
estimates. The maintainer-reported approximately 2:20 read-through belongs to
the earlier 316-word `03028dd` draft, not this revision or the edited video.

The script/runbook now reflect delivered live browser coaching and the confirmed
Ubuntu/Bluetooth operator handoff. The [passed reliability batch](https://github.com/crasni/LeCoach/issues/11#issuecomment-6095334266)
is attributed operator evidence; no repetition is requested. Exact moment
time/text/citations and sanitized run/configuration provenance still need reviewer
confirmation before live advice acceptance and final footage. Revised read-through,
per-slot/edit timing and recording/publication/submission authorization are separate
remaining pickups. Stage II accelerator validation is unmeasured.
