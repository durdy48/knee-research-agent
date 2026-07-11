"""Adapter-side normalisation helpers.

PaperReview keeps a strict StudyType enum (it is the data contract). Real model output and
free-text registry values do not always match, so providers normalise to the closest enum
value — or None — before building the PaperReview, instead of letting bad data through.
"""
from __future__ import annotations

from typing import Optional

from core.models.enums import StudyType

# Order matters: higher-evidence / more specific labels win when several cues appear
# (e.g. "Systematic Review / Meta-analysis" -> Meta-analysis).
_RULES = [
    ("meta", StudyType.meta_analysis),
    ("systematic", StudyType.systematic_review),
    ("random", StudyType.rct),
    ("case-control", StudyType.case_control),
    ("case control", StudyType.case_control),
    ("cohort", StudyType.cohort),
    ("case series", StudyType.case_series),
    ("guideline", StudyType.guideline),
    ("criteria", StudyType.guideline),
    ("consensus", StudyType.guideline),
    ("opinion", StudyType.expert_opinion),
]


def normalize_study_type(value: Optional[str]) -> Optional[str]:
    """Map free text to a StudyType value, or None if nothing plausible matches."""
    if not value:
        return None
    low = value.lower()
    for cue, st in _RULES:
        if cue in low:
            return st.value
    return StudyType.other.value
