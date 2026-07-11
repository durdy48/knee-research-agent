"""In-memory repository adapters — used for tests and dry runs.

They implement the core ports without any persistence, so the domain and use cases can
be validated without touching Markdown, Git or a database.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from core.models import ClinicalTopic, Paper
from core.ports.repositories import PaperRepository, TopicRepository


class InMemoryPaperRepository(PaperRepository):
    def __init__(self) -> None:
        self._store: Dict[str, Paper] = {}

    def get(self, paper_id: str) -> Optional[Paper]:
        p = self._store.get(paper_id)
        return p.model_copy(deep=True) if p else None

    def save(self, paper: Paper) -> None:
        self._store[paper.paper_id] = paper.model_copy(deep=True)

    def list_all(self) -> List[Paper]:
        return [p.model_copy(deep=True) for p in self._store.values()]

    def find_by_status(self, status: str) -> List[Paper]:
        return [p.model_copy(deep=True) for p in self._store.values() if str(p.status) == status]


class InMemoryTopicRepository(TopicRepository):
    def __init__(self) -> None:
        self._store: Dict[str, ClinicalTopic] = {}

    def get(self, topic_id: str) -> Optional[ClinicalTopic]:
        t = self._store.get(topic_id)
        return t.model_copy(deep=True) if t else None

    def save(self, topic: ClinicalTopic) -> None:
        self._store[topic.topic_id] = topic.model_copy(deep=True)

    def list_all(self) -> List[ClinicalTopic]:
        return [t.model_copy(deep=True) for t in self._store.values()]
