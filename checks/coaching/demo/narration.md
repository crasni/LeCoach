# English narration — 2:55 CPU live draft

Companion to [the Lane 5 runbook](README.md) and integration's
[shot plan](../../../docs/DEMO.md). This revises the merged `03028dd` preview for
main's delivered live composition. It is a reviewable script, not a final recording
or submission. Read only the six `text` blocks.

The maintainer reported an approximately **2:20 spoken read-through of the previous
316-word script** ([source](https://github.com/crasni/LeCoach/issues/12#issuecomment-6095163116)).
That timing does not measure this revision, individual slots or the edited video.
The confirmed host is the maintainer's Ubuntu PC using local CPU inference and a
Bluetooth microphone. The operator reports that the live functional batch passed;
exact coaching moments/citations and quantitative accuracy/latency remain separate.
See [the functional handoff](https://github.com/crasni/LeCoach/issues/11#issuecomment-6095334266).

Keep **Live · local CPU** visible for actual live footage and **Synthetic replay**
for fixture footage. Session timestamps and edited-video times are different clocks.
Do not substitute synthetic values for a live run. The spoken text makes no fixed
live timestamp, insight-count or filler-recall claim.

## 0:00–0:20 — Why rehearse with an audience?

Screen: title and audience. Introduce intended value; no user-study result is claimed.

```text
Practicing a presentation alone gives you few clues about how an audience might
respond. LeCoach is our prototype for a private virtual audience, designed to
connect delivery habits with visible reactions and practical rehearsal advice.
```

## 0:20–0:35 — Identify the demonstrated mode

Screen: the live selector and local input notices on the confirmed CPU host.
Use this paragraph with actual live footage only; the default fixture preview
has authored example coaching and needs its own explicit replay label.

```text
The live prototype runs on an ordinary computer, using local speech and camera
processing. Starting a rehearsal opens the inputs. Stopping it produces a summary
from the observations collected during that session.
```

## 0:35–1:35 — Weak delivery and recovery

Screen: the authorized pace/facing scenario from the runbook, followed by its
actual timeline. Show the observed sequence; do not force a specific state or
reuse the synthetic 20/30/35/40-second transitions as live results. If footage
fails to support a sentence, revise that sentence before final review.

```text
We practice the same short workplace update twice. First, we rush the key points
and stay turned toward our notes. Then we repeat the passage at a steadier pace,
facing the camera.

The virtual audience responds to sustained delivery signals. Changes take time;
one brief movement does not define the whole rehearsal. These reactions are a
practice aid, not a measurement of real people's feelings.

The timeline lets us revisit the moment when the audience changed. We can compare
that reaction with the delivery observations instead of guessing what happened.
```

## 1:35–2:15 — Timestamp, observation, action

Screen: generated **live** feedback after stop, showing its actual timestamps.
Match each visible card to its existing canonical evidence IDs before review.
The final shot needs at least one supported example of the advice described below;
show fewer cards when evidence is limited. Do not overlay synthetic advice on live footage.

```text
The summary gives us a specific place to practice again. A fast passage can lead
to a simple next step: repeat it more slowly, pausing after each key point. A
camera-facing suggestion asks us to deliver the next sentence toward the camera.

Supported strengths show what to repeat. Each suggestion keeps its timestamp and
links to recorded observations. The camera estimates direction, not eye contact.
Missing inputs or insufficient evidence produce limitations, rather than invented advice.
```

## 2:15–2:40 — Local CPU processing and the hardware plan

Screen: existing architecture and **Stage I: local CPU · Stage II: UGen300
unmeasured** caption. Local processing and raw-recording defaults are implemented
properties; they are not a completed security audit or a performance benchmark.

```text
Speech recognition and pose processing run locally on the Stage I computer.
Rehearsal data stays local, and raw audio and video recording are off by default.
We have not measured accelerator performance. UGen300 integration and hardware
validation belong to Stage II after qualification.
```

## 2:40–2:55 — One useful next rehearsal

Screen: one reviewed observation/action card and the new-session control. No
accuracy, learning-outcome or release-date promise.

```text
Choose one supported suggestion, then practice the passage again. LeCoach aims
to make that next rehearsal more focused: connect a delivery habit with an
audience response and a concrete action you can try.
```

## Final pickups

The slots total 175 seconds. Before final script/footage acceptance:

- Supply a sanitized run/revision/configuration reference and the actual visible
  moment kind, timestamp, observation, action and supporting IDs for the advice shot.
  #11's passed operator batch does not supply these exact values. Do not repeat
  the completed functional batch just to establish the same general success.
- Confirm that live footage shows generated coaching. Plain `lecoach serve` and
  fixture selection still show authored example coaching; label that mode explicitly.
- Review the actual outcome with #20/#11 owners. More silence is not necessarily
  intentional; camera direction is not eye contact. Avoid filler-driven reactions
  while #14's recall investigation is unresolved.
- Time this revised read-through, actual per-slot holds and the final edit.
  The earlier approximately 2:20 result belongs to `03028dd`, not this draft.
- Retain CPU/hardware attribution and local-retention limits. Obtain separate
  recording, publication and submission authorization before those actions.

Integration receives the versioned script, evidence references and measured edit
through #21/#12. Final task acceptance remains in Issues.
