"""Proposed v0 English word and filler rules for LeCoach speech metrics.

Lane 2 preparation artifact. ARCHITECTURE.md requires the speech adapter to
document its tokenizer, analysis language, and filler lexicon. The adapter
applies these rules to finalized transcript text only; partial revisions are
never counted. Review the rules with Lanes 1 and 4 before tuning pace or
filler thresholds. They are demo heuristics, not validated measures.
"""

import re


ANALYSIS_LANGUAGE = "en"

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


def is_hesitation(token):
    return _HESITATION.fullmatch(token) is not None


def spoken_tokens(text):
    """Return (token, counts_as_word, ends_filler) tuples in spoken order."""
    result = []
    for clause in _CLAUSE_BREAK.split(_ANNOTATION.sub(" ", text)):
        tokens = _TOKEN.findall(clause.lower())
        lexical = [index for index, token in enumerate(tokens) if not is_hesitation(token)]
        marker_end = lexical[-1] if tuple(tokens[i] for i in lexical) in FILLER_CLAUSES \
            else None
        for index, token in enumerate(tokens):
            hesitation = is_hesitation(token)
            result.append((token, not hesitation, hesitation or index == marker_end))
    return result


def word_count(text):
    return sum(1 for _, counts_as_word, _ in spoken_tokens(text) if counts_as_word)


def filler_count(text):
    return sum(1 for _, _, ends_filler in spoken_tokens(text) if ends_filler)
