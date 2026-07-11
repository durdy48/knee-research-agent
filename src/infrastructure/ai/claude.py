"""ClaudeAIReviewer — the real AIReviewer adapter (AIProvider) backed by Anthropic.

This is the single, controlled integration point of Sprint 5A:

    Paper -> ClaudeAIReviewer -> PaperReview (Pydantic) -> Quality Gates -> Benchmark

It performs NO knowledge consolidation, NO reporting and NO evolution — it only turns
one Paper into one structured PaperReview, so the benchmark can answer the one question
that matters now: *can an LLM produce reviews that approach the Gold Standard?*

The adapter needs an Anthropic API key (``KRA_ANTHROPIC_API_KEY`` or ``ANTHROPIC_API_KEY``).
Without a key it raises a clear error instead of guessing — the core golden rule is to
never invent evidence. The whole harness around it is exercised with the stub / fake
providers, so the user only has to plug in a key and run.
"""
from __future__ import annotations

import os
from typing import Optional

from core.models import Paper, PaperReview
from core.ports.services import AIReviewer

from .mapping import build_review, extract_json

# The extraction contract handed to the model. It mirrors PaperReview and is deliberately
# strict: extract only what the source supports, never invent, and surface controversy.
_SYSTEM_PROMPT = """You are a scientific Paper Reviewer for an evidence-based knowledge \
platform on knee osteoarthritis. Extract a structured review of a single paper.

Hard rules:
- Never invent data, figures, citations or findings. If the source does not support a \
statement, do not make it.
- Every claim MUST carry its supporting_data (the specific result/number/quote it rests \
on). Claims without support are not allowed.
- Preserve uncertainty: if the paper contradicts prevailing evidence or reports a null/ \
negative result, say so explicitly in contradicts_existing and in the relevant claim.
- Assign study_type and evidence_level (1-5) only if the source makes them clear.
- Mark needs_full_text_confirmation=true for anything taken from title/abstract alone.

Return ONLY a JSON object with keys: study_type (string), evidence_level (int 1-5 or null), \
primary_findings (string), main_limitations (list of strings), contradicts_existing \
(string or null), reinforces_existing (string or null), open_questions (list of strings), \
claims (list of objects with: text, supporting_data, evidence_level (int or null), \
needs_full_text_confirmation (bool)). No prose outside the JSON."""


class ClaudeAIReviewer(AIReviewer):
    """Real reviewer. Constructed cheaply; the key is only required when ``review`` runs."""

    def __init__(self, *, api_key: Optional[str] = None, model: str = "claude-sonnet-5") -> None:
        self._api_key = api_key or os.getenv("KRA_ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self._model = model

    # -- helpers -----------------------------------------------------------------
    def _require_key(self) -> str:
        if not self._api_key:
            raise RuntimeError(
                "ClaudeAIReviewer needs an Anthropic API key. Set KRA_ANTHROPIC_API_KEY "
                "(or ANTHROPIC_API_KEY) and re-run. The rest of the harness runs with the "
                "'stub' or 'fake' providers without a key."
            )
        return self._api_key

    def _build_user_prompt(self, paper: Paper) -> str:
        abstract = paper.abstract or ""
        parts = [f"Title: {paper.title}"]
        if paper.study_type:
            parts.append(f"Registry study_type: {paper.study_type}")
        if paper.topics:
            parts.append(f"Clinical area(s): {', '.join(paper.topics)}")
        if paper.doi:
            parts.append(f"DOI: {paper.doi}")
        if abstract:
            parts.append(f"Abstract:\n{abstract}")
        else:
            parts.append(
                "No abstract/full text was provided; review only what the metadata "
                "supports and set needs_full_text_confirmation=true on every claim."
            )
        return "\n".join(parts)

    # -- port --------------------------------------------------------------------
    def review(self, paper: Paper) -> PaperReview:
        self._require_key()
        try:
            import anthropic  # lazy: only needed for a real run
        except ImportError as e:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "The 'anthropic' package is not installed. Run: pip install anthropic"
            ) from e

        client = anthropic.Anthropic(api_key=self._api_key)
        msg = client.messages.create(
            model=self._model,
            max_tokens=2000,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": self._build_user_prompt(paper)}],
        )
        text = "".join(getattr(b, "text", "") for b in msg.content).strip()
        data = extract_json(text)
        return build_review(paper, data, notes=f"Reviewed by ClaudeAIReviewer ({self._model}).")
