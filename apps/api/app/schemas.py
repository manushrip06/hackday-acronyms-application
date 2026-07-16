from __future__ import annotations

import json
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


Role = Literal["lead", "member"]
TermStatus = Literal["pending", "approved", "rejected"]


class TermOut(BaseModel):
    id: str
    team_id: str
    term: str
    definition: str
    aliases: list[str] = Field(default_factory=list)
    status: str
    source: str
    kind: str
    confidence: float
    context: str = ""
    conflict_note: Optional[str] = None
    created_by: str
    updated_by: str
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime


class TermSuggest(BaseModel):
    term: str
    definition: str
    aliases: list[str] = Field(default_factory=list)
    kind: str = "other"


class TermUpdate(BaseModel):
    term: Optional[str] = None
    definition: Optional[str] = None
    aliases: Optional[list[str]] = None
    status: Optional[TermStatus] = None
    conflict_note: Optional[str] = None


class CandidateTerm(BaseModel):
    term: str
    kind: str = "other"
    definition: str = ""
    confidence: float = 0.0
    context: str = ""
    aliases: list[str] = Field(default_factory=list)


class UploadResult(BaseModel):
    document_id: str
    filename: str
    candidates_found: int
    pending_created: int
    pending_updated: int
    conflicts: int
    approved_unchanged: int


class Health(BaseModel):
    status: str = "ok"
    service: str


def aliases_loads(raw: str) -> list[str]:
    try:
        data = json.loads(raw or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def aliases_dumps(aliases: list[str]) -> str:
    return json.dumps(aliases or [])
