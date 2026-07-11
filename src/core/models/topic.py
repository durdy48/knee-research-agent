"""Living Clinical Topic and its evolution events — the consolidated knowledge object.

The ClinicalTopic is the source of truth; living-topic.md is a rendered view of it.
It carries a numeric `confidence` that evolution events move, and the ordered history of
those `events` (Knowledge Integrity: nothing is lost).
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .enums import Impact


class EvidenceTimelineEntry(BaseModel):
    year: int
    note: str = ""


class EvolutionEvent(BaseModel):
    """One knowledge-evolution event for a topic (see GLOSSARY: Impact Classification)."""

    topic_id: str
    date: str
    impact: Impact = Impact.new
    papers_added: int = 0
    confidence_before: Optional[float] = None
    confidence_after: Optional[float] = None
    summary: str = ""


class ClinicalTopic(BaseModel):
    """A continuously evolving unit of knowledge (see GLOSSARY: Living Clinical Topic)."""

    topic_id: str
    name: str
    status: str = "Living Topic"
    confidence: float = 0.5  # 0..1, moved by evolution events
    research_confidence: Optional[str] = None
    consensus: str = ""
    executive_summary: str = ""
    current_scientific_consensus: str = ""
    evidence_timeline: List[EvidenceTimelineEntry] = Field(default_factory=list)
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    relevance_for_patient: str = ""
    discussion_points: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    events: List[EvolutionEvent] = Field(default_factory=list)
    last_updated: str = ""
