"""Repository ports — persistence interfaces the core depends on.

Implementations (Markdown/Git/SQLite/in-memory) live in src/infrastructure/ and are
interchangeable without changing the core.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from typing import Dict

from ..models import ClinicalTopic, Paper, PaperReview


class PaperRepository(ABC):
    @abstractmethod
    def get(self, paper_id: str) -> Optional[Paper]: ...

    @abstractmethod
    def save(self, paper: Paper) -> None: ...

    @abstractmethod
    def list_all(self) -> List[Paper]: ...

    @abstractmethod
    def find_by_status(self, status: str) -> List[Paper]: ...


class TopicRepository(ABC):
    @abstractmethod
    def get(self, topic_id: str) -> Optional[ClinicalTopic]: ...

    @abstractmethod
    def save(self, topic: ClinicalTopic) -> None: ...

    @abstractmethod
    def list_all(self) -> List[ClinicalTopic]: ...


class ReviewStore(ABC):
    """Persists a PaperReview and its Claims as artifacts (Markdown + JSON views)."""

    @abstractmethod
    def save(self, review: PaperReview) -> Dict[str, str]:
        """Return the relative paths, e.g. {'review': '...md', 'claims': '...json'}."""

