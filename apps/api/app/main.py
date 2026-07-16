from __future__ import annotations

# from pathlib import Path  # uncomment if re-enabling document file storage
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from .auth import Actor, get_actor, get_team_id, require_lead
from .db import SessionLocal, Term, init_db, utcnow  # Document — if re-enabling file storage
from .merge import merge_candidates
from .nlp_client import extract_candidates
from .schemas import (
    Health,
    TermOut,
    TermSuggest,
    TermUpdate,
    UploadResult,
    aliases_dumps,
    aliases_loads,
)
from .seed import seed_demo
from .text_extract import extract_text

app = FastAPI(title="Hackday Acronyms API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def term_to_out(row: Term) -> TermOut:
    return TermOut(
        id=row.id,
        team_id=row.team_id,
        term=row.term,
        definition=row.definition,
        aliases=aliases_loads(row.aliases),
        status=row.status,
        source=row.source,
        kind=row.kind,
        confidence=row.confidence,
        context=row.context or "",
        conflict_note=row.conflict_note,
        created_by=row.created_by,
        updated_by=row.updated_by,
        last_seen_at=row.last_seen_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    session = SessionLocal()
    try:
        seed_demo(session)
    finally:
        session.close()


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(service="api")


@app.post("/demo/reset")
def reset_team_dictionary(
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> dict:
    """Hackday demo: wipe this team's terms so Dictionary starts empty again."""
    require_lead(actor)
    result = session.execute(delete(Term).where(Term.team_id == team_id))
    session.commit()
    return {"ok": True, "team_id": team_id, "deleted": result.rowcount or 0}


@app.get("/terms", response_model=list[TermOut])
def list_terms(
    q: str | None = None,
    status: str | None = Query(default=None),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> list[TermOut]:
    stmt = select(Term).where(Term.team_id == team_id)
    if status:
        stmt = stmt.where(Term.status == status)
    else:
        stmt = stmt.where(Term.status == "approved")
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Term.term.ilike(like), Term.definition.ilike(like)))
    stmt = stmt.order_by(Term.term.asc())
    rows = session.scalars(stmt).all()
    return [term_to_out(r) for r in rows]


@app.post("/terms", response_model=TermOut)
def suggest_term(
    body: TermSuggest,
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> TermOut:
    existing = session.scalar(
        select(Term).where(
            Term.team_id == team_id,
            func.lower(Term.term) == body.term.strip().lower(),
        )
    )
    if existing and existing.status == "approved":
        raise HTTPException(status_code=409, detail="Term already approved; ask a lead to edit")
    if existing:
        existing.definition = body.definition
        existing.aliases = aliases_dumps(body.aliases)
        existing.status = "pending"
        existing.source = "suggest"
        existing.kind = body.kind
        existing.updated_by = actor.user
        existing.last_seen_at = utcnow()
        session.commit()
        session.refresh(existing)
        return term_to_out(existing)

    row = Term(
        team_id=team_id,
        term=body.term.strip(),
        definition=body.definition,
        aliases=aliases_dumps(body.aliases),
        status="pending",
        source="suggest",
        kind=body.kind,
        confidence=0.5,
        created_by=actor.user,
        updated_by=actor.user,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return term_to_out(row)


@app.patch("/terms/{term_id}", response_model=TermOut)
def edit_term(
    term_id: str,
    body: TermUpdate,
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> TermOut:
    require_lead(actor)
    row = session.get(Term, term_id)
    if not row or row.team_id != team_id:
        raise HTTPException(status_code=404, detail="Term not found")
    if body.term is not None:
        row.term = body.term.strip()
    if body.definition is not None:
        row.definition = body.definition
    if body.aliases is not None:
        row.aliases = aliases_dumps(body.aliases)
    if body.status is not None:
        row.status = body.status
    if body.conflict_note is not None:
        row.conflict_note = body.conflict_note
    row.updated_by = actor.user
    row.updated_at = utcnow()
    session.commit()
    session.refresh(row)
    return term_to_out(row)


@app.delete("/terms/{term_id}")
def delete_term(
    term_id: str,
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> dict:
    require_lead(actor)
    row = session.get(Term, term_id)
    if not row or row.team_id != team_id:
        raise HTTPException(status_code=404, detail="Term not found")
    session.delete(row)
    session.commit()
    return {"ok": True}


@app.get("/review", response_model=list[TermOut])
def review_queue(
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> list[TermOut]:
    require_lead(actor)
    rows = session.scalars(
        select(Term)
        .where(
            Term.team_id == team_id,
            or_(Term.status == "pending", Term.conflict_note.is_not(None)),
        )
        .order_by(Term.updated_at.desc())
    ).all()
    return [term_to_out(r) for r in rows]


@app.post("/review/{term_id}/approve", response_model=TermOut)
def approve_term(
    term_id: str,
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> TermOut:
    require_lead(actor)
    row = session.get(Term, term_id)
    if not row or row.team_id != team_id:
        raise HTTPException(status_code=404, detail="Term not found")
    row.status = "approved"
    row.conflict_note = None
    row.updated_by = actor.user
    row.updated_at = utcnow()
    session.commit()
    session.refresh(row)
    return term_to_out(row)


@app.post("/review/{term_id}/reject", response_model=TermOut)
def reject_term(
    term_id: str,
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> TermOut:
    require_lead(actor)
    row = session.get(Term, term_id)
    if not row or row.team_id != team_id:
        raise HTTPException(status_code=404, detail="Term not found")
    row.status = "rejected"
    row.conflict_note = None
    row.updated_by = actor.user
    row.updated_at = utcnow()
    session.commit()
    session.refresh(row)
    return term_to_out(row)


@app.post("/documents/upload", response_model=UploadResult)
async def upload_document(
    file: UploadFile = File(...),
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> UploadResult:
    require_lead(actor)
    raw = await file.read()
    filename = file.filename or "upload.txt"
    try:
        text = extract_text(filename, raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    doc_id = str(uuid4())
    # Optional: persist uploaded file + document record (disabled — only terms are kept)
    # settings = get_settings()
    # dest = Path(settings.upload_dir) / f"{doc_id}_{Path(filename).name}"
    # dest.parent.mkdir(parents=True, exist_ok=True)
    # dest.write_bytes(raw)
    # doc = Document(
    #     id=doc_id,
    #     team_id=settings.team_id,
    #     filename=filename,
    #     stored_path=str(dest),
    #     text_preview=text[:2000],
    #     uploaded_by=actor.user,
    # )
    # session.add(doc)
    # session.commit()

    candidates = await extract_candidates(text, team_id=team_id)
    stats = merge_candidates(
        session, candidates, team_id=team_id, actor_user=actor.user, source="upload"
    )
    return UploadResult(
        document_id=doc_id,
        filename=filename,
        candidates_found=len(candidates),
        pending_created=stats["pending_created"],
        pending_updated=stats["pending_updated"],
        conflicts=stats["conflicts"],
        approved_unchanged=stats["approved_unchanged"],
    )


@app.post("/documents/paste", response_model=UploadResult)
async def paste_document(
    body: dict,
    actor: Actor = Depends(get_actor),
    team_id: str = Depends(get_team_id),
    session: Session = Depends(db_session),
) -> UploadResult:
    require_lead(actor)
    text = (body.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    filename = body.get("filename") or "pasted.txt"
    doc_id = str(uuid4())
    # Optional: persist pasted text as file + document record (disabled — only terms are kept)
    # settings = get_settings()
    # dest = Path(settings.upload_dir) / f"{doc_id}_{filename}"
    # dest.parent.mkdir(parents=True, exist_ok=True)
    # dest.write_text(text, encoding="utf-8")
    # session.add(
    #     Document(
    #         id=doc_id,
    #         team_id=settings.team_id,
    #         filename=filename,
    #         stored_path=str(dest),
    #         text_preview=text[:2000],
    #         uploaded_by=actor.user,
    #     )
    # )
    # session.commit()
    candidates = await extract_candidates(text, team_id=team_id)
    stats = merge_candidates(
        session, candidates, team_id=team_id, actor_user=actor.user, source="upload"
    )
    return UploadResult(
        document_id=doc_id,
        filename=filename,
        candidates_found=len(candidates),
        pending_created=stats["pending_created"],
        pending_updated=stats["pending_updated"],
        conflicts=stats["conflicts"],
        approved_unchanged=stats["approved_unchanged"],
    )
