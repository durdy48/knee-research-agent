"""Consolidate a topic's knowledge from its validated reviews and persist the result.

Application-layer orchestration (hexagonal): loads validated reviews (infrastructure), runs
the pure Knowledge Consolidation Engine (core), and persists the topic + ledger
(infrastructure). Deterministic and idempotent: re-running with no new evidence is a no-op.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from application.quality_gates import check_review
from benchmark import load_dataset
from core.consolidation import KnowledgeConsolidationEngine
from core.models import ClinicalTopic, Paper
from core.storage import paths
from infrastructure.ai import ManualAIProvider
from infrastructure.repositories.knowledge_store import KnowledgeStore


def area_to_topic_id(area: str) -> str:
    return "TOPIC-" + area.upper().replace(" / ", "-").replace("/", "-").replace(" ", "-")


def _paper(entry) -> Paper:
    return Paper(
        paper_id=entry.gold_id, title=entry.title, doi=entry.doi, pmid=entry.pmid,
        year=entry.year, study_type=entry.study_type, topics=[entry.area],
    )


@dataclass
class ConsolidationRun:
    topic_id: str
    area: str
    reviewed: int
    confidence_before: float
    confidence_after: float
    version: int
    ledger_ids: List[str] = field(default_factory=list)
    skipped_gate: List[str] = field(default_factory=list)
    changed: bool = False


def consolidate_topic_knowledge(
    area: str,
    *,
    reviews_dir: Optional[Path] = None,
    produced_by: str = "manual",
    when: Optional[str] = None,
) -> ConsolidationRun:
    gold = load_dataset(name="gold-standard")
    provider = ManualAIProvider(reviews_dir or (paths.runs_dir() / "manual" / "reviews"))
    store = KnowledgeStore()
    topic_id = area_to_topic_id(area)

    topic = store.load_topic(topic_id) or ClinicalTopic(topic_id=topic_id, name=area)
    before = topic.confidence

    entries = [e for e in gold.curated() if e.area == area]
    # Reinforcing/new evidence first, contradictions last (build the consensus, then contest it).
    entries.sort(key=lambda e: (
        1 if (provider.review(_paper(e)).contradicts_existing or "").strip() else 0, e.gold_id
    ))

    eng = KnowledgeConsolidationEngine()
    run = ConsolidationRun(topic_id, area, 0, before, before, topic.version)
    for e in entries:
        review = provider.review(_paper(e))
        if not check_review(review).passed:
            run.skipped_gate.append(e.gold_id)
            continue
        run.reviewed += 1
        result = eng.consolidate(topic, [review], produced_by=produced_by, when=when)
        if result.changed and result.delta is not None:
            run.ledger_ids.append(store.append_delta(result.delta))
            run.changed = True

    if run.changed:
        store.save_topic(topic)
    run.confidence_after = topic.confidence
    run.version = topic.version
    return run
