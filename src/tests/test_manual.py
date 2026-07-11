#!/usr/bin/env python3
"""Manual-mode tests — ManualAIProvider (human-in-the-loop / Claude Code engine), key-free.

Checks package generation, review ingestion (per-file and combined map), the pending error,
and a runner pass with a partial review set. Run: python3 src/tests/test_manual.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark import BenchmarkRunner, load_dataset  # noqa: E402
from benchmark.dataset import GoldClaim, GoldEntry, GoldStandard  # noqa: E402
from core.models import Paper  # noqa: E402
from infrastructure.ai import ManualAIProvider, ReviewPendingError, build_review_package  # noqa: E402


def test_build_review_package() -> None:
    with tempfile.TemporaryDirectory() as d:
        paper = Paper(paper_id="GOLD-X", title="A paper", doi="10.1/x", topics=["PRP"])
        folder = build_review_package(paper, Path(d))
        assert (folder / "prompt.md").is_file()
        assert (folder / "schema.json").is_file()
        assert (folder / "metadata.json").is_file()
        meta = json.loads((folder / "metadata.json").read_text())
        assert meta["paper_id"] == "GOLD-X"
        assert "supporting_data" in (folder / "prompt.md").read_text()


def test_pending_then_review() -> None:
    with tempfile.TemporaryDirectory() as d:
        prov = ManualAIProvider(Path(d))
        paper = Paper(paper_id="GOLD-Y", title="t", topics=["PRP"])
        try:
            prov.review(paper)
            raise AssertionError("expected ReviewPendingError")
        except ReviewPendingError:
            pass

        # per-file review
        (Path(d) / "GOLD-Y.json").write_text(json.dumps({
            "study_type": "Meta-analysis", "evidence_level": 5,
            "claims": [{"text": "a claim", "supporting_data": "x"}],
        }), encoding="utf-8")
        review = prov.review(paper)
        assert review.study_type == "Meta-analysis"
        assert len(review.claims) == 1 and review.claims[0].supporting_data == "x"


def test_combined_reviews_map() -> None:
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "reviews.json").write_text(json.dumps({
            "GOLD-Z": {"study_type": "Randomized Controlled Trial", "evidence_level": 2,
                        "claims": [{"text": "c", "supporting_data": "s"}]},
        }), encoding="utf-8")
        prov = ManualAIProvider(Path(d))
        review = prov.review(Paper(paper_id="GOLD-Z", title="t"))
        assert review.study_type == "Randomized Controlled Trial"


def test_runner_reports_pending() -> None:
    gold = GoldStandard(name="fix", entries=[
        GoldEntry(gold_id="A", area="PRP", title="A", status="curated",
                  gold_claims=[GoldClaim(text="PRP improves outcomes vs HA")]),
        GoldEntry(gold_id="B", area="PRP", title="B", status="curated",
                  gold_claims=[GoldClaim(text="something else")]),
    ])
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "A.json").write_text(json.dumps({
            "study_type": "Meta-analysis", "evidence_level": 5,
            "claims": [{"text": "PRP improves outcomes vs HA", "supporting_data": "pooled"}],
        }), encoding="utf-8")
        res = BenchmarkRunner(ManualAIProvider(Path(d)), "manual").run(gold)
        assert res.n_entries == 1                 # only A reviewed
        assert res.pending == ["B"]               # B still pending
        assert res.coverage == 1.0 and res.gate_pass_rate == 1.0


def test_real_reviews_load_if_present() -> None:
    # If the authored reviews exist, the provider maps them for a curated entry.
    gold = load_dataset(name="gold-standard")
    reviews = Path(__file__).resolve().parents[2] / "runs" / "manual" / "reviews" / "reviews.json"
    if not reviews.is_file():
        return
    prov = ManualAIProvider(reviews.parent)
    entry = gold.curated()[0]
    review = prov.review(Paper(paper_id=entry.gold_id, title=entry.title, topics=[entry.area]))
    assert review.claims and all(c.supporting_data for c in review.claims)


def main() -> int:
    test_build_review_package()
    test_pending_then_review()
    test_combined_reviews_map()
    test_runner_reports_pending()
    test_real_reviews_load_if_present()
    print("OK — manual-mode test passed (package + ingestion + pending + runner)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
