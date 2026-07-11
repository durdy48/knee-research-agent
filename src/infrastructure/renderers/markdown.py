"""Markdown renderers — domain objects rendered into views.

Objects are the source of truth; Markdown is a view (see the architecture discussion).
"""
from __future__ import annotations

from core.models import PaperReview


def _stars(level) -> str:
    try:
        return "★" * int(level)
    except (TypeError, ValueError):
        return ""


def render_paper_review(review: PaperReview) -> str:
    """Render a PaperReview object as the paper-review data-contract Markdown."""
    lines = [
        "# Paper Review",
        "",
        "**Status:** Immutable",
        f"**Paper:** {review.paper_id or ''}",
        f"**Review Version:** 1.0",
        "",
        "---",
        "",
        "# Paper Metadata",
        "",
        f"## Title\n\n{review.title}",
        f"## Authors\n\n{', '.join(review.authors)}",
        f"## Journal\n\n{review.journal or ''}",
        f"## Publication Year\n\n{review.year or ''}",
        f"## DOI\n\n{review.doi or ''}",
        f"## URL\n\n{review.url or ''}",
        f"## PMID\n\n{review.pmid or ''}",
        f"## Study Type\n\n{review.study_type or ''}",
        "",
        "---",
        "",
        "# Research Context",
        "",
        f"## Clinical Topics\n\n{', '.join(review.clinical_topics)}",
        f"## Research Question\n\n{review.research_question}",
        f"## Clinical Problem\n\n{review.clinical_problem}",
        "",
        "---",
        "",
        "# Claims",
        "",
        "| ID | Claim | Supporting Data |",
        "|----|-------|-----------------|",
    ]
    for c in review.claims:
        lines.append(f"| {c.claim_id} | {c.text} | {c.supporting_data} |")
    lines += [
        "",
        "---",
        "",
        "# Evidence Quality",
        "",
        f"## Study Quality\n\n{_stars(review.evidence_level)}",
        f"## Risk of Bias\n\n{review.risk_of_bias or ''}",
        "",
        "---",
        "",
        "# References",
        "",
        *[f"- {r}" for r in review.references],
        "",
        "---",
        "",
        "# AI Review Notes",
        "",
        review.ai_review_notes,
        "",
    ]
    return "\n".join(lines)
