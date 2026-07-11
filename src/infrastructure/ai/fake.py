"""FakeAIReviewer — a deterministic, key-free provider to exercise the full harness.

Unlike the stub (which extracts nothing), the fake returns a small, well-formed review:
metadata, one grounded claim and a limitation. It cannot match arbitrary Gold Reviews,
so it scores low on coverage — but it lets us test the plumbing end to end (Quality Gates,
GRSS / CDR / UCR) without an API key. Real measurement uses the 'claude' provider.
"""
from __future__ import annotations

from core.models import Claim, Paper, PaperReview
from core.ports.services import AIReviewer

from .normalize import normalize_study_type


class FakeAIReviewer(AIReviewer):
    def review(self, paper: Paper) -> PaperReview:
        return PaperReview(
            paper_id=paper.paper_id,
            title=paper.title,
            doi=paper.doi,
            pmid=paper.pmid,
            year=paper.year,
            study_type=normalize_study_type(paper.study_type) or "Other",
            evidence_level=3,
            clinical_topics=list(paper.topics),
            primary_findings="Deterministic placeholder finding for harness testing.",
            main_limitations=["Fake reviewer: content is not derived from the source."],
            claims=[
                Claim(
                    claim_id="C1",
                    text=f"{paper.title} reports outcomes relevant to {', '.join(paper.topics) or 'knee osteoarthritis'}.",
                    supporting_data="placeholder supporting data",
                    needs_full_text_confirmation=True,
                )
            ],
            ai_review_notes="Fake reviewer: deterministic output for tests, no real content.",
        )
