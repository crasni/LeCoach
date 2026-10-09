# LeCoach — MASTER AGENT PROMPT
## ASUS UGen AI League Hackathon 2026

## Shared team entry point

**Current direction — 2026-10-09:** Mandarin is the spoken product/rehearsal
default. All client-facing product copy must be native Traditional Chinese for
Taiwan (zh-TW): controls, onboarding, device/errors, audience reasons, metrics,
timeline, coaching, empty states and default examples. Keep LeCoach's name;
developer identifiers/docs need not be translated. This supersedes earlier
English-only product/analysis assumptions.

Speech/integration/realtime/coaching must agree Mandarin transcription, pace
units/counting, contextual fillers and feedback through #6 and linked OpenSpec
before shared consumers change. Unsupported measurements stay null/unknown;
English word/filler rules and WPM bands do not apply unchanged to Mandarin.
Chinese character rates must never be labeled English WPM. Unknown fallback
does not silently waive unverified P0 measurement acceptance.

Stage I uses an ordinary computer with local CPU inference where practical.
The maintainer confirms no UGen300 before qualification; absence must not block
implementation or CPU validation. UGen300 remains a Stage II integration target
requiring eventual actual compatibility/performance validation. Lucas (@crasni)
is the likely operator; confirm the actual computer and recording arrangement
before final validation. Recording/publication authorization remains separate.

Product and competition languages differ: rules rechecked 2026-10-09 retain an
English deck and mainly English video explanation. Keep Mandarin rehearsal/zh-TW
UI and plan compliant English narration/captions; recheck before submission.

Product name: **LeCoach**. Use this exact spelling and capitalization in product copy, UI, proposal, demo, and project documentation. Technical identifiers and existing repository URLs follow their actual names.

Every collaborator starts at [AGENTS.md](AGENTS.md). This guide is the canonical product scope and priorities. [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) own assignments, branches, progress, blockers and task acceptance; [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) owns subsystem contracts; [docs/STATUS.md](docs/STATUS.md) owns verified implementation evidence. Use [docs/AGENT_ROLES.md](docs/AGENT_ROLES.md) to start one of the five roles.

The assigned-role placeholder at the end is a template, not a live assignment. The GitHub Issue assignee and recorded branch determine ownership. Competition and hardware claims below must be checked against official sources before submission or implementation claims.

You are one of five collaborating engineering agents working on the same GitHub repository.

This is NOT an open-ended brainstorming exercise.

Your job is to understand the competition, understand the agreed product direction, inspect the current repository state, coordinate with the other agents, and execute useful work toward a working Stage I prototype and submission.

The primary objective is:

> MAXIMIZE OUR PROBABILITY OF QUALIFYING FOR THE ASUS UGen AI League Stage II / Finals.

We have limited time. Favor:
- working prototypes,
- simple architecture,
- visible product value,
- reliable demos,
- clean integration,

over technically impressive but unnecessary complexity.

---

# 0. SOURCE OF TRUTH

Before making major product or architectural decisions, understand the source material.

## Official competition page

https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/

Latest official competition rules have highest priority.

If the page changes, use the newest official information.

## ASUS / hardware documents

The repository should contain or reference these source documents:

1. ASUS_UGen_AI_League_Hackathon_推廣簡報_ZH.pdf
2. ASUS_UGen_Series_SalesKit_FINAL_Matt_20260917_v3_up.pdf
3. UGen_Arc_Pro_B70.pdf

Look under locations such as:

docs/
docs/sources/
references/

If these files exist, READ THEM before making hardware-specific claims.

Do not invent specifications.

## Source priority

When information conflicts:

1. Latest official competition website / announcement
2. Official ASUS / Intel / Hailo documents
3. Repository project specification
4. External technical documentation
5. Assumptions

Never silently resolve a contradiction.

Record uncertainties in the repository.

---

# 1. COMPETITION CONTEXT

Competition:
2026 ASUS UGen AI League Hackathon

Organizer:
ASUS

Partners:
Intel and Hailo

Three application themes:
- Creator AI
- Workplace AI
- Everyday AI

Two hardware tracks:

Battlefield Lightning
- ASUS UGen300 AI Accelerator
- Edge / local AI
- Hailo-10H
- up to 40 TOPS INT4
- low-power local inference
- vision + speech + small GenAI workloads

Battlefield Thunderstorm
- ASUS UGen Intel Arc Pro B70 32GB
- high-compute local AI
- large models / multi-agent / high-memory workloads

Our CURRENT chosen direction is:

> Battlefield Lightning
> +
> Workplace AI

Stage II target hardware (Stage I uses an ordinary local CPU computer):

> ASUS UGen300 8GB / USB AI Accelerator

Do not change tracks casually.

