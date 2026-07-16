from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Kind = Literal["acronym", "camelcase", "entity", "noun_phrase", "other"]
Classification = Literal["team_specific", "standard_technical", "noise"]


class CandidateTerm(BaseModel):
    term: str
    kind: Kind | str = "other"
    definition: str = ""
    confidence: float = 0.0
    context: str = ""
    aliases: list[str] = Field(default_factory=list)
    classification: Classification = "team_specific"


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    candidates: list[CandidateTerm]
