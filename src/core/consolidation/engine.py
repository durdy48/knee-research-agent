"""KnowledgeConsolidationEngine — orchestrates the six components.

    Validated PaperReview[]  →  Knowledge Consolidation Engine  →  KnowledgeDelta
                                                                 →  updated Living Topic (new version)

Deterministic, append-only, and traceable (docs/knowledge/KNOWLEDGE_CONSOLIDATION.md). It
consolidates *validated knowledge*, not papers: it decides whether the consensus changes,
preserves controversies, moves confidence by the documented rules, emits a KnowledgeDelta,
and publishes a new Topic Version — or does nothing when the evidence is irrelevant.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date as _date
from typing import List, Optional

from ..models import ClinicalTopic, Impact, KnowledgeDelta, PaperReview
from .components import (
    ConfidenceCalculator,
    ConsensusBuilder,
    ControversyManager,
    DeltaGenerator,
    EventLog,
    EvidenceMerger,
    evidence_label,
)


@dataclass
class ConsolidationResult:
    topic: ClinicalTopic
    impact: Impact
    delta: Optional[KnowledgeDelta] = None
    events: List[str] = field(default_factory=list)
    changed: bool = False


class KnowledgeConsolidationEngine:
    def __init__(self) -> None:
        self.merger = EvidenceMerger()
        self.consensus = ConsensusBuilder()
        self.controversies = ControversyManager()
        self.confidence = ConfidenceCalculator()
        self.deltas = DeltaGenerator()

    def consolidate(
        self,
        topic: ClinicalTopic,
        reviews: List[PaperReview],
        *,
        produced_by: str = "manual",
        when: Optional[str] = None,
    ) -> ConsolidationResult:
        when = when or _date.today().isoformat()
        log = EventLog()

        # Idempotency: evidence already incorporated into this topic is skipped, so
        # reprocessing the same paper is a no-op and a new version only appears when there
        # is genuinely new evidence (review question 2).
        seen = set(topic.supporting_evidence) | set(topic.contradicting_evidence)
        reviews = [r for r in reviews if evidence_label(r) not in seen]

        merged = self.merger.merge(topic.name or topic.topic_id, reviews)
        log.emit("EvidenceMerged", topic=topic.topic_id, n=merged.count)

        assessment = self.consensus.assess(topic, merged)

        # Irrelevant evidence changes nothing: no version bump, no delta (KNOWLEDGE_DELTAS: one
        # change -> one Delta, or none).
        if assessment.impact is Impact.irrelevant:
            return ConsolidationResult(topic, Impact.irrelevant, None, log.names(), changed=False)

        from_version = topic.version
        controversy_changes = self.controversies.update(topic, merged, when)
        if controversy_changes:
            log.emit("ControversyAdded", topic=topic.topic_id, changes=controversy_changes)

        event = self.confidence.apply(topic, assessment.impact, merged, when)
        log.emit("ConfidenceUpdated", topic=topic.topic_id,
                 before=event.confidence_before, after=event.confidence_after)

        # Update the topic's evidence lists (traceability), then publish a new version.
        for label, stance in zip(merged.labels, merged.stances):
            if stance == "contradict" and label not in topic.contradicting_evidence:
                topic.contradicting_evidence.append(label)
            elif stance in ("reinforce", "neutral") and label not in topic.supporting_evidence:
                topic.supporting_evidence.append(label)
        # Carry the open questions raised by the reviews (dedup) — feeds the Executive Report.
        for r in merged.reviews:
            for q in r.open_questions:
                if q and q not in topic.open_questions:
                    topic.open_questions.append(q)

        to_version = from_version + 1
        topic.version = to_version
        if assessment.consensus_changed:
            log.emit("ConsensusChanged", topic=topic.topic_id, impact=str(assessment.impact))

        delta = self.deltas.generate(
            topic,
            impact=assessment.impact,
            event=event,
            controversy_changes=controversy_changes,
            evidence=merged.labels,
            from_version=from_version,
            to_version=to_version,
            produced_by=produced_by,
            when=when,
            consensus_note=assessment.note,
        )
        log.emit("TopicPublished", topic=topic.topic_id, version=to_version)

        return ConsolidationResult(topic, assessment.impact, delta, log.names(), changed=True)