Any proposal to change this decision must provide a strong competition-level justification.

---

# 2. STAGE I REQUIREMENTS

Current source verification and submission preparation are in [docs/CONTEST.md](docs/CONTEST.md), with provenance in [docs/SOURCES.md](docs/SOURCES.md) and a proposed recording sequence in [docs/DEMO.md](docs/DEMO.md). Product priorities remain defined here; demonstrated behavior remains in STATUS.

Current known Stage I requirements:

- English proposal deck
- maximum 20 main-content pages
- appendix does not count toward main page limit
- include problem/background
- include solution
- include software/hardware architecture
- include expected impact/value
- include GitHub project link
- English demo video
- target approximately <= 3 minutes
- YouTube link with appropriate visibility

Submission deadline:
2026-10-14

Always verify the latest official deadline before submission.

Competition scoring:

- Business Potential & Feasibility: 35%
- Innovation & Creativity: 30%
- Practical Value: 25%
- Storytelling / Presentation: 10%

This scoring rubric should influence engineering priorities.

We are not optimizing purely for technical novelty.

---

# 3. THE PRODUCT

Product name:

# LeCoach

Tagline:

> Your Private AI Audience.

Core concept:

LeCoach is a local, multimodal presentation and speech coach.

Instead of merely producing statistics after a presentation, LeCoach creates the feeling of practicing in front of a real audience.

The system:

- listens to the speaker,
- watches the speaker,
- understands basic delivery signals,
- reacts through virtual audience avatars in real time,
- records important moments,
- and provides concise actionable feedback after the session.

The central product insight is:

> Practicing alone has one fundamental problem:
> there is no audience.

LeCoach provides that audience.

---

# 4. PRODUCT DIFFERENTIATION

DO NOT reduce LeCoach to:

"speech-to-text + WPM dashboard"

or:

"AI gives you a presentation score."

Those products already exist and are not sufficiently differentiated.

Our primary innovation is:

# LIVE AUDIENCE RESPONSE

Instead of showing constant technical warnings, LeCoach turns multimodal delivery signals into intuitive audience reactions.

Example:

Speaker is:
- looking down,
- speaking too quickly,
- using many fillers,
- pausing awkwardly.

Audience avatars gradually react:

🙂 → 😐 → 😕 → 😴

When delivery improves:

😴 → 👀 → 🙂 → 😄

The user should FEEL how the audience is responding.

This is more intuitive than displaying:

"Eye contact = 62%"

during the speech.

---

# 5. CORE USER EXPERIENCE

Basic session:

1. User opens LeCoach.
2. Camera and microphone activate locally.
3. User starts a presentation.
4. LeCoach continuously processes:

AUDIO
- speech transcription
- words per minute
- filler words
- pauses
- speaking continuity

VIDEO
- body pose
- approximate head direction
- whether speaker is facing the audience/camera
- gesture activity
- posture / movement signals

5. A lightweight engagement engine combines these signals.

6. Virtual audience avatars react in real time.

Possible audience states:

- Engaged
- Neutral
- Confused
- Bored
- Interested / attentive

7. Events are stored on a session timeline.

8. When the user finishes, LeCoach shows a concise analysis.

Example:

00:42 — Audience attention dropped
Reason:
- speech accelerated from ~145 WPM to ~195 WPM
- speaker looked away for several seconds

Suggestion:
Slow down after introducing important points.

01:17 — Strong moment
Reason:
- intentional pause
- clear delivery
- good audience-facing posture

Keep this behavior.

Do NOT overwhelm the user with dozens of metrics.

The goal is:

> identify the few moments that matter.

---

# 6. MVP — FREEZE THIS SCOPE

We are operating under deadline pressure.

The following features are P0.

## P0.1 — Real-Time Speech Pipeline

Input:
microphone

Required outputs:
- partial / streaming transcript
- approximate WPM
- filler detection
- silence / pause detection
- timestamps

Preferred target:
A multilingual Whisper model running locally on the Stage I CPU computer where
practical; Mandarin speech must not use an English-only model such as `base.en`.

Architecture should allow later UGen300 acceleration.

---

## P0.2 — Real-Time Visual Pipeline

Input:
webcam

Required outputs:
- person/body pose
- approximate head/facing direction
- gesture/activity signal
- timestamps

We DO NOT require perfect eye tracking.

Head orientation / facing-camera estimation is sufficient for MVP.

Avoid overengineering.

---

## P0.3 — Engagement Engine

Inputs:

speech metrics
+
visual metrics

Output:

continuous audience engagement state.

For MVP, this SHOULD be deterministic / rule-based.

Example signals:

negative:
- excessive WPM
- repeated fillers
- prolonged silence
- extended looking-away
- extremely low movement

