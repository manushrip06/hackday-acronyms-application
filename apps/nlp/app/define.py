from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

try:
    import boto3
except ImportError:  # pragma: no cover - optional dependency in tests
    boto3 = None

from .config import get_settings
from .schemas import CandidateTerm

logger = logging.getLogger(__name__)

# Known standard technical terms that should be filtered even without LLM
STANDARD_TECHNICAL_TERMS = {
    "s3", "lambda", "dynamodb", "api gateway", "cloudwatch", "ec2", "rds", "iam", "sns", "sqs",
    "github", "git", "docker", "kubernetes", "k8s", "aws", "azure", "gcp",
    "api", "http", "json", "sql", "database", "server", "client", "cache", "queue",
    "deploy", "deployment", "container", "image", "build", "test", "ci", "cd",
    "ingest", "process", "stream", "batch", "kafka", "rabbitmq", "redis",
}

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


def _resolve_llm_provider(settings: Any) -> str:
    provider = (getattr(settings, "llm_provider", "") or "").strip().lower()

    if provider == "token" and (
        getattr(settings, "auth_token_url", "")
        and getattr(settings, "auth_client_id", "")
        and getattr(settings, "auth_client_secret", "")
    ):
        return "token"

    if getattr(settings, "auth_token_url", "") and getattr(settings, "auth_client_id", "") and getattr(settings, "auth_client_secret", ""):
        return "token"

    if getattr(settings, "openai_base_url", "") and getattr(settings, "openai_api_key", ""):
        return "openai"

    if provider == "bedrock" and (
        getattr(settings, "aws_access_key_id", "")
        or getattr(settings, "aws_secret_access_key", "")
        or getattr(settings, "bedrock_api_key", "")
        or getattr(settings, "bedrock_endpoint", "")
    ):
        return "bedrock"

    if provider in {"openai", "azure"}:
        return provider

    if getattr(settings, "azure_openai_api_key", "") and getattr(settings, "azure_openai_endpoint", ""):
        return "azure"

    if (
        getattr(settings, "aws_access_key_id", "")
        or getattr(settings, "aws_secret_access_key", "")
        or getattr(settings, "bedrock_api_key", "")
        or getattr(settings, "bedrock_endpoint", "")
    ):
        return "bedrock"

    return "openai"


