"""Paper Ingestion — the first vertical slice, now built on the workflow framework.

It is a composition of steps run by the WorkflowRunner. Once these steps exist,
topic_update and monthly_research are just other compositions on the same engine.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from application.use_cases import IngestPaper, ReviewPaper
from core.models import Paper
from core.ports.repositories import PaperRepository, ReviewStore
from core.ports.services import AIReviewer
from framework import WorkflowContext, WorkflowRunner, WorkflowStep


class CreatePaperStep(WorkflowStep):
    name = "create_paper"

    def __init__(self, papers: PaperRepository) -> None:
        self.papers = papers
        self.ingest = IngestPaper(papers)

    def run(self, ctx: WorkflowContext) -> None:
        d = ctx.data
        # Idempotency: if the same DOI is already registered, reuse it (no duplicate data).
        if d.get("doi"):
            existing = next(
                (p for p in self.papers.list_all() if p.doi and p.doi == d["doi"]), None
            )
            if existing is not None:
                d["paper_id"] = existing.paper_id
                ctx.emit("paper.exists", paper_id=existing.paper_id)
                return
        paper_id = (
            self.papers.next_id()  # type: ignore[attr-defined]
            if hasattr(self.papers, "next_id")
            else f"PAPER-{date.today().year}-0001"
        )
        paper = Paper(
            paper_id=paper_id,
            title=d.get("title") or d.get("doi") or "Untitled",
            doi=d.get("doi"),
            pmid=d.get("pmid"),
            year=d.get("year"),
            topics=d.get("topics") or [],
        )
        self.ingest.execute(paper)
        d["paper_id"] = paper_id
        ctx.emit("paper.created", paper_id=paper_id)


class ReviewPaperStep(WorkflowStep):
    name = "review_paper"

    def __init__(self, papers: PaperRepository, reviewer: AIReviewer) -> None:
        self.review = ReviewPaper(papers, reviewer)

    def run(self, ctx: WorkflowContext) -> None:
        paper_id = ctx.data["paper_id"]
        review = self.review.execute(paper_id)
        review.paper_id = paper_id
        ctx.data["review"] = review
        ctx.metrics.claims += len(review.claims)
        ctx.emit("paper.reviewed", paper_id=paper_id, claims=len(review.claims))


class SaveArtifactsStep(WorkflowStep):
    name = "save_artifacts"

    def __init__(self, papers: PaperRepository, reviews: ReviewStore) -> None:
        self.papers = papers
        self.reviews = reviews

    def run(self, ctx: WorkflowContext) -> None:
        review = ctx.data["review"]
        saved = self.reviews.save(review)
        paper = self.papers.get(ctx.data["paper_id"])
        paper.review = saved["review"]
        paper.claims = saved["claims"]
        self.papers.save(paper)
        ctx.data["artifacts"] = saved
        ctx.emit("review.saved", **saved)


class PaperIngestionWorkflow:
    def __init__(self, papers: PaperRepository, reviewer: AIReviewer, reviews: ReviewStore) -> None:
        self.papers = papers
        self.runner = WorkflowRunner(
            [
                CreatePaperStep(papers),
                ReviewPaperStep(papers, reviewer),
                SaveArtifactsStep(papers, reviews),
            ],
            name="paper_ingestion",
        )

    def run(
        self,
        *,
        doi: Optional[str] = None,
        title: Optional[str] = None,
        pmid: Optional[str] = None,
        year: Optional[int] = None,
        topics: Optional[List[str]] = None,
    ) -> dict:
        ctx = WorkflowContext(
            data={"doi": doi, "title": title, "pmid": pmid, "year": year, "topics": topics or []}
        )
        ctx = self.runner.run(ctx)
        paper_id = ctx.data["paper_id"]
        saved = ctx.data["artifacts"]
        return {
            "paper_id": paper_id,
            "status": self.papers.get(paper_id).status,
            "state": ctx.state.value,
            "review": saved["review"],
            "claims": saved["claims"],
            "n_claims": ctx.metrics.claims,
            "duration_s": ctx.metrics.duration_s,
            "steps": list(ctx.metrics.steps.keys()),
        }
