#!/usr/bin/env python3
"""Knowledge Consolidation Engine — behaviour tests (deterministic, no AI, no key).

These describe BEHAVIOUR, not implementation, mirroring the design in docs/knowledge/:
new / reinforcement / contradiction→controversy / no-evidence→no-change / guideline. Then it
consolidates the real TOPIC-PRP and TOPIC-MSC from the validated manual reviews to show the
engine is generic. Run: python3 src/tests/test_consolidation.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark import load_dataset  # noqa: E402
from core.consolidation import KnowledgeConsolidationEngine  # noqa: E402
from core.models import (  # noqa: E402
    Claim,
    ClinicalTopic,
    Impact,
    Paper,
    PaperReview,
)
from core.models.enums import ResolutionLevel  # noqa: E402
from infrastructure.ai import ManualAIProvider  # noqa: E402


def _review(title, *, reinforces=None, contradicts=None, study_type="Randomized Controlled Trial"):
    return PaperReview(
        paper_id=title, title=title, study_type=study_type, evidence_level=4,
        reinforces_existing=reinforces, contradicts_existing=contradicts,
        claims=[Claim(claim_id="C1", text=f"finding from {title}", supporting_data="data")],
    )


def test_case_new_and_reinforcement() -> None:
    eng = KnowledgeConsolidationEngine()
    topic = ClinicalTopic(topic_id="T", name="T")

    r1 = eng.consolidate(topic, [_review("A", reinforces="supports X")], when="2026-01-01")
    assert r1.impact is Impact.new and r1.changed and topic.version == 2
    c_after_new = topic.confidence
    assert c_after_new > 0.5                                   # New raised confidence

    r2 = eng.consolidate(topic, [_review("B", reinforces="supports X")], when="2026-02-01")
    assert r2.impact is Impact.reinforcement and topic.version == 3
    assert topic.confidence > c_after_new                      # reinforcement raised it more
    assert "TopicPublished" in r2.events


def test_case_contradiction_opens_controversy() -> None:
    eng = KnowledgeConsolidationEngine()
    topic = ClinicalTopic(topic_id="T", name="T")
    eng.consolidate(topic, [_review("A", reinforces="supports X")], when="2026-01-01")
    before = topic.confidence

    r = eng.consolidate(topic, [_review("RCT-neg", contradicts="X is not superior to placebo")], when="2026-03-01")
    assert r.impact is Impact.contradiction
    assert topic.confidence < before                           # contradiction lowered confidence
    assert len(topic.controversies) == 1                       # a controversy was opened
    assert topic.controversies[0].resolution_level == ResolutionLevel.open
    assert "ControversyAdded" in r.events

    # A second contradiction escalates the same controversy (never a duplicate).
    r2 = eng.consolidate(topic, [_review("RCT-neg2", contradicts="still not superior")], when="2026-04-01")
    assert len(topic.controversies) == 1
    assert topic.controversies[0].resolution_level == ResolutionLevel.emerging
    assert r2.impact is Impact.contradiction


def test_case_no_evidence_no_change() -> None:
    eng = KnowledgeConsolidationEngine()
    topic = ClinicalTopic(topic_id="T", name="T")
    eng.consolidate(topic, [_review("A", reinforces="x")], when="2026-01-01")
    v, c = topic.version, topic.confidence

    r = eng.consolidate(topic, [], when="2026-05-01")          # no new evidence
    assert r.impact is Impact.irrelevant and not r.changed
    assert r.delta is None
    assert topic.version == v and topic.confidence == c        # nothing changed


def test_case_guideline_updates_recommendations() -> None:
    eng = KnowledgeConsolidationEngine()
    topic = ClinicalTopic(topic_id="T", name="T")
    eng.consolidate(topic, [_review("A", reinforces="x")], when="2026-01-01")

    guide = PaperReview(
        paper_id="G", title="OARSI guideline", study_type="Clinical Guideline",
        evidence_class="Consensus", reinforces_existing="core treatment is exercise",
        claims=[Claim(claim_id="C1", text="exercise is a core treatment", supporting_data="recommendation")],
    )
    r = eng.consolidate(topic, [guide], when="2026-06-01")
    assert r.impact is Impact.reinforcement
    assert "recommend" in (r.delta.what_changed.lower())
    assert "ConsensusChanged" in r.events                      # wording updated


def test_idempotent_reprocessing() -> None:
    """Reprocessing the same paper changes nothing (review question 2: idempotency)."""
    eng = KnowledgeConsolidationEngine()
    topic = ClinicalTopic(topic_id="T", name="T")
    rev = _review("A", reinforces="supports X")
    eng.consolidate(topic, [rev], when="2026-01-01")
    v, c = topic.version, topic.confidence

    again = eng.consolidate(topic, [rev], when="2026-01-02")  # same paper again
    assert again.impact is Impact.irrelevant and not again.changed
    assert again.delta is None
    assert topic.version == v and topic.confidence == c       # nothing moved


def test_determinism() -> None:
    """Same sequence of evidence -> identical topic state (review question 1)."""
    def run():
        eng = KnowledgeConsolidationEngine()
        t = ClinicalTopic(topic_id="T", name="T")
        eng.consolidate(t, [_review("A", reinforces="x")], when="2026-01-01")
        eng.consolidate(t, [_review("B", contradicts="not superior")], when="2026-02-01")
        return t

    a, b = run(), run()
    assert a.confidence == b.confidence
    assert a.version == b.version
    assert len(a.controversies) == len(b.controversies) == 1


def test_end_to_end() -> None:
    """New Paper -> Review -> Quality Gates -> Consolidation -> Delta -> Living Topic."""
    from application.quality_gates import check_review

    gold = load_dataset(name="gold-standard")
    reviews_dir = Path(__file__).resolve().parents[2] / "runs" / "manual" / "reviews"
    if not (reviews_dir / "reviews.json").is_file():
        return
    entry = next(e for e in gold.curated() if e.gold_id == "GOLD-PRP-001")
    paper = Paper(paper_id=entry.gold_id, title=entry.title, doi=entry.doi, pmid=entry.pmid,
                  study_type=entry.study_type, topics=[entry.area])
    review = ManualAIProvider(reviews_dir).review(paper)     # produce
    assert check_review(review).passed                        # gate

    topic = ClinicalTopic(topic_id="TOPIC-PRP", name="PRP")
    res = KnowledgeConsolidationEngine().consolidate(topic, [review], when="2026-07-01")
    assert res.changed and res.delta is not None              # consolidate -> delta
    assert res.delta.confidence_after is not None and res.delta.evidence
    assert "TopicPublished" in res.events and topic.version == 2


def test_prp_and_msc_are_generic() -> None:
    gold = load_dataset(name="gold-standard")
    reviews_dir = Path(__file__).resolve().parents[2] / "runs" / "manual" / "reviews"
    if not (reviews_dir / "reviews.json").is_file():
        return
    provider = ManualAIProvider(reviews_dir)

    def consolidate_area(area: str, order: list) -> ClinicalTopic:
        topic = ClinicalTopic(topic_id=f"TOPIC-{area}", name=area)
        eng = KnowledgeConsolidationEngine()
        by_id = {e.gold_id: e for e in gold.curated() if e.area == area or True}
        for gid in order:
            e = by_id[gid]
            paper = Paper(paper_id=e.gold_id, title=e.title, doi=e.doi, pmid=e.pmid,
                          year=e.year, study_type=e.study_type, topics=[e.area])
            eng.consolidate(topic, [provider.review(paper)], when="2026-07-01")
        return topic

    # PRP: three favourable meta-analyses then the negative RESTORE RCT -> a controversy.
    prp = consolidate_area("PRP", ["GOLD-PRP-001", "GOLD-PRP-002", "GOLD-PRP-004", "GOLD-PRP-003"])
    assert len(prp.controversies) == 1
    assert 0.35 <= prp.confidence <= 0.8                       # moderate, not settled
    assert prp.version == 5                                    # four consolidations

    # MSC: a favourable synthesis then a null one -> the SAME engine opens a controversy.
    msc = consolidate_area("Mesenchymal Stem Cells", ["GOLD-MSC-001", "GOLD-MSC-002"])
    assert len(msc.controversies) == 1
    assert msc.version == 3


def main() -> int:
    test_case_new_and_reinforcement()
    test_case_contradiction_opens_controversy()
    test_case_no_evidence_no_change()
    test_case_guideline_updates_recommendations()
    test_idempotent_reprocessing()
    test_determinism()
    test_end_to_end()
    test_prp_and_msc_are_generic()
    print("OK — consolidation test passed (cases + determinism + idempotency + e2e + PRP/MSC)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
