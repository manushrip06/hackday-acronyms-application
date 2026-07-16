from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Kind = Literal["acronym", "camelcase", "entity", "noun_phrase", "other"]


class CandidateTerm(BaseModel):
    term: str
    kind: Kind | str = "other"
    definition: str = ""
    confidence: float = 0.0
    context: str = ""
    aliases: list[str] = Field(default_factory=list)


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    candidates: list[CandidateTerm]
