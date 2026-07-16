from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Term, utcnow
from .schemas import aliases_dumps


SEED_TERMS = [
    {
        "term": "PIR",
        "definition": "Post-Incident Review — meeting held after a production incident to capture learnings.",
        "kind": "acronym",
        "status": "approved",
    },
    {
        "term": "GTM",
        "definition": "Go-To-Market — the plan and activities for launching a product or feature.",
        "kind": "acronym",
        "status": "approved",
    },
    {
        "term": "BAU",
        "definition": "Business As Usual — routine operations outside of incident response.",
        "kind": "acronym",
        "status": "approved",
    },
    {
        "term": "SLO",
        "definition": "Service Level Objective — target reliability/latency goal for a service.",
        "kind": "acronym",
        "status": "approved",
    },
    {
        "term": "RFC",
        "definition": "Request for Comments — design proposal reviewed before large changes.",
        "kind": "acronym",
        "status": "approved",
    },
    {
        "term": "OKR",
        "definition": "Objectives and Key Results — goal-setting framework used each quarter.",
        "kind": "acronym",
        "status": "approved",
    },
]


def seed_demo(session: Session) -> int:
    settings = get_settings()
    created = 0
    for item in SEED_TERMS:
        exists = session.scalar(
            select(Term).where(
                Term.team_id == settings.team_id,
                Term.term == item["term"],
            )
        )
        if exists:
            continue
        session.add(
            Term(
                team_id=settings.team_id,
                term=item["term"],
                definition=item["definition"],
                aliases=aliases_dumps([]),
                status=item["status"],
                source="seed",
                kind=item["kind"],
                confidence=1.0,
                context="",
                created_by="seed",
                updated_by="seed",
                last_seen_at=utcnow(),
            )
        )
        created += 1
    session.commit()
    return created
