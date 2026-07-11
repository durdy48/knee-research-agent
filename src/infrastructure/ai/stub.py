"""Stub AI reviewer — a deterministic AIReviewer adapter for tests and dry runs.

It does NOT read the paper or invent medical data; it returns an empty, clearly-marked
PaperReview scaffold. The real ClaudeAIReviewer is a Sprint 3B adapter.
"""
from __future__ import annotations

from core.models import Paper, PaperReview
from core.ports.services import AIReviewer

from .normalize import normalize_study_type


class StubAIReviewer(AIReviewer):
    def review(self, paper: Paper) -> PaperReview:
        return PaperReview(
            paper_id=paper.paper_id,
            title=paper.title,
            doi=paper.doi,
            pmid=paper.pmid,
            year=paper.year,
            study_type=normalize_study_type(paper.study_type),
            clinical_topics=list(paper.topics),
            ai_review_notes="Stub reviewer: no content extracted. To be filled by a real reviewer.",
        )