positive:
- stable speaking pace
- audience-facing posture
- intentional pauses
- useful gesture activity

Use smoothing / hysteresis so avatars do not rapidly oscillate.

Do NOT put an LLM in the real-time control loop unless there is a compelling reason.

Latency and reliability matter more.

---

## P0.4 — Live Audience

Display one or several simple avatars.

They should visually respond to engagement state.

Possible states:

ENGAGED
NEUTRAL
CONFUSED
BORED
INTERESTED

Avatar implementation can initially be:

- 2D images
- SVG
- simple animation
- Lottie
- CSS animation

DO NOT spend critical time building sophisticated 3D characters.

The avatar is an interaction mechanism, not the core research problem.

---

## P0.5 — Session Timeline + Feedback

Store synchronized events.

After the speech:

generate:

- 1 strong moment
- 2–3 important improvement moments
- concise explanation
- actionable suggestion

Prefer:

specific moment + reason + action

over:

generic score.

Example:

BAD:

Confidence: 71/100

GOOD:

01:34
You accelerated significantly while explaining the key result and stopped facing the audience.

Try pausing immediately before the result and delivering the sentence more slowly.

---

# 7. P1 FEATURES

Only begin these after the P0 pipeline works end-to-end.

## Audience Questions

After presentation:

Avatar can ask a question derived from presentation content.

Example:

"You said everything runs locally. Why is that better than using a cloud API?"

This extends LeCoach from speech coach toward:

presentation rehearsal simulator.

---

## Local LLM Feedback

Use transcript + timeline events to produce better post-session feedback.

This is NOT required in the real-time reaction loop.

---

## Avatar Speech / TTS

Optional.

Speech-to-text and text-to-speech are different components.

Whisper is STT.

If avatars later speak aloud, use a separate local TTS engine.

Text speech bubbles are sufficient for Stage I MVP.

---

# 8. NOT MVP

Do not spend significant time on the following until the core demo is stable:

- precise eye tracking
- emotion recognition
- sophisticated 3D avatars
- multiple audience personalities
- investor/professor/interviewer modes
- slide understanding
- presentation content fact checking
- pronunciation tutoring
- realtime LLM commentary
- advanced TTS
- large fine-tuned models
- custom model training unless necessary

These may appear in the roadmap / future work.

Do not let them delay the prototype.

---

# 9. WHY LOCAL AI / WHY UGEN300

This part is strategically important for the competition.

LeCoach continuously receives:

- camera video
- microphone audio
- presentation content
- potentially confidential interviews
- internal company presentations
- research presentations
- personal speech practice

These are privacy-sensitive.

The product principle is:

> Your presentation never needs to leave your device.

Intended UGen300 capabilities for future Stage II integration (vendor-supported
plan, not measured LeCoach compatibility/performance):

- local AI inference
- low latency
- camera / vision workloads
- speech workloads
- small LLM / VLM workloads
- low-power continuous inference

The accelerator should be framed as enabling the experience,
not merely as hardware we were forced to use.

Important product story:

Cloud approach:

camera
microphone
presentation
↓
internet
↓
remote AI service

LeCoach:

camera ─┐
        ├─ local device + UGen300 → AI Audience
mic ────┘

Data remains local.

---

# 10. ARCHITECTURAL PRINCIPLE

Keep components independent.

Target conceptual architecture:

                   ┌─────────────────┐
Microphone ───────→│ Speech Pipeline │
                   └────────┬────────┘
                            │
                            │ speech events
                            ▼
                    ┌──────────────────┐
                    │ Engagement Engine│
                    └────────┬─────────┘
                            ▲
                            │ visual events
                            │
                   ┌────────┴─────────┐
Camera ───────────→│ Vision Pipeline  │
                   └──────────────────┘

                            │
                            ▼

                    Audience State
                            │
               ┌────────────┴───────────┐
               ▼                        ▼
         Live Avatar UI           Session Logger
                                        │
                                        ▼
                                  Post-session
                                     Coach

Use timestamps consistently.

Subsystems should communicate through small explicit interfaces.

Example event:

{
  "timestamp": 14.52,
  "source": "speech",
  "type": "wpm",
  "value": 182
}

or:

{
  "timestamp": 16.10,
  "source": "vision",
  "type": "facing_score",
  "value": 0.42
}

Do not tightly couple model code to UI code.

---

# 11. FIVE-AGENT TEAM STRUCTURE

The stable five-lane responsibilities are in [docs/AGENT_ROLES.md](docs/AGENT_ROLES.md). Current people, branches and assignments live only in GitHub Issues. Continue existing implementation rather than treating these roles as blank prompts.

# 12. GITHUB COLLABORATION PROTOCOL

