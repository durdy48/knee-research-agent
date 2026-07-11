"""Benchmark metrics — compare a produced PaperReview against the Gold Review.

Base metrics: coverage, traceability, hallucinations, time, cost.
Sprint 5A KPIs (kept SEPARATE, per the chat — they are the differentiators):
  - GRSS  Gold Review Similarity Score : weighted composite headline (0-1).
  - CDR   Controversy Detection Rate   : did the model recover the controversy claims?
  - UCR   Unsupported Claim Rate       : produced claims not corroborated by the gold.
Matching is a simple normalised token-Jaccard so it stays model-agnostic and explainable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from core.models import Claim, PaperReview
from core.models.enums import EvidenceClass
from .dataset import GoldClaim, GoldEntry, GoldTopic

_MATCH_THRESHOLD = 0.5

# Cues that mark a gold claim as expressing controversy / uncertainty / a null result.
# CDR measures whether the model recovers precisely these — the KRA differentiator.
_CONTROVERSY_CUES = (
    "no better", "not superior", "no different", "not inferior", "did not",
    "no single", "no agreed", "remains limited", "no significant difference",
    "conflict", "contradict", "uncertain", "not settled", "no consensus",
    "not universally", "no evidence",
)

# GRSS component weights (sum = 1.0). The composite is decomposed so you can see WHERE a
# model fails, not just the headline. CDR/UCR are also reported on their own.
_GRSS_WEIGHTS = {
    "claims": 0.28,              # relevant gold claims recovered (coverage)
    "grounding": 0.22,          # 1 - UCR (absence of unsupported claims)
    "controversies": 0.15,      # controversies / null results recognised (CDR)
    "metadata": 0.10,           # study type present and matching
    "evidence": 0.10,           # evidence classified (level or category)
    "limitations": 0.08,        # limitations identified
    "clinical_relevance": 0.07,  # findings / relation to existing knowledge stated
}


def _tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def _matches(a: str, b: str) -> bool:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    jaccard = len(ta & tb) / len(ta | tb)
    return jaccard >= _MATCH_THRESHOLD


def _is_controversy(text: str) -> bool:
    low = (text or "").lower()
    return any(cue in low for cue in _CONTROVERSY_CUES)


@dataclass
class EntryResult:
    gold_id: str
    coverage: float          # recall of gold claims
    traceability: float      # fraction of produced claims that are grounded
    hallucinations: int      # produced claims not matching any gold claim
    produced: int
    gold: int
    time_s: float = 0.0
    cost_usd: float = 0.0
    grss: float = 0.0                 # Gold Review Similarity Score (0-1)
    ucr: float = 0.0                  # Unsupported Claim Rate (0-1)
    cdr: float = 1.0                  # per-entry controversy recall (1.0 if none to detect)
    controversy_gold: int = 0         # gold controversy claims in this entry
    controversy_hit: int = 0          # of those, how many the model recovered
    components: dict = field(default_factory=dict)  # GRSS sub-scores (where it fails)
    passed_gate: bool = True
    gate_violations: List[str] = field(default_factory=list)


def evaluate_entry(
    gold_id: str,
    produced: List[Claim],
    gold: List[GoldClaim],
    *,
    time_s: float = 0.0,
    cost_usd: float = 0.0,
) -> EntryResult:
    prod_texts = [c.text for c in produced]
    gold_texts = [g.text for g in gold]

    matched_gold = sum(1 for g in gold_texts if any(_matches(g, p) for p in prod_texts))
    matched_prod = sum(1 for p in prod_texts if any(_matches(p, g) for g in gold_texts))
    hallucinations = len(prod_texts) - matched_prod

    coverage = (matched_gold / len(gold_texts)) if gold_texts else 1.0
    # A produced claim is "traceable" if it carries supporting data or matches the gold.
    traceable = sum(
        1
        for c in produced
        if c.supporting_data or any(_matches(c.text, g) for g in gold_texts)
    )
    traceability = (traceable / len(produced)) if produced else 1.0

    return EntryResult(
        gold_id=gold_id,
        coverage=round(coverage, 4),
        traceability=round(traceability, 4),
        hallucinations=hallucinations,
        produced=len(produced),
        gold=len(gold_texts),
        time_s=round(time_s, 6),
        cost_usd=round(cost_usd, 6),
    )


def evaluate_entry_full(
    entry: GoldEntry,
    review: PaperReview,
    *,
    time_s: float = 0.0,
    cost_usd: float = 0.0,
    passed_gate: bool = True,
    gate_violations: Optional[List[str]] = None,
) -> EntryResult:
    """Full Sprint-5A scoring of a produced PaperReview against a Gold Review."""
    base = evaluate_entry(
        entry.gold_id, review.claims, entry.gold_claims, time_s=time_s, cost_usd=cost_usd
    )
    prod_texts = [c.text for c in review.claims]
    gold_texts = [g.text for g in entry.gold_claims]

    # UCR: produced claims not corroborated by any gold claim (proxy for "not in source").
    ucr = (base.hallucinations / base.produced) if base.produced else 0.0
    # A review that extracts nothing is not "grounded" — it just has nothing to ground.
    grounding = (1.0 - ucr) if base.produced else 0.0

    # CDR: of the gold claims that express controversy, how many the model recovered.
    controversy_gold_texts = [g for g in gold_texts if _is_controversy(g)]
    controversy_hit = sum(
        1 for g in controversy_gold_texts if any(_matches(g, p) for p in prod_texts)
    )
    controversy_gold = len(controversy_gold_texts)
    cdr = (controversy_hit / controversy_gold) if controversy_gold else 1.0

    # GRSS components (each 0-1) — decomposed so we can see WHERE a model fails.
    study_present = 0.5 if review.study_type is not None else 0.0
    study_match = 0.5 if _study_type_ok(review.study_type, entry.study_type) else 0.0
    evidence_ok = 1.0 if (
        review.evidence_level is not None
        or (review.evidence_class not in (None, EvidenceClass.unclassified))
    ) else 0.0
    clinical_ok = 1.0 if (
        (review.primary_findings or "").strip()
        or review.reinforces_existing
        or review.contradicts_existing
    ) else 0.0
    comp = {
        "claims": base.coverage,
        "grounding": grounding,
        "controversies": cdr,
        "metadata": study_present + study_match,
        "evidence": evidence_ok,
        "limitations": 1.0 if review.main_limitations else 0.0,
        "clinical_relevance": clinical_ok,
    }
    grss = sum(_GRSS_WEIGHTS[k] * v for k, v in comp.items())

    base.components = {k: round(v, 4) for k, v in comp.items()}
    base.grss = round(grss, 4)
    base.ucr = round(ucr, 4)
    base.cdr = round(cdr, 4)
    base.controversy_gold = controversy_gold
    base.controversy_hit = controversy_hit
    base.passed_gate = passed_gate
    base.gate_violations = gate_violations or []
    return base


def _study_type_ok(produced: Optional[str], gold: Optional[str]) -> bool:
    if not gold:
        return True  # nothing to match against
    if not produced:
        return False
    ta, tb = _tokens(produced), _tokens(gold)
    # study-type strings are short; any shared significant token counts as a match.
    return bool(ta & tb)


def evaluate_topic(
    produced_consensus: str,
    produced_confidence: float,
    produced_claims: List[str],
    gold: GoldTopic,
) -> dict:
    """Topic-level check: does the consolidated topic match the expected Gold Topic?"""
    consensus_match = _matches(produced_consensus, gold.expected_consensus) if gold.expected_consensus else True
    confidence_ok = gold.min_confidence <= produced_confidence <= gold.max_confidence
    key_covered = sum(1 for k in gold.key_claims if any(_matches(k, p) for p in produced_claims))
    key_coverage = (key_covered / len(gold.key_claims)) if gold.key_claims else 1.0
    return {
        "topic_id": gold.topic_id,
        "consensus_match": consensus_match,
        "confidence_ok": confidence_ok,
        "key_coverage": round(key_coverage, 4),
    }


@dataclass
class BenchmarkResult:
    model: str
    n_entries: int
    coverage: float
    traceability: float
    hallucinations: int
    cost_usd: float
    time_s: float
    grss: float = 0.0            # mean Gold Review Similarity Score (headline KPI)
    cdr: float = 1.0            # overall Controversy Detection Rate
    ucr: float = 0.0            # overall Unsupported Claim Rate
    gate_pass_rate: float = 0.0  # fraction of reviews passing the Quality Gates
    grss_components: dict = field(default_factory=dict)  # mean GRSS sub-scores
    pending: List[str] = field(default_factory=list)  # gold_ids awaiting a manual review
    per_entry: List[EntryResult] = field(default_factory=list)


def aggregate(model: str, results: List[EntryResult]) -> BenchmarkResult:
    n = len(results)
    if n == 0:
        return BenchmarkResult(model, 0, 0.0, 0.0, 0, 0.0, 0.0, per_entry=[])
    total_produced = sum(r.produced for r in results)
    total_halluc = sum(r.hallucinations for r in results)
    total_contro_gold = sum(r.controversy_gold for r in results)
    total_contro_hit = sum(r.controversy_hit for r in results)
    comp_keys = _GRSS_WEIGHTS.keys()
    grss_components = {
        k: round(sum(r.components.get(k, 0.0) for r in results) / n, 4) for k in comp_keys
    }
    return BenchmarkResult(
        model=model,
        n_entries=n,
        coverage=round(sum(r.coverage for r in results) / n, 4),
        traceability=round(sum(r.traceability for r in results) / n, 4),
        hallucinations=total_halluc,
        cost_usd=round(sum(r.cost_usd for r in results), 6),
        time_s=round(sum(r.time_s for r in results), 6),
        grss=round(sum(r.grss for r in results) / n, 4),
        cdr=round((total_contro_hit / total_contro_gold) if total_contro_gold else 1.0, 4),
        ucr=round((total_halluc / total_produced) if total_produced else 0.0, 4),
        gate_pass_rate=round(sum(1 for r in results if r.passed_gate) / n, 4),
        grss_components=grss_components,
        per_entry=results,
    )
