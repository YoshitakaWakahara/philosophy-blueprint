from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


ClaimType = Literal["genealogy", "inversion", "diagnosis", "critique", "distinction"]


class SourceRef(BaseModel):
    ref: str
    span: Optional[str] = None  # "§7-8" など


class Claim(BaseModel):
    claim_id: str
    type: ClaimType
    statement_ja: str
    my_paraphrase: Optional[str] = None
    concepts: list[str] = Field(default_factory=list)
    sources: list[SourceRef] = Field(default_factory=list)
    scope: Optional[str] = None
    depends_on: list[str] = Field(default_factory=list)


class ClaimsFile(BaseModel):
    version: int = 1
    work: str
    section: Optional[str] = None
    claims: list[Claim]