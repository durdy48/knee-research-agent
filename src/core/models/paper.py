"""Paper, Claim and PaperReview — the input side of the domain.

PaperReview is the object form of the data contract in templates/paper-review.md.
Markdown/JSON are just views of these objects.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import EvidenceClass, EvidenceLevel, PaperStatus, RiskOfBias, StudyType


class Paper(BaseModel):
    """A registry entry for a scientific publication."""

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

    paper_id: str
    title: str = ""
    doi: Optional[str] = None
    pmid: Optional[str] = None
    year: Optional[int] = None
    abstract: Optional[str] = None  # source text handed to the reviewer (never fabricated)
    study_type: Optional[str] = None  # free text at registry level; PaperReview uses the StudyType enum
    status: PaperStatus = PaperStatus.discovered
    review: Optional[str] = None
    claims: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    discovered_at: str = ""
    last_updated: str = ""


class Claim(BaseModel):
    """An atomic factual statement extracted from a single Paper."""

    claim_id: str
    topic: Optional[str] = None
    text: str
    supporting_data: str = ""
    evidence_level: Optional[EvidenceLevel] = None
    atomic: bool = True
    needs_full_text_confirmation: bool = False


class PaperReview(BaseModel):
    """Structured, immutable review of one Paper (the data contract as an object)."""

    paper_id: Optional[str] = None
    title: str
    authors: List[str] = Field(default_factory=list)
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    pmid: Optional[str] = None
    study_type: Optional[StudyType] = None
    evidence_level: Optional[EvidenceLevel] = None
    evidence_class: Optional[EvidenceClass] = None  # Evidence Classification (stars or category)

    research_question: str = ""
    clinical_problem: str = ""
    clinical_topics: List[str] = Field(default_factory=list)

    population: str = ""
    inclusion_criteria: str = ""
    exclusion_criteria: str = ""
    intervention: str = ""
    comparator: str = ""
    outcomes: List[str] = Field(default_factory=list)
    follow_up: str = ""

    primary_findings: str = ""
    secondary_findings: str = ""
    statistical_significance: str = ""
    clinical_significance: str = ""

    claims: List[Claim] = Field(default_factory=list)

    risk_of_bias: Optional[RiskOfBias] = None
    main_limitations: List[str] = Field(default_factory=list)
    external_validity: str = ""

    reinforces_existing: Optional[str] = None
    contradicts_existing: Optional[str] = None
    introduces_new: Optional[str] = None

    applicable_profiles: str = ""
    non_applicable_profiles: str = ""

    open_questions: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    ai_review_notes: str = ""
    immutable: bool = True
