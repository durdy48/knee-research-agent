# DECISIONS — why KRA is different

**Status:** Living
**Last Updated:** 2026-07-11

> Not another ADR. A short statement of the few decisions that make KRA what it is — the
> project's philosophy, condensed. If you understand these five, you understand KRA.

## The five decisions

1. **Knowledge is more important than documents.** KRA does not collect or summarise papers;
   it consolidates them into knowledge. Papers are inputs; the Living Clinical Topic is the
   product.

2. **Personalisation never changes the science.** The patient's context changes only what is
   *highlighted* (relevance), never the scientific conclusion. Evidence and personalisation
   are separate layers, by design.

3. **Every change must be traceable.** Nothing enters the knowledge base directly. It is
   reviewed → validated (Quality Gates) → measured (Benchmark) → consolidated, and every
   change is an immutable, justified Knowledge Delta in the append-only Ledger.

4. **Topics are living documents.** A Clinical Topic is never re-created, only updated — and
   its history is never lost (Evidence Snapshots + the Ledger).

5. **Uncertainty must be preserved.** When high-quality evidence disagrees, KRA holds the
   controversy explicitly instead of averaging it away or picking a side. Preserving
   uncertainty is a feature, not a gap.

## What follows from them

- A **deterministic** consolidation engine (not an LLM deciding what changed), so the
  reasoning is auditable and reproducible.
- A **benchmark** as the compass (GRSS / CDR / UCR): the benchmark drives the corpus, not
  the other way round.
- The AI model is a **replaceable provider** behind a port; no vendor is coupled to the
  domain.
- Humans make the decisions; KRA improves understanding and never diagnoses or prescribes.

That is the whole philosophy. Everything else in the codebase is in service of these five.
