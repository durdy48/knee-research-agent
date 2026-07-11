"""Benchmark Runner — the single Sprint-5A pipeline stage.

    Paper -> reviewer.review() -> PaperReview -> Quality Gates -> score vs Gold Review

Nothing else: no Topic Update, no Report, no Knowledge Evolution. It reviews each curated
Gold Paper, runs the Quality Gates, and scores the review with the full metric set
(coverage, traceability, GRSS, CDR, UCR). Swap the reviewer to compare providers.
"""
from __future__ import annotations

from time import perf_counter
from typing import Optional

from application.quality_gates import check_review
from core.models import Paper
from core.ports.services import AIReviewer
from infrastructure.ai import ReviewPendingError
from infrastructure.sources import LocalAbstractSource
from .dataset import GoldStandard
from .metrics import BenchmarkResult, aggregate, evaluate_entry_full


class BenchmarkRunner:
    def __init__(
        self,
        reviewer: AIReviewer,
        model_name: str = "stub",
        *,
        abstract_source: Optional[LocalAbstractSource] = None,
    ) -> None:
        self.reviewer = reviewer
        self.model_name = model_name
        # Resolves real, human-provided abstracts so the reviewer works on source text,
        # not just title/metadata. Never fabricates. Missing abstracts -> None.
        self.abstract_source = abstract_source or LocalAbstractSource()

    def run(self, gold: GoldStandard) -> BenchmarkResult:
        results = []
        pending = []
        for entry in gold.curated():
            abstract = entry.abstract or self.abstract_source.get(
                entry.gold_id, entry.pmid, entry.doi
            )
            paper = Paper(
                paper_id=entry.gold_id,
                title=entry.title,
                doi=entry.doi,
                pmid=entry.pmid,
                year=entry.year,
                abstract=abstract,
                study_type=entry.study_type,
                topics=[entry.area],
            )
            t0 = perf_counter()
            try:
                review = self.reviewer.review(paper)
            except ReviewPendingError:
                pending.append(entry.gold_id)  # manual mode: not reviewed yet
                continue
            dt = perf_counter() - t0

            gate = check_review(review)
            results.append(
                evaluate_entry_full(
                    entry,
                    review,
                    time_s=dt,
                    passed_gate=gate.passed,
                    gate_violations=gate.violations,
                )
            )
        result = aggregate(self.model_name, results)
        result.pending = pending
        return result