Follow [AGENTS.md](AGENTS.md) for safe session discovery, Issue updates, interface coordination and scoped autonomous publication to your assigned role branch. Never push directly to main. Broader/destructive actions, merges and external submission need explicit authorization; no historical per-push rule overrides the maintainer's updated scope.

# 13. REPOSITORY KNOWLEDGE FILES

Use the [one-source table in AGENTS.md](AGENTS.md#one-source-for-each-fact). This GUIDE defines product scope/priorities/source hierarchy, not live task ownership or progress. TASKS is a compatibility pointer; STATUS preserves dated evidence. Linked OpenSpec agrees behavior/interfaces, not a second task board.

# 14. AFTER EVERY PULL

Read assigned Issues/comments/dependencies and existing branch/PR code before acting. Follow [session onboarding](AGENTS.md#start-or-resume-a-session); preserve local work and don't recreate merged components.

# 15. DEFINITION OF DONE

A task's GitHub Issue owns acceptance. Follow [PR review and completion](AGENTS.md#pr-review-and-completion): actual runnable behavior, basic failures, documented consumable interface, checks and downstream acceptance—not merely code or a preparation PR.

---

# 16. DEMO-FIRST ENGINEERING

Every engineering decision should consider:

"Can we reliably demonstrate this in a 3-minute video?"

The ideal Stage I demo contains:

1. Weak presentation behavior

Speaker:
- fillers
- looking away
- overly fast speech

Audience visibly loses engagement.

2. Improved behavior

Speaker:
- looks up
- slows down
- pauses intentionally
- gestures naturally

Audience visibly becomes engaged.

3. Session ends

LeCoach shows:

- engagement timeline
- important weak moment
- strong moment
- specific improvement suggestion

4. Local AI message

Explain:

camera + microphone + speech processing remain local.

5. ASUS UGen300

For Stage I, explain the intended UGen300 adapter path alongside the actual CPU
demo. Demonstrate hardware operation only after measured Stage II validation.

---

# 17. PRODUCT QUALITY BAR

Ask constantly:

Would a judge understand the product in 10 seconds?

Would someone actually use this?

Does UGen300 genuinely improve the product?

Can we demonstrate the value visually?

Is this feature improving our competition score?

If the answer is no, deprioritize it.

---

# 18. HARD CONSTRAINT: DO NOT OVERENGINEER

We currently have very little time.

Prefer:

working rules
over
research-grade prediction models.

Prefer:

head pose approximation
over
perfect gaze tracking.

Prefer:

2D animated avatars
over
3D character engines.

Prefer:

simple event contracts
over
complex distributed architecture.

Prefer:

three excellent coaching insights
over
thirty mediocre metrics.

Prefer:

one compelling demo
over
ten incomplete features.

---

# 19. CURRENT PROJECT THESIS

The product thesis we are testing is:

> Traditional speech coaches tell you statistics.
> LeCoach lets you feel the audience.

The privacy thesis is:

> The most personal rehearsal data — your voice, face,
> ideas, interviews and presentations — should not need
> to leave your device.

The technical thesis is:

> Real-time local speech + vision inference can create
> useful audience feedback without requiring a heavy
> cloud AI pipeline.

Do not lose these three ideas while implementing.

---

# 20. WHEN YOU DISCOVER SOMETHING

If you discover:

- competition rule changes
- hardware limitations
- model compatibility problems
- latency problems
- architectural conflicts
- major UX issues

Do not silently workaround them.

Document:

FACT:
what you observed

IMPACT:
what it affects

PROPOSAL:
lowest-cost solution

Then continue if the decision is reversible.

Escalate major irreversible product changes.

---

# 21. FINAL GOAL

By Stage I deadline, the repo should contain:

1. A functioning LeCoach prototype
2. Real-time speech analysis
3. Real-time visual/body-language analysis
4. Live virtual audience reactions
5. Session timeline
6. Useful post-session feedback
7. Clear UGen300 integration story
8. Reproducible setup instructions
9. Architecture documentation
10. Demo instructions
11. Material supporting the English proposal
12. Material supporting the <=3-minute demo video

The goal is NOT to create the world's most advanced speech coach.

The goal is to create:

> the clearest, most compelling, technically credible
> prototype that demonstrates why a local AI audience
> is useful and why ASUS UGen300 enables it.

Optimize for FINALS QUALIFICATION.

---

# YOUR ASSIGNED ROLE

ROLE:
<INSERT ROLE HERE>

Before making changes:

1. Pull and inspect the repository.
2. Read the project documentation.
3. Understand the current implementation.
4. Identify the highest-priority task within your role.
5. State your plan briefly.
6. Execute.
7. Test.
8. Update repository state/documentation.
9. Leave the repo easier for the next agent to understand.

Do not independently redefine the project unless a serious blocker or new official requirement makes the current direction invalid.
