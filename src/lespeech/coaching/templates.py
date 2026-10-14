"""Plain-language descriptions of recorded reasons; no audience-rule thresholds."""

from lespeech.contracts import Event

# This consumer vocabulary follows ARCHITECTURE.md / LIVE-01's published handoff.
REASON_SOURCES = {
    "pace_high": "speech",
    "pace_low": "speech",
    "fillers_frequent": "speech",
    "silence_prolonged": "speech",
    "facing_away_sustained": "vision",
    "pace_steady": "speech",
    "facing_audience": "vision",
}
POSITIVE_CODES = frozenset({"pace_steady", "facing_audience"})


def usable_measurement(code: str, event: Event) -> bool:
    source = REASON_SOURCES[code]
    if event.type != f"{source}.metrics" or event.payload.availability != "available":
        return False
    p = event.payload
    if source == "vision":
        return p.person_present is True and p.pose_available is True and p.facing_score is not None
    if code == "fillers_frequent":
        return p.filler_rate_per_min is not None and p.filler_rate_per_min > 0
    if code == "silence_prolonged":
        return (
            p.pause.state == "active" and p.pause.duration_s is not None and p.pause.duration_s > 0
        )
    return p.wpm is not None and p.wpm > 0


def observed_range(values: list[float]) -> str:
    low, high = min(values), max(values)
    return f"{low:g}" if low == high else f"{low:g}–{high:g}"


def improvement(code: str, measurements: list[Event]) -> tuple[str, str]:
    if code in ("pace_high", "pace_low"):
        pace = observed_range([event.payload.wpm for event in measurements])
        label = "fast" if code == "pace_high" else "slowly"
        action = (
            "Slow down and pause after each key point."
            if code == "pace_high"
            else "Join short phrases together and pause only between ideas."
        )
        return (
            f"You were talking {label} here, at about {pace} words per minute.",
            action,
        )
    if code == "fillers_frequent":
        rate = observed_range([event.payload.filler_rate_per_min for event in measurements])
        return (
            f"The transcript suggests about {rate} filler words (like “um”) per minute here.",
            "Take a short, silent breath instead of saying a filler word.",
        )
    if code == "silence_prolonged":
        duration = max(event.payload.pause.duration_s for event in measurements)
        return (
            f"You were silent for at least {duration:g} seconds. "
            "We cannot tell whether it was planned.",
            "Have your next sentence ready before you pause.",
        )
    return (
        "You seemed to stay turned away from the camera here.",
        "Face the camera for your next key line. Keep your notes next to it.",
    )


def strength(codes: set[str], measurements: list[Event]) -> tuple[str, str]:
    observations = []
    if "pace_steady" in codes:
        pace = observed_range(
            [event.payload.wpm for event in measurements if event.source == "speech"]
        )
        observations.append(f"Your pace stayed around {pace} words per minute")
    if "facing_audience" in codes:
        observations.append("you seemed to keep facing the camera")
    if len(observations) == 2:
        action = "Keep this pace and keep facing the camera."
    elif "pace_steady" in codes:
        action = "Keep this same pace."
    else:
        action = "Keep facing the camera."
        observations[0] = observations[0].capitalize()
    return (
        " and ".join(observations) + ".",
        action,
    )
