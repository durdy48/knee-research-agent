# BASELINE v0.1 — First measured state of KRA

**Date:** 2026-07-11
**Status:** Frozen baseline (scientific record, not a technical changelog)

> This document freezes the first measured state of the Knee Research Agent so we can
> return to it later and answer: did we improve? which prompt/model was better? when did a
> regression appear? It records *what was measured, on what, with what, and with which
> known limitations* — in the spirit of a methods section, not a release note.

---

## Configuration under test

| Item | Value |
|------|-------|
| Dataset | `gold-standard` |
| Gold Standard version | v1.0 (14 curated entries, 6 Gold Topics, 7 clinical areas) |
| Prompt version | extraction contract v1 (`infrastructure/ai/manual.py` / `claude.py`) |
| Workflow version | Sprint 5A single stage: `Paper → Review → Quality Gates → Benchmark` |
| Provider | `manual` (Claude Code as engine, human-in-the-loop; no API key) |
| Evidence model | Evidence Level (1–5) + Evidence Classification (stars / Consensus / Exploratory) |
| Quality Gates | traceability + study-type + evidence-classified |

The 14 reviews scored here live in `runs/manual/reviews/reviews.json`.

## Metrics (frozen)

| KPI | Value |
|-----|-------|
| GRSS (Gold Review Similarity Score) | 98.9% |
| CDR (Controversy Detection Rate) | 100.0% |
| UCR (Unsupported Claim Rate) | 0.0% |
| Coverage | 98.6% |
| Traceability | 100.0% |
| Hallucinations | 0 |
| Quality gates passed | 100.0% |

GRSS breakdown (where the reviewer succeeds/fails):

| Sub-score | Value |
|-----------|-------|
| claims | 98.6% |
| grounding | 100.0% |
| controversies | 100.0% |
| metadata | 92.9% |
| evidence | 100.0% |
| limitations | 100.0% |
| clinical_relevance | 100.0% |

## Known limitations (read this before trusting the numbers)

- **This is an optimistic, non-blind measurement.** The same intelligence that curated the
  Gold Standard also produced the reviews, so it *calibrates the loop* (proving the
  pipeline detects coverage and controversies end to end) rather than blindly testing a
  model. A true evaluation needs a reviewer that did not see the gold, or held-out gold.
- **Reviews are abstract/metadata level.** No full text was fed; every claim carries
  `needs_full_text_confirmation = true`.
- **Gold Standard is 14/30.** Areas PRP, MSC, Cartilage, Meniscus and Early-OA still have
  open slots. We expand only when the metrics reveal a gap.
- **Matching is token-Jaccard.** Explainable but shallow; it rewards lexical overlap, not
  deep semantic equivalence.
- **`metadata` sub-score < 100%** because a couple of non-graded study-type labels
  (e.g. classification-criteria/consensus) don't lexically match the gold label.

## Future work (next, per the design conversation)

1. **Blind Review experiment** — pick 3 papers outside the Gold Standard; a reviewer that
   has not seen the gold reviews them; compare against a manual review. First unbiased signal.
2. **Blind / API or local run** — `--model claude` (Anthropic key) or Ollama, to measure a
   reviewer independent of the gold.
3. **Knowledge Consolidator** — the "jewel": `Validated Review → Evidence Consolidation →
   Consensus Update → Controversy Update → Research Gaps → Living Topic`. Decides which
   evidence weighs more, when a controversy lowers confidence, when a study shifts consensus.
4. **Then Sprint 5B** — consolidate *validated knowledge* (not papers) into Living Topics.

## How to reproduce

```bash
./kra benchmark --model manual        # reproduces the metrics above
```

## Freezing this baseline in Git

Run on your machine (this environment cannot see the repo):

```bash
git add -A && git commit -m "Baseline v0.1: first measured state (Sprint 5A)"
git tag -a baseline-v0.1 -m "First measured state of KRA (GRSS 98.9%, manual provider)"
```
