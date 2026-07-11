"""Use case: consolidate evidence into a topic by applying a knowledge event.

Role: Knowledge Consolidator (+ Change Analyzer providing the impact). Uses the pure
domain `knowledge_engine`; history and confidence are handled by the domain.
"""
from __future__ import annotations

from typing import Optional, Tuple

from core.knowledge_engine import apply_event
from core.models import ClinicalTopic
from core.models.enums import Impact
from core.models.topic import EvolutionEvent
from core.ports.repositories import TopicRepository


class ConsolidateTopic:
    def __init__(self, topics: TopicRepository) -> None:
        self.topics = topics

    def execute(
        self,
        topic_id: str,
        name: Optional[str] = None,
        *,
        impact: Impact = Impact.new,
        papers_added: int = 1,
        summary: str = "",
    ) -> Tuple[ClinicalTopic, EvolutionEvent]:
        topic = self.topics.get(topic_id)
        if topic is None:
            topic = ClinicalTopic(topic_id=topic_id, name=name or topic_id.split("-", 1)[-1])
        event = apply_event(topic, impact=impact, papers_added=papers_added, summary=summary)
        self.topics.save(topic)
        return topic, event
