from __future__ import annotations

import re
from collections import Counter

from .schemas import CandidateTerm

STOP_ACRONYMS = {
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HAD", "HER",
    "WAS", "ONE", "OUR", "OUT", "DAY", "GET", "HAS", "HIM", "HIS", "HOW", "ITS",
    "MAY", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY", "DID", "LET", "PUT",
    "SAY", "SHE", "TOO", "USE", "PDF", "HTTP", "HTTPS", "URL", "JSON", "HTML",
    "CSS", "UTC", "GMT", "AM", "PM", "ID", "OK", "US"
}

STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "into", "onto", "over",
    "under", "about", "after", "before", "between", "within", "without", "their",
    "there", "these", "those", "have", "has", "had", "were", "was", "been", "being",
    "are", "is", "a", "an", "of", "to", "in", "on", "at", "by", "or", "as", "we",
    "our", "your", "you", "they", "them", "it", "its",
}


def _context_window(text: str, term: str, radius: int = 60) -> str:
    idx = text.find(term)
    if idx < 0:
        # case-insensitive fallback
        lower = text.lower()
        idx = lower.find(term.lower())
        if idx < 0:
            return text[:120]
    start = max(0, idx - radius)
    end = min(len(text), idx + len(term) + radius)
    snippet = text[start:end].replace("\n", " ")
    return snippet.strip()


def extract_acronyms(text: str) -> list[CandidateTerm]:
    found: dict[str, CandidateTerm] = {}
    # Explicit expansion: Written Assessment of Risk (WAR)
    for match in re.finditer(
        r"\b([A-Z][A-Za-z0-9](?:[A-Za-z0-9 /&-]{2,80}?))\s*\(([A-Z]{2,6})\)",
        text,
    ):
        expansion, acr = match.group(1).strip(), match.group(2)
        if acr in STOP_ACRONYMS:
            continue
        found[acr] = CandidateTerm(
            term=acr,
            kind="acronym",
            definition=f"{expansion} ({acr})",
            confidence=0.75,
            context=_context_window(text, acr),
            aliases=[expansion],
        )
    for match in re.finditer(r"\b([A-Z]{2,6})\b", text):
        acr = match.group(1)
        if acr in STOP_ACRONYMS:
            continue
        if acr not in found:
            found[acr] = CandidateTerm(
                term=acr,
                kind="acronym",
                definition="",
                confidence=0.55,
                context=_context_window(text, acr),
            )
    return list(found.values())


def extract_camel_case(text: str) -> list[CandidateTerm]:
    out: list[CandidateTerm] = []
    seen: set[str] = set()
    for match in re.finditer(r"\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b", text):
        term = match.group(1)
        if term in seen:
            continue
        seen.add(term)
        out.append(
            CandidateTerm(
                term=term,
                kind="camelcase",
                definition="",
                confidence=0.5,
                context=_context_window(text, term),
            )
        )
    return out


def extract_capitalized_entities(text: str) -> list[CandidateTerm]:
    out: list[CandidateTerm] = []
    seen: set[str] = set()
    for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b", text):
        term = match.group(1)
        # skip sentence starters that are common
        words = term.split()
        if all(w.lower() in STOP_WORDS for w in words):
            continue
        if term in seen:
            continue
        seen.add(term)
        out.append(
            CandidateTerm(
                term=term,
                kind="entity",
                definition="",
                confidence=0.45,
                context=_context_window(text, term),
            )
        )
    return out


def extract_repeated_noun_phrases(text: str, min_freq: int = 2) -> list[CandidateTerm]:
    # Lightweight bigram/trigram of Title Case or lowercase content words
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9-]*", text)
    phrases: list[str] = []
    for n in (2, 3):
        for i in range(len(tokens) - n + 1):
            window = tokens[i : i + n]
            if any(t.lower() in STOP_WORDS for t in window):
                continue
            if not any(t[0].isupper() for t in window):
                continue
            phrases.append(" ".join(window))
    counts = Counter(phrases)
    out: list[CandidateTerm] = []
    for phrase, freq in counts.items():
        if freq < min_freq:
            continue
        out.append(
            CandidateTerm(
                term=phrase,
                kind="noun_phrase",
                definition="",
                confidence=min(0.4 + 0.1 * freq, 0.8),
                context=_context_window(text, phrase),
            )
        )
    return out


def dedupe_score(candidates: list[CandidateTerm]) -> list[CandidateTerm]:
    best: dict[str, CandidateTerm] = {}
    kind_priority = {"acronym": 4, "camelcase": 3, "entity": 2, "noun_phrase": 1, "other": 0}
    for cand in candidates:
        key = cand.term.strip().lower()
        if not key:
            continue
        prev = best.get(key)
        if prev is None:
            best[key] = cand
            continue
        # keep higher confidence; break ties with kind priority and prefer non-empty definition
        score_new = (cand.confidence, kind_priority.get(str(cand.kind), 0), 1 if cand.definition else 0)
        score_old = (prev.confidence, kind_priority.get(str(prev.kind), 0), 1 if prev.definition else 0)
        if score_new >= score_old:
            # merge aliases
            aliases = list(dict.fromkeys((prev.aliases or []) + (cand.aliases or [])))
            merged = cand.model_copy(update={"aliases": aliases, "definition": cand.definition or prev.definition})
            best[key] = merged
    return sorted(best.values(), key=lambda c: (-c.confidence, c.term.lower()))


def extract_candidates(text: str, noun_phrase_min_freq: int = 2) -> list[CandidateTerm]:
    # Normalize newlines so markdown headings don't glue into phrases
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    raw = (
        extract_acronyms(text)
        + extract_camel_case(text)
        + extract_capitalized_entities(text)
        + extract_repeated_noun_phrases(text, min_freq=noun_phrase_min_freq)
    )
    # Drop junk spanning line breaks
    cleaned = [c for c in raw if "\n" not in c.term and len(c.term.strip()) >= 2]
    return dedupe_score(cleaned)
