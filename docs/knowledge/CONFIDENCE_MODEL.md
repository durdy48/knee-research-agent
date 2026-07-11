# CONFIDENCE_MODEL — how sure KRA is, and why

**Version:** 0.1 (design, pre-implementation)
**Status:** Draft for human curation
**Last Updated:** 2026-07-11

> Confidence is *how sure the current consensus is* for a Clinical Topic, expressed as a
> number in `0..1`. This document fixes the **factors** that determine it and the **rules**
> by which evidence moves it — but deliberately **not** a final closed-form formula. We want
> the behaviour agreed before the arithmetic is frozen.
>
> Companion: `KNOWLEDGE_CONSOLIDATION.md` (§2–§3), `CONTROVERSY_MODEL.md`. Must stay
> consistent with `src/core/knowledge_engine.py`.

---

## What confidence is (and is not)

- **Confidence** is a property of the **consensus of a Topic**: how strongly the current
  body of evidence supports the prevailing position. Range `0.0` (no support / fully
  contested) to `1.0` (settled, reproduced, uncontested).
- It is **distinct from Evidence Level / Evidence Classification.** A single meta-analysis is
  ★★★★★ evidence, but if it is the *only* study and untested, topic confidence is still
  moderate. Evidence quality is an *input* to confidence, not confidence itself.
- It is **distinct from Confidence-for-the-patient** (the Insight layer). Personal relevance
  never changes scientific confidence (Golden Rule 3).

The default confidence for a new Topic is `0.5` (genuinely uncertain), matching
`ClinicalTopic.confidence = 0.5`.

---

## The factors

Confidence rises and falls as a function of six factors. Each is scored from a signal we can
actually observe in the validated reviews:

| Factor | What it captures | Observable signal |
|--------|------------------|-------------------|
| **Methodological quality** | strength of the study designs | Evidence Classification (★★★★★ … Exploratory) |
| **Consistency** | do studies agree? | agreement vs conflict among Claims across reviews |
| **Effect size** | is the effect meaningful, not just significant? | magnitude reported in supporting data |
| **Reproducibility** | replicated by independent groups? | number of independent studies pointing the same way |
| **Recency** | is the evidence current? | publication years; ageing without new support |
| **Controversy** | is there active disagreement? | presence/severity of open controversies |

Rules of thumb (to be quantified during curation):

- High-quality **and** consistent **and** reproduced → confidence trends high (`0.75–0.9`).
- High-quality but **contested** (a credible contradicting study) → confidence capped in the
  **moderate** band (`0.4–0.75`); the controversy is what holds it down.
- Low-quality or single-study → confidence stays near the middle regardless of a loud result.
- Consensus/guideline documents corroborate but do not, by themselves, push confidence to the
  top — they summarise, they do not add independent evidence.

Confidence is **bounded per Topic** by a plausible range (the Gold Standard encodes this as
`min_confidence`/`max_confidence` per Gold Topic — e.g. PRP `0.4–0.75`). The model must not
produce a value outside a topic's defensible range.

---

## How evidence moves confidence (the mechanics)

Each consolidation applies **one Impact event** to the Topic. This is already implemented in
`knowledge_engine.apply_event`; the model here is the meaning behind those numbers:

| Impact | Meaning | Effect on confidence |
|--------|---------|----------------------|
| **New** | first substantial evidence on the point | raise (largest step) |
| **Reinforcement** | agrees with the current consensus | raise (smaller step) |
| **Contradiction** | credible evidence against the consensus | lower |
| **Irrelevant** | no bearing on this consensus | unchanged |

Current engine steps (base, before scaling): New `+0.10`, Reinforcement `+0.08`,
Contradiction `−0.12`, Irrelevant `0`. Two properties matter and should be preserved:

- **Contradiction outweighs Reinforcement** (`−0.12` vs `+0.08`): it is easier to lose
  confidence than to gain it. This is the mathematical face of "preserve uncertainty".
- **Diminishing returns with volume**: adding many papers at once scales the step by
  `√(papers)`, not linearly — the tenth confirmatory study matters less than the first.
- Confidence is **clamped to `[0,1]`** and every move records `confidence_before` and
  `confidence_after` in an `EvolutionEvent` (→ becomes part of a Knowledge Delta).

---

## Worked example — PRP

1. Start: new Topic, confidence `0.5`.
2. Belk 2021 (★★★★★, favourable) → **New** → confidence up (~`0.60`).
3. Dai 2017 (★★★★★, favourable) → **Reinforcement** → up, diminishing (~`0.66`).
4. Nie 2021 (★★★★★, favourable) → **Reinforcement** → up, diminishing (~`0.70`).
5. RESTORE 2021 (★★★★ RCT, **negative**) → **Contradiction** → down (~`0.58`) **and opens a
   controversy**.

Result: confidence lands in the **moderate** band and a controversy is explicit — exactly
the honest state. Note the outcome is inside PRP's defensible range (`0.4–0.75`) and could
not have reached "settled" on this evidence.

---

## Open design questions (for human curation)

- Turn the six factors into an explicit weighting, or keep them as an ordered checklist that
  maps to Impact + step size? (Start with the latter; formalise only if the benchmark asks.)
- Should confidence **decay** over time when no new evidence arrives (recency)?
- Should effect size modulate the step (a large, clinically meaningful effect moving more
  than a statistically-significant-but-tiny one)?
- How should conflicting high-level evidence set the *ceiling* on confidence, not just the
  current value?
