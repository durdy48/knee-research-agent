"""Domain enumerations (part of the ubiquitous language)."""
from __future__ import annotations

from enum import Enum
from typing import Optional


class StrValueEnum(str, Enum):
    """A string enum that renders as its *value*, not `ClassName.member`.

    Python 3.11 changed how mixed-in enums format: `f"{Impact.new}"` now yields
    `"Impact.new"` instead of the value `"New"`. Human-facing views (Obsidian topics,
    executive reports) interpolate these directly, so we restore value formatting here.
    An Enum with no members can be subclassed, so all string enums extend this.
    """

    def __str__(self) -> str:
        return str(self.value)

    def __format__(self, spec: str) -> str:
        return format(self.value, spec)


class PaperStatus(StrValueEnum):
    discovered = "discovered"
    pending_review = "pending_review"
    reviewed = "reviewed"
    consolidated = "consolidated"


class StudyType(StrValueEnum):
    meta_analysis = "Meta-analysis"
    systematic_review = "Systematic Review"
    rct = "Randomized Controlled Trial"
    cohort = "Cohort Study"
    case_control = "Case-Control Study"
    case_series = "Case Series"
    guideline = "Clinical Guideline"
    expert_opinion = "Expert Opinion"
    other = "Other"


class EvidenceLevel(int, Enum):
    """Evidence Quality Scale (★ = 1 … ★★★★★ = 5)."""

    expert_opinion = 1
    case_series = 2
    cohort = 3
    rct = 4
    meta_analysis = 5


class EvidenceClass(StrValueEnum):
    """Evidence Classification — the *kind* of evidence rating a document deserves.

    Graded study designs get a star level; documents that do not fit the 1-5 scale
    (guidelines, consensus/position statements, scoping reviews) get a categorical label.
    This is what lets the Quality Gates stop rejecting valid non-graded documents.
    """

    five_star = "★★★★★"
    four_star = "★★★★"
    three_star = "★★★"
    two_star = "★★"
    one_star = "★"
    consensus = "Consensus"
    exploratory = "Exploratory"
    unclassified = "Unclassified"


def classify_evidence(study_type: Optional[str]) -> EvidenceClass:
    """Map a study-type string (free text or enum value) to an EvidenceClass."""
    if not study_type:
        return EvidenceClass.unclassified
    low = study_type.lower()
    if "meta" in low or "systematic" in low:
        return EvidenceClass.five_star
    if "random" in low or "rct" in low:
        return EvidenceClass.four_star
    if "cohort" in low:
        return EvidenceClass.three_star
    if "case-control" in low or "case control" in low or "case series" in low:
        return EvidenceClass.two_star
    if "guideline" in low or "consensus" in low or "position" in low or "criteria" in low:
        return EvidenceClass.consensus
    if "scoping" in low or "exploratory" in low or "narrative" in low:
        return EvidenceClass.exploratory
    return EvidenceClass.unclassified


class Impact(StrValueEnum):
    """Change Analyzer output (see GLOSSARY: Impact Classification)."""

    new = "New"
    reinforcement = "Reinforcement"
    contradiction = "Contradiction"
    irrelevant = "Irrelevant"


class RiskOfBias(StrValueEnum):
    low = "Low"
    moderate = "Moderate"
    high = "High"


class RelevanceLevel(StrValueEnum):
    low = "low"
    moderate = "moderate"
    high = "high"
    very_high = "very high"


class ResolutionLevel(StrValueEnum):
    """Lifecycle state of a Controversy (see docs/knowledge/CONTROVERSY_MODEL.md)."""

    open = "open"
    emerging = "emerging"
    contested = "contested"
    resolving = "resolving"
    resolved = "resolved"
