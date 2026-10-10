"""English word and filler rules for speech metrics, plus capture-time attribution.

`checks/speech/speech_text.py` keeps a standard-library copy of these rules so the
standalone checker runs without installing the package; a parity test keeps the
two identical. The rules apply to finalized text only and are demo heuristics,
not validated measures.
"""

import re
from collections.abc import Sequence
from typing import NamedTuple

# Bracketed or parenthesized annotations such as "[BLANK_AUDIO]" or
# "(applause)" are not speech.
_ANNOTATION = re.compile(r"\[[^\]]*\]|\([^)]*\)")
# Clause punctuation. A period followed by a digit stays inside a number.
_CLAUSE_BREAK = re.compile(r"[,;:!?…—–\"“”]|\.(?!\d)")
# Letters/digits with internal apostrophes, hyphens, or periods count as one
# token: "don't", "real-time", "3.5", "UGen300".
_TOKEN = re.compile(r"[^\W_]+(?:['’.\-][^\W_]+)*")
# Non-lexical hesitations, including stretched spellings: um, uhh, erm, ahh,
# hmm, mhm, eh. They are fillers and are excluded from WPM.
_HESITATION = re.compile(r"(?:u+m+|u+h+m*|e+r+m*|a+h+|h+m+|m+h*m+|e+h+)")
# Discourse markers count as fillers only when punctuation sets them off as a
# whole clause ("It was, like, fast"; "You know, it works"), so "I like it" or
# "Do you know?" are not fillers. They still count as words.
FILLER_CLAUSES = (("like",), ("you", "know"), ("i", "mean"))


class TimedToken(NamedTuple):
    """A spoken token attributed to the capture time at which it ends."""

    at_s: float
    counts_as_word: bool
    ends_filler: bool


def is_hesitation(token: str) -> bool:
    return _HESITATION.fullmatch(token) is not None


def spoken_tokens(text: str) -> list[tuple[str, bool, bool]]:
    """Return (token, counts_as_word, ends_filler) tuples in spoken order."""
    result = []
    for clause in _CLAUSE_BREAK.split(_ANNOTATION.sub(" ", text)):
        tokens = _TOKEN.findall(clause.lower())
        lexical = [index for index, token in enumerate(tokens) if not is_hesitation(token)]
        marker_end = (
            lexical[-1] if tuple(tokens[i] for i in lexical) in FILLER_CLAUSES else None
        )
        for index, token in enumerate(tokens):
            hesitation = is_hesitation(token)
            result.append((token, not hesitation, hesitation or index == marker_end))
    return result


def word_count(text: str) -> int:
    return sum(1 for _, counts_as_word, _ in spoken_tokens(text) if counts_as_word)


def filler_count(text: str) -> int:
    return sum(1 for _, _, ends_filler in spoken_tokens(text) if ends_filler)


def even_tokens(text: str, start_s: float, end_s: float) -> list[TimedToken]:
    """Spread tokens evenly across an utterance; the last ends at its end."""
    tokens = spoken_tokens(text)
    step = (end_s - start_s) / max(len(tokens), 1)
    return [
        TimedToken(end_s if index == len(tokens) - 1 else start_s + (index + 1) * step,
                   counts_as_word, ends_filler)
        for index, (_, counts_as_word, ends_filler) in enumerate(tokens)
    ]


def timed_tokens(
    words: Sequence[tuple[str, float]], start_s: float, end_s: float
) -> list[TimedToken]:
    """Attribute tokens to model word end times, already mapped to capture time.

    `words` are the model's word pieces in order, as (text, end_s). Clause-level
    filler rules run on their concatenation. If the pieces do not align with
    the tokenizer, tokens fall back to an even spread across the utterance.
    """
    text = "".join(word for word, _ in words)
    tokens = spoken_tokens(text)
    times: list[float] = []
    for word, at_s in words:
        pieces = _TOKEN.findall(_ANNOTATION.sub(" ", word).lower())
        times.extend([min(max(at_s, start_s), end_s)] * len(pieces))
    if len(times) != len(tokens):
        return even_tokens(text, start_s, end_s)
    return [TimedToken(at_s, counts_as_word, ends_filler)
            for at_s, (_, counts_as_word, ends_filler) in zip(times, tokens)]
