"""Quality Gates — the checkpoint between a produced PaperReview and the Benchmark.

    Paper -> ClaudeAIReviewer -> PaperReview -> [Quality Gates] -> Benchmark

Gates enforce the project's golden rules *before* a review is allowed to count:
traceability (every claim carries its supporting data), metadata completeness (study
type and evidence level assigned) and non-emptiness. A review that fails the gates is
still scored (so the numbers are visible) but flagged, so a model that fabricates or
omits grounding cannot silently pass.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from core.models import PaperReview
from core.models.enums import EvidenceClass


@dataclass
class GateResult:
    passed: bool
    violations: List[str] = field(default_factory=list)


def check_review(review: PaperReview) -> GateResult:
    v: List[str] = []

    if not review.claims:
        v.append("no claims extracted")
    for c in review.claims:
        if not (c.text or "").strip():
            v.append(f"claim {c.claim_id}: empty text")
        if not (c.supporting_data or "").strip():
            v.append(f"claim {c.claim_id}: missing supporting_data (untraceable)")

    if review.study_type is None:
        v.append("study_type not identified")

    # Evidence must be CLASSIFIED, not necessarily on the 1-5 scale. A guideline or
    # scoping review is valid with a categorical class (Consensus / Exploratory); only
    # 'unclassified' (or nothing) fails the gate.
    classified = review.evidence_level is not None or (
        review.evidence_class not in (None, EvidenceClass.unclassified)
    )
    if not classified:
        v.append("evidence not classified (no level and no evidence_class)")

    return GateResult(passed=len(v) == 0, violations=v)
