from __future__ import annotations

import httpx

from .config import get_settings
from .schemas import CandidateTerm
from .seed import TEAM_SEEDS
from .text_chunk import chunk_text


def mock_candidates_for_team(team_id: str) -> list[CandidateTerm]:
    items = TEAM_SEEDS.get(team_id, TEAM_SEEDS["default"])
    out: list[CandidateTerm] = []
    for i, item in enumerate(items):
        out.append(
            CandidateTerm(
                term=item["term"],
                kind=item.get("kind", "acronym"),
                definition=item["definition"],
                confidence=0.92 - (i * 0.01),
                context=f"Extracted from uploaded document ({item['term']})",
            )
        )
    return out


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


async def extract_candidates(text: str, *, team_id: str = "default") -> list[CandidateTerm]:
    settings = get_settings()
    if settings.use_mock_nlp:
        return mock_candidates_for_team(team_id)

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
        return mock_candidates_for_team(team_id)
