#!/usr/bin/env python3
"""Definition of Done — automated check for the paper_ingestion workflow.

Verifies the criteria in docs/DEFINITION_OF_DONE.md on an isolated temp root.
Run: python3 src/tests/test_definition_of_done.py
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="kra-dod-"))
    os.environ["KRA_ROOT"] = str(tmp)

    from application.workflows.paper_ingestion import PaperIngestionWorkflow
    from core.models import PaperReview
    from core.storage import paths
    from framework import WorkflowContext, WorkflowState
    from infrastructure.ai.stub import StubAIReviewer
    from infrastructure.repositories.file_review_store import FileReviewStore
    from infrastructure.repositories.json_registry import JsonPaperRepository

    wf = PaperIngestionWorkflow(JsonPaperRepository(), StubAIReviewer(), FileReviewStore())

    # Run through the runner with our own context so we can inspect events + metrics.
    seen = []
    ctx = WorkflowContext(data={"doi": "10.1000/dod", "title": "DoD demo", "year": 2025, "topics": ["TOPIC-PRP"]})
    ctx.events.subscribe("*", lambda e: seen.append(e.name))
    ctx = wf.runner.run(ctx)

    # 1. Unique identifier
    assert re.match(r"^PAPER-\d{4}-\d{4}$", ctx.data["paper_id"]), ctx.data["paper_id"]
    # 2. Typed validation: PaperReview validates against Pydantic
    review = ctx.data["review"]
    assert isinstance(review, PaperReview)
    PaperReview.model_validate(review.model_dump())
    # 4. Execution metrics
    assert ctx.metrics.duration_s >= 0 and len(ctx.metrics.steps) == 3
    # 5. Events emitted
    for name in ("workflow.started", "paper.created", "paper.reviewed", "review.saved", "workflow.completed"):
        assert name in seen, name
    # 9. Artifacts saved
    artifacts = ctx.data["artifacts"]
    assert (tmp / artifacts["review"]).exists() and (tmp / artifacts["claims"]).exists()
    # 3. Traceability: claims.json links to the paper
    claims_doc = json.loads((tmp / artifacts["claims"]).read_text(encoding="utf-8"))
    assert claims_doc["paper_id"] == ctx.data["paper_id"]
    assert "source_review" in claims_doc
    for c in claims_doc["claims"]:
        assert c.get("claim_id")
    # 10. Final state recorded
    assert ctx.state == WorkflowState.completed

    # 8. Idempotent by DOI: re-running the same DOI does not duplicate
    wf.run(doi="10.1000/dod", title="DoD demo again", year=2025)
    reg = json.loads(paths.registry_file().read_text(encoding="utf-8"))
    dod_papers = [p for p in reg["papers"] if p.get("doi") == "10.1000/dod"]
    assert len(dod_papers) == 1, f"idempotency broken: {len(dod_papers)} entries"

    shutil.rmtree(tmp, ignore_errors=True)
    print("OK — Definition of Done satisfied for paper_ingestion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
