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
    ResolutionLevel,
    RiskOfBias,
    StudyType,
    classify_evidence,
)
from .paper import Claim, Paper, PaperReview
from .topic import ClinicalTopic, Controversy, EvidenceTimelineEntry, EvolutionEvent
from .delta import KnowledgeDelta
from .evidence import Evidence
from .insight import Insight
from .report import ExecutiveReport
from .patient import (
    PatientProfile,
    PatientVariables,
    Persona,
    PersonalContext,
    PersonalGoals,
)

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
    "ResolutionLevel",
    # models
    "Paper",
    "Claim",
    "PaperReview",
    "ClinicalTopic",
    "Controversy",
    "KnowledgeDelta",
    "EvidenceTimelineEntry",
    "EvolutionEvent",
    "Evidence",
    "Insight",
    "ExecutiveReport",
    "PatientProfile",
    "PatientVariables",
    "Persona",
    "PersonalGoals",
    "PersonalContext",
]
