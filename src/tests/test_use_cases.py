#!/usr/bin/env python3
"""Use-case tests — hexagonal core with in-memory adapters (no external models).

Run: python3 src/tests/test_use_cases.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from application.use_cases import ConsolidateTopic, IngestPaper, ReviewPaper  # noqa: E402
from core.models import Paper  # noqa: E402
from core.models.enums import Impact  # noqa: E402
from infrastructure.ai.stub import StubAIReviewer  # noqa: E402
from infrastructure.repositories.in_memory import (  # noqa: E402
    InMemoryPaperRepository,
    InMemoryTopicRepository,
)


def main() -> int:
    papers = InMemoryPaperRepository()
    topics = InMemoryTopicRepository()
    reviewer = StubAIReviewer()

    # ingest
    p = Paper(paper_id="PAPER-2026-0001", title="PRP vs HA", topics=["TOPIC-PRP"])
    IngestPaper(papers).execute(p)
    assert papers.get("PAPER-2026-0001").status == "pending_review"
    assert papers.find_by_status("pending_review")

    # review (through the AIReviewer port)
    review = ReviewPaper(papers, reviewer).execute("PAPER-2026-0001")
    assert review.paper_id == "PAPER-2026-0001"
    assert papers.get("PAPER-2026-0001").status == "reviewed"

    # consolidate (through the knowledge engine)
    topic, event = ConsolidateTopic(topics).execute(
        "TOPIC-PRP", impact=Impact.new, papers_added=1, summary="First consolidation."
    )
    assert topics.get("TOPIC-PRP") is not None
    assert event.confidence_after > event.confidence_before
    assert len(topics.get("TOPIC-PRP").events) == 1

    # a second consolidation keeps history
    ConsolidateTopic(topics).execute("TOPIC-PRP", impact=Impact.reinforcement, papers_added=2)
    assert len(topics.get("TOPIC-PRP").events) == 2

    print("OK — use-case test passed (ingest -> review -> consolidate, in-memory)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
