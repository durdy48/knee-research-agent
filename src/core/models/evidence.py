"""Consolidated Evidence — the objective bridge between reviews and knowledge."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .enums import EvidenceLevel


class Evidence(BaseModel):
    topic: str
    question: str = ""
    evidence_level: Optional[EvidenceLevel] = None
    confidence: Optional[float] = None
    agreements: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    claims: List[str] = Field(default_factory=list)  # Claim ids
