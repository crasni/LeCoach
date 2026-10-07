# LeCoach implementation status

Last updated: 2026-10-07.

This file records verified implementation evidence. Task ownership and progress live in [TASKS.md](../TASKS.md); product scope lives in [GUIDE.md](../GUIDE.md).

## Verified

- GitHub repository: https://github.com/crasni/LeCoach. Canonical SSH remote supplied by the maintainer: `git@github.com:crasni/LeCoach.git`.
- Initial bootstrap commit: `5f3eb6b` on `main`, pushed to `origin/main` and verified against the remote commit.
- README, product guide, ignore rules, and three reference PDFs are present.
- At the start of coordination work, `git pull --ff-only` reported already up to date.

## Not implemented or verified

- No application scaffold, runnable product, camera/microphone capture, speech/vision inference, engagement engine, audience UI, or post-session feedback exists yet.
- No model availability, inference latency, local privacy behavior, or UGen300 runtime compatibility has been measured.
- Competition details in GUIDE.md are project context; the latest official requirements have not been rechecked during repository bootstrap or team coordination.
- Event contracts and five role handoffs describe the intended MVP, not implementation evidence.

## Team assignments and access

FACT: On 2026-10-07 the maintainer supplied all five GitHub usernames and authorized assigning them to the five roles. The canonical named roster, task owners, branches, and reported invitation states are now in [TASKS.md](../TASKS.md). Assignment does not imply work has started.

IMPACT: Each onboarded agent can determine its lane from its collaborator's GitHub username. Some repository invitations are still pending according to the supplied roster, so those owners need to accept before pushing work. No collaborator has been messaged or newly invited by this agent.

PROPOSAL: Assigned owners follow the TASKS.md first-task and dependency instructions; the integration owner starts the scaffold. After accepting an invitation, update the access state in TASKS.md. GitHub API authentication is still unavailable here, so invitation acceptance cannot be checked automatically; SSH Git pull/push remains available.

## Evidence to add as work lands

For each completed task, record the commit/PR, exact runnable command, whether inputs are fixtures or live, observed result, and remaining limitation. For hardware measurements also record device, runtime/model version, and measurement method. Record discoveries as FACT / IMPACT / PROPOSAL as GUIDE.md requires.

## AUD-01 preparation — pending integration review

FACT: Lane 2 prepared commit `1ac7b53` on `agent/audio-streaming`, following claim commit `1412994`. [checks/speech/README.md](../checks/speech/README.md) documents ten synthetic cases covering eleven speech sessions, generated from hand-written scenario scripts. They cover steady and rapid pace, heavy fillers, prolonged silence, model warm-up with late, retried and out-of-order delivery, a hallucinated partial retracted by an empty final, denied and lost microphones, silence only, unsupported language, and repeated sessions. They follow proposed v0 speech rules documented in that README: English tokenizer and filler lexicon, window and coverage rules, null versus zero, and pause reporting. No microphone, audio, model, or accelerator was used.

Validation in the cloud development container (Linux, Python 3.13.16; the tests also pass with Python 3.11 and 3.12):

```sh
python3 checks/speech/check_speech.py
python3 -m unittest discover -s checks/speech -p 'test_*.py' -v
python3 checks/speech/make_fixtures.py --check
```

Observed result: all 10 cases / 11 sessions match their hand-derived oracles, and the committed fixtures match the scenario scripts. All 33 tests pass. They include rejection of:

- double-counted retries;
- revisions after a final;
- overlapping finals;
- unfinalized speech at completion;
- windows counted before their overlapping finals;
- zero instead of null for short or unavailable windows;
- metrics claiming availability during an outage;
- inflated WPM or filler counts;
- leading silence reported as a pause;
- unreported, duplicated or misplaced pauses.

Lane 5's `check_event` from [draft PR #1](https://github.com/crasni/LeCoach/pull/1) accepted all 214 fixture events. These results verify synthetic artifacts and the check utility only. They do not verify microphone capture, transcription accuracy, latency, or a live adapter.

FACT: The official SalesKit in `docs/` lists Whisper-Tiny, Whisper-Base and Whisper-Small as runnable on the UGen300 (Hailo-10H) SKUs through the Hailo GenAI Model Zoo (PDF pages 7, 8 and 15). External reports say Whisper often omits filler words and can produce text on silence or noise; sources are in the README. None of this has been run or measured locally or on UGen300.

IMPACT: Lanes 4 and 5 can develop against realistic speech streams before the live adapter exists, including pace, fillers, pauses, unavailable input, and null versus zero. AUD-01 remains blocked on INT-01's scaffold, configuration location, and executable contract and replay seam. No production speech adapter, capture code, or dependency was added. Filler counts from standard Whisper output may be undercounts, so filler-driven reactions depend on AUD-02 measurements.

PROPOSAL: The integration owner reviews the claim, the fixture placement, and the proposed v0 speech rules and open questions in the README: pause-completion events, leading silence, null reasons, configuration, analysis language, and model-failure status. After INT-01 lands, Lane 2 implements microphone capture → voice activity detection → local Whisper with word timestamps in the approved layout. Recorded sessions are then checked with `check_speech.py --stream`, and AUD-02 measures latency and filler recall per model size before any claim is made.
