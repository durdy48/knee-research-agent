"""Domain models — the official language of the system (Pydantic v2).

Objects are the source of truth. Markdown, JSON and Obsidian notes are views rendered
from these objects (ADR-0001; see the architecture discussion in docs/).
"""
from __future__ import annotations

from . import ids
from .enums import (
    EvidenceClass,
    EvidenceLevel,
    Impact,
    PaperStatus,
    RelevanceLevel,
    RiskOfBias,
    StudyType,
    classify_evidence,
)
from .paper import Claim, Paper, PaperReview
from .topic import ClinicalTopic, EvidenceTimelineEntry, EvolutionEvent
from .evidence import Evidence
from .insight import Insight
from .report import ExecutiveReport
from .patient import PatientProfile, Persona, PersonalContext, PersonalGoals

__all__ = [
    "ids",
    # enums
    "PaperStatus",
    "StudyType",
    "EvidenceLevel",
    "EvidenceClass",
    "classify_evidence",
    "Impact",
    "RiskOfBias",
    "RelevanceLevel",
    # models
    "Paper",
    "Claim",
    "PaperReview",
    "ClinicalTopic",
    "EvidenceTimelineEntry",
    "EvolutionEvent",
    "Evidence",
    "Insight",
    "ExecutiveReport",
    "PatientProfile",
    "Persona",
    "PersonalGoals",
    "PersonalContext",
]
