"""Service ports — external capabilities the core depends on.

Concrete adapters (ClaudeAIReviewer, PubMedSearcher, ObsidianRenderer, ...) live in
src/infrastructure/. The core stays ignorant of any specific model or tool.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import ClinicalTopic, Paper, PaperReview


class AIReviewer(ABC):
    """Turns a Paper into a structured PaperReview (role: Paper Reviewer)."""

    @abstractmethod
    def review(self, paper: Paper) -> PaperReview: ...


class LiteratureSearcher(ABC):
    """Finds candidate Papers for a topic (role: Literature Collector)."""

    @abstractmethod
    def search(self, topic_id: str, query: str = "") -> List[Paper]: ...


class KnowledgeRenderer(ABC):
    """Renders a domain object into a view (e.g. Markdown for Obsidian)."""

    @abstractmethod
    def render_topic(self, topic: ClinicalTopic) -> str: ...
