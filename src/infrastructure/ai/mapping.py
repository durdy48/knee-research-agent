"""Shared mapping: a review dict (from a model or a human) -> PaperReview.

Both the ClaudeAIReviewer (API) and the ManualAIProvider (human-in-the-loop / Claude Code
as engine) receive the SAME JSON shape and build the SAME PaperReview through this module.
That is what lets the manual mode be swapped for the API later without changing anything
else — the review package's schema is this contract.
"""
from __future__ import annotations

import json
from typing import Optional

from core.models import Claim, Paper, PaperReview, classify_evidence

from .normalize import normalize_study_type

# The keys a review dict may carry (the review-package schema).
REVIEW_KEYS = (
    "study_type", "evidence_level", "primary_findings", "main_limitations",
    "contradicts_existing", "reinforces_existing", "open_questions", "claims",
)


def build_review(paper: Paper, data: dict, notes: str = "") -> PaperReview:
    raw_study_type = data.get("study_type") or paper.study_type
    # Evidence Classification is derived from the study type (stars for graded designs,
    # a category for guidelines/consensus/scoping) unless the reviewer states it.
    evidence_class = data.get("evidence_class") or classify_evidence(raw_study_type)
    claims = []
    for i, c in enumerate(data.get("claims", []) or [], start=1):
        claims.append(
            Claim(
                claim_id=c.get("claim_id") or f"C{i}",
                text=(c.get("text") or "").strip(),
                supporting_data=(c.get("supporting_data") or "").strip(),
                evidence_level=c.get("evidence_level"),
                needs_full_text_confirmation=bool(c.get("needs_full_text_confirmation", True)),
            )
        )
    return PaperReview(
        paper_id=paper.paper_id,
        title=paper.title,
        doi=paper.doi,
        pmid=paper.pmid,
        year=paper.year,
        study_type=normalize_study_type(raw_study_type),
        evidence_level=data.get("evidence_level"),
        evidence_class=evidence_class,
        clinical_topics=list(paper.topics),
        primary_findings=data.get("primary_findings", "") or "",
        main_limitations=data.get("main_limitations", []) or [],
        contradicts_existing=data.get("contradicts_existing"),
        reinforces_existing=data.get("reinforces_existing"),
        open_questions=data.get("open_questions", []) or [],
        claims=claims,
        ai_review_notes=notes,
    )


def extract_json(text: str) -> dict:
    """Parse a JSON object, tolerating code fences or stray prose around it."""
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{") :] if "{" in text else text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise
