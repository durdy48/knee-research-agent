#!/usr/bin/env python3
"""Benchmark tests — metrics correctness + runner, with a fake reviewer.

Run: python3 src/tests/test_benchmark.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark import BenchmarkRunner, load_dataset  # noqa: E402
from benchmark.dataset import GoldClaim, GoldEntry, GoldStandard, GoldTopic  # noqa: E402
from benchmark.metrics import evaluate_entry, evaluate_topic  # noqa: E402
from core.models import Claim, Paper, PaperReview  # noqa: E402
from core.ports.services import AIReviewer  # noqa: E402
from infrastructure.ai.stub import StubAIReviewer  # noqa: E402


class FakeReviewer(AIReviewer):
    """Returns two claims that match the gold and one hallucination."""

    def review(self, paper: Paper) -> PaperReview:
        return PaperReview(
            paper_id=paper.paper_id,
            title=paper.title,
            claims=[
                Claim(claim_id="C1", text="PRP improves clinical outcomes compared with HA in knee osteoarthritis", supporting_data="meta-analysis"),
                Claim(claim_id="C2", text="PRP superior to HA in WOMAC and VAS at 3 6 and 12 months", supporting_data="pooled"),
                Claim(claim_id="C3", text="Stem cells regenerate a full meniscus in one week", supporting_data="none"),
            ],
        )


def main() -> int:
    gold = GoldStandard(
        name="fixture",
        areas={"PRP": 1},
        entries=[
            GoldEntry(
                gold_id="GOLD-TEST-001",
                area="PRP",
                title="PRP vs HA",
                status="curated",
                gold_claims=[
                    GoldClaim(text="Intra-articular PRP improves clinical outcomes compared with HA in knee osteoarthritis."),
                    GoldClaim(text="PRP was superior to HA in WOMAC and VAS at 3, 6 and 12 months."),
                    GoldClaim(text="Leukocyte-poor PRP may be superior to leukocyte-rich PRP in IKDC scores."),
                ],
            )
        ],
    )

    # Unit: metric computation on a single entry.
    review = FakeReviewer().review(Paper(paper_id="X", title="t"))
    m = evaluate_entry("GOLD-TEST-001", review.claims, gold.entries[0].gold_claims)
    assert m.gold == 3 and m.produced == 3
    assert abs(m.coverage - 2 / 3) < 1e-3, m.coverage      # 2 of 3 gold recovered
    assert m.hallucinations == 1                            # the meniscus claim
    assert m.traceability == 1.0                            # all produced have supporting_data

    # Runner with the fake reviewer.
    res = BenchmarkRunner(FakeReviewer(), "fake").run(gold)
    assert res.n_entries == 1 and res.hallucinations == 1
    assert abs(res.coverage - 2 / 3) < 1e-3

    # Runner with the stub: honest zero coverage (it fabricates nothing).
    res_stub = BenchmarkRunner(StubAIReviewer(), "stub").run(gold)
    assert res_stub.coverage == 0.0 and res_stub.hallucinations == 0

    # Topic-level check (Gold Topics): consensus + confidence range + key-claim coverage.
    gt = GoldTopic(
        topic_id="TOPIC-PRP",
        name="PRP",
        expected_consensus="PRP tends to improve pain and function versus hyaluronic acid in knee osteoarthritis",
        min_confidence=0.6,
        max_confidence=0.9,
        key_claims=["PRP improves clinical outcomes compared with HA in knee osteoarthritis"],
    )
    t = evaluate_topic(
        "PRP tends to improve pain and function versus hyaluronic acid in knee osteoarthritis",
        0.75,
        ["PRP improves clinical outcomes compared with HA in knee osteoarthritis"],
        gt,
    )
    assert t["consensus_match"] and t["confidence_ok"] and t["key_coverage"] == 1.0
    # Out-of-range confidence fails the check.
    t_bad = evaluate_topic("unrelated text", 0.2, [], gt)
    assert not t_bad["confidence_ok"] and not t_bad["consensus_match"]

    # The real seed dataset loads: 3 parts present.
    real = load_dataset(name="gold-standard")
    assert len(real.curated()) >= 1
    assert real.areas.get("PRP") == 6
    assert len(real.gold_topics) >= 1 and real.gold_topics[0].topic_id == "TOPIC-PRP"

    print("OK — benchmark test passed (metrics + topic check + runner + 3-part dataset)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
