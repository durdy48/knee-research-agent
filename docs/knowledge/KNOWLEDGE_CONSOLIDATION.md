# KNOWLEDGE_CONSOLIDATION — the rulebook

**Version:** 0.1 (design, pre-implementation)
**Status:** Draft for human curation
**Last Updated:** 2026-07-11

> This is the **rulebook** of the Knowledge Consolidator — the intellectual heart of KRA.
> It does not talk about Python or Claude. It talks about **how scientific knowledge
> evolves**, so that the behaviour is decided *before* any code fixes it in place. If this
> document conflicts with an implementation, the document wins until it is revised.
>
> Companion documents: `CONFIDENCE_MODEL.md`, `CONTROVERSY_MODEL.md`, `KNOWLEDGE_DELTAS.md`.
> It must stay consistent with `ADR-0001`, the `GLOSSARY`, and the existing knowledge engine
> (`src/core/knowledge_engine.py`, which already moves a topic's `confidence` by Impact).

---

## What the Consolidator is (and is not)

The Consolidator takes **validated evidence about one Clinical Topic** and maintains a
single, current, confidence-weighted **consensus**, an explicit set of **controversies**,
and a list of **open questions** — while never losing history. It works with *knowledge*,
not with topics as containers; its output can feed Living Topics, Executive Reports,
Personal Insights, Obsidian and (later) APIs.

It is **not** a summariser (it does not shorten papers), **not** a reviewer (that is the AI
Provider that produces a `PaperReview`), and **not** a decision-maker (Golden Rule 5 —
humans decide). It sits *after* review and Quality Gates, and *after* the benchmark has
shown the reviews are trustworthy:

```
Paper → Review → Quality Gates → Benchmark        (validated review)
                                     │
                                     ▼
        Validated Review → KNOWLEDGE CONSOLIDATION → updated Living Topic + Knowledge Delta
```

---

## The five questions this document answers

### 1. What does it mean to consolidate knowledge?

Five papers do not produce five conclusions. They produce **one consolidated conclusion**,
with a confidence and its exceptions. Consolidation is the transformation:

```
many Evidence items about a Topic  →  one current Consensus
                                        + a Confidence (0..1)
                                        + explicit Controversies
                                        + Open Questions
                                        + preserved history
```

This is the Data → Knowledge boundary of the project (`CLAUDE.md` §9):

- **Data** — a raw fact from one study (a Claim + its supporting data).
- **Knowledge** — a conclusion consolidated *across* studies (the Topic's consensus).
- **Insight** — a personalised interpretation for the patient (a later, separate layer).

Consolidation lives entirely at the **Knowledge** level. It never invents; every element of
the consensus traces back to Evidence (Golden Rule 4).

### 2. When does a consensus change?

A consensus changes only when the **weight of evidence** shifts — not because the newest
paper is loud. Weight is a function of evidence quality (Evidence Classification), the
consistency across studies, effect size, reproducibility and recency (see
`CONFIDENCE_MODEL.md`). Guiding rules:

- A single contradicting study among a strong, consistent body **does not flip** the
  consensus. It **lowers confidence** and **opens or strengthens a controversy**.
- The consensus flips only when the contradicting evidence **outweighs** the prior body by
  level *and* consistency — e.g. repeated high-level results, not one outlier.
- When in genuine equipoise, the consensus is stated as *uncertain* and the controversy is
  made explicit (Golden Rule 2). Uncertainty is a valid, first-class state.

The canonical example is PRP (see `CONTROVERSY_MODEL.md`): three favourable Level-1
meta-analyses (Belk 2021, Dai 2017, Nie 2021) versus one rigorous negative RCT (RESTORE,
Bennell 2021). The correct outcome is **not** "PRP works" nor "PRP fails", but "benefit is
plausible but contested; confidence moderate; controversy open".

### 3. How is confidence calculated?

Confidence is a number in `0..1` attached to the Topic. It is not an arbitrary score: it
depends on methodological quality, consistency between studies, effect size,
reproducibility, recency and the existence of controversies. The exact formula is
deliberately **not** fixed yet — only the factors are. The full model, and how Impact
events move confidence, is specified in `CONFIDENCE_MODEL.md`. It must remain consistent
with the existing engine, where `New`/`Reinforcement` raise confidence, `Contradiction`
lowers it, and `Irrelevant` leaves it unchanged.

### 4. How are controversies represented?

A controversy is **never deleted**; it is preserved explicitly as a first-class object with
its supporting studies, contradicting studies, possible explanations and a *resolution
level*. Full specification in `CONTROVERSY_MODEL.md`. The rule: when the evidence disagrees,
the system's job is to *hold* the disagreement faithfully, not to resolve it prematurely.

### 5. What happens when a new paper arrives?

We never overwrite the Topic. The flow is append-only and produces an auditable record:

```
New Paper
  ↓ Evidence Extraction        (Claims + supporting data — the PaperReview)
  ↓ Evidence Evaluation        (Evidence Classification, quality, effect)
  ↓ Knowledge Consolidation
      ├─ Compare with current Consensus
      ├─ Detect conflicts           → may open/strengthen a Controversy
      ├─ Adjust Confidence          → per CONFIDENCE_MODEL (an Impact event)
      ├─ Update Controversies       → per CONTROVERSY_MODEL
      └─ Generate a Knowledge Delta → per KNOWLEDGE_DELTAS
  ↓ Publish a new Topic Version   (previous version snapshotted, never erased)
```

Every run yields **at most one new Topic Version** and **one Knowledge Delta**. The prior
version is kept as an **Evidence Snapshot** (Golden Rule 7 — Knowledge Integrity).

---

## Inputs and outputs (the contract)

**Input:** one or more *validated* `PaperReview`s for a single Clinical Topic (validated =
passed the Quality Gates), each carrying Claims with supporting data and an Evidence
Classification.

**Output:**
- an updated **Living Clinical Topic** (consensus, confidence, supporting/contradicting
  evidence, controversies, open questions, relevance-for-patient left to the Insight layer);
- exactly one **Knowledge Delta** describing the change;
- a new **Topic Version** with the previous state snapshotted.

---

## Invariants (must always hold)

1. **Evidence before opinion.** Nothing enters the consensus without traceable evidence.
2. **Preserve uncertainty.** Contradiction lowers confidence and surfaces a controversy; it
   is never silently averaged away.
3. **Append-only history.** A change creates a new version + a Delta; the past is snapshotted,
   never overwritten (Knowledge Integrity).
4. **Personalisation is out of scope here.** Consolidation produces *knowledge*; relevance
   for a specific patient is the Insight layer and must not bend the scientific conclusion
   (Golden Rule 3).
5. **Humans make decisions.** The Consolidator proposes the updated consensus and Delta; a
   human may curate before it is published.

---

## Relationship to what already exists

- `src/core/knowledge_engine.py` already implements the *mechanics* of confidence movement
  (`apply_event` with the `Impact` classification, append-only `events`). This document is
  the *semantics* those mechanics must serve; `CONFIDENCE_MODEL.md` bridges the two.
- `ClinicalTopic` (in `src/core/models/topic.py`) is the object being consolidated; the
  `living-topic.md` template is a rendered view of it.
- The benchmark's **CDR** (Controversy Detection Rate) is what tells us, objectively,
  whether consolidation is preserving controversies as this rulebook requires.

## Open design questions (for human curation)

- How many contradicting studies (and of what level) should *flip* a consensus vs merely
  open a controversy? (Quantify in `CONFIDENCE_MODEL.md`.)
- Should confidence decay with age when no new evidence arrives (recency factor)?
- Do guideline/consensus documents update the consensus directly, or only corroborate it?
