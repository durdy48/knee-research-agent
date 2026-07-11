"""Paper Ingestion workflow (coordination only — see agents/workflows/paper-ingestion.md).

Chains the stages for a single paper and records the run. Workflows contain no
intelligence; they sequence roles/stages.
"""
from __future__ import annotations

from core.pipeline import stages
from core.storage import runs


def run(paper_id: str) -> dict:
    run_id = runs.next_run_id()
    log = runs.create(run_id, "Paper Ingestion (manual)", goal=f"Ingest {paper_id} end to end.")
    review_path = stages.review(paper_id)
    runs.step(log, f"Paper Reviewer -> {review_path.name}")
    runs.step(log, "Evidence Evaluator / Knowledge Consolidator: pending (run `kra consolidate`).")
    return {"run_id": run_id, "review": str(review_path)}