def build_llm_request(settings: Any, system: str, user: str) -> tuple[str, str, dict[str, Any], dict[str, Any]]:
    provider = _resolve_llm_provider(settings)
    if provider == "bedrock" and getattr(settings, "bedrock_endpoint", "") and getattr(settings, "bedrock_api_key", ""):
        endpoint = getattr(settings, "bedrock_endpoint", "").rstrip("/")
        if "/chat/completions" in endpoint:
            pass
        elif endpoint.endswith("/v1"):
            endpoint = f"{endpoint}/chat/completions"
        else:
            endpoint = f"{endpoint}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {getattr(settings, 'bedrock_api_key', '')}",
            "Content-Type": "application/json",
        }
        body = {
            "model": getattr(settings, "bedrock_model_id", "") or getattr(settings, "openai_model", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        return provider, endpoint, headers, body

    if provider == "token" and getattr(settings, "openai_base_url", "") and getattr(settings, "auth_token_url", ""):
        endpoint = getattr(settings, "openai_base_url", "").rstrip("/")
        if "/chat/completions" in endpoint:
            pass
        elif endpoint.endswith("/v1"):
            endpoint = f"{endpoint}/chat/completions"
        else:
            endpoint = f"{endpoint}/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        body = {
            "model": getattr(settings, "openai_model", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        return provider, endpoint, headers, body

    if provider == "openai" and getattr(settings, "openai_api_key", "") and getattr(settings, "openai_base_url", ""):
        endpoint = getattr(settings, "openai_base_url", "").rstrip("/")
        if "/chat/completions" in endpoint:
            pass
        elif endpoint.endswith("/v1"):
            endpoint = f"{endpoint}/chat/completions"
        else:
            endpoint = f"{endpoint}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {getattr(settings, 'openai_api_key', '')}",
            "Content-Type": "application/json",
        }
        body = {
            "model": getattr(settings, "openai_model", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        return provider, endpoint, headers, body

    if provider == "bedrock":
        model_id = getattr(settings, "bedrock_model_id", "") or "anthropic.claude-3-5-sonnet-20240620-v1:0"
        region = getattr(settings, "bedrock_region", "") or "us-east-1"
        url = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/invoke"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": f"{system}\n\n{user}"}],
                }
            ],
        }
        return provider, url, headers, body

    if provider == "azure" and getattr(settings, "azure_openai_api_key", "") and getattr(settings, "azure_openai_endpoint", ""):
        url = (
            getattr(settings, "azure_openai_endpoint", "").rstrip("/")
            + f"/openai/deployments/{getattr(settings, 'azure_openai_deployment', '')}/chat/completions?api-version=2024-08-01-preview"
        )
        headers = {"api-key": getattr(settings, "azure_openai_api_key", ""), "Content-Type": "application/json"}
        body: dict[str, Any] = {
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }
        return provider, url, headers, body

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {getattr(settings, 'openai_api_key', '')}",
        "Content-Type": "application/json",
    }
    body = {
        "model": getattr(settings, "openai_model", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    return provider, url, headers, body


async def _get_access_token(settings: Any) -> str:
    token_url = getattr(settings, "auth_token_url", "")
    client_id = getattr(settings, "auth_client_id", "")
    client_secret = getattr(settings, "auth_client_secret", "")
    if not token_url or not client_id or not client_secret:
        raise RuntimeError("Token auth settings are incomplete")

    data = {
        "grant_type": getattr(settings, "auth_grant_type", "client_credentials") or "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    scope = getattr(settings, "auth_scope", "")
    if scope:
        data["scope"] = scope

    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(
            token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        payload = resp.json()

    token = payload.get("access_token") or payload.get("token")
    if not token:
        raise RuntimeError(f"Token endpoint did not return an access token: {payload}")
    return token


async def _call_token_provider(settings: Any, system: str, user: str) -> str:
    provider, url, headers, body = build_llm_request(settings, system, user)
    if provider != "token":
        raise RuntimeError("Token provider expected")

    access_token = await _get_access_token(settings)
    headers["Authorization"] = f"Bearer {access_token}"

    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()

    if isinstance(payload.get("choices"), list) and payload["choices"]:
        return payload["choices"][0]["message"]["content"]
    if isinstance(payload.get("content"), list):
        texts = [item.get("text", "") for item in payload.get("content", []) if isinstance(item, dict)]
        return "\n".join(texts).strip()
    return json.dumps(payload)


async def _call_bedrock(settings: Any, system: str, user: str) -> str:
    provider, url, headers, body = build_llm_request(settings, system, user)

    if provider == "bedrock" and getattr(settings, "bedrock_endpoint", "") and getattr(settings, "bedrock_api_key", ""):
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            payload = resp.json()
        if isinstance(payload.get("choices"), list) and payload["choices"]:
            return payload["choices"][0]["message"]["content"]
        if isinstance(payload.get("content"), list):
            texts = [item.get("text", "") for item in payload.get("content", []) if isinstance(item, dict)]
            return "\n".join(texts).strip()
        return json.dumps(payload)

    if boto3 is None:
        raise RuntimeError("boto3 is required for Bedrock support")

    client_kwargs: dict[str, Any] = {"region_name": getattr(settings, "bedrock_region", "") or "us-east-1"}
    if getattr(settings, "aws_access_key_id", ""):
        client_kwargs["aws_access_key_id"] = getattr(settings, "aws_access_key_id", "")
    if getattr(settings, "aws_secret_access_key", ""):
        client_kwargs["aws_secret_access_key"] = getattr(settings, "aws_secret_access_key", "")
    if getattr(settings, "aws_session_token", ""):
        client_kwargs["aws_session_token"] = getattr(settings, "aws_session_token", "")

    client = boto3.client("bedrock-runtime", **client_kwargs)
    response = client.invoke_model(
        modelId=getattr(settings, "bedrock_model_id", "") or "anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps(body),
    )
    payload = json.loads(response["body"].read().decode("utf-8"))
    if isinstance(payload.get("content"), list):
        texts = [item.get("text", "") for item in payload.get("content", []) if isinstance(item, dict)]
        return "\n".join(texts).strip()
    if isinstance(payload.get("completion"), str):
        return payload["completion"].strip()
    return json.dumps(payload)


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

    provider = _resolve_llm_provider(settings)
    if provider == "token" and not (
        settings.auth_token_url and settings.auth_client_id and settings.auth_client_secret and settings.openai_base_url
    ):
        return base
    if provider == "openai" and not settings.openai_api_key:
        return base
    if provider == "azure" and not (settings.azure_openai_api_key and settings.azure_openai_endpoint):
        return base
    if provider == "bedrock" and not (
        settings.bedrock_model_id
        or settings.aws_access_key_id
        or settings.aws_secret_access_key
        or settings.bedrock_api_key
        or settings.bedrock_endpoint
    ):
        return base

    try:
        return await _llm_define(base)
    except Exception:
        return base


async def _llm_define(candidates: list[CandidateTerm]) -> list[CandidateTerm]:
    settings = get_settings()
    payload_terms = [
        {"term": c.term, "kind": c.kind, "context": c.context, "hint": c.definition}
        for c in candidates[:40]
    ]
    logger.info(f"LLM classify: {len(payload_terms)} terms")
    system = (
        "You are a classifier for technical jargon. For each term, classify it as one of: "
        "'team_specific' (unique to this team), 'standard_technical' (AWS/standard cloud/programming term), or 'noise' (generic word appearing multiple times). "
        "Return ONLY valid JSON: {\"definitions\":[{\"term\":\"...\",\"definition\":\"...\","
        "\"confidence\":0.0,\"classification\":\"team_specific|standard_technical|noise\",\"aliases\":[]}]}. "
        "Be strict: S3, Lambda, DynamoDB, API Gateway, CloudWatch, github, docker, etc. are 'standard_technical'. Any other standard technical terms should be classified here as well."
        "Common verbs like 'Ingest', 'Process', 'Queue' used generically are 'noise'. "
        "Only mark as 'team_specific' if it is clearly unique team jargon."
    )
    user = json.dumps({"terms": payload_terms})

    provider, url, headers, body = build_llm_request(settings, system, user)
    if provider == "token":
        content = await _call_token_provider(settings, system, user)
    elif provider == "bedrock":
        content = await _call_bedrock(settings, system, user)
    else:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]

    logger.info(f"LLM response: {content}")
    data = json.loads(content)
    by_term = {
        d["term"].strip().lower(): d
        for d in data.get("definitions", [])
        if isinstance(d, dict) and d.get("term")
    }
    logger.info(f"Parsed {len(by_term)} definitions with classifications")

    out: list[CandidateTerm] = []
    for cand in candidates:
        hit = by_term.get(cand.term.lower())
        classification = "team_specific"  # default if LLM doesn't classify
        
        # Check heuristic blocklist first
        if cand.term.lower() in STANDARD_TECHNICAL_TERMS:
            classification = "standard_technical"
        elif hit:
            classification = hit.get("classification", "team_specific")
        
        # Only include team-specific terms; filter out standard_technical and noise
        if classification in ("standard_technical", "noise"):
            continue
        
        if not hit:
            out.append(cand.model_copy(update={"classification": classification}))
            continue
        out.append(
            cand.model_copy(
                update={
                    "definition": hit.get("definition") or cand.definition,
                    "confidence": float(hit.get("confidence", cand.confidence) or cand.confidence),
                    "classification": classification,
                    "aliases": list(
                        dict.fromkeys((cand.aliases or []) + list(hit.get("aliases") or []))
                    ),
                }
            )
        )
    return out
