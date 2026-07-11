"""Personal Insight — the personalised interpretation (Personal Intelligence Layer)."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .enums import RelevanceLevel


class Insight(BaseModel):
    topic_id: str
    personal_relevance: RelevanceLevel = RelevanceLevel.moderate
    reasons: List[str] = Field(default_factory=list)
    why_it_matters: str = ""
    confidence_for_case: Optional[str] = None
    what_changed: str = ""
    what_to_monitor: List[str] = Field(default_factory=list)
    questions_for_specialist: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
