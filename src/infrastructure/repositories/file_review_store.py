"""FileReviewStore — persists a PaperReview as reviews/paper-reviews/<slug>.md + .claims.json."""
from __future__ import annotations

import json
import re
from datetime import date
from typing import Dict

from core.models import PaperReview
from core.ports.repositories import ReviewStore
from core.storage import paths
from infrastructure.renderers.markdown import render_paper_review


def _slug(text: str, maxlen: int = 60) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:maxlen] or "untitled"


class FileReviewStore(ReviewStore):
    def save(self, review: PaperReview) -> Dict[str, str]:
        year = review.year or date.today().year
        name = f"{year}-{_slug(review.title)}"
        paths.ensure(paths.reviews_dir())

        review_path = paths.reviews_dir() / f"{name}.md"
        review_path.write_text(render_paper_review(review), encoding="utf-8")

        claims_path = paths.reviews_dir() / f"{name}.claims.json"
        claims_doc = {
            "schema_version": "1.0",
            "paper_id": review.paper_id,
            "source_review": str(review_path.relative_to(paths.root())),
            "claims": [c.model_dump(mode="json") for c in review.claims],
        }
        claims_path.write_text(
            json.dumps(claims_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

        return {
            "review": str(review_path.relative_to(paths.root())),
            "claims": str(claims_path.relative_to(paths.root())),
        }
