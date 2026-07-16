from __future__ import annotations

import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import Term, utcnow
from .schemas import CandidateTerm, aliases_dumps, aliases_loads


def _norm(term: str) -> str:
    return re.sub(r"\s+", " ", term.strip()).lower()


def _defs_differ(a: str, b: str) -> bool:
    na = re.sub(r"\s+", " ", (a or "").strip().lower())
    nb = re.sub(r"\s+", " ", (b or "").strip().lower())
    if not na or not nb:
        return False
    if na == nb:
        return False
    # crude: differ if Jaccard of words < 0.6
    wa, wb = set(na.split()), set(nb.split())
    if not wa or not wb:
        return True
    j = len(wa & wb) / len(wa | wb)
    return j < 0.6


def merge_candidates(
    session: Session,
    candidates: list[CandidateTerm],
    *,
    team_id: str,
    actor_user: str,
    source: str = "upload",
) -> dict[str, int]:
    pending_created = pending_updated = conflicts = approved_unchanged = 0

    for cand in candidates:
        term_text = cand.term.strip()
        if not term_text:
            continue
        existing = session.scalar(
            select(Term).where(
                Term.team_id == team_id,
                func.lower(Term.term) == _norm(term_text),
            )
        )
        now = utcnow()
        if existing is None:
            session.add(
                Term(
                    team_id=team_id,
                    term=term_text,
                    definition=cand.definition or "",
                    aliases=aliases_dumps(cand.aliases),
                    status="pending",
                    source=source,
                    kind=cand.kind or "other",
                    confidence=float(cand.confidence or 0),
                    context=cand.context or "",
                    created_by=actor_user,
                    updated_by=actor_user,
                    last_seen_at=now,
                )
            )
            pending_created += 1
            continue

        existing.last_seen_at = now
        existing.updated_by = actor_user

        if existing.status == "approved":
            approved_unchanged += 1
            if _defs_differ(existing.definition, cand.definition or ""):
                existing.conflict_note = (
                    f"AI suggests different definition: {(cand.definition or '')[:280]}"
                )
                conflicts += 1
            continue

        if existing.status == "pending":
            existing.definition = cand.definition or existing.definition
            existing.confidence = float(cand.confidence or existing.confidence)
            existing.context = cand.context or existing.context
            existing.kind = cand.kind or existing.kind
            if cand.aliases:
                merged = list(dict.fromkeys(aliases_loads(existing.aliases) + cand.aliases))
                existing.aliases = aliases_dumps(merged)
            pending_updated += 1
            continue

        # rejected → re-open as pending with new suggestion
        if existing.status == "rejected":
            existing.status = "pending"
            existing.definition = cand.definition or existing.definition
            existing.confidence = float(cand.confidence or 0)
            existing.context = cand.context or ""
            existing.conflict_note = None
            pending_updated += 1

    session.commit()
    return {
        "pending_created": pending_created,
        "pending_updated": pending_updated,
        "conflicts": conflicts,
        "approved_unchanged": approved_unchanged,
    }
