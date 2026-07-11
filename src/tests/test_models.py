#!/usr/bin/env python3
"""Domain-model tests (Pydantic v2). Pure domain — no AI, no APIs, no storage.

Run: python3 src/tests/test_models.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC))

from core.models import (  # noqa: E402
    Claim,
    ClinicalTopic,
    EvidenceLevel,
    EvolutionEvent,
    ExecutiveReport,
    Impact,
    Insight,
    Paper,
    PaperReview,
    PatientProfile,
    PersonalContext,
    RiskOfBias,
    StudyType,
)


def main() -> int:
    # Every model instantiates.
    paper = Paper(paper_id="PAPER-2026-0001", title="PRP vs HA", study_type="Systematic Review")
    claim = Claim(claim_id="CLAIM-2026-0001", text="PRP improves outcomes vs HA", evidence_level=EvidenceLevel.meta_analysis)
    review = PaperReview(title="PRP vs HA", claims=[claim], risk_of_bias=RiskOfBias.low)
    topic = ClinicalTopic(topic_id="TOPIC-PRP", name="PRP")
    event = EvolutionEvent(topic_id="TOPIC-PRP", date="2026-07-11", impact=Impact.new, papers_added=1)
    insight = Insight(topic_id="TOPIC-PRP")
    report = ExecutiveReport(report_id="REPORT-2026-07", month="2026-07")
    ctx = PersonalContext()
    ctx.patient = PatientProfile(age=46, diagnoses=["post-traumatic knee OA"])

    # JSON round-trip keeps the object identical (objects are the source of truth).
    for obj in (paper, claim, review, topic, event, insight, report, ctx):
        data = obj.model_dump_json()
        back = type(obj).model_validate_json(data)
        assert back == obj, type(obj).__name__

    # Validation works: bad enum value is rejected.
    try:
        Paper(paper_id="X", status="not-a-status")
        raise AssertionError("expected validation error")
    except Exception:
        pass

    # Schema generation works (used for LLM structured outputs / FastAPI).
    schema = PaperReview.model_json_schema()
    assert schema["title"] == "PaperReview"
    assert "claims" in schema["properties"]
    json.dumps(schema)  # serialisable

    print("OK — domain models test passed (instantiate + JSON round-trip + validation + schema)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
