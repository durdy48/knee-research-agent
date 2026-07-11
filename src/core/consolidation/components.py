"""The six deterministic components of the Knowledge Consolidation Engine.

Pure domain logic — no AI, no storage, no vendor. Each component implements one of the
design documents in docs/knowledge/. The rules here are deterministic and driven by signals
already present in a validated PaperReview (its stance via `contradicts_existing` /
`reinforces_existing`, its Evidence Classification), so the same input always yields the
same knowledge move.

  1. EvidenceMerger      PaperReview[]           -> MergedEvidence
  2. ConsensusBuilder    (Topic, MergedEvidence) -> Assessment (Impact + whether consensus changes)
  3. ControversyManager  opens/updates Controversies (CONTROVERSY_MODEL.md)
  4. ConfidenceCalculator moves confidence via the knowledge engine (CONFIDENCE_MODEL.md)
  5. DeltaGenerator      builds the KnowledgeDelta (KNOWLEDGE_DELTAS.md)
  6. EventLog            records domain events for downstream consumers
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..models import (
    ClinicalTopic,
    Controversy,
    EvolutionEvent,
    Impact,
    KnowledgeDelta,
    PaperReview,
)
from ..models.enums import EvidenceClass, ResolutionLevel
from ..knowledge_engine import apply_event

_ESCALATION = {
    ResolutionLevel.open: ResolutionLevel.emerging,
    ResolutionLevel.emerging: ResolutionLevel.contested,
    ResolutionLevel.contested: ResolutionLevel.contested,
    ResolutionLevel.resolving: ResolutionLevel.contested,  # reopened by new contradiction
    ResolutionLevel.resolved: ResolutionLevel.contested,   # reopened by new contradiction
}


def evidence_label(review: PaperReview) -> str:
    """Stable identity of a review's evidence (used for traceability AND idempotency)."""
    return review.doi or review.pmid or review.paper_id or review.title


def _stance(review: PaperReview) -> str:
    if (review.contradicts_existing or "").strip():
        return "contradict"
    if (review.reinforces_existing or "").strip():
        return "reinforce"
    return "neutral"


# 1 -------------------------------------------------------------------------------------
@dataclass
class MergedEvidence:
    topic: str
    reviews: List[PaperReview]
    stances: List[str]
    labels: List[str]
    guideline: bool

    @property
    def count(self) -> int:
        return len(self.reviews)

    def labels_with(self, stance: str) -> List[str]:
        return [self.labels[i] for i, s in enumerate(self.stances) if s == stance]


class EvidenceMerger:
    """PaperReview[] -> MergedEvidence: group the findings that bear on one topic."""

    def merge(self, topic: str, reviews: List[PaperReview]) -> MergedEvidence:
        stances = [_stance(r) for r in reviews]
        labels = [evidence_label(r) for r in reviews]
        guideline = any(r.evidence_class == EvidenceClass.consensus for r in reviews)
        return MergedEvidence(topic, list(reviews), stances, labels, guideline)


# 2 -------------------------------------------------------------------------------------
@dataclass
class Assessment:
    impact: Impact
    consensus_changed: bool
    note: str = ""


class ConsensusBuilder:
    """Decide how the merged evidence affects the consensus (does NOT mutate the topic)."""

    def assess(self, topic: ClinicalTopic, merged: MergedEvidence) -> Assessment:
        if merged.count == 0:
            return Assessment(Impact.irrelevant, False, "no new evidence")

        has_prior = bool(topic.events)
        if "contradict" in merged.stances:
            impact = Impact.contradiction
        elif not has_prior:
            impact = Impact.new
        elif "reinforce" in merged.stances:
            impact = Impact.reinforcement
        else:
            impact = Impact.irrelevant

        # New/Contradiction change the consensus; a guideline updates its wording; a plain
        # reinforcement only strengthens confidence.
        consensus_changed = impact in (Impact.new, Impact.contradiction) or (
            impact is Impact.reinforcement and merged.guideline
        )
        note = "guideline updates recommendations" if merged.guideline else ""
        return Assessment(impact, consensus_changed, note)


