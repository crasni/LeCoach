# English narration draft — 2:55 development preview

Companion to [the Lane 5 runbook](README.md) and integration's existing
[shot plan](../../../docs/DEMO.md). This text is for script review and timed
read-through. It is not a final live-demo script, recording or submission.
Live replacements depend on accepted runs in Issues
[#20](https://github.com/crasni/LeCoach/issues/20) and
[#11](https://github.com/crasni/LeCoach/issues/11).

Read only the six `text` blocks. Screen directions, timing notes and live pickups
are not narration. Keep a visible **Synthetic development preview** label.
Session timestamps and edited-video times are different clocks; the fixed numbers
below belong to `weak_to_improved` only.

## 0:00–0:20 — Why rehearse with an audience?

Screen: title and rehearsal audience. Introduce intended value as a product goal;
no user study or measured outcome is claimed.

```text
Practicing a presentation alone gives you few clues about how an audience might
respond. LeCoach is our prototype for a private virtual audience, designed to
connect delivery habits with visible reactions and practical rehearsal advice.
```

## 0:20–0:35 — Identify the demonstrated mode

Screen: fixture selector and Start replay control; no live capture indicator.
Generated coaching will be shown separately in the terminal.

```text
This development preview uses synthetic speech and camera measurements. The
audience reactions are computed locally. We show generated coaching separately;
the browser currently displays an authored example summary.
```

## 0:35–1:35 — Weak delivery and recovery

Screen: play the synthetic audience sequence, then hold the timeline/reasons.
Default 5× replay lasts about ten wall-clock seconds. Use the rest of the slot
to explain the completed timeline; retain the mode and speed labels.

```text
The example starts with fast speech and a sustained turn away from the audience.
The recorded speech windows are around two hundred words per minute. The virtual
listeners become confused at twenty seconds, then bored at thirty seconds.

As the example settles into a steadier pace and faces forward, the audience
becomes interested, then engaged at forty seconds. These are session timestamps.

The reactions use sustained observations and smoothing, so a single movement
does not define the whole rehearsal. The timeline makes the change visible and
gives the speaker a place to review what happened.
```

## 1:35–2:15 — Timestamp, observation, action

Screen: terminal output from `feedback_replay.py --case weak_to_improved
--show-feedback`, paired with its generated moments and evidence IDs. Keep the
browser's authored summary out of this shot or label it explicitly as authored.
No generated-summary browser integration is claimed here.

```text
The generated summary points to fast speech at ten seconds and approximate
head or body facing at twenty-five seconds. It suggests pausing after key points
and placing notes nearer the camera. At forty seconds, it highlights a supported
strong moment with a steadier pace and forward orientation.

Each observation links to recorded evidence. Facing uses coarse head and body
estimates. When inputs are missing or evidence is insufficient, the coach reports
limitations and returns fewer suggestions.
```

## 2:15–2:40 — Stage I CPU processing and the hardware plan

Screen: existing architecture diagram and **Stage I: local CPU target;
Stage II: UGen300 validation pending** caption. This preview has no accelerator
benchmark or live privacy validation.

```text
Stage I targets an ordinary computer using local CPU inference. The current
checks exercise synthetic events; real microphone and camera validation is still
pending. LeCoach is designed to keep rehearsal data on the device, with raw
recording off by default. UGen300 integration and hardware measurements belong
to Stage II after qualification.
```

## 2:40–2:55 — Next demonstrated milestone

Screen: audience and generated moments with the synthetic label retained. End
on the next validation step, without a release-date promise.

```text
Our next milestone is an accepted microphone and camera rehearsal with the same
evidence-linked coaching. The goal is simple: help speakers connect delivery,
audience response, and a useful next practice step.
```

## Timing method and final live pickups

The slots total 175 seconds. Word counts and estimated reading times are in the
runbook; they are not measured voiceover or finished-video durations. Record
actual per-slot times during an authorized read-through. Use screen holds for
the timeline, reasons and evidence.

Before adapting this narration to an accepted live run:

- Replace the mode paragraph with the actual host/input mode and accepted run
  reference. Keep CPU and verified accelerator execution distinct.
- Replace fixture values/times with actual capture timestamps, reasons and
  supported moments. Describe the observed count; three is not a quota.
- Show generated feedback in the UI only after its composition/rendering is
  accepted. Otherwise identify the actual viewer used in the footage.
- Retain the approximate-facing qualification. Missing input is a limitation;
  pause duration alone does not establish whether a pause was intentional.
- Keep local processing as design intent until actual live data flow and
  retention are reviewed. Stage I uses the confirmed ordinary CPU host; Stage II
  accelerator wording changes only with measured hardware evidence. See the
  [English CPU direction](https://github.com/crasni/LeCoach/issues/21).
- Re-time the revised narration and final edit. Supply commit/run references,
  actual duration and reviewer notes to integration.

These pickups prepare a later final script. Real rehearsal recording, video
upload and competition delivery require their applicable authorization.
