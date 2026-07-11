"""Knowledge-evolution engine — pure domain logic (no AI, no storage).

Applies a knowledge event to a Living Clinical Topic: it moves the topic's confidence
according to the Impact Classification and records the event, preserving history.

Rules (ADR-0001): consensus/confidence change only when evidence warrants; nothing is
lost. Confidence rises for New/Reinforcement, falls for Contradiction, unchanged for
Irrelevant.
"""
from __future__ import annotations

from datetime import date as _date
from typing import Optional

from .models.enums import Impact
from .models.topic import ClinicalTopic, EvolutionEvent

# Base confidence step per impact (before scaling by number of papers).
_STEP = {
    Impact.new: 0.10,
    Impact.reinforcement: 0.08,
    Impact.contradiction: -0.12,
    Impact.irrelevant: 0.0,
}


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def apply_event(
    topic: ClinicalTopic,
    *,
    impact: Impact,
    papers_added: int = 1,
    summary: str = "",
    when: Optional[str] = None,
) -> EvolutionEvent:
    """Apply an evolution event to `topic` in place and return the recorded event."""
    impact = Impact(impact)
    when = when or _date.today().isoformat()

    before = round(topic.confidence, 4)
    # More papers move confidence a little more, with diminishing scaling.
    scale = max(1, papers_added) ** 0.5 if impact is not Impact.irrelevant else 0
    after = round(_clamp(before + _STEP[impact] * scale), 4)

    event = EvolutionEvent(
        topic_id=topic.topic_id,
        date=when,
        impact=impact,
        papers_added=papers_added,
        confidence_before=before,
        confidence_after=after,
        summary=summary,
    )

    topic.confidence = after
    topic.events.append(event)  # history is preserved (append-only)
    topic.last_updated = when
    return event
