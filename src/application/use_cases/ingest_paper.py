"""Use case: register a paper (Literature Collector -> Paper Registry)."""
from __future__ import annotations

from core.models import Paper
from core.models.enums import PaperStatus
from core.ports.repositories import PaperRepository


class IngestPaper:
    def __init__(self, papers: PaperRepository) -> None:
        self.papers = papers

    def execute(self, paper: Paper) -> Paper:
        paper.status = PaperStatus.pending_review.value
        self.papers.save(paper)
        return paper
