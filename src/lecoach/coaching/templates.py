"""Plain-language descriptions of recorded reasons; no audience-rule thresholds."""

from lecoach.contracts import Event

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
        label = "fast" if code == "pace_high" else "slow"
        action = (
            "Pause after key points and rehearse this passage at a slower pace."
            if code == "pace_high"
            else "Rehearse this passage in shorter phrases with fewer gaps between ideas."
        )
        return (
            f"The simulated audience flagged a {label} passage; cited speech windows "
            f"were approximately {pace} WPM.",
            action,
        )
    if code == "fillers_frequent":
        rate = observed_range([event.payload.filler_rate_per_min for event in measurements])
        return (
            f"The audience's filler-related reaction cited approximately {rate} fillers per minute "
            "in finalized speech windows.",
            "Rehearse this passage with a brief silent breath "
            "where you would otherwise use a filler.",
        )
    if code == "silence_prolonged":
        duration = observed_range([event.payload.pause.duration_s for event in measurements])
        return (
            f"A recorded active pause had reached {duration} seconds in the audience's evidence. "
            "The recording does not establish whether the pause was intentional.",
            "Rehearse the transition between these points "
            "and prepare the next sentence before pausing.",
        )
    facing = observed_range([event.payload.facing_score for event in measurements])
    return (
        f"The audience's facing-away reaction cited approximate head/body facing estimates of "
        f"{facing} out of 1; this is not eye tracking.",
        "Look toward the camera while delivering the next key sentence; place notes closer to it.",
    )


def strength(codes: set[str], measurements: list[Event]) -> tuple[str, str]:
    observations = []
    actions = []
    if "pace_steady" in codes:
        pace = observed_range(
            [event.payload.wpm for event in measurements if event.source == "speech"]
        )
        observations.append(f"speech windows were approximately {pace} WPM")
        actions.append("a similarly steady speaking pace")
    if "facing_audience" in codes:
        facing = observed_range(
            [event.payload.facing_score for event in measurements if event.source == "vision"]
        )
        observations.append(f"head/body facing estimates were approximately {facing} out of 1")
        actions.append("a similar orientation toward the camera")
    return (
        "The simulated audience reached ENGAGED; in its cited observations, "
        + " and ".join(observations)
        + ".",
        "Rehearse your next key point with " + " and ".join(actions) + ".",
    )
