"""ManualAIProvider — human-in-the-loop / Claude-Code-as-engine reviewer (no API key).

Two halves of the same contract:

  1. build_review_package(paper, out_dir): KRA emits a package the engine can consume —
     prompt.md (the extraction instructions), schema.json (the expected JSON shape) and
     metadata.json (the paper identifiers). You open it with Claude (Code or web), produce
     the review, and save it as <paper_id>.json.

  2. ManualAIProvider(reviews_dir).review(paper): KRA reads the saved review back and turns
     it into a PaperReview — the SAME shape the API adapter would return. The day an API key
     appears, swap ManualAIProvider for ClaudeAIReviewer and nothing else changes.

A missing review raises ReviewPendingError so the benchmark can report what is still pending
instead of inventing anything.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from core.models import Paper, PaperReview
from core.ports.services import AIReviewer
from core.storage import paths

from .mapping import REVIEW_KEYS, build_review

_EXTRACTION_PROMPT = """You are a scientific Paper Reviewer for an evidence-based knowledge \
platform on knee osteoarthritis. Produce a structured review of the paper below.

Hard rules:
- Never invent data, figures, citations or findings. If the source does not support a \
statement, do not make it.
- Every claim MUST carry its supporting_data (the specific result/number/quote it rests on).
- Preserve uncertainty: if the paper contradicts prevailing evidence or reports a null / \
negative result, say so in contradicts_existing and in the relevant claim.
- Assign study_type and evidence_level (1-5) only if the source makes them clear.
- Set needs_full_text_confirmation=true for anything taken from title/abstract alone.

Return ONLY the JSON object described in schema.json — no prose around it."""

_SCHEMA = {
    "study_type": "string (e.g. 'Meta-analysis', 'Randomized Controlled Trial', ...)",
    "evidence_level": "int 1-5 or null",
    "primary_findings": "string",
    "main_limitations": ["string"],
    "contradicts_existing": "string or null",
    "reinforces_existing": "string or null",
    "open_questions": ["string"],
    "claims": [
        {
            "text": "string",
            "supporting_data": "string (required)",
            "evidence_level": "int 1-5 or null",
            "needs_full_text_confirmation": "bool",
        }
    ],
}


class ReviewPendingError(RuntimeError):
    """Raised when no manual review exists yet for a paper."""


def build_review_package(paper: Paper, out_dir: Path) -> Path:
    """Write prompt.md, schema.json and metadata.json for one paper. Returns the folder."""
    folder = Path(out_dir) / paper.paper_id
    folder.mkdir(parents=True, exist_ok=True)

    body = [f"# Review task: {paper.paper_id}", "", _EXTRACTION_PROMPT, "", "## Paper", f"- Title: {paper.title}"]
    if paper.study_type:
        body.append(f"- Study type (registry): {paper.study_type}")
    if paper.topics:
        body.append(f"- Clinical area(s): {', '.join(paper.topics)}")
    if paper.doi:
        body.append(f"- DOI: {paper.doi}")
    if paper.pmid:
        body.append(f"- PMID: {paper.pmid}")
    body.append("")
    body.append("## Abstract")
    body.append(paper.abstract or "(none provided — review from metadata and flag needs_full_text_confirmation=true)")

    (folder / "prompt.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    (folder / "schema.json").write_text(json.dumps(_SCHEMA, indent=2) + "\n", encoding="utf-8")
    (folder / "metadata.json").write_text(
        json.dumps(
            {"paper_id": paper.paper_id, "title": paper.title, "doi": paper.doi,
             "pmid": paper.pmid, "year": paper.year, "area": paper.topics},
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    return folder


class ManualAIProvider(AIReviewer):
    def __init__(self, reviews_dir: Optional[Path] = None) -> None:
        self.reviews_dir = Path(reviews_dir) if reviews_dir else (paths.root() / "runs" / "manual" / "reviews")

    def _load(self, paper_id: str) -> Optional[dict]:
        # 1) per-paper file: <reviews_dir>/<paper_id>.json
        per = self.reviews_dir / f"{paper_id}.json"
        if per.is_file():
            return json.loads(per.read_text(encoding="utf-8"))
        # 2) combined map: <reviews_dir>/reviews.json = {paper_id: review}
        combined = self.reviews_dir / "reviews.json"
        if combined.is_file():
            data = json.loads(combined.read_text(encoding="utf-8"))
            if paper_id in data:
                return data[paper_id]
        return None

    def review(self, paper: Paper) -> PaperReview:
        data = self._load(paper.paper_id)
        if data is None:
            raise ReviewPendingError(
                f"no manual review for '{paper.paper_id}'. Generate its package with "
                f"'kra review-package' and save the answer as {paper.paper_id}.json (or add "
                f"it to reviews.json) in {self.reviews_dir}."
            )
        return build_review(paper, data, notes="Manual review (human-in-the-loop / Claude Code engine).")
