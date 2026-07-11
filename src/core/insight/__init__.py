"""Personal Insight Engine — the personalisation layer (pure domain).

Turns consolidated knowledge + the person's profile into 'what changed for me?' — without
ever changing the science (Golden Rule 3) or prescribing (Golden Rule 5).
"""
from __future__ import annotations

from .engine import (
    DISCLAIMER,
    InsightItem,
    PersonalInsightEngine,
    PersonalInsightReport,
)

__all__ = [
    "PersonalInsightEngine",
    "PersonalInsightReport",
    "InsightItem",
    "DISCLAIMER",
]
