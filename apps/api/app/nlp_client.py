from __future__ import annotations

import httpx

from .config import get_settings
from .schemas import CandidateTerm


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


async def extract_candidates(text: str) -> list[CandidateTerm]:
    settings = get_settings()
    if settings.use_mock_nlp:
        return list(MOCK_CANDIDATES)

    url = settings.nlp_url.rstrip("/") + "/nlp/extract"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json={"text": text})
            resp.raise_for_status()
            data = resp.json()
            items = data.get("candidates", data if isinstance(data, list) else [])
            return [CandidateTerm.model_validate(item) for item in items]
    except Exception:
        # Graceful fallback so upload still works offline / before NLP is up
        return list(MOCK_CANDIDATES)
