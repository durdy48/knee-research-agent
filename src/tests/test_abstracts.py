#!/usr/bin/env python3
"""Abstract-enrichment tests — the reviewer receives real source text when available.

No API key needed: we check the plumbing (Paper.abstract, LocalAbstractSource, runner
enrichment, and that the Claude prompt includes the abstract). Run: python3 src/tests/test_abstracts.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark import BenchmarkRunner  # noqa: E402
from benchmark.dataset import GoldClaim, GoldEntry, GoldStandard  # noqa: E402
from core.models import Paper  # noqa: E402
from core.ports.services import AIReviewer  # noqa: E402
from infrastructure.ai import ClaudeAIReviewer  # noqa: E402
from infrastructure.sources import LocalAbstractSource  # noqa: E402


class CapturingReviewer(AIReviewer):
    """Records the abstract it was handed, so we can assert enrichment happened."""

    def __init__(self) -> None:
        self.seen = {}

    def review(self, paper: Paper):
        self.seen[paper.paper_id] = paper.abstract
        from core.models import Claim, PaperReview

        return PaperReview(
            paper_id=paper.paper_id,
            title=paper.title,
            study_type="Meta-analysis",
            evidence_level=5,
            claims=[Claim(claim_id="C1", text="a claim", supporting_data="x")],
        )


def test_local_abstract_source() -> None:
    with tempfile.TemporaryDirectory() as d:
        src = LocalAbstractSource(Path(d))
        assert src.get("GOLD-X", None, None) is None
        (Path(d) / "32302218.txt").write_text("Real abstract text.", encoding="utf-8")
        # Found by PMID; also DOI slugging works.
        assert src.get("GOLD-X", "32302218", None) == "Real abstract text."
        (Path(d) / "10.1177_0363546520909397.md").write_text("By DOI.", encoding="utf-8")
        assert src.get(None, None, "10.1177/0363546520909397") == "By DOI."


def test_runner_enriches_from_dataset_and_source() -> None:
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "GOLD-B.txt").write_text("Abstract from file.", encoding="utf-8")
        gold = GoldStandard(
            name="fix",
            entries=[
                GoldEntry(gold_id="GOLD-A", area="PRP", title="A", status="curated",
                          abstract="Inline abstract.",
                          gold_claims=[GoldClaim(text="a claim")]),
                GoldEntry(gold_id="GOLD-B", area="PRP", title="B", status="curated",
                          gold_claims=[GoldClaim(text="a claim")]),
            ],
        )
        rev = CapturingReviewer()
        BenchmarkRunner(rev, "cap", abstract_source=LocalAbstractSource(Path(d))).run(gold)
        assert rev.seen["GOLD-A"] == "Inline abstract."   # dataset field wins
        assert rev.seen["GOLD-B"] == "Abstract from file."  # falls back to the source


def test_claude_prompt_includes_abstract() -> None:
    reviewer = ClaudeAIReviewer(api_key="dummy")
    with_abs = reviewer._build_user_prompt(Paper(paper_id="X", title="T", abstract="ABSTRACT_HERE"))
    assert "ABSTRACT_HERE" in with_abs
    without = reviewer._build_user_prompt(Paper(paper_id="X", title="T"))
    assert "needs_full_text_confirmation" in without  # instructed to be cautious


def main() -> int:
    test_local_abstract_source()
    test_runner_enriches_from_dataset_and_source()
    test_claude_prompt_includes_abstract()
    print("OK — abstract-enrichment test passed (source + runner enrichment + prompt)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