# 3 -------------------------------------------------------------------------------------
class ControversyManager:
    """Open or update Controversies when evidence contradicts the consensus. Never deletes."""

    def update(self, topic: ClinicalTopic, merged: MergedEvidence, when: str) -> List[str]:
        if "contradict" not in merged.stances:
            return []
        contradicting = merged.labels_with("contradict")
        supporting = merged.labels_with("reinforce") + list(topic.supporting_evidence)
        question = next(
            (r.contradicts_existing for r in merged.reviews if (r.contradicts_existing or "").strip()),
            f"Disputed claim in {topic.name}",
        )
        changes: List[str] = []
        if topic.controversies:
            c = topic.controversies[0]
            for s in contradicting:
                if s not in c.contradicting_studies:
                    c.contradicting_studies.append(s)
            c.resolution_level = _ESCALATION[ResolutionLevel(c.resolution_level)]
            c.last_updated = when
            changes.append(f"controversy '{c.controversy_id}' updated -> {c.resolution_level}")
        else:
            c = Controversy(
                controversy_id=f"{topic.topic_id}-C1",
                question=question,
                supporting_studies=supporting,
                contradicting_studies=contradicting,
                resolution_level=ResolutionLevel.open,
                opened=when,
                last_updated=when,
            )
            topic.controversies.append(c)
            changes.append(f"controversy opened: {question}")
        return changes


# 4 -------------------------------------------------------------------------------------
class ConfidenceCalculator:
    """Move the topic's confidence through the knowledge engine (records an EvolutionEvent)."""

    def apply(self, topic: ClinicalTopic, impact: Impact, merged: MergedEvidence, when: str) -> EvolutionEvent:
        return apply_event(
            topic,
            impact=impact,
            papers_added=merged.count,
            summary=f"{impact} from {merged.count} review(s)",
            when=when,
        )


# 5 -------------------------------------------------------------------------------------
class DeltaGenerator:
    """Build the immutable KnowledgeDelta describing this change."""

    def generate(
        self,
        topic: ClinicalTopic,
        *,
        impact: Impact,
        event: EvolutionEvent,
        controversy_changes: List[str],
        evidence: List[str],
        from_version: int,
        to_version: int,
        produced_by: str,
        when: str,
        consensus_note: str,
    ) -> KnowledgeDelta:
        what = {
            Impact.new: "new consolidated conclusion established",
            Impact.reinforcement: (consensus_note or "consensus reinforced"),
            Impact.contradiction: "consensus contested; confidence lowered",
            Impact.irrelevant: "no change",
        }[impact]
        if controversy_changes:
            what += "; " + "; ".join(controversy_changes)
        # Explainability: the change must be reconstructable — which rule, which evidence,
        # what the confidence did (CONFIDENCE_MODEL). Not just the final value.
        why = (
            f"CONFIDENCE_MODEL '{impact.value}' rule applied "
            f"({event.confidence_before} -> {event.confidence_after}); "
            f"triggered by: {', '.join(evidence)}"
        )
        return KnowledgeDelta(
            delta_id=f"{topic.topic_id}-v{to_version}",
            topic_id=topic.topic_id,
            date=when,
            impact=impact,
            what_changed=what,
            why=why,
            evidence=evidence,
            confidence_before=event.confidence_before,
            confidence_after=event.confidence_after,
            controversy_changes=controversy_changes,
            from_version=from_version,
            to_version=to_version,
            produced_by=produced_by,
        )


# 6 -------------------------------------------------------------------------------------
@dataclass
class EventLog:
    """Records domain events emitted during consolidation (for reports, sync, stats)."""

    events: List[Tuple[str, dict]] = field(default_factory=list)

    def emit(self, name: str, **payload) -> None:
        self.events.append((name, payload))

    def names(self) -> List[str]:
        return [n for n, _ in self.events]
