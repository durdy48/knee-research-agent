#!/usr/bin/env python3
"""Sprint 5A tests — AIProvider abstraction, Quality Gates, GRSS/CDR/UCR metrics.

Everything is exercised WITHOUT an API key (stub + fake + an in-test oracle). The real
'claude' provider is only checked to construct and to fail loudly without a key.

Run: python3 src/tests/test_sprint5a.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from application.quality_gates import check_review  # noqa: E402
from benchmark import BenchmarkRunner, evaluate_entry_full, load_dataset  # noqa: E402
from benchmark.dataset import GoldClaim, GoldEntry, GoldStandard  # noqa: E402
from benchmark.models import available, get_reviewer  # noqa: E402
from core.models import Claim, Paper, PaperReview  # noqa: E402
from core.ports.services import AIReviewer  # noqa: E402
from infrastructure.ai import ClaudeAIReviewer, FakeAIReviewer, StubAIReviewer  # noqa: E402


# A PRP-like gold entry with a real controversy claim (RESTORE-style null result).
GOLD = GoldEntry(
    gold_id="GOLD-TEST-PRP",
    area="PRP",
    title="PRP for knee OA",
    study_type="Randomized Controlled Trial",
    status="curated",
    gold_claims=[
        GoldClaim(text="Intra-articular PRP improves clinical outcomes compared with HA in knee osteoarthritis."),
        GoldClaim(text="Intra-articular PRP was not superior to placebo for knee pain at 12 months."),
    ],
)


class OracleReviewer(AIReviewer):
    """Returns grounded claims that match the gold, including the controversy."""

    def review(self, paper: Paper) -> PaperReview:
        return PaperReview(
            paper_id=paper.paper_id,
            title=paper.title,
            study_type="Randomized Controlled Trial",
            evidence_level=4,
            main_limitations=["Heterogeneous PRP preparations."],
            contradicts_existing="A placebo-controlled RCT found PRP no better than saline.",
            claims=[
                Claim(claim_id="C1", text="PRP improves clinical outcomes compared with HA in knee osteoarthritis", supporting_data="pooled WOMAC"),
                Claim(claim_id="C2", text="PRP was not superior to placebo for knee pain at 12 months", supporting_data="RESTORE RCT"),
            ],
        )


def test_quality_gates() -> None:
    good = OracleReviewer().review(Paper(paper_id="X", title="t"))
    assert check_review(good).passed

    bad = PaperReview(
        title="t",
        claims=[Claim(claim_id="C1", text="something", supporting_data="")],
    )
    res = check_review(bad)
    assert not res.passed
    assert any("supporting_data" in v for v in res.violations)
    assert any("study_type" in v for v in res.violations)

    # The stub extracts nothing -> fails the gate honestly.
    stub_review = StubAIReviewer().review(Paper(paper_id="X", title="t"))
    assert not check_review(stub_review).passed


def test_full_metrics_oracle() -> None:
    review = OracleReviewer().review(Paper(paper_id="GOLD-TEST-PRP", title="PRP for knee OA"))
    r = evaluate_entry_full(GOLD, review, passed_gate=True)
    assert r.coverage == 1.0, r.coverage
    assert r.ucr == 0.0, r.ucr                      # no unsupported claims
    assert r.controversy_gold == 1 and r.controversy_hit == 1
    assert r.cdr == 1.0                              # detected the controversy
    assert r.grss >= 0.95, r.grss                   # near-perfect review


def test_full_metrics_miss_controversy() -> None:
    # A review that only says the positive half misses the controversy and adds noise.
    review = PaperReview(
        title="PRP for knee OA",
        study_type="Randomized Controlled Trial",
        evidence_level=4,
        claims=[
            Claim(claim_id="C1", text="PRP improves clinical outcomes compared with HA in knee osteoarthritis", supporting_data="pooled"),
            Claim(claim_id="C2", text="PRP cures osteoarthritis permanently in all patients", supporting_data="none"),
        ],
    )
    r = evaluate_entry_full(GOLD, review)
    assert r.controversy_hit == 0 and r.cdr == 0.0   # missed the controversy
    assert r.ucr > 0.0                               # the fabricated claim is unsupported
    assert r.grss < 0.95


def test_provider_registry() -> None:
    assert available() == ["claude", "fake", "manual", "stub"]
    assert isinstance(get_reviewer("fake"), FakeAIReviewer)
    assert isinstance(get_reviewer("claude"), ClaudeAIReviewer)

    # The real provider constructs cheaply but refuses to run without a key.
    reviewer = ClaudeAIReviewer(api_key=None)
    try:
        reviewer.review(Paper(paper_id="X", title="t"))
        raise AssertionError("expected RuntimeError without an API key")
    except RuntimeError as e:
        assert "API key" in str(e)


def test_evidence_classification_gate() -> None:
    from application.quality_gates import check_review
    from core.models import classify_evidence
    from core.models.enums import EvidenceClass
    from infrastructure.ai.mapping import build_review

    # Graded designs -> stars; non-graded documents -> categories.
    assert classify_evidence("Systematic Review / Meta-analysis") == EvidenceClass.five_star
    assert classify_evidence("Randomized Controlled Trial") == EvidenceClass.four_star
    assert classify_evidence("Clinical Practice Guideline") == EvidenceClass.consensus
    assert classify_evidence("Scoping Review") == EvidenceClass.exploratory

    # A guideline with no 1-5 level now PASSES the gate via its evidence_class.
    guide = build_review(
        Paper(paper_id="G", title="OARSI guideline", study_type="Clinical Practice Guideline"),
        {"claims": [{"text": "core treatment is exercise", "supporting_data": "recommendation"}]},
    )
    assert guide.evidence_level is None
    assert guide.evidence_class == EvidenceClass.consensus
    assert check_review(guide).passed


def test_runner_with_fake_on_real_dataset() -> None:
    gold = load_dataset(name="gold-standard")
    res = BenchmarkRunner(FakeAIReviewer(), "fake").run(gold)
    assert res.n_entries == len(gold.curated()) >= 6
    # Fake produces one grounded claim + metadata: passes the gate, but low coverage.
    assert res.gate_pass_rate == 1.0
    assert 0.0 <= res.grss <= 1.0
    assert 0.0 <= res.cdr <= 1.0

    # The stub extracts nothing: fails every gate, zero coverage.
    res_stub = BenchmarkRunner(StubAIReviewer(), "stub").run(gold)
    assert res_stub.gate_pass_rate == 0.0
    assert res_stub.coverage == 0.0


def main() -> int:
    test_quality_gates()
    test_full_metrics_oracle()
    test_full_metrics_miss_controversy()
    test_evidence_classification_gate()
    test_provider_registry()
    test_runner_with_fake_on_real_dataset()
    print("OK — Sprint 5A test passed (providers + quality gates + GRSS/CDR/UCR + runner)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
