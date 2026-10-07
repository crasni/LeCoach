# LeCoach

Your Private AI Audience.

LeCoach is a local, multimodal presentation coach for the ASUS UGen AI League Hackathon 2026. It combines speech and body-language signals to make a virtual audience react in real time, then highlights specific moments and practical improvements after each rehearsal.

## MVP

- Local speech transcription, speaking pace, fillers, and pauses.
- Webcam-based pose, approximate facing direction, and gesture activity.
- A deterministic engagement engine with smooth audience reactions.
- A synchronized session timeline and concise, actionable feedback.

Target track: Workplace AI / Battlefield Lightning, with ASUS UGen300 as the intended accelerator. Hardware integration and performance remain to be validated.

## Project status

Repository bootstrap. No application implementation or setup commands yet.

Start at [AGENTS.md](AGENTS.md), the shared entry point for all five collaborators. Follow the canonical documents linked there:

- [GUIDE.md](GUIDE.md): agreed product scope and priorities.
- [TASKS.md](TASKS.md): five workstreams, assignments, dependencies, and progress.
- [Architecture](docs/ARCHITECTURE.md): shared event contracts.
- [Implementation status](docs/STATUS.md): tested behavior and current blockers.
- [Role handoffs](docs/AGENT_ROLES.md): the prompt for each agent.

Official competition and hardware reference PDFs are in [docs/](docs/).

## Development

Inspect current code and task assignments before starting work. Keep subsystem interfaces explicit, changes scoped, and documentation current. Prioritize a reliable end-to-end MVP and demo before optional features.
