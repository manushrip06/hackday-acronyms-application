from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Session

from .db import Term

# Mock NLP catalog only — not inserted into DB on startup.
# Terms enter the dictionary after upload (mock/real NLP) → lead review → approve.

ENGINEERING_TERMS = [
    {
        "term": "PIR",
        "definition": "Post-Incident Review — meeting held after a production incident to capture learnings.",
        "kind": "acronym",
    },
    {
        "term": "GTM",
        "definition": "Go-To-Market — the plan and activities for launching a product or feature.",
        "kind": "acronym",
    },
    {
        "term": "BAU",
        "definition": "Business As Usual — routine operations outside of incident response.",
        "kind": "acronym",
    },
    {
        "term": "SLO",
        "definition": "Service Level Objective — target reliability/latency goal for a service.",
        "kind": "acronym",
    },
    {
        "term": "RFC",
        "definition": "Request for Comments — design proposal reviewed before large changes.",
        "kind": "acronym",
    },
    {
        "term": "OKR",
        "definition": "Objectives and Key Results — goal-setting framework used each quarter.",
        "kind": "acronym",
    },
]

SALES_TERMS = [
    {
        "term": "CRM",
        "definition": "Customer Relationship Management — system for tracking leads, accounts, and deals.",
        "kind": "acronym",
    },
    {
        "term": "ARR",
        "definition": "Annual Recurring Revenue — normalized yearly value of subscription contracts.",
        "kind": "acronym",
    },
    {
        "term": "MQL",
        "definition": "Marketing Qualified Lead — lead that marketing has vetted as worth sales follow-up.",
        "kind": "acronym",
    },
    {
        "term": "SQL",
        "definition": "Sales Qualified Lead — lead accepted by sales as ready for active pursuit.",
        "kind": "acronym",
    },
    {
        "term": "AE",
        "definition": "Account Executive — salesperson who owns closing deals with customers.",
        "kind": "acronym",
    },
    {
        "term": "ICP",
        "definition": "Ideal Customer Profile — description of the best-fit buyer for the product.",
        "kind": "acronym",
    },
]

TEAM_SEEDS: dict[str, list[dict]] = {
    "default": ENGINEERING_TERMS,
    "sales": SALES_TERMS,
}


def seed_demo(session: Session) -> int:
    """Dictionary starts empty — remove any legacy pre-seeded rows from earlier builds."""
    session.execute(delete(Term).where(Term.source == "seed"))
    session.commit()
    return 0
