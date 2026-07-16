from __future__ import annotations

import json
import re
from typing import Any

import httpx

from .config import get_settings
from .schemas import CandidateTerm

HEURISTIC_DEFS: dict[str, str] = {
    "pir": "Post-Incident Review — meeting after a production incident to capture learnings.",
    "gtm": "Go-To-Market — plan and activities for launching a product or feature.",
    "bau": "Business As Usual — routine operations outside of incident response.",
    "slo": "Service Level Objective — target reliability or latency goal for a service.",
    "rfc": "Request for Comments — design proposal reviewed before large changes.",
    "okr": "Objectives and Key Results — goal-setting framework used each quarter.",
    "ciso": "Chief Information Security Officer.",
    "war": "Written Assessment of Risk.",
    "acr": "Azure Container Registry (or context-specific container registry acronym).",
    "ci": "Continuous Integration — automated build and test pipeline.",
    "ga": "General Availability — public production release of a product.",
    "mvp": "Minimum Viable Product — smallest useful shippable scope.",
    "qbr": "Quarterly Business Review.",
    "nfr": "Non-Functional Requirements — performance, security, reliability criteria.",
}


def _heuristic_definition(cand: CandidateTerm) -> str:
    if cand.definition:
        return cand.definition
    key = cand.term.lower()
    if key in HEURISTIC_DEFS:
        return HEURISTIC_DEFS[key]
    if cand.kind == "camelcase":
        parts = re.findall(r"[A-Z][a-z0-9]*", cand.term)
        if parts:
            return f"Team-specific term referring to {' '.join(parts).lower()} (inferred from CamelCase)."
    if cand.kind == "entity":
        return f"Named entity or proper noun used in team documentation: {cand.term}."
    if cand.kind == "noun_phrase":
        return f"Repeated domain phrase in team docs: {cand.term}."
    return f"Team-specific acronym or jargon: {cand.term}. (Needs lead review.)"


async def define_terms(candidates: list[CandidateTerm]) -> list[CandidateTerm]:
    settings = get_settings()
    if not candidates:
        return []

    # Always fill heuristics first; LLM upgrades when available
    base = [
        c.model_copy(
            update={
                "definition": _heuristic_definition(c),
                "confidence": c.confidence if c.definition else max(c.confidence, 0.4),
            }
        )
        for c in candidates
    ]

    if settings.openai_api_key or (settings.azure_openai_api_key and settings.azure_openai_endpoint):
        try:
            return await _llm_define(base)
        except Exception:
            return base
    return base


async def _llm_define(candidates: list[CandidateTerm]) -> list[CandidateTerm]:
    settings = get_settings()
    payload_terms = [
        {"term": c.term, "kind": c.kind, "context": c.context, "hint": c.definition}
        for c in candidates[:40]
    ]
    system = (
        "You extract team-specific jargon definitions from documentation context. "
        "Return ONLY valid JSON: {\"definitions\":[{\"term\":\"...\",\"definition\":\"...\","
        "\"confidence\":0.0,\"aliases\":[]}]}. "
        "Definitions must be concise (1-2 sentences), team-oriented, and grounded in context."
    )
    user = json.dumps({"terms": payload_terms})

    if settings.azure_openai_api_key and settings.azure_openai_endpoint:
        url = (
            settings.azure_openai_endpoint.rstrip("/")
            + f"/openai/deployments/{settings.azure_openai_deployment}/chat/completions?api-version=2024-08-01-preview"
        )
        headers = {"api-key": settings.azure_openai_api_key, "Content-Type": "application/json"}
        body: dict[str, Any] = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
    else:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        data = json.loads(content)
        by_term = {
            d["term"].strip().lower(): d
            for d in data.get("definitions", [])
            if isinstance(d, dict) and d.get("term")
        }

    out: list[CandidateTerm] = []
    for cand in candidates:
        hit = by_term.get(cand.term.lower())
        if not hit:
            out.append(cand)
            continue
        out.append(
            cand.model_copy(
                update={
                    "definition": hit.get("definition") or cand.definition,
                    "confidence": float(hit.get("confidence", cand.confidence) or cand.confidence),
                    "aliases": list(
                        dict.fromkeys((cand.aliases or []) + list(hit.get("aliases") or []))
                    ),
                }
            )
        )
    return out
