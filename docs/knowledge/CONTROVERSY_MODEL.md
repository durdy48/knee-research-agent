# CONTROVERSY_MODEL — holding disagreement faithfully

**Version:** 0.1 (design, pre-implementation)
**Status:** Draft for human curation
**Last Updated:** 2026-07-11

> A controversy is not a problem to be resolved by the system; it is **knowledge to be
> preserved**. This document specifies the controversy as a first-class object: its
> attributes, its lifecycle, and how it interacts with confidence and the Living Topic.
>
> Companion: `KNOWLEDGE_CONSOLIDATION.md` (§4), `CONFIDENCE_MODEL.md`. Embodies Golden Rule 2
> ("preserve the uncertainty explicitly") and is what the benchmark's **CDR** measures.

---

## Why controversies are first-class

Most tools flatten disagreement — they average it, pick a side, or drop the outlier. KRA
does the opposite: when credible evidence disagrees, the disagreement itself becomes a
tracked object. This is the project's differentiator, and the reason a KRA recommendation
can eventually be trusted like a good systematic review: it tells you not just *what* the
evidence says, but *where and why it disagrees*.

A controversy is **never deleted**. It is opened, updated, and — if the evidence eventually
converges — marked resolved, but its history remains (Knowledge Integrity, Golden Rule 7).

---

## Attributes of a Controversy

| Attribute | Meaning |
|-----------|---------|
| `id` | stable identifier, scoped to the Topic |
| `question` | the precise point in dispute (one sentence) |
| `supporting_studies` | evidence supporting the position (with Evidence Classification) |
| `contradicting_studies` | evidence against it (with Evidence Classification) |
| `possible_explanations` | why the evidence might disagree (heterogeneity, population, protocol, bias) |
| `resolution_level` | current state (see below) |
| `effect_on_confidence` | how much this controversy caps/lowers Topic confidence |
| `opened` / `last_updated` | dates (history preserved) |

The point in dispute must be **specific**. Not "does PRP work?" but "is intra-articular PRP
superior to placebo for knee-OA pain at 12 months?" — a controversy is about a claim, not a
whole topic.

---

## Resolution level (the lifecycle)

```
open ──▶ emerging ──▶ contested ──▶ resolving ──▶ resolved
                        │                            │
                        └────────── may reopen ◀─────┘   (new contradicting evidence)
```

| Level | Meaning | Typical confidence effect |
|-------|---------|---------------------------|
| **open** | a single credible contradiction has appeared | confidence dips; controversy flagged |
| **emerging** | more than one study now disagrees | confidence held in moderate band |
| **contested** | comparable weight on both sides (equipoise) | confidence near the middle; consensus stated as *uncertain* |
| **resolving** | evidence is converging toward one side | confidence begins to move toward that side |
| **resolved** | consistent, reproduced convergence | controversy archived; consensus updated; **history kept** |

A `resolved` controversy can **reopen** if new contradicting evidence of sufficient level
arrives. Nothing is lost.

---

## How a controversy is created and updated

During consolidation (`KNOWLEDGE_CONSOLIDATION.md` §5), *Detect conflicts* compares new
Evidence against the current consensus:

- If new Evidence **credibly contradicts** the consensus and none is yet tracked → **open** a
  controversy; apply a `Contradiction` Impact; record the studies on each side.
- If a tracked controversy gains **more** contradicting or supporting evidence → update its
  `resolution_level`, its study lists, and confidence accordingly.
- If evidence **converges** consistently → move toward `resolving`/`resolved`.

"Credibly contradicts" is judged by Evidence Classification and consistency, not by recency
alone — a single ★★★★ RCT can *open* a controversy against ★★★★★ meta-analyses (it did, for
PRP) but does not by itself *win* it.

---

## Rendering in the Living Topic

A Topic's **Controversias** section (per the `living-topic.md` template) is a view of its
open controversies: for each, the question, the two sides with their evidence levels, the
possible explanations, and the resolution level. The consensus text must acknowledge any
`contested`/`open` controversy rather than assert a settled position.

---

## Canonical example — PRP for knee osteoarthritis

- **Question:** Is intra-articular PRP superior to placebo/HA for knee-OA pain and function?
- **Supporting:** Belk 2021 (★★★★★), Dai 2017 (★★★★★), Nie 2021 (★★★★★) — favourable.
- **Contradicting:** RESTORE / Bennell 2021 (★★★★ RCT) — PRP no better than saline at 12 mo.
- **Possible explanations:** heterogeneous PRP formulations; different comparators (HA vs
  saline); outcome timing; leukocyte content.
- **Resolution level:** `contested`.
- **Effect on confidence:** holds the PRP Topic in the moderate band (`~0.4–0.75`).

The correct consolidated consensus is therefore: *"benefit is plausible but contested at
Level-1 evidence; not settled."* Any system that outputs "PRP works" **or** "PRP fails" has
failed this model — and the benchmark's CDR would catch it.

---

## Open design questions (for human curation)

- Fixed vocabulary for `possible_explanations` (heterogeneity / population / protocol / bias
  / comparator / outcome-timing) or free text?
- Should a `contested` controversy hard-cap confidence at a fixed ceiling (e.g. `0.75`)?
- When does a resolved controversy get archived out of the main Topic view (while keeping the
  record in the Ledger)?
