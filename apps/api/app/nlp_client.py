from __future__ import annotations

import httpx

from .config import get_settings
from .schemas import CandidateTerm
from .text_chunk import chunk_text


MOCK_CANDIDATES = [
    CandidateTerm(
        term="PIR",
        kind="acronym",
        definition="Post-Incident Review — meeting held after a production incident.",
        confidence=0.9,
        context="schedule a PIR within 48 hours",
    ),
    CandidateTerm(
        term="GTM",
        kind="acronym",
        definition="Go-To-Market — plan for launching a product or feature.",
        confidence=0.88,
        context="current GTM plan for the developer portal",
    ),
    CandidateTerm(
        term="BAU",
        kind="acronym",
        definition="Business As Usual — routine non-incident operations.",
        confidence=0.85,
        context="prefer BAU operations only for non-critical changes",
    ),
]


def _norm_term(term: str) -> str:
    return term.strip().lower()


def dedupe_candidates(candidates: list[CandidateTerm]) -> list[CandidateTerm]:
    best: dict[str, CandidateTerm] = {}
    for cand in candidates:
        key = _norm_term(cand.term)
        if not key:
            continue
        existing = best.get(key)
        if existing is None or cand.confidence >= existing.confidence:
            best[key] = cand
    return list(best.values())


async def _extract_chunk(client: httpx.AsyncClient, url: str, chunk: str) -> list[CandidateTerm]:
    resp = await client.post(url, json={"text": chunk})
    resp.raise_for_status()
    data = resp.json()
    items = data.get("candidates", data if isinstance(data, list) else [])
    return [CandidateTerm.model_validate(item) for item in items]


async def extract_candidates(text: str) -> list[CandidateTerm]:
    settings = get_settings()
    if settings.use_mock_nlp:
        return list(MOCK_CANDIDATES)

    url = settings.nlp_url.rstrip("/") + "/nlp/extract"
    chunks = chunk_text(text)
    if not chunks:
        return []

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            merged: list[CandidateTerm] = []
            for chunk in chunks:
                merged.extend(await _extract_chunk(client, url, chunk))
            return dedupe_candidates(merged)
    except Exception:
        # Graceful fallback so upload still works offline / before NLP is up
        return list(MOCK_CANDIDATES)
