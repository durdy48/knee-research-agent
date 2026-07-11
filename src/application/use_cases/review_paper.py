"""Use case: review a paper via an AIReviewer port (role: Paper Reviewer)."""
from __future__ import annotations

from core.models import PaperReview
from core.models.enums import PaperStatus
from core.ports.repositories import PaperRepository
from core.ports.services import AIReviewer


class ReviewPaper:
    def __init__(self, papers: PaperRepository, reviewer: AIReviewer) -> None:
        self.papers = papers
        self.reviewer = reviewer

    def execute(self, paper_id: str) -> PaperReview:
        paper = self.papers.get(paper_id)
        if paper is None:
            raise KeyError(paper_id)
        review = self.reviewer.review(paper)
        paper.status = PaperStatus.reviewed.value
        self.papers.save(paper)
        return review
